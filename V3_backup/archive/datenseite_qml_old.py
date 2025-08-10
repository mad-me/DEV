from PySide6.QtCore import QObject, Slot, Signal, Property, QTimer, QThread
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QInputDialog
import sys
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
import json
from generic_wizard import GenericWizard
import subprocess
import calendar
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import threading
import logging
from typing import Dict, List, Optional, Any
import asyncio

# Loader-Klasse (aus loader_test.py, ggf. importieren)
try:
    from loader_test import LoadingSplash
except ImportError:
    LoadingSplash = None

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataLoadWorker(QThread):
    """Worker-Thread für asynchrones Laden von Daten"""
    dataLoaded = Signal(dict)
    errorOccurred = Signal(str)
    progressChanged = Signal(int)
    
    def __init__(self, time_range: str, driver: str, platform: str):
        super().__init__()
        self.time_range = time_range
        self.driver = driver
        self.platform = platform
        
    def run(self):
        try:
            self.progressChanged.emit(10)
            # Simuliere Datenbankzugriff
            data = self._load_database_data()
            self.progressChanged.emit(50)
            
            # Berechne Statistiken
            statistics = self._calculate_statistics(data)
            self.progressChanged.emit(80)
            
            # Erstelle Chart-Daten
            chart_data = self._create_chart_data(data)
            self.progressChanged.emit(100)
            
            result = {
                'data': data,
                'statistics': statistics,
                'chart_data': chart_data
            }
            self.dataLoaded.emit(result)
            
        except Exception as e:
            logging.error(f"Fehler beim Laden der Daten: {e}")
            self.errorOccurred.emit(str(e))
    
    def _load_database_data(self) -> List[Dict]:
        """Lädt Daten aus der Datenbank"""
        # Hier würde die echte Datenbankabfrage stehen
        # Für jetzt verwenden wir Beispieldaten
        return self._generate_sample_data()
    
    def _generate_sample_data(self) -> List[Dict]:
        """Generiert Beispieldaten"""
        sample_data = []
        
        if self.time_range == "week":
            days = 7
        elif self.time_range == "month":
            days = 30
        elif self.time_range == "quarter":
            days = 90
        else:  # year
            days = 365
            
        base_date = datetime.now()
        
        for i in range(days):
            date = base_date - timedelta(days=i)
            
            # Verschiedene Platforms
            platforms = ["Uber", "Bolt", "40100"] if self.platform == "all" else [self.platform]
            
            for p in platforms:
                # Verschiedene Fahrer
                drivers = ["Max Mustermann", "Anna Schmidt"] if self.driver == "all" else [self.driver]
                
                for d in drivers:
                    # Simuliere realistische Daten
                    earnings = round(20 + (i % 7) * 5 + hash(f"{p}{d}") % 30, 2)
                    hours = round(2 + (i % 5) * 0.5, 1)
                    
                    sample_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'platform': p,
                        'driver': d,
                        'earnings': earnings,
                        'hours': hours,
                        'trips': hash(f"{p}{d}{i}") % 10 + 1,
                        'status': 'Abgeschlossen'
                    })
        
        return sample_data
    
    def _calculate_statistics(self, data: List[Dict]) -> Dict:
        """Berechnet Statistiken aus den Daten"""
        if not data:
            return {
                'total_earnings': 0.0,
                'total_trips': 0,
                'total_hours': 0.0,
                'avg_per_hour': 0.0,
                'growth_rate': 0.0
            }
            
        total_earnings = sum(item['earnings'] for item in data)
        total_trips = sum(item['trips'] for item in data)
        total_hours = sum(item['hours'] for item in data)
        avg_per_hour = total_earnings / total_hours if total_hours > 0 else 0
        
        # Simuliere Wachstumsrate
        growth_rate = 12.5  # Prozent
        
        return {
            'total_earnings': round(total_earnings, 2),
            'total_trips': total_trips,
            'total_hours': round(total_hours, 1),
            'avg_per_hour': round(avg_per_hour, 2),
            'growth_rate': growth_rate
        }
    
    def _create_chart_data(self, data: List[Dict]) -> Dict:
        """Erstellt Daten für Charts"""
        if not data:
            return {'daily_earnings': [], 'platform_distribution': []}
            
        # Gruppiere nach Datum für Umsatz-Chart
        daily_earnings = {}
        platform_distribution = {}
        
        for item in data:
            date = item['date']
            earnings = item['earnings']
            platform = item['platform']
            
            # Tägliche Umsätze
            if date not in daily_earnings:
                daily_earnings[date] = 0
            daily_earnings[date] += earnings
            
            # Platform-Verteilung
            if platform not in platform_distribution:
                platform_distribution[platform] = 0
            platform_distribution[platform] += earnings
        
        return {
            'daily_earnings': [
                {'date': date, 'earnings': earnings}
                for date, earnings in sorted(daily_earnings.items())
            ],
            'platform_distribution': [
                {'platform': platform, 'earnings': earnings}
                for platform, earnings in platform_distribution.items()
            ]
        }

class DatenSeiteQML(QObject):
    # Erweiterte Signals für QML
    dataChanged = Signal()
    loadingChanged = Signal()
    chartDataChanged = Signal()
    statisticsChanged = Signal()
    errorOccurred = Signal(str, str)  # (title, message)
    
    # Import-Signals
    importStatusChanged = Signal(str)  # Signal für Import-Status-Updates
    importProgressChanged = Signal(int)  # Signal für Import-Fortschritt (0-100)
    importFinished = Signal(bool, str)  # Signal für Import-Abschluss (success, message)
    
    # Status-Signals
    statusMessageChanged = Signal(str)
    performanceDataChanged = Signal()
    
    def __init__(self):
        super().__init__()
        # Core Properties
        self._is_loading = False
        self._chart_data = []
        self._filtered_data = []
        self._statistics = {
            'total_earnings': 0.0,
            'total_trips': 0,
            'total_hours': 0.0,
            'avg_per_hour': 0.0,
            'growth_rate': 0.0
        }
        
        # Import-spezifische Properties
        self._is_importing = False
        self._import_progress = 0
        self._import_total_files = 0
        self._import_current_file = 0
        
        # Performance-Tracking
        self._performance_data = {
            'load_time': 0,
            'last_update': datetime.now(),
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Cache für bessere Performance
        self._data_cache = {}
        self._cache_timeout = 300  # 5 Minuten
        
        # Worker-Thread
        self._data_worker = None
        
        # Wizard-Referenzen für die UI
        self._berichte_wizard = None
        self._monat_wizard = None
        self._quartal_wizard = None
        self._fahrzeug_wizard = None
        self._import_wizard = None
        self._chart_wizard = None
        
        # Status-Nachrichten
        self._status_message = "Bereit"
        
        # Timer für automatische Updates
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._auto_refresh)
        self._update_timer.setInterval(30000)  # 30 Sekunden
        
        logging.info("DatenSeiteQML initialisiert")
        
    # Core Properties für QML
    @Property(bool, notify=loadingChanged)
    def isLoading(self):
        return self._is_loading
        
    @Property(list, notify=chartDataChanged)
    def chartData(self):
        return self._chart_data
        
    @Property(dict, notify=statisticsChanged)
    def statistics(self):
        return self._statistics
    
    @Property(str, notify=statusMessageChanged)
    def statusMessage(self):
        return self._status_message
    
    @Property(dict, notify=performanceDataChanged)
    def performanceData(self):
        return self._performance_data
    
    # Import-spezifische Properties
    @Property(bool, notify=importProgressChanged)
    def isImporting(self):
        return self._is_importing
    
    @Property(int, notify=importProgressChanged)
    def importProgress(self):
        return self._import_progress
    
    @Property(int, notify=importProgressChanged)
    def importTotalFiles(self):
        return self._import_total_files
    
    @Property(int, notify=importProgressChanged)
    def importCurrentFile(self):
        return self._import_current_file
    
    # Erweiterte Properties
    @Property(bool, notify=dataChanged)
    def hasData(self):
        return len(self._filtered_data) > 0
    
    @Property(int, notify=dataChanged)
    def dataCount(self):
        return len(self._filtered_data)
    
    @Property(bool, notify=loadingChanged)
    def cacheEnabled(self):
        return len(self._data_cache) > 0
        
    @Slot(str, str, str)
    def loadData(self, time_range: str, driver: str, platform: str):
        """Lädt Daten basierend auf den Filtern mit modernisiertem asynchronem Ansatz"""
        if self._is_loading:
            logging.warning("Daten werden bereits geladen, Anfrage ignoriert")
            return
            
        # Cache-Schlüssel erstellen
        cache_key = f"{time_range}_{driver}_{platform}"
        
        # Prüfe Cache
        if self._check_cache(cache_key):
            logging.info("Daten aus Cache geladen")
            self._performance_data['cache_hits'] += 1
            self.performanceDataChanged.emit()
            return
        
        self._performance_data['cache_misses'] += 1
        
        # Status setzen
        self._is_loading = True
        self._status_message = f"Lade Daten für {time_range}..."
        self.loadingChanged.emit()
        self.statusMessageChanged.emit()
        
        start_time = datetime.now()
        
        try:
            # Worker-Thread für asynchrones Laden
            if self._data_worker and self._data_worker.isRunning():
                self._data_worker.terminate()
                self._data_worker.wait()
            
            self._data_worker = DataLoadWorker(time_range, driver, platform)
            self._data_worker.dataLoaded.connect(self._on_data_loaded)
            self._data_worker.errorOccurred.connect(self._on_data_error)
            self._data_worker.progressChanged.connect(self._on_progress_changed)
            self._data_worker.start()
            
            # Cache-Eintrag vorbereiten
            self._current_cache_key = cache_key
            
        except Exception as e:
            logging.error(f"Fehler beim Starten des Data Workers: {e}")
            self._is_loading = False
            self._status_message = "Fehler beim Laden"
            self.loadingChanged.emit()
            self.statusMessageChanged.emit()
            self.errorOccurred.emit("Ladefehler", str(e))
    
    def _check_cache(self, cache_key: str) -> bool:
        """Prüft ob gültige Cache-Daten vorhanden sind"""
        if cache_key not in self._data_cache:
            return False
            
        cache_entry = self._data_cache[cache_key]
        cache_time = cache_entry.get('timestamp', datetime.min)
        
        if (datetime.now() - cache_time).seconds > self._cache_timeout:
            del self._data_cache[cache_key]
            return False
        
        # Lade Daten aus Cache
        self._filtered_data = cache_entry['data']
        self._statistics = cache_entry['statistics']
        self._chart_data = cache_entry['chart_data']
        
        self.dataChanged.emit()
        self.statisticsChanged.emit()
        self.chartDataChanged.emit()
        
        return True
    
    def _on_data_loaded(self, result: Dict):
        """Callback für erfolgreich geladene Daten"""
        try:
            self._filtered_data = result['data']
            self._statistics = result['statistics']
            self._chart_data = result['chart_data']
            
            # In Cache speichern
            if hasattr(self, '_current_cache_key'):
                self._data_cache[self._current_cache_key] = {
                    'data': self._filtered_data,
                    'statistics': self._statistics,
                    'chart_data': self._chart_data,
                    'timestamp': datetime.now()
                }
            
            # Performance-Daten aktualisieren
            end_time = datetime.now()
            if hasattr(self, '_load_start_time'):
                load_time = (end_time - self._load_start_time).total_seconds() * 1000
                self._performance_data['load_time'] = load_time
                self._performance_data['last_update'] = end_time
            
            self._status_message = f"Daten geladen: {len(self._filtered_data)} Einträge"
            
            # Signals emittieren
            self.dataChanged.emit()
            self.statisticsChanged.emit()
            self.chartDataChanged.emit()
            self.performanceDataChanged.emit()
            self.statusMessageChanged.emit()
            
            logging.info(f"Daten erfolgreich geladen: {len(self._filtered_data)} Einträge")
            
        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten der geladenen Daten: {e}")
            self.errorOccurred.emit("Verarbeitungsfehler", str(e))
        finally:
            self._is_loading = False
            self.loadingChanged.emit()
    
    def _on_data_error(self, error_message: str):
        """Callback für Fehler beim Laden"""
        logging.error(f"Fehler beim Laden der Daten: {error_message}")
        self._is_loading = False
        self._status_message = "Fehler beim Laden der Daten"
        
        self.loadingChanged.emit()
        self.statusMessageChanged.emit()
        self.errorOccurred.emit("Ladefehler", error_message)
    
    def _on_progress_changed(self, progress: int):
        """Callback für Fortschritts-Updates"""
        self._status_message = f"Lade Daten... {progress}%"
        self.statusMessageChanged.emit()
    
    @Slot()
    def _auto_refresh(self):
        """Automatische Aktualisierung der Daten"""
        if not self._is_loading and self._filtered_data:
            logging.info("Automatische Datenaktualisierung")
            # Hier könnten wir die letzten Filter-Parameter verwenden
            # Für jetzt nur ein einfacher Refresh
            self.refreshData()
    
    @Slot()
    def startAutoRefresh(self):
        """Startet automatische Aktualisierung"""
        self._update_timer.start()
        logging.info("Automatische Aktualisierung gestartet")
    
    @Slot()
    def stopAutoRefresh(self):
        """Stoppt automatische Aktualisierung"""
        self._update_timer.stop()
        logging.info("Automatische Aktualisierung gestoppt")
    
    @Slot()
    def clearCache(self):
        """Leert den Daten-Cache"""
        self._data_cache.clear()
        self._performance_data['cache_hits'] = 0
        self._performance_data['cache_misses'] = 0
        self.performanceDataChanged.emit()
        logging.info("Cache geleert")
    
    # Modernisierte Export-Funktionen
    @Slot(str)
    def exportDataAsync(self, export_format: str = "json"):
        """Asynchroner Export der aktuellen Daten"""
        if not self._filtered_data:
            self.errorOccurred.emit("Export-Fehler", "Keine Daten zum Exportieren verfügbar.")
            return
        
        try:
            self._status_message = "Bereite Export vor..."
            self.statusMessageChanged.emit()
            
            # Export-Worker starten (für große Datenmengen)
            export_thread = threading.Thread(target=self._perform_export, args=(export_format,))
            export_thread.daemon = True
            export_thread.start()
            
        except Exception as e:
            logging.error(f"Fehler beim Export-Start: {e}")
            self.errorOccurred.emit("Export-Fehler", str(e))
    
    def _perform_export(self, export_format: str):
        """Führt den tatsächlichen Export durch"""
        try:
            # Export-Daten erstellen
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'format': export_format,
                    'data_count': len(self._filtered_data),
                    'performance': self._performance_data
                },
                'statistics': self._statistics,
                'data': self._filtered_data,
                'chart_data': self._chart_data
            }
            
            # Datei-Dialog öffnen (im Main-Thread)
            QTimer.singleShot(0, lambda: self._show_export_dialog(export_data, export_format))
            
        except Exception as e:
            logging.error(f"Fehler beim Export: {e}")
            self.errorOccurred.emit("Export-Fehler", str(e))
    
    def _show_export_dialog(self, export_data: Dict, export_format: str):
        """Zeigt Datei-Dialog für Export"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_format == "json":
                file_filter = "JSON Dateien (*.json)"
                default_name = f"daten_export_{timestamp}.json"
            elif export_format == "csv":
                file_filter = "CSV Dateien (*.csv)"
                default_name = f"daten_export_{timestamp}.csv"
            elif export_format == "excel":
                file_filter = "Excel Dateien (*.xlsx)"
                default_name = f"daten_export_{timestamp}.xlsx"
            else:
                file_filter = "Alle Dateien (*.*)"
                default_name = f"daten_export_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Daten exportieren",
                default_name,
                file_filter
            )
            
            if file_path:
                self._save_export_file(export_data, file_path, export_format)
            else:
                self._status_message = "Export abgebrochen"
                self.statusMessageChanged.emit()
                
        except Exception as e:
            logging.error(f"Fehler beim Export-Dialog: {e}")
            self.errorOccurred.emit("Export-Fehler", str(e))
    
    def _save_export_file(self, export_data: Dict, file_path: str, export_format: str):
        """Speichert die Export-Datei"""
        try:
            if export_format == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
                    
            elif export_format == "csv":
                df = pd.DataFrame(export_data['data'])
                df.to_csv(file_path, index=False, encoding='utf-8')
                
            elif export_format == "excel":
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Daten-Sheet
                    df_data = pd.DataFrame(export_data['data'])
                    df_data.to_excel(writer, sheet_name='Daten', index=False)
                    
                    # Statistiken-Sheet
                    df_stats = pd.DataFrame([export_data['statistics']])
                    df_stats.to_excel(writer, sheet_name='Statistiken', index=False)
                    
                    # Performance-Sheet
                    df_perf = pd.DataFrame([export_data['export_info']['performance']])
                    df_perf.to_excel(writer, sheet_name='Performance', index=False)
            
            self._status_message = f"Export erfolgreich: {file_path}"
            self.statusMessageChanged.emit()
            
            # Erfolgs-Nachricht nach kurzer Verzögerung zurücksetzen
            QTimer.singleShot(3000, lambda: self._reset_status_message())
            
            logging.info(f"Export erfolgreich: {file_path}")
            
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Export-Datei: {e}")
            self.errorOccurred.emit("Export-Fehler", f"Fehler beim Speichern: {e}")
    
    def _reset_status_message(self):
        """Setzt Status-Nachricht zurück"""
        self._status_message = "Bereit"
        self.statusMessageChanged.emit()
    
    @Slot()
    def exportData(self):
        """Legacy-Methode für Rückwärtskompatibilität - ruft neue Methode auf"""
        self.exportDataAsync("json")
    
    @Slot(str, str)
    def showMessage(self, title: str, message: str):
        """Modernisierte Nachrichtenanzeige"""
        logging.info(f"{title}: {message}")
        self.errorOccurred.emit(title, message)
    
    @Slot()
    def refreshData(self):
        """Aktualisiert die Daten mit letzten Parametern"""
        # Verwende Standard-Parameter wenn keine letzten Parameter verfügbar
        self.loadData("week", "all", "all")
        logging.info("Daten manuell aktualisiert")
    
    @Slot(str)
    def updateTimeRange(self, time_range: str):
        """Aktualisiert den Zeitraum und lädt Daten neu"""
        logging.info(f"Zeitraum geändert zu: {time_range}")
        self._status_message = f"Lade Daten für {time_range}..."
        self.statusMessageChanged.emit()
        
        # Hier würde normalerweise eine intelligente Aktualisierung mit den anderen aktuellen Filtern erfolgen
        # Für jetzt verwenden wir Standard-Parameter
        self.loadData(time_range, "all", "all")
    
    @Slot(str)
    def updateDriverFilter(self, driver: str):
        """Aktualisiert den Fahrer-Filter und lädt Daten neu"""
        logging.info(f"Fahrer-Filter geändert zu: {driver}")
        self._status_message = f"Filtere nach Fahrer: {driver}..."
        self.statusMessageChanged.emit()
        
        # Hier würde normalerweise eine intelligente Aktualisierung mit den anderen aktuellen Filtern erfolgen
        self.loadData("week", driver, "all")
    
    @Slot(str)
    def updatePlatformFilter(self, platform: str):
        """Aktualisiert den Platform-Filter und lädt Daten neu"""
        logging.info(f"Platform-Filter geändert zu: {platform}")
        self._status_message = f"Filtere nach Platform: {platform}..."
        self.statusMessageChanged.emit()
        
        # Hier würde normalerweise eine intelligente Aktualisierung mit den anderen aktuellen Filtern erfolgen
        self.loadData("week", "all", platform)
    
    # Erweiterte Filter-Funktionen
    @Slot(str, str, str)
    def applyFilters(self, time_range: str, driver: str, platform: str):
        """Wendet alle Filter gleichzeitig an"""
        logging.info(f"Filter angewendet: {time_range}, {driver}, {platform}")
        self.loadData(time_range, driver, platform)
    
    @Slot()
    def resetFilters(self):
        """Setzt alle Filter zurück"""
        logging.info("Filter zurückgesetzt")
        self.loadData("week", "all", "all")
    
    @Slot(str)
    def searchData(self, search_term: str):
        """Sucht in den geladenen Daten"""
        if not self._filtered_data:
            self.errorOccurred.emit("Suchfehler", "Keine Daten zum Durchsuchen verfügbar")
            return
        
        search_term = search_term.lower().strip()
        if not search_term:
            # Reset search - show all data
            self.dataChanged.emit()
            return
        
        # Filter data based on search term
        filtered_results = []
        for item in self._filtered_data:
            # Search in multiple fields
            searchable_text = f"{item.get('driver', '')} {item.get('platform', '')} {item.get('date', '')}".lower()
            if search_term in searchable_text:
                filtered_results.append(item)
        
        logging.info(f"Suche nach '{search_term}': {len(filtered_results)} Ergebnisse")
        
        # Temporarily update filtered data for display
        original_data = self._filtered_data
        self._filtered_data = filtered_results
        self.dataChanged.emit()
        
        # Restore original data after a short delay (this is just for demo)
        QTimer.singleShot(5000, lambda: self._restore_search_data(original_data))
    
    def _restore_search_data(self, original_data: List[Dict]):
        """Stellt ursprüngliche Daten nach Suche wieder her"""
        self._filtered_data = original_data
        self.dataChanged.emit()
        logging.info("Suchergebnisse zurückgesetzt")
    
    # Performance- und Analyse-Funktionen
    @Slot()
    def analyzePerformance(self):
        """Analysiert Performance-Daten"""
        if not self._filtered_data:
            self.errorOccurred.emit("Analyse-Fehler", "Keine Daten für Analyse verfügbar")
            return
        
        try:
            analysis = {
                'data_points': len(self._filtered_data),
                'load_time': self._performance_data.get('load_time', 0),
                'cache_efficiency': (
                    self._performance_data['cache_hits'] / 
                    (self._performance_data['cache_hits'] + self._performance_data['cache_misses'])
                    if (self._performance_data['cache_hits'] + self._performance_data['cache_misses']) > 0 else 0
                ),
                'memory_usage': len(self._data_cache),
                'last_update': self._performance_data.get('last_update', datetime.now())
            }
            
            logging.info(f"Performance-Analyse: {analysis}")
            self._status_message = f"Analyse: {analysis['data_points']} Datenpunkte, Cache-Effizienz: {analysis['cache_efficiency']:.1%}"
            self.statusMessageChanged.emit()
            
            # Reset status after delay
            QTimer.singleShot(5000, self._reset_status_message)
            
        except Exception as e:
            logging.error(f"Fehler bei Performance-Analyse: {e}")
            self.errorOccurred.emit("Analyse-Fehler", str(e))

    def get_recent_weeks(self, n: int = 12) -> List[str]:
        """Gibt die letzten n Kalenderwochen zurück"""
        today = datetime.now()
        current_kw = today.isocalendar()[1]
        last_kw = current_kw - 1 if current_kw > 1 else 53
        weeks = []
        for i in range(n):
            kw = last_kw - i
            if kw < 1:
                kw += 53
            weeks.append(f"KW {kw}")
        return weeks
    
    # Cleanup-Funktionen
    def cleanup(self):
        """Bereinigt Ressourcen beim Schließen"""
        try:
            # Timer stoppen
            if self._update_timer.isActive():
                self._update_timer.stop()
            
            # Worker-Thread beenden
            if self._data_worker and self._data_worker.isRunning():
                self._data_worker.terminate()
                self._data_worker.wait(3000)  # 3 Sekunden warten
            
            # Wizards schließen
            for wizard_attr in ['_berichte_wizard', '_monat_wizard', '_quartal_wizard', 
                               '_fahrzeug_wizard', '_import_wizard', '_chart_wizard']:
                wizard = getattr(self, wizard_attr, None)
                if wizard:
                    try:
                        wizard.close()
                    except RuntimeError:
                        pass  # Widget bereits gelöscht
                    setattr(self, wizard_attr, None)
            
            # Cache leeren
            self._data_cache.clear()
            
            logging.info("DatenSeiteQML Ressourcen bereinigt")
            
        except Exception as e:
            logging.error(f"Fehler bei Cleanup: {e}")
    
    def __del__(self):
        """Destruktor"""
        self.cleanup()

    @Slot()
    def show_import_wizard(self):
        """Modernisierter Import-Wizard mit verbesserter Fehlerbehandlung"""
        logging.info('Import-Wizard gestartet')
        # Zuerst nur Import-Typ abfragen
        fields = [
            ("Import-Typ", "import_typ", "combo", ["Umsatz", "Gehalt", "Funk"])
        ]
        def import_typ_callback(data):
            print(f"[ImportWizard] Auswahl: {data}")
            if data["import_typ"] == "Gehalt":
                pdf_files, _ = QFileDialog.getOpenFileNames(
                    None,
                    "Bitte Gehaltsabrechnungs-PDFs auswählen - Mehrfachauswahl möglich",
                    "",
                    "PDF-Dateien (*.pdf)"
                )
                if not pdf_files:
                    print("Keine Dateien ausgewählt. Abbruch.")
                    return
                print(f"[DEBUG] {len(pdf_files)} Gehaltsabrechnungs-PDFs ausgewählt")

                # Loader nur anzeigen, wenn Tkinter verfügbar ist
                loader = LoadingSplash() if LoadingSplash else None
                status_lock = threading.Lock()
                status_text = {"msg": "Starte Import ..."}
                if loader:
                    def update_status():
                        with status_lock:
                            loader.text_label.config(text=status_text["msg"])
                        loader.root.after(200, update_status)
                    loader.root.after(200, update_status)

                def import_task():
                    try:
                        for i, pdf_file in enumerate(pdf_files, 1):
                            with status_lock:
                                status_text["msg"] = f"Importiere Datei {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}"
                            self._import_current_file = i
                            self._import_progress = int((i / len(pdf_files)) * 100)
                            self.importProgressChanged.emit(self._import_progress)
                            self.importStatusChanged.emit(f"Verarbeite Gehaltsabrechnung {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
                            try:
                                from salary_import_tool import import_salary_pdf
                                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL")
                                salaries_db = os.path.join(base_dir, "salaries.db")
                                drivers_db = os.path.join(base_dir, "database.db")
                                result = import_salary_pdf(pdf_file, salaries_db, drivers_db)
                                if result["success"]:
                                    with status_lock:
                                        status_text["msg"] = f"{os.path.basename(pdf_file)} erfolgreich importiert."
                                    self.importStatusChanged.emit(f"Import erfolgreich: {result['imported_count']} Einträge")
                                else:
                                    with status_lock:
                                        status_text["msg"] = f"Fehler bei {os.path.basename(pdf_file)}!"
                                    self.importStatusChanged.emit(f"Import fehlgeschlagen: {result['error']}")
                            except Exception as e:
                                with status_lock:
                                    status_text["msg"] = f"Fehler bei {os.path.basename(pdf_file)}: {e}"
                                self.importStatusChanged.emit(f"Fehler beim Import von {os.path.basename(pdf_file)}: {e}")
                        with status_lock:
                            status_text["msg"] = "Alle Gehaltsabrechnungen importiert!"
                        self._is_importing = False
                        self._import_progress = 100
                        self.importProgressChanged.emit(100)
                        self.importStatusChanged.emit("Import abgeschlossen!")
                        self.importFinished.emit(True, "Import von Gehaltsabrechnungen erfolgreich abgeschlossen!")
                    finally:
                        if loader:
                            loader.root.after(500, loader.root.destroy)

                # Import im Thread starten
                t = threading.Thread(target=import_task, daemon=True)
                t.start()
                if loader:
                    loader.show()
                return  # Wizard beenden
            elif data["import_typ"] == "Funk":
                print("==> Starte Funk-Import-Logik")
                pdf_files, _ = QFileDialog.getOpenFileNames(
                    None,
                    "Bitte Funk-PDFs auswählen (31300 oder 40100) - Mehrfachauswahl möglich",
                    "",
                    "PDF-Dateien (*.pdf)"
                )
                print(f"==> PDF-Auswahl: {pdf_files}")
                if not pdf_files:
                    print("Keine Dateien ausgewählt. Abbruch.")
                    return
                print("==> PDF-Auswahl erfolgreich, fahre fort")

                # Wizard schließen, damit der Loader sichtbar wird
                if hasattr(self, '_import_wizard') and self._import_wizard:
                    print("==> Schließe Import-Wizard für Loader-Anzeige")
                    self._import_wizard.close()
                    self._import_wizard = None

                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL")
                # Router, der PDF/CSV erkennt und an das passende Skript delegiert
                router_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "funk_router.py")

                # Loader-Backend holen
                app = QApplication.instance()
                engine = getattr(app, 'engine', None)
                salary_loader_backend = None
                if engine:
                    salary_loader_backend = engine.rootContext().contextProperty("salaryLoaderBackend")
                print(f"salary_loader_backend gefunden: {salary_loader_backend}")

                if salary_loader_backend:
                    print("==> Starte Loader-Integration")
                    salary_loader_backend.show_loader = True
                    salary_loader_backend.status_text = "Import läuft..."
                    salary_loader_backend.terminal_content = "[Terminal bereit]\n"
                    # UI-Update forcieren, damit Loader sofort erscheint
                    QApplication.processEvents()

                for i, pdf_file in enumerate(pdf_files, 1):
                    print(f"Starte Subprozess für: {pdf_file}")
                    try:
                        if salary_loader_backend:
                            salary_loader_backend.status_text = f"Importiere Datei {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}"
                            salary_loader_backend.append_terminal(f"Starte Import: {pdf_file}")
                        process = subprocess.Popen([
                            sys.executable,
                            router_path,
                            pdf_file
                        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                        for line in process.stdout:
                            if salary_loader_backend:
                                salary_loader_backend.append_terminal(line.strip())
                        process.wait()
                        if process.returncode == 0:
                            if salary_loader_backend:
                                salary_loader_backend.append_terminal(f"[OK] {os.path.basename(pdf_file)} erfolgreich importiert")
                        else:
                            if salary_loader_backend:
                                salary_loader_backend.append_terminal(f"[FEHLER] Fehler bei {os.path.basename(pdf_file)}")
                    except Exception as e:
                        print(f"Fehler beim Import von {os.path.basename(pdf_file)}: {e}")
                        if salary_loader_backend:
                            salary_loader_backend.append_terminal(f"Fehler beim Import von {os.path.basename(pdf_file)}: {e}")
                if salary_loader_backend:
                    print("==> Import abgeschlossen, Loader auf fertig setzen")
                    salary_loader_backend.status_text = "Import abgeschlossen!"
                    salary_loader_backend.process_finished = True
                print("==> Funk-Import-Logik beendet")
                return  # Wizard beenden
            elif data["import_typ"] == "Umsatz":
                # Zweiten Wizard für Umsatz-spezifische Felder öffnen
                umsatz_fields = [
                    ("Plattform", "plattform", "combo", ["Alle", "Uber", "40100", "Bolt", "31300"]),
                    ("Kalenderwoche", "kalenderwoche", "combo", self.get_recent_weeks())
                ]
                def umsatz_callback(umsatz_data):
                    plattform_map = {"Alle": "0", "Uber": "1", "40100": "2", "Bolt": "3", "31300": "4"}
                    plattform_num = plattform_map.get(umsatz_data["plattform"], "0")
                    kw_num = ''.join(filter(str.isdigit, umsatz_data["kalenderwoche"]))
                    dl_path = os.path.join("download", "src", "DL.py")
                    try:
                        subprocess.Popen([
                            sys.executable,
                            dl_path,
                            kw_num,
                            plattform_num
                        ])
                        print(f"DL.py mit KW {kw_num} und Plattform {plattform_num} gestartet.")
                    except Exception as e:
                        print(f"Fehler beim Start von DL.py: {e}")
                parent = None
                self._umsatz_wizard = GenericWizard(umsatz_fields, callback=umsatz_callback, parent=parent, title="Umsatz Import Wizard")
                self._umsatz_wizard.show()
            else:
                print("Plattform/Kalenderwoche nicht relevant für diesen Import-Typ.")
        parent = None
        self._import_wizard = GenericWizard(fields, callback=import_typ_callback, parent=parent, title="Import Wizard")
        self._import_wizard.show()

    def _get_abgeschlossene_monate(self):
        heute = datetime.now()
        monate = []
        # Deutsche Monatsnamen
        monat_namen = [
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        for i in range(1, 13):
            monat = heute.month - i
            if monat < 1:
                monat += 12
            monate.append(monat_namen[monat-1])
        return monate

    def _get_abgeschlossene_quartale(self):
        heute = datetime.now()
        quartale = []
        # Bestimme das aktuelle Quartal
        aktuelles_quartal = (heute.month - 1) // 3 + 1
        for i in range(1, 5):
            quartal = aktuelles_quartal - i
            jahr = heute.year
            if quartal < 1:
                quartal += 4
                jahr -= 1
            quartale.append(f"Q{quartal} {jahr}")
        return quartale

    @Slot()
    def show_generic_wizard(self):
        print('show_generic_wizard aufgerufen')
        # Felder für den Chart-Wizard
        fields = [
            ("Diagrammtyp", "chart_type", "combo", ["Berichte", "Umsatz Verlauf", "Plattform-Verteilung", "Fahrten pro Tag"])
        ]
        def chart_wizard_callback(data):
            print(f"[ChartWizard] Auswahl: {data}")
            if data.get("chart_type") == "Berichte":
                # Wizard für Zeitraum-Auswahl öffnen
                zeitraum_fields = [
                    ("Zeitraum", "zeitraum", "combo", ["Monat", "Quartal"])
                ]
                def zeitraum_callback(zeitraum_data):
                    print(f"[Berichte-Zeitraum] Auswahl: {zeitraum_data}")
                    if zeitraum_data.get("zeitraum") == "Monat":
                        monate = self._get_abgeschlossene_monate()
                        def monat_callback(monat_data):
                            print(f"[Berichte-Monat] Auswahl: {monat_data}")
                            # Fahrzeugauswahl nach Monat
                            fahrzeuge = self._get_fahrzeuge()
                            def fahrzeug_callback(fahrzeug_data):
                                print(f"[Berichte-Fahrzeug] Auswahl: {fahrzeug_data}")
                                fahrzeug = fahrzeug_data["fahrzeug"]
                                monat = monat_data["monat"]
                                jahr = datetime.now().year # Standardwert
                                self.erstelle_monatsbericht(fahrzeug, monat, jahr)
                                if getattr(self, '_monat_wizard', None):
                                    try:
                                        self._monat_wizard.close()
                                    except RuntimeError:
                                        pass
                                    self._monat_wizard = None
                            fahrzeug_fields = [("Fahrzeug", "fahrzeug", "combo", fahrzeuge)]
                            self._fahrzeug_wizard = GenericWizard(fahrzeug_fields, callback=fahrzeug_callback, parent=None, title="Fahrzeug wählen")
                            self._fahrzeug_wizard.show()
                            if getattr(self, '_monat_wizard', None):
                                try:
                                    self._monat_wizard.close()
                                except RuntimeError:
                                    pass
                                self._monat_wizard = None
                        monat_fields = [("Monat", "monat", "combo", monate)]
                        self._monat_wizard = GenericWizard(monat_fields, callback=monat_callback, parent=None, title="Abgeschlossener Monat")
                        self._monat_wizard.show()
                    elif zeitraum_data.get("zeitraum") == "Quartal":
                        quartale = self._get_abgeschlossene_quartale()
                        def quartal_callback(quartal_data):
                            print(f"[Berichte-Quartal] Auswahl: {quartal_data}")
                        quartal_fields = [("Quartal", "quartal", "combo", quartale)]
                        self._quartal_wizard = GenericWizard(quartal_fields, callback=quartal_callback, parent=None, title="Abgeschlossenes Quartal")
                        self._quartal_wizard.show()
                parent = None
                self._berichte_wizard = GenericWizard(zeitraum_fields, callback=zeitraum_callback, parent=parent, title="Berichte Zeitraum")
                self._berichte_wizard.show()
            else:
                # Hier könnte Logik zur Anzeige des gewählten Diagramms ergänzt werden
                pass
        parent = None
        self._chart_wizard = GenericWizard(fields, callback=chart_wizard_callback, parent=parent, title="Diagramm Wizard")
        self._chart_wizard.show()

    def _get_fahrzeuge(self):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL", "database.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT license_plate FROM vehicles")
        fahrzeuge = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sorted(fahrzeuge)

    def erstelle_monatsbericht(self, fahrzeug, monat_name, jahr):
        # 1. Monat in Zahl umwandeln
        monat_map = {
            "Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6,
            "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12
        }
        monat = monat_map[monat_name]

        # 2. Kalenderwochen bestimmen, die im Monat beginnen und Montage zählen
        cws = set()
        montage = 0
        import calendar
        from datetime import datetime
        for week in calendar.monthcalendar(jahr, monat):
            if week[0] != 0:  # Montag vorhanden
                montage += 1
                day = week[0]
                cw = datetime(jahr, monat, day).isocalendar()[1]
                cws.add(cw)
        cws = sorted(list(cws))

        # 3. Datenbanken öffnen
        import os
        import sqlite3
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL")
        revenue_db = sqlite3.connect(os.path.join(base_dir, "revenue.db"))
        running_db = sqlite3.connect(os.path.join(base_dir, "running_costs.db"))
        salaries_db = sqlite3.connect(os.path.join(base_dir, "salaries.db"))
        funk_db = sqlite3.connect(os.path.join(base_dir, "funk.db"))
        vehicles_db = sqlite3.connect(os.path.join(base_dir, "database.db"))

        # 4. Berichtsdaten sammeln
        bericht = []
        for cw in cws:
            # revenue
            cur = revenue_db.cursor()
            try:
                cur.execute(f"SELECT SUM(income), SUM(total), GROUP_CONCAT(DISTINCT driver), GROUP_CONCAT(DISTINCT deal) FROM {fahrzeug} WHERE cw = ?", (cw,))
                row = cur.fetchone()
                revenue = row[0] or 0
                total = row[1] or 0
                fahrer_liste = (row[2] or "").split(",") if row[2] else []
                # Nehme das erste Deal der Woche (oder Standard)
                deal = (row[3].split(",")[0] if row[3] else "%")
                # Fahrername für die Spalte (wenn mehrere, dann alle durch Komma getrennt)
                fahrer_name = ", ".join(fahrer_liste)
            except Exception as e:
                revenue = 0
                total = 0
                fahrer_liste = []
                deal = "%"
                fahrer_name = ""

            # running_cost_total
            cur = running_db.cursor()
            try:
                cur.execute(f"SELECT SUM(amount) FROM {fahrzeug} WHERE cw = ?", (cw,))
                running_cost_total = cur.fetchone()[0] or 0
            except Exception as e:
                running_cost_total = 0
            # running_cost_ohne_gas
            try:
                cur.execute(f"SELECT SUM(amount) FROM {fahrzeug} WHERE cw = ? AND (category IS NULL OR category != 'Gas')", (cw,))
                running_cost_ohne_gas = cur.fetchone()[0] or 0
            except Exception as e:
                running_cost_ohne_gas = 0
            # running_cost_gas_parking_halb
            try:
                cur.execute(f"SELECT SUM(CASE WHEN category = 'Gas' OR category = 'Parking' THEN amount/2 ELSE amount END) FROM {fahrzeug} WHERE cw = ?", (cw,))
                running_cost_gas_parking_halb = cur.fetchone()[0] or 0
            except Exception as e:
                running_cost_gas_parking_halb = running_cost_total

            # running_cost_ohne_gas_und_parkinghalb
            try:
                cur.execute(f"SELECT SUM(CASE WHEN category = 'Parking' THEN amount/2 WHEN category = 'Gas' THEN 0 ELSE amount END) FROM {fahrzeug} WHERE cw = ?", (cw,))
                running_cost_ohne_gas_und_parkinghalb = cur.fetchone()[0] or 0
            except Exception as e:
                running_cost_ohne_gas_und_parkinghalb = running_cost_ohne_gas

            # running_cost_summe_komplett (für Vorsteuer)
            try:
                cur.execute(f"SELECT SUM(amount) FROM {fahrzeug} WHERE cw = ?", (cw,))
                running_cost_summe_komplett = cur.fetchone()[0] or 0
            except Exception as e:
                running_cost_summe_komplett = 0

            # health-care (tokenbasiertes Matching)
            monat_tab = f"{monat:02d}_{str(jahr)[-2:]}"
            health_care = 0
            try:
                cur = salaries_db.cursor()
                cur.execute(f"SELECT dienstnehmer, zahlbetrag FROM '{monat_tab}'")
                alle_dienstnehmer = cur.fetchall()
                for fahrer in fahrer_liste:
                    such_tokens = set(fahrer.lower().strip().split())
                    best_match = None
                    best_score = 0
                    best_betrag = 0
                    for dn, betrag in alle_dienstnehmer:
                        name_tokens = set((dn or '').lower().strip().split())
                        score = len(such_tokens & name_tokens)
                        if score > best_score:
                            best_score = score
                            best_match = dn
                            best_betrag = betrag
                    print(f"Fahrer: '{fahrer}' | Bester Match: '{best_match}' | Score: {best_score} | Betrag: {best_betrag}")
                    if best_score > 0 and best_betrag:
                        anteil = (best_betrag or 0) / len(cws) if len(cws) > 0 else 0
                        health_care += anteil * 14 / 12 * 0.51
            except Exception as e:
                print(f"Fehler beim Health-Care-Matching: {e}")
                health_care = 0

            # funk
            funk = 0
            try:
                cur = funk_db.cursor()
                cur.execute(f"SELECT netto FROM '{monat_tab}' WHERE kennzeichen = ?", (fahrzeug,))
                z = cur.fetchone()
                if z:
                    funk = (z[0] or 0) / montage if montage > 0 else 0
            except Exception as e:
                funk = 0

            # Vorsteuer
            vorsteuer = (running_cost_total / 6) + (funk / 6)

            # Umsatzsteuer nach neuer Formel
            # Umsatzsteuer = Gesamtumsatz (total) * 0,1 - Vorsteuer
            umsatzsteuer = total * 0.1 - vorsteuer
            # Negative Werte sind jetzt erlaubt, daher keine Korrektur auf 0

            # insurance & credit
            cur = vehicles_db.cursor()
            try:
                cur.execute("SELECT insurance, credit FROM vehicles WHERE license_plate = ?", (fahrzeug,))
                z = cur.fetchone()
                print(f"Fahrzeug für DB-Abfrage: '{fahrzeug}', Montage: {montage}, DB-Result: {z}")
                if z and montage > 0 and z[0] is not None:
                    insurance = float(z[0]) / montage
                else:
                    insurance = ""
                if z and montage > 0 and z[1] is not None:
                    credit = float(z[1]) / montage
                else:
                    credit = ""
                print(f"Insurance geteilt: {insurance}, Credit geteilt: {credit}")
            except Exception as e:
                insurance = ""
                credit = ""

            bericht.append({
                "cw": cw,
                "fahrer": fahrer_name,
                "revenue": revenue,
                "health_care": health_care,
                "funk": funk,
                # Standardmäßig running_cost_total, für Ergo wird dynamisch gewählt
                "running_cost": running_cost_total,
                "running_cost_ohne_gas": running_cost_ohne_gas,
                "running_cost_gas_parking_halb": running_cost_gas_parking_halb,
                "running_cost_ohne_gas_und_parkinghalb": running_cost_ohne_gas_und_parkinghalb,
                "running_cost_summe_komplett": running_cost_summe_komplett,
                "umsatzsteuer": umsatzsteuer,
                "vorsteuer": vorsteuer,
                "insurance": insurance,
                "credit": credit,
                "deal": deal
            })

        # Ergo-Berechnung je nach Deal
        for row in bericht:
            deal = row.get("deal", "%")
            if deal == "P":
                rc = row.get("running_cost_ohne_gas_und_parkinghalb", row["running_cost"])
            else:
                rc = row.get("running_cost_gas_parking_halb", row["running_cost"])
            row["ergo"] = (
                row["revenue"]
                - row["health_care"]
                - row["funk"]
                - rc
                - row["umsatzsteuer"]
                - (row["insurance"] if row["insurance"] != "" else 0)
                - (row["credit"] if row["credit"] != "" else 0)
            )

        # Vorsteuer-Berechnung mit running_cost_summe_komplett
        for row in bericht:
            row["vorsteuer"] = (row["running_cost_summe_komplett"] / 6) + (row["funk"] / 6)

        # 5. PDF speichern
        from PySide6.QtWidgets import QFileDialog
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.pdfgen import canvas
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "PDF Bericht speichern",
            f"Monatsbericht_{fahrzeug}_{monat_name}_{jahr}.pdf",
            "PDF Dateien (*.pdf)"
        )
        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Neue Spalte 'Ergo' berechnen und Bericht erweitern
        # Dynamisch Spalten bestimmen, die nicht komplett leer sind
        all_keys = ["cw", "fahrer", "revenue", "health_care", "funk", "running_cost", "umsatzsteuer", "vorsteuer", "insurance", "credit", "ergo"]
        # Eine Spalte ist leer, wenn sie in allen Zeilen 0, "" oder None ist (außer 'cw' und 'fahrer')
        non_empty_keys = [k for k in all_keys if k in ("cw", "fahrer") or any(row.get(k, 0) not in (0, "", None) for row in bericht)]
        # Header-Anpassungen und Spaltenbreiten
        headers_map = {
            "cw": "CW",
            "fahrer": "driver",
            "revenue": "Revenue",
            "health_care": "Health-Care",
            "funk": "Disp",
            "running_cost": "Running Cost",
            "umsatzsteuer": "USt",
            "vorsteuer": "VSt",
            "insurance": "Insurance",
            "credit": "Credit",
            "ergo": "Ergo"
        }
        headers = [headers_map[k] for k in non_empty_keys]
        # Spaltenbreiten: CW schmaler, Fahrer breiter, Ergo wie gehabt, Rest dynamisch
        left_margin = 50
        right_margin = 50
        cw_width = 30
        driver_width = 130  # Fahrer-Spalte jetzt breiter
        ergo_width = 60
        other_columns = [k for k in non_empty_keys if k not in ("cw", "fahrer", "ergo")]
        available_width = width - left_margin - right_margin - cw_width - driver_width - ergo_width
        if len(other_columns) > 0:
            col_width = available_width / len(other_columns)
        else:
            col_width = available_width
        col_widths = []
        for k in non_empty_keys:
            if k == "cw":
                col_widths.append(cw_width)
            elif k == "fahrer":
                col_widths.append(driver_width)
            elif k == "ergo":
                col_widths.append(ergo_width)
            else:
                col_widths.append(col_width)
        # Überschriften
        y = height - 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Monatsbericht {fahrzeug} - {monat_name} {jahr}")
        y -= 30
        c.setFont("Helvetica", 10)
        x = left_margin
        for i, h in enumerate(headers):
            c.drawString(x, y, h)
            x += col_widths[i]
        y -= 20
        # Werte
        for row in bericht:
            x = left_margin
            for i, key in enumerate(non_empty_keys):
                value = row[key]
                if key == "ergo":
                    c.setFont("Helvetica-Bold", 10)
                else:
                    c.setFont("Helvetica", 10)
                if value == 0 or value == 0.0:
                    value_str = "-"
                elif key == "cw":
                    value_str = str(value)
                elif key == "fahrer":
                    value_str = str(value)
                else:
                    value_str = str(round(value, 2)) if isinstance(value, float) else str(value)
                c.drawString(x, y, value_str)
                x += col_widths[i]
            y -= 18
            if y < 60:
                c.showPage()
                y = height - 40
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, f"Monatsbericht {fahrzeug} - {monat_name} {jahr}")
                y -= 30
                c.setFont("Helvetica", 10)
                x = left_margin
                for i, h in enumerate(headers):
                    c.drawString(x, y, h)
                    x += col_widths[i]
                y -= 20
        # Summenzeile
        sum_row = {}
        for key in non_empty_keys:
            if key == "cw":
                sum_row[key] = ""
            elif key == "fahrer":
                sum_row[key] = "SUM"
            else:
                sum_row[key] = sum(row.get(key, 0) for row in bericht if isinstance(row.get(key, 0), (int, float)))
        c.setFont("Helvetica-Bold", 10)
        x = left_margin
        for i, key in enumerate(non_empty_keys):
            value = sum_row[key]
            if value == 0 or value == 0.0:
                value_str = "-"
            else:
                value_str = str(round(value, 2)) if isinstance(value, float) else str(value)
            c.drawString(x, y, value_str)
            x += col_widths[i]
        y -= 30
        # Überschrift für Running Costs Liste
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Running Costs {fahrzeug} - {monat_name} {jahr}")
        y -= 30
        c.setFont("Helvetica", 10)

        # Running Costs aus Datenbank holen (Liste wie vorher, mit zwei Spalten)
        cur = running_db.cursor()
        cur.execute(f"SELECT cw, amount, category, details FROM {fahrzeug} WHERE cw IN ({','.join(str(cw) for cw in cws)}) ORDER BY cw ASC")
        rows = cur.fetchall()
        headers2 = ["CW", "Betrag", "Kategorie", "Details"]
        col_widths2 = [40, 80, 120, width//2-50-40-80-120-20]
        max_rows_per_col = int((height - y - 40) // 16)
        col_offsets = [50, width // 2 + 10]
        row_count = 0
        col_idx = 0
        y_start = y
        # Überschriften für beide Spalten (nur erste Spalte initial)
        c.setFont("Helvetica", 10)
        for j, h in enumerate(headers2):
            c.drawString(col_offsets[0] + sum(col_widths2[:j]), y, h)
        y -= 20
        y_col = [y, y]
        c.setFont("Helvetica", 10)
        zweite_spalte_benutzt = False
        for row in rows:
            x = col_offsets[col_idx]
            for i, val in enumerate(row):
                c.drawString(x + sum(col_widths2[:i]), y_col[col_idx], str(val))
            y_col[col_idx] -= 16
            row_count += 1
            if row_count >= max_rows_per_col:
                col_idx += 1
                row_count = 0
                if col_idx >= len(col_offsets):
                    c.showPage()
                    y = height - 40
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(50, y, f"Running Costs {fahrzeug} - {monat_name} {jahr}")
                    y -= 30
                    c.setFont("Helvetica", 10)
                    for i, x in enumerate(col_offsets):
                        for j, h in enumerate(headers2):
                            c.drawString(x + sum(col_widths2[:j]), y, h)
                    y -= 20
                    y_col = [y, y]
                    col_idx = 0
                    c.setFont("Helvetica", 10)
                elif col_idx == 1:
                    zweite_spalte_benutzt = True
                    c.setFont("Helvetica", 10)
                    for j, h in enumerate(headers2):
                        c.drawString(col_offsets[1] + sum(col_widths2[:j]), y_col[1], h)
                    y_col[1] -= 20
                    c.setFont("Helvetica", 10)
        c.save()
        self.showMessage("PDF Export", f"PDF wurde gespeichert: {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    daten = DatenSeiteQML()
    engine.rootContext().setContextProperty("datenBackend", daten)
    engine.load('Style/Datenseite.qml')
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec()) 