from import_salarie import import_salarie
from pathlib import Path

# Test-Pfade anpassen, falls nötig
pdf_path = Path(r"C:\DEV\V3\SQL\Abrechnungen\Abrechnungen 06_2025.pdf")
salaries_db_path = Path(r"C:\DEV\V3\SQL\salaries.db")
drivers_db_path = Path(r"C:\DEV\V3\SQL\database.db")

print("Verwendeter drivers_db_path:", drivers_db_path.resolve())

import_salarie(pdf_path, salaries_db_path, drivers_db_path) 