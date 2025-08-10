"""
Neue Datenseite - Integration der DatenseiteV3 in das Hauptprogramm
Archivierte Version: archive/datenseite_qml_old.py
"""

from PySide6.QtCore import QObject, Slot, Signal, Property
import os
import sys

# Import der neuen DatenseiteV3
from datenseite_v3 import DatenSeiteQMLV3

class DatenSeiteQML(QObject):
    """
    Wrapper-Klasse für die Integration der neuen DatenseiteV3 in das Hauptprogramm.
    
    Diese Klasse stellt die gleiche Schnittstelle wie die alte datenseite_qml.py bereit,
    verwendet aber intern die neue DatenseiteV3-Implementierung.
    """
    
    # Signals (kompatibel mit der alten Implementierung)
    dataChanged = Signal()
    loadingChanged = Signal()
    chartDataChanged = Signal()
    statisticsChanged = Signal()
    errorOccurred = Signal(str, str)  # (title, message)
    
    # Import-Signals
    importStatusChanged = Signal(str)
    importProgressChanged = Signal(int)
    importFinished = Signal(bool, str)
    
    # Status-Signals
    statusMessageChanged = Signal(str)
    performanceDataChanged = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Erstelle die neue DatenseiteV3-Instanz
        self._new_backend = DatenSeiteQMLV3()
        
        # Verbinde die Signals der neuen Implementierung mit den alten Signals
        self._connect_signals()
        
        print("Neue DatenseiteV3 erfolgreich initialisiert")
    
    def _connect_signals(self):
        """Verbindet die Signals der neuen Implementierung mit den alten Signals"""
        # Daten-Signals
        self._new_backend.dataChanged.connect(self.dataChanged)
        self._new_backend.errorOccurred.connect(self.errorOccurred)
        
        # Import-Signals
        self._new_backend.importFeedbackChanged.connect(self._on_import_feedback)
        
        # Status-Signals
        # (Die neuen Signals werden direkt weitergeleitet)
    
    def _on_import_feedback(self, feedback_type: str, message: str):
        """Verarbeitet Import-Feedback von der neuen Implementierung"""
        if feedback_type == "success":
            self.importFinished.emit(True, message)
        elif feedback_type == "error":
            self.importFinished.emit(False, message)
        
        self.importStatusChanged.emit(message)
    
    # Properties (kompatibel mit der alten Implementierung)
    @Property(bool, notify=loadingChanged)
    def isLoading(self):
        return self._new_backend.isLoading
    
    @Property(list, notify=chartDataChanged)
    def chartData(self):
        return self._new_backend.dataList
    
    @Property(dict, notify=statisticsChanged)
    def statistics(self):
        return self._new_backend.performanceData
    
    @Property(str, notify=statusMessageChanged)
    def statusMessage(self):
        return self._new_backend.statusMessage
    
    @Property(dict, notify=performanceDataChanged)
    def performanceData(self):
        return self._new_backend.performanceData
    
    @Property(bool, notify=importProgressChanged)
    def isImporting(self):
        return self._new_backend.isLoading
    
    @Property(int, notify=importProgressChanged)
    def importProgress(self):
        return self._new_backend.importProgress
    
    @Property(int, notify=importProgressChanged)
    def importTotalFiles(self):
        return len(self._new_backend.selectedFiles)
    
    @Property(int, notify=importProgressChanged)
    def importCurrentFile(self):
        return 1  # Vereinfacht für die neue Implementierung
    
    @Property(bool, notify=dataChanged)
    def hasData(self):
        return len(self._new_backend.dataList) > 0
    
    @Property(int, notify=dataChanged)
    def dataCount(self):
        return len(self._new_backend.dataList)
    
    @Property(bool, notify=loadingChanged)
    def cacheEnabled(self):
        return True  # Vereinfacht für die neue Implementierung
    
    # Slots (kompatibel mit der alten Implementierung)
    @Slot(str, str, str)
    def loadData(self, time_range: str, driver: str, platform: str):
        """Lädt Daten mit den neuen Parametern"""
        self._new_backend.loadData(time_range, driver, platform)
    
    @Slot()
    def refreshData(self):
        """Aktualisiert die Daten"""
        self._new_backend.refreshData()
    
    @Slot(str)
    def updateTimeRange(self, time_range: str):
        """Aktualisiert den Zeitraum"""
        self._new_backend.updateTimeRange(time_range)
    
    @Slot(str)
    def updateDriverFilter(self, driver: str):
        """Aktualisiert den Fahrer-Filter"""
        self._new_backend.updateDriverFilter(driver)
    
    @Slot(str)
    def updatePlatformFilter(self, platform: str):
        """Aktualisiert den Plattform-Filter"""
        self._new_backend.updatePlatformFilter(platform)
    
    @Slot(str)
    def searchData(self, search_term: str):
        """Durchsucht die Daten"""
        self._new_backend.searchData(search_term)
    
    @Slot()
    def analyzePerformance(self):
        """Analysiert die Performance"""
        self._new_backend.analyzePerformance()
    
    @Slot()
    def clearCache(self):
        """Löscht den Cache"""
        self._new_backend.clearCache()
    
    @Slot(str)
    def exportDataAsync(self, export_format: str = "json"):
        """Exportiert Daten asynchron"""
        self._new_backend.exportDataAsync(export_format)
    
    @Slot()
    def exportData(self):
        """Exportiert Daten"""
        self._new_backend.exportDataAsync("json")
    
    @Slot(str, str)
    def showMessage(self, title: str, message: str):
        """Zeigt eine Nachricht an"""
        self.errorOccurred.emit(title, message)
    
    @Slot()
    def show_import_wizard(self):
        """Zeigt den Import-Wizard an (verwendet die neue Drag&Drop-Funktionalität)"""
        # Die neue Implementierung hat bereits Drag&Drop integriert
        # Daher ist kein separater Wizard mehr nötig
        print("Import-Wizard: Verwende die neue Drag&Drop-Funktionalität")
    
    # Zusätzliche Methoden für die neue Implementierung
    @Slot('QVariant')
    def addDroppedFiles(self, urls):
        """Fügt gedroppte Dateien hinzu (neue Funktionalität)"""
        self._new_backend.addDroppedFiles(urls)
    
    @Slot(str)
    def selectPlatform(self, platform: str):
        """Wählt eine Plattform aus (neue Funktionalität)"""
        self._new_backend.selectPlatform(platform)
    
    # Kompatibilitätsmethoden für alte Funktionalität
    def cleanup(self):
        """Cleanup-Methode für die alte Implementierung"""
        if hasattr(self._new_backend, 'cleanup'):
            self._new_backend.cleanup()
    
    def __del__(self):
        """Destruktor"""
        self.cleanup()
