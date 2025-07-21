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
    
    # Prüfe, welches Format es ist
    if "TAXI 31300" in text or ("Rechnung-Nr." in text and "31300" in text):
        print("[DEBUG] Erkannt: 31300-Rechnungsformat")
        return extract_31300_blocks(text)
    elif "TAXI 40100" in text or ("Rechnung-Nr." in text and "40100" in text) or "Fahrzeug:" in text:
        print("[DEBUG] Erkannt: 40100/ARF-Rechnungsformat")
        return extract_40100_blocks(text)
    else:
        print("[DEBUG] Unbekanntes Format - verwende 40100/ARF als Fallback")
        return extract_40100_blocks(text)



def extract_31300_blocks(text):
    """Extrahiert Blöcke aus 31300-Rechnungsformat"""
    blocks = []
    
    # Suche nach "Fahrzeug: [Kennung]" Pattern
    fahrzeug_pattern = r"Fahrzeug:\s*([A-Z0-9]+)"
    fahrzeug_matches = re.finditer(fahrzeug_pattern, text)
    
    for match in fahrzeug_matches:
        kennung = match.group(1).strip()
        start_pos = match.end()
        
        # Suche nach dem nächsten "Fahrzeug:" oder Ende des Textes
        next_fahrzeug = re.search(r"Fahrzeug:\s*[A-Z0-9]+", text[start_pos:])
        if next_fahrzeug:
            end_pos = start_pos + next_fahrzeug.start()
        else:
            end_pos = len(text)
        
        # Extrahiere den Block zwischen diesem Fahrzeug und dem nächsten
        block_text = text[start_pos:end_pos]
        
        # Suche nach "Gesamt Kennung [Kennung] [Netto] [Brutto]"
        gesamt_pattern = rf"Gesamt Kennung\s*{kennung}\s+([\d\.,]+)\s+([\d\.,]+)"
        gesamt_match = re.search(gesamt_pattern, block_text)
        
        if gesamt_match:
            netto = gesamt_match.group(1).strip()
            brutto = gesamt_match.group(2).strip()
            
            # Verwende die Kennung als Referent (da kein separater Referent im 31300-Format)
            referent = kennung
            
            debug_info = {
                'raw': block_text[:200],
                'format': '31300',
                'kennung': kennung
            }
            
            print(f"[DEBUG] 31300-Block: Kennung={kennung}, Netto={netto}, Brutto={brutto}")
            
            blocks.append((referent, kennung, netto, brutto, debug_info))
        else:
            print(f"[DEBUG] Kein 'Gesamt Kennung' für Fahrzeug {kennung} gefunden")
    
    return blocks

def extract_40100_blocks(text):
    """Extrahiert Blöcke aus 40100-Rechnungsformat (ähnlich wie 31300)"""
    blocks = []
    
    # Suche nach "Fahrzeug: [Kennung]" Pattern (wie bei 31300)
    fahrzeug_pattern = r"Fahrzeug:\s*([A-Z0-9]+)"
    fahrzeug_matches = re.finditer(fahrzeug_pattern, text)
    
    for match in fahrzeug_matches:
        kennung = match.group(1).strip()
        start_pos = match.end()
        
        # Suche nach dem nächsten "Fahrzeug:" oder Ende des Textes
        next_fahrzeug = re.search(r"Fahrzeug:\s*[A-Z0-9]+", text[start_pos:])
        if next_fahrzeug:
            end_pos = start_pos + next_fahrzeug.start()
        else:
            end_pos = len(text)
        
        # Extrahiere den Block zwischen diesem Fahrzeug und dem nächsten
        block_text = text[start_pos:end_pos]
        
        # Suche nach "Gesamt Kennung [Kennung] [Netto] [Brutto]"
        gesamt_pattern = rf"Gesamt Kennung\s*{kennung}\s+([\d\.,]+)\s+([\d\.,]+)"
        gesamt_match = re.search(gesamt_pattern, block_text)
        
        if gesamt_match:
            netto = gesamt_match.group(1).strip()
            brutto = gesamt_match.group(2).strip()
            
            # Verwende die Kennung als Referent (da kein separater Referent im 40100-Format)
            referent = kennung
            
            debug_info = {
                'raw': block_text[:200],
                'format': '40100',
                'kennung': kennung
            }
            
            print(f"[DEBUG] 40100-Block: Kennung={kennung}, Netto={netto}, Brutto={brutto}")
            
            blocks.append((referent, kennung, netto, brutto, debug_info))
        else:
            print(f"[DEBUG] Kein 'Gesamt Kennung' für Fahrzeug {kennung} gefunden")
    
    return blocks

def extract_date_from_pdf_text(text):
    """Extrahiert das Rechnungsdatum aus dem PDF-Text"""
    # Verschiedene Datums-Patterns versuchen
    date_patterns = [
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
        r'(\d{1,2})\.(\d{1,2})\.(\d{2})',   # DD.MM.YY
        r'(\d{1,2})/(\d{1,2})/(\d{4})',     # DD/MM/YYYY
        r'(\d{1,2})/(\d{1,2})/(\d{2})',     # DD/MM/YY
        r'Datum:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})',  # Datum: DD.MM.YYYY
        r'Datum:\s*(\d{1,2})\.(\d{1,2})\.(\d{2})',  # Datum: DD.MM.YY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            
            # Wenn Jahr nur 2-stellig, zu 4-stellig erweitern
            if year < 100:
                year += 2000
                
            print(f"[DEBUG] Datum gefunden: {day:02d}.{month:02d}.{year}")
            return day, month, year
    
    print("[DEBUG] Kein Datum im PDF gefunden, verwende aktuelles Datum")
    now = datetime.now()
    return now.day, now.month, now.year

def determine_table_month(day, month, year):
    """Bestimmt die Monatstabelle basierend auf dem Rechnungsdatum"""
    # Wenn Tag vor dem 5., dann Vormonat
    if day < 5:
        if month == 1:
            table_month = 12
            table_year = year - 1
        else:
            table_month = month - 1
            table_year = year
        print(f"[DEBUG] Rechnungsdatum {day:02d}.{month:02d}.{year} -> Vormonat: {table_month:02d}_{str(table_year)[-2:]}")
    # Wenn Tag nach dem 25., dann aktueller Monat
    elif day > 25:
        table_month = month
        table_year = year
        print(f"[DEBUG] Rechnungsdatum {day:02d}.{month:02d}.{year} -> Aktueller Monat: {table_month:02d}_{str(table_year)[-2:]}")
    # Zwischen 5. und 25. -> aktueller Monat
    else:
        table_month = month
        table_year = year
        print(f"[DEBUG] Rechnungsdatum {day:02d}.{month:02d}.{year} -> Aktueller Monat: {table_month:02d}_{str(table_year)[-2:]}")
    
    return table_month, table_year

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
    # OCR-Text extrahieren
    images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
    text = "\n".join([pytesseract.image_to_string(img, lang='deu', config='--psm 6') for img in images])
    print("[DEBUG] Gesamter OCR-Text:\n" + text[:1000] + ("..." if len(text) > 1000 else ""))
    
    # Datum aus PDF-Text extrahieren und Tabelle bestimmen
    day, month, year = extract_date_from_pdf_text(text)
    table_month, table_year = determine_table_month(day, month, year)
    table_name = f"{table_month:02d}_{str(table_year)[-2:]}"
    
    print(f"[DEBUG] Verwende Tabelle: {table_name}")
    
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
    for referent, kennung, netto, brutto, debug_info in blocks:
        # Suche nach dem echten Kennzeichen in der vehicles.db
        real_license_plate = None
        
        # 1. Versuche direkten Match mit der Kennung
        c_veh.execute("SELECT license_plate, rfrnc FROM vehicles WHERE rfrnc = ?", (kennung,))
        matches = c_veh.fetchall()
        
        if matches:
            # Verwende das erste Match
            real_license_plate = matches[0][0]  # license_plate
            print(f"[DEBUG] [OK] Direkter Match: Kennung={kennung} -> Kennzeichen={real_license_plate}")
        else:
            # 2. Versuche Match mit Kennung als Teil des Kennzeichens
            c_veh.execute("SELECT license_plate, rfrnc FROM vehicles WHERE license_plate LIKE ?", (f"%{kennung}%",))
            matches = c_veh.fetchall()
            
            if matches:
                real_license_plate = matches[0][0]  # license_plate
                print(f"[DEBUG] [OK] Teil-Match: Kennung={kennung} -> Kennzeichen={real_license_plate}")
            else:
                # 3. Kein Match gefunden - verwende die Kennung als Kennzeichen
                real_license_plate = kennung
                print(f"[DEBUG] [WARN] Kein Match gefunden für Kennung={kennung}, verwende Kennung als Kennzeichen")
        
        # Debug-Ausgabe
        print(f"[DEBUG] Block: Kennung={kennung}, Echter Kennzeichen={real_license_plate}, Referent={referent}, Netto={netto}, Brutto={brutto}")
        
        def to_float(val):
            try:
                return float(val.replace('.', '').replace(',', '.'))
            except Exception:
                return None
        
        if referent and real_license_plate and netto and brutto:
            c.execute(f'''INSERT INTO "{table_name}" (kennzeichen, referent, netto, brutto) VALUES (?, ?, ?, ?)''',
                      (real_license_plate, referent, to_float(netto), to_float(brutto)))
            print(f"[DEBUG] [OK] Importiert: {real_license_plate} (Kennung: {kennung})")
        else:
            print(f"[DEBUG]  -> Block wird NICHT importiert! Details: {debug_info}")
    conn_funk.commit()
    conn_funk.close()
    conn_vehicles.close()
    print(f"[OK] ARF/Funk verarbeitet und in Tabelle {table_name} gespeichert.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Aufruf: python import_funk.py <pdf_path> <funk_db_path> <vehicles_db_path>")
        sys.exit(1)
    import_funk(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])) 