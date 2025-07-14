#!/usr/bin/env python3
"""
PDF-Parser für ARF, FL und Gehaltsabrechnungen.
OCR, Strukturierung, Ausgabe in Excel und automatische Ablage der Original-PDFs.
"""

import argparse
import re
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from PyQt6.QtWidgets import QApplication, QFileDialog
from pdf2image import convert_from_path
import pytesseract
from openpyxl import load_workbook
from openpyxl.styles import Font
import sqlite3

from Flughafenfahrten import extract_and_structure

# Monatsnamen
GERMAN_MONTHS = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

# Tesseract & Poppler Pfade
pytesseract.pytesseract.tesseract_cmd = r"C:/Users/moahm/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
POPPLER_PATH = r"C:\Users\moahm\AppData\Local\Programs\poppler-24.08.0\Library\bin"


def get_german_month_name(month: int) -> str:
    if 1 <= month <= 12:
        return GERMAN_MONTHS[month - 1]
    raise ValueError(f"Ungültiger Monatswert: {month}")


def get_previous_month(month: int, year: int) -> tuple[int, int]:
    if month == 1:
        return 12, year - 1
    return month - 1, year


def extract_month_year_from_filename(filename: str, keyword: str) -> tuple[int, int]:
    filename_upper = filename.upper()

    if keyword in ("FL", "ARF"):
        try:
            base = filename_upper.split(keyword)[-1]
            year_part = base[0:2]
            month_part = base[2:4]
            year = int("20" + year_part)
            month = int(month_part)
            if 1 <= month <= 12:
                return month, year
        except Exception:
            pass

    elif keyword == "ABRECHNUNGEN":
        match = re.search(r'Abrechnungen?\s+(\d{2})_(\d{4})', filename, re.IGNORECASE)
        if match:
            month = int(match.group(1))
            year = int(match.group(2))
            if 1 <= month <= 12:
                return month, year

    # Fallback
    print("⚠️ Konnte Monat und Jahr nicht automatisch erkennen.")
    try:
        user_input = input("Bitte Monat eingeben (1–12, Enter = aktueller Monat): ").strip()
        if user_input:
            month = int(user_input)
            if not (1 <= month <= 12):
                raise ValueError
        else:
            month = datetime.now().month
        year = datetime.now().year
        return month, year
    except ValueError:
        print("❌ Ungültige Eingabe. Verwende aktuellen Monat.")
        return datetime.now().month, datetime.now().year


def choose_multiple_files_gui() -> list[Path]:
    downloads_path = Path.home() / "Downloads"
    if not downloads_path.exists():
        downloads_path = Path.home()

    app = QApplication(sys.argv)
    dialog = QFileDialog()
    dialog.setWindowTitle("Bitte PDF-Dateien auswählen")
    dialog.setDirectory(str(downloads_path))
    dialog.setNameFilter("PDF-Dateien (*.pdf)")
    dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

    if dialog.exec():
        return [Path(f) for f in dialog.selectedFiles()]
    return []


def process_fl(pdf_path: Path, base_output_dir: Path):
    month, year = extract_month_year_from_filename(pdf_path.name, "FL")
    month, year = get_previous_month(month, year)
    month_name = get_german_month_name(month)

    output_dir = base_output_dir / month_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"Rechnung_FL_{month_name}.xlsx"

    extract_and_structure(str(pdf_path), str(output_file), "Flughafenfahrten")
    print(f"✅ FL verarbeitet und gespeichert: {output_file}")

    # PDF verschieben
    pdf_target_dir = output_file.parent / "PDF"
    pdf_target_dir.mkdir(exist_ok=True)
    try:
        pdf_path.replace(pdf_target_dir / pdf_path.name)
        print(f"📁 PDF verschoben nach: {pdf_target_dir / pdf_path.name}")
    except Exception as e:
        print(f"⚠️ Konnte PDF nicht verschieben: {e}")


def process_arf(pdf_path: Path, base_output_dir: Path):
    month, year = extract_month_year_from_filename(pdf_path.name, "ARF")
    month, year = get_previous_month(month, year)
    month_name = get_german_month_name(month)

    output_dir = base_output_dir / month_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"Rechnung_ARF_{month_name}.xlsx"

    extract_and_structure(str(pdf_path), str(output_file), "Funk")
    print(f"✅ ARF verarbeitet und gespeichert: {output_file}")

    # PDF verschieben
    pdf_target_dir = output_file.parent / "PDF"
    pdf_target_dir.mkdir(exist_ok=True)
    try:
        pdf_path.replace(pdf_target_dir / pdf_path.name)
        print(f"📁 PDF verschoben nach: {pdf_target_dir / pdf_path.name}")
    except Exception as e:
        print(f"⚠️ Konnte PDF nicht verschieben: {e}")


def normalize_name(name):
    # Nur Buchstaben, alles klein
    return [token for token in re.findall(r'[a-zA-Zäöüß]+', name.lower())]


def match_driver(dienstnehmer, conn):
    tokens = normalize_name(dienstnehmer)
    if not tokens:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT driver_id, first_name, last_name FROM drivers")
    candidates = cursor.fetchall()
    for driver_id, first_name, last_name in candidates:
        driver_tokens = normalize_name(f"{first_name} {last_name}")
        # 2/3-Token-Matching
        match_count = sum(1 for t in tokens if t in driver_tokens)
        if len(tokens) >= 3 and match_count >= 2:
            return driver_id
        elif len(tokens) < 3 and match_count == len(tokens):
            return driver_id
    return None


def process_abrechnung(pdf_path: Path, db_path: Path):
    match = re.search(r'Abrechnungen?\s+(\d{2})_(\d{4})', pdf_path.name, re.IGNORECASE)
    if not match:
        print(f"⚠️ Dateiname {pdf_path.name} entspricht nicht dem Abrechnungs-Muster.")
        return

    month = int(match.group(1))
    year = int(match.group(2))
    table_name = f'{year}_{month:02d}'

    images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
    patterns = {
        'Dienstnehmer': r'Dienstnehmer\W*[:\-]?\s*(.*?)\s*(?=DN[- ]?Nr)',
        'DN-Nr.': r'DN[- ]?Nr\.?\W*[:\-]?\s*(\d+)',
        'Brutto': r'Brutto\W*[:\-]?\s*(\d+[\d\.,]*)',
        'Zahlbetrag': r'Zahlbetrag\W*[:\-]?\s*(\d+[\d\.,]*)'
    }
    flags = re.IGNORECASE | re.DOTALL

    payroll_rows = []
    for img in images:
        text6 = pytesseract.image_to_string(img, lang='deu', config='--psm 6')
        text11 = None
        row = {}
        for key, pat in patterns.items():
            m6 = re.search(pat, text6, flags)
            if m6:
                row[key] = m6.group(1).strip()
            else:
                if text11 is None:
                    text11 = pytesseract.image_to_string(img, lang='deu', config='--psm 11')
                m11 = re.search(pat, text11, flags)
                row[key] = m11.group(1).strip() if m11 else ''
        payroll_rows.append(row)

    # Verbindung zur DB
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    # Tabelle anlegen, falls nicht vorhanden
    c.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER,
        dienstnehmer TEXT,
        dn_nr TEXT,
        brutto REAL,
        zahlbetrag REAL,
        FOREIGN KEY(driver_id) REFERENCES drivers(driver_id)
    )''')
    conn.commit()

    for row in payroll_rows:
        dienstnehmer = row.get('Dienstnehmer', '')
        driver_id = match_driver(dienstnehmer, conn)
        if not driver_id:
            print(f"❗ Kein Fahrer-Match für: '{dienstnehmer}' in Tabelle drivers!")
        # Werte konvertieren
        def to_float(val):
            try:
                return float(val.replace('.', '').replace(',', '.'))
            except Exception:
                return None
        c.execute(f'''INSERT INTO "{table_name}" (driver_id, dienstnehmer, dn_nr, brutto, zahlbetrag) VALUES (?, ?, ?, ?, ?)''',
                  (driver_id, dienstnehmer, row.get('DN-Nr.', ''), to_float(row.get('Brutto', '')), to_float(row.get('Zahlbetrag', ''))))
    conn.commit()
    conn.close()
    print(f"✅ Abrechnung verarbeitet und in Tabelle {table_name} gespeichert.")


PROCESSORS = {
    "FL": process_fl,
    "ARF": process_arf,
    "ABRECHNUNGEN": process_abrechnung
}


def detect_processor(pdf_name: str):
    name_upper = pdf_name.upper()
    for key in PROCESSORS:
        if key in name_upper:
            return PROCESSORS[key], key
    return None, None


def main():
    parser = argparse.ArgumentParser(description="PDF-Verarbeitung für ARF, FL & Abrechnungen.")
    parser.add_argument("pdf_path", nargs='?', type=Path, help="Pfad zur PDF-Datei (optional)")
    parser.add_argument("-b", "--base-dir", type=Path, default=Path(r"C:\EKK\Ausgaben"), help="Basis-Ausgabeverzeichnis")
    parser.add_argument("-o", "--output-name", type=str, help="Nur bei Einzelabrechnung: Dateiname für Excel")

    args = parser.parse_args()

    if args.pdf_path is None:
        print("📂 Kein Pfad angegeben – öffne Dateiauswahldialog...")
        selected_files = choose_multiple_files_gui()
        if not selected_files:
            print("❌ Keine Dateien ausgewählt. Abbruch.")
            exit(1)
    else:
        selected_files = [args.pdf_path.expanduser().resolve()]

    base_dir = args.base_dir.expanduser().resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in selected_files:
        if not pdf_path.is_file():
            print(f"⚠️ Datei nicht gefunden: {pdf_path}")
            continue

        proc_func, key = detect_processor(pdf_path.name)
        if not proc_func:
            print(f"⚠️ Kein gültiges Schlüsselwort in {pdf_path.name}")
            continue

        try:
            if key == "ABRECHNUNGEN":
                month, year = extract_month_year_from_filename(pdf_path.name, key)
                month_name = get_german_month_name(month)
                out_dir = base_dir / month_name
                out_dir.mkdir(parents=True, exist_ok=True)

                if args.output_name and len(selected_files) == 1:
                    output_filename = args.output_name
                else:
                    output_filename = f"Gehaltsabrechnung_{month_name}.xlsx"
                output_path = out_dir / output_filename

                print(f"📢 Speichere Ausgabe unter: {output_path}")
                proc_func(pdf_path, output_path)
            else:
                proc_func(pdf_path, base_dir)

        except Exception as e:
            print(f"❌ Fehler bei Datei {pdf_path.name}: {e}")

    print("✅ Verarbeitung abgeschlossen.")


if __name__ == "__main__":
    main()
