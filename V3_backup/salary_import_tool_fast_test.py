"""
Schneller Test-Importer für Gehaltsabrechnungen (ohne Funktionalitätsverlust)

Ziele (nur für Tests, keine Produktivdaten überschreiben):
- pdfplumber-first (direkter PDF-Text), OCR nur als Fallback und nur wo nötig
- Seiten-Parallelisierung (optional)
- Vorgecompilete Regexe
- Eigene Test-Datenbank: SQL/salaries_test.db

Aufruf (PowerShell):
  python .\\salary_import_tool_fast_test.py "Pfad\\zur\\Abrechnung.pdf"
"""

from __future__ import annotations

import re
import sys
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

import pdfplumber  # direkte Textextraktion
from pdf2image import convert_from_path
import pytesseract


# Laute pdfminer/pdfplumber-Hinweise (z. B. "CropBox missing from /Page, defaulting to MediaBox") unterdrücken
for _noisy in (
    "pdfminer",
    "pdfminer.pdfpage",
    "pdfminer.pdfinterp",
    "pdfminer.layout",
    "pdfminer.converter",
    "pdfminer.pdfdocument",
    "pdfminer.pdftypes",
    "pdfplumber",
):
    logging.getLogger(_noisy).setLevel(logging.ERROR)

# Optional: Tesseract-/Poppler-Pfade anpassen, falls nötig
try:
    from import_config import TESSERACT_PATH as _CFG_TESS, POPPLER_PATH as _CFG_POPPLER
except Exception:
    _CFG_TESS = None
    _CFG_POPPLER = None

if _CFG_TESS:
    pytesseract.pytesseract.tesseract_cmd = _CFG_TESS
POPPLER_PATH = _CFG_POPPLER


TEST_DB_PATH = Path("SQL") / "salaries_test.db"
DRIVERS_DB_PATH = Path("SQL") / "database.db"


@dataclass
class PayrollEntry:
    dienstnehmer: str
    dn_nr: str
    brutto: float
    zahlbetrag: float
    page_number: int


# Sammeln und schön ausgeben: Pretty Trace
@dataclass
class PageSummary:
    page_number: int
    plumber_dn: str = ''
    plumber_dn_nr: str = ''
    header_dn: str = ''
    header_dn_nr: str = ''
    entries: List[PayrollEntry] = None
    match: Optional[Tuple[Optional[int], str, float]] = None  # (driver_id, name, score)

    def __post_init__(self):
        if self.entries is None:
            self.entries = []


class PrettyTracer:
    def __init__(self):
        self.pages: Dict[int, PageSummary] = {}

    def _get(self, page: int) -> PageSummary:
        if page not in self.pages:
            self.pages[page] = PageSummary(page)
        return self.pages[page]

    def record_plumber_header(self, page: int, dn: str, dn_nr: str):
        ps = self._get(page)
        ps.plumber_dn = dn
        ps.plumber_dn_nr = dn_nr

    def record_header(self, page: int, dn: str, dn_nr: str):
        ps = self._get(page)
        ps.header_dn = dn
        ps.header_dn_nr = dn_nr

    def record_entry(self, page: int, entry: PayrollEntry):
        ps = self._get(page)
        ps.entries.append(entry)

    def record_match(self, page: int, driver_id: Optional[int], name: str, score: float):
        ps = self._get(page)
        ps.match = (driver_id, name, score)

    def print_summary(self):
        print("\n===== Trace (kompakt, 1 Zeile pro Seite) =====")
        for page in sorted(self.pages.keys()):
            ps = self.pages[page]
            # Felder wählen (Priorität: Text-Header vor Pos-Header; dann Entry-Felder)
            dn = ps.header_dn or ps.plumber_dn
            dn_nr = ps.header_dn_nr or ps.plumber_dn_nr
            brutto = None
            zahlbetrag = None
            if ps.entries:
                # Nimm den ersten Eintrag der Seite
                brutto = ps.entries[0].brutto
                zahlbetrag = ps.entries[0].zahlbetrag
                # Falls DN/DN-Nr. noch leer, versuche aus Entry
                dn = dn or ps.entries[0].dienstnehmer
                dn_nr = dn_nr or ps.entries[0].dn_nr
            did, mname, score = (None, '', 0.0)
            if ps.match is not None:
                did, mname, score = ps.match
            brutto_str = f"{brutto:.2f}" if isinstance(brutto, (int, float)) else ""
            zahlbetrag_str = f"{zahlbetrag:.2f}" if isinstance(zahlbetrag, (int, float)) else ""
            print(
                f"p{page:02d} | DN='{dn}' | DN-Nr='{dn_nr}' | Brutto={brutto_str} | Zahlbetrag={zahlbetrag_str} | driver_id={did} | Match='{mname}' | score={score:.2f}"
            )
        print("===== Ende Trace =====\n")

# Vorgecompilete Muster
RE_DIENSTNEHMER_LINE = re.compile(r"Dienstnehme(?:r(?:/in|In)?)?\s*:\s*([^\n]+)", re.IGNORECASE)
RE_DIENSTNEHMER = re.compile(r"Dienstnehme(?:r(?:/in|In)?)?\W*[:\-]?\s*(.*?)(?=\s*(DN\W*Nr|Monat|Firma|Unternehmen|El\b)|$)", re.IGNORECASE)
# DN-Nr mit beliebigen Bindestrichen/Trennzeichen (\- ‑ – —) und optionalem Doppelpunkt
RE_DNNR = re.compile(r"(?:DN\s*[\-‑–—]?\s*Nr|DNr)\.?\s*[:]?\s*(\d+)", re.IGNORECASE)
RE_BRUTTO = re.compile(r"Brutto(?:-?Bezug)?\W*[:\-]?\s*([\d\.,]+)", re.IGNORECASE)
RE_ZAHLBETRAG = re.compile(r"(?:Zahlbetrag|Auszahlungsbetrag|Netto(?:betrag)?)\W*[:\-]?\s*([\d\.,]+)", re.IGNORECASE)


def to_float(amount_str: str) -> float:
    s = (amount_str or "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def plumber_extract_page_texts(pdf_path: Path) -> Dict[int, str]:
    texts: Dict[int, str] = {}
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                t = page.extract_text(x_tolerance=1, y_tolerance=1) or ""
                texts[i] = t
    except Exception:
        pass
    return texts


def ocr_page_to_text(image) -> str:
    # Zwei PSMs probieren; 350–400 DPI reichen, hier kommt schon ein Image
    for psm in (6, 11):
        try:
            t = pytesseract.image_to_string(image, lang='deu', config=f'--psm {psm} --oem 3')
            if t and t.strip():
                return t
        except Exception:
            continue
    return ""


def plumber_header_from_page(pdf_path: Path, page_number: int, trace: bool = False, pretty: Optional[PrettyTracer] = None) -> Tuple[str, str]:
    """Extrahiert Dienstnehmer und DN-Nr. positionsbasiert aus einer PDF-Seite via pdfplumber.words."""
    dn = ''
    dnnr = ''
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            if 1 <= page_number <= len(pdf.pages):
                page = pdf.pages[page_number - 1]
                words = page.extract_words(x_tolerance=2, y_tolerance=2)
                # Dienstnehmer: finde Token beginnend mit 'Dienstnehme' (mit/ohne ':')
                for w in words:
                    t = w.get('text', '')
                    if re.match(r"^Dienstnehme", t, re.IGNORECASE):
                        y = w.get('top', 0.0)
                        x_right = w.get('x1', 0.0)
                        right_words = [ww for ww in words if abs(ww.get('top', 0.0) - y) <= 2.0 and ww.get('x0', 0.0) > x_right]
                        line = ' '.join(ww.get('text', '') for ww in right_words)
                        line = _normalize_text(line)
                        # bis zum nächsten Label abschneiden
                        line = re.split(r"\b(DN\W*Nr|Monat|Firma|Unternehmen)\b", line, flags=re.IGNORECASE)[0].strip()
                        # Adresse abschneiden
                        line = re.split(r"\s\d{2,}.*", line)[0].strip()
                        if line:
                            dn = line
                            break
                # DN-Nr suchen: kombiniert "DN-Nr.:" / "DNr.:" oder getrennte Varianten, Zahl rechts daneben
                label_pat = re.compile(r"^(?:DN\W*Nr|DNr)\.?[:]?$", re.IGNORECASE)
                dn_only_pat = re.compile(r"^DN$", re.IGNORECASE)
                for w in words:
                    t = (w.get('text', '') or '').strip()
                    if label_pat.match(t) or dn_only_pat.match(t):
                        y = float(w.get('top', 0.0))
                        x_right = float(w.get('x1', 0.0))
                        same_line = [ww for ww in words if abs(float(ww.get('top', 0.0)) - y) <= 3.0 and float(ww.get('x0', 0.0)) > x_right]
                        numeric_right = sorted(
                            [ww for ww in same_line if re.match(r"^\d{1,8}$", (ww.get('text', '') or '').strip())],
                            key=lambda a: float(a.get('x0', 0.0))
                        )
                        if numeric_right:
                            dnnr = (numeric_right[0].get('text', '') or '').strip()
                            break
                        # Fallback: kleine Vertikalabweichung tolerieren (z. B. Zahl auf nächster Zeile, rechts vom Label)
                        near_right = sorted(
                            [ww for ww in words if (y - 8.0) <= float(ww.get('top', 0.0)) <= (y + 8.0) and float(ww.get('x0', 0.0)) > x_right and re.match(r"^\d{1,8}$", (ww.get('text', '') or '').strip())],
                            key=lambda a: (abs(float(a.get('top', 0.0)) - y), float(a.get('x0', 0.0)))
                        )
                        if near_right:
                            dnnr = (near_right[0].get('text', '') or '').strip()
                            break
    except Exception:
        pass
    if trace:
        print(f"[TRACE] plumber_header p{page_number}: dn='{dn}' dn_nr='{dnnr}'")
    if pretty is not None:
        pretty.record_plumber_header(page_number, dn, dnnr)
    return dn, dnnr


def _normalize_text(s: str) -> str:
    s = s.replace('\xa0', ' ')
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _find_page_header_fields(text: str) -> Tuple[str, str]:
    """Versucht Dienstnehmer und DN-Nr. aus dem gesamten Seiten-Text zu extrahieren.
    Falls der Name in der nächsten Zeile steht, wird diese genommen."""
    dn = ''
    dnnr = ''
    # Direkte Suche in der gleichen Zeile
    m = RE_DIENSTNEHMER_LINE.search(text)
    if m:
        raw = _normalize_text(m.group(1))
        # Schneide an markanten Tokens ab
        raw = re.split(r"\b(DN\s*[-]?\s*Nr|Monat|Firma|Unternehmen)\b", raw, flags=re.IGNORECASE)[0].strip()
        # Entferne Adresse/PLZ (beginnt meist mit Ziffer)
        raw = re.split(r"\s\d{2,}.*", raw)[0].strip()
        # Wenn noch zu lang, nimm erste 3 Worte
        parts = raw.split()
        if len(parts) > 4:
            raw = " ".join(parts[:4])
        dn = raw
    else:
        # Suche Zeile mit Label und nimm nächste nicht-leere Zeile
        lines = text.splitlines()
        for i, raw in enumerate(lines):
            if re.search(r"Dienstnehme(?:r(?:/in|In)?)?\b", raw, re.IGNORECASE):
                # Nächste nicht-leere Zeile als Name
                for j in range(i + 1, min(i + 5, len(lines))):
                    candidate = lines[j].strip()
                    if candidate:
                        # Entferne offensichtliche Adressen (PLZ am Anfang)
                        if re.match(r"^\d{3,}\b", candidate):
                            continue
                        dn = _normalize_text(candidate)
                        break
                break
    # DN-Nr. robust suchen (verschiedene Schreibweisen/Abstände)
    m2 = RE_DNNR.search(text)
    if m2:
        dnnr = m2.group(1).strip()
    else:
        # Fallback: Zeilenweise suchen
        lines = text.splitlines()
        for raw in lines[:60]:
            mm = RE_DNNR.search(raw)
            if mm:
                dnnr = mm.group(1).strip()
                break
        # Weitere Heuristik: DN-Nr steht oft auf gleicher Überschriftszeile wie Monat → schaue 1-2 Zeilen davor
        if not dnnr:
            for idx, raw in enumerate(lines[:80]):
                if re.search(r"\bMonat\b", raw, re.IGNORECASE):
                    for k in range(max(0, idx - 3), idx + 1):
                        mm = RE_DNNR.search(lines[k])
                        if mm:
                            dnnr = mm.group(1).strip()
                            break
                    break
    # Falls Dienstnehmer noch leer: Heuristik – suche oberste Zeile mit Namensmuster
    if not dn:
        name_line = None
        for raw in text.splitlines()[:20]:
            cand = _normalize_text(raw)
            if not cand or len(cand) < 5:
                continue
            # Zeilen mit Zahlen/Monat/Belegspalten überspringen
            if re.search(r"\d{2}[/\-.]\d{4}|Brutto|Netto|Zahlbetrag|Betrag|Einbehalte|Bemessung|Bezug|Monat", cand, re.IGNORECASE):
                continue
            # Namensmuster: 2–4 Worte, jeweils groß geschrieben, keine Ziffern
            tokens = cand.split()
            if 2 <= len(tokens) <= 5 and all(t[0].isalpha() and t[0].isupper() and not re.search(r"\d", t) for t in tokens):
                name_line = cand
                break
        if name_line:
            dn = name_line
    return dn, dnnr


def extract_entries_from_text(text: str, page_number: int, trace: bool = False, defaults: Tuple[str, str] = ('', ''), pretty: Optional[PrettyTracer] = None) -> List[PayrollEntry]:
    entries: List[PayrollEntry] = []
    # Zeilenweises Parsing mit Zustand
    current: Dict[str, str] = {}
    page_dn_default, page_dnnr_default = _find_page_header_fields(text)
    if not page_dn_default and defaults[0]:
        page_dn_default = defaults[0]
    if not page_dnnr_default and defaults[1]:
        page_dnnr_default = defaults[1]
    if trace:
        print(f"[TRACE] header p{page_number}: dn='{page_dn_default}' dn_nr='{page_dnnr_default}'")
    if pretty is not None:
        pretty.record_header(page_number, page_dn_default, page_dnnr_default)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = RE_DIENSTNEHMER.search(line)
        if m:
            # Vorherigen Eintrag abschließen
            if 'Dienstnehmer' in current:
                entry = PayrollEntry(
                    dienstnehmer=current.get('Dienstnehmer', '') or page_dn_default,
                    dn_nr=current.get('DN-Nr.', '') or page_dnnr_default,
                    brutto=to_float(current.get('Brutto', '0')),
                    zahlbetrag=to_float(current.get('Zahlbetrag', '0')),
                    page_number=page_number,
                )
                entries.append(entry)
                if pretty is not None:
                    pretty.record_entry(page_number, entry)
                current = {}
            current['Dienstnehmer'] = m.group(1).strip()
        m = RE_DNNR.search(line)
        if m:
            current['DN-Nr.'] = m.group(1).strip()
        m = RE_BRUTTO.search(line)
        if m:
            current['Brutto'] = m.group(1).strip()
        m = RE_ZAHLBETRAG.search(line)
        if m:
            current['Zahlbetrag'] = m.group(1).strip()

    if 'Dienstnehmer' in current:
        entry = PayrollEntry(
            dienstnehmer=current.get('Dienstnehmer', '') or page_dn_default,
            dn_nr=current.get('DN-Nr.', '') or page_dnnr_default,
            brutto=to_float(current.get('Brutto', '0')),
            zahlbetrag=to_float(current.get('Zahlbetrag', '0')),
            page_number=page_number,
        )
        entries.append(entry)
        if pretty is not None:
            pretty.record_entry(page_number, entry)
    # Fallback: Wenn keine Einträge generiert wurden, versuche seitenweite Suche
    if not entries:
        dn_match = RE_DIENSTNEHMER.search(text)
        id_match = RE_DNNR.search(text)
        br_match = RE_BRUTTO.search(text)
        zb_match = RE_ZAHLBETRAG.search(text)
        if any([dn_match, id_match, br_match, zb_match]):
            dn = dn_match.group(1).strip() if dn_match else ''
            dnnr = id_match.group(1).strip() if id_match else ''
            brutto = to_float(br_match.group(1)) if br_match else 0.0
            zahlbetrag = to_float(zb_match.group(1)) if zb_match else 0.0
            if trace:
                print(f"[TRACE] pagewide p{page_number}: dn='{dn}' dn_nr='{dnnr}' brutto={brutto} zahlbetrag={zahlbetrag}")
            # Defaults anwenden, falls leer
            if not dn:
                dn = page_dn_default
            if not dnnr:
                dnnr = page_dnnr_default
            entry = PayrollEntry(dienstnehmer=dn, dn_nr=dnnr, brutto=brutto, zahlbetrag=zahlbetrag, page_number=page_number)
            entries.append(entry)
            if pretty is not None:
                pretty.record_entry(page_number, entry)
    if trace:
        for e in entries:
            print(f"[TRACE] entry p{e.page_number}: dn='{e.dienstnehmer}' dn_nr='{e.dn_nr}' brutto={e.brutto} zahlbetrag={e.zahlbetrag}")
    return entries


def load_driver_cache() -> Tuple[Dict[int, str], Dict[str, int]]:
    """Lädt Fahrer aus SQL/database.db und baut zwei Maps:
    - driver_id_to_name: int -> canonical_name
    - name_key_to_id: normalized name key -> driver_id (für schnellen Lookup)
    """
    driver_id_to_name: Dict[int, str] = {}
    name_key_to_id: Dict[str, int] = {}
    if not DRIVERS_DB_PATH.exists():
        return driver_id_to_name, name_key_to_id
    conn = sqlite3.connect(str(DRIVERS_DB_PATH))
    cur = conn.cursor()
    try:
        rows: List[Tuple[Optional[int], Optional[str], Optional[str]]] = []
        try:
            cur.execute("SELECT driver_id, first_name, last_name FROM drivers")
            rows = cur.fetchall() or []
        except Exception:
            rows = []
        # Fallback: einige Schemas nutzen 'id' statt 'driver_id'
        if not rows:
            try:
                cur.execute("SELECT id, first_name, last_name FROM drivers")
                rows = cur.fetchall() or []
            except Exception:
                rows = []
        for did, fn, ln in rows:
            if did is None:
                continue
            cname = f"{fn or ''} {ln or ''}".strip()
            if not cname:
                continue
            driver_id_to_name[int(did)] = cname
            key = normalize_name_key(cname)
            if key:
                name_key_to_id[key] = int(did)
    finally:
        conn.close()
    return driver_id_to_name, name_key_to_id


def normalize_name_key(name: str) -> str:
    s = (name or "").lower()
    s = s.replace('-', ' ').replace('_', ' ')
    s = re.sub(r"[^a-zäöüß\s]", " ", s)
    # Titel/Prefixe entfernen
    s = re.sub(r"\b(ing|dr|mag|dipling|bsc|msc)\b\.?", " ", s)
    s = re.sub(r"\bal\s+", "el ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fuzzy_match_scored(dienstnehmer: str, driver_id_to_name: Dict[int, str]) -> Tuple[Optional[int], Optional[str], float]:
    """Einfaches Token-Overlap Matching mit Ordnung/Prefix-Bonus; gibt Score zurück."""
    q = normalize_name_key(dienstnehmer)
    if not q:
        return None, None, 0.0
    q_tokens = q.split()
    if not q_tokens:
        return None, None, 0.0
    best = (0.0, None, None)  # score, id, name
    for did, cname in driver_id_to_name.items():
        t = normalize_name_key(cname)
        t_tokens = t.split()
        if not t_tokens:
            continue
        inter = len(set(q_tokens) & set(t_tokens))
        coverage = inter / max(1, len(set(q_tokens)))
        order_bonus = 0.0
        if q_tokens and t_tokens and q_tokens[0] == t_tokens[0]:
            order_bonus += 0.1
        if q_tokens and t_tokens and q_tokens[-1] == t_tokens[-1]:
            order_bonus += 0.1
        prefix_bonus = 0.0
        for tok in q_tokens:
            if any(tt.startswith(tok) or tok.startswith(tt) for tt in t_tokens):
                prefix_bonus += 0.05
        prefix_bonus = min(prefix_bonus, 0.15)
        score = coverage + order_bonus + prefix_bonus
        if score > best[0]:
            best = (score, did, cname)
    if best[0] >= 0.6:  # konservative Schwelle
        return best[1], best[2], best[0]
    return None, None, best[0]


def import_pdf_fast_test(pdf_path: Path, trace: bool = False, pretty_mode: bool = False) -> Dict[str, object]:
    pdf_path = pdf_path.expanduser().resolve()
    if not pdf_path.exists():
        return {"success": False, "error": f"Datei nicht gefunden: {pdf_path}"}

    m = re.search(r'Abrechnungen?\s+(\d{2})_(\d{4})', pdf_path.name, re.IGNORECASE)
    if not m:
        return {"success": False, "error": "Ungültiger Dateiname (erwartet z. B. Abrechnungen 06_2025.pdf)"}
    month = int(m.group(1))
    year = int(m.group(2))
    table = f"{year}_{month:02d}_FASTTEST"

    # 1) Plumber first
    plumber_texts = plumber_extract_page_texts(pdf_path)
    # Dokument-Defaults aus erster Seite
    doc_dn_default = ''
    doc_dnnr_default = ''
    if 1 in plumber_texts and plumber_texts[1].strip():
        dn_d, dnnr_d = _find_page_header_fields(plumber_texts[1])
        doc_dn_default, doc_dnnr_default = dn_d, dnnr_d
    # positionsbasierte Defaults, falls nötig
    if not doc_dn_default or not doc_dnnr_default:
        dn_p, dnnr_p = plumber_header_from_page(pdf_path, 1, trace=trace)
        if dn_p and not doc_dn_default:
            doc_dn_default = dn_p
        if dnnr_p and not doc_dnnr_default:
            doc_dnnr_default = dnnr_p

    # 2) Bilder nur für Seiten ohne brauchbaren Text
    images = []
    try:
        if any(not (plumber_texts.get(i, "").strip()) for i in range(1, len(plumber_texts) + 1)):
            images = convert_from_path(str(pdf_path), dpi=350, poppler_path=POPPLER_PATH)
    except Exception as e:
        # Fallback: komplette OCR
        images = convert_from_path(str(pdf_path), dpi=350, poppler_path=POPPLER_PATH)

    all_entries: List[PayrollEntry] = []
    pretty = PrettyTracer() if pretty_mode else None
    num_pages = max(len(plumber_texts), len(images)) or 0
    for i in range(1, num_pages + 1):
        text = plumber_texts.get(i, "")
        if not text.strip() and images:
            # OCR nur wenn nötig
            img = images[i - 1] if i - 1 < len(images) else None
            if img is not None:
                text = ocr_page_to_text(img)
        if not text.strip():
            continue
        # Per-Seite Header per Text- und Positionssuche bestimmen
        dn_def, dnnr_def = _find_page_header_fields(text)
        if not dn_def or not dnnr_def:
            dn_p, dnnr_p = plumber_header_from_page(pdf_path, i, trace=trace, pretty=pretty)
            dn_def = dn_def or dn_p
            dnnr_def = dnnr_def or dnnr_p
        entries = extract_entries_from_text(text, i, trace=trace, defaults=(dn_def or doc_dn_default, dnnr_def or doc_dnnr_default), pretty=pretty)
        all_entries.extend(entries)

    # 3) Fahrer-Cache laden
    driver_id_to_name, name_key_to_id = load_driver_cache()

    # 4) In Test-DB schreiben (eigene Tabelle)
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(TEST_DB_PATH))
    cur = conn.cursor()
    cur.execute(
        f'''
        CREATE TABLE IF NOT EXISTS "{table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER,
            dienstnehmer TEXT,
            dn_nr TEXT,
            brutto REAL,
            zahlbetrag REAL,
            page_number INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    # Unique-Index und REPLACE für Dublettenvermeidung (bevorzugt driver_id, sonst Name)
    try:
        cur.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_uniq ON "{table}" (COALESCE(driver_id, -1), dienstnehmer, dn_nr, page_number)')
    except Exception:
        pass

    inserted = 0
    for e in all_entries:
        # 3.1 DN-Nr.-Priorität
        driver_id: Optional[int] = None
        canonical_name: Optional[str] = None
        dn = (e.dn_nr or '').strip()
        if dn.isdigit():
            did = int(dn)
            if did in driver_id_to_name:
                driver_id = did
                canonical_name = driver_id_to_name[did]
            else:
                # Fallback: DN-Nr. = driver_id laut Schema → setze dennoch driver_id
                driver_id = did
        # 3.2 Exakt-/Norm-Match nach Name (inkl. vertauschter Reihenfolge)
        if driver_id is None and e.dienstnehmer:
            q = normalize_name_key(e.dienstnehmer)
            # exakte Normalform
            for did, cname in driver_id_to_name.items():
                if normalize_name_key(cname) == q:
                    driver_id, canonical_name = did, cname
                    break
            # Vorname/Nachname getauscht testen
            if driver_id is None and ' ' in q:
                parts = q.split()
                swapped = f"{parts[-1]} {' '.join(parts[:-1])}".strip()
                for did, cname in driver_id_to_name.items():
                    if normalize_name_key(cname) == swapped:
                        driver_id, canonical_name = did, cname
                        break
        # 3.3 Fuzzy, falls noch nicht gematcht
        match_score = 0.0
        if driver_id is None:
            driver_id, canonical_name, match_score = fuzzy_match_scored(e.dienstnehmer, driver_id_to_name)
        name_to_store = canonical_name or e.dienstnehmer

        if trace:
            print(f"[TRACE] match p{e.page_number}: dn='{e.dienstnehmer}' dn_nr='{e.dn_nr}' -> driver_id={driver_id} name='{name_to_store}' score={match_score:.2f}")
        if pretty is not None:
            pretty.record_match(e.page_number, driver_id, name_to_store, match_score)

        cur.execute(
            f'INSERT OR REPLACE INTO "{table}" (driver_id, dienstnehmer, dn_nr, brutto, zahlbetrag, page_number) VALUES (?, ?, ?, ?, ?, ?)',
            (driver_id, name_to_store, e.dn_nr, e.brutto, e.zahlbetrag, e.page_number)
        )
        inserted += 1
    conn.commit()
    conn.close()

    if pretty is not None:
        pretty.print_summary()
    return {"success": True, "table": table, "inserted": inserted, "pages": num_pages}


def main():
    if len(sys.argv) < 2:
        print("Nutzung: python salary_import_tool_fast_test.py <Abrechnung.pdf>")
        sys.exit(2)
    pdf = Path(sys.argv[1])
    trace = any(arg in ('--trace', '-t') for arg in sys.argv[2:])
    pretty_mode = any(arg in ('--pretty', '-p') for arg in sys.argv[2:])
    res = import_pdf_fast_test(pdf, trace=trace, pretty_mode=pretty_mode)
    if not res.get("success"):
        print(f"❌ {res.get('error')}")
        sys.exit(1)
    print(f"✅ Test-Import OK: Tabelle={res['table']} | Einträge={res['inserted']} | Seiten={res['pages']}")
    print(f"➡️ Test-DB: {TEST_DB_PATH}")


if __name__ == "__main__":
    main()


