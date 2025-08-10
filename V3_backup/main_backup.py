
import sys
import os
import logging

# PySide6 Imports
from PySide6.QtCore import QObject, QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from PySide6.QtQuickControls2 import QQuickStyle

# Backend-Klassen
from abrechnungsseite_qml_optimized import AbrechnungsSeiteQML
from datenseite_v3 import DatenSeiteQMLV3
from mitarbeiter_seite_qml_v2 import MitarbeiterSeiteQMLV3
from fahrzeug_seite_qml_v2 import FahrzeugSeiteQMLV2
from main_menu_qml import MainMenuQML
from salary_loader_backend import SalaryLoaderBackend

# Debug-Konfiguration
from debug_config import DEBUG_MODE, debug_print

# Logging-Konfiguration
if not DEBUG_MODE:
    logging.getLogger().setLevel(logging.WARNING)

# Debug-Ausgaben
if DEBUG_MODE:
    debug_print(f"Arbeitsverzeichnis: {os.getcwd()}", "STARTUP")
    debug_print(f"QML_IMPORT_PATH: {os.environ.get('QML_IMPORT_PATH')}", "STARTUP")
    debug_print(f"Python-Executable: {sys.executable}", "STARTUP")

# Arbeitsverzeichnis setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class DashboardApp(QObject):
    """Hauptanwendungsklasse für das Dashboard"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.style_path = os.path.join(self.current_dir, "Style")
        
        self._setup_qml_paths()
        self._create_backends()
        self._register_backends()
        self._load_qml()
    
    def _setup_qml_paths(self):
        """QML-Import-Pfade konfigurieren"""
        self.engine.addImportPath(self.current_dir)
        self.engine.addImportPath(".")
        self.engine.addImportPath(self.style_path)
        
        debug_print(f"QML-Import-Pfade: {self.engine.importPathList()}", "QML")
    
    def _create_backends(self):
        """Backend-Instanzen erstellen"""
        self.abrechnungs_backend = AbrechnungsSeiteQML()
        self.daten_backend = DatenSeiteQMLV3()
        self.mitarbeiter_backend_v2 = MitarbeiterSeiteQMLV3()
        self.fahrzeug_backend = FahrzeugSeiteQMLV2()
        self.main_menu_backend = MainMenuQML()
        self.salary_loader_backend = SalaryLoaderBackend()
        
        debug_print("Backend-Instanzen erstellt", "INIT")
    
    def _register_backends(self):
        """Backends am QML-Kontext registrieren"""
        context = self.engine.rootContext()
        
        backends = {
            "abrechnungsBackend": self.abrechnungs_backend,
            "datenBackend": self.daten_backend,
            "mitarbeiterBackendV2": self.mitarbeiter_backend_v2,
            "fahrzeugBackendV2": self.fahrzeug_backend,
            "mainMenuBackend": self.main_menu_backend,
            "salaryLoaderBackend": self.salary_loader_backend
        }
        
        for name, backend in backends.items():
            context.setContextProperty(name, backend)
        
        debug_print("Backends registriert", "INIT")
    
    def _load_qml(self):
        """QML-Datei laden"""
        qml_file = os.path.join(self.style_path, "MainMenu.qml")
        
        if DEBUG_MODE:
            debug_print(f"Lade QML-Datei: {qml_file}", "QML")
            debug_print(f"Datei existiert: {os.path.exists(qml_file)}", "QML")
            self._check_qmldir()
        
        try:
            self.engine.load(QUrl.fromLocalFile(qml_file))
            
            if not self.engine.rootObjects():
                self._handle_qml_load_error()
            else:
                debug_print("QML-Datei erfolgreich geladen", "QML")
                root_window = self.engine.rootObjects()[0]
                self.abrechnungs_backend.set_root_window(root_window)
                
        except Exception as e:
            self._handle_qml_exception(e)
    
    def _check_qmldir(self):
        """qmldir-Datei überprüfen (nur im Debug-Modus)"""
        qmldir_path = os.path.join(self.style_path, "qmldir")
        if os.path.exists(qmldir_path):
            with open(qmldir_path, 'r', encoding='utf-8') as f:
                debug_print(f"qmldir-Inhalt: {f.read().strip()}", "QML")
        else:
            debug_print("qmldir-Datei nicht gefunden", "QML")
    
    def _handle_qml_load_error(self):
        """Fehlerbehandlung für QML-Ladefehler"""
        print("❌ Fehler beim Laden der QML-Datei")
        print("Verfügbare QML-Dateien im Style-Verzeichnis:")
        
        if os.path.exists(self.style_path):
            qml_files = [f for f in os.listdir(self.style_path) if f.endswith('.qml')]
            for file in qml_files:
                print(f"  - {file}")
        else:
            print("  Style-Verzeichnis nicht gefunden!")
        
        sys.exit(-1)
    
    def _handle_qml_exception(self, exception):
        """Fehlerbehandlung für QML-Ausnahmen"""
        print(f"❌ Ausnahme beim Laden der QML-Datei: {exception}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
        sys.exit(-1)
    
def main():
    """Hauptfunktion - Startet die Anwendung"""
    # Qt Quick Controls Style setzen (vor QApplication!)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"  # Basic Style über Umgebungsvariable
    QQuickStyle.setStyle("Basic")  # Basic Style erlaubt vollständige Anpassung
    
    # QApplication für QML-Singleton-Support
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Fusion Style für bessere QML-Unterstützung
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    app.engine = engine  # Referenz für spätere Verwendung
    
    # Dashboard-App erstellen und starten
    dashboard = DashboardApp(engine)
    
    # Event-Loop starten
    sys.exit(app.exec())


if __name__ == "__main__":
    main()