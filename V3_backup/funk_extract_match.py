#!/usr/bin/env python3
"""
Isoliertes Test- und Optimierungs-Tool für Funk-PDF-Auslesen und Fahrzeug-Matching

Funktionen:
- OCR-Text aus PDF extrahieren (pdf2image + Tesseract)
- Vendor-Erkennung (4010/31300) und Dokumenttyp (ARF/FL)
- Heuristische Betragsextraktion (Netto/Brutto)
- Fahrzeug-Matching: Nummerntafel/Kennzeichen gegen `SQL/database.db` → Tabelle `vehicles.license_plate`

CLI:
  python funk_extract_match.py <rechnung.pdf> [--db SQL/database.db] [--top 5] [--dump dump.txt]

Ausgabe:
- Top-N Fahrzeug-Kandidaten mit Score, gefundener Substring und normalisierten Formen
- Erkanntes vendor/type/netto/brutto

Hinweis: Dieses Tool schreibt NICHT in Datenbanken; es dient rein zum Auslesen & Matching.
"""

import argparse
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from pdf2image import convert_from_path
    import pytesseract
except Exception as e:
    print(f"[FEHLER] Benötigte Pakete fehlen: {e}. Bitte `pip install pdf2image pytesseract`.", file=sys.stderr)
    sys.exit(2)

try:
    from import_config import TESSERACT_PATH as _CFG_TESS, POPPLER_PATH as _CFG_POPPLER
except Exception:
    _CFG_TESS = None
    _CFG_POPPLER = None

if _CFG_TESS and os.path.exists(_CFG_TESS):
    pytesseract.pytesseract.tesseract_cmd = _CFG_TESS

POPPLER_PATH = _CFG_POPPLER if (_CFG_POPPLER and os.path.exists(_CFG_POPPLER)) else None


# -------------------- OCR & Erkennung --------------------

def ocr_pdf_text(pdf_path: Path, max_pages: int = 3) -> str:
    images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
    texts: List[str] = []
    for img in images[: max_pages]:
        # Mehrere PSM-Modi versuchen
        for psm in (6, 11, 8):
            try:
                txt = pytesseract.image_to_string(img, lang='deu', config=f'--psm {psm} --oem 3')
                if txt and txt.strip():
                    texts.append(txt)
                    break
            except Exception:
                continue
    return "\n".join(texts)


def detect_vendor(text: str) -> str:
    t = text.lower()
    if "taxi4me" in t or "4010" in t or "40100" in t:
        return "4010"
    if "3130" in t or "31300" in t:
        return "31300"
    return "unknown"


def detect_document_type(text: str) -> str:
    t = text.lower()
    if re.search(r"\barf\b", t):
        return "ARF"
    if "flughafen" in t or re.search(r"\bfl\b", t):
        return "FL"
    return "ARF"


def parse_amounts(text: str) -> Tuple[Optional[float], Optional[float]]:
    def to_float(s: str) -> Optional[float]:
        try:
            s = s.replace(' ', '').replace('.', '').replace(',', '.')
            return float(s)
        except Exception:
            return None

    netto = None
    brutto = None
    m = re.search(r"netto\s*[:=]?\s*([\d\.\s,]+)", text, re.IGNORECASE)
    if m:
        netto = to_float(m.group(1))
    m = re.search(r"brutto\s*[:=]?\s*([\d\.\s,]+)", text, re.IGNORECASE)
    if m:
        brutto = to_float(m.group(1))
    if brutto is None or netto is None:
        nums = [to_float(x) for x in re.findall(r"[\d\.\s,]{4,}", text)]
        nums = [n for n in nums if n is not None]
        nums.sort(reverse=True)
        if nums:
            if brutto is None:
                brutto = nums[0]
            if netto is None and len(nums) >= 2:
                netto = nums[1]
    return netto, brutto


# -------------------- Fahrzeug-Matching --------------------

def load_license_plates(vehicles_db: Path) -> List[str]:
    conn = sqlite3.connect(str(vehicles_db))
    try:
        cur = conn.cursor()
        cur.execute("SELECT license_plate FROM vehicles")
        rows = cur.fetchall()
        return [str(r[0] or '') for r in rows]
    finally:
        conn.close()


def normalize_plate(plate: str, confusables: bool = False) -> str:
    s = re.sub(r"[^A-Za-z0-9]", "", str(plate).upper())
    if confusables:
        # Häufige OCR-Verwechslungen angleichen
        s = (
            s.replace('0', 'O')
             .replace('1', 'I')
             .replace('5', 'S')
             .replace('2', 'Z')
             .replace('6', 'G')
             .replace('8', 'B')
        )
    return s


def normalize_text_for_plate(text: str, confusables: bool = False) -> str:
    s = re.sub(r"[^A-Za-z0-9]", "", text.upper())
    if confusables:
        s = (
            s.replace('0', 'O')
             .replace('1', 'I')
             .replace('5', 'S')
             .replace('2', 'Z')
             .replace('6', 'G')
             .replace('8', 'B')
        )
    return s


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            ins = prev[j + 1] + 1
            dele = cur[j] + 1
            sub = prev[j] + (ca != cb)
            cur.append(min(ins, dele, sub))
        prev = cur
    return prev[-1]


def best_plate_match(text: str, plates: List[str], top_n: int = 5) -> List[Dict[str, object]]:
    """Findet Top-N Kennzeichen-Matches im Text.
    Strategie: normalisieren, Sliding-Window-Vergleich mit Levenshtein-Score.
    """
    text_norm = normalize_text_for_plate(text, confusables=True)
    results: List[Tuple[float, str, str]] = []  # (score, plate, snippet)

    for plate in plates:
        p_norm = normalize_plate(plate, confusables=True)
        if not p_norm:
            continue
        L = len(p_norm)
        if L == 0:
            continue
        best_score = 0.0
        best_snip = ""
        # Direkt-Containment (ohne Distanz)
        if p_norm in text_norm:
            best_score = 1.0
            best_snip = p_norm
        else:
            # Sliding Window
            for i in range(0, max(0, len(text_norm) - L + 1)):
                cand = text_norm[i : i + L]
                dist = levenshtein(cand, p_norm)
                score = max(0.0, 1.0 - (dist / L))
                if score > best_score:
                    best_score = score
                    best_snip = cand
                if best_score == 1.0:
                    break
        if best_score > 0:
            results.append((best_score, plate, best_snip))

    results.sort(key=lambda x: x[0], reverse=True)
    top = results[: top_n]
    return [
        {"score": round(score, 3), "plate": plate, "matched": snip}
        for (score, plate, snip) in top
    ]


# -------------------- CLI --------------------

def main():
    parser = argparse.ArgumentParser(description="Isoliertes Auslesen & Fahrzeug-Matching für Funk-PDFs")
    parser.add_argument("pdf", type=Path, help="Pfad zur Funk-Rechnung (PDF)")
    parser.add_argument("--db", type=Path, default=Path("SQL") / "database.db", help="Pfad zur Vehicles-DB (Default: SQL/database.db)")
    parser.add_argument("--top", type=int, default=5, help="Anzahl Top-Matches")
    parser.add_argument("--dump", type=Path, default=None, help="Optional: Raw-OCR-Text in Datei dumpen")
    args = parser.parse_args()

    if not args.pdf.exists():
        print(f"[FEHLER] PDF nicht gefunden: {args.pdf}")
        sys.exit(2)
    if not args.db.exists():
        print(f"[FEHLER] Vehicles-DB nicht gefunden: {args.db}")
        sys.exit(2)

    print(f"📄 Datei: {args.pdf}")
    print(f"🗄️  Vehicles-DB: {args.db}")

    text = ocr_pdf_text(args.pdf)
    if args.dump:
        try:
            args.dump.parent.mkdir(parents=True, exist_ok=True)
            args.dump.write_text(text, encoding="utf-8")
            print(f"📝 OCR-Dump gespeichert: {args.dump}")
        except Exception as e:
            print(f"[WARN] Konnte Dump nicht speichern: {e}")

    vendor = detect_vendor(text)
    doc_type = detect_document_type(text)
    netto, brutto = parse_amounts(text)

    print(f"🔎 Erkannt: vendor={vendor} | type={doc_type} | netto={netto} | brutto={brutto}")

    plates = load_license_plates(args.db)
    candidates = best_plate_match(text, plates, top_n=args.top)
    if candidates:
        print("\n🚗 Top Fahrzeug-Matches:")
        for i, c in enumerate(candidates, 1):
            print(f" {i:>2}. score={c['score']:.3f}  plate={c['plate']:<12}  match={c['matched']}")
    else:
        print("Keine Fahrzeug-Matches gefunden.")


if __name__ == "__main__":
    main()





