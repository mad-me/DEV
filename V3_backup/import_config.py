"""
Konfigurationsdatei für den optimierten Import-Prozess
"""

import os
from pathlib import Path

# OCR-Konfiguration
TESSERACT_PATH = r"C:\Users\moahm\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\moahm\AppData\Local\Programs\poppler-24.08.0\Library\bin"

# OCR-Parameter
OCR_PSM_MODES = [6, 11, 8, 13]  # Verschiedene OCR-Modi für bessere Ergebnisse
OCR_LANGUAGE = 'deu'
OCR_DPI = 300

# Regex-Muster für Gehaltsdaten
PAYROLL_PATTERNS = {
    'Dienstnehmer': r'Dienstnehmer\W*[:\-]?\s*(.*?)(?=\s*DN[- ]?Nr|$)',
    'DN-Nr.': r'DN[- ]?Nr\.?\W*[:\-]?\s*(\d+)',
    'Brutto': r'Brutto\W*[:\-]?\s*([\d\.,]+)',
    'Zahlbetrag': r'Zahlbetrag\W*[:\-]?\s*([\d\.,]+)'
}

# Datenbank-Konfiguration
DEFAULT_SALARIES_DB = Path(__file__).parent / "SQL" / "salaries.db"
DEFAULT_DRIVERS_DB = Path(__file__).parent / "SQL" / "database.db"

# Performance-Optimierungen
MAX_WORKERS = 4  # Anzahl paralleler Threads
BATCH_SIZE = 10  # Anzahl PDFs pro Batch
CACHE_SIZE = 1000  # Maximale Cache-Größe für Fahrer-Matches

# Logging-Konfiguration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = 'import_salarie.log'

# Fahrer-Matching-Konfiguration
MATCHING_THRESHOLD = 0.6  # Mindest-Konfidenz für Fahrer-Matches
MIN_TOKEN_MATCH_RATIO = 0.67  # 2/3-Token-Matching

# Betragsparsing-Konfiguration
AMOUNT_DECIMAL_SEPARATOR = ','
AMOUNT_THOUSAND_SEPARATOR = '.'
DEFAULT_AMOUNT = 0.0

# Datenbank-Schema
SALARY_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS "{table_name}" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER,
    dienstnehmer TEXT,
    dn_nr TEXT,
    brutto REAL,
    zahlbetrag REAL,
    page_number INTEGER,
    confidence REAL,
    import_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

# Fehlerbehandlung
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # Sekunden

# Validierung
MIN_CONFIDENCE = 0.5
MAX_PAGE_NUMBER = 1000
MIN_AMOUNT = 0.0
MAX_AMOUNT = 999999.99

# Dateinamen-Muster
PDF_FILENAME_PATTERN = r'Abrechnungen?\s+(\d{2})_(\d{4})'

# Export-Konfiguration
EXPORT_FORMATS = ['csv', 'json', 'xlsx']
EXPORT_ENCODING = 'utf-8'

def get_project_root() -> Path:
    """Gibt das Projekt-Root-Verzeichnis zurück"""
    return Path(__file__).parent

def get_sql_directory() -> Path:
    """Gibt das SQL-Verzeichnis zurück"""
    return get_project_root() / "SQL"

def get_abrechnungen_directory() -> Path:
    """Gibt das Abrechnungen-Verzeichnis zurück"""
    return get_sql_directory() / "Abrechnungen"

def ensure_directories():
    """Stellt sicher, dass alle erforderlichen Verzeichnisse existieren"""
    directories = [
        get_sql_directory(),
        get_abrechnungen_directory()
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Verzeichnis sichergestellt: {directory}")

def validate_config():
    """Validiert die Konfiguration"""
    errors = []
    
    # Prüfe Tesseract
    if not os.path.exists(TESSERACT_PATH):
        errors.append(f"Tesseract nicht gefunden: {TESSERACT_PATH}")
    
    # Prüfe Poppler
    if not os.path.exists(POPPLER_PATH):
        errors.append(f"Poppler nicht gefunden: {POPPLER_PATH}")
    
    # Prüfe Datenbanken
    if not DEFAULT_SALARIES_DB.exists():
        errors.append(f"Salaries-Datenbank nicht gefunden: {DEFAULT_SALARIES_DB}")
    
    if not DEFAULT_DRIVERS_DB.exists():
        errors.append(f"Drivers-Datenbank nicht gefunden: {DEFAULT_DRIVERS_DB}")
    
    if errors:
        print("❌ Konfigurationsfehler gefunden:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Konfiguration ist gültig")
    return True

if __name__ == "__main__":
    print("🔧 Import-Konfiguration wird überprüft...")
    ensure_directories()
    validate_config() 