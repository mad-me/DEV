"""
Debug-Version des Import-Tools
Zeigt detaillierte Informationen über nicht erkannte Einträge
"""

import re
import sqlite3
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os

# Setze explizit den Pfad zur tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\moahm\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Passe diesen Pfad ggf. an deine Poppler-Installation an
POPPLER_PATH = r"C:\Users\moahm\AppData\Local\Programs\poppler-24.08.0\Library\bin"

class DebugSalaryImporter:
    """Debug-Version des Import-Tools für detaillierte Analyse"""
    
    def __init__(self, salaries_db_path: str, drivers_db_path: str):
        self.salaries_db_path = salaries_db_path
        self.drivers_db_path = drivers_db_path
        self.driver_cache = {}
        self.dn_to_driver_cache = {}  # Cache für DN-Nr. zu Driver-Mapping
        self.setup_logging()
        self.load_driver_cache()
        self.load_dn_to_driver_mapping()
        
    def setup_logging(self):
        """Konfiguriert das Logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('debug_import.log', mode='a', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
    def load_driver_cache(self):
        """Lädt alle Fahrer in den Cache"""
        try:
            conn = sqlite3.connect(self.drivers_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT driver_id, first_name, last_name FROM drivers")
            drivers = cursor.fetchall()
            
            for driver_id, first_name, last_name in drivers:
                normalized_name = self.normalize_name(f"{first_name} {last_name}")
                self.driver_cache[tuple(normalized_name)] = driver_id
                
            conn.close()
            logging.info(f"OK {len(drivers)} Fahrer in Cache geladen")
        except Exception as e:
            logging.error(f"Fehler beim Laden des Fahrer-Caches: {e}")
    
    def load_dn_to_driver_mapping(self):
        """Lädt DN-Nr. zu Driver-ID Mapping aus der database.db"""
        try:
            conn = sqlite3.connect(self.drivers_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT driver_id, driver_license_number FROM drivers WHERE driver_license_number IS NOT NULL AND driver_license_number != ''")
            mappings = cursor.fetchall()
            
            for driver_id, dn_nr in mappings:
                self.dn_to_driver_cache[dn_nr] = driver_id
                
            conn.close()
            logging.info(f"OK {len(mappings)} DN-Nr. zu Driver-ID Mappings geladen")
        except Exception as e:
            logging.error(f"Fehler beim Laden der DN-Nr. Mappings: {e}")
    
    def get_driver_name_by_dn_nr(self, dn_nr: str) -> Optional[str]:
        """Holt den Fahrernamen aus der database.db basierend auf der DN-Nr."""
        try:
            conn = sqlite3.connect(self.drivers_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT first_name, last_name FROM drivers WHERE driver_license_number = ?", (dn_nr,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                first_name, last_name = result
                full_name = f"{first_name} {last_name}".strip()
                logging.info(f"DEBUG: Gefundener Fahrer für DN-Nr. {dn_nr}: {full_name}")
                return full_name
            else:
                logging.warning(f"DEBUG: Kein Fahrer für DN-Nr. {dn_nr} gefunden")
                return ""
        except Exception as e:
            logging.error(f"Fehler beim Abrufen des Fahrernamens für DN-Nr. {dn_nr}: {e}")
            return ""
    
    def normalize_name(self, name: str) -> List[str]:
        """Normalisiert Namen für besseres Matching"""
        return [token for token in re.findall(r'[a-zA-Zäöüß]+', name.lower())]
    
    def extract_text(self, image) -> str:
        """Extrahiert Text aus einem Bild"""
        try:
            # Erste OCR-Versuche mit verschiedenen PSM-Modi
            psm_modes = [6, 11, 8, 13]
            
            for psm in psm_modes:
                try:
                    text = pytesseract.image_to_string(
                        image, 
                        lang='deu', 
                        config=f'--psm {psm} --oem 3'
                    )
                    if text.strip():
                        return text
                except Exception:
                    continue
            
            return ""
        except Exception as e:
            logging.error(f"OCR-Fehler: {e}")
            return ""
    
    def extract_payroll_data_debug(self, text: str, page_number: int) -> List[Dict]:
        """Extrahiert Gehaltsdaten mit detailliertem Debugging"""
        entries = []
        
        patterns = {
            'Dienstnehmer': r'Dienstnehmer\W*[:\-]?\s*(.*?)(?=\s*DN[- ]?Nr|$)',
            'DN-Nr.': r'DN[- ]?Nr\.?\W*[:\-]?\s*(\d+)',
            'Driver-ID': r'Driver[- ]?ID\W*[:\-]?\s*(\d+)',
            'Brutto': r'Brutto\W*[:\-]?\s*([\d\.,]+)',
            'Zahlbetrag': r'Zahlbetrag\W*[:\-]?\s*([\d\.,]+)',
            # Alternative Muster für bessere Erkennung
            'Dienstnehmer_alt': r'Name\W*[:\-]?\s*(.*?)(?=\s*DN[- ]?Nr|$)',
            'DN-Nr._alt': r'Nr\.?\W*[:\-]?\s*(\d+)',
            'Brutto_alt': r'Brutto\W*[:\-]?\s*([\d\.,]+)',
            'Zahlbetrag_alt': r'Zahlung\W*[:\-]?\s*([\d\.,]+)'
        }
        
        lines = text.split('\n')
        current_entry = {}
        debug_info = []
        
        logging.info(f"DEBUG: Verarbeite {len(lines)} Zeilen auf Seite {page_number}")
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            logging.info(f"DEBUG: Zeile {line_num + 1}: '{line}'")
            
            # Erste Runde: Standard-Muster
            for key, pattern in patterns.items():
                if not key.endswith('_alt'):  # Nur Standard-Muster
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        current_entry[key] = match.group(1).strip()
                        logging.info(f"DEBUG: Standard-Match '{key}': '{match.group(1).strip()}'")
            
            # Zweite Runde: Alternative Muster (falls Standard-Muster fehlschlagen)
            if not all(key in current_entry for key in ['Dienstnehmer', 'DN-Nr.', 'Brutto', 'Zahlbetrag']):
                for key, pattern in patterns.items():
                    if key.endswith('_alt'):  # Nur Alternative-Muster
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            # Mappe alternative Schlüssel auf Standard-Schlüssel
                            if key == 'Dienstnehmer_alt':
                                current_entry['Dienstnehmer'] = match.group(1).strip()
                            elif key == 'DN-Nr._alt':
                                current_entry['DN-Nr.'] = match.group(1).strip()
                            elif key == 'Brutto_alt':
                                current_entry['Brutto'] = match.group(1).strip()
                            elif key == 'Zahlbetrag_alt':
                                current_entry['Zahlbetrag'] = match.group(1).strip()
                            logging.info(f"DEBUG: Alt-Match '{key}': '{match.group(1).strip()}'")
            
            # Dritte Runde: DN-Nr. Matching falls Dienstnehmer fehlt
            if 'DN-Nr.' in current_entry and 'Dienstnehmer' not in current_entry:
                dn_nr = current_entry['DN-Nr.']
                driver_name = self.get_driver_name_by_dn_nr(dn_nr)
                if driver_name and driver_name.strip():
                    current_entry['Dienstnehmer'] = driver_name
                    logging.info(f"DEBUG: DN-Nr. Match - Gefundener Dienstnehmer: '{driver_name}' für DN-Nr. {dn_nr}")
            
            if all(key in current_entry for key in ['Dienstnehmer', 'DN-Nr.', 'Brutto', 'Zahlbetrag']):
                try:
                    entry = {
                        'dienstnehmer': current_entry['Dienstnehmer'],
                        'dn_nr': current_entry['DN-Nr.'],
                        'driver_id': current_entry.get('Driver-ID', ''),
                        'brutto': self.parse_amount(current_entry['Brutto']),
                        'zahlbetrag': self.parse_amount(current_entry['Zahlbetrag'])
                    }
                    entries.append(entry)
                    logging.info(f"DEBUG: Vollständiger Eintrag gefunden: {entry}")
                except Exception as e:
                    logging.warning(f"Fehler beim Parsen der Daten: {e}")
                
                current_entry = {}
            else:
                # Debug: Zeige was noch fehlt
                missing = [key for key in ['Dienstnehmer', 'DN-Nr.', 'Brutto', 'Zahlbetrag'] if key not in current_entry]
                if missing:
                    logging.info(f"DEBUG: Fehlende Felder: {missing}")
                    logging.info(f"DEBUG: Aktueller Eintrag: {current_entry}")
        
        return entries
    
    def parse_amount(self, amount_str: str) -> float:
        """Parst Beträge"""
        try:
            cleaned = amount_str.replace(' ', '').replace(',', '.')
            if cleaned.count('.') > 1:
                parts = cleaned.split('.')
                cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def import_pdf_debug(self, pdf_path: str) -> Dict:
        """Importiert eine PDF-Datei mit detailliertem Debugging"""
        logging.info(f"DEBUG: Verarbeite Datei: {pdf_path}")
        
        # Extrahiere Monat und Jahr aus dem Dateinamen
        match = re.search(r'Abrechnungen?\s+(\d{2})_(\d{4})', Path(pdf_path).name, re.IGNORECASE)
        if not match:
            error_msg = f"Dateiname {pdf_path} entspricht nicht dem Abrechnungs-Muster."
            logging.error(f"WARNUNG: {error_msg}")
            return {"success": False, "error": error_msg, "imported_count": 0}

        month = int(match.group(1))
        year = int(match.group(2))
        table_name = f"{month:02d}_{str(year)[-2:]}"
        logging.info(f"DEBUG: Erstelle Tabelle: {table_name} (Monat: {month}, Jahr: {year})")

        # PDF zu Bildern konvertieren
        try:
            images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        except Exception as e:
            error_msg = f"PDF-Konvertierung fehlgeschlagen: {e}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg, "imported_count": 0}

        # Alle Einträge sammeln
        all_entries = []
        total_pages = len(images)
        
        for i, img in enumerate(images):
            try:
                text = self.extract_text(img)
                if text.strip():
                    logging.info(f"DEBUG: Seite {i+1}/{total_pages} - Text extrahiert ({len(text)} Zeichen)")
                    entries = self.extract_payroll_data_debug(text, i + 1)
                    all_entries.extend(entries)
                    logging.info(f"DEBUG: Seite {i+1}: {len(entries)} Einträge gefunden")
                else:
                    logging.warning(f"DEBUG: Seite {i+1}: Kein Text extrahiert")
            except Exception as e:
                logging.error(f"Fehler bei der Verarbeitung von Seite {i+1}: {e}")

        logging.info(f"DEBUG: Gesamt gefundene Einträge: {len(all_entries)}")
        
        # Zeige alle gefundenen Einträge
        for i, entry in enumerate(all_entries):
            logging.info(f"DEBUG: Eintrag {i+1}: {entry}")
        
        return {
            "success": True,
            "table_name": table_name,
            "imported_count": len(all_entries),
            "total_entries": len(all_entries),
            "month": month,
            "year": year,
            "entries": all_entries
        }

def debug_import_pdf(pdf_path: str, salaries_db_path: str = None, drivers_db_path: str = None) -> Dict:
    """Debug-Funktion zum Importieren einer einzelnen PDF"""
    if salaries_db_path is None:
        salaries_db_path = str(Path(__file__).parent / "SQL" / "salaries.db")
    if drivers_db_path is None:
        drivers_db_path = str(Path(__file__).parent / "SQL" / "database.db")
    
    importer = DebugSalaryImporter(salaries_db_path, drivers_db_path)
    return importer.import_pdf_debug(pdf_path)

if __name__ == "__main__":
    # Test mit einer PDF-Datei
    pdf_path = r"C:\DEV\V3\SQL\Abrechnungen\Abrechnungen 05_2025.pdf"
    
    if Path(pdf_path).exists():
        print("DEBUG: Starte Debug-Import...")
        result = debug_import_pdf(pdf_path)
        
        if result["success"]:
            print(f"DEBUG: Import abgeschlossen!")
            print(f"  - Gefundene Einträge: {result['total_entries']}")
            print(f"  - Tabelle: {result['table_name']}")
            
            # Zeige alle gefundenen Einträge
            for i, entry in enumerate(result.get('entries', [])):
                print(f"  Eintrag {i+1}: {entry}")
        else:
            print(f"DEBUG: Import fehlgeschlagen: {result['error']}")
    else:
        print(f"DEBUG: PDF-Datei nicht gefunden: {pdf_path}") 