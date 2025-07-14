import sys
import os
from PySide6.QtCore import QObject, Signal, QUrl, Property
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

# Import der Backend-Klassen
from abrechnungsseite_qml import AbrechnungsSeiteQML
from datenseite_qml import DatenSeiteQML
from mitarbeiter_seite_qml import MitarbeiterSeiteQML
from fahrzeug_seite_qml import FahrzeugSeiteQML
from main_menu_qml import MainMenuQML


class DashboardApp(QObject):
    def __init__(self):
        super().__init__()

        # QML Engine erstellen
        self.engine = QQmlApplicationEngine()

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

        # Backends an QML-Kontext registrieren
        self.engine.rootContext().setContextProperty("abrechnungsBackend", self.abrechnungs_backend)
        self.engine.rootContext().setContextProperty("datenBackend", self.daten_backend)
        self.engine.rootContext().setContextProperty("mitarbeiterBackend", self.mitarbeiter_backend)
        self.engine.rootContext().setContextProperty("fahrzeugBackend", self.fahrzeug_backend)
        self.engine.rootContext().setContextProperty("mainMenuBackend", self.main_menu_backend)

        # QML-Datei laden
        qml_file = os.path.join(current_dir, "Style/MainMenu.qml")
        print(f"Lade QML-Datei: {qml_file}")
        print(f"Import-Pfad: {current_dir}")
        print(f"qmldir-Inhalt:")
        qmldir_path = os.path.join(current_dir, "qmldir")
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


def main():
    # QApplication für QML-Singleton-Support
    app = QApplication(sys.argv)

    # Dashboard-App erstellen und starten
    dashboard = DashboardApp()

    # Event-Loop starten
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 