from PySide6.QtCore import QObject, Signal, Property, QThread, QTimer
from PySide6.QtWidgets import QApplication, QFileDialog
from pathlib import Path
import sys
import os
import time
from typing import Dict, List, Optional
import logging

# Import der Gehaltsimport-Funktionalität
from salary_import_tool import SalaryImportTool, create_import_tool

class SalaryImportWorker(QThread):
    """Worker-Thread für den Gehaltsimport"""
    progress_updated = Signal(str)  # Terminal-Ausgabe
    status_updated = Signal(str)    # Status-Text
    import_finished = Signal(dict)  # Ergebnis
    import_error = Signal(str)      # Fehler
    
    def __init__(self, pdf_paths: List[str], salaries_db_path: str, drivers_db_path: str):
        super().__init__()
        self.pdf_paths = pdf_paths
        self.salaries_db_path = salaries_db_path
        self.drivers_db_path = drivers_db_path
        self.is_running = True
        
    def run(self):
        """Führt den Import in einem separaten Thread aus"""
        try:
            self.progress_updated.emit("[INFO] Starte Gehaltsimport...")
            self.status_updated.emit("Initialisiere Import-Tool...")
            
            # Import-Tool erstellen
            importer = create_import_tool(self.salaries_db_path, self.drivers_db_path)
            self.progress_updated.emit("[OK] Import-Tool initialisiert")
            
            total_files = len(self.pdf_paths)
            processed_files = 0
            total_entries = 0
            
            for pdf_path in self.pdf_paths:
                if not self.is_running:
                    break
                    
                self.status_updated.emit(f"Verarbeite Datei {processed_files + 1}/{total_files}")
                self.progress_updated.emit(f"[INFO] Verarbeite: {os.path.basename(pdf_path)}")
                
                try:
                    # Einzelne PDF verarbeiten
                    result = importer.import_single_pdf(Path(pdf_path))
                    
                    if result['success']:
                        entries_count = result.get('entries_imported', 0)
                        total_entries += entries_count
                        self.progress_updated.emit(f"[OK] {os.path.basename(pdf_path)}: {entries_count} Einträge importiert")
                    else:
                        self.progress_updated.emit(f"[FEHLER] Fehler bei {os.path.basename(pdf_path)}: {result.get('error', 'Unbekannter Fehler')}")
                        
                except Exception as e:
                    self.progress_updated.emit(f"[FEHLER] Fehler bei {os.path.basename(pdf_path)}: {str(e)}")
                
                processed_files += 1
                
                # Kurze Pause für UI-Updates
                time.sleep(0.1)
            
            if self.is_running:
                self.status_updated.emit("Import abgeschlossen")
                self.progress_updated.emit(f"[OK] Import abgeschlossen! {total_entries} Einträge importiert")
                
                result = {
                    'success': True,
                    'files_processed': processed_files,
                    'total_entries': total_entries,
                    'message': f"Import erfolgreich abgeschlossen. {total_entries} Einträge aus {processed_files} Dateien importiert."
                }
                self.import_finished.emit(result)
            else:
                self.import_error.emit("Import wurde abgebrochen")
                
        except Exception as e:
            self.import_error.emit(f"Kritischer Fehler: {str(e)}")
    
    def stop(self):
        """Stoppt den Import-Thread"""
        self.is_running = False

class SalaryLoaderBackend(QObject):
    """Backend für den Loader mit Terminal für Gehaltsimport"""
    
    # Signals für QML
    statusTextChanged = Signal()
    terminalContentChanged = Signal()
    showTerminalChanged = Signal()
    processFinishedChanged = Signal()
    showLoaderChanged = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Loader-Eigenschaften
        self._status_text = "Bereit für Import..."
        self._terminal_content = "[Terminal bereit]\n"
        self._show_terminal = True
        self._process_finished = False
        self._show_loader = False
        
        # Import-Worker
        self.import_worker = None
        
        # Standard-Pfade für Datenbanken
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.default_salaries_db = os.path.join(current_dir, "salaries.db")
        self.default_drivers_db = os.path.join(current_dir, "database.db")
        
        # Logging
        self.setup_logging()
    
    def setup_logging(self):
        """Konfiguriert das Logging"""
        self.logger = logging.getLogger("SalaryLoaderBackend")
        self.logger.setLevel(logging.INFO)
        
        # Entferne bestehende Handler
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Neue Handler
        file_handler = logging.FileHandler('salary_loader.log')
        console_handler = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    # Properties für QML
    def get_status_text(self):
        return self._status_text
    
    def set_status_text(self, value):
        if self._status_text != value:
            self._status_text = value
            self.statusTextChanged.emit()
    
    def get_terminal_content(self):
        return self._terminal_content
    
    def set_terminal_content(self, value):
        if self._terminal_content != value:
            self._terminal_content = value
            self.terminalContentChanged.emit()
    
    def get_show_terminal(self):
        return self._show_terminal
    
    def set_show_terminal(self, value):
        if self._show_terminal != value:
            self._show_terminal = value
            self.showTerminalChanged.emit()
    
    def get_process_finished(self):
        return self._process_finished
    
    def set_process_finished(self, value):
        if self._process_finished != value:
            self._process_finished = value
            self.processFinishedChanged.emit()
    
    def get_show_loader(self):
        return self._show_loader
    
    def set_show_loader(self, value):
        if self._show_loader != value:
            self._show_loader = value
            self.showLoaderChanged.emit()
    
    def append_terminal(self, message: str):
        """Fügt eine Nachricht zum Terminal hinzu"""
        # Emojis durch Text ersetzen
        message = message.replace('✅', '[OK]').replace('❌', '[FEHLER]').replace('📁', '[INFO]').replace('📊', '[INFO]').replace('⏹️', '[STOP]')
        self._terminal_content += f"{message}\n"
        self.terminalContentChanged.emit()
        self.logger.info(message)
    
    def reset_loader(self):
        """Setzt den Loader zurück"""
        self._status_text = "Bereit für Import..."
        self._terminal_content = "[Terminal bereit]\n"
        self._process_finished = False
        self._show_terminal = True
        self.statusTextChanged.emit()
        self.terminalContentChanged.emit()
        self.processFinishedChanged.emit()
        self.showTerminalChanged.emit()
    
    def start_salary_import(self):
        """Startet den Gehaltsimport mit Dateiauswahl"""
        try:
            # Dateiauswahl-Dialog
            file_dialog = QFileDialog()
            file_dialog.setWindowTitle("Gehaltsabrechnungs-PDFs auswählen")
            file_dialog.setNameFilter("PDF-Dateien (*.pdf)")
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
            
            if file_dialog.exec():
                pdf_files = file_dialog.selectedFiles()
                
                if pdf_files:
                    self._show_loader = True
                    self.showLoaderChanged.emit()
                    self.reset_loader()
                    self.append_terminal("[INFO] Ausgewählte Dateien:")
                    
                    for file_path in pdf_files:
                        self.append_terminal(f"  - {os.path.basename(file_path)}")
                    
                    # Datenbank-Pfade abfragen
                    salaries_db = self.get_database_path("Gehaltsdatenbank", self.default_salaries_db)
                    drivers_db = self.get_database_path("Fahrerdatenbank", self.default_drivers_db)
                    
                    if salaries_db and drivers_db:
                        self.start_import_process(pdf_files, salaries_db, drivers_db)
                    else:
                        self.append_terminal("[FEHLER] Datenbank-Pfade nicht angegeben")
                        self._process_finished = True
                        self.processFinishedChanged.emit()
                else:
                    self.append_terminal("[FEHLER] Keine Dateien ausgewählt")
        except Exception as e:
            self.append_terminal(f"[FEHLER] Fehler beim Starten des Imports: {str(e)}")
            self._process_finished = True
            self.processFinishedChanged.emit()
    
    def get_database_path(self, title: str, default_path: str) -> Optional[str]:
        """Hilfsfunktion zum Abfragen von Datenbank-Pfaden"""
        try:
            self.append_terminal(f"[INFO] Verwende {title}: {os.path.basename(default_path)}")
            return default_path
        except Exception as e:
            self.append_terminal(f"[FEHLER] Fehler beim Abfragen der {title}: {str(e)}")
            return None
    
    def start_import_process(self, pdf_files: List[str], salaries_db: str, drivers_db: str):
        """Startet den eigentlichen Import-Prozess"""
        try:
            # Worker-Thread erstellen
            self.import_worker = SalaryImportWorker(pdf_files, salaries_db, drivers_db)
            
            # Signals verbinden
            self.import_worker.progress_updated.connect(self.append_terminal)
            self.import_worker.status_updated.connect(self.set_status_text)
            self.import_worker.import_finished.connect(self.on_import_finished)
            self.import_worker.import_error.connect(self.on_import_error)
            
            # Thread starten
            self.import_worker.start()
            
        except Exception as e:
            self.append_terminal(f"[FEHLER] Fehler beim Starten des Import-Threads: {str(e)}")
            self._process_finished = True
            self.processFinishedChanged.emit()
    
    def on_import_finished(self, result: Dict):
        """Callback für erfolgreichen Import"""
        self.append_terminal(f"[OK] {result.get('message', 'Import erfolgreich')}")
        self._status_text = "Import abgeschlossen"
        self.statusTextChanged.emit()
        self._process_finished = True
        self.processFinishedChanged.emit()
    
    def on_import_error(self, error_message: str):
        """Callback für Import-Fehler"""
        self.append_terminal(f"[FEHLER] {error_message}")
        self._status_text = "Import fehlgeschlagen"
        self.statusTextChanged.emit()
        self._process_finished = True
        self.processFinishedChanged.emit()
    
    def stop_import(self):
        """Stoppt den laufenden Import"""
        if self.import_worker and self.import_worker.isRunning():
            self.append_terminal("[STOP] Import wird gestoppt...")
            self.import_worker.stop()
            self.import_worker.wait()
            self.append_terminal("[STOP] Import gestoppt")
            self._process_finished = True
            self.processFinishedChanged.emit()
    
    def hide_loader(self):
        """Versteckt den Loader"""
        self._show_loader = False
        self.showLoaderChanged.emit()
    
    def clear_terminal(self):
        """Löscht den Terminal-Inhalt"""
        self._terminal_content = "[Terminal bereit]\n"
        self.terminalContentChanged.emit()
    
    def toggle_terminal(self):
        """Schaltet das Terminal ein/aus"""
        self._show_terminal = not self._show_terminal
        self.showTerminalChanged.emit()

    # Property-Deklarationen - PySide6 korrekte Syntax (jetzt am Ende der Klasse!)
    status_text = Property(str, get_status_text, set_status_text, notify=statusTextChanged)
    terminal_content = Property(str, get_terminal_content, set_terminal_content, notify=terminalContentChanged)
    show_terminal = Property(bool, get_show_terminal, set_show_terminal, notify=showTerminalChanged)
    process_finished = Property(bool, get_process_finished, set_process_finished, notify=processFinishedChanged)
    show_loader = Property(bool, get_show_loader, set_show_loader, notify=showLoaderChanged) 