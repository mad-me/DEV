"""
Isolierter Test für OCR-Auslesen und Fahrermatching von Gehaltsabrechnungen.

Nutzung (Beispiele):

  python salary_extract_match_debug.py --pdf "SQL/x/Abrechnungen/Abrechnungen 07_2025.pdf"
  python salary_extract_match_debug.py --pdf "C:/Pfad/zu/Abrechnungen 07_2025.pdf" --pages 2-5 --export out.csv

Standardmäßig werden KEINE Daten in die Datenbank geschrieben. Es wird lediglich
ausgelesen und gematcht und eine Übersicht in der Konsole (und optional CSV) erzeugt.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sqlite3
import re

from salary_import_tool import SalaryImportTool, POPPLER_PATH
from pdf2image import convert_from_path


def parse_page_range(pages_arg: Optional[str], total_pages: int) -> List[int]:
    if not pages_arg:
        return list(range(1, total_pages + 1))
    pages_arg = pages_arg.strip()
    result: List[int] = []
    for part in pages_arg.split(','):
        part = part.strip()
        if '-' in part:
            start_str, end_str = part.split('-', 1)
            try:
                start = int(start_str)
                end = int(end_str)
            except ValueError:
                continue
            if start <= end:
                result.extend(range(start, end + 1))
        else:
            try:
                result.append(int(part))
            except ValueError:
                continue
    # Begrenzen auf gültigen Bereich
    result = [p for p in result if 1 <= p <= total_pages]
    # Deduplizieren und sortieren
    return sorted(set(result))


def analyze_pdf(pdf_path: Path, drivers_db: Path, pages: Optional[str], export_csv: Optional[Path], dump_text: bool, top_k: int = 0) -> None:
    # Tool mit beliebigen DB-Pfaden erzeugen; wir speichern NICHTS, nutzen nur OCR + Matching
    tool = SalaryImportTool(salaries_db_path=Path(':memory:'), drivers_db_path=drivers_db)

    # PDF → Bilder
    images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
    selected_pages = parse_page_range(pages, len(images))

    rows: List[Dict] = []
    page_texts: Dict[int, str] = {}
    for page_number in selected_pages:
        img = images[page_number - 1]
        # OCR-Text optional sammeln
        try:
            page_texts[page_number] = tool.extract_text_optimized(img)
        except Exception:
            page_texts[page_number] = ''
        entries = tool.process_single_page(img, page_number)

        # Fallback: Wenn keine Einträge erkannt, versuche heuristische Extraktion aus OCR-Text
        if not entries and page_texts[page_number]:
            txt = page_texts[page_number]
            # Normalisiere Zeilen
            lines = [ln.strip() for ln in txt.split('\n') if ln.strip()]
            # Name: nach 'Dienstnehme(r/in)' suchen, ggf. nächste Zeile als Name
            name = None
            for i, ln in enumerate(lines):
                if re.search(r'Dienstnehme(?:r(?:/in|In)?)?\b', ln, re.IGNORECASE):
                    # Versuche Name aus derselben Zeile bis vor "DN-Nr" zu extrahieren
                    m = re.search(r'Dienstnehme(?:r(?:/in|In)?)?\W*[:\-]?\s*(.*)$', ln, re.IGNORECASE)
                    candidate = (m.group(1) or '').strip() if m else ''
                    if candidate:
                        # hart vor DN-Block abschneiden
                        candidate = re.split(r'\bDN[- ]?Nr', candidate, flags=re.IGNORECASE)[0].strip()
                    # Validierungsheuristik für Namen: keine Adress-Zeichen (Zahl/Komma) und >=2 Wörter
                    if candidate and not re.search(r'[\d,]', candidate) and len(candidate.split()) >= 2:
                        name = candidate
                    else:
                        # nächste Zeile prüfen, nur wenn sie wie ein Name aussieht
                        if i + 1 < len(lines):
                            nl = lines[i + 1].strip()
                            if nl and not re.search(r'^DN[- ]?Nr', nl, re.IGNORECASE) and not re.search(r'[\d,]', nl) and len(nl.split()) >= 2:
                                name = nl
                    break
            # DN-Nr
            dn_nr = ''
            for ln in lines:
                m = re.search(r'DN[- ]?Nr\.?\W*[:\-]?\s*(\d+)', ln, re.IGNORECASE)
                if m:
                    dn_nr = m.group(1)
                    break
            # Brutto
            brutto = 0.0
            for ln in lines:
                m = re.search(r'Brutto(?:-?Bezug)?\W*[:\-]?\s*([\d\.,]+)', ln, re.IGNORECASE)
                if m:
                    brutto_str = m.group(1)
                    try:
                        brutto = float(brutto_str.replace(' ', '').replace('.', '').replace(',', '.'))
                    except Exception:
                        brutto = 0.0
                    break
            # Zahlbetrag/Netto/Auszahlungsbetrag
            zahlbetrag = 0.0
            for ln in lines:
                m = re.search(r'(?:Zahlbetrag|Auszahlungsbetrag|Netto(?:betrag)?)\W*[:\-]?\s*([\d\.,]+)', ln, re.IGNORECASE)
                if m:
                    zb_str = m.group(1)
                    try:
                        zahlbetrag = float(zb_str.replace(' ', '').replace('.', '').replace(',', '.'))
                    except Exception:
                        zahlbetrag = 0.0
                    break
            # Im Debug-Fallback auch ohne DN-Nr einen Eintrag erzeugen, wenn Name und Beträge vorhanden sind
            if name:
                entries = [type('E', (), {
                    'dienstnehmer': name,
                    'dn_nr': dn_nr,
                    'brutto': brutto,
                    'zahlbetrag': zahlbetrag,
                    'page_number': page_number,
                    'confidence': 0.6,
                })()]

        for entry in entries:
            # DN-Nr → driver_id (Primärregel)
            match_source = ''
            driver_id = None
            canonical_name = None
            dn = str(getattr(entry, 'dn_nr', '') or '').strip()
            if dn.isdigit():
                dn_int = int(dn)
                if dn_int in tool.driver_id_to_name:
                    driver_id = dn_int
                    canonical_name = tool.driver_id_to_name[dn_int]
                    match_source = 'dn_nr'
            # Fuzzy nur wenn kein DN-Match
            if driver_id is None:
                driver_id, canonical_name = tool.match_driver_optimized(entry.dienstnehmer)
                if canonical_name:
                    match_source = 'fuzzy'
            tokens = tool.normalize_name(entry.dienstnehmer)
            rows.append({
                'page': page_number,
                'dienstnehmer_raw': entry.dienstnehmer,
                'dienstnehmer_matched': canonical_name or '',
                'driver_id': driver_id if driver_id is not None else '',
                'dn_nr': entry.dn_nr,
                'brutto': entry.brutto,
                'zahlbetrag': entry.zahlbetrag,
                'confidence': entry.confidence,
                'tokens': ' '.join(tokens),
                'match_source': match_source,
            })

    # Optional: OCR-Rohtext dumpen
    if dump_text:
        print("\n===== OCR-Text (Roh) =====")
        for p in selected_pages:
            txt = page_texts.get(p, '') or ''
            print(f"\n--- Seite {p} ---\n{txt}")

    # Ausgabe
    if not rows:
        print("Keine Einträge erkannt.")
        return

    # Konsolen-Tabelle
    headers = [
        'page', 'dienstnehmer_raw', 'dienstnehmer_matched', 'driver_id',
        'dn_nr', 'brutto', 'zahlbetrag', 'confidence', 'tokens', 'match_source'
    ]
    widths = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}
    line = ' | '.join(h.ljust(widths[h]) for h in headers)
    sep = '-+-'.join('-' * widths[h] for h in headers)
    print(line)
    print(sep)
    for r in rows:
        print(' | '.join(str(r[h]).ljust(widths[h]) for h in headers))

    # Erweiterter Matching-Test (Top-N Kandidaten) optional anzeigen
    if top_k and int(top_k) > 0:
        top_k = int(top_k)
        print("\n===== Matching-Test (Top-{} Kandidaten) =====".format(top_k))

        def clean_name(name: str) -> str:
            s = str(name).lower().replace('-', ' ').replace('_', ' ')
            s = re.sub(r"\s+", " ", s)
            s = re.sub(r"\bal\s+", "el ", s)
            s = re.sub(r"\bei\b", "el", s)
            return s.strip()

        def levenshtein_distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

        def fuzzy_match_score(search_name: str, target_name: str, max_distance: int = 3) -> Tuple[float, float, bool]:
            if not search_name or not target_name:
                return 0.0, 0.0, False
            if search_name == target_name:
                return 100.0, 1.0, True
            search_tokens = clean_name(search_name).split()
            target_tokens = clean_name(target_name).split()
            def extend_tokens(tokens: List[str]) -> List[str]:
                ext = tokens.copy()
                for i, token in enumerate(tokens):
                    if token == 'el' and i + 1 < len(tokens):
                        ext.append('el' + tokens[i + 1])
                for i in range(len(tokens) - 1):
                    ext.append(tokens[i] + tokens[i + 1])
                return ext
            s_ext = extend_tokens(search_tokens)
            t_ext = extend_tokens(target_tokens)
            set_s, set_t = set(s_ext), set(t_ext)
            inter = set_s & set_t
            union = set_s | set_t
            inter_size = len(inter)
            if inter_size == 0 and levenshtein_distance(search_name, target_name) > max_distance:
                return 0.0, 0.0, False
            dice = (2 * inter_size) / max(1, (len(set_s) + len(set_t)))
            jaccard = inter_size / max(1, len(union))
            coverage = inter_size / max(1, len(set_s))
            order_ok = False
            if search_tokens and target_tokens and search_tokens[0] == target_tokens[0]:
                order_ok = True
            if search_tokens and target_tokens and search_tokens[-1] == target_tokens[-1]:
                order_ok = True
            if search_tokens and target_tokens and sorted(search_tokens) == sorted(target_tokens):
                order_ok = True
            prefix_bonus = 0.0
            for st in search_tokens:
                if any(tt.startswith(st) or st.startswith(tt) for tt in target_tokens):
                    prefix_bonus += 2.0
            prefix_bonus = min(prefix_bonus, 8.0)
            arabic_bonus = 0.0
            if any(t == 'el' or t.startswith('el') for t in search_tokens) and any(t == 'el' or t.startswith('el') for t in target_tokens):
                arabic_bonus = 20.0
            dist = levenshtein_distance(search_name, target_name)
            max_len = max(len(search_name), len(target_name))
            norm_dist = (dist / max_len) if max_len else 1.0
            distance_score = max(0.0, 100.0 - (norm_dist * 100.0)) / 100.0
            base = (0.55 * dice + 0.20 * coverage + 0.10 * jaccard + 0.15 * distance_score) * 100.0
            score = float(max(0.0, min(100.0, base + prefix_bonus + (8.0 if order_ok else 0.0))))
            return score, coverage, order_ok

        conn = sqlite3.connect(str(drivers_db))
        cur = conn.cursor()
        cur.execute("SELECT driver_id, first_name, last_name FROM drivers")
        candidates = [(int(r[0]) if r[0] is not None else None, f"{r[1] or ''} {r[2] or ''}".strip()) for r in cur.fetchall()]

        for r in rows:
            name = r['dienstnehmer_raw']
            scores: List[Tuple[float, float, int, str]] = []
            for did, label in candidates:
                s, cov, _ = fuzzy_match_score(name, label)
                scores.append((s, cov, did or -1, label))
            scores.sort(key=lambda x: (x[0], x[1]), reverse=True)
            top = scores[:top_k]
            print(f"\nSeite {r['page']} | '{name}' → Top-{top_k} Vorschläge:")
            for s, cov, did, label in top:
                print(f"  - {label} (id={did if did!=-1 else ''}) | Score={s:.1f}, Coverage={cov:.2f}")

        conn.close()

    # CSV-Export
    if export_csv:
        export_csv.parent.mkdir(parents=True, exist_ok=True)
        with export_csv.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow({h: r[h] for h in headers})
        print(f"CSV exportiert: {export_csv}")


def main():
    # Windows-Konsole: UTF-8 erzwingen, wenn möglich
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description='Isolierter OCR- und Matching-Test für Gehalts-PDFs (ohne DB-Speicherung).')
    parser.add_argument('--pdf', required=True, help='Pfad zur Gehaltsabrechnungs-PDF')
    parser.add_argument('--drivers-db', default=str(Path(__file__).parent / 'SQL' / 'database.db'), help='Pfad zur Fahrer-Stammdatenbank (SQLite)')
    parser.add_argument('--pages', default=None, help='Seiten-Selektion, z. B. "1-3,7"')
    parser.add_argument('--export', default=None, help='Optionaler CSV-Export-Pfad')
    parser.add_argument('--top', default="0", help='Zeigt Matching-Test mit Top-N Kandidaten (0 = aus)')
    parser.add_argument('--dump-text', action='store_true', help='OCR-Rohtext der ausgewählten Seiten ausgeben')
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    drivers_db = Path(args.drivers_db)
    export_csv = Path(args.export) if args.export else None

    if not pdf_path.exists():
        print(f"PDF nicht gefunden: {pdf_path}")
        sys.exit(1)
    if not drivers_db.exists():
        print(f"Drivers-DB nicht gefunden: {drivers_db}")
        sys.exit(1)

    analyze_pdf(pdf_path, drivers_db, args.pages, export_csv, bool(args.dump_text), int(args.top or 0))


if __name__ == '__main__':
    main()


