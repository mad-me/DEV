"""
Vereinfachtes und robustes Gehalts-Import-Tool für das Dashboard
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

class SimpleSalaryImporter:
    """Vereinfachtes und robustes Import-Tool für Gehaltsabrechnungen"""
    
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
        # Einfaches Logging ohne komplexe Konfiguration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('salary_import.log', mode='a', encoding='utf-8'),
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
            logging.info(f"✅ {len(drivers)} Fahrer in Cache geladen")
        except Exception as e:
            logging.error(f"❌ Fehler beim Laden des Fahrer-Caches: {e}")
    
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
            logging.info(f"✅ {len(mappings)} DN-Nr. zu Driver-ID Mappings geladen")
        except Exception as e:
            logging.error(f"❌ Fehler beim Laden der DN-Nr. Mappings: {e}")
    
    def get_driver_name_by_dn_nr(self, dn_nr: str) -> str:
        """Holt den Fahrernamen aus der database.db basierend auf der DN-Nr. (driver_id)."""
        try:
            conn = sqlite3.connect(self.drivers_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT first_name, last_name FROM drivers WHERE driver_id = ?", (dn_nr,))
            result = cursor.fetchone()
            conn.close()
            if result:
                first_name, last_name = result
                full_name = f"{first_name} {last_name}".strip()
                logging.info(f"✅ Gefundener Fahrer für DN-Nr. {dn_nr}: {full_name}")
                return full_name
            else:
                logging.warning(f"⚠️ Kein Fahrer für DN-Nr. {dn_nr} gefunden")
                return ""
        except Exception as e:
            logging.error(f"❌ Fehler beim Abrufen des Fahrernamens für DN-Nr. {dn_nr}: {e}")
            return ""
    
    def normalize_name(self, name: str) -> List[str]:
        """Normalisiert Namen für besseres Matching"""
        return [token for token in re.findall(r'[a-zA-Zäöüß]+', name.lower())]
    
    def match_driver(self, dienstnehmer: str, driver_id: str = None) -> Optional[int]:
        """Findet den passenden Fahrer - zuerst Name-Matching, dann Driver-ID-Matching"""
        if not dienstnehmer.strip():
            return None
            
        # 1. Versuche Name-Matching
        tokens = self.normalize_name(dienstnehmer)
        if tokens:
            for cached_tokens, cached_driver_id in self.driver_cache.items():
                match_count = sum(1 for t in tokens if t in cached_tokens)
                if len(tokens) >= 3 and match_count >= 2:
                    return cached_driver_id
                elif len(tokens) < 3 and match_count == len(tokens):
                    return cached_driver_id
        
        # 2. Falls Name-Matching fehlschlägt und Driver-ID vorhanden ist, versuche Driver-ID-Matching
        if driver_id and driver_id.strip():
            try:
                # Suche in der Datenbank nach der Driver-ID
                conn = sqlite3.connect(self.drivers_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT driver_id FROM drivers WHERE driver_id = ?", (driver_id,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    logging.info(f"✅ Driver-ID-Match gefunden: {driver_id}")
                    return result[0]
                else:
                    logging.warning(f"⚠️ Driver-ID {driver_id} nicht in Datenbank gefunden")
            except Exception as e:
                logging.error(f"❌ Fehler beim Driver-ID-Matching: {e}")
                
        return None
    
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
    
    def extract_payroll_data(self, text: str) -> List[Dict]:
        """Extrahiert Gehaltsdaten aus Text"""
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
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Erste Runde: Standard-Muster
            for key, pattern in patterns.items():
                if not key.endswith('_alt'):  # Nur Standard-Muster
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        current_entry[key] = match.group(1).strip()
            
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
            
            # Dritte Runde: DN-Nr. Matching für korrekten Namen aus der Datenbank
            if 'DN-Nr.' in current_entry:
                dn_nr = current_entry['DN-Nr.']
                driver_name = self.get_driver_name_by_dn_nr(dn_nr)
                if driver_name and driver_name.strip():
                    current_entry['Dienstnehmer'] = driver_name
                    logging.info(f"✅ DN-Nr. Match - Verwende Namen aus Datenbank: '{driver_name}' für DN-Nr. {dn_nr}")
                elif 'Dienstnehmer' in current_entry:
                    logging.warning(f"⚠️ DN-Nr. {dn_nr} nicht in Datenbank gefunden, verwende erkannten Namen")
            
            if all(key in current_entry for key in ['Dienstnehmer', 'DN-Nr.', 'Brutto', 'Zahlbetrag']):
                try:
                    entry = {
                        'dienstnehmer': current_entry['Dienstnehmer'],
                        'dn_nr': current_entry['DN-Nr.'],
                        'driver_id': current_entry.get('Driver-ID', ''),  # Optional Driver-ID
                        'brutto': self.parse_amount(current_entry['Brutto']),
                        'zahlbetrag': self.parse_amount(current_entry['Zahlbetrag'])
                    }
                    entries.append(entry)
                except Exception as e:
                    logging.warning(f"Fehler beim Parsen der Daten: {e}")
                
                current_entry = {}
        
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
    
    def import_pdf(self, pdf_path: str) -> Dict:
        """Importiert eine PDF-Datei"""
        logging.info(f"🔍 Verarbeite Datei: {pdf_path}")
        
        # Extrahiere Monat und Jahr aus dem Dateinamen
        match = re.search(r'Abrechnungen?\s+(\d{2})_(\d{4})', Path(pdf_path).name, re.IGNORECASE)
        if not match:
            error_msg = f"Dateiname {pdf_path} entspricht nicht dem Abrechnungs-Muster."
            logging.error(f"⚠️ {error_msg}")
            return {"success": False, "error": error_msg, "imported_count": 0}

        month = int(match.group(1))
        year = int(match.group(2))
        table_name = f"{month:02d}_{str(year)[-2:]}"
        logging.info(f"📊 Erstelle Tabelle: {table_name} (Monat: {month}, Jahr: {year})")

        # PDF zu Bildern konvertieren
        try:
            images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        except Exception as e:
            error_msg = f"PDF-Konvertierung fehlgeschlagen: {e}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg, "imported_count": 0}

        # Alle Einträge sammeln
        all_entries = []
        for i, img in enumerate(images):
            try:
                text = self.extract_text(img)
                if text.strip():
                    entries = self.extract_payroll_data(text)
                    all_entries.extend(entries)
                    logging.info(f"Seite {i+1}: {len(entries)} Einträge gefunden")
            except Exception as e:
                logging.error(f"Fehler bei der Verarbeitung von Seite {i+1}: {e}")

        # In Datenbank speichern
        result = self.save_to_database(all_entries, table_name)
        
        return {
            "success": True,
            "table_name": table_name,
            "imported_count": result,
            "total_entries": len(all_entries),
            "month": month,
            "year": year
        }
    
    def save_to_database(self, entries: List[Dict], table_name: str) -> int:
        """Speichert Einträge in der Datenbank mit Duplikat-Prüfung"""
        try:
            conn = sqlite3.connect(self.salaries_db_path)
            cursor = conn.cursor()
            
            # Tabelle anlegen
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER,
                dienstnehmer TEXT,
                dn_nr TEXT,
                brutto REAL,
                zahlbetrag REAL,
                import_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Einträge einfügen mit Duplikat-Prüfung
            inserted_count = 0
            skipped_count = 0
            
            for entry in entries:
                # Prüfe auf Duplikate basierend auf DN-Nr. und Dienstnehmer
                cursor.execute(f'''SELECT COUNT(*) FROM "{table_name}" 
                    WHERE dn_nr = ? AND dienstnehmer = ?''', 
                    (entry['dn_nr'], entry['dienstnehmer']))
                
                if cursor.fetchone()[0] > 0:
                    logging.info(f"⏭️ Duplikat übersprungen: {entry['dienstnehmer']} (DN-Nr: {entry['dn_nr']})")
                    skipped_count += 1
                    continue
                
                # Erweiterte Driver-Zuordnung: Name-Matching + Driver-ID-Matching
                driver_id = self.match_driver(entry['dienstnehmer'], entry.get('driver_id'))
                
                cursor.execute(f'''INSERT INTO "{table_name}" 
                    (driver_id, dienstnehmer, dn_nr, brutto, zahlbetrag) 
                    VALUES (?, ?, ?, ?, ?)''',
                    (driver_id, entry['dienstnehmer'], entry['dn_nr'], 
                     entry['brutto'], entry['zahlbetrag']))
                inserted_count += 1
                
                if driver_id:
                    logging.info(f"✅ Eintrag importiert: {entry['dienstnehmer']} -> Driver ID {driver_id}")
                else:
                    logging.warning(f"⚠️ Kein Driver-Match für: {entry['dienstnehmer']}")
            
            conn.commit()
            conn.close()
            
            logging.info(f"✅ {inserted_count} neue Einträge in Tabelle {table_name} gespeichert")
            if skipped_count > 0:
                logging.info(f"⏭️ {skipped_count} Duplikate übersprungen")
            return inserted_count
            
        except Exception as e:
            logging.error(f"Fehler beim Speichern in Datenbank: {e}")
            return 0

# Globale Funktionen für einfache Integration
def import_salary_pdf(pdf_path: str, salaries_db_path: str = None, drivers_db_path: str = None) -> Dict:
    """Einfache Funktion zum Importieren einer einzelnen PDF"""
    if salaries_db_path is None:
        salaries_db_path = str(Path(__file__).parent / "SQL" / "salaries.db")
    if drivers_db_path is None:
        drivers_db_path = str(Path(__file__).parent / "SQL" / "database.db")
    
    importer = SimpleSalaryImporter(salaries_db_path, drivers_db_path)
    return importer.import_pdf(pdf_path)

def get_salary_import_status(salaries_db_path: str = None) -> Dict:
    """Gibt den Import-Status zurück"""
    if salaries_db_path is None:
        salaries_db_path = str(Path(__file__).parent / "SQL" / "salaries.db")
    
    try:
        conn = sqlite3.connect(salaries_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_%'")
        tables = cursor.fetchall()
        
        table_stats = {}
        for (table_name,) in tables:
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            count = cursor.fetchone()[0]
            table_stats[table_name] = count
        
        conn.close()
        
        return {
            "total_tables": len(tables),
            "table_stats": table_stats,
            "last_import": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen des Import-Status: {e}")
        return {"error": str(e)}

# Kompatibilitätsfunktion für das bestehende System
def import_salarie(pdf_path: Path, salaries_db_path: Path, drivers_db_path: Path):
    """Kompatibilitätsfunktion für das bestehende System"""
    result = import_salary_pdf(str(pdf_path), str(salaries_db_path), str(drivers_db_path))
    
    if result["success"]:
        print(f"✅ Abrechnung verarbeitet und in Tabelle {result['table_name']} gespeichert.")
        print(f"📊 {result['imported_count']} Einträge importiert")
    else:
        print(f"❌ Import fehlgeschlagen: {result['error']}")
    
    return result 