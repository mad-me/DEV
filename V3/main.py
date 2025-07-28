import sys
import os
print("Arbeitsverzeichnis:", os.getcwd())
print("QML_IMPORT_PATH:", os.environ.get("QML_IMPORT_PATH"))
print("Python-Executable:", sys.executable)
# Arbeitsverzeichnis auf das Skriptverzeichnis setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))


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

        print("DEBUG: Backend-Instanzen erstellt")
        print("DEBUG: abrechnungs_backend:", self.abrechnungs_backend)

        # Backends an QML-Kontext registrieren
        self.engine.rootContext().setContextProperty("abrechnungsBackend", self.abrechnungs_backend)
        self.engine.rootContext().setContextProperty("datenBackend", self.daten_backend)
        self.engine.rootContext().setContextProperty("mitarbeiterBackend", self.mitarbeiter_backend)
        self.engine.rootContext().setContextProperty("fahrzeugBackend", self.fahrzeug_backend)
        self.engine.rootContext().setContextProperty("mainMenuBackend", self.main_menu_backend)
        self.engine.rootContext().setContextProperty("salaryLoaderBackend", self.salary_loader_backend)

        print("DEBUG: Backends an QML-Kontext registriert")

        # QML-Datei laden
        qml_file = os.path.join(current_dir, "Style/MainMenu.qml")
        print(f"Lade QML-Datei: {qml_file}")
        print(f"Import-Pfad: {current_dir}")
        print(f"qmldir-Inhalt:")             # qmldir-Datei auslesen       
        qmldir_path = os.path.join(current_dir, "Style", "qmldir")          # qmldir-Datei suchen   
        if os.path.exists(qmldir_path):      # Wenn qmldir-Datei gefunden wurde, dann:
            with open(qmldir_path, 'r') as f:
                print(f"  {f.read().strip()}")
        else:           # Wenn qmldir-Datei nicht gefunden wurde, dann:
            print("  qmldir-Datei nicht gefunden!")

        self.engine.load(QUrl.fromLocalFile(qml_file)) # QML-Datei laden

        # Prüfen ob QML erfolgreich geladen wurde
        if not self.engine.rootObjects():
            print("Fehler beim Laden der QML-Datei")
            print("Verfügbare QML-Dateien:")
            for file in os.listdir(current_dir):
                if file.endswith('.qml'):
                    print(f"  - {file}")
            sys.exit(-1)
        else:           # Wenn QML erfolgreich geladen wurde, dann:
            print("QML-Datei erfolgreich geladen!")
            root_window = self.engine.rootObjects()[0]
            self.abrechnungs_backend.set_root_window(root_window)
            # root_window.showFullScreen()
    
def main(): # Hauptfunktion
    # QApplication für QML-Singleton-Support                
    app = QApplication(sys.argv)    # QApplication erstellen    
    app.setStyle("Basic")  # Reduziert QML-Style-Warnungen
    engine = QQmlApplicationEngine()        # QML-Engine erstellen  
    app.engine = engine  # <--- WICHTIG!

    # Dashboard-App erstellen und starten
    dashboard = DashboardApp(engine)

    # Event-Loop starten
    sys.exit(app.exec())

if __name__ == "__main__":
    main()