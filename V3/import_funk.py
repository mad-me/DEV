import re
import sqlite3
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import sys
from datetime import datetime

# Setze explizit den Pfad zur tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:/Users/moahm/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
POPPLER_PATH = r"C:/Users/moahm/AppData/Local/Programs/poppler-24.08.0/Library/bin"

def extract_funk_blocks_flex(text):
    blocks = []
    # Splitte nach 'Fahrzeug:'
    parts = re.split(r"Fahrzeug:\s*", text)
    for part in parts[1:]:  # Erster Teil ist vor dem ersten Fahrzeug
        debug_info = {'raw': part}
        # Referent: erstes Wort
        ref_match = re.match(r"(\S+)", part)
        referent = ref_match.group(1).strip() if ref_match else ''
        debug_info['referent'] = referent
        # Kennzeichen: Suche nach 'W' gefolgt von Zahlen, optionalen Buchstaben und 'TX', mit beliebigen Leerzeichen
        kenn_match = re.search(r"(W\s*[0-9]{3,5}\s*[A-Z]*\s*T?X)", part, re.IGNORECASE)
        kennzeichen = kenn_match.group(1).replace(' ', '').upper() if kenn_match else ''
        debug_info['kennzeichen'] = kennzeichen
        # Summen: nach 'Gesamt Kennung' + Referent, dann zwei Beträge
        summe_match = re.search(rf"Gesamt Kennung\s*{referent}.*?(\d+[\d\.,]*)\s+(\d+[\d\.,]*)", part, re.DOTALL)
        if not summe_match:
            # Fallback: Suche nach zwei Beträgen nach 'Gesamt Kennung'
            summe_match = re.search(r"Gesamt Kennung.*?(\d+[\d\.,]*)\s+(\d+[\d\.,]*)", part, re.DOTALL)
        netto = summe_match.group(1).strip() if summe_match else ''
        brutto = summe_match.group(2).strip() if summe_match else ''
        debug_info['netto'] = netto
        debug_info['brutto'] = brutto
        # Debug-Ausgabe für diesen Block
        print(f"[DEBUG] Abschnitt: Referent={referent}, Kennzeichen={kennzeichen}, Netto={netto}, Brutto={brutto}")
        if not referent or not kennzeichen or not netto or not brutto:
            print(f"[DEBUG]  → Unvollständiger Block! OCR-Abschnitt:\n{part[:300]}...")
        blocks.append((referent, kennzeichen, netto, brutto, debug_info))
    return blocks

def extract_month_year_from_filename(filename):
    match = re.search(r'ARF(\d{2})(\d{2})', filename.upper())
    if match:
        year = int('20' + match.group(1))
        month = int(match.group(2))
        # Vormonat bestimmen
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        return month, year
    # Fallback: aktueller Monat/Jahr, dann Vormonat
    now = datetime.now()
    month = now.month - 1 if now.month > 1 else 12
    year = now.year if now.month > 1 else now.year - 1
    return month, year

def import_funk(pdf_path: Path, funk_db_path: Path, vehicles_db_path: Path):
    """
    Extrahiert Funkdaten (ARF) aus einer PDF und importiert sie in die Tabelle MM_YY in funk.db.
    Für jeden Block: kennzeichen, referent, netto, brutto. Mit ausführlicher Debug-Ausgabe.
    """
    month, year = extract_month_year_from_filename(pdf_path.name)
    table_name = f"{month:02d}_{str(year)[-2:]}"
    images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
    text = "\n".join([pytesseract.image_to_string(img, lang='deu', config='--psm 6') for img in images])
    print("[DEBUG] Gesamter OCR-Text:\n" + text[:1000] + ("..." if len(text) > 1000 else ""))
    blocks = extract_funk_blocks_flex(text)
    # Verbindung zur Fahrzeugdatenbank
    conn_vehicles = sqlite3.connect(str(vehicles_db_path))
    c_veh = conn_vehicles.cursor()
    # Verbindung zur Funkdatenbank
    conn_funk = sqlite3.connect(str(funk_db_path))
    c = conn_funk.cursor()
    # Tabelle anlegen, falls nicht vorhanden
    c.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kennzeichen TEXT,
        referent TEXT,
        netto REAL,
        brutto REAL
    )''')
    conn_funk.commit()
    for referent, kennzeichen, netto, brutto, debug_info in blocks:
        # Debug: Matching gegen vehicles
        c_veh.execute("SELECT license_plate, rfrnc FROM vehicles WHERE license_plate LIKE ? OR rfrnc LIKE ?", (f"%{kennzeichen}%", f"%{referent}%"))
        matches = c_veh.fetchall()
        print(f"[DEBUG] Block: Kennzeichen={kennzeichen}, Referent={referent}, Netto={netto}, Brutto={brutto}")
        if matches:
            for lp, rf in matches:
                print(f"[DEBUG]  → DB-Match: license_plate={lp}, rfrnc={rf}")
        else:
            print(f"[DEBUG]  → Kein Match in DB für Kennzeichen={kennzeichen} oder Referent={referent}")
        def to_float(val):
            try:
                return float(val.replace('.', '').replace(',', '.'))
            except Exception:
                return None
        if referent and kennzeichen and netto and brutto:
            c.execute(f'''INSERT INTO "{table_name}" (kennzeichen, referent, netto, brutto) VALUES (?, ?, ?, ?)''',
                      (kennzeichen, referent, to_float(netto), to_float(brutto)))
        else:
            print(f"[DEBUG]  → Block wird NICHT importiert! Details: {debug_info}")
    conn_funk.commit()
    conn_funk.close()
    conn_vehicles.close()
    print(f"✅ ARF/Funk verarbeitet und in Tabelle {table_name} gespeichert.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Aufruf: python import_funk.py <pdf_path> <funk_db_path> <vehicles_db_path>")
        sys.exit(1)
    import_funk(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])) 