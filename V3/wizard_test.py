from PySide6.QtWidgets import QApplication
from generic_wizard import GenericWizard
import sys

app = QApplication(sys.argv)
fields = [("Import-Typ", "import_typ", "combo", ["Umsatz", "Gehalt", "Funk"])]
wizard = GenericWizard(fields, title="Import Wizard")
wizard.show()
sys.exit(app.exec()) 