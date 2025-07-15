"""
Test-Datei für das optimierte Gehalts-Import-Tool
"""

from pathlib import Path
import sys
import os

# Arbeitsverzeichnis auf das Skriptverzeichnis setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def test_salary_import_tool():
    """Testet das optimierte Import-Tool"""
    
    print("🧪 Teste optimiertes Gehalts-Import-Tool...")
    
    # Test-Pfade
    pdf_path = Path(r"C:\DEV\V3\SQL\Abrechnungen\Abrechnungen 06_2025.pdf")
    salaries_db_path = Path(r"C:\DEV\V3\SQL\salaries.db")
    drivers_db_path = Path(r"C:\DEV\V3\SQL\database.db")
    
    print(f"PDF-Pfad: {pdf_path}")
    print(f"Salaries DB: {salaries_db_path}")
    print(f"Drivers DB: {drivers_db_path}")
    
    # Prüfe ob Dateien existieren
    if not pdf_path.exists():
        print(f"❌ PDF-Datei nicht gefunden: {pdf_path}")
        return
    
    if not salaries_db_path.exists():
        print(f"❌ Salaries-Datenbank nicht gefunden: {salaries_db_path}")
        return
        
    if not drivers_db_path.exists():
        print(f"❌ Drivers-Datenbank nicht gefunden: {drivers_db_path}")
        return
    
    try:
        # Import-Tool testen
        from salary_import_tool import import_salary_pdf
        
        print("\n📄 Teste Import-Funktion...")
        result = import_salary_pdf(str(pdf_path), str(salaries_db_path), str(drivers_db_path))
        
        if result["success"]:
            print(f"✅ Import erfolgreich!")
            print(f"  - Tabelle: {result['table_name']}")
            print(f"  - Importierte Einträge: {result['imported_count']}")
            print(f"  - Gesamt-Einträge: {result['total_entries']}")
            print(f"  - Monat: {result['month']}")
            print(f"  - Jahr: {result['year']}")
        else:
            print(f"❌ Import fehlgeschlagen: {result['error']}")
            
    except ImportError as e:
        print(f"❌ Import-Tool nicht gefunden: {e}")
        print("Bitte stellen Sie sicher, dass salary_import_tool.py im gleichen Verzeichnis liegt.")
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")

def test_import_status():
    """Testet die Status-Abfrage"""
    
    print("\n📊 Teste Import-Status...")
    
    try:
        from salary_import_tool import get_salary_import_status
        
        salaries_db_path = Path(r"C:\DEV\V3\SQL\salaries.db")
        status = get_salary_import_status(str(salaries_db_path))
        
        if "error" not in status:
            print(f"✅ Status erfolgreich abgerufen!")
            print(f"  - Anzahl Tabellen: {status['total_tables']}")
            print(f"  - Tabellen-Statistiken: {status['table_stats']}")
            print(f"  - Letzter Import: {status['last_import']}")
        else:
            print(f"❌ Status-Fehler: {status['error']}")
            
    except ImportError as e:
        print(f"❌ Import-Tool nicht gefunden: {e}")
    except Exception as e:
        print(f"❌ Fehler beim Status-Test: {e}")

if __name__ == "__main__":
    print("🚀 Starte Tests für optimiertes Gehalts-Import-Tool...")
    
    test_salary_import_tool()
    test_import_status()
    
    print("\n✅ Tests abgeschlossen!") 