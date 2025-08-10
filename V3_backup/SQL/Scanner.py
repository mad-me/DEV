#!/usr/bin/env python3
"""
Verbesserter PDF-Scanner für Abrechnungen mit robuster OCR-Pipeline.

Funktionen:
- Erzeugt zuerst Text via pdfplumber (wenn PDF digitalen Text enthält)
- Fallback: OCR mit hohem DPI und Bildvorverarbeitung (OpenCV, falls vorhanden)
- Extrahiert Felder: Dienstnehmer, DN-Nr., Brutto, Zahlbetrag
- Schreibt in SQL/salaries.db in Tabelle "YYYY_MM"

Hinweis: ARF/FL werden hier nicht umgesetzt. Für diese Fälle bitte
SQL/Flughafenfahrten.py implementieren oder Router-Fallback verwenden.
"""

from __future__ import annotations

import re
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    from pdf2image import convert_from_path
except Exception:
    convert_from_path = None

try:
    import pytesseract
except Exception:
    pytesseract = None

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None


def _extract_text_pdf_first(pdf_path: Path) -> str:
    text = ""
    if pdfplumber is not None:
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                parts = []
                for page in pdf.pages:
                    t = page.extract_text(x_tolerance=1, y_tolerance=1) or ""
                    parts.append(t)
                text = "\n".join(parts)
                if len(text.strip()) > 200:
                    return text
        except Exception:
            pass
    # keine ausreichenden Texte, OCR später
    return text


def _preprocess_for_ocr(pil_image):
    if cv2 is None or np is None:
        return pil_image
    # Graustufen
    gray = pil_image.convert('L')
    img = np.array(gray)
    # leichte Schärfung
    blur = cv2.GaussianBlur(img, (0, 0), 1.2)
    sharp = cv2.addWeighted(img, 1.6, blur, -0.6, 0)
    # adaptive Threshold
    thr = cv2.adaptiveThreshold(
        sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 10
    )
    # Deskew
    coords = np.column_stack(np.where(thr < 255))
    if coords.size > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        (h, w) = thr.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        thr = cv2.warpAffine(thr, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return thr


def _ocr_pages(pdf_path: Path) -> str:
    if convert_from_path is None or pytesseract is None:
        return ""
    # Hoher DPI-Wert für bessere OCR
    try:
        images = convert_from_path(str(pdf_path), dpi=500)
    except Exception:
        # Fallback DPI
        images = convert_from_path(str(pdf_path), dpi=350)

    texts = []
    for img in images:
        pre = _preprocess_for_ocr(img)
        # Kernkonfiguration: LSTM, Deutsch, hoher DPI
        config_base = "--oem 1 -l deu --dpi 500"
        try:
            # PSM 6 zuerst
            t6 = pytesseract.image_to_string(pre, config=f"{config_base} --psm 6")
            if t6 and len(t6.strip()) > 20:
                texts.append(t6)
                continue
            # PSM 11 als Fallback
            t11 = pytesseract.image_to_string(pre, config=f"{config_base} --psm 11")
            texts.append(t11)
        except Exception:
            try:
                texts.append(pytesseract.image_to_string(img, lang='deu', config='--oem 1 --psm 6'))
            except Exception:
                texts.append("")
    return "\n".join(texts)


def _extract_fields(full_text: str, filename: str = "") -> dict[str, str]:
    # Einheitliche Whitespaces
    text = full_text.replace('\xa0', ' ')

    flags = re.IGNORECASE | re.DOTALL

    # Mehr Varianten der Labels zulassen
    dienstnehmer_patterns = [
        r'Dienstnehmer(?:/in|In)?\W*[:\-]?\s*(.*?)\s*(?=DN[\-\s]?Nr)',
        r'Dienstnehmer(?:/in|In)?\W*[:\-]?\s*([^\n\r]+)'
    ]
    dn_nr_patterns = [
        r'DN[\-\s]?Nr\.?\W*[:\-]?\s*(\d+)',
        r'DNr\.?\W*[:\-]?\s*(\d+)',
        r'Personalnummer\W*[:\-]?\s*(\d+)'
    ]
    brutto_patterns = [
        r'Brutto(?:bezüge|summe)?\W*[:\-]?\s*(\d+[\d\.,]*)',
        r'Bruttobezüge\W*[:\-]?\s*(\d+[\d\.,]*)'
    ]
    zahlbetrag_patterns = [
        r'Zahlbetrag\W*[:\-]?\s*(\d+[\d\.,]*)',
        r'Auszahlungsbetrag\W*[:\-]?\s*(\d+[\d\.,]*)',
        r'Überweisungsbetrag\W*[:\-]?\s*(\d+[\d\.,]*)'
    ]

    def first_match(patterns_list):
        for pat in patterns_list:
            m = re.search(pat, text, flags)
            if m:
                return m.group(1).strip()
        return ''

    result = {
        'Dienstnehmer': first_match(dienstnehmer_patterns),
        'DN-Nr.': first_match(dn_nr_patterns),
        'Brutto': first_match(brutto_patterns),
        'Zahlbetrag': first_match(zahlbetrag_patterns)
    }

    # Fallback: DN-Nr. aus Dateinamen extrahieren (lange Ziffernfolge)
    if not result['DN-Nr.'] and filename:
        m = re.search(r'(\d{7,})', filename)
        if m:
            result['DN-Nr.'] = m.group(1)

    # Zusätzliche Heuristik zeilenbasiert, falls leer
    if not any(result.values()):
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        # Dienstnehmer: erste Zeile mit Label
        for ln in lines:
            if re.search(r'Dienstnehmer', ln, re.IGNORECASE):
                # Wert ist Rest der Zeile nach ':' oder der ganze Teil ohne Label
                if ':' in ln:
                    result['Dienstnehmer'] = ln.split(':', 1)[1].strip()
                else:
                    result['Dienstnehmer'] = re.sub(r'Dienstnehmer(?:/in|In)?', '', ln, flags=re.IGNORECASE).strip()
                break
        # DN-Nr
        if not result['DN-Nr.']:
            for ln in lines:
                m = re.search(r'(DN[\-\s]?Nr\.?|DNr\.?|Personalnummer)\W*[:\-]?\s*(\d+)', ln, re.IGNORECASE)
                if m:
                    result['DN-Nr.'] = m.group(2)
                    break
        # Brutto
        if not result['Brutto']:
            for ln in lines:
                m = re.search(r'Brutto\W*[:\-]?\s*(\d+[\d\.,]*)', ln, re.IGNORECASE)
                if m:
                    result['Brutto'] = m.group(1)
                    break
        # Zahlbetrag
        if not result['Zahlbetrag']:
            for ln in lines:
                m = re.search(r'(Zahlbetrag|Auszahlungsbetrag|Überweisungsbetrag)\W*[:\-]?\s*(\d+[\d\.,]*)', ln, re.IGNORECASE)
                if m:
                    result['Zahlbetrag'] = m.group(2)
                    break

    return result


def _to_float(val: str) -> float | None:
    try:
        s = str(val).replace('.', '').replace(',', '.')
        return float(s)
    except Exception:
        return None


def process_abrechnung(pdf_path: Path) -> dict:
    # 1) Text direkt aus PDF
    text = _extract_text_pdf_first(pdf_path)
    # 2) Fallback OCR
    if len(text.strip()) < 100:
        text = _ocr_pages(pdf_path)
    fields = _extract_fields(text, filename=pdf_path.name)
    return fields


# === FUNK-RECHNUNG (Gesamt Kennung ...) ===
def _parse_number(token: str) -> float | None:
    try:
        return float(token.replace('.', '').replace(',', '.'))
    except Exception:
        return None


def _slice_relevant_text(full_text: str) -> str:
    """Schneidet den für die Abrechnung relevanten Bereich heraus:
    Von der Zeile mit "Einzelposten zu Rechnung" bis zur Zeile, die mit
    "Gesamt " beginnt (Gesamt-Summe), exklusiv der Gesamt-Zeile.
    Fällt zurück auf den gesamten Text, wenn Marker nicht gefunden werden.
    """
    raw_lines = full_text.splitlines()
    start_idx = None
    end_idx = None
    for i, ln in enumerate(raw_lines):
        if start_idx is None and re.search(r"Einzelposten\s+zu\s+Rechnung", ln, re.IGNORECASE):
            start_idx = i
        # Finale Gesamtzeile beginnt typischerweise mit "Gesamt " und hat zwei Beträge
        if re.match(r"\s*Gesamt\s+\d|\s*Gesamt\s+\d{1,3}[\s\d\.,]*", ln):
            end_idx = i
            break
        if re.match(r"\s*Gesamt\s+$", ln):
            end_idx = i
            break
    if start_idx is not None and end_idx is not None and end_idx > start_idx:
        return "\n".join(raw_lines[start_idx:end_idx])
    return full_text


def _parse_gesamt_kennung_lines(full_text: str, trace: bool = False) -> list[dict]:
    # Nur relevanten Bereich betrachten
    sliced = _slice_relevant_text(full_text)
    lines = [ln.strip() for ln in sliced.splitlines() if ln.strip()]
    results: list[dict] = []

    # Betrag mit optionalen Tausendern per Punkt ODER Leerzeichen (z. B. 1 197,23)
    AMT = r'(?<!\d)(?:\d{1,3}(?:[\.\s]\d{3})*|\d+),\d{2}(?!\d)'
    pattern = re.compile(rf'^\s*Gesamt\s+Kennung\s+([A-Z0-9]+)(.*)$', re.IGNORECASE)

    for ln in lines:
        if 'kennung' not in ln.lower():
            continue
        m = pattern.search(ln)
        if m:
            kennung = m.group(1)
            tail = m.group(2)
            amounts = re.findall(AMT, tail)
            # Filtere die MWSt-Prozentspalte (genau 20,00) konsequent heraus
            amounts = [a for a in amounts if a.strip() != '20,00']
            if trace:
                print(f"[TRACE] line='{ln}' | amounts_raw={re.findall(AMT, tail)} | amounts_filtered={amounts}")
            # Falls 3 Beträge (Netto, MWSt, Brutto) vorhanden: nimm 1. und letzten
            if len(amounts) >= 3:
                # Wähle das Paar (n,b), das am besten n*1.2 ≈ b erfüllt
                best = None
                vals = [(_parse_number(a), a) for a in amounts]
                for i in range(len(vals)):
                    for j in range(i+1, len(vals)):
                        n, ns = vals[i]
                        b, bs = vals[j]
                        if n is None or b is None:
                            continue
                        if n <= 0 or b <= 0:
                            continue
                        # Toleranz 0.5 EUR
                        if abs(b - (n * 1.2)) <= 0.5:
                            best = (ns, bs, n, b)
                if best:
                    _, _, n, b = best
                    if trace:
                        print(f"[TRACE] picked plausibility pair kennung={kennung} netto={n} brutto={b}")
                    results.append({'kennung': kennung, 'netto': n, 'brutto': b})
                    continue
                # Fallback: erster und letzter
                netto_s, brutto_s = amounts[0], amounts[-1]
                if trace:
                    print(f"[TRACE] picked first/last kennung={kennung} netto={netto_s} brutto={brutto_s}")
                results.append({'kennung': kennung, 'netto': _parse_number(netto_s), 'brutto': _parse_number(brutto_s)})
                continue
            # Falls 2 Beträge: nimm beide als Netto/Brutto
            if len(amounts) == 2:
                netto_s, brutto_s = amounts[0], amounts[1]
                if trace:
                    print(f"[TRACE] picked two-values kennung={kennung} netto={netto_s} brutto={brutto_s}")
                results.append({'kennung': kennung, 'netto': _parse_number(netto_s), 'brutto': _parse_number(brutto_s)})
                continue

        # Fallback: finde Kennung und die letzten zwei Beträge per findall
        if re.search(r'^\s*Gesamt\s+Kennung\s+', ln, re.IGNORECASE):
            # Kennung grob extrahieren
            km = re.search(r'^\s*Gesamt\s+Kennung\s+([A-Z0-9]+)', ln, re.IGNORECASE)
            kennung = km.group(1) if km else ''
            amounts = [a for a in re.findall(AMT, ln) if a.strip() != '20,00']
            if len(amounts) >= 2:
                netto_s, brutto_s = amounts[-2], amounts[-1]
                if trace:
                    print(f"[TRACE] fallback-line kennung={kennung} netto={netto_s} brutto={brutto_s}")
                results.append({'kennung': kennung, 'netto': _parse_number(netto_s), 'brutto': _parse_number(brutto_s)})

    return results


def _load_kennung_map_from_db() -> dict:
    """Lädt Mapping Kennung -> Kennzeichen aus SQL/database.db (vehicles.rfrnc → vehicles.license_plate)."""
    mapping = {}
    db_path = Path(__file__).resolve().parent / 'database.db'
    if not db_path.exists():
        return mapping
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT rfrnc, license_plate FROM vehicles WHERE rfrnc IS NOT NULL AND rfrnc != ''")
        for rfrnc, license_plate in cur.fetchall():
            r = (rfrnc or '').strip()
            lp = (license_plate or '').strip()
            if r and lp:
                mapping[r] = lp
        conn.close()
    except Exception:
        pass
    return mapping


def save_to_funk_db(entries: list[dict], month: int, year: int, trace: bool = False) -> None:
    db_path = Path(__file__).resolve().parent / 'funk.db'
    table = f'{month:02d}_{str(year)[-2:]}'
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        f'''CREATE TABLE IF NOT EXISTS "{table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kennzeichen TEXT,
            netto REAL,
            brutto REAL
        )'''
    )

    # Stelle sicher, dass die Spalte 'brutto' existiert (Migration alter Tabellen)
    try:
        cur.execute(f'PRAGMA table_info("{table}")')
        cols = [row[1] for row in cur.fetchall()]
        if 'brutto' not in cols:
            cur.execute(f'ALTER TABLE "{table}" ADD COLUMN brutto REAL')
    except Exception:
        pass

    mapping = _load_kennung_map_from_db()
    if trace:
        print(f"[TRACE] mapping_size={len(mapping)}")

    for e in entries:
        kennung = e.get('kennung') or ''
        netto = e.get('netto')
        brutto = e.get('brutto')
        if netto is None:
            continue
        kennzeichen = mapping.get(kennung, kennung)
        if trace:
            print(f"[TRACE] write kennung={kennung} -> kennzeichen={kennzeichen} | netto={netto} | brutto={brutto}")
        # Ersetze vorhandene Zeile für dasselbe Kennzeichen
        cur.execute(f'DELETE FROM "{table}" WHERE kennzeichen = ?', (kennzeichen,))
        cur.execute(
            f'INSERT INTO "{table}" (kennzeichen, netto, brutto) VALUES (?, ?, ?)',
            (kennzeichen, float(netto), float(brutto) if brutto is not None else None)
        )

    conn.commit()
    conn.close()


def process_funk_invoice(pdf_path: Path, trace: bool = False) -> list[dict]:
    text = _extract_text_pdf_first(pdf_path)
    if len(text.strip()) < 100:
        text = _ocr_pages(pdf_path)
    entries = _parse_gesamt_kennung_lines(text, trace=trace)
    return entries


def detect_month_year_from_name(name: str) -> tuple[int, int] | None:
    m = re.search(r'(\d{2})_(\d{4})', name)
    if m:
        month = int(m.group(1))
        year = int(m.group(2))
        if 1 <= month <= 12:
            return month, year
    return None


def save_to_salaries_db(fields: dict, month: int, year: int) -> None:
    db_path = Path(__file__).resolve().parent / 'salaries.db'
    table = f'{year}_{month:02d}'
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        f'''CREATE TABLE IF NOT EXISTS "{table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dienstnehmer TEXT,
            dn_nr TEXT,
            brutto REAL,
            zahlbetrag REAL
        )'''
    )
    cur.execute(
        f'INSERT INTO "{table}" (dienstnehmer, dn_nr, brutto, zahlbetrag) VALUES (?, ?, ?, ?)',
        (
            fields.get('Dienstnehmer', ''),
            fields.get('DN-Nr.', ''),
            _to_float(fields.get('Brutto')),
            _to_float(fields.get('Zahlbetrag')),
        )
    )
    conn.commit()
    conn.close()


def main():
    if len(sys.argv) < 2:
        print('📂 Kein Pfad angegeben – Abbruch.')
        sys.exit(2)

    pdf_path = Path(sys.argv[1]).expanduser().resolve()
    if not pdf_path.exists():
        print(f'⚠️ Datei nicht gefunden: {pdf_path}')
        sys.exit(1)

    # Optional: Volltext-Dump für Debugging
    if any(arg in ('--dump', '-d') for arg in sys.argv[2:]):
        text = _extract_text_pdf_first(pdf_path)
        if len(text.strip()) < 100:
            text = _ocr_pages(pdf_path)
        print('----- BEGIN SCANNER FULLTEXT -----')
        for i, line in enumerate(text.splitlines(), start=1):
            print(f"{i:04d}: {line}")
        print('----- END SCANNER FULLTEXT -----')
        sys.exit(0)

    name_upper = pdf_path.name.upper()
    if 'FL' in name_upper:
        # FL bleibt Debug-Ausgabe (sofern benötigt). ARF wird jetzt wie Funk verarbeitet.
        print('[INFO] FL erkannt – extrahiere Volltext (kein strukturierter Import).')
        text = _extract_text_pdf_first(pdf_path)
        if len(text.strip()) < 100:
            text = _ocr_pages(pdf_path)
        preview = text if len(text) <= 4000 else text[:4000] + '\n[...]'
        print('----- BEGIN OCR TEXT -----')
        print(preview)
        print('----- END OCR TEXT -----')
        sys.exit(0)

    # Monat/Jahr aus Dateiname oder aktuelles Datum
    my = detect_month_year_from_name(pdf_path.name)
    if my is None:
        now = datetime.now()
        my = (now.month, now.year)
    month, year = my

    # 1) Funk-Rechnung erkennen (Gesamt Kennung ...)
    trace_mode = any(arg in ('--trace', '-t') for arg in sys.argv[2:])
    entries = process_funk_invoice(pdf_path, trace=trace_mode)
    if entries:
        print(f"[INFO] Erkannte Funk-Rechnung mit {len(entries)} Eintrag(en)")
        save_to_funk_db(entries, month, year, trace=trace_mode)
        print('[OK] Funk-Rechnung gespeichert')
        sys.exit(0)

    # 2) Abrechnung (Gehalt) als Fallback
    print(f'[INFO] Scanne Abrechnung: {pdf_path.name} (Ziel: {year}_{month:02d})')
    fields = process_abrechnung(pdf_path)
    if not any(fields.values()):
        print('[FEHLER] Keine relevanten Felder erkannt')
        sys.exit(1)

    print(f"[INFO] Gefunden: Dienstnehmer='{fields.get('Dienstnehmer','')}', DN-Nr.='{fields.get('DN-Nr.','')}', Brutto='{fields.get('Brutto','')}', Zahlbetrag='{fields.get('Zahlbetrag','')}'")
    save_to_salaries_db(fields, month, year)
    print('[OK] Abrechnung gespeichert')
    sys.exit(0)


if __name__ == '__main__':
    main()


