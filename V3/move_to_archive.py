import os
import shutil
from pathlib import Path

# Liste der Kandidaten-Dateien (nur im Hauptverzeichnis!)
CANDIDATES = [
    # Datenbanken
    'database.db', 'databse.db', 'report.db', 'revenue.db', 'running_cost.db', 'running_costs.db', 'salaries.db',
    'bolt.sqlite', '40100.sqlite', 'uber.sqlite',
    # PDF- und Exportdateien
    'rechnung.25003898.pdf',
    # Monatsberichte (alle, die mit Monatsbericht_ anfangen)
    *[f for f in os.listdir('.') if f.startswith('Monatsbericht_') and f.endswith('.pdf')],
    # Logdateien
    'debug_import.log', 'salary_import.log', 'salary_loader.log',
    # Test- und Hilfsskripte
    'loader_test.py', 'wizard_test.py', 'test_enhanced_import.py', 'test_import_salarie_optimized.py',
    'test_import_salarie.py', 'test_import.py', 'test_loader_qml.py', 'test_regex.py', 'test_salary_import_tool.py',
    # Veraltete oder doppelte Skripte
    'import_31300.py', 'import_funk.py', 'import_salarie.py', 'salary_import_simple.py',
    # Sonstige Skripte
    'debug_import.py', 'analyze_new_pdf.py',
]

ARCHIVE_DIR = 'archive'

# Archiv-Ordner anlegen, falls nicht vorhanden
os.makedirs(ARCHIVE_DIR, exist_ok=True)

for fname in CANDIDATES:
    fpath = Path(fname)
    if fpath.exists() and fpath.is_file():
        print(f"Verschiebe {fname} nach {ARCHIVE_DIR}/")
        shutil.move(str(fpath), os.path.join(ARCHIVE_DIR, fname))
    else:
        pass  # Datei existiert nicht oder ist kein reguläres File

print("Fertig! Alle Kandidaten wurden (falls vorhanden) verschoben.") 