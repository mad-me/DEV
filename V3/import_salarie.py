import re
import sqlite3
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import sys

# Setze explizit den Pfad zur tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\moahm\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Passe diesen Pfad ggf. an deine Poppler-Installation an
POPPLER_PATH = r"C:\Users\moahm\AppData\Local\Programs\poppler-24.08.0\Library\bin"


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


def import_salarie(pdf_path: Path, salaries_db_path: Path, drivers_db_path: Path):
    """
    Extrahiert Gehaltsdaten aus einer PDF und importiert sie in die Tabelle MM_YY in salaries.db.
    Führt ein 2/3-Token-Matching mit der drivers-Tabelle in drivers_db_path durch.
    """
    match = re.search(r'Abrechnungen?\s+(\d{2})_(\d{4})', Path(pdf_path).name, re.IGNORECASE)
    if not match:
        print(f"⚠️ Dateiname {pdf_path} entspricht nicht dem Abrechnungs-Muster.")
        return

    month = int(match.group(1))
    year = int(match.group(2))
    table_name = f"{month:02d}_{str(year)[-2:]}"

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

    # Verbindung zur Gehaltsdatenbank (salaries.db)
    conn_salaries = sqlite3.connect(str(salaries_db_path))
    c = conn_salaries.cursor()
    # Verbindung zur Fahrerdatenbank (database.db)
    conn_drivers = sqlite3.connect(str(drivers_db_path))

    # Tabelle anlegen, falls nicht vorhanden
    c.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER,
        dienstnehmer TEXT,
        dn_nr TEXT,
        brutto REAL,
        zahlbetrag REAL
    )''')
    conn_salaries.commit()

    for row in payroll_rows:
        dienstnehmer = row.get('Dienstnehmer', '')
        driver_id = match_driver(dienstnehmer, conn_drivers)
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
    conn_salaries.commit()
    conn_salaries.close()
    conn_drivers.close()
    print(f"✅ Abrechnung verarbeitet und in Tabelle {table_name} gespeichert.")


if __name__ == "__main__":
    try:
        from PyQt6.QtWidgets import QApplication, QFileDialog
    except ImportError:
        print("PyQt6 ist nicht installiert. Bitte installiere es mit 'pip install PyQt6'.")
        sys.exit(1)
    app = QApplication(sys.argv)
    dialog = QFileDialog()
    dialog.setWindowTitle("Bitte Gehaltsabrechnungs-PDF auswählen")
    dialog.setNameFilter("PDF-Dateien (*.pdf)")
    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    if dialog.exec():
        pdf_file = dialog.selectedFiles()[0]
        print(f"Ausgewählte Datei: {pdf_file}")
    else:
        print("Keine Datei ausgewählt. Abbruch.")
        sys.exit(1)

    # Datenbankpfade abfragen oder Defaults setzen
    default_salaries = str(Path(__file__).parent / "SQL" / "salaries.db")
    default_drivers = str(Path(__file__).parent / "SQL" / "database.db")
    print(f"Pfad zur Gehaltsdatenbank (Enter für Default: {default_salaries}): ", end="")
    salaries_db = input().strip() or default_salaries
    print(f"Pfad zur Fahrerdatenbank (Enter für Default: {default_drivers}): ", end="")
    drivers_db = input().strip() or default_drivers

    import_salarie(Path(pdf_file), Path(salaries_db), Path(drivers_db)) 