import sys
import os
print("Arbeitsverzeichnis:", os.getcwd())
print("QML_IMPORT_PATH:", os.environ.get("QML_IMPORT_PATH"))
print("Python-Executable:", sys.executable)
# Arbeitsverzeichnis auf das Skriptverzeichnis setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Qt-Logging reduzieren
#os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.qml.*=false;*.warning=false"

from PySide6.QtCore import QObject, Signal, QUrl, Property
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

# Import der Backend-Klassen
from abrechnungsseite_qml import AbrechnungsSeiteQML
from datenseite_qml import DatenSeiteQML
from mitarbeiter_seite_qml import MitarbeiterSeiteQML
from fahrzeug_seite_qml import FahrzeugSeiteQML
from main_menu_qml import MainMenuQML
from salary_loader_backend import SalaryLoaderBackend

class DashboardApp(QObject):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        # Style-Singleton registrieren - WICHTIG!
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.engine.addImportPath(current_dir)

        # QML-Module explizit registrieren
        from PySide6.QtQml import qmlRegisterType
        from PySide6.QtCore import QUrl
        self.engine.addImportPath(".")

        # Backend-Instanzen erstellen
        self.abrechnungs_backend = AbrechnungsSeiteQML()
        self.daten_backend = DatenSeiteQML()
        self.mitarbeiter_backend = MitarbeiterSeiteQML()
        self.fahrzeug_backend = FahrzeugSeiteQML()
        self.main_menu_backend = MainMenuQML()
        self.salary_loader_backend = SalaryLoaderBackend()

        # Backends an QML-Kontext registrieren
        self.engine.rootContext().setContextProperty("abrechnungsBackend", self.abrechnungs_backend)
        self.engine.rootContext().setContextProperty("datenBackend", self.daten_backend)
        self.engine.rootContext().setContextProperty("mitarbeiterBackend", self.mitarbeiter_backend)
        self.engine.rootContext().setContextProperty("fahrzeugBackend", self.fahrzeug_backend)
        self.engine.rootContext().setContextProperty("mainMenuBackend", self.main_menu_backend)
        self.engine.rootContext().setContextProperty("salaryLoaderBackend", self.salary_loader_backend)

        # QML-Datei laden
        qml_file = os.path.join(current_dir, "Style/MainMenu.qml")
        print(f"Lade QML-Datei: {qml_file}")
        print(f"Import-Pfad: {current_dir}")
        print(f"qmldir-Inhalt:")
        qmldir_path = os.path.join(current_dir, "Style", "qmldir")
        if os.path.exists(qmldir_path):
            with open(qmldir_path, 'r') as f:
                print(f"  {f.read().strip()}")
        else:
            print("  qmldir-Datei nicht gefunden!")

        self.engine.load(QUrl.fromLocalFile(qml_file))

        # Prüfen ob QML erfolgreich geladen wurde
        if not self.engine.rootObjects():
            print("Fehler beim Laden der QML-Datei")
            print("Verfügbare QML-Dateien:")
            for file in os.listdir(current_dir):
                if file.endswith('.qml'):
                    print(f"  - {file}")
            sys.exit(-1)
        else:
            print("QML-Datei erfolgreich geladen!")
            root_window = self.engine.rootObjects()[0]
            self.abrechnungs_backend.set_root_window(root_window)
            # root_window.showFullScreen()
    
def main():
    # QApplication für QML-Singleton-Support
    app = QApplication(sys.argv)
    app.setStyle("Basic")  # Reduziert QML-Style-Warnungen
    engine = QQmlApplicationEngine()
    app.engine = engine  # <--- WICHTIG!

    # Dashboard-App erstellen und starten
    dashboard = DashboardApp(engine)

    # Event-Loop starten
    sys.exit(app.exec())

if __name__ == "__main__":
    main()