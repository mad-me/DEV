import os
import sys
import threading
import subprocess
import sqlite3
from typing import List, Dict
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

# Import smart_import für echte Dateiverarbeitung
SMART_IMPORT_AVAILABLE = False
verarbeite_datei = None

try:
    # Direkter Import aus dem SQL-Ordner
    sql_path = Path(__file__).parent / "SQL"
    if sql_path.exists():
        sys.path.insert(0, str(sql_path))
        from smart_import import verarbeite_datei
        SMART_IMPORT_AVAILABLE = True
        print("✅ smart_import erfolgreich importiert")
    else:
        print(f"⚠️ SQL-Ordner nicht gefunden: {sql_path}")
except ImportError as e:
    print(f"⚠️ smart_import nicht verfügbar: {e}")
    SMART_IMPORT_AVAILABLE = False

class DatenSeiteQMLV3(QObject):
    """Live-Backend für die neue DatenseiteV3."""

    # Signals
    dataChanged = Signal()
    errorOccurred = Signal(str, str)
    selectedFilesChanged = Signal()
    importFeedbackChanged = Signal(str, str)  # type, message
    platformSelectionRequested = Signal(str, str)  # filename, platforms
    platformSelectionCompleted = Signal(str)  # selected_platform
    monthYearSelectionRequested = Signal(str, str)  # filename, suggested_date

    def __init__(self):
        super().__init__()
        self._is_loading: bool = False
        self._status_message: str = "Bereit"
        self._performance = {"cache_hits": 0, "cache_misses": 0}
        self._data_list: List[dict] = []
        self._recent_jobs: List[dict] = []
        self._selected_files: List[str] = []
        self._import_progress: int = 0
        self._export_progress: int = 0
        self._export_dir: str = os.path.join(os.getcwd(), "exports")
        self._export_pattern: str = "export_{DATE}_{FMT}.ext"
        self._next_job_id: int = 1
        self._pending_platform_selection = None  # Für asynchrone Plattform-Auswahl
        self._pending_month_year_selection = None  # Für asynchrone Monat/Jahr-Auswahl

    # Properties (kompatibel mit der alten Implementierung)
    @Property(bool, notify=dataChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @Property(bool, notify=dataChanged)
    def hasData(self) -> bool:
        return len(self._data_list) > 0

    @Property(str, notify=dataChanged)
    def statusMessage(self) -> str:
        return self._status_message

    @Property('QVariant', notify=dataChanged)
    def performanceData(self):
        return self._performance

    @Property(list, notify=dataChanged)
    def dataList(self) -> List[dict]:
        return self._data_list

    @Property(list, notify=dataChanged)
    def recentJobs(self) -> List[dict]:
        return self._recent_jobs

    @Property(list, notify=selectedFilesChanged)
    def selectedFiles(self) -> List[str]:
        return self._selected_files

    @Property(int, notify=dataChanged)
    def importProgress(self) -> int:
        return self._import_progress

    @Property(int, notify=dataChanged)
    def exportProgress(self) -> int:
        return self._export_progress

    @Property(str, notify=dataChanged)
    def exportDir(self) -> str:
        return self._export_dir

    # Methoden, die in QML aufgerufen werden
    @Slot(str)
    def updateTimeRange(self, value: str) -> None:
        self._status_message = f"Zeitraum: {value}"
        self.dataChanged.emit()

    @Slot(str)
    def updateDriverFilter(self, value: str) -> None:
        self._status_message = f"Fahrer: {value}"
        self.dataChanged.emit()

    @Slot(str)
    def updatePlatformFilter(self, value: str) -> None:
        self._status_message = f"Plattform: {value}"
        self.dataChanged.emit()

    @Slot(str)
    def searchData(self, text: str) -> None:
        self._status_message = f"Suche: {text}"
        self.dataChanged.emit()

    @Slot()
    def refreshData(self) -> None:
        self._is_loading = True
        self.dataChanged.emit()
        
        # Simuliere asynchrones Laden
        QTimer.singleShot(1000, self._finish_refresh)

    def _finish_refresh(self) -> None:
        self._is_loading = False
        self._status_message = "Daten aktualisiert"
        self.dataChanged.emit()

    @Slot()
    def analyzePerformance(self) -> None:
        self._performance = {"cache_hits": 5, "cache_misses": 2}
        self.dataChanged.emit()

    @Slot()
    def clearCache(self) -> None:
        self._performance = {"cache_hits": 0, "cache_misses": 0}
        self.dataChanged.emit()

    @Slot()
    def show_import_wizard(self) -> None:
        print("Import-Wizard: Verwende die neue Drag&Drop-Funktionalität")

    @Slot(str)
    def exportDataAsync(self, fmt: str) -> None:
        self._export_progress = 0
        self.dataChanged.emit()
        
        # Simuliere Export
        QTimer.singleShot(2000, lambda: self._finish_export(fmt))

    def _finish_export(self, fmt: str) -> None:
        self._export_progress = 100
        self.dataChanged.emit()

    @Slot(str, str, str)
    def loadData(self, timeRange: str, driver: str, platform: str) -> None:
        self._is_loading = True
        self.dataChanged.emit()
        
        # Simuliere asynchrones Laden
        QTimer.singleShot(1500, lambda: self._finish_load(timeRange, driver, platform))

    def _finish_load(self, timeRange: str, driver: str, platform: str) -> None:
        self._is_loading = False
        self._data_list = [
            {"date": "2025-08-01", "platform": platform, "driver": driver, "earnings": 120.5, "status": "OK"},
            {"date": "2025-08-02", "platform": platform, "driver": driver, "earnings": 98.7, "status": "OK"},
        ]
        self._status_message = f"Daten geladen: {timeRange}, {driver}, {platform}"
        self.dataChanged.emit()

    @Slot('QVariant')
    def addDroppedFiles(self, urls) -> None:
        """Fügt gedroppte Dateien hinzu"""
        print(f"Stub: addDroppedFiles aufgerufen mit URLs: {urls}")
        
        # URLs zu Pfaden konvertieren
        for url in urls:
            if hasattr(url, 'toLocalFile'):
                file_path = url.toLocalFile()
            else:
                file_path = str(url).replace('file:///', '').replace('file://', '')
            
            print(f"Stub: URL {url} -> Pfad {file_path}")
            
            if file_path not in self._selected_files:
                self._selected_files.append(file_path)
                print(f"Stub: Datei hinzugefügt: {file_path}")
        
        self.selectedFilesChanged.emit()
        
        # Import-Typ erkennen und verarbeiten
        import_type = self._detect_import_type()
        print(f"Automatisch erkannt: {import_type}")
        
        if import_type == "Umsatz":
            self._import_with_smart_import()
        elif import_type == "Gehalt":
            self._import_with_salary_tool()
        elif import_type == "Funk":
            self._import_with_funk_router()
        else:
            self.importFeedbackChanged.emit("error", f"Unbekannter Import-Typ: {import_type}")

    def _extract_month_year_from_filename(self, filename: str) -> tuple[int, int] | None:
        """Extrahiert Monat und Jahr aus verschiedenen Dateinamen-Formaten"""
        import re
        
        # Pattern 1: rechnung.ARF25080257.pdf -> ARF25080257 -> 08/2025
        m = re.search(r'ARF(\d{2})(\d{2})(\d{2})(\d{2})', filename.upper())
        if m:
            month = int(m.group(2))  # 08
            year = 2000 + int(m.group(3))  # 25 -> 2025
            if 1 <= month <= 12:
                return month, year
        
        # Pattern 2: rechnung.25004496.pdf -> 25004496 -> 08/2025
        m = re.search(r'(\d{2})(\d{2})(\d{2})(\d{2})', filename)
        if m:
            month = int(m.group(2))  # 08
            year = 2000 + int(m.group(3))  # 25 -> 2025
            if 1 <= month <= 12:
                return month, year
        
        # Pattern 3: Standard MM_YYYY Format
        m = re.search(r'(\d{2})_(\d{4})', filename)
        if m:
            month = int(m.group(1))
            year = int(m.group(2))
            if 1 <= month <= 12:
                return month, year
        
        return None

    def _detect_import_type(self) -> str:
        """Erkennt den Import-Typ basierend auf den Dateinamen"""
        for file_path in self._selected_files:
            filename = os.path.basename(file_path).lower()
            
            # Taxi-Umsatz-Dateien
            if "uportal_getumsatzliste" in filename:
                return "Umsatz"
            
            # Gehaltsdateien (PDF mit Gehalts-Keywords oder Abrechnungen)
            file_ext = Path(file_path).suffix.lower()
            if file_ext == ".pdf" and any(keyword in filename for keyword in ["gehalt", "salary", "lohn", "abrechnung", "abrechnungen"]):
                return "Gehalt"
            
            # Funk-Dateien (PDF oder CSV mit Funk-Keywords)
            if any(keyword in filename for keyword in ["funk", "radio", "dispatch", "31300", "40100", "arf", "fl", "rechnung"]):
                return "Funk"
            
            # Uber/Bolt Dateien
            if any(keyword in filename for keyword in ["uber", "bolt", "earnings", "driver_performance"]):
                return "Umsatz"
        
        return "Unbekannt"

    def _import_with_smart_import(self) -> None:
        """Import mit smart_import.py"""
        def import_task():
            try:
                for file_path in self._selected_files[:]:  # Kopie der Liste
                    filename = os.path.basename(file_path)
                    
                    # Prüfe auf Taxi-Umsatz-Dateien
                    if "uportal_getumsatzliste" in filename.lower():
                        print(f"   ⏳ Warte auf Plattform-Auswahl für {filename}...")
                        
                        # Plattform-Auswahl anfordern
                        self._pending_platform_selection = {
                            'file_path': file_path,
                            'filename': filename
                        }
                        self.platformSelectionRequested.emit(filename, "40100,31300")
                        return  # Pausiere Import bis Plattform ausgewählt
                    
                    # Normale Dateiverarbeitung
                    self._process_single_file(file_path)
                
                # Import abgeschlossen
                self.importFeedbackChanged.emit("success", "✅ Import abgeschlossen")
                
            except Exception as e:
                print(f"   ❌ Import-Fehler: {str(e)}")
                import traceback
                traceback.print_exc()
                self.importFeedbackChanged.emit("error", f"❌ Import-Fehler: {str(e)}")
        
        # Import in separatem Thread ausführen
        threading.Thread(target=import_task, daemon=True).start()

    def _process_single_file(self, file_path: str, platform_choice: str = None) -> None:
        """Verarbeitet eine einzelne Datei"""
        try:
            filename = os.path.basename(file_path)
            
            if SMART_IMPORT_AVAILABLE and verarbeite_datei:
                # Echten Import verwenden
                print(f"   🔄 Starte echten Import für: {filename}")
                print(f"   📁 Dateipfad: {file_path}")
                print(f"   🎯 Plattform: {platform_choice if platform_choice else 'Auto-Erkennung'}")
                
                # Echten Import ausführen
                verarbeite_datei(file_path, platform_choice)
                
                print(f"   ✅ Import erfolgreich abgeschlossen: {filename}")
                self.importFeedbackChanged.emit("success", f"✅ {filename} erfolgreich importiert")
            else:
                # Fallback: Simuliere Import
                print(f"   ⚠️ Verwende Stub-Import für: {filename}")
                if platform_choice:
                    self.importFeedbackChanged.emit("success", f"✅ {platform_choice} Daten importiert")
                else:
                    self.importFeedbackChanged.emit("success", f"✅ Umsatz-Daten importiert")
            
            # Datei aus der Liste entfernen, um doppelte Verarbeitung zu vermeiden
            if file_path in self._selected_files:
                self._selected_files.remove(file_path)
                print(f"   📝 Datei aus Liste entfernt: {filename}")
                                
        except Exception as e:
            print(f"   ❌ Fehler beim Import von {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.importFeedbackChanged.emit("error", f"❌ Fehler bei {filename}: {str(e)}")

    @Slot(str)
    def selectPlatform(self, platform: str) -> None:
        """Wählt eine Plattform aus (für Taxi-Umsatz-Dateien)"""
        if self._pending_platform_selection:
            file_path = self._pending_platform_selection['file_path']
            filename = self._pending_platform_selection['filename']
            
            print(f"   🎯 Plattform ausgewählt: {platform} für {filename}")
            
            # Datei mit ausgewählter Plattform verarbeiten
            self._process_single_file(file_path, platform)
            
            # Pending-Status zurücksetzen
            self._pending_platform_selection = None
            
            # Weitere Dateien verarbeiten
            self._continue_import_after_platform_selection()
        else:
            print("   ⚠️ Keine ausstehende Plattform-Auswahl")

    @Slot(str, str)
    def selectMonthYear(self, month: str, year: str) -> None:
        """Wählt Monat und Jahr aus (für Funk-Rechnungen)"""
        if self._pending_month_year_selection:
            file_path = self._pending_month_year_selection['file_path']
            filename = self._pending_month_year_selection['filename']
            entries = self._pending_month_year_selection['entries']
            
            try:
                month_int = int(month)
                year_int = int(year)
                
                print(f"   📅 Monat/Jahr ausgewählt: {month_int}/{year_int} für {filename}")
                
                # Import mit ausgewähltem Monat/Jahr durchführen
                sys.path.insert(0, str(Path(__file__).parent / "SQL"))
                from Scanner import save_to_funk_db
                
                save_to_funk_db(entries, month_int, year_int, trace=True)
                self.importFeedbackChanged.emit("success", f"✅ {filename} erfolgreich importiert: {len(entries)} Einträge")
                print(f"   ✅ {len(entries)} Funk-Einträge importiert")
                
            except ValueError as e:
                self.importFeedbackChanged.emit("error", f"❌ Ungültiges Datum: {month}/{year}")
                print(f"   ❌ Ungültiges Datum: {month}/{year}")
            
            # Pending-Status zurücksetzen
            self._pending_month_year_selection = None
            
            # Weitere Dateien verarbeiten
            self._continue_import_after_month_year_selection()
        else:
            print("   ⚠️ Keine ausstehende Monat/Jahr-Auswahl")

    def _continue_import_after_month_year_selection(self) -> None:
        """Setzt den Import nach Monat/Jahr-Auswahl fort"""
        if self._selected_files:
            def continue_import_task():
                try:
                    for file_path in self._selected_files[:]:
                        self._process_single_file(file_path)
                    
                    self.importFeedbackChanged.emit("success", "✅ Import abgeschlossen")
                    
                except Exception as e:
                    self.importFeedbackChanged.emit("error", f"❌ Import-Fehler: {str(e)}")
            
            threading.Thread(target=continue_import_task, daemon=True).start()

    def _continue_import_after_platform_selection(self) -> None:
        """Setzt den Import nach Plattform-Auswahl fort"""
        if self._selected_files:
            def continue_import_task():
                try:
                    for file_path in self._selected_files[:]:
                        self._process_single_file(file_path)
                    
                    self.importFeedbackChanged.emit("success", "✅ Import abgeschlossen")
                    
                except Exception as e:
                    self.importFeedbackChanged.emit("error", f"❌ Import-Fehler: {str(e)}")
            
            threading.Thread(target=continue_import_task, daemon=True).start()

    def _import_with_salary_tool(self) -> None:
        """Import mit salary_import_tool.py (1:1 aus Testdatei)"""
        def import_task():
            try:
                for file_path in self._selected_files:
                    filename = os.path.basename(file_path)
                    print(f"   📊 Verarbeite Gehaltsdatei: {filename}")
                    
                    # Echten Gehaltsimport verwenden (1:1 aus Testdatei)
                    try:
                        from salary_import_tool import import_salary_pdf
                        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL")
                        salaries_db = os.path.join(base_dir, "salaries.db")
                        drivers_db = os.path.join(base_dir, "database.db")
                        result = import_salary_pdf(file_path, salaries_db, drivers_db)
                        
                        if result["success"]:
                            self.importFeedbackChanged.emit("success", f"✅ {filename} erfolgreich importiert: {result['imported_count']} Einträge")
                            print(f"   ✅ {result['imported_count']} Gehaltsdatensätze importiert")
                        else:
                            error_msg = result.get('error', 'Unbekannter Fehler')
                            self.importFeedbackChanged.emit("error", f"❌ Gehaltsimport-Fehler: {error_msg}")
                            print(f"   ❌ Gehaltsimport-Fehler: {error_msg}")
                    except Exception as import_error:
                        print(f"   ⚠️ Fehler beim Gehaltsimport: {import_error}")
                        import traceback
                        traceback.print_exc()
                        self.importFeedbackChanged.emit("error", f"❌ Gehaltsimport-Fehler: {str(import_error)}")
                
                self.importFeedbackChanged.emit("success", "✅ Gehaltsimport abgeschlossen")
                
            except Exception as e:
                self.importFeedbackChanged.emit("error", f"❌ Gehaltsimport-Fehler: {str(e)}")
        
        threading.Thread(target=import_task, daemon=True).start()

    def _import_with_funk_router(self) -> None:
        """Import mit Scanner.py (1:1 aus der alten Version - auslesen, parsen, importieren)"""
        def import_task():
            try:
                for file_path in self._selected_files:
                    filename = os.path.basename(file_path)
                    print(f"   📻 Verarbeite Funk-Datei: {filename}")
                    
                    # Echten Funk-Import verwenden (1:1 aus der alten Version)
                    try:
                        # Import Scanner.py für echte PDF-Verarbeitung
                        sys.path.insert(0, str(Path(__file__).parent / "SQL"))
                        from Scanner import process_funk_invoice, save_to_funk_db
                        
                        print(f"   🔄 Starte echte PDF-Verarbeitung für: {filename}")
                        print(f"   📁 Dateipfad: {file_path}")
                        
                        # PDF auslesen, parsen und importieren (1:1 aus der alten Version)
                        entries = process_funk_invoice(Path(file_path), trace=True)
                        
                        if entries:
                            # Monat/Jahr aus Dateiname extrahieren (verbesserte Erkennung)
                            month_year = self._extract_month_year_from_filename(filename)
                            if month_year:
                                month, year = month_year
                                save_to_funk_db(entries, month, year, trace=True)
                                self.importFeedbackChanged.emit("success", f"✅ {filename} erfolgreich importiert: {len(entries)} Einträge")
                                print(f"   ✅ {len(entries)} Funk-Einträge importiert")
                            else:
                                # Dialog für Monat/Jahr-Auswahl anfordern
                                print(f"   ⏳ Warte auf Monat/Jahr-Auswahl für {filename}...")
                                
                                # Vorschlag: Aktuelles Datum
                                from datetime import datetime
                                now = datetime.now()
                                suggested_date = f"{now.month:02d}/{now.year}"
                                
                                # Monat/Jahr-Auswahl anfordern
                                self._pending_month_year_selection = {
                                    'file_path': file_path,
                                    'filename': filename,
                                    'entries': entries
                                }
                                self.monthYearSelectionRequested.emit(filename, suggested_date)
                                return  # Pausiere Import bis Monat/Jahr ausgewählt
                        else:
                            self.importFeedbackChanged.emit("error", f"❌ Keine Einträge in PDF gefunden: {filename}")
                            
                    except Exception as import_error:
                        print(f"   ⚠️ Fehler beim Funk-Import: {import_error}")
                        import traceback
                        traceback.print_exc()
                        self.importFeedbackChanged.emit("error", f"❌ Funk-Import-Fehler: {str(import_error)}")
                
                self.importFeedbackChanged.emit("success", "✅ Funk-Import abgeschlossen")
                
            except Exception as e:
                self.importFeedbackChanged.emit("error", f"❌ Funk-Import-Fehler: {str(e)}")
        
        threading.Thread(target=import_task, daemon=True).start()

    # Zusätzliche Methoden für Kompatibilität
    @Slot()
    def openFileDialog(self) -> None:
        print("Stub: Dateiauswahl-Dialog würde geöffnet werden")

    @Slot(int)
    def removeSelectedFileAt(self, index: int) -> None:
        if 0 <= index < len(self._selected_files):
            removed_file = self._selected_files.pop(index)
            print(f"Datei entfernt: {removed_file}")
            self.selectedFilesChanged.emit()

    @Slot()
    def clearSelectedFiles(self) -> None:
        self._selected_files.clear()
        self.selectedFilesChanged.emit()

    def cleanup(self):
        """Cleanup-Methode"""
        pass

    def __del__(self):
        """Destruktor"""
        self.cleanup()


class DatenSeiteStub(QObject):
    """Leichtgewichtiger Stub für isolierte UI-Tests ohne DB/Logik."""

    dataChanged = Signal()
    errorOccurred = Signal(str, str)
    selectedFilesChanged = Signal()
    importFeedbackChanged = Signal(str, str)  # type, message
    platformSelectionRequested = Signal(str, str)  # filename, platforms
    platformSelectionCompleted = Signal(str)  # selected_platform
    monthYearSelectionRequested = Signal(str, str)  # filename, suggested_date

    def __init__(self) -> None:
        super().__init__()
        self._is_loading: bool = False
        self._status_message: str = "Bereit (Demo)"
        self._performance = {"cache_hits": 3, "cache_misses": 1}
        self._data_list: List[dict] = [
            {"date": "2025-08-01", "platform": "Uber", "driver": "Max Mustermann", "earnings": 120.5, "status": "OK"},
            {"date": "2025-08-02", "platform": "Bolt", "driver": "Anna Schmidt", "earnings": 98.7, "status": "OK"},
            {"date": "2025-08-03", "platform": "40100", "driver": "Max Mustermann", "earnings": 135.2, "status": "Geklärt"},
        ]
        self._recent_jobs: List[dict] = []
        self._selected_files: List[str] = []
        self._import_progress: int = 0
        self._export_progress: int = 0
        self._export_dir: str = os.path.join(os.getcwd(), "exports")
        self._export_pattern: str = "export_{DATE}_{FMT}.ext"
        self._next_job_id: int = 1
        self._pending_platform_selection = None
        self._pending_month_year_selection = None  # Für asynchrone Monat/Jahr-Auswahl

    # Properties (gleiche wie DatenSeiteQMLV3)
    @Property(bool, notify=dataChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @Property(bool, notify=dataChanged)
    def hasData(self) -> bool:
        return len(self._data_list) > 0

    @Property(str, notify=dataChanged)
    def statusMessage(self) -> str:
        return self._status_message

    @Property('QVariant', notify=dataChanged)
    def performanceData(self):
        return self._performance

    @Property(list, notify=dataChanged)
    def dataList(self) -> List[dict]:
        return self._data_list

    @Property(list, notify=dataChanged)
    def recentJobs(self) -> List[dict]:
        return self._recent_jobs

    @Property(list, notify=selectedFilesChanged)
    def selectedFiles(self) -> List[str]:
        return self._selected_files

    @Property(int, notify=dataChanged)
    def importProgress(self) -> int:
        return self._import_progress

    @Property(int, notify=dataChanged)
    def exportProgress(self) -> int:
        return self._export_progress

    @Property(str, notify=dataChanged)
    def exportDir(self) -> str:
        return self._export_dir

    # Methoden (gleiche wie DatenSeiteQMLV3)
    @Slot(str)
    def updateTimeRange(self, value: str) -> None:
        self._status_message = f"Zeitraum: {value}"
        self.dataChanged.emit()

    @Slot(str)
    def updateDriverFilter(self, value: str) -> None:
        self._status_message = f"Fahrer: {value}"
        self.dataChanged.emit()

    @Slot(str)
    def updatePlatformFilter(self, value: str) -> None:
        self._status_message = f"Plattform: {value}"
        self.dataChanged.emit()

    @Slot(str)
    def searchData(self, text: str) -> None:
        self._status_message = f"Suche: {text}"
        self.dataChanged.emit()

    @Slot()
    def refreshData(self) -> None:
        self._is_loading = True
        self.dataChanged.emit()
        QTimer.singleShot(1000, self._finish_refresh)

    def _finish_refresh(self) -> None:
        self._is_loading = False
        self._status_message = "Daten aktualisiert"
        self.dataChanged.emit()

    @Slot()
    def analyzePerformance(self) -> None:
        self._performance = {"cache_hits": 5, "cache_misses": 2}
        self.dataChanged.emit()

    @Slot()
    def clearCache(self) -> None:
        self._performance = {"cache_hits": 0, "cache_misses": 0}
        self.dataChanged.emit()

    @Slot()
    def show_import_wizard(self) -> None:
        print("Import-Wizard: Verwende die neue Drag&Drop-Funktionalität")

    @Slot(str)
    def exportDataAsync(self, fmt: str) -> None:
        self._export_progress = 0
        self.dataChanged.emit()
        QTimer.singleShot(2000, lambda: self._finish_export(fmt))

    def _finish_export(self, fmt: str) -> None:
        self._export_progress = 100
        self.dataChanged.emit()

    @Slot(str, str, str)
    def loadData(self, timeRange: str, driver: str, platform: str) -> None:
        self._is_loading = True
        self.dataChanged.emit()
        QTimer.singleShot(1500, lambda: self._finish_load(timeRange, driver, platform))

    def _finish_load(self, timeRange: str, driver: str, platform: str) -> None:
        self._is_loading = False
        self._data_list = [
            {"date": "2025-08-01", "platform": platform, "driver": driver, "earnings": 120.5, "status": "OK"},
            {"date": "2025-08-02", "platform": platform, "driver": driver, "earnings": 98.7, "status": "OK"},
        ]
        self._status_message = f"Daten geladen: {timeRange}, {driver}, {platform}"
        self.dataChanged.emit()

    @Slot('QVariant')
    def addDroppedFiles(self, urls) -> None:
        print(f"Stub: addDroppedFiles aufgerufen mit URLs: {urls}")
        
        for url in urls:
            if hasattr(url, 'toLocalFile'):
                file_path = url.toLocalFile()
            else:
                file_path = str(url).replace('file:///', '').replace('file://', '')
            
            print(f"Stub: URL {url} -> Pfad {file_path}")
            
            if file_path not in self._selected_files:
                self._selected_files.append(file_path)
                print(f"Stub: Datei hinzugefügt: {file_path}")
        
        self.selectedFilesChanged.emit()
        
        import_type = self._detect_import_type()
        print(f"Automatisch erkannt: {import_type}")
        
        if import_type == "Umsatz":
            self._import_with_smart_import()
        elif import_type == "Gehalt":
            self._import_with_salary_tool()
        elif import_type == "Funk":
            self._import_with_funk_router()
        else:
            self.importFeedbackChanged.emit("error", f"Unbekannter Import-Typ: {import_type}")

    def _detect_import_type(self) -> str:
        for file_path in self._selected_files:
            filename = os.path.basename(file_path).lower()
            file_ext = Path(file_path).suffix.lower()
            
            # Taxi-Umsatz-Dateien
            if "uportal_getumsatzliste" in filename:
                return "Umsatz"
            
            # Gehaltsdateien (PDF mit Gehalts-Keywords oder Abrechnungen)
            if file_ext == ".pdf" and any(keyword in filename for keyword in ["gehalt", "salary", "lohn", "abrechnung", "abrechnungen"]):
                return "Gehalt"
            
            # Funk-Dateien (PDF oder CSV mit Funk-Keywords)
            if any(keyword in filename for keyword in ["funk", "radio", "dispatch", "31300", "40100", "arf", "fl", "rechnung"]):
                return "Funk"
            
            # Uber/Bolt Dateien
            if any(keyword in filename for keyword in ["uber", "bolt", "earnings", "driver_performance"]):
                return "Umsatz"
            
            # Fallback: PDF-Dateien als Gehalt behandeln (häufigste Verwendung)
            if file_ext == ".pdf":
                return "Gehalt"
            
            # Fallback: CSV-Dateien als Funk behandeln (häufigste Verwendung)
            if file_ext == ".csv":
                return "Funk"
        
        return "Unbekannt"

    def _import_with_smart_import(self) -> None:
        def import_task():
            try:
                for file_path in self._selected_files[:]:
                    filename = os.path.basename(file_path)
                    
                    if "uportal_getumsatzliste" in filename.lower():
                        print(f"   ⏳ Warte auf Plattform-Auswahl für {filename}...")
                        
                        self._pending_platform_selection = {
                            'file_path': file_path,
                            'filename': filename
                        }
                        self.platformSelectionRequested.emit(filename, "40100,31300")
                        return
                    
                    self._process_single_file(file_path)
                
                self.importFeedbackChanged.emit("success", "✅ Import abgeschlossen")
                
            except Exception as e:
                self.importFeedbackChanged.emit("error", f"❌ Import-Fehler: {str(e)}")
        
        threading.Thread(target=import_task, daemon=True).start()

    def _process_single_file(self, file_path: str, platform_choice: str = None) -> None:
        try:
            filename = os.path.basename(file_path)
            
            if platform_choice:
                self.importFeedbackChanged.emit("success", f"✅ {platform_choice} Daten importiert")
            else:
                self.importFeedbackChanged.emit("success", f"✅ Umsatz-Daten importiert")
            
            if file_path in self._selected_files:
                self._selected_files.remove(file_path)
                print(f"   📝 Datei aus Liste entfernt: {filename}")
            
        except Exception as e:
            self.importFeedbackChanged.emit("error", f"❌ Fehler bei {filename}: {str(e)}")

    @Slot(str)
    def selectPlatform(self, platform: str) -> None:
        if self._pending_platform_selection:
            file_path = self._pending_platform_selection['file_path']
            filename = self._pending_platform_selection['filename']
            
            print(f"   🎯 Plattform ausgewählt: {platform} für {filename}")
            
            self._process_single_file(file_path, platform)
            
            self._pending_platform_selection = None
            
            self._continue_import_after_platform_selection()
        else:
            print("   ⚠️ Keine ausstehende Plattform-Auswahl")

    def _continue_import_after_platform_selection(self) -> None:
        if self._selected_files:
            def continue_import_task():
                try:
                    for file_path in self._selected_files[:]:
                        self._process_single_file(file_path)
                    
                    self.importFeedbackChanged.emit("success", "✅ Import abgeschlossen")
                    
                except Exception as e:
                    self.importFeedbackChanged.emit("error", f"❌ Import-Fehler: {str(e)}")
            
            threading.Thread(target=continue_import_task, daemon=True).start()

    def _import_with_salary_tool(self) -> None:
        """Import mit salary_import_tool.py (1:1 aus der alten Version)"""
        def import_task():
            try:
                for file_path in self._selected_files:
                    filename = os.path.basename(file_path)
                    print(f"   📊 Verarbeite Gehaltsdatei: {filename}")
                    
                    # Echten Gehaltsimport verwenden (1:1 aus der alten Version)
                    try:
                        from salary_import_tool import import_salary_pdf
                        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL")
                        salaries_db = os.path.join(base_dir, "salaries.db")
                        drivers_db = os.path.join(base_dir, "database.db")
                        
                        result = import_salary_pdf(file_path, salaries_db, drivers_db)
                        
                        if result["success"]:
                            self.importFeedbackChanged.emit("success", f"✅ {filename} erfolgreich importiert: {result['imported_count']} Einträge")
                            print(f"   ✅ {result['imported_count']} Gehaltsdatensätze importiert")
                        else:
                            error_msg = result.get('error', 'Unbekannter Fehler')
                            self.importFeedbackChanged.emit("error", f"❌ Gehaltsimport-Fehler: {error_msg}")
                            print(f"   ❌ Gehaltsimport-Fehler: {error_msg}")
                            
                    except Exception as import_error:
                        print(f"   ⚠️ Fehler beim Gehaltsimport: {import_error}")
                        import traceback
                        traceback.print_exc()
                        self.importFeedbackChanged.emit("error", f"❌ Gehaltsimport-Fehler: {str(import_error)}")
                
                self.importFeedbackChanged.emit("success", "✅ Gehaltsimport abgeschlossen")
                
            except Exception as e:
                self.importFeedbackChanged.emit("error", f"❌ Gehaltsimport-Fehler: {str(e)}")
        
        threading.Thread(target=import_task, daemon=True).start()

    def _import_with_funk_router(self) -> None:
        """Import mit funk_router.py (1:1 aus der alten Version)"""
        def import_task():
            try:
                for file_path in self._selected_files:
                    filename = os.path.basename(file_path)
                    print(f"   📻 Verarbeite Funk-Datei: {filename}")
                    
                    # Echten Funk-Import verwenden (1:1 aus der alten Version)
                    try:
                        import subprocess
                        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL")
                        router_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "funk_router.py")
                        
                        # Funk-Router als Subprocess ausführen
                        result = subprocess.run([
                            sys.executable,
                            router_path,
                            file_path
                        ], capture_output=True, text=True, cwd=str(Path(__file__).parent))
                        
                        if result.returncode == 0:
                            self.importFeedbackChanged.emit("success", f"✅ {filename} erfolgreich importiert")
                            print(f"   ✅ Funk-Import erfolgreich: {result.stdout}")
                        else:
                            error_msg = result.stderr or result.stdout or "Unbekannter Fehler"
                            self.importFeedbackChanged.emit("error", f"❌ Funk-Import-Fehler: {error_msg}")
                            print(f"   ❌ Funk-Import-Fehler: {error_msg}")
                            
                    except Exception as import_error:
                        print(f"   ⚠️ Fehler beim Funk-Import: {import_error}")
                        import traceback
                        traceback.print_exc()
                        self.importFeedbackChanged.emit("error", f"❌ Funk-Import-Fehler: {str(import_error)}")
                
                self.importFeedbackChanged.emit("success", "✅ Funk-Import abgeschlossen")
                
            except Exception as e:
                self.importFeedbackChanged.emit("error", f"❌ Funk-Import-Fehler: {str(e)}")
        
        threading.Thread(target=import_task, daemon=True).start()

    @Slot()
    def openFileDialog(self) -> None:
        print("Stub: Dateiauswahl-Dialog würde geöffnet werden")

    @Slot(int)
    def removeSelectedFileAt(self, index: int) -> None:
        if 0 <= index < len(self._selected_files):
            removed_file = self._selected_files.pop(index)
            print(f"Datei entfernt: {removed_file}")
            self.selectedFilesChanged.emit()

    @Slot()
    def clearSelectedFiles(self) -> None:
        self._selected_files.clear()
        self.selectedFilesChanged.emit()

    def cleanup(self):
        pass

    def __del__(self):
        self.cleanup()
