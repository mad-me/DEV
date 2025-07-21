from import_salarie_optimized import OptimizedSalaryImporter
from pathlib import Path
import logging

# Logging für Tests konfigurieren
logging.basicConfig(level=logging.INFO)

def test_optimized_import():
    """Testet die optimierte Import-Funktionalität"""
    
    # Test-Pfade
    pdf_path = Path(r"C:\DEV\V3\SQL\Abrechnungen\Abrechnungen 06_2025.pdf")
    salaries_db_path = Path(r"C:\DEV\V3\SQL\salaries.db")
    drivers_db_path = Path(r"C:\DEV\V3\SQL\database.db")
    
    print("🧪 Teste optimierten Import-Prozess...")
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
    
    # Importer erstellen
    importer = OptimizedSalaryImporter(salaries_db_path, drivers_db_path)
    
    # Einzelne PDF importieren
    print("\n📄 Importiere einzelne PDF...")
    result = importer.import_single_pdf(pdf_path)
    print(f"✅ Import abgeschlossen: {result} Einträge importiert")
    
    # Batch-Import testen (mit derselben Datei)
    print("\n📦 Teste Batch-Import...")
    results = importer.import_salarie_batch([pdf_path])
    print(f"✅ Batch-Import abgeschlossen:")
    for filename, count in results.items():
        print(f"  {filename}: {count} Einträge")

if __name__ == "__main__":
    test_optimized_import() 