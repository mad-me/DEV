import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from import_salarie import import_salarie

# Teste den Import mit der Mai-PDF
pdf_path = Path("c:/DEV/V3/SQL/Abrechnungen/Abrechnungen 05_2025.pdf")
salaries_db = Path("c:/DEV/V3/SQL/salaries.db")
drivers_db = Path("c:/DEV/V3/SQL/database.db")

print("Starte Import-Test...")
import_salarie(pdf_path, salaries_db, drivers_db)
print("Import-Test abgeschlossen.") 