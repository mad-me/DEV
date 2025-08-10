#!/usr/bin/env python3
"""
Funk-Import-Tool für ARF/FL Rechnungen

Ziele:
- Unterscheidet automatisch zwischen 4010 (40100) und 31300 Funkrechnungen
- Extrahiert relevante Daten aus PDF (ARF/FL Varianten) je nach Typ
- Speichert Ergebnisse in `SQL/funk.db` in monatlichen Tabellen (MM_JJ)

Hinweise:
- Für die PDF-Extraktion wird pdf2image + Tesseract OCR verwendet
- Tesseract/Poppler-Pfade werden aus `import_config.py` gelesen, mit Fallback
- Minimaler, aber robuster Parser, der auf typische Muster prüft
"""

import re
import sys
import os
import sqlite3
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

try:
    from pdf2image import convert_from_path
    import pytesseract
except Exception as e:
    print(f"[FEHLER] Benötigte Pakete fehlen: {e}. Bitte `pip install pdf2image pytesseract`.")
    sys.exit(2)

# Konfiguration laden (optional)
try:
    from import_config import TESSERACT_PATH as _CFG_TESS, POPPLER_PATH as _CFG_POPPLER
except Exception:
    _CFG_TESS = None
    _CFG_POPPLER = None

if _CFG_TESS and os.path.exists(_CFG_TESS):
    pytesseract.pytesseract.tesseract_cmd = _CFG_TESS

POPPLER_PATH = _CFG_POPPLER if (_CFG_POPPLER and os.path.exists(_CFG_POPPLER)) else None


def detect_vendor(text: str) -> str:
    """Erkennt den Anbieter: '4010' oder '31300'."""
    t = text.lower()
    # Starke Hinweise
    if "taxi4me" in t or "4010" in t or "40100" in t:
        return "4010"
    if "3130" in t or "31300" in t:
        return "31300"
    # Inhalte/Begriffe pro Layout
    if "unternehmer2.4" in t and "auswertungen" in t:
        # Beide nutzen das Portal, fallback 4010
        return "4010"
    return "unknown"


def detect_document_type(text: str) -> str:
    """Erkennt Dokumenttyp: 'ARF' (Funk) oder 'FL' (Flughafenfahrten)."""
    t = text.lower()
    if re.search(r"\barf\b", t):
        return "ARF"
    # Heuristik für FL
    if "flughafen" in t or re.search(r"\bfl\b", t):
        return "FL"
    return "ARF"  # Default: Funk


def parse_month_from_filename(filename: str) -> Optional[str]:
    """Extrahiert MM_JJ aus Dateiname, z. B. 'Abrechnungen 07_2025.pdf' -> '07_25'."""
    m = re.search(r"(\d{2})_(\d{4})", filename)
    if m:
        mm, yyyy = m.group(1), m.group(2)
        return f"{mm}_{yyyy[-2:]}"
    # ARFYYMM / FLYYMM
    m2 = re.search(r"(?:ARF|FL)(\d{2})(\d{2})", filename, re.IGNORECASE)
    if m2:
        yy, mm = m2.group(1), m2.group(2)
        return f"{mm}_{yy}"
    return None


def ocr_pdf_to_text(pdf_path: Path) -> str:
    images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
    texts = []
    for img in images[:3]:  # Erste Seiten genügen meist zur Erkennung
        for psm in (6, 11):
            try:
                txt = pytesseract.image_to_string(img, lang='deu', config=f'--psm {psm} --oem 3')
                if txt and txt.strip():
                    texts.append(txt)
                    break
            except Exception:
                continue
    return "\n".join(texts)


def ensure_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.close()


def create_table_if_not_exists(conn: sqlite3.Connection, table: str):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS "{table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT,          -- '4010' oder '31300'
            doc_type TEXT,        -- 'ARF' oder 'FL'
            filename TEXT,
            netto REAL,
            brutto REAL,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()


def ensure_columns(conn: sqlite3.Connection, table: str):
    """Stellt sicher, dass die für das Tool benötigten Spalten existieren (Migration bei alten Tabellen)."""
    cursor = conn.execute(f"PRAGMA table_info('{table}')")
    existing = {row[1] for row in cursor.fetchall()}  # Spaltennamen
    required = {
        "vendor": "TEXT",
        "doc_type": "TEXT",
        "filename": "TEXT",
        "netto": "REAL",
        "brutto": "REAL",
        "details": "TEXT",
        "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
    }
    for col, coltype in required.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE '{table}' ADD COLUMN {col} {coltype}")
    conn.commit()


def parse_amounts(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Einfache Heuristik, um Netto/Brutto-Beträge zu finden."""
    # Erlaube Formate wie 1.234,56 oder 1234,56
    def to_float(s: str) -> Optional[float]:
        try:
            s = s.replace(' ', '').replace('.', '').replace(',', '.')
            return float(s)
        except Exception:
            return None

    netto = None
    brutto = None

    # Suche nach expliziten Labels
    m = re.search(r"netto\s*[:=]?\s*([\d\.\s,]+)", text, re.IGNORECASE)
    if m:
        netto = to_float(m.group(1))
    m = re.search(r"brutto\s*[:=]?\s*([\d\.\s,]+)", text, re.IGNORECASE)
    if m:
        brutto = to_float(m.group(1))

    # Fallback: größte/zweite größte Zahl als brutto/netto
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


def import_funk_pdf(pdf_path: Path) -> Dict[str, Any]:
    """Hauptfunktion: erkennt Vendor/Typ, extrahiert Daten, speichert in funk.db."""
    base_dir = Path(__file__).resolve().parent / "SQL"
    db_path = base_dir / "funk.db"
    ensure_db(db_path)

    filename = pdf_path.name
    month_id = parse_month_from_filename(filename)
    if not month_id:
        from datetime import datetime
        now = datetime.now()
        month_id = f"{now.month:02d}_{str(now.year)[-2:]}"

    # OCR
    text = ocr_pdf_to_text(pdf_path)
    vendor = detect_vendor(text)
    doc_type = detect_document_type(text)
    netto, brutto = parse_amounts(text)

    table = month_id
    conn = sqlite3.connect(str(db_path))
    try:
        create_table_if_not_exists(conn, table)
        ensure_columns(conn, table)
        conn.execute(
            f"INSERT INTO \"{table}\" (vendor, doc_type, filename, netto, brutto, details) VALUES (?, ?, ?, ?, ?, ?)",
            (vendor, doc_type, filename, netto, brutto, f"autodetect; len={len(text)}")
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "success": True,
        "vendor": vendor,
        "doc_type": doc_type,
        "table": table,
        "netto": netto,
        "brutto": brutto,
    }


def main():
    if len(sys.argv) < 2:
        print("[FEHLER] Nutzung: python funk_import_tool.py <rechnung.pdf> [mehrere...]")
        sys.exit(2)
    exit_code = 0
    for p in sys.argv[1:]:
        try:
            result = import_funk_pdf(Path(p))
            print(f"✅ Import OK: {Path(p).name} -> Tabelle {result['table']} | vendor={result['vendor']} | type={result['doc_type']} | netto={result['netto']} | brutto={result['brutto']}")
        except Exception as e:
            print(f"❌ Fehler bei {p}: {e}")
            exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


