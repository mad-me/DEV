import sys
import os
import logging
from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
import abrechnungsseite_qml_optimized
import fahrzeug_seite_qml_v2
import datenseite_qml
import mitarbeiter_seite_qml
import main_menu_qml

# Debug-Konfiguration importieren
from debug_config import DEBUG_MODE, debug_print

# Logging-Konfiguration
if not DEBUG_MODE:
    # Reduziere Logging-Level für weniger Ausgaben
    logging.getLogger().setLevel(logging.WARNING)

if DEBUG_MODE:
    print("Arbeitsverzeichnis:", os.getcwd())
    print("QML_IMPORT_PATH:", os.environ.get("QML_IMPORT_PATH"))
    print("Python-Executable:", sys.executable)
# Arbeitsverzeichnis auf das Skriptverzeichnis setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))


from PySide6.QtCore import QObject, Signal, QUrl, Property
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

# Import der Backend-Klassen
from abrechnungsseite_qml_optimized import AbrechnungsSeiteQML
from datenseite_qml import DatenSeiteQML
from mitarbeiter_seite_qml import MitarbeiterSeiteQML
from fahrzeug_seite_qml_v2 import FahrzeugSeiteQMLV2
from main_menu_qml import MainMenuQML
from salary_loader_backend import SalaryLoaderBackend

class DashboardApp(QObject):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        # Style-Singleton registrieren - WICHTIG!
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # QML-Import-Pfade korrekt setzen
        self.engine.addImportPath(current_dir)
        self.engine.addImportPath(".")
        
        # Style-Verzeichnis explizit hinzufügen
        style_path = os.path.join(current_dir, "Style")
        self.engine.addImportPath(style_path)
        
        debug_print(f"QML-Import-Pfade: {self.engine.importPathList()}", "QML")

        # QML-Module explizit registrieren
        from PySide6.QtQml import qmlRegisterType
        from PySide6.QtCore import QUrl

        # Backend-Instanzen erstellen
        self.abrechnungs_backend = AbrechnungsSeiteQML()
        self.daten_backend = DatenSeiteQML()
        self.mitarbeiter_backend = MitarbeiterSeiteQML()
        self.fahrzeug_backend = FahrzeugSeiteQMLV2()
        self.main_menu_backend = MainMenuQML()
        self.salary_loader_backend = SalaryLoaderBackend()

        debug_print("Backend-Instanzen erstellt", "GENERAL")
        debug_print(f"abrechnungs_backend: {self.abrechnungs_backend}", "GENERAL")

        # Backends an QML-Kontext registrieren
        self.engine.rootContext().setContextProperty("abrechnungsBackend", self.abrechnungs_backend)
        self.engine.rootContext().setContextProperty("datenBackend", self.daten_backend)
        self.engine.rootContext().setContextProperty("mitarbeiterBackend", self.mitarbeiter_backend)
        self.engine.rootContext().setContextProperty("fahrzeugBackendV2", self.fahrzeug_backend)
        self.engine.rootContext().setContextProperty("mainMenuBackend", self.main_menu_backend)
        self.engine.rootContext().setContextProperty("salaryLoaderBackend", self.salary_loader_backend)

        debug_print("Backends an QML-Kontext registriert", "GENERAL")

        # QML-Datei laden mit verbesserter Fehlerbehandlung
        qml_file = os.path.join(style_path, "MainMenu.qml")
        print(f"Lade QML-Datei: {qml_file}")
        print(f"Datei existiert: {os.path.exists(qml_file)}")
        
        # qmldir-Datei überprüfen
        qmldir_path = os.path.join(style_path, "qmldir")
        if os.path.exists(qmldir_path):
            with open(qmldir_path, 'r', encoding='utf-8') as f:
                print(f"qmldir-Inhalt: {f.read().strip()}")
        else:
            print("qmldir-Datei nicht gefunden!")

        try:
            self.engine.load(QUrl.fromLocalFile(qml_file))
            
            # Prüfen ob QML erfolgreich geladen wurde
            if not self.engine.rootObjects():
                print("❌ Fehler beim Laden der QML-Datei")
                print("Verfügbare QML-Dateien im Style-Verzeichnis:")
                if os.path.exists(style_path):
                    for file in os.listdir(style_path):
                        if file.endswith('.qml'):
                            print(f"  - {file}")
                else:
                    print("  Style-Verzeichnis nicht gefunden!")
                sys.exit(-1)
            else:
                print("✅ QML-Datei erfolgreich geladen!")
                root_window = self.engine.rootObjects()[0]
                self.abrechnungs_backend.set_root_window(root_window)
                
        except Exception as e:
            print(f"❌ Ausnahme beim Laden der QML-Datei: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(-1)
    
def main(): # Hauptfunktion
    # QApplication für QML-Singleton-Support                
    app = QApplication(sys.argv)    # QApplication erstellen    
    app.setStyle("Fusion")  # Fusion Style für bessere QML-Unterstützung
    engine = QQmlApplicationEngine()        # QML-Engine erstellen  
    app.engine = engine  # <--- WICHTIG!

    # Dashboard-App erstellen und starten
    dashboard = DashboardApp(engine)

    # Event-Loop starten
    sys.exit(app.exec())

if __name__ == "__main__":
    main()