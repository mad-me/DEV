from PySide6.QtCore import QObject, Slot, Signal, Property
import sqlite3
from generic_wizard import GenericWizard
from db_manager import DBManager, DatabaseError
import difflib
from datetime import datetime
import logging
import time
from typing import Optional, Dict, Any, List
from threading import Timer

# Logger für bessere Fehlerbehandlung
logger = logging.getLogger(__name__)

class FahrzeugSeiteQMLV2(QObject):
    fahrzeugListChanged = Signal()
    filterTextChanged = Signal()
    showOnlyActiveChanged = Signal()
    selectedVehicleChanged = Signal()
    statusMessageChanged = Signal()
    isCalendarViewChanged = Signal()
    weekDataLoaded = Signal(str, int, 'QVariantList', 'QVariantList')  # license_plate, week, revenue_data, running_costs_data
    askDeleteRunningCosts = Signal(str, int, int)  # license_plate, week, count
    errorOccurred = Signal(str)  # Neues Signal für Fehlerbehandlung
    loadingChanged = Signal()  # Signal für Loading-States

    def __init__(self):
        super().__init__()
        self._fahrzeug_list = []
        self._filter_text = ""
        self._show_only_active = True
        self._selected_vehicle = None
        self._status_message = ""
        self._is_calendar_view = False
        self._db_manager = DBManager()
        self._retry_count = 0
        self._max_retries = 3
        
        # Performance-Optimierungen
        self._page_size = 50  # Anzahl Fahrzeuge pro Seite
        self._current_page = 0
        self._total_vehicles = 0
        self._all_vehicles_cache = []  # Cache für gefilterte Daten
        self._is_loading = False
        
        # Debounced Search
        self._search_timer = None
        self._search_delay = 300  # 300ms Verzögerung
        
        # Memory Management
        self._cache_size_limit = 1000  # Maximale Cache-Größe
        self._cache_timestamp = time.time()
        self._cache_ttl = 300  # 5 Minuten Cache-TTL
        
        # Logger einrichten
        self._setup_logging()
        
        # Daten beim Initialisieren laden
        self.anzeigenFahrzeuge()

    def _setup_logging(self):
        """Logging für bessere Fehlerbehandlung einrichten"""
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

    def _debounced_search(self, search_text: str):
        """Debounced Search für bessere Performance"""
        # Vorherigen Timer abbrechen
        if self._search_timer:
            self._search_timer.cancel()
        
        # Neuen Timer starten
        self._search_timer = Timer(self._search_delay / 1000.0, self._perform_search, args=[search_text])
        self._search_timer.start()
    
    def _perform_search(self, search_text: str):
        """Führt die tatsächliche Suche aus"""
        try:
            self._filter_text = search_text
            self.filterTextChanged.emit()
            
            # Cache invalidieren und neue Suche starten
            self._current_page = 0
            self._fahrzeug_list = self._load_vehicles_paginated(0, force_reload=True)
            
            self.fahrzeugListChanged.emit()
            self.setStatusMessage(f"Suche abgeschlossen: {len(self._fahrzeug_list)} Ergebnisse")
            
        except Exception as e:
            self._handle_error("Suche ausführen", e)

    def _handle_error(self, operation: str, error: Exception, show_user_message: bool = True) -> None:
        """Zentrale Fehlerbehandlung für alle Operationen"""
        error_msg = f"Fehler bei {operation}: {str(error)}"
        logger.error(error_msg, exc_info=True)
        
        if show_user_message:
            # User-friendly Fehlermeldung
            if isinstance(error, DatabaseError):
                user_msg = f"Database-Fehler: {operation} fehlgeschlagen"
            elif isinstance(error, ValueError):
                user_msg = str(error)
            elif isinstance(error, sqlite3.Error):
                user_msg = f"Database-Verbindungsfehler bei {operation}"
            else:
                user_msg = f"Unerwarteter Fehler bei {operation}"
            
            self.setStatusMessage(user_msg)
            self.errorOccurred.emit(user_msg)
        else:
            self.setStatusMessage(error_msg)

    def _retry_operation(self, operation_func, *args, **kwargs):
        """Retry-Mechanismus für kritische Operationen"""
        for attempt in range(self._max_retries):
            try:
                return operation_func(*args, **kwargs)
            except (sqlite3.Error, DatabaseError) as e:
                if attempt < self._max_retries - 1:
                    logger.warning(f"Versuch {attempt + 1} fehlgeschlagen, versuche erneut in 1s: {e}")
                    time.sleep(1)
                    continue
                else:
                    raise e
            except Exception as e:
                # Nicht-retrybare Fehler sofort werfen
                raise e

    # Neue Properties für Performance
    @Property(bool, notify=loadingChanged)
    def isLoading(self):
        return self._is_loading
    
    @Property(int, notify=loadingChanged)
    def totalVehicles(self):
        return self._total_vehicles
    
    @Property(int, notify=loadingChanged)
    def currentPage(self):
        return self._current_page
    
    @Property(int, notify=loadingChanged)
    def pageSize(self):
        return self._page_size
    
    @Property('QVariantList', notify=fahrzeugListChanged)
    def fahrzeugList(self):
        return self._fahrzeug_list

    def getFilterText(self):
        return getattr(self, '_filter_text', "")
    def setFilterText(self, value):
        if getattr(self, '_filter_text', "") != value:
            # Debounced Search verwenden
            self._debounced_search(value)
    @Property(str, fget=getFilterText, fset=setFilterText, notify=filterTextChanged)
    def filterText(self):
        return self.getFilterText()

    def getShowOnlyActive(self):
        return getattr(self, '_show_only_active', True)
    def setShowOnlyActive(self, value):
        if getattr(self, '_show_only_active', True) != value:
            self._show_only_active = value
            self.showOnlyActiveChanged.emit()
            # Sofort neu laden bei Filter-Änderung
            self.anzeigenFahrzeuge()
    @Property(bool, fget=getShowOnlyActive, fset=setShowOnlyActive, notify=showOnlyActiveChanged)
    def showOnlyActive(self):
        return self.getShowOnlyActive()

    def getSelectedVehicle(self):
        return self._selected_vehicle
    def setSelectedVehicle(self, value):
        if self._selected_vehicle != value:
            self._selected_vehicle = value
            self.selectedVehicleChanged.emit()
    @Property('QVariant', fget=getSelectedVehicle, fset=setSelectedVehicle, notify=selectedVehicleChanged)
    def selectedVehicle(self):
        return self.getSelectedVehicle()

    def getStatusMessage(self):
        return self._status_message
    def setStatusMessage(self, value):
        if self._status_message != value:
            self._status_message = value
            self.statusMessageChanged.emit()
    @Property(str, fget=getStatusMessage, fset=setStatusMessage, notify=statusMessageChanged)
    def statusMessage(self):
        return self.getStatusMessage()

    def getIsCalendarView(self):
        return self._is_calendar_view
    def setIsCalendarView(self, value):
        if self._is_calendar_view != value:
            self._is_calendar_view = value
            self.isCalendarViewChanged.emit()
    @Property(bool, fget=getIsCalendarView, fset=setIsCalendarView, notify=isCalendarViewChanged)
    def isCalendarView(self):
        return self.getIsCalendarView()

    @Slot()
    def showVehicleWizard(self):
        try:
            print("Fahrzeug-Wizard wird geöffnet...")
            self.setStatusMessage("Fahrzeug-Wizard wird geöffnet...")
            
            fields = [
                ("Kennzeichen", "license_plate", "text"),
                ("Referenz", "rfrnc", "text"),
                ("Modell", "model", "text"),
                ("Baujahr", "year", "text"),
                ("Versicherung (€)", "insurance", "text"),
                ("Finanzierung (€)", "credit", "text"),
                ("Status", "status", "combo", ["Aktiv", "Inaktiv", "Wartung"]),
                ("Stammfahrer", "stammfahrer", "text"),
                ("Notizen", "notes", "text")
            ]
            
            def wizard_callback(data):
                try:
                    print(f"[DEBUG] Neues Fahrzeug-Dict: {data}")
                    self.setStatusMessage("Fahrzeug wird gespeichert...")
                    
                    # Validierung
                    if not data.get("license_plate"):
                        raise ValueError("Kennzeichen ist erforderlich!")
                    
                    # Daten bereinigen
                    cleaned_data = {}
                    for key, value in data.items():
                        if value is not None and str(value).strip():
                            cleaned_data[key] = str(value).strip()
                        else:
                            cleaned_data[key] = ""
                    
                    # Retry-Mechanismus für kritische DB-Operation
                    def save_vehicle():
                        return self._db_manager.insert_fahrzeug(cleaned_data)
                    
                    self._retry_operation(save_vehicle)
                    
                    self.setStatusMessage(f"Fahrzeug {cleaned_data['license_plate']} erfolgreich gespeichert!")
                    print("Fahrzeug erfolgreich in DB gespeichert.")
                    logger.info(f"Fahrzeug {cleaned_data['license_plate']} erfolgreich erstellt")
                    
                except ValueError as e:
                    # User-friendly Fehlermeldung für Validierungsfehler
                    self.setStatusMessage(str(e))
                    self.errorOccurred.emit(str(e))
                    logger.warning(f"Validierungsfehler beim Erstellen des Fahrzeugs: {e}")
                except Exception as e:
                    self._handle_error("Fahrzeug speichern", e)
                
                finally:
                    self.anzeigenFahrzeuge()
                    
            wizard = GenericWizard(fields, callback=wizard_callback, title="Neues Fahrzeug anlegen")
            wizard.show()
            
        except Exception as e:
            self._handle_error("Fahrzeug-Wizard öffnen", e)

    @Slot('QVariant')
    def saveVehicleFromForm(self, vehicle_data):
        try:
            print(f"[DEBUG] Fahrzeug-Daten aus Formular: {vehicle_data}")
            self.setStatusMessage("Fahrzeug wird gespeichert...")
            
            # QJSValue zu Dictionary konvertieren
            if hasattr(vehicle_data, 'toVariant'):
                vehicle_data = vehicle_data.toVariant()
            
            # Validierung
            if not vehicle_data.get("license_plate"):
                raise ValueError("Kennzeichen ist erforderlich!")
            
            # Daten bereinigen
            cleaned_data = {}
            for key, value in vehicle_data.items():
                if value is not None and str(value).strip():
                    cleaned_data[key] = str(value).strip()
                else:
                    cleaned_data[key] = ""
            
            # Retry-Mechanismus für kritische DB-Operation
            def save_vehicle():
                return self._db_manager.insert_fahrzeug(cleaned_data)
            
            self._retry_operation(save_vehicle)
            
            self.setStatusMessage(f"Fahrzeug {cleaned_data['license_plate']} erfolgreich gespeichert!")
            print("Fahrzeug erfolgreich in DB gespeichert.")
            logger.info(f"Fahrzeug {cleaned_data['license_plate']} erfolgreich erstellt")
            
        except ValueError as e:
            # User-friendly Fehlermeldung für Validierungsfehler
            self.setStatusMessage(str(e))
            self.errorOccurred.emit(str(e))
            logger.warning(f"Validierungsfehler beim Erstellen des Fahrzeugs: {e}")
        except Exception as e:
            self._handle_error("Fahrzeug speichern", e)
        
        finally:
            self.anzeigenFahrzeuge()

    @Slot('QVariant')
    def updateVehicleFromForm(self, vehicle_data):
        """Aktualisiert ein bestehendes Fahrzeug aus dem Formular"""
        try:
            print(f"[DEBUG] Fahrzeug-Update-Daten aus Formular: {vehicle_data}")
            self.setStatusMessage("Fahrzeug wird aktualisiert...")
            
            # QJSValue zu Dictionary konvertieren
            if hasattr(vehicle_data, 'toVariant'):
                vehicle_data = vehicle_data.toVariant()
            
            # Validierung
            if not vehicle_data.get("license_plate"):
                raise ValueError("Kennzeichen ist erforderlich!")
            
            # Daten bereinigen
            cleaned_data = {}
            for key, value in vehicle_data.items():
                if value is not None and str(value).strip():
                    cleaned_data[key] = str(value).strip()
                else:
                    cleaned_data[key] = ""
            
            license_plate = cleaned_data["license_plate"]
            
            # Retry-Mechanismus für kritische DB-Operation
            def update_vehicle():
                return self._db_manager.update_fahrzeug_by_plate(license_plate, cleaned_data)
            
            self._retry_operation(update_vehicle)
            
            self.setStatusMessage(f"Fahrzeug {license_plate} erfolgreich aktualisiert!")
            print("Fahrzeug erfolgreich in DB aktualisiert.")
            logger.info(f"Fahrzeug {license_plate} erfolgreich aktualisiert")
            
        except ValueError as e:
            # User-friendly Fehlermeldung für Validierungsfehler
            self.setStatusMessage(str(e))
            self.errorOccurred.emit(str(e))
            logger.warning(f"Validierungsfehler beim Aktualisieren des Fahrzeugs: {e}")
        except Exception as e:
            self._handle_error("Fahrzeug aktualisieren", e)
        
        finally:
            self.anzeigenFahrzeuge()

    def _cleanup_cache(self):
        """Bereinigt den Cache für bessere Memory-Performance"""
        try:
            current_time = time.time()
            
            # Cache-TTL prüfen
            if current_time - self._cache_timestamp > self._cache_ttl:
                logger.info("Cache-TTL abgelaufen, Cache wird geleert")
                self._all_vehicles_cache.clear()
                self._cache_timestamp = current_time
                return
            
            # Cache-Größe prüfen
            if len(self._all_vehicles_cache) > self._cache_size_limit:
                logger.info(f"Cache-Größe überschritten ({len(self._all_vehicles_cache)}), Cache wird geleert")
                self._all_vehicles_cache.clear()
                self._cache_timestamp = current_time
                return
                
        except Exception as e:
            logger.warning(f"Fehler beim Cache-Cleanup: {e}")

    def _load_vehicles_paginated(self, page: int = 0, force_reload: bool = False) -> List[Dict]:
        """Lädt Fahrzeuge mit Pagination für bessere Performance"""
        try:
            # Cache-Cleanup vor dem Laden
            self._cleanup_cache()
            
            # Cache nur bei ersten Aufruf oder bei Force-Reload
            if not self._all_vehicles_cache or force_reload:
                self._is_loading = True
                self.loadingChanged.emit()
                
                # Alle Fahrzeuge laden (mit Retry)
                def load_all_vehicles():
                    return self._db_manager.get_all_fahrzeuge()
                
                rows = self._retry_operation(load_all_vehicles)
                
                # Daten verarbeiten und cachen
                self._all_vehicles_cache = []
                filter_text = getattr(self, '_filter_text', "").lower()
                fuzzy_threshold = 0.8
                
                for row in rows:
                    fahrzeug = {
                        "kennzeichen": row[0] or "",
                        "rfrnc": row[1] or "",
                        "modell": row[2] or "",
                        "baujahr": str(row[3]) if row[3] else "",
                        "versicherung": row[4] or "",
                        "finanzierung": row[5] or "",
                        "status": row[6] or "Aktiv",
                        "stammfahrer": row[7] or "",
                        "notizen": row[8] or "",
                        "erstellt": row[9] or "",
                        "aktualisiert": row[10] or ""
                    }
                    
                    # Filter anwenden
                    if filter_text:
                        suchfelder = [
                            str(fahrzeug["kennzeichen"]),
                            str(fahrzeug["rfrnc"]),
                            str(fahrzeug["modell"]),
                            str(fahrzeug["baujahr"]),
                            str(fahrzeug["status"]),
                            str(fahrzeug["stammfahrer"]),
                            str(fahrzeug["notizen"])
                        ]
                        # Normale Teilstring-Suche
                        match = any(filter_text in feld.lower() for feld in suchfelder)
                        # Fuzzy-Suche
                        if not match:
                            for feld in suchfelder:
                                ratio = difflib.SequenceMatcher(None, filter_text, feld.lower()).ratio()
                                if ratio >= fuzzy_threshold:
                                    match = True
                                    break
                        if not match:
                            continue
                    
                    # Status-Filter
                    if self._show_only_active and fahrzeug["status"] != "Aktiv":
                        continue
                    
                    self._all_vehicles_cache.append(fahrzeug)
                
                self._total_vehicles = len(self._all_vehicles_cache)
                self._cache_timestamp = time.time()
                self._is_loading = False
                self.loadingChanged.emit()
            
            # Pagination anwenden
            start_index = page * self._page_size
            end_index = start_index + self._page_size
            return self._all_vehicles_cache[start_index:end_index]
            
        except Exception as e:
            self._is_loading = False
            self.loadingChanged.emit()
            self._handle_error("Fahrzeuge laden (Pagination)", e)
            return []

    def clearCache(self):
        """Manuelles Cache-Clearing für Memory-Management"""
        try:
            self._all_vehicles_cache.clear()
            self._cache_timestamp = time.time()
            logger.info("Cache manuell geleert")
            self.setStatusMessage("Cache geleert")
        except Exception as e:
            self._handle_error("Cache leeren", e)

    @Slot(int)
    def loadPage(self, page: int):
        """Lädt eine spezifische Seite von Fahrzeugen"""
        try:
            self._current_page = page
            self._fahrzeug_list = self._load_vehicles_paginated(page)
            self.fahrzeugListChanged.emit()
            self.setStatusMessage(f"Seite {page + 1} geladen ({len(self._fahrzeug_list)} Fahrzeuge)")
            
        except Exception as e:
            self._handle_error("Seite laden", e)

    @Slot()
    def loadNextPage(self):
        """Lädt die nächste Seite"""
        max_pages = (self._total_vehicles - 1) // self._page_size
        if self._current_page < max_pages:
            self.loadPage(self._current_page + 1)

    @Slot()
    def loadPreviousPage(self):
        """Lädt die vorherige Seite"""
        if self._current_page > 0:
            self.loadPage(self._current_page - 1)

    @Slot()
    def anzeigenFahrzeuge(self):
        try:
            self.setStatusMessage("Fahrzeuge werden geladen...")
            
            # Cache invalidieren und erste Seite laden
            self._current_page = 0
            self._fahrzeug_list = self._load_vehicles_paginated(0, force_reload=True)
            
            self.fahrzeugListChanged.emit()
            self.setStatusMessage(f"{len(self._fahrzeug_list)} Fahrzeuge geladen (von {self._total_vehicles} insgesamt)")
            print(f"{len(self._fahrzeug_list)} Fahrzeuge geladen (von {self._total_vehicles} insgesamt)")
            logger.info(f"{len(self._fahrzeug_list)} Fahrzeuge erfolgreich geladen (Pagination)")
            
        except Exception as e:
            self._handle_error("Fahrzeuge laden", e)

    @Slot()
    def editVehicleWizard(self):
        try:
            from generic_wizard import GenericWizard
            print("Fahrzeug bearbeiten Wizard wird geöffnet...")
            self.setStatusMessage("Fahrzeug bearbeiten Wizard wird geöffnet...")
            
            # Retry-Mechanismus für kritische DB-Operation
            def load_all_vehicles():
                return self._db_manager.get_all_fahrzeuge()
            
            alle_fahrzeuge = self._retry_operation(load_all_vehicles)
            kennzeichen_liste = [row[0] for row in alle_fahrzeuge]
            
            # Felder für den Wizard
            fields = [
                ("Kennzeichen", "license_plate", "combo", kennzeichen_liste),
                ("Referenz", "rfrnc", "text"),
                ("Modell", "model", "text"),
                ("Baujahr", "year", "text"),
                ("Versicherung (€)", "insurance", "text"),
                ("Finanzierung (€)", "credit", "text"),
                ("Status", "status", "combo", ["Aktiv", "Inaktiv", "Wartung"]),
                ("Stammfahrer", "stammfahrer", "text"),
                ("Notizen", "notes", "text")
            ]
            
            def wizard_callback(data):
                try:
                    print(f"[DEBUG] Bearbeitetes Fahrzeug: {data}")
                    self.setStatusMessage("Fahrzeug wird aktualisiert...")
                    
                    # Retry-Mechanismus für kritische DB-Operation
                    def update_vehicle():
                        return self._db_manager.update_fahrzeug_by_plate(data["license_plate"], data)
                    
                    self._retry_operation(update_vehicle)
                    
                    self.setStatusMessage(f"Fahrzeug {data['license_plate']} erfolgreich aktualisiert!")
                    print("Fahrzeug erfolgreich aktualisiert.")
                    logger.info(f"Fahrzeug {data['license_plate']} erfolgreich aktualisiert")
                    
                except ValueError as e:
                    # User-friendly Fehlermeldung für Validierungsfehler
                    self.setStatusMessage(str(e))
                    self.errorOccurred.emit(str(e))
                    logger.warning(f"Validierungsfehler beim Aktualisieren des Fahrzeugs: {e}")
                except Exception as e:
                    self._handle_error("Fahrzeug aktualisieren", e)
                
                finally:
                    self.anzeigenFahrzeuge()
            
            # Vorbelegung der Felder nach Auswahl
            def on_combo_change(index):
                if index < 0 or index >= len(alle_fahrzeuge):
                    return
                row = alle_fahrzeuge[index]
                # Mapping: (license_plate, rfrnc, model, year, insurance, credit, status, stammfahrer, notes, created_at, updated_at)
                if "rfrnc" in wizard.inputs:
                    wizard.inputs["rfrnc"].setText(row[1] or "")
                if "model" in wizard.inputs:
                    wizard.inputs["model"].setText(row[2] or "")
                if "year" in wizard.inputs:
                    wizard.inputs["year"].setText(str(row[3]) if row[3] else "")
                if "insurance" in wizard.inputs:
                    wizard.inputs["insurance"].setText(str(row[4]) if row[4] else "")
                if "credit" in wizard.inputs:
                    wizard.inputs["credit"].setText(str(row[5]) if row[5] else "")
                if "status" in wizard.inputs and len(row) > 6:
                    wizard.inputs["status"].setCurrentText(row[6] or "Aktiv")
                if "stammfahrer" in wizard.inputs and len(row) > 7:
                    wizard.inputs["stammfahrer"].setText(row[7] or "")
                if "notes" in wizard.inputs and len(row) > 8:
                    wizard.inputs["notes"].setText(row[8] or "")
            
            wizard = GenericWizard(fields, callback=wizard_callback, title="Fahrzeug bearbeiten")
            # ComboBox-Change-Handler setzen
            if hasattr(wizard, "inputs") and "license_plate" in wizard.inputs:
                combo = wizard.inputs["license_plate"]
                combo.currentIndexChanged.connect(on_combo_change)
            wizard.show()
            
        except Exception as e:
            self._handle_error("Fahrzeug-Wizard öffnen", e)

    @Slot(str)
    def editVehicleWizard_by_id(self, license_plate):
        try:
            from generic_wizard import GenericWizard
            print(f"Fahrzeug bearbeiten Wizard für Kennzeichen {license_plate} wird geöffnet...")
            self.setStatusMessage(f"Fahrzeug {license_plate} wird bearbeitet...")
            
            # Retry-Mechanismus für kritische DB-Operation
            def load_vehicle():
                return self._db_manager.get_fahrzeug_by_plate(license_plate)
            
            row = self._retry_operation(load_vehicle)
            if not row:
                raise ValueError(f"Kein Fahrzeug mit Kennzeichen {license_plate} gefunden.")
            
            # Felder für den Wizard
            fields = [
                ("Kennzeichen", "license_plate", "text"),
                ("Referenz", "rfrnc", "text"),
                ("Modell", "model", "text"),
                ("Baujahr", "year", "text"),
                ("Versicherung (€)", "insurance", "text"),
                ("Finanzierung (€)", "credit", "text"),
                ("Status", "status", "combo", ["Aktiv", "Inaktiv", "Wartung"]),
                ("Stammfahrer", "stammfahrer", "text"),
                ("Notizen", "notes", "text")
            ]
            
            def wizard_callback(data):
                try:
                    print(f"[DEBUG] Bearbeitetes Fahrzeug: {data}")
                    self.setStatusMessage("Fahrzeug wird aktualisiert...")
                    
                    # Retry-Mechanismus für kritische DB-Operation
                    def update_vehicle():
                        return self._db_manager.update_fahrzeug_by_plate(license_plate, data)
                    
                    self._retry_operation(update_vehicle)
                    
                    self.setStatusMessage(f"Fahrzeug {license_plate} erfolgreich aktualisiert!")
                    print("Fahrzeug erfolgreich aktualisiert.")
                    logger.info(f"Fahrzeug {license_plate} erfolgreich aktualisiert")
                    
                except ValueError as e:
                    # User-friendly Fehlermeldung für Validierungsfehler
                    self.setStatusMessage(str(e))
                    self.errorOccurred.emit(str(e))
                    logger.warning(f"Validierungsfehler beim Aktualisieren des Fahrzeugs: {e}")
                except Exception as e:
                    self._handle_error("Fahrzeug aktualisieren", e)
                
                finally:
                    self.anzeigenFahrzeuge()
            
            wizard = GenericWizard(fields, callback=wizard_callback, title=f"Fahrzeug bearbeiten: {license_plate}")
            
            # Vorbelegung der Felder
            if hasattr(wizard, "inputs"):
                if "license_plate" in wizard.inputs:
                    wizard.inputs["license_plate"].setText(row[0] or "")
                if "rfrnc" in wizard.inputs:
                    wizard.inputs["rfrnc"].setText(row[1] or "")
                if "model" in wizard.inputs:
                    wizard.inputs["model"].setText(row[2] or "")
                if "year" in wizard.inputs:
                    wizard.inputs["year"].setText(str(row[3]) if row[3] else "")
                if "insurance" in wizard.inputs:
                    wizard.inputs["insurance"].setText(str(row[4]) if row[4] else "")
                if "credit" in wizard.inputs:
                    wizard.inputs["credit"].setText(str(row[5]) if row[5] else "")
                if "status" in wizard.inputs and len(row) > 6:
                    wizard.inputs["status"].setCurrentText(row[6] or "Aktiv")
                if "stammfahrer" in wizard.inputs and len(row) > 7:
                    wizard.inputs["stammfahrer"].setText(row[7] or "")
                if "notes" in wizard.inputs and len(row) > 8:
                    wizard.inputs["notes"].setText(row[8] or "")
            
            wizard.show()
            
        except ValueError as e:
            # User-friendly Fehlermeldung für Validierungsfehler
            self.setStatusMessage(str(e))
            self.errorOccurred.emit(str(e))
            logger.warning(f"Validierungsfehler beim Bearbeiten des Fahrzeugs: {e}")
        except Exception as e:
            self._handle_error("Fahrzeug-Wizard öffnen", e)

    @Slot(str)
    def deleteVehicle(self, license_plate):
        """Fahrzeug löschen"""
        try:
            print(f"Fahrzeug {license_plate} wird gelöscht...")
            self.setStatusMessage(f"Fahrzeug {license_plate} wird gelöscht...")
            
            # Retry-Mechanismus für kritische DB-Operation
            def delete_vehicle():
                return self._db_manager.delete_fahrzeug_by_plate(license_plate)
            
            self._retry_operation(delete_vehicle)
            
            self.setStatusMessage(f"Fahrzeug {license_plate} erfolgreich gelöscht!")
            print("Fahrzeug erfolgreich gelöscht.")
            logger.info(f"Fahrzeug {license_plate} erfolgreich gelöscht")
            
        except ValueError as e:
            # User-friendly Fehlermeldung für Validierungsfehler
            self.setStatusMessage(str(e))
            self.errorOccurred.emit(str(e))
            logger.warning(f"Validierungsfehler beim Löschen des Fahrzeugs: {e}")
        except Exception as e:
            self._handle_error("Fahrzeug löschen", e)
        
        finally:
            self.anzeigenFahrzeuge()

    @Slot(str)
    def selectVehicle(self, license_plate):
        """Fahrzeug auswählen für Details"""
        try:
            for fahrzeug in self._fahrzeug_list:
                if fahrzeug.get("kennzeichen") == license_plate:
                    self.setSelectedVehicle(fahrzeug)
                    self.setStatusMessage(f"Fahrzeug {license_plate} ausgewählt")
                    break
        except Exception as e:
            self._handle_error("Fahrzeug auswählen", e, show_user_message=False)

    @Slot()
    def refreshData(self):
        """Daten neu laden"""
        try:
            self.setStatusMessage("Daten werden neu geladen...")
            self.anzeigenFahrzeuge()
        except Exception as e:
            self._handle_error("Daten neu laden", e)

    @Slot(str, str)
    def updateVehicleStatus(self, license_plate, new_status):
        """Aktualisiert den Status eines Fahrzeugs"""
        try:
            print(f"Status-Update für {license_plate}: {new_status}")
            self.setStatusMessage(f"Status wird aktualisiert: {new_status}")
            
            # Retry-Mechanismus für kritische DB-Operation
            def update_status():
                return self._db_manager.update_fahrzeug_by_plate(license_plate, {"status": new_status})
            
            self._retry_operation(update_status)
            
            print(f"Status erfolgreich aktualisiert: {license_plate} → {new_status}")
            self.setStatusMessage(f"Status aktualisiert: {new_status}")
            logger.info(f"Status für Fahrzeug {license_plate} auf {new_status} aktualisiert")
            
        except ValueError as e:
            # User-friendly Fehlermeldung für Validierungsfehler
            self.setStatusMessage(str(e))
            self.errorOccurred.emit(str(e))
            logger.warning(f"Validierungsfehler beim Status-Update: {e}")
        except Exception as e:
            self._handle_error("Status aktualisieren", e)
        
        finally:
            # Daten neu laden
            self.anzeigenFahrzeuge()

    @Slot()
    def toggleViewMode(self):
        """Wechselt zwischen normaler Ansicht und Kalenderwochen-Ansicht"""
        self.setIsCalendarView(not self._is_calendar_view)
        if self._is_calendar_view:
            self.setStatusMessage("Kalenderwochen-Ansicht aktiviert")
            self.loadCalendarView()
        else:
            self.setStatusMessage("Normale Fahrzeugansicht aktiviert")
            self.anzeigenFahrzeuge()

    def loadCalendarView(self):
        """Lädt die Kalenderwochen-Daten für alle Fahrzeuge"""
        try:
            # Aktuelle Kalenderwoche ermitteln
            from datetime import datetime, timedelta
            current_date = datetime.now()
            current_week = current_date.isocalendar()[1]
            current_year = current_date.year
            
            # Alle Fahrzeuge laden
            conn = sqlite3.connect("SQL/database.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT license_plate, rfrnc, model, year, insurance, credit, 
                       COALESCE(status, 'Aktiv') as status, 
                       COALESCE(notes, '') as notes
                FROM vehicles
                ORDER BY license_plate
            """)
            vehicles = cursor.fetchall()
            
            # Revenue-Datenbank prüfen
            revenue_conn = sqlite3.connect("SQL/revenue.db")
            revenue_cursor = revenue_conn.cursor()
            
            self._fahrzeug_list = []
            
            for vehicle in vehicles:
                fahrzeug = {
                    "kennzeichen": vehicle[0] or "",
                    "rfrnc": vehicle[1] or "",
                    "modell": vehicle[2] or "",
                    "baujahr": str(vehicle[3]) if vehicle[3] else "",
                    "versicherung": vehicle[4] or "",
                    "finanzierung": vehicle[5] or "",
                    "status": vehicle[6] or "Aktiv",
                    "notizen": vehicle[7] or "",
                    "calendar_weeks": []
                }
                
                # Kalenderwochen für das aktuelle Jahr generieren (nur bis zur aktuellen Woche)
                weeks = []
                
                # Prüfen ob Fahrzeug-Tabellen in BEIDEN Datenbanken existieren
                try:
                    # Revenue-Datenbank prüfen
                    revenue_cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=?
                    """, (fahrzeug["kennzeichen"],))
                    revenue_table_exists = revenue_cursor.fetchone() is not None
                    
                    # Running-Costs-Datenbank prüfen
                    running_costs_conn = sqlite3.connect("SQL/running_costs.db")
                    running_costs_cursor = running_costs_conn.cursor()
                    running_costs_cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=?
                    """, (fahrzeug["kennzeichen"],))
                    running_costs_table_exists = running_costs_cursor.fetchone() is not None
                    
                    # Wochen mit Daten aus BEIDEN Datenbanken sammeln
                    weeks_with_data = set()
                    
                    # Revenue-Daten prüfen
                    if revenue_table_exists:
                        revenue_cursor.execute("""
                            SELECT cw FROM [{}] 
                            WHERE cw BETWEEN 1 AND ?
                        """.format(fahrzeug["kennzeichen"]), (current_week,))
                        revenue_weeks = {row[0] for row in revenue_cursor.fetchall()}
                        weeks_with_data.update(revenue_weeks)
                    
                    # Running-Costs-Daten prüfen
                    if running_costs_table_exists:
                        running_costs_cursor.execute("""
                            SELECT cw FROM [{}] 
                            WHERE cw BETWEEN 1 AND ?
                        """.format(fahrzeug["kennzeichen"]), (current_week,))
                        running_costs_weeks = {row[0] for row in running_costs_cursor.fetchall()}
                        weeks_with_data.update(running_costs_weeks)
                    
                    existing_weeks = weeks_with_data
                    
                    # Nur bei W135CTX ausgeben für Debug
                    if fahrzeug['kennzeichen'] == 'W135CTX':
                        print(f"Fahrzeug {fahrzeug['kennzeichen']}: {len(existing_weeks)} Wochen mit Daten gefunden")
                        print(f"  - Revenue Wochen: {revenue_weeks if revenue_table_exists else 'Keine Tabelle'}")
                        print(f"  - Running-Costs Wochen: {running_costs_weeks if running_costs_table_exists else 'Keine Tabelle'}")
                    
                    # Running-Costs-Verbindung schließen
                    running_costs_conn.close()
                        
                except Exception as e:
                    # Nur bei W135CTX ausgeben für Debug
                    if fahrzeug['kennzeichen'] == 'W135CTX':
                        print(f"Fehler bei Fahrzeug {fahrzeug['kennzeichen']}: {e}")
                    existing_weeks = set()
                
                # Wochen generieren
                for week in range(1, current_week + 1):
                    week_data = {
                        "week": week,
                        "year": current_year,
                        "has_data": week in existing_weeks,
                        "kennzeichen": fahrzeug["kennzeichen"]  # Kennzeichen hinzufügen
                    }
                    weeks.append(week_data)
                
                fahrzeug["calendar_weeks"] = weeks
                self._fahrzeug_list.append(fahrzeug)
            
            self.fahrzeugListChanged.emit()
            self.setStatusMessage(f"Kalenderwochen für {len(self._fahrzeug_list)} Fahrzeuge geladen")
            print(f"Kalenderwochen für {len(self._fahrzeug_list)} Fahrzeuge geladen")
            
        except Exception as e:
            error_msg = f"Fehler beim Laden der Kalenderwochen: {e}"
            self.setStatusMessage(error_msg)
            print(error_msg)
        finally:
            try:
                conn.close()
                revenue_conn.close()
            except:
                pass

    @Slot(str, int)
    def loadWeekDataForOverlay(self, license_plate, week):
        """Lädt Daten für eine Kalenderwoche und sendet sie an das QML-Overlay"""
        print(f"Lade Daten für {license_plate} KW {week}")
        self.setStatusMessage(f"Daten für KW {week} werden geladen...")
        
        try:
            # Daten aus revenue.db laden
            revenue_conn = sqlite3.connect("SQL/revenue.db")
            revenue_cursor = revenue_conn.cursor()
            
            # Prüfen ob Tabelle existiert
            revenue_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            table_exists = revenue_cursor.fetchone() is not None
            
            if table_exists:
                # Alle Daten für diese Woche laden
                revenue_cursor.execute("""
                    SELECT deal, driver, total, taxed, income, timestamp 
                    FROM [{}] 
                    WHERE cw = ?
                    ORDER BY timestamp
                """.format(license_plate), (week,))
                revenue_data = revenue_cursor.fetchall()
                
                # Daten formatieren
                formatted_revenue = []
                for row in revenue_data:
                    formatted_revenue.append({
                        "deal": row[0] or "N/A",
                        "driver": row[1] or "N/A",
                        "total": row[2] or 0,
                        "taxed": row[3] or 0,
                        "income": row[4] or 0,
                        "timestamp": row[5] or "N/A"
                    })
            else:
                formatted_revenue = []
            
            # Daten aus running_costs.db laden
            running_costs_conn = sqlite3.connect("SQL/running_costs.db")
            running_costs_cursor = running_costs_conn.cursor()
            
            # Prüfen ob Tabelle existiert
            running_costs_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            table_exists = running_costs_cursor.fetchone() is not None
            
            if table_exists:
                # Alle Daten für diese Woche laden
                running_costs_cursor.execute("""
                    SELECT category, amount, details, timestamp 
                    FROM [{}] 
                    WHERE cw = ?
                    ORDER BY timestamp
                """.format(license_plate), (week,))
                running_costs_data = running_costs_cursor.fetchall()
                
                # Daten formatieren
                formatted_running_costs = []
                for row in running_costs_data:
                    formatted_running_costs.append({
                        "category": row[0] or "N/A",
                        "amount": row[1] or 0,
                        "details": row[2] or "",
                        "timestamp": row[3] or "N/A"
                    })
            else:
                formatted_running_costs = []
            
            # Debug-Ausgabe für Datenstruktur
            print(f"Revenue-Daten für {license_plate} KW {week}: {formatted_revenue}")
            print(f"Running-Costs-Daten für {license_plate} KW {week}: {formatted_running_costs}")
            
            # Signal an QML senden
            self.weekDataLoaded.emit(license_plate, week, formatted_revenue, formatted_running_costs)
            self.setStatusMessage(f"Daten für KW {week} geladen")
            
        except Exception as e:
            error_msg = f"Fehler beim Laden der Daten: {e}"
            self.setStatusMessage(error_msg)
            print(error_msg)
        finally:
            try:
                revenue_conn.close()
                running_costs_conn.close()
            except:
                pass

    @Slot(str, int)
    def showWeekDataOverlay(self, license_plate, week):
        """Zeigt vorhandene Daten für eine Kalenderwoche in einem Overlay an"""
        print(f"Zeige Daten für {license_plate} KW {week}")
        self.setStatusMessage(f"Daten für KW {week} werden geladen...")
        
        try:
            # Daten aus BEIDEN Datenbanken laden
            revenue_data = []
            running_costs_data = []
            
            # Revenue-Datenbank prüfen
            revenue_conn = sqlite3.connect("SQL/revenue.db")
            revenue_cursor = revenue_conn.cursor()
            revenue_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            revenue_table_exists = revenue_cursor.fetchone() is not None
            
            if revenue_table_exists:
                revenue_cursor.execute("""
                    SELECT * FROM [{}] 
                    WHERE cw = ?
                """.format(license_plate), (week,))
                revenue_data = revenue_cursor.fetchall()
            
            # Running-Costs-Datenbank prüfen
            running_costs_conn = sqlite3.connect("SQL/running_costs.db")
            running_costs_cursor = running_costs_conn.cursor()
            running_costs_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            running_costs_table_exists = running_costs_cursor.fetchone() is not None
            
            if running_costs_table_exists:
                running_costs_cursor.execute("""
                    SELECT * FROM [{}] 
                    WHERE cw = ?
                """.format(license_plate), (week,))
                running_costs_data = running_costs_cursor.fetchall()
            
            # Overlay mit Daten aus beiden Datenbanken anzeigen
            if revenue_data or running_costs_data:
                self.showWeekDataDialog(license_plate, week, revenue_data, running_costs_data)
            else:
                self.setStatusMessage(f"Keine Daten für KW {week} gefunden")
                
        except Exception as e:
            error_msg = f"Fehler beim Laden der Wochen-Daten: {e}"
            self.setStatusMessage(error_msg)
            print(error_msg)
        finally:
            try:
                revenue_conn.close()
                running_costs_conn.close()
            except:
                pass

    @Slot(str, int)
    def createWeekDataEntry(self, license_plate, week):
        """Erstellt einen neuen Eintrag für eine Kalenderwoche"""
        print(f"Erstelle neuen Eintrag für {license_plate} KW {week}")
        self.setStatusMessage(f"Neuer Eintrag für KW {week} wird erstellt...")
        
        try:
            # Wizard für neuen Eintrag öffnen
            fields = [
                ("Datum", "date", "text"),
                ("Umsatz (€)", "revenue", "text"),
                ("Kilometer", "kilometers", "text"),
                ("Bemerkungen", "notes", "text")
            ]
            
            def wizard_callback(data):
                print(f"[DEBUG] Neuer Wochen-Eintrag: {data}")
                self.setStatusMessage("Eintrag wird gespeichert...")
                
                # Validierung
                if not data.get("date"):
                    raise ValueError("Datum ist erforderlich!")
                
                if not data.get("revenue"):
                    raise ValueError("Umsatz ist erforderlich!")
                
                # Daten bereinigen
                cleaned_data = {}
                for key, value in data.items():
                    if value is not None and str(value).strip():
                        cleaned_data[key] = str(value).strip()
                    else:
                        cleaned_data[key] = ""
                
                # In revenue.db speichern
                try:
                    revenue_conn = sqlite3.connect("SQL/revenue.db")
                    revenue_cursor = revenue_conn.cursor()
                    
                    # Prüfen ob Tabelle existiert, sonst erstellen
                    revenue_cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=?
                    """, (license_plate,))
                    table_exists = revenue_cursor.fetchone() is not None
                    
                    if not table_exists:
                        # Tabelle erstellen
                        revenue_cursor.execute("""
                            CREATE TABLE [{}] (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                cw INTEGER,
                                date TEXT,
                                revenue REAL,
                                kilometers INTEGER,
                                notes TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """.format(license_plate))
                    
                    # Eintrag einfügen
                    revenue_cursor.execute("""
                        INSERT INTO [{}] (cw, date, revenue, kilometers, notes)
                        VALUES (?, ?, ?, ?, ?)
                    """.format(license_plate), (
                        week,
                        cleaned_data.get("date", ""),
                        float(cleaned_data.get("revenue", 0)),
                        int(cleaned_data.get("kilometers", 0)),
                        cleaned_data.get("notes", "")
                    ))
                    
                    revenue_conn.commit()
                    self.setStatusMessage(f"Eintrag für KW {week} erfolgreich gespeichert!")
                    print("Wochen-Eintrag erfolgreich gespeichert.")
                    
                    # Kalenderwochen-Ansicht neu laden
                    if self._is_calendar_view:
                        self.loadCalendarView()
                    
                except Exception as e:
                    error_msg = f"Fehler beim Speichern des Eintrags: {e}"
                    self.setStatusMessage(error_msg)
                    print(error_msg)
                finally:
                    try:
                        revenue_conn.close()
                    except:
                        pass
            
            wizard = GenericWizard(fields, callback=wizard_callback, title=f"Neuer Eintrag: {license_plate} KW {week}")
            wizard.show()
            
        except ValueError as e:
            # User-friendly Fehlermeldung für Validierungsfehler
            self.setStatusMessage(str(e))
            self.errorOccurred.emit(str(e))
            logger.warning(f"Validierungsfehler beim Erstellen des Wochen-Eintrags: {e}")
        except Exception as e:
            error_msg = f"Fehler beim Erstellen des Eintrags: {e}"
            self.setStatusMessage(error_msg)
            print(error_msg)

    def showWeekDataDialog(self, license_plate, week, revenue_data, running_costs_data):
        """Zeigt ein Dialog mit den Wochen-Daten aus beiden Datenbanken an"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QScrollArea, QWidget, QTabWidget
            from PySide6.QtCore import Qt
            
            dialog = QDialog()
            dialog.setWindowTitle(f"KW {week} - {license_plate}")
            dialog.setMinimumSize(800, 600)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1a1a1a;
                    color: white;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #333333;
                    border: 1px solid #555555;
                    padding: 8px 16px;
                    color: white;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #ff8c00;
                }
                QTextEdit {
                    background-color: #2a2a2a;
                    border: 1px solid #555555;
                    color: white;
                    padding: 8px;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #2a2a2a;
                }
                QTabBar::tab {
                    background-color: #333333;
                    color: white;
                    padding: 8px 16px;
                    border: 1px solid #555555;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background-color: #ff8c00;
                }
            """)
            
            layout = QVBoxLayout()
            
            # Header
            header_layout = QHBoxLayout()
            title_label = QLabel(f"Kalenderwoche {week} - {license_plate}")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff8c00;")
            header_layout.addWidget(title_label)
            
            close_button = QPushButton("Schließen")
            close_button.clicked.connect(dialog.close)
            header_layout.addWidget(close_button)
            layout.addLayout(header_layout)
            
            # Tab-Widget für beide Datenbanken
            tab_widget = QTabWidget()
            
            # Revenue-Tab
            if revenue_data:
                revenue_tab = QWidget()
                revenue_layout = QVBoxLayout()
                
                revenue_header = QLabel("📈 Revenue-Daten")
                revenue_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin: 10px;")
                revenue_layout.addWidget(revenue_header)
                
                revenue_scroll = QScrollArea()
                revenue_widget = QWidget()
                revenue_scroll_layout = QVBoxLayout()
                
                for i, row in enumerate(revenue_data):
                    # Revenue-Schema: (id, cw, date, revenue, kilometers, notes, created_at)
                    if len(row) >= 6:
                        entry_layout = QHBoxLayout()
                        
                        # Datum
                        date_label = QLabel(f"Datum: {row[2] if row[2] else 'N/A'}")
                        entry_layout.addWidget(date_label)
                        
                        # Umsatz
                        revenue_label = QLabel(f"Umsatz: {row[3] if row[3] else 0} €")
                        revenue_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                        entry_layout.addWidget(revenue_label)
                        
                        # Kilometer
                        km_label = QLabel(f"KM: {row[4] if row[4] else 0}")
                        entry_layout.addWidget(km_label)
                        
                        revenue_scroll_layout.addLayout(entry_layout)
                        
                        # Notizen (falls vorhanden)
                        if row[5] and row[5].strip():
                            notes_label = QLabel(f"Notizen: {row[5]}")
                            notes_label.setStyleSheet("color: #cccccc; font-style: italic;")
                            revenue_scroll_layout.addWidget(notes_label)
                        
                        # Separator
                        if i < len(revenue_data) - 1:
                            separator = QLabel("─" * 50)
                            separator.setStyleSheet("color: #555555;")
                            revenue_scroll_layout.addWidget(separator)
                
                revenue_widget.setLayout(revenue_scroll_layout)
                revenue_scroll.setWidget(revenue_widget)
                revenue_scroll.setWidgetResizable(True)
                revenue_layout.addWidget(revenue_scroll)
                revenue_tab.setLayout(revenue_layout)
                tab_widget.addTab(revenue_tab, "Revenue")
            
            # Running-Costs-Tab
            if running_costs_data:
                running_costs_tab = QWidget()
                running_costs_layout = QVBoxLayout()
                
                running_costs_header = QLabel("💰 Running-Costs-Daten")
                running_costs_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF9800; margin: 10px;")
                running_costs_layout.addWidget(running_costs_header)
                
                running_costs_scroll = QScrollArea()
                running_costs_widget = QWidget()
                running_costs_scroll_layout = QVBoxLayout()
                
                for i, row in enumerate(running_costs_data):
                    # Running-Costs-Schema: (id, cw, amount, category, details, timestamp)
                    if len(row) >= 5:
                        entry_layout = QHBoxLayout()
                        
                        # Kategorie
                        category_label = QLabel(f"Kategorie: {row[3] if row[3] else 'N/A'}")
                        entry_layout.addWidget(category_label)
                        
                        # Betrag
                        amount_label = QLabel(f"Betrag: {row[2] if row[2] else 0} €")
                        amount_label.setStyleSheet("color: #FF9800; font-weight: bold;")
                        entry_layout.addWidget(amount_label)
                        
                        # Details
                        details_label = QLabel(f"Details: {row[4] if row[4] else 'N/A'}")
                        entry_layout.addWidget(details_label)
                        
                        running_costs_scroll_layout.addLayout(entry_layout)
                        
                        # Separator
                        if i < len(running_costs_data) - 1:
                            separator = QLabel("─" * 50)
                            separator.setStyleSheet("color: #555555;")
                            running_costs_scroll_layout.addWidget(separator)
                
                running_costs_widget.setLayout(running_costs_scroll_layout)
                running_costs_scroll.setWidget(running_costs_widget)
                running_costs_scroll.setWidgetResizable(True)
                running_costs_layout.addWidget(running_costs_scroll)
                running_costs_tab.setLayout(running_costs_layout)
                tab_widget.addTab(running_costs_tab, "Running-Costs")
            
            # Keine Daten
            if not revenue_data and not running_costs_data:
                no_data_label = QLabel("Keine Daten für diese Kalenderwoche gefunden.")
                no_data_label.setStyleSheet("font-size: 16px; color: #cccccc; text-align: center; margin: 20px;")
                layout.addWidget(no_data_label)
            else:
                layout.addWidget(tab_widget)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            error_msg = f"Fehler beim Anzeigen der Wochen-Daten: {e}"
            self.setStatusMessage(error_msg)
            print(error_msg)

    @Slot(str, int, 'QVariant')
    def deleteRevenueEntry(self, license_plate, week, entry_data):
        """Löscht einen Revenue-Eintrag aus der Datenbank"""
        try:
            print(f"Lösche Revenue-Eintrag für {license_plate} KW {week}: {entry_data}")
            self.setStatusMessage(f"Revenue-Eintrag wird gelöscht...")
            
            # QJSValue zu Dictionary konvertieren
            if hasattr(entry_data, 'toVariant'):
                entry_data = entry_data.toVariant()
            
            # Verbindung zur revenue.db
            conn = sqlite3.connect("SQL/revenue.db")
            cursor = conn.cursor()
            
            # Prüfen ob Tabelle existiert
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Eintrag basierend auf den Daten löschen
                cursor.execute("""
                    DELETE FROM [{}] 
                    WHERE cw = ? AND deal = ? AND driver = ? AND total = ? AND income = ?
                """.format(license_plate), (
                    week,
                    entry_data.get('deal', ''),
                    entry_data.get('driver', ''),
                    entry_data.get('total', 0),
                    entry_data.get('income', 0)
                ))
                
                conn.commit()
                deleted_rows = cursor.rowcount
                
                if deleted_rows > 0:
                    self.setStatusMessage(f"Revenue-Eintrag erfolgreich gelöscht")
                    print(f"Revenue-Eintrag gelöscht: {deleted_rows} Zeilen betroffen")
                    
                    # Prüfen ob Running-Costs-Einträge für diese Woche existieren
                    running_costs_conn = sqlite3.connect("SQL/running_costs.db")
                    running_costs_cursor = running_costs_conn.cursor()
                    
                    # Prüfen ob Running-Costs-Tabelle existiert
                    running_costs_cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=?
                    """, (license_plate,))
                    running_costs_table_exists = running_costs_cursor.fetchone() is not None
                    
                    if running_costs_table_exists:
                        # Anzahl der Running-Costs-Einträge für diese Woche prüfen
                        running_costs_cursor.execute("""
                            SELECT COUNT(*) FROM [{}] WHERE cw = ?
                        """.format(license_plate), (week,))
                        running_costs_count = running_costs_cursor.fetchone()[0]
                        
                        if running_costs_count > 0:
                            # Signal an QML senden für Bestätigungsdialog
                            self.askDeleteRunningCosts.emit(license_plate, week, running_costs_count)
                        else:
                            # Keine Running-Costs-Einträge, direkt Daten neu laden
                            self.loadWeekDataForOverlay(license_plate, week)
                    else:
                        # Keine Running-Costs-Tabelle, direkt Daten neu laden
                        self.loadWeekDataForOverlay(license_plate, week)
                    
                    try:
                        running_costs_conn.close()
                    except:
                        pass
                else:
                    self.setStatusMessage(f"Revenue-Eintrag nicht gefunden")
                    print("Revenue-Eintrag nicht gefunden")
            else:
                self.setStatusMessage(f"Keine Revenue-Tabelle für {license_plate} gefunden")
                print(f"Keine Revenue-Tabelle für {license_plate} gefunden")
                
        except Exception as e:
            error_msg = f"Fehler beim Löschen des Revenue-Eintrags: {e}"
            self.setStatusMessage(error_msg)
            print(error_msg)
        finally:
            try:
                conn.close()
            except:
                pass

    @Slot(str, int, 'QVariant')
    def deleteRunningCostsEntry(self, license_plate, week, entry_data):
        """Löscht einen Running-Costs-Eintrag aus der Datenbank"""
        try:
            print(f"Lösche Running-Costs-Eintrag für {license_plate} KW {week}: {entry_data}")
            self.setStatusMessage(f"Running-Costs-Eintrag wird gelöscht...")
            
            # QJSValue zu Dictionary konvertieren
            if hasattr(entry_data, 'toVariant'):
                entry_data = entry_data.toVariant()
            
            # Verbindung zur running_costs.db
            conn = sqlite3.connect("SQL/running_costs.db")
            cursor = conn.cursor()
            
            # Prüfen ob Tabelle existiert
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Eintrag basierend auf den Daten löschen
                cursor.execute("""
                    DELETE FROM [{}] 
                    WHERE cw = ? AND category = ? AND amount = ? AND details = ?
                """.format(license_plate), (
                    week,
                    entry_data.get('category', ''),
                    entry_data.get('amount', 0),
                    entry_data.get('details', '')
                ))
                
                conn.commit()
                deleted_rows = cursor.rowcount
                
                if deleted_rows > 0:
                    self.setStatusMessage(f"Running-Costs-Eintrag erfolgreich gelöscht")
                    print(f"Running-Costs-Eintrag gelöscht: {deleted_rows} Zeilen betroffen")
                    
                    # Daten neu laden und Overlay aktualisieren
                    self.loadWeekDataForOverlay(license_plate, week)
                else:
                    self.setStatusMessage(f"Running-Costs-Eintrag nicht gefunden")
                    print("Running-Costs-Eintrag nicht gefunden")
            else:
                self.setStatusMessage(f"Keine Running-Costs-Tabelle für {license_plate} gefunden")
                print(f"Keine Running-Costs-Tabelle für {license_plate} gefunden")
                
        except Exception as e:
            error_msg = f"Fehler beim Löschen des Running-Costs-Eintrags: {e}"
            self.setStatusMessage(error_msg)
            print(error_msg)
        finally:
            try:
                conn.close()
            except:
                pass

    @Slot(str, int)
    def deleteRunningCostsForWeek(self, license_plate, week):
        """Löscht alle Running-Costs-Einträge für eine Kalenderwoche"""
        try:
            print(f"Lösche alle Running-Costs-Einträge für {license_plate} KW {week}")
            self.setStatusMessage(f"Running-Costs-Einträge werden gelöscht...")
            
            # Verbindung zur running_costs.db
            conn = sqlite3.connect("SQL/running_costs.db")
            cursor = conn.cursor()
            
            # Prüfen ob Tabelle existiert
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Alle Einträge für diese Woche löschen
                cursor.execute("""
                    DELETE FROM [{}] WHERE cw = ?
                """.format(license_plate), (week,))
                
                conn.commit()
                deleted_rows = cursor.rowcount
                
                if deleted_rows > 0:
                    self.setStatusMessage(f"{deleted_rows} Running-Costs-Einträge erfolgreich gelöscht")
                    print(f"Running-Costs-Einträge gelöscht: {deleted_rows} Zeilen betroffen")
                else:
                    self.setStatusMessage(f"Keine Running-Costs-Einträge für KW {week} gefunden")
                    print("Keine Running-Costs-Einträge gefunden")
            else:
                self.setStatusMessage(f"Keine Running-Costs-Tabelle für {license_plate} gefunden")
                print(f"Keine Running-Costs-Tabelle für {license_plate} gefunden")
            
            # Daten neu laden und Overlay aktualisieren
            self.loadWeekDataForOverlay(license_plate, week)
                
        except Exception as e:
            error_msg = f"Fehler beim Löschen der Running-Costs-Einträge: {e}"
            self.setStatusMessage(error_msg)
            print(error_msg)
        finally:
            try:
                conn.close()
            except:
                pass 

    def __del__(self):
        """Cleanup beim Zerstören des Objekts"""
        try:
            if self._search_timer:
                self._search_timer.cancel()
            self._all_vehicles_cache.clear()
            logger.info("FahrzeugSeiteQMLV2 Cleanup abgeschlossen")
        except Exception as e:
            logger.warning(f"Fehler beim Cleanup: {e}") 