from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
import sys
import os

class MainMenuQML(QObject):
    # Signals für QML
    pageChanged = Signal(int)
    
    def __init__(self):
        super().__init__()
        self._current_page = -1
        self._abrechnung_backend = None
        
    @Slot()
    def showPrevPage(self):
        """Zeigt die vorherige Seite in der Abrechnungsseite an"""
        if self._abrechnung_backend:
            self._abrechnung_backend.showPrevPage()
        print("Vorherige Seite")
        
    @Slot()
    def showNextPage(self):
        """Zeigt die nächste Seite in der Abrechnungsseite an"""
        if self._abrechnung_backend:
            self._abrechnung_backend.showNextPage()
        print("Nächste Seite")
        
    @Slot(int)
    def navigateToPage(self, pageIndex):
        """Navigiert zu einer bestimmten Seite"""
        self._current_page = pageIndex
        self.pageChanged.emit(pageIndex)
        print(f"Navigation zu Seite {pageIndex}")
        
    def setAbrechnungBackend(self, backend):
        """Setzt das Abrechnungs-Backend für Navigation"""
        self._abrechnung_backend = backend
        
    def getCurrentPage(self):
        """Gibt die aktuelle Seite zurück"""
        return self._current_page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImportPath(os.path.join(os.path.dirname(__file__), 'Style'))
    
    # MainMenu Backend
    mainMenu = MainMenuQML()
    engine.rootContext().setContextProperty("mainMenuBackend", mainMenu)
    
    # Lade das MainMenu
    qml_path = os.path.join(os.path.dirname(__file__), 'Style/MainMenu.qml')
    engine.load(qml_path)
    
    if not engine.rootObjects():
        print("Fehler beim Laden des MainMenu")
        sys.exit(-1)
        
    print("MainMenu erfolgreich geladen")
    sys.exit(app.exec()) 