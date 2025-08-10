import sys
import os
from PySide6.QtCore import QCoreApplication, QObject, QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

# Arbeitsverzeichnis auf das Skriptverzeichnis setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import der MitarbeiterSeiteQMLV2
from mitarbeiter_seite_qml_v3 import MitarbeiterSeiteQMLV2

class TestDeleteSimpleApp(QObject):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        # QML-Import-Pfade setzen
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.engine.addImportPath(current_dir)
        self.engine.addImportPath(".")
        
        # Style-Verzeichnis hinzufügen
        style_path = os.path.join(current_dir, "Style")
        self.engine.addImportPath(style_path)
        
        print(f"QML-Import-Pfade: {self.engine.importPathList()}")

        # MitarbeiterSeiteQMLV2 Backend-Instanz erstellen
        self.mitarbeiter_backend_v2 = MitarbeiterSeiteQMLV2()
        
        print("MitarbeiterSeiteQMLV2 Backend erstellt")

        # Backend an QML-Kontext registrieren
        self.engine.rootContext().setContextProperty("mitarbeiterBackendV2", self.mitarbeiter_backend_v2)
        
        print("Backend an QML-Kontext registriert")

        # Teste Backend-Methoden direkt
        self._test_delete_methods()

        # Vollständige QML-Datei laden
        qml_file = os.path.join(style_path, "MitarbeiterSeiteV3Cards.qml")
        print(f"Lade QML-Datei: {qml_file}")
        print(f"Datei existiert: {os.path.exists(qml_file)}")
        
        try:
            self.engine.load(QUrl.fromLocalFile(qml_file))
            
            # Prüfen ob QML erfolgreich geladen wurde
            if not self.engine.rootObjects():
                print("❌ Fehler beim Laden der QML-Datei")
                sys.exit(-1)
            else:
                print("✅ QML-Datei erfolgreich geladen!")
                print(f"Root-Objekte: {len(self.engine.rootObjects())}")
                print("🚀 Delete-Simple Test-Anwendung gestartet!")
                
        except Exception as e:
            print(f"❌ Ausnahme beim Laden der QML-Datei: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(-1)

    def _test_delete_methods(self):
        """Testet die Delete-Methoden direkt"""
        print("\n🔧 Teste Delete-Methoden direkt...")
        
        # Teste deleteEmployee
        if hasattr(self.mitarbeiter_backend_v2, 'deleteEmployee'):
            print("✅ deleteEmployee Methode verfügbar")
            
            # Teste mit einer nicht-existierenden ID
            try:
                print("Teste deleteEmployee mit ID 99999...")
                self.mitarbeiter_backend_v2.deleteEmployee(99999)
                print("✅ deleteEmployee funktioniert")
            except Exception as e:
                print(f"❌ Fehler bei deleteEmployee: {e}")
        else:
            print("❌ deleteEmployee Methode fehlt")
        
        # Teste deleteEmployeeWithConfirmation
        if hasattr(self.mitarbeiter_backend_v2, 'deleteEmployeeWithConfirmation'):
            print("✅ deleteEmployeeWithConfirmation Methode verfügbar")
            
            # Teste mit einer nicht-existierenden ID
            try:
                print("Teste deleteEmployeeWithConfirmation mit ID 99999...")
                self.mitarbeiter_backend_v2.deleteEmployeeWithConfirmation(99999)
                print("✅ deleteEmployeeWithConfirmation funktioniert")
            except Exception as e:
                print(f"❌ Fehler bei deleteEmployeeWithConfirmation: {e}")
        else:
            print("❌ deleteEmployeeWithConfirmation Methode fehlt")
        
        print("🔧 Delete-Methoden Tests abgeschlossen\n")

def main():
    # QApplication erstellen
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    engine = QQmlApplicationEngine()
    app.engine = engine

    # Test-App erstellen und starten
    test_app = TestDeleteSimpleApp(engine)

    # Event-Loop starten
    print("🚀 Starte Event-Loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 