"""
Test-Datei für die erweiterten Import-Funktionen:
1. Duplikat-Prüfung
2. Driver-ID-Matching
"""

from pathlib import Path
import sys
import os

# Arbeitsverzeichnis auf das Skriptverzeichnis setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_import():
    """Testet die erweiterten Import-Funktionen"""
    
    print("🧪 Teste erweiterte Import-Funktionen...")
    
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
        from salary_import_simple import import_salary_pdf
        
        print("\n📄 Teste erweiterten Import...")
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
        print("Bitte stellen Sie sicher, dass salary_import_simple.py im gleichen Verzeichnis liegt.")
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")

def test_driver_matching():
    """Testet das erweiterte Driver-Matching"""
    
    print("\n👥 Teste Driver-Matching...")
    
    try:
        from salary_import_simple import SimpleSalaryImporter
        
        salaries_db_path = str(Path(r"C:\DEV\V3\SQL\salaries.db"))
        drivers_db_path = str(Path(r"C:\DEV\V3\SQL\database.db"))
        
        importer = SimpleSalaryImporter(salaries_db_path, drivers_db_path)
        
        # Test 1: Name-Matching
        test_name = "Max Mustermann"
        driver_id_name = importer.match_driver(test_name)
        print(f"Name-Matching '{test_name}': {driver_id_name}")
        
        # Test 2: Driver-ID-Matching
        test_driver_id = "123"
        driver_id_id = importer.match_driver("Unbekannter Name", test_driver_id)
        print(f"Driver-ID-Matching '{test_driver_id}': {driver_id_id}")
        
        # Test 3: Kombiniertes Matching
        driver_id_combined = importer.match_driver(test_name, test_driver_id)
        print(f"Kombiniertes Matching: {driver_id_combined}")
        
    except Exception as e:
        print(f"❌ Fehler beim Driver-Matching-Test: {e}")

def test_duplicate_check():
    """Testet die Duplikat-Prüfung"""
    
    print("\n🔄 Teste Duplikat-Prüfung...")
    
    try:
        import sqlite3
        from pathlib import Path
        
        salaries_db_path = Path(r"C:\DEV\V3\SQL\salaries.db")
        
        if not salaries_db_path.exists():
            print(f"❌ Salaries-Datenbank nicht gefunden: {salaries_db_path}")
            return
        
        conn = sqlite3.connect(str(salaries_db_path))
        cursor = conn.cursor()
        
        # Prüfe alle Tabellen auf Duplikate
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_%'")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            cursor.execute(f'''SELECT dn_nr, dienstnehmer, COUNT(*) 
                FROM "{table_name}" 
                GROUP BY dn_nr, dienstnehmer 
                HAVING COUNT(*) > 1''')
            duplicates = cursor.fetchall()
            
            if duplicates:
                print(f"⚠️ Duplikate in Tabelle {table_name}:")
                for dn_nr, dienstnehmer, count in duplicates:
                    print(f"  - {dienstnehmer} (DN-Nr: {dn_nr}): {count}x")
            else:
                print(f"✅ Keine Duplikate in Tabelle {table_name}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Duplikat-Test: {e}")

if __name__ == "__main__":
    print("🚀 Starte Tests für erweiterte Import-Funktionen...")
    
    test_enhanced_import()
    test_driver_matching()
    test_duplicate_check()
    
    print("\n✅ Tests abgeschlossen!") 