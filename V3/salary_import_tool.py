"""
Optimiertes Gehalts-Import-Tool für das Dashboard
Integration in die bestehende Dashboard-Struktur
"""

import re
import sqlite3
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import sys
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os

# Setze explizit den Pfad zur tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\moahm\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Passe diesen Pfad ggf. an deine Poppler-Installation an
POPPLER_PATH = r"C:\Users\moahm\AppData\Local\Programs\poppler-24.08.0\Library\bin"

@dataclass
class PayrollEntry:
    """Datenklasse für Gehaltsabrechnungs-Einträge"""
    dienstnehmer: str
    dn_nr: str
    brutto: float
    zahlbetrag: float
    page_number: int
    confidence: float

class SalaryImportTool:
    """Optimiertes Import-Tool für Gehaltsabrechnungen"""
    
    def __init__(self, salaries_db_path: Path, drivers_db_path: Path):
        self.salaries_db_path = salaries_db_path
        self.drivers_db_path = drivers_db_path
        self.driver_cache = {}
        self.load_driver_cache()
        
        # Logging für das Tool
        self.setup_logging()
        
    def setup_logging(self):
        """Konfiguriert das Logging für das Import-Tool"""
        # Erstelle einen Logger für diese Instanz
        self.logger = logging.getLogger(f"SalaryImportTool_{id(self)}")
        self.logger.setLevel(logging.INFO)
        
        # Entferne bestehende Handler um Duplikate zu vermeiden
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Erstelle neue Handler
        file_handler = logging.FileHandler('salary_import.log')
        console_handler = logging.StreamHandler()
        
        # Formatter erstellen
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Handler hinzufügen
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def load_driver_cache(self):
        """Lädt alle Fahrer in den Cache für schnelleres Matching"""
        try:
            conn = sqlite3.connect(str(self.drivers_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT driver_id, first_name, last_name FROM drivers")
            drivers = cursor.fetchall()
            
            for driver_id, first_name, last_name in drivers:
                # Normalisierte Namen als Schlüssel
                normalized_name = self.normalize_name(f"{first_name} {last_name}")
                self.driver_cache[tuple(normalized_name)] = driver_id
                
            conn.close()
            self.logger.info(f"✅ {len(drivers)} Fahrer in Cache geladen")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Laden des Fahrer-Caches: {e}")
    
    def normalize_name(self, name: str) -> List[str]:
        """Optimierte Namensnormalisierung"""
        return [token for token in re.findall(r'[a-zA-Zäöüß]+', name.lower())]
    
    def match_driver_optimized(self, dienstnehmer: str) -> Optional[int]:
        """Optimiertes Fahrer-Matching mit Cache"""
        if not dienstnehmer.strip():
            return None
            
        tokens = self.normalize_name(dienstnehmer)
        if not tokens:
            return None
            
        # Direkte Cache-Suche
        for cached_tokens, driver_id in self.driver_cache.items():
            match_count = sum(1 for t in tokens if t in cached_tokens)
            if len(tokens) >= 3 and match_count >= 2:
                return driver_id
            elif len(tokens) < 3 and match_count == len(tokens):
                return driver_id
                
        return None
    
    def extract_text_optimized(self, image) -> str:
        """Optimierte Textextraktion mit Fallback-Strategien"""
        # Erste OCR-Versuche mit verschiedenen PSM-Modi
        psm_modes = [6, 11, 8, 13]  # Verschiedene OCR-Modi für bessere Ergebnisse
        
        for psm in psm_modes:
            try:
                text = pytesseract.image_to_string(
                    image, 
                    lang='deu', 
                    config=f'--psm {psm} --oem 3'
                )
                if text.strip():
                    return text
            except Exception as e:
                self.logger.warning(f"OCR-Fehler mit PSM {psm}: {e}")
                continue
        
        return ""
    
    def extract_payroll_data(self, text: str, page_number: int) -> List[PayrollEntry]:
        """Optimierte Extraktion von Gehaltsdaten mit verbesserten Regex-Mustern"""
        entries = []
        
        # Verbesserte Regex-Muster mit höherer Präzision
        patterns = {
            'Dienstnehmer': r'Dienstnehmer\W*[:\-]?\s*(.*?)(?=\s*DN[- ]?Nr|$)',
            'DN-Nr.': r'DN[- ]?Nr\.?\W*[:\-]?\s*(\d+)',
            'Brutto': r'Brutto\W*[:\-]?\s*([\d\.,]+)',
            'Zahlbetrag': r'Zahlbetrag\W*[:\-]?\s*([\d\.,]+)'
        }
        
        # Text in Zeilen aufteilen für bessere Verarbeitung
        lines = text.split('\n')
        
        current_entry = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Suche nach allen Mustern in der aktuellen Zeile
            for key, pattern in patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    current_entry[key] = match.group(1).strip()
            
            # Wenn wir alle erforderlichen Felder haben, erstelle einen Eintrag
            if all(key in current_entry for key in ['Dienstnehmer', 'DN-Nr.', 'Brutto', 'Zahlbetrag']):
                try:
                    entry = PayrollEntry(
                        dienstnehmer=current_entry['Dienstnehmer'],
                        dn_nr=current_entry['DN-Nr.'],
                        brutto=self.parse_amount(current_entry['Brutto']),
                        zahlbetrag=self.parse_amount(current_entry['Zahlbetrag']),
                        page_number=page_number,
                        confidence=0.8  # Basis-Konfidenz
                    )
                    entries.append(entry)
                except ValueError as e:
                    self.logger.warning(f"Fehler beim Parsen der Daten: {e}")
                
                current_entry = {}
        
        return entries
    
    def parse_amount(self, amount_str: str) -> float:
        """Optimierte Betragsparsing mit Fehlerbehandlung"""
        try:
            # Entferne alle Leerzeichen und ersetze Komma durch Punkt
            cleaned = amount_str.replace(' ', '').replace(',', '.')
            # Entferne alle Punkte außer dem letzten (für Tausender-Trennzeichen)
            if cleaned.count('.') > 1:
                parts = cleaned.split('.')
                cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def process_single_page(self, image, page_number: int) -> List[PayrollEntry]:
        """Verarbeitet eine einzelne PDF-Seite"""
        try:
            text = self.extract_text_optimized(image)
            if not text.strip():
                self.logger.warning(f"Kein Text auf Seite {page_number} extrahiert")
                return []
            
            entries = self.extract_payroll_data(text, page_number)
            self.logger.info(f"Seite {page_number}: {len(entries)} Einträge gefunden")
            return entries
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Verarbeitung von Seite {page_number}: {e}")
            return []
    
    def import_single_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """Importiert eine einzelne PDF-Datei und gibt Ergebnisse zurück"""
        self.logger.info(f"🔍 Verarbeite Datei: {pdf_path}")
        
        # Extrahiere Monat und Jahr aus dem Dateinamen
        match = re.search(r'Abrechnungen?\s+(\d{2})_(\d{4})', pdf_path.name, re.IGNORECASE)
        if not match:
            self.logger.error(f"⚠️ Dateiname {pdf_path} entspricht nicht dem Abrechnungs-Muster.")
            return {"success": False, "error": "Ungültiger Dateiname", "imported_count": 0}

        month = int(match.group(1))
        year = int(match.group(2))
        table_name = f"{month:02d}_{str(year)[-2:]}"
        self.logger.info(f"📊 Erstelle Tabelle: {table_name} (Monat: {month}, Jahr: {year})")

        # PDF zu Bildern konvertieren
        try:
            images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
        except Exception as e:
            self.logger.error(f"Fehler beim Konvertieren der PDF: {e}")
            return {"success": False, "error": f"PDF-Konvertierung fehlgeschlagen: {e}", "imported_count": 0}

        # Alle Einträge sammeln
        all_entries = []
        for i, img in enumerate(images):
            entries = self.process_single_page(img, i + 1)
            all_entries.extend(entries)

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
    
    def save_to_database(self, entries: List[PayrollEntry], table_name: str) -> int:
        """Speichert Einträge in der Datenbank"""
        try:
            conn = sqlite3.connect(str(self.salaries_db_path))
            cursor = conn.cursor()
            
            # Tabelle anlegen
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER,
                dienstnehmer TEXT,
                dn_nr TEXT,
                brutto REAL,
                zahlbetrag REAL,
                page_number INTEGER,
                confidence REAL,
                import_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Einträge einfügen
            inserted_count = 0
            for entry in entries:
                driver_id = self.match_driver_optimized(entry.dienstnehmer)
                
                cursor.execute(f'''INSERT INTO "{table_name}" 
                    (driver_id, dienstnehmer, dn_nr, brutto, zahlbetrag, page_number, confidence) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (driver_id, entry.dienstnehmer, entry.dn_nr, entry.brutto, 
                     entry.zahlbetrag, entry.page_number, entry.confidence))
                inserted_count += 1
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"✅ {inserted_count} Einträge in Tabelle {table_name} gespeichert")
            return inserted_count
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern in Datenbank: {e}")
            return 0
    
    def get_import_status(self) -> Dict[str, any]:
        """Gibt den aktuellen Import-Status zurück"""
        try:
            conn = sqlite3.connect(str(self.salaries_db_path))
            cursor = conn.cursor()
            
            # Alle Tabellen auflisten
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_%'")
            tables = cursor.fetchall()
            
            # Statistiken für jede Tabelle
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
            self.logger.error(f"Fehler beim Abrufen des Import-Status: {e}")
            return {"error": str(e)}

# Globale Funktionen für einfache Integration
def create_import_tool(salaries_db_path: str = None, drivers_db_path: str = None) -> SalaryImportTool:
    """Erstellt eine Instanz des Import-Tools mit Standard-Pfaden"""
    if salaries_db_path is None:
        salaries_db_path = Path(__file__).parent / "SQL" / "salaries.db"
    if drivers_db_path is None:
        drivers_db_path = Path(__file__).parent / "SQL" / "database.db"
    
    return SalaryImportTool(Path(salaries_db_path), Path(drivers_db_path))

def import_salary_pdf(pdf_path: str, salaries_db_path: str = None, drivers_db_path: str = None) -> Dict[str, any]:
    """Einfache Funktion zum Importieren einer einzelnen PDF"""
    tool = create_import_tool(salaries_db_path, drivers_db_path)
    return tool.import_single_pdf(Path(pdf_path))

def get_salary_import_status(salaries_db_path: str = None) -> Dict[str, any]:
    """Gibt den Import-Status zurück"""
    tool = create_import_tool(salaries_db_path)
    return tool.get_import_status()

# Kompatibilitätsfunktion für das bestehende System
def import_salarie(pdf_path: Path, salaries_db_path: Path, drivers_db_path: Path):
    """Kompatibilitätsfunktion für das bestehende System"""
    tool = SalaryImportTool(salaries_db_path, drivers_db_path)
    result = tool.import_single_pdf(pdf_path)
    
    if result["success"]:
        print(f"✅ Abrechnung verarbeitet und in Tabelle {result['table_name']} gespeichert.")
        print(f"📊 {result['imported_count']} Einträge importiert")
    else:
        print(f"❌ Import fehlgeschlagen: {result['error']}")
    
    return result 