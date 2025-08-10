from PySide6.QtCore import QObject, Slot, Signal, Property, QTimer
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

class MitarbeiterSeiteQMLV2(QObject):
    mitarbeiterListChanged = Signal()
    filterTextChanged = Signal()
    showOnlyActiveChanged = Signal()
    selectedEmployeeChanged = Signal()
    statusMessageChanged = Signal()
    toggleViewChanged = Signal()
    errorOccurred = Signal(str)  # Neues Signal für Fehlerbehandlung
    validationErrorOccurred = Signal(list, str)  # Signal für Validierungsfehler (Fehlerliste, Operation)
    loadingChanged = Signal()  # Signal für Loading-States
    loadingMessageChanged = Signal()  # Signal für Loading-Nachrichten
    loadingProgressChanged = Signal()  # Signal für Loading-Fortschritt
    savingChanged = Signal()  # Signal für Speichern-Status
    searchingChanged = Signal()  # Signal für Such-Status
    deleteConfirmationRequested = Signal(dict)  # Signal für Delete-Bestätigungsdialog
    duplicateCheckRequested = Signal(dict)  # Signal für Duplikat-Prüfung
    editEmployeeInForm = Signal(int)  # Signal für Edit im Formular
    
    # UI/UX-Verbesserungen (Task 4.7) - Konsolidiert
    toastNotificationRequested = Signal(str, str, int)  # message, type, duration
    loadingStateChanged = Signal(str, bool, str)  # operation, is_active, message
    confirmationDialogRequested = Signal(str, str, str, str, str, str)  # title, message, confirm_text, cancel_text, dialog_type, callback_id

    def __init__(self):
        super().__init__()
        self._mitarbeiter_list = []
        self._filter_text = ""
        self._show_only_active = True
        self._selected_employee = None
        self._status_message = ""
        self._toggle_view = False
        self._db_manager = DBManager()
        self._retry_count = 0
        self._max_retries = 3
        
        # Performance-Optimierungen
        self._page_size = 50  # Anzahl Mitarbeiter pro Seite
        self._current_page = 0
        self._total_employees = 0
        self._all_employees_cache = []  # Cache für gefilterte Daten
        self._is_loading = False
        self._loading_message = ""
        self._loading_progress = 0
        self._loading_operation = ""
        self._is_saving = False
        self._is_searching = False
        
        # Debounced Search
        self._search_timer = None
        self._search_delay = 300  # 300ms Verzögerung
        
        # Memory-Monitoring (deaktiviert für Thread-Kompatibilität)
        self._memory_monitor_timer = None
        self._last_memory_cleanup = time.time()
        self._memory_cleanup_interval = 300  # 5 Minuten
        
        # Memory Management
        self._cache_size_limit = 1000  # Maximale Cache-Größe
        self._cache_timestamp = time.time()
        self._cache_ttl = 300  # 5 Minuten Cache-TTL
        
        # Deals-Cache für N+1 Query Problem
        self._deals_cache = {}
        self._deals_cache_timestamp = time.time()
        self._deals_cache_ttl = 600  # 10 Minuten
        
        # Erweiterte Performance-Optimierungen (Task 4.3)
        self._query_cache = {}  # Cache für SQL-Queries
        self._query_cache_ttl = 180  # 3 Minuten Query-Cache-TTL
        self._query_cache_timestamp = time.time()
        
        # Lazy Loading für große Datensätze
        self._lazy_loading_enabled = True
        self._lazy_loading_threshold = 100  # Anzahl Einträge für Lazy Loading
        
        # Connection Pool für Datenbankverbindungen
        self._connection_pool = {}
        self._max_connections = 5
        self._connection_timeout = 30
        
        # Performance-Monitoring
        self._performance_stats = {
            'queries_executed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_query_time': 0.0,
            'memory_usage': 0.0
        }
        self._query_times = []
        
        # Background Processing
        self._background_tasks = []
        self._background_thread_pool = None
        
        # Erweiterte Suchfunktionen (Task 4.4)
        self._advanced_search_enabled = True
        self._search_filters = {
            'name': True,
            'email': True,
            'phone': True,
            'driver_id': True,
            'status': True,
            'hire_date': True,
            'deal': True
        }
        self._search_options = {
            'case_sensitive': False,
            'fuzzy_search': True,
            'partial_match': True,
            'regex_search': False,
            'search_history': [],
            'max_history': 10
        }
        self._search_results_cache = {}
        self._search_suggestions = []
        self._search_highlighting = True
        
        # UI/UX-Verbesserungen (Task 4.7)
        self._ui_features = {
            'toast_notifications': True,
            'loading_animations': True,
            'keyboard_shortcuts': True,
            'confirmation_dialogs': True,
            'auto_save': False,
            'dark_mode': True
        }
        self._toast_queue = []
        self._loading_states = {}
        self._keyboard_shortcuts = {}
        self._confirmation_callbacks = {}
        
        # Logger einrichten
        self._setup_logging()
        
        # Daten beim Initialisieren laden
        self.anzeigenMitarbeiter()

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
        """Führt die erweiterte Suche aus"""
        try:
            # Loading-State für Suche setzen
            self._is_searching = True
            self._loading_message = f"Erweiterte Suche läuft... '{search_text}'"
            self._loading_progress = 0
            self._loading_operation = "advanced_search"
            self.searchingChanged.emit()
            self.loadingMessageChanged.emit()
            self.loadingProgressChanged.emit()
            self.loadingChanged.emit()
            
            self._filter_text = search_text
            self.filterTextChanged.emit()
            
            # Suchhistorie aktualisieren
            self._update_search_history(search_text)
            
            # Progress simulieren
            self._loading_progress = 25
            self.loadingProgressChanged.emit()
            
            # Erweiterte Suche ausführen
            search_results = self._advanced_search_employees(search_text)
            
            # Progress simulieren
            self._loading_progress = 75
            self.loadingProgressChanged.emit()
            
            # Ergebnisse formatieren und cachen
            self._mitarbeiter_list = self._format_search_results(search_results, search_text)
            self._search_results_cache[search_text] = self._mitarbeiter_list
            
            # Progress abschließen
            self._loading_progress = 100
            self.loadingProgressChanged.emit()
            
            # Loading-State zurücksetzen
            self._is_searching = False
            self._loading_message = ""
            self._loading_progress = 0
            self._loading_operation = ""
            self.searchingChanged.emit()
            self.loadingMessageChanged.emit()
            self.loadingProgressChanged.emit()
            self.loadingChanged.emit()
            
            self.mitarbeiterListChanged.emit()
            self.setStatusMessage(f"Erweiterte Suche abgeschlossen: {len(self._mitarbeiter_list)} Ergebnisse")
            
        except Exception as e:
            # Loading-State zurücksetzen bei Fehler
            self._is_searching = False
            self._loading_message = ""
            self._loading_progress = 0
            self._loading_operation = ""
            self.searchingChanged.emit()
            self.loadingMessageChanged.emit()
            self.loadingProgressChanged.emit()
            self.loadingChanged.emit()
            self._handle_error("Erweiterte Suche ausführen", e)

    def _advanced_search_employees(self, search_text: str) -> List[Dict]:
        """Erweiterte Suche mit verschiedenen Suchoptionen"""
        try:
            if not search_text.strip():
                return self._load_employees_paginated(0, force_reload=True)
            
            # SQL-basierte Suche für bessere Performance
            query = """
                SELECT d.driver_id, d.driver_license_number, d.first_name, d.last_name, 
                       d.phone, d.email, d.hire_date, d.status,
                       dl.deal, dl.pauschale, dl.umsatzgrenze, dl.garage
                FROM drivers d
                LEFT JOIN deals dl ON dl.name = d.first_name || ' ' || d.last_name
                WHERE 1=0
            """
            params = []
            
            # Dynamische WHERE-Bedingungen basierend auf aktivierten Filtern
            if self._search_filters['name']:
                query += " OR (LOWER(d.first_name) LIKE ? OR LOWER(d.last_name) LIKE ?)"
                search_pattern = f"%{search_text.lower()}%"
                params.extend([search_pattern, search_pattern])
            
            if self._search_filters['email']:
                query += " OR LOWER(d.email) LIKE ?"
                params.append(f"%{search_text.lower()}%")
            
            if self._search_filters['phone']:
                query += " OR d.phone LIKE ?"
                params.append(f"%{search_text}%")
            
            if self._search_filters['driver_id']:
                if search_text.isdigit():
                    query += " OR d.driver_id = ?"
                    params.append(int(search_text))
            
            if self._search_filters['status']:
                query += " OR LOWER(d.status) LIKE ?"
                params.append(f"%{search_text.lower()}%")
            
            if self._search_filters['hire_date']:
                query += " OR d.hire_date LIKE ?"
                params.append(f"%{search_text}%")
            
            if self._search_filters['deal']:
                query += " OR dl.deal LIKE ?"
                params.append(f"%{search_text}%")
            
            # Status-Filter anwenden
            if self._show_only_active:
                query += " AND d.status = 'active'"
            
            query += " ORDER BY d.last_name, d.first_name"
            
            # Query ausführen
            result = self._execute_query_with_cache(
                query, 
                tuple(params),
                cache_key=f"advanced_search_{hash(search_text)}_{self._show_only_active}"
            )
            
            # Ergebnisse formatieren
            employees = []
            
            for row in result:
                employee = {
                    "driver_id": row[0],
                    "driver_license_number": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "phone": row[4] or "",
                    "email": row[5] or "",
                    "hire_date": row[6] or "",
                    "status": row[7] or "active",
                    "deal": row[8] or "-",
                    "pauschale": f"{row[9]:.2f} €" if row[9] is not None else "-",
                    "umsatzgrenze": f"{row[10]:.2f} €" if row[10] is not None else "-",
                    "garage": f"{row[11]:.2f} €" if row[11] is not None else "-"
                }
                employees.append(employee)
            
            return employees
            
        except Exception as e:
            logger.error(f"Fehler bei erweiterter Suche: {e}")
            return []

    def _format_search_results(self, results: List[Dict], search_text: str) -> List[Dict]:
        """Formatiert Suchergebnisse mit Highlighting"""
        if not self._search_highlighting or not search_text:
            return results
        
        formatted_results = []
        for employee in results:
            formatted_employee = employee.copy()
            
            # Highlighting für verschiedene Felder
            for field in ['first_name', 'last_name', 'email', 'phone', 'deal']:
                if field in formatted_employee and formatted_employee[field]:
                    original_value = str(formatted_employee[field])
                    highlighted_value = self._highlight_search_term(original_value, search_text)
                    if highlighted_value != original_value:
                        formatted_employee[f"{field}_highlighted"] = highlighted_value
            
            formatted_results.append(formatted_employee)
        
        return formatted_results

    def _highlight_search_term(self, text: str, search_term: str) -> str:
        """Markiert Suchbegriffe in Text"""
        if not search_term or not text:
            return text
        
        try:
            import re
            # Case-insensitive Suche
            pattern = re.compile(re.escape(search_term), re.IGNORECASE)
            highlighted = pattern.sub(f"<b>{search_term}</b>", text)
            return highlighted
        except Exception as e:
            logger.warning(f"Fehler beim Highlighting: {e}")
            return text

    def _update_search_history(self, search_text: str):
        """Aktualisiert die Suchhistorie"""
        if not search_text.strip():
            return
        
        # Duplikate entfernen
        if search_text in self._search_options['search_history']:
            self._search_options['search_history'].remove(search_text)
        
        # An den Anfang einfügen
        self._search_options['search_history'].insert(0, search_text)
        
        # Größe begrenzen
        if len(self._search_options['search_history']) > self._search_options['max_history']:
            self._search_options['search_history'] = self._search_options['search_history'][:self._search_options['max_history']]

    def _generate_search_suggestions(self, partial_text: str) -> List[str]:
        """Generiert Suchvorschläge basierend auf partieller Eingabe"""
        if not partial_text or len(partial_text) < 2:
            return []
        
        try:
            suggestions = []
            
            # Vorschläge aus Suchhistorie
            for history_item in self._search_options['search_history']:
                if partial_text.lower() in history_item.lower():
                    suggestions.append(history_item)
            
            # Vorschläge aus Datenbank
            query = """
                SELECT DISTINCT 
                    first_name, last_name, email, phone, status
                FROM drivers
                WHERE LOWER(first_name) LIKE ? 
                   OR LOWER(last_name) LIKE ? 
                   OR LOWER(email) LIKE ? 
                   OR phone LIKE ?
                LIMIT 10
            """
            search_pattern = f"%{partial_text.lower()}%"
            params = [search_pattern, search_pattern, search_pattern, search_pattern]
            
            result = self._execute_query_with_cache(
                query, 
                tuple(params),
                cache_key=f"suggestions_{hash(partial_text)}"
            )
            
            for row in result:
                for field in row:
                    if field and partial_text.lower() in str(field).lower():
                        suggestions.append(str(field))
            
            # Duplikate entfernen und begrenzen
            unique_suggestions = list(dict.fromkeys(suggestions))
            return unique_suggestions[:10]
            
        except Exception as e:
            logger.error(f"Fehler beim Generieren von Suchvorschlägen: {e}")
            return []

    @Slot(str, result='QVariantList')
    def get_search_suggestions(self, partial_text: str) -> List[str]:
        """Gibt Suchvorschläge für QML zurück"""
        return self._generate_search_suggestions(partial_text)

    @Slot(result='QVariantList')
    def get_search_history(self) -> List[str]:
        """Gibt Suchhistorie für QML zurück"""
        return self._search_options['search_history']

    @Slot(str, bool)
    def set_search_filter(self, filter_name: str, enabled: bool):
        """Aktiviert/Deaktiviert Suchfilter"""
        if filter_name in self._search_filters:
            self._search_filters[filter_name] = enabled
            logger.info(f"Suchfilter '{filter_name}' auf {enabled} gesetzt")

    @Slot(str, bool)
    def set_search_option(self, option_name: str, enabled: bool):
        """Setzt Suchoptionen"""
        if option_name in self._search_options:
            self._search_options[option_name] = enabled
            logger.info(f"Suchoption '{option_name}' auf {enabled} gesetzt")

    @Slot(result='QVariant')
    def get_search_filters(self) -> Dict[str, bool]:
        """Gibt aktuelle Suchfilter zurück"""
        return self._search_filters

    @Slot(result='QVariant')
    def get_search_options(self) -> Dict[str, any]:
        """Gibt aktuelle Suchoptionen zurück"""
        return self._search_options

    @Slot()
    def clear_search_history(self):
        """Leert die Suchhistorie"""
        self._search_options['search_history'].clear()
        logger.info("Suchhistorie geleert")

    @Slot(str)
    def fuzzy_search(self, search_text: str):
        """Fuzzy-Suche mit Toleranz"""
        if not self._search_options['fuzzy_search']:
            return
        
        try:
            import difflib
            
            # Alle Mitarbeiter laden für Fuzzy-Suche
            all_employees = self._load_employees_paginated(0, force_reload=True)
            fuzzy_results = []
            
            for employee in all_employees:
                searchable_fields = [
                    str(employee.get('first_name', '')),
                    str(employee.get('last_name', '')),
                    str(employee.get('email', '')),
                    str(employee.get('phone', '')),
                    str(employee.get('status', ''))
                ]
                
                for field in searchable_fields:
                    if field:
                        similarity = difflib.SequenceMatcher(None, search_text.lower(), field.lower()).ratio()
                        if similarity >= 0.6:  # 60% Ähnlichkeit
                            employee['similarity'] = similarity
                            fuzzy_results.append(employee)
                            break
            
            # Nach Ähnlichkeit sortieren
            fuzzy_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            # Ergebnisse setzen
            self._mitarbeiter_list = fuzzy_results[:50]  # Top 50 Ergebnisse
            self.mitarbeiterListChanged.emit()
            self.setStatusMessage(f"Fuzzy-Suche: {len(fuzzy_results)} ähnliche Ergebnisse")
            
        except Exception as e:
            logger.error(f"Fehler bei Fuzzy-Suche: {e}")
            self._handle_error("Fuzzy-Suche", e)

    # UI/UX-Verbesserungen (Task 4.7)
    @Slot(str, str, int)
    def show_toast_notification(self, message: str, notification_type: str = "info", duration: int = 3000):
        """Zeigt eine Toast-Benachrichtigung an"""
        if not self._ui_features['toast_notifications']:
            return
        
        try:
            # Toast zur Queue hinzufügen
            toast_data = {
                'message': message,
                'type': notification_type,
                'duration': duration,
                'timestamp': time.time()
            }
            self._toast_queue.append(toast_data)
            
            # Toast-Signal senden
            self.toastNotificationRequested.emit(message, notification_type, duration)
            logger.info(f"Toast-Notification: {message} ({notification_type})")
            
        except Exception as e:
            logger.error(f"Fehler bei Toast-Notification: {e}")

    @Slot(str, str)
    def show_loading_state(self, operation: str, message: str = ""):
        """Zeigt einen Loading-State an"""
        if not self._ui_features['loading_animations']:
            return
        
        try:
            self._loading_states[operation] = {
                'message': message or f"{operation} läuft...",
                'start_time': time.time(),
                'is_active': True
            }
            
            # Loading-Signal senden
            self.loadingStateChanged.emit(operation, True, message)
            logger.info(f"Loading-State gestartet: {operation}")
            
        except Exception as e:
            logger.error(f"Fehler beim Loading-State: {e}")

    @Slot(str)
    def hide_loading_state(self, operation: str):
        """Versteckt einen Loading-State"""
        if not self._ui_features['loading_animations']:
            return
        
        try:
            if operation in self._loading_states:
                self._loading_states[operation]['is_active'] = False
                
                # Loading-Signal senden
                self.loadingStateChanged.emit(operation, False, "")
                logger.info(f"Loading-State beendet: {operation}")
                
        except Exception as e:
            logger.error(f"Fehler beim Beenden des Loading-States: {e}")

    @Slot(str, str, str, str, str, str)
    def show_confirmation_dialog(self, title: str, message: str, confirm_text: str = "Bestätigen", 
                                cancel_text: str = "Abbrechen", dialog_type: str = "info"):
        """Zeigt einen Bestätigungsdialog an"""
        if not self._ui_features['confirmation_dialogs']:
            return
        
        try:
            # Callback-ID generieren
            callback_id = f"confirm_{int(time.time() * 1000)}"
            
            # Callbacks speichern (leer für QML-Handling)
            self._confirmation_callbacks[callback_id] = {
                'on_confirm': None,
                'on_cancel': None
            }
            
            # Dialog-Signal senden
            self.confirmationDialogRequested.emit(title, message, confirm_text, cancel_text, 
                                                dialog_type, callback_id)
            logger.info(f"Confirmation-Dialog: {title}")
            
        except Exception as e:
            logger.error(f"Fehler beim Confirmation-Dialog: {e}")

    @Slot(str, str)
    def handle_confirmation_result(self, callback_id: str, result: str):
        """Behandelt das Ergebnis eines Confirmation-Dialogs"""
        try:
            if callback_id in self._confirmation_callbacks:
                callbacks = self._confirmation_callbacks[callback_id]
                
                if result == "confirm" and callbacks['on_confirm']:
                    callbacks['on_confirm']()
                elif result == "cancel" and callbacks['on_cancel']:
                    callbacks['on_cancel']()
                
                # Callback entfernen
                del self._confirmation_callbacks[callback_id]
                
        except Exception as e:
            logger.error(f"Fehler beim Behandeln des Confirmation-Results: {e}")

    @Slot(str, str)
    def register_keyboard_shortcut(self, key: str, action: str):
        """Registriert einen Keyboard-Shortcut"""
        if not self._ui_features['keyboard_shortcuts']:
            return
        
        try:
            self._keyboard_shortcuts[key] = action
            logger.info(f"Keyboard-Shortcut registriert: {key} -> {action}")
            
        except Exception as e:
            logger.error(f"Fehler beim Registrieren des Keyboard-Shortcuts: {e}")

    @Slot(str)
    def unregister_keyboard_shortcut(self, key: str):
        """Entfernt einen Keyboard-Shortcut"""
        try:
            if key in self._keyboard_shortcuts:
                del self._keyboard_shortcuts[key]
                logger.info(f"Keyboard-Shortcut entfernt: {key}")
                
        except Exception as e:
            logger.error(f"Fehler beim Entfernen des Keyboard-Shortcuts: {e}")

    @Slot(str, bool)
    def set_ui_feature(self, feature: str, enabled: bool):
        """Aktiviert/Deaktiviert UI-Features"""
        if feature in self._ui_features:
            self._ui_features[feature] = enabled
            logger.info(f"UI-Feature '{feature}' auf {enabled} gesetzt")
        else:
            logger.warning(f"Unbekanntes UI-Feature: {feature}")

    @Slot(result='QVariant')
    def get_ui_features(self) -> Dict[str, bool]:
        """Gibt aktuelle UI-Features zurück"""
        return self._ui_features

    @Slot(str, str, int)
    def show_success_toast(self, message: str, duration: int = 3000):
        """Zeigt eine Erfolgs-Toast an"""
        self.show_toast_notification(message, "success", duration)

    @Slot(str, str, int)
    def show_error_toast(self, message: str, duration: int = 5000):
        """Zeigt eine Fehler-Toast an"""
        self.show_toast_notification(message, "error", duration)

    @Slot(str, str, int)
    def show_warning_toast(self, message: str, duration: int = 4000):
        """Zeigt eine Warnungs-Toast an"""
        self.show_toast_notification(message, "warning", duration)

    @Slot(str, str, int)
    def show_info_toast(self, message: str, duration: int = 3000):
        """Zeigt eine Info-Toast an"""
        self.show_toast_notification(message, "info", duration)

    def _handle_error(self, operation: str, error: Exception, show_user_message: bool = True) -> None:
        """Zentrale Fehlerbehandlung für alle Operationen"""
        error_msg = f"Fehler bei {operation}: {str(error)}"
        logger.error(error_msg, exc_info=True)
        
        if show_user_message:
            # Spezialisierte Behandlung für Validierungsfehler
            if isinstance(error, ValueError) and "Validierungsfehler" in str(error):
                self._handle_validation_error(operation, error)
                return
            
            # User-friendly Fehlermeldung für andere Fehler
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

    def _handle_validation_error(self, operation: str, error: ValueError) -> None:
        """Spezialisierte Behandlung für Validierungsfehler"""
        try:
            # Fehlermeldung parsen
            error_str = str(error)
            if "Validierungsfehler:" in error_str:
                # Validierungsfehler-Format: "Validierungsfehler: field1: msg1; field2: msg2"
                error_parts = error_str.split("Validierungsfehler:")[1].strip()
                error_list = [part.strip() for part in error_parts.split(";") if part.strip()]
                
                # Fehlermeldungen formatieren
                formatted_errors = []
                for error_item in error_list:
                    if ":" in error_item:
                        field, message = error_item.split(":", 1)
                        formatted_errors.append(f"{field.strip()}: {message.strip()}")
                    else:
                        formatted_errors.append(error_item.strip())
                
                # Validierungsfehler-Signal senden
                self.validationErrorOccurred.emit(formatted_errors, operation)
                self.setStatusMessage(f"Validierungsfehler bei {operation}")
            else:
                # Fallback für andere ValueError
                self.errorOccurred.emit(str(error))
                self.setStatusMessage(str(error))
                
        except Exception as parse_error:
            logger.error(f"Fehler beim Parsen der Validierungsfehler: {parse_error}")
            # Fallback
            self.errorOccurred.emit(str(error))
            self.setStatusMessage(str(error))

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
    
    @Property(str, notify=loadingMessageChanged)
    def loadingMessage(self):
        return self._loading_message
    
    @Property(int, notify=loadingProgressChanged)
    def loadingProgress(self):
        return self._loading_progress
    
    @Property(str, notify=loadingChanged)
    def loadingOperation(self):
        return self._loading_operation
    
    @Property(bool, notify=savingChanged)
    def isSaving(self):
        return self._is_saving
    
    @Property(bool, notify=searchingChanged)
    def isSearching(self):
        return self._is_searching
    
    @Property(int, notify=loadingChanged)
    def totalEmployees(self):
        return self._total_employees
    
    @Property(int, notify=loadingChanged)
    def currentPage(self):
        return self._current_page
    
    @Property(int, notify=loadingChanged)
    def pageSize(self):
        return self._page_size
    
    @Property('QVariantList', notify=mitarbeiterListChanged)
    def mitarbeiterList(self):
        return self._mitarbeiter_list

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
            self.anzeigenMitarbeiter()
    @Property(bool, fget=getShowOnlyActive, fset=setShowOnlyActive, notify=showOnlyActiveChanged)
    def showOnlyActive(self):
        return self.getShowOnlyActive()

    def getSelectedEmployee(self):
        return self._selected_employee
    def setSelectedEmployee(self, value):
        if self._selected_employee != value:
            self._selected_employee = value
            self.selectedEmployeeChanged.emit()
    @Property('QVariant', fget=getSelectedEmployee, fset=setSelectedEmployee, notify=selectedEmployeeChanged)
    def selectedEmployee(self):
        return self.getSelectedEmployee()

    def getStatusMessage(self):
        return self._status_message
    def setStatusMessage(self, value):
        if self._status_message != value:
            self._status_message = value
            self.statusMessageChanged.emit()
    @Property(str, fget=getStatusMessage, fset=setStatusMessage, notify=statusMessageChanged)
    def statusMessage(self):
        return self.getStatusMessage()

    def getToggleView(self):
        return self._toggle_view
    def setToggleView(self, value):
        if self._toggle_view != value:
            self._toggle_view = value
            self.toggleViewChanged.emit()
            self.anzeigenMitarbeiter()
    @Property(bool, fget=getToggleView, fset=setToggleView, notify=toggleViewChanged)
    def toggleView(self):
        return self.getToggleView()

    @Slot()
    def toggleViewMode(self):
        """Wechselt zwischen normaler Ansicht und Deals-Ansicht"""
        self.setToggleView(not self._toggle_view)
        if self._toggle_view:
            self.setStatusMessage("Deals-Ansicht aktiviert")
        else:
            self.setStatusMessage("Normale Mitarbeiteransicht aktiviert")

    @Slot()
    def showMitarbeiterWizard(self):
        try:
            print("Mitarbeiter-Wizard wird geöffnet...")
            self.setStatusMessage("Mitarbeiter-Wizard wird geöffnet...")
            
            fields = [
                ("Führerscheinnummer", "driver_license_number", "text"),
                ("Vorname", "first_name", "text"),
                ("Nachname", "last_name", "text"),
                ("Telefon", "phone", "text"),
                ("E-Mail", "email", "text"),
                ("Einstellungsdatum", "hire_date", "text"),
                ("Status", "status", "combo", ["active", "inactive", "suspended"])
            ]
            
            def wizard_callback(data):
                try:
                    print(f"[DEBUG] Neuer Mitarbeiter-Dict: {data}")
                    self.setStatusMessage("Mitarbeiter wird gespeichert...")
                    
                    # Validierung
                    if not data.get("first_name"):
                        raise ValueError("Vorname ist erforderlich!")
                    
                    if not data.get("last_name"):
                        raise ValueError("Nachname ist erforderlich!")
                    
                    # Daten bereinigen
                    cleaned_data = {}
                    for key, value in data.items():
                        if value is not None and str(value).strip():
                            cleaned_data[key] = str(value).strip()
                        else:
                            cleaned_data[key] = ""
                    
                    # Retry-Mechanismus für kritische DB-Operation
                    def save_employee():
                        return self._db_manager.insert_mitarbeiter(cleaned_data)
                    
                    self._retry_operation(save_employee)
                    
                    self.setStatusMessage(f"Mitarbeiter {cleaned_data['first_name']} {cleaned_data['last_name']} erfolgreich gespeichert!")
                    print("Mitarbeiter erfolgreich in DB gespeichert.")
                    logger.info(f"Mitarbeiter {cleaned_data['first_name']} {cleaned_data['last_name']} erfolgreich erstellt")
                    
                except ValueError as e:
                    # User-friendly Fehlermeldung für Validierungsfehler
                    self.setStatusMessage(str(e))
                    self.errorOccurred.emit(str(e))
                    logger.warning(f"Validierungsfehler beim Erstellen des Mitarbeiters: {e}")
                except Exception as e:
                    self._handle_error("Mitarbeiter speichern", e)
                
                finally:
                    self.anzeigenMitarbeiter()
                    
            wizard = GenericWizard(fields, callback=wizard_callback, title="Neuen Mitarbeiter anlegen")
            wizard.show()
            
        except Exception as e:
            self._handle_error("Mitarbeiter-Wizard öffnen", e)

    def _cleanup_cache(self):
        """Bereinigt den Cache für bessere Memory-Performance"""
        try:
            current_time = time.time()
            
            # Cache-TTL prüfen
            if current_time - self._cache_timestamp > self._cache_ttl:
                logger.info("Cache-TTL abgelaufen, Cache wird geleert")
                self._all_employees_cache.clear()
                self._cache_timestamp = current_time
                return
            
            # Cache-Größe prüfen
            if len(self._all_employees_cache) > self._cache_size_limit:
                logger.info(f"Cache-Größe überschritten ({len(self._all_employees_cache)}), Cache wird geleert")
                self._all_employees_cache.clear()
                self._cache_timestamp = current_time
                return
            
            # Deals-Cache TTL prüfen
            if current_time - self._deals_cache_timestamp > self._deals_cache_ttl:
                logger.info("Deals-Cache-TTL abgelaufen, Deals-Cache wird geleert")
                self._deals_cache.clear()
                self._deals_cache_timestamp = current_time
            
            # Memory-Cleanup durchführen (alle 5 Minuten)
            current_time = time.time()
            if current_time - self._last_memory_cleanup > self._memory_cleanup_interval:
                self._memory_cleanup()
                self._last_memory_cleanup = current_time
                
        except Exception as e:
            logger.warning(f"Fehler beim Cache-Cleanup: {e}")
    
    def _load_deals_batch(self, employee_names):
        """Lädt alle Deals-Daten in einem Batch (N+1 Query Problem lösen)"""
        try:
            if not employee_names:
                return {}
            
            # Prüfe Cache-TTL
            current_time = time.time()
            if current_time - self._deals_cache_timestamp > self._deals_cache_ttl:
                self._deals_cache.clear()
                self._deals_cache_timestamp = current_time
            
            # Fehlende Deals aus Cache laden
            missing_names = [name for name in employee_names if name not in self._deals_cache]
            
            if missing_names:
                try:
                    conn = sqlite3.connect("SQL/database.db")
                    cursor = conn.cursor()
                    
                    # Batch-Query für alle fehlenden Namen
                    placeholders = ','.join(['?' for _ in missing_names])
                    query = f"SELECT name, deal, pauschale, umsatzgrenze, garage FROM deals WHERE name IN ({placeholders})"
                    cursor.execute(query, missing_names)
                    deal_rows = cursor.fetchall()
                    
                    # Ergebnisse in Cache speichern
                    for row in deal_rows:
                        name = row[0]
                        self._deals_cache[name] = {
                            "deal": row[1] or "-",
                            "pauschale": f"{row[2]:.2f} €" if row[2] is not None else "-",
                            "umsatzgrenze": f"{row[3]:.2f} €" if row[3] is not None else "-",
                            "garage": f"{row[4]:.2f} €" if row[4] is not None else "-"
                        }
                    
                    # Fehlende Namen mit Standardwerten markieren
                    for name in missing_names:
                        if name not in self._deals_cache:
                            self._deals_cache[name] = {
                                "deal": "-",
                                "pauschale": "-",
                                "umsatzgrenze": "-",
                                "garage": "-"
                            }
                    
                    conn.close()
                    logger.info(f"Batch-Loading: {len(missing_names)} Deals in einem Query geladen")
                    
                except Exception as e:
                    logger.error(f"Fehler beim Batch-Loading der Deals: {e}")
                    # Fallback: Standardwerte für alle fehlenden Namen
                    for name in missing_names:
                        self._deals_cache[name] = {
                            "deal": "-",
                            "pauschale": "-",
                            "umsatzgrenze": "-",
                            "garage": "-"
                        }
            
            return self._deals_cache
            
        except Exception as e:
            logger.error(f"Fehler beim Deals-Batch-Loading: {e}")
            return {}

    def _load_employees_paginated(self, page: int = 0, force_reload: bool = False) -> List[Dict]:
        """Lädt Mitarbeiter mit Pagination für bessere Performance"""
        try:
            # Cache-Cleanup vor dem Laden
            self._cleanup_cache()
            
            # Cache nur bei ersten Aufruf oder bei Force-Reload
            if not self._all_employees_cache or force_reload:
                # Loading-State setzen
                self._is_loading = True
                self._loading_message = "Lade Mitarbeiter..."
                self._loading_progress = 0
                self._loading_operation = "load_employees"
                self.loadingChanged.emit()
                self.loadingMessageChanged.emit()
                self.loadingProgressChanged.emit()
                
                # Alle Mitarbeiter laden (mit Retry)
                def load_all_employees():
                    return self._db_manager.get_all_mitarbeiter()
                
                rows = self._retry_operation(load_all_employees)
                
                # Progress: Daten geladen
                self._loading_progress = 30
                self._loading_message = f"Verarbeite {len(rows)} Mitarbeiter..."
                self.loadingProgressChanged.emit()
                self.loadingMessageChanged.emit()
                
                # Daten verarbeiten und cachen
                self._all_employees_cache = []
                filter_text = getattr(self, '_filter_text', "").lower()
                fuzzy_threshold = 0.8
                
                # Sammle alle Mitarbeiter-Namen für Batch-Loading
                employee_names = []
                filtered_employees = []
                
                for row in rows:
                    # sqlite3.Row Objekt in Dictionary umwandeln
                    if hasattr(row, 'keys'):  # sqlite3.Row Objekt
                        mitarbeiter = {
                            "driver_id": row['driver_id'] if row['driver_id'] is not None else "",
                            "driver_license_number": row['driver_license_number'] if row['driver_license_number'] is not None else "",
                            "first_name": row['first_name'] if row['first_name'] is not None else "",
                            "last_name": row['last_name'] if row['last_name'] is not None else "",
                            "phone": row['phone'] if row['phone'] is not None else "",
                            "email": row['email'] if row['email'] is not None else "",
                            "hire_date": row['hire_date'] if row['hire_date'] is not None else "",
                            "status": row['status'] if row['status'] is not None else "active"
                        }
                    else:  # Tuple
                        mitarbeiter = {
                            "driver_id": row[0] if row[0] is not None else "",
                            "driver_license_number": row[1] if row[1] is not None else "",
                            "first_name": row[2] if row[2] is not None else "",
                            "last_name": row[3] if row[3] is not None else "",
                            "phone": row[4] if row[4] is not None else "",
                            "email": row[5] if row[5] is not None else "",
                            "hire_date": row[6] if row[6] is not None else "",
                            "status": row[7] if row[7] is not None else "active"
                        }
                    
                    # Name-Feld für QML-Kompatibilität hinzufügen
                    mitarbeiter["name"] = f"{mitarbeiter['first_name']} {mitarbeiter['last_name']}".strip()
                    
                    # Filter anwenden
                    if filter_text:
                        suchfelder = [
                            str(mitarbeiter["first_name"]),
                            str(mitarbeiter["last_name"]),
                            str(mitarbeiter["email"]),
                            str(mitarbeiter["status"])
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
                            # Telefon-Suche mit verschiedenen Formaten
                            phone = str(mitarbeiter["phone"]).lower().replace(" ", "")
                            phone_alt = phone.replace("+43", "0") if "+43" in phone else phone.replace("0", "+43")
                            phone_match = (
                                filter_text in phone or
                                filter_text in phone_alt
                            )
                            if not phone_match:
                                continue
                    
                    # Status-Filter
                    if self._show_only_active and mitarbeiter["status"] != "active":
                        continue
                    
                    # Sammle Namen für Batch-Loading
                    fahrer_name = f"{mitarbeiter['first_name']} {mitarbeiter['last_name']}"
                    employee_names.append(fahrer_name)
                    filtered_employees.append(mitarbeiter)
                
                # Progress: Mitarbeiter verarbeitet
                self._loading_progress = 60
                self._loading_message = f"Verarbeite {len(filtered_employees)} Mitarbeiter..."
                self.loadingProgressChanged.emit()
                self.loadingMessageChanged.emit()
                
                # Batch-Loading für Deals (N+1 Query Problem lösen)
                if employee_names:
                    self._loading_message = "Lade Deals-Daten..."
                    self.loadingMessageChanged.emit()
                    deals_cache = self._load_deals_batch(employee_names)
                    
                    # Deals-Daten zu Mitarbeitern hinzufügen
                    for i, mitarbeiter in enumerate(filtered_employees):
                        fahrer_name = employee_names[i]
                        deal_data = deals_cache.get(fahrer_name, {})
                        mitarbeiter["deal"] = deal_data.get("deal", "-")
                        mitarbeiter["pauschale"] = deal_data.get("pauschale", "-")
                        mitarbeiter["umsatzgrenze"] = deal_data.get("umsatzgrenze", "-")
                        mitarbeiter["garage"] = deal_data.get("garage", "-")
                
                # Gefilterte Mitarbeiter zum Cache hinzufügen
                self._all_employees_cache.extend(filtered_employees)
                
                # Progress: Finalisierung
                self._loading_progress = 100
                self._loading_message = f"Fertig! {len(self._all_employees_cache)} Mitarbeiter geladen"
                self.loadingProgressChanged.emit()
                self.loadingMessageChanged.emit()
                
                self._total_employees = len(self._all_employees_cache)
                self._cache_timestamp = time.time()
                
                # Loading-State zurücksetzen
                self._is_loading = False
                self._loading_message = ""
                self._loading_progress = 0
                self._loading_operation = ""
                self.loadingChanged.emit()
                self.loadingMessageChanged.emit()
                self.loadingProgressChanged.emit()
            
            # Pagination anwenden
            start_index = page * self._page_size
            end_index = start_index + self._page_size
            return self._all_employees_cache[start_index:end_index]
            
        except Exception as e:
            self._is_loading = False
            self.loadingChanged.emit()
            self._handle_error("Mitarbeiter laden (Pagination)", e)
            return []

    def clearCache(self):
        """Manuelles Cache-Clearing für Memory-Management"""
        try:
            self._all_employees_cache.clear()
            self._cache_timestamp = time.time()
            logger.info("Cache manuell geleert")
            self.setStatusMessage("Cache geleert")
        except Exception as e:
            self._handle_error("Cache leeren", e)

    @Slot(int)
    def loadPage(self, page: int):
        """Lädt eine spezifische Seite von Mitarbeitern"""
        try:
            self._current_page = page
            self._mitarbeiter_list = self._load_employees_paginated(page)
            self.mitarbeiterListChanged.emit()
            self.setStatusMessage(f"Seite {page + 1} geladen ({len(self._mitarbeiter_list)} Mitarbeiter)")
            
        except Exception as e:
            self._handle_error("Seite laden", e)

    @Slot()
    def loadNextPage(self):
        """Lädt die nächste Seite"""
        max_pages = (self._total_employees - 1) // self._page_size
        if self._current_page < max_pages:
            self.loadPage(self._current_page + 1)

    @Slot()
    def loadPreviousPage(self):
        """Lädt die vorherige Seite"""
        if self._current_page > 0:
            self.loadPage(self._current_page - 1)

    @Slot()
    def anzeigenMitarbeiter(self):
        try:
            self.setStatusMessage("Mitarbeiter werden geladen...")
            
            # Cache invalidieren und erste Seite laden
            self._current_page = 0
            self._mitarbeiter_list = self._load_employees_paginated(0, force_reload=True)
            
            self.mitarbeiterListChanged.emit()
            self.setStatusMessage(f"{len(self._mitarbeiter_list)} Mitarbeiter geladen (von {self._total_employees} insgesamt)")
            print(f"{len(self._mitarbeiter_list)} Mitarbeiter geladen (von {self._total_employees} insgesamt)")
            logger.info(f"{len(self._mitarbeiter_list)} Mitarbeiter erfolgreich geladen (Pagination)")
            
        except Exception as e:
            self._handle_error("Mitarbeiter laden", e)

    @Slot()
    def editMitarbeiterWizard(self):
        try:
            from generic_wizard import GenericWizard
            print("Mitarbeiter bearbeiten Wizard wird geöffnet...")
            self.setStatusMessage("Mitarbeiter bearbeiten Wizard wird geöffnet...")
            
            # Retry-Mechanismus für kritische DB-Operation
            def load_all_employees():
                return self._db_manager.get_all_mitarbeiter()
            
            alle_mitarbeiter = self._retry_operation(load_all_employees)
            name_liste = [f"{row[2]} {row[3]}" for row in alle_mitarbeiter]
            
            # Felder für den Wizard
            fields = [
                ("Mitarbeiter", "mitarbeiter_combo", "combo", name_liste),
                ("Führerscheinnummer", "driver_license_number", "text"),
                ("Vorname", "first_name", "text"),
                ("Nachname", "last_name", "text"),
                ("Telefon", "phone", "text"),
                ("E-Mail", "email", "text"),
                ("Einstellungsdatum", "hire_date", "text"),
                ("Status", "status", "combo", ["active", "inactive", "suspended"])
            ]
            
            def wizard_callback(data):
                try:
                    print(f"[DEBUG] Bearbeiteter Mitarbeiter: {data}")
                    self.setStatusMessage("Mitarbeiter wird aktualisiert...")
                    
                    # Retry-Mechanismus für kritische DB-Operation
                    def update_employee():
                        index = name_liste.index(data["mitarbeiter_combo"])
                        driver_id = alle_mitarbeiter[index][0]
                        return self._db_manager.update_mitarbeiter_by_id(driver_id, data)
                    
                    self._retry_operation(update_employee)
                    
                    self.setStatusMessage(f"Mitarbeiter {data['first_name']} {data['last_name']} erfolgreich aktualisiert!")
                    print("Mitarbeiter erfolgreich aktualisiert.")
                    logger.info(f"Mitarbeiter {data['first_name']} {data['last_name']} erfolgreich aktualisiert")
                    
                except ValueError as e:
                    # User-friendly Fehlermeldung für Validierungsfehler
                    self.setStatusMessage(str(e))
                    self.errorOccurred.emit(str(e))
                    logger.warning(f"Validierungsfehler beim Aktualisieren des Mitarbeiters: {e}")
                except Exception as e:
                    self._handle_error("Mitarbeiter aktualisieren", e)
                
                finally:
                    self.anzeigenMitarbeiter()
            
            # Vorbelegung der Felder nach Auswahl
            def on_combo_change(index):
                if index < 0 or index >= len(alle_mitarbeiter):
                    return
                row = alle_mitarbeiter[index]
                # Mapping: (driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status)
                if "driver_license_number" in wizard.inputs:
                    wizard.inputs["driver_license_number"].setText(row[1] or "")
                if "first_name" in wizard.inputs:
                    wizard.inputs["first_name"].setText(row[2] or "")
                if "last_name" in wizard.inputs:
                    wizard.inputs["last_name"].setText(row[3] or "")
                if "phone" in wizard.inputs:
                    wizard.inputs["phone"].setText(row[4] or "")
                if "email" in wizard.inputs:
                    wizard.inputs["email"].setText(row[5] or "")
                if "hire_date" in wizard.inputs:
                    wizard.inputs["hire_date"].setText(str(row[6]) if row[6] else "")
                if "status" in wizard.inputs:
                    wizard.inputs["status"].setCurrentText(row[7] or "active")
            
            wizard = GenericWizard(fields, callback=wizard_callback, title="Mitarbeiter bearbeiten")
            # ComboBox-Change-Handler setzen
            if hasattr(wizard, "inputs") and "mitarbeiter_combo" in wizard.inputs:
                combo = wizard.inputs["mitarbeiter_combo"]
                combo.currentIndexChanged.connect(on_combo_change)
            wizard.show()
            
        except Exception as e:
            self._handle_error("Mitarbeiter-Wizard öffnen", e)

    @Slot(int)
    def editMitarbeiterWizard_by_id(self, driver_id):
        try:
            from generic_wizard import GenericWizard
            print(f"Mitarbeiter bearbeiten Wizard für ID {driver_id} wird geöffnet...")
            self.setStatusMessage(f"Mitarbeiter {driver_id} wird bearbeitet...")
            
            # Retry-Mechanismus für kritische DB-Operation
            def load_employee():
                return self._db_manager.get_mitarbeiter_by_id(driver_id)
            
            row = self._retry_operation(load_employee)
            if not row:
                raise ValueError(f"Kein Mitarbeiter mit ID {driver_id} gefunden.")
            
            # Felder für den Wizard
            fields = [
                ("ID", "driver_id", "text"),
                ("Führerscheinnummer", "driver_license_number", "text"),
                ("Vorname", "first_name", "text"),
                ("Nachname", "last_name", "text"),
                ("Telefon", "phone", "text"),
                ("E-Mail", "email", "text"),
                ("Einstellungsdatum", "hire_date", "text"),
                ("Status", "status", "combo", ["active", "inactive", "suspended"])
            ]
            
            def wizard_callback(data):
                try:
                    print(f"[DEBUG] Bearbeiteter Mitarbeiter: {data}")
                    self.setStatusMessage("Mitarbeiter wird aktualisiert...")
                    
                    # Retry-Mechanismus für kritische DB-Operation
                    def update_employee():
                        return self._db_manager.update_mitarbeiter_by_id(driver_id, data)
                    
                    self._retry_operation(update_employee)
                    
                    self.setStatusMessage(f"Mitarbeiter {data['first_name']} {data['last_name']} erfolgreich aktualisiert!")
                    print("Mitarbeiter erfolgreich aktualisiert.")
                    logger.info(f"Mitarbeiter {data['first_name']} {data['last_name']} erfolgreich aktualisiert")
                    
                except ValueError as e:
                    # User-friendly Fehlermeldung für Validierungsfehler
                    self.setStatusMessage(str(e))
                    self.errorOccurred.emit(str(e))
                    logger.warning(f"Validierungsfehler beim Aktualisieren des Mitarbeiters: {e}")
                except Exception as e:
                    self._handle_error("Mitarbeiter aktualisieren", e)
                
                finally:
                    self.anzeigenMitarbeiter()
            
            wizard = GenericWizard(fields, callback=wizard_callback, title=f"Mitarbeiter bearbeiten: {driver_id}")
            
            # Vorbelegung der Felder
            if hasattr(wizard, "inputs"):
                if "driver_id" in wizard.inputs:
                    wizard.inputs["driver_id"].setText(str(row[0]))
                if "driver_license_number" in wizard.inputs:
                    wizard.inputs["driver_license_number"].setText(row[1] or "")
                if "first_name" in wizard.inputs:
                    wizard.inputs["first_name"].setText(row[2] or "")
                if "last_name" in wizard.inputs:
                    wizard.inputs["last_name"].setText(row[3] or "")
                if "phone" in wizard.inputs:
                    wizard.inputs["phone"].setText(row[4] or "")
                if "email" in wizard.inputs:
                    wizard.inputs["email"].setText(row[5] or "")
                if "hire_date" in wizard.inputs:
                    wizard.inputs["hire_date"].setText(str(row[6]) if row[6] else "")
                if "status" in wizard.inputs:
                    wizard.inputs["status"].setCurrentText(row[7] or "active")
            
            wizard.show()
            
        except ValueError as e:
            # User-friendly Fehlermeldung für Validierungsfehler
            self.setStatusMessage(str(e))
            self.errorOccurred.emit(str(e))
            logger.warning(f"Validierungsfehler beim Bearbeiten des Mitarbeiters: {e}")
        except Exception as e:
            self._handle_error("Mitarbeiter-Wizard öffnen", e)

    @Slot(int)
    def editDealsWizard(self, vorwahl_index):
        from generic_wizard import GenericWizard
        db = DBManager()
        alle_mitarbeiter = db.get_all_mitarbeiter()
        name_liste = [f"{row[2]} {row[3]}" for row in alle_mitarbeiter]
        
        fields = [
            ("Mitarbeiter", "mitarbeiter_combo", "combo", name_liste),
            ("Deal-Typ", "deal", "combo", ["P", "%"]),
            ("Pauschale (€)", "pauschale", "text"),
            ("Umsatzgrenze (€)", "umsatzgrenze", "text"),
            ("Garage (€)", "garage", "text")
        ]
        
        def wizard_callback(data):
            try:
                # Hole die aktuellen Deals-Daten für den Mitarbeiter
                fahrer_name = data["mitarbeiter_combo"]
                deal_type = data["deal"]
                pauschale = float(data["pauschale"]) if data["pauschale"] and deal_type == "P" else None
                umsatzgrenze = float(data["umsatzgrenze"]) if data["umsatzgrenze"] and deal_type == "P" else None
                garage = float(data["garage"]) if data["garage"] else None
                
                # Validiere die Daten je nach Deal-Typ
                if deal_type == "P":
                    if pauschale is None or umsatzgrenze is None:
                        print("Fehler: Bei P-Deal müssen Pauschale und Umsatzgrenze angegeben werden.")
                        return
                elif deal_type == "%":
                    # Bei %-Deal werden Pauschale und Umsatzgrenze automatisch auf None gesetzt
                    pass
                
                # Speichere in deals-Tabelle
                conn = sqlite3.connect("SQL/database.db")
                cursor = conn.cursor()
                
                # Prüfe ob Eintrag bereits existiert
                cursor.execute("SELECT id FROM deals WHERE name = ?", (fahrer_name,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update bestehenden Eintrag
                    cursor.execute("""
                        UPDATE deals 
                        SET deal = ?, pauschale = ?, umsatzgrenze = ?, garage = ?
                        WHERE name = ?
                    """, (deal_type, pauschale, umsatzgrenze, garage, fahrer_name))
                else:
                    # Erstelle neuen Eintrag
                    cursor.execute("""
                        INSERT INTO deals (name, deal, pauschale, umsatzgrenze, garage)
                        VALUES (?, ?, ?, ?, ?)
                    """, (fahrer_name, deal_type, pauschale, umsatzgrenze, garage))
                
                conn.commit()
                conn.close()
                print("Deals-Daten erfolgreich gespeichert.")
                
            except Exception as e:
                print(f"Fehler beim Speichern der Deals-Daten: {e}")
            
            self.anzeigenMitarbeiter()
        
        def on_combo_change(index):
            if index < 0 or index >= len(alle_mitarbeiter):
                return
            
            # Lade bestehende Deals-Daten für den Mitarbeiter
            fahrer_name = name_liste[index]
            try:
                conn = sqlite3.connect("SQL/database.db")
                cursor = conn.cursor()
                cursor.execute("SELECT deal, pauschale, umsatzgrenze, garage FROM deals WHERE name = ?", (fahrer_name,))
                row = cursor.fetchone()
                conn.close()
                
                if row and "deal" in wizard.inputs:
                    wizard.inputs["deal"].setCurrentText(row[0] or "P")
                if row and "pauschale" in wizard.inputs:
                    wizard.inputs["pauschale"].setText(f"{row[1]:.2f}" if row[1] is not None else "")
                if row and "umsatzgrenze" in wizard.inputs:
                    wizard.inputs["umsatzgrenze"].setText(f"{row[2]:.2f}" if row[2] is not None else "")
                if row and "garage" in wizard.inputs:
                    wizard.inputs["garage"].setText(f"{row[3]:.2f}" if row[3] is not None else "")
                    
            except Exception as e:
                print(f"Fehler beim Laden der Deals-Daten: {e}")
        
        wizard = GenericWizard(fields, callback=wizard_callback, title="Deals bearbeiten")
        if hasattr(wizard, "inputs") and "mitarbeiter_combo" in wizard.inputs:
            combo = wizard.inputs["mitarbeiter_combo"]
            combo.currentIndexChanged.connect(on_combo_change)
            # Vorwahl setzen, falls Index übergeben
            if vorwahl_index >= 0 and vorwahl_index < len(name_liste):
                combo.setCurrentIndex(vorwahl_index)
                on_combo_change(vorwahl_index)
        wizard.show()

    @Slot(int)
    def editDealsWizard_by_id(self, driver_id):
        db = DBManager()
        row = db.get_mitarbeiter_by_id(driver_id)
        if not row:
            print(f"Kein Mitarbeiter mit ID {driver_id} gefunden.")
            return
        name = f"{row[2]} {row[3]}"
        alle_mitarbeiter = db.get_all_mitarbeiter()
        name_liste = [f"{r[2]} {r[3]}" for r in alle_mitarbeiter]
        try:
            index = name_liste.index(name)
        except ValueError:
            print(f"Name {name} nicht in der Liste gefunden.")
            return
        self.editDealsWizard(index)

    @Slot(int, str)
    def updateStatus(self, index, status):
        db = DBManager()
        alle_mitarbeiter = db.get_all_mitarbeiter()
        if 0 <= index < len(alle_mitarbeiter):
            driver_id = alle_mitarbeiter[index][0]
            # Hole aktuelle Daten
            row = alle_mitarbeiter[index]
            data = {
                "driver_license_number": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "phone": row[4],
                "email": row[5],
                "hire_date": row[6],
                "status": status
            }
            db.update_mitarbeiter_by_id(driver_id, data)
            self.anzeigenMitarbeiter()

    @Slot(int)
    def selectEmployee(self, driver_id):
        """Wählt einen Mitarbeiter aus"""
        try:
            # Mitarbeiter in der Datenbank finden
            query = """
                SELECT * FROM drivers 
                WHERE driver_id = ?
            """
            rows = self._db_manager.fetch_all(query, (driver_id,))
            employee = rows[0] if rows else None
            
            if employee:
                self._selected_employee = dict(employee)
                self.selectedEmployeeChanged.emit()
                self.setStatusMessage(f"Mitarbeiter ausgewählt: {employee['first_name']} {employee['last_name']}")
            else:
                self.setStatusMessage("Mitarbeiter nicht gefunden")
                
        except Exception as e:
            self._handle_error("Mitarbeiter auswählen", e)

    @Slot(int)
    def deleteEmployee(self, driver_id):
        """Löscht einen Mitarbeiter aus der Datenbank (ohne Bestätigung - für direkte Aufrufe)"""
        try:
            # Mitarbeiter-Daten für Status-Nachricht abrufen
            query = "SELECT first_name, last_name FROM drivers WHERE driver_id = ?"
            rows = self._db_manager.fetch_all(query, (driver_id,))
            employee = rows[0] if rows else None
            
            if not employee:
                self.setStatusMessage("Mitarbeiter nicht gefunden")
                return
            
            # Mitarbeiter löschen
            delete_query = "DELETE FROM drivers WHERE driver_id = ?"
            self._db_manager.execute_query(delete_query, (driver_id,))
            
            # Cache invalidieren
            self._current_page = 0
            self._mitarbeiter_list = self._load_employees_paginated(0, force_reload=True)
            self.mitarbeiterListChanged.emit()
            
            self.setStatusMessage(f"Mitarbeiter '{employee['first_name']} {employee['last_name']}' erfolgreich gelöscht")
            
        except Exception as e:
            self._handle_error("Mitarbeiter löschen", e)

    @Slot(int)
    def deleteEmployeeWithConfirmation(self, driver_id):
        """Löscht einen Mitarbeiter mit Bestätigungsdialog"""
        try:
            # Mitarbeiter-Daten für Bestätigungsdialog abrufen
            query = "SELECT first_name, last_name, driver_id FROM drivers WHERE driver_id = ?"
            rows = self._db_manager.fetch_all(query, (driver_id,))
            employee = rows[0] if rows else None
            
            if not employee:
                self.setStatusMessage("Mitarbeiter nicht gefunden")
                return
            
            # Bestätigungsdialog anzeigen
            self._show_delete_confirmation_dialog(employee)
            
        except Exception as e:
            self._handle_error("Mitarbeiter-Löschung vorbereiten", e)

    def _show_delete_confirmation_dialog(self, employee):
        """Zeigt Bestätigungsdialog für Mitarbeiter-Löschung"""
        try:
            # Mitarbeiter-Daten für Dialog
            employee_data = {
                'driver_id': employee['driver_id'],
                'first_name': employee['first_name'],
                'last_name': employee['last_name']
            }
            
            # Signal für QML-Dialog senden
            self.deleteConfirmationRequested.emit(employee_data)
            
        except Exception as e:
            self._handle_error("Bestätigungsdialog anzeigen", e)

    @Slot(dict)
    def confirmDeleteEmployee(self, employee_data):
        """Bestätigt die Löschung eines Mitarbeiters"""
        try:
            driver_id = employee_data.get('driver_id')
            first_name = employee_data.get('first_name')
            last_name = employee_data.get('last_name')
            
            if not driver_id:
                self.setStatusMessage("Ungültige Mitarbeiter-Daten")
                return
            
            # Prüfen ob Mitarbeiter noch existiert
            query = "SELECT driver_id FROM drivers WHERE driver_id = ?"
            rows = self._db_manager.fetch_all(query, (driver_id,))
            
            if not rows:
                self.setStatusMessage("Mitarbeiter wurde bereits gelöscht")
                return
            
            # Abhängigkeiten prüfen (Deals, etc.)
            dependencies = self._check_employee_dependencies(driver_id)
            if dependencies:
                self.setStatusMessage(f"Mitarbeiter kann nicht gelöscht werden: {dependencies}")
                return
            
            # Mitarbeiter löschen
            delete_query = "DELETE FROM drivers WHERE driver_id = ?"
            self._db_manager.execute_query(delete_query, (driver_id,))
            
            # Cache invalidieren
            self._current_page = 0
            self._mitarbeiter_list = self._load_employees_paginated(0, force_reload=True)
            self.mitarbeiterListChanged.emit()
            
            self.setStatusMessage(f"Mitarbeiter '{first_name} {last_name}' erfolgreich gelöscht")
            
        except Exception as e:
            self._handle_error("Mitarbeiter löschen", e)

    def _check_employee_dependencies(self, driver_id):
        """Prüft Abhängigkeiten eines Mitarbeiters"""
        try:
            # Hier können weitere Abhängigkeiten geprüft werden
            # z.B. Deals, Fahrzeuge, etc.
            
            # Aktuell keine Abhängigkeiten implementiert
            # TODO: Implementiere Abhängigkeiten-Prüfung wenn Deals-Tabelle verfügbar ist
            
            return None  # Keine Abhängigkeiten
            
        except Exception as e:
            logger.error(f"Fehler beim Prüfen der Abhängigkeiten: {e}")
            return "Fehler beim Prüfen der Abhängigkeiten"
    
    def _check_duplicates(self, employee_data):
        """Prüft auf Duplikate in der Datenbank"""
        try:
            driver_id = employee_data.get('driver_id', '').strip()
            license_number = employee_data.get('driver_license_number', '').strip()
            original_driver_id = employee_data.get('original_driver_id', '').strip()
            
            duplicates = {
                'driver_id_exists': False,
                'license_exists': False,
                'existing_employee': None,
                'existing_license_employee': None
            }
            
            # Prüfe Driver ID Duplikat
            if driver_id:
                query = "SELECT driver_id, first_name, last_name FROM drivers WHERE driver_id = ?"
                if original_driver_id and original_driver_id != driver_id:
                    # Update-Fall: Prüfe nur andere Mitarbeiter (nicht den aktuellen)
                    query += " AND driver_id != ?"
                    rows = self._db_manager.fetch_all(query, (driver_id, original_driver_id))
                elif original_driver_id and original_driver_id == driver_id:
                    # Update-Fall: Gleiche ID, keine Duplikat-Prüfung nötig
                    rows = []
                else:
                    # Neuer Mitarbeiter: Prüfe alle
                    rows = self._db_manager.fetch_all(query, (driver_id,))
                
                if rows:
                    duplicates['driver_id_exists'] = True
                    duplicates['existing_employee'] = {
                        'driver_id': rows[0]['driver_id'],
                        'first_name': rows[0]['first_name'],
                        'last_name': rows[0]['last_name']
                    }
            
            # Prüfe Führerscheinnummer Duplikat
            if license_number:
                query = "SELECT driver_id, first_name, last_name FROM drivers WHERE driver_license_number = ?"
                if original_driver_id:
                    # Update-Fall: Prüfe nur andere Mitarbeiter (nicht den aktuellen)
                    query += " AND driver_id != ?"
                    rows = self._db_manager.fetch_all(query, (license_number, original_driver_id))
                else:
                    # Neuer Mitarbeiter: Prüfe alle
                    rows = self._db_manager.fetch_all(query, (license_number,))
                
                if rows:
                    duplicates['license_exists'] = True
                    duplicates['existing_license_employee'] = {
                        'driver_id': rows[0]['driver_id'],
                        'first_name': rows[0]['first_name'],
                        'last_name': rows[0]['last_name']
                    }
            
            return duplicates
            
        except Exception as e:
            logger.error(f"Fehler beim Prüfen der Duplikate: {e}")
            return None

    @Slot('QVariant')
    def saveEmployee(self, employee_data):
        """Speichert einen neuen Mitarbeiter oder aktualisiert einen bestehenden"""
        try:
            # Saving-State setzen
            self._is_saving = True
            self._loading_message = "Speichere Mitarbeiter..."
            self._loading_progress = 0
            self._loading_operation = "save_employee"
            self.savingChanged.emit()
            self.loadingMessageChanged.emit()
            self.loadingProgressChanged.emit()
            self.loadingChanged.emit()
            
            # QJSValue zu Python-Dict konvertieren
            if hasattr(employee_data, 'toVariant'):
                employee_data = employee_data.toVariant()
            elif hasattr(employee_data, 'toPyObject'):
                employee_data = employee_data.toPyObject()
            
            # Progress: Validierung
            self._loading_progress = 20
            self._loading_message = "Validiere Daten..."
            self.loadingProgressChanged.emit()
            self.loadingMessageChanged.emit()
            
            # Duplikate prüfen
            duplicates = self._check_duplicates(employee_data)
            if duplicates and (duplicates['driver_id_exists'] or duplicates['license_exists']):
                # Progress: Duplikate gefunden
                self._loading_progress = 50
                self._loading_message = "Duplikate gefunden..."
                self.loadingProgressChanged.emit()
                self.loadingMessageChanged.emit()
                
                # Loading-State zurücksetzen
                self._is_saving = False
                self._loading_message = ""
                self._loading_progress = 0
                self._loading_operation = ""
                self.savingChanged.emit()
                self.loadingMessageChanged.emit()
                self.loadingProgressChanged.emit()
                self.loadingChanged.emit()
                
                # Duplikate gefunden - Dialog anzeigen
                self._show_duplicate_dialog(employee_data, duplicates)
                return
            
            # Progress: Speichern
            self._loading_progress = 80
            self._loading_message = "Speichere in Datenbank..."
            self.loadingProgressChanged.emit()
            self.loadingMessageChanged.emit()
            
            # Keine Duplikate - direkt speichern
            self._save_employee_internal(employee_data)
            
            # Progress: Fertig
            self._loading_progress = 100
            self._loading_message = "Mitarbeiter erfolgreich gespeichert!"
            self.loadingProgressChanged.emit()
            self.loadingMessageChanged.emit()
            
            # Loading-State zurücksetzen
            self._is_saving = False
            self._loading_message = ""
            self._loading_progress = 0
            self._loading_operation = ""
            self.savingChanged.emit()
            self.loadingMessageChanged.emit()
            self.loadingProgressChanged.emit()
            self.loadingChanged.emit()
            
        except Exception as e:
            # Loading-State zurücksetzen bei Fehler
            self._is_saving = False
            self._loading_message = ""
            self._loading_progress = 0
            self._loading_operation = ""
            self.savingChanged.emit()
            self.loadingMessageChanged.emit()
            self.loadingProgressChanged.emit()
            self.loadingChanged.emit()
            self._handle_error("Mitarbeiter speichern", e)
    
    def _show_duplicate_dialog(self, employee_data, duplicates):
        """Zeigt Dialog für Duplikat-Behandlung"""
        try:
            dialog_data = {
                'employee_data': employee_data,
                'duplicates': duplicates,
                'message': self._build_duplicate_message(duplicates)
            }
            self.duplicateCheckRequested.emit(dialog_data)
        except Exception as e:
            self._handle_error("Duplikat-Dialog anzeigen", e)
    
    def _build_duplicate_message(self, duplicates):
        """Erstellt Nachricht für Duplikat-Dialog"""
        messages = []
        
        if duplicates['driver_id_exists']:
            existing = duplicates['existing_employee']
            messages.append(f"Driver ID '{existing['driver_id']}' existiert bereits bei '{existing['first_name']} {existing['last_name']}'")
        
        if duplicates['license_exists']:
            existing = duplicates['existing_license_employee']
            messages.append(f"Führerscheinnummer existiert bereits bei '{existing['first_name']} {existing['last_name']}'")
        
        return " | ".join(messages)
    
    def _save_employee_internal(self, employee_data):
        """Interne Methode zum Speichern eines Mitarbeiters"""
        try:
            # Daten validieren
            required_fields = ['driver_license_number', 'first_name', 'last_name']
            for field in required_fields:
                value = employee_data.get(field)
                if not value:
                    self.setStatusMessage(f"Pflichtfeld '{field}' ist leer")
                    return
            
            # Prüfen ob Driver ID angegeben wurde
            driver_id = employee_data.get('driver_id')
            if not driver_id:
                self.setStatusMessage("Driver ID ist erforderlich")
                return
            
            # Prüfen ob neue Driver ID bereits existiert (außer bei Update des gleichen Mitarbeiters)
            existing_driver_id = self._db_manager.fetch_all("SELECT driver_id FROM drivers WHERE driver_id = ?", (employee_data['driver_id'],))
            
            # Prüfen ob es sich um ein Update handelt (original_driver_id ist gesetzt)
            original_driver_id = employee_data.get('original_driver_id')
            
            if original_driver_id and original_driver_id != employee_data['driver_id']:
                # Driver ID wurde geändert - prüfen ob neue ID bereits existiert
                if existing_driver_id:
                    self.setStatusMessage(f"Driver ID '{employee_data['driver_id']}' existiert bereits")
                    return
                
                # Update mit neuer Driver ID
                update_query = """
                    UPDATE drivers 
                    SET driver_id = ?, driver_license_number = ?, first_name = ?, last_name = ?, 
                        phone = ?, email = ?, hire_date = ?, status = ?
                    WHERE driver_id = ?
                """
                update_data = (
                    employee_data['driver_id'],
                    employee_data['driver_license_number'],
                    employee_data['first_name'],
                    employee_data['last_name'],
                    employee_data.get('phone', ''),
                    employee_data.get('email', ''),
                    employee_data.get('hire_date', ''),
                    employee_data.get('status', 'active'),
                    original_driver_id
                )
                
                self._db_manager.execute_query(update_query, update_data)
                self.setStatusMessage(f"Mitarbeiter '{employee_data['first_name']} {employee_data['last_name']}' aktualisiert (Driver ID: {original_driver_id} → {employee_data['driver_id']})")
                
            elif existing_driver_id:
                # Update bestehenden Mitarbeiters (Driver ID unverändert)
                update_query = """
                    UPDATE drivers 
                    SET driver_license_number = ?, first_name = ?, last_name = ?, 
                        phone = ?, email = ?, hire_date = ?, status = ?
                    WHERE driver_id = ?
                """
                update_data = (
                    employee_data['driver_license_number'],
                    employee_data['first_name'],
                    employee_data['last_name'],
                    employee_data.get('phone', ''),
                    employee_data.get('email', ''),
                    employee_data.get('hire_date', ''),
                    employee_data.get('status', 'active'),
                    employee_data['driver_id']
                )
                
                self._db_manager.execute_query(update_query, update_data)
                self.setStatusMessage(f"Mitarbeiter '{employee_data['first_name']} {employee_data['last_name']}' aktualisiert")
                
            else:
                # Neuer Mitarbeiter
                insert_query = """
                    INSERT INTO drivers (driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                insert_data = (
                    employee_data['driver_id'],
                    employee_data['driver_license_number'],
                    employee_data['first_name'],
                    employee_data['last_name'],
                    employee_data.get('phone', ''),
                    employee_data.get('email', ''),
                    employee_data.get('hire_date', ''),
                    employee_data.get('status', 'active')
                )
                
                self._db_manager.execute_query(insert_query, insert_data)
                self.setStatusMessage(f"Mitarbeiter '{employee_data['first_name']} {employee_data['last_name']}' erfolgreich angelegt")
            
            # Daten neu laden
            self._current_page = 0
            self._mitarbeiter_list = self._load_employees_paginated(0, force_reload=True)
            self.mitarbeiterListChanged.emit()
            
        except Exception as e:
            self._handle_error("Mitarbeiter speichern", e)
    
    @Slot(dict)
    def handleDuplicateChoice(self, choice_data):
        """Behandelt die Benutzerauswahl bei Duplikaten"""
        try:
            choice = choice_data.get('choice')
            employee_data = choice_data.get('employee_data')
            
            if choice == 'replace':
                # Bestehenden Mitarbeiter ersetzen
                self._save_employee_internal(employee_data)
            elif choice == 'new_id':
                # Neue Driver ID generieren
                new_driver_id = self._generate_new_driver_id()
                employee_data['driver_id'] = new_driver_id
                self._save_employee_internal(employee_data)
            elif choice == 'edit_existing':
                # Bestehenden Mitarbeiter bearbeiten - Signal an QML senden
                existing_driver_id = choice_data.get('existing_driver_id')
                logger.info(f"Edit existing employee with driver_id: {existing_driver_id}")
                if existing_driver_id:
                    # Signal an QML senden, um das Formular zu öffnen
                    logger.info(f"Emitting editEmployeeInForm signal with driver_id: {existing_driver_id}")
                    self.editEmployeeInForm.emit(existing_driver_id)
                else:
                    logger.error("No existing_driver_id found in choice_data")
            else:
                self.setStatusMessage("Aktion abgebrochen")
                
        except Exception as e:
            self._handle_error("Duplikat-Behandlung", e)
    
    def _generate_new_driver_id(self):
        """Generiert eine neue, freie Driver ID"""
        try:
            # Finde die höchste existierende Driver ID
            query = "SELECT MAX(CAST(driver_id AS INTEGER)) FROM drivers"
            result = self._db_manager.fetch_all(query)
            max_id = result[0][0] if result and result[0][0] else 0
            
            # Neue ID ist die höchste + 1
            new_id = max_id + 1
            
            # Stelle sicher, dass die ID mindestens 3-stellig ist
            while new_id < 100:
                new_id += 1
                
            return str(new_id)
            
        except Exception as e:
            logger.error(f"Fehler beim Generieren der Driver ID: {e}")
            return "999"  # Fallback
    
    @Slot(int, result='QVariant')
    def getEmployeeById(self, driver_id):
        """Lädt einen Mitarbeiter anhand der Driver ID"""
        try:
            logger.info(f"getEmployeeById aufgerufen mit driver_id: {driver_id}")
            query = """
                SELECT driver_id, driver_license_number, first_name, last_name, 
                       phone, email, hire_date, status
                FROM drivers 
                WHERE driver_id = ?
            """
            rows = self._db_manager.fetch_all(query, (driver_id,))
            logger.info(f"Database query result: {rows}")
            
            if rows:
                # Konvertiere zu QML-kompatiblen Typen
                employee_data = {
                    'driver_id': str(rows[0]['driver_id']),
                    'driver_license_number': str(rows[0]['driver_license_number']),
                    'first_name': str(rows[0]['first_name']),
                    'last_name': str(rows[0]['last_name']),
                    'phone': str(rows[0]['phone'] or ''),
                    'email': str(rows[0]['email'] or ''),
                    'hire_date': str(rows[0]['hire_date'] or ''),
                    'status': str(rows[0]['status'] or 'active')
                }
                logger.info(f"Employee data prepared: {employee_data}")
                return employee_data
            else:
                logger.warning(f"Mitarbeiter mit Driver ID {driver_id} nicht gefunden")
                self.setStatusMessage(f"Mitarbeiter mit Driver ID {driver_id} nicht gefunden")
                return None
                
        except Exception as e:
            logger.error(f"Fehler beim Laden des Mitarbeiters: {e}")
            self._handle_error("Mitarbeiter laden", e)
            return None

    @Slot(int, result='QVariant')
    def getDealByDriverId(self, driver_id):
        """Holt die Deal-Daten für einen Mitarbeiter anhand der Driver ID"""
        try:
            logger.info(f"getDealByDriverId aufgerufen mit driver_id: {driver_id}")
            
            # Hole Mitarbeiter-Daten
            query = """
                SELECT driver_id, first_name, last_name
                FROM drivers 
                WHERE driver_id = ?
            """
            rows = self._db_manager.fetch_all(query, (driver_id,))
            
            if not rows:
                logger.warning(f"Mitarbeiter mit Driver ID {driver_id} nicht gefunden")
                return None
            
            employee = rows[0]
            employee_name = f"{employee['first_name']} {employee['last_name']}"
            
            # Hole Deal-Daten
            deal_query = """
                SELECT deal, pauschale, umsatzgrenze, garage
                FROM deals 
                WHERE name = ?
            """
            deal_rows = self._db_manager.fetch_all(deal_query, (employee_name,))
            
            if deal_rows:
                deal = deal_rows[0]
                logger.info(f"Deal-Daten gefunden für {employee_name}: {deal}")
                logger.info(f"Deal-Typ: {deal['deal']}, Typ: {type(deal['deal'])}")
                logger.info(f"Pauschale: {deal['pauschale']}, Typ: {type(deal['pauschale'])}")
                logger.info(f"Umsatzgrenze: {deal['umsatzgrenze']}, Typ: {type(deal['umsatzgrenze'])}")
                logger.info(f"Garage: {deal['garage']}, Typ: {type(deal['garage'])}")
                
                # Sichere Typkonvertierung
                deal_type = str(deal['deal']) if deal['deal'] is not None else 'P'
                pauschale = str(deal['pauschale']) if deal['pauschale'] is not None else ''
                umsatzgrenze = str(deal['umsatzgrenze']) if deal['umsatzgrenze'] is not None else ''
                garage = str(deal['garage']) if deal['garage'] is not None else ''
                
                result = {
                    'driver_id': str(driver_id),
                    'employee_name': employee_name,
                    'deal_type': deal_type,
                    'pauschale': pauschale,
                    'umsatzgrenze': umsatzgrenze,
                    'garage': garage
                }
                
                logger.info(f"Zurückgegebene Daten: {result}")
                return result
            else:
                # Fallback: Standard-Deal
                logger.info(f"Keine Deal-Daten für {employee_name} gefunden, verwende Standard")
                return {
                    'driver_id': str(driver_id),
                    'employee_name': employee_name,
                    'deal_type': 'P',
                    'pauschale': '',
                    'umsatzgrenze': '',
                    'garage': ''
                }
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Deal-Daten: {e}")
            self._handle_error("Deal-Daten laden", e)
            return None

    @Slot(int, str, str, str, str, result='QVariant')
    def saveDealData(self, driver_id, deal_type, pauschale, umsatzgrenze, garage):
        """Speichert Deal-Daten direkt in der Datenbank"""
        try:
            logger.info(f"saveDealData aufgerufen mit driver_id: {driver_id}, deal_type: {deal_type}")
            
            # Hole Mitarbeiter-Daten
            query = """
                SELECT driver_id, first_name, last_name
                FROM drivers 
                WHERE driver_id = ?
            """
            rows = self._db_manager.fetch_all(query, (driver_id,))
            
            if not rows:
                logger.warning(f"Mitarbeiter mit Driver ID {driver_id} nicht gefunden")
                return False
            
            employee = rows[0]
            employee_name = f"{employee['first_name']} {employee['last_name']}"
            
            # Prüfe ob Deal bereits existiert
            check_query = "SELECT id FROM deals WHERE name = ?"
            existing_deal = self._db_manager.fetch_all(check_query, (employee_name,))
            
            # Werte basierend auf Deal-Typ korrekt setzen
            if deal_type == '%':
                # Bei %-Deal: pauschale und umsatzgrenze müssen NULL sein
                pauschale_db = None
                umsatzgrenze_db = None
            elif deal_type == 'P':
                # Bei P-Deal: pauschale und umsatzgrenze müssen Werte haben
                pauschale_db = float(pauschale) if pauschale and pauschale.strip() else None
                umsatzgrenze_db = float(umsatzgrenze) if umsatzgrenze and umsatzgrenze.strip() else None
            else:  # C-Deal
                # Bei C-Deal: keine Einschränkungen
                pauschale_db = float(pauschale) if pauschale and pauschale.strip() else None
                umsatzgrenze_db = float(umsatzgrenze) if umsatzgrenze and umsatzgrenze.strip() else None
            
            garage_db = float(garage) if garage and garage.strip() else 0.0
            
            logger.info(f"Deal-Typ: {deal_type}, Pauschale: {pauschale_db}, Umsatzgrenze: {umsatzgrenze_db}, Garage: {garage_db}")
            
            if existing_deal:
                # Update bestehenden Deal
                update_query = """
                    UPDATE deals 
                    SET deal = ?, pauschale = ?, umsatzgrenze = ?, garage = ?
                    WHERE name = ?
                """
                self._db_manager.execute_query(update_query, (deal_type, pauschale_db, umsatzgrenze_db, garage_db, employee_name))
                logger.info(f"Deal für {employee_name} aktualisiert")
            else:
                # Erstelle neuen Deal
                insert_query = """
                    INSERT INTO deals (name, deal, pauschale, umsatzgrenze, garage)
                    VALUES (?, ?, ?, ?, ?)
                """
                self._db_manager.execute_query(insert_query, (employee_name, deal_type, pauschale_db, umsatzgrenze_db, garage_db))
                logger.info(f"Neuer Deal für {employee_name} erstellt")
            
            # Cache invalidieren
            self._deals_cache = {}
            
            self.setStatusMessage(f"Deal für {employee_name} erfolgreich gespeichert")
            return {"success": True, "message": f"Deal für {employee_name} erfolgreich gespeichert"}
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Deal-Daten: {e}")
            self._handle_error("Deal-Daten speichern", e)
            return {"success": False, "message": f"Fehler beim Speichern: {str(e)}"}

    @Slot(int, str)
    def updateStatusById(self, driver_id, status):
        """Aktualisiert den Status eines Mitarbeiters anhand der ID"""
        try:
            # Status validieren
            valid_statuses = ['active', 'suspended', 'inactive']
            if status not in valid_statuses:
                self.setStatusMessage(f"Ungültiger Status: {status}")
                return
            
            # Status aktualisieren
            update_query = "UPDATE drivers SET status = ? WHERE driver_id = ?"
            self._db_manager.execute_query(update_query, (status, driver_id))
            
            # Cache invalidieren und Daten neu laden
            self._current_page = 0
            self._mitarbeiter_list = self._load_employees_paginated(0, force_reload=True)
            self.mitarbeiterListChanged.emit()
            
            self.setStatusMessage(f"Status auf '{status}' geändert")
            
        except Exception as e:
            self._handle_error("Status aktualisieren", e)

    @Slot()
    def refreshData(self):
        """Lädt alle Daten neu"""
        try:
            self._is_loading = True
            self.loadingChanged.emit()
            
            # Cache komplett leeren
            self._all_employees_cache = []
            self._current_page = 0
            self._cache_timestamp = time.time()
            
            # Daten neu laden
            self._mitarbeiter_list = self._load_employees_paginated(0, force_reload=True)
            self.mitarbeiterListChanged.emit()
            
            self._is_loading = False
            self.loadingChanged.emit()
            self.setStatusMessage("Daten erfolgreich aktualisiert")
            
        except Exception as e:
            self._is_loading = False
            self.loadingChanged.emit()
            self._handle_error("Daten aktualisieren", e)

    def __del__(self):
        """Cleanup beim Zerstören des Objekts"""
        try:
            # Timer bereinigen
            if hasattr(self, '_search_timer') and self._search_timer:
                self._search_timer.cancel()
                self._search_timer = None
            
            # Memory-Monitor-Timer ist deaktiviert für Thread-Kompatibilität
            pass
            
            # Cache-Objekte leeren
            if hasattr(self, '_all_employees_cache'):
                self._all_employees_cache.clear()
                self._all_employees_cache = None
            
            if hasattr(self, '_deals_cache'):
                self._deals_cache.clear()
                self._deals_cache = None
            
            # Database-Manager bereinigen
            if hasattr(self, '_db_manager'):
                self._db_manager = None
            
            # QML-Signale trennen (vereinfacht)
            try:
                # Signale werden automatisch beim Zerstören des Objekts getrennt
                pass
            except Exception as e:
                logger.warning(f"Fehler beim Trennen der Signale: {e}")
            
            logger.info("MitarbeiterSeiteQMLV2 Cleanup abgeschlossen")
        except Exception as e:
            logger.warning(f"Fehler beim Cleanup: {e}")
    
    def cleanup_resources(self):
        """Manuelles Cleanup für Memory-Management"""
        try:
            # Cache leeren
            if hasattr(self, '_all_employees_cache'):
                self._all_employees_cache.clear()
            
            if hasattr(self, '_deals_cache'):
                self._deals_cache.clear()
            
            # Timer stoppen
            if hasattr(self, '_search_timer') and self._search_timer:
                self._search_timer.cancel()
                self._search_timer = None
            
            # Loading-State zurücksetzen
            self._is_loading = False
            self.loadingChanged.emit()
            
            logger.info("Ressourcen manuell bereinigt")
            self.setStatusMessage("Ressourcen bereinigt")
            
        except Exception as e:
            logger.error(f"Fehler beim manuellen Cleanup: {e}")
    
    def _memory_cleanup(self):
        """Automatisches Memory-Cleanup"""
        try:
            current_time = time.time()
            
            # Cache-Größe prüfen und reduzieren
            if hasattr(self, '_all_employees_cache') and len(self._all_employees_cache) > self._cache_size_limit:
                # Nur die ersten 50 Einträge behalten
                self._all_employees_cache = self._all_employees_cache[:50]
                logger.info("Cache-Größe reduziert")
            
            # Deals-Cache-Größe prüfen
            if hasattr(self, '_deals_cache') and len(self._deals_cache) > 100:
                # Nur die letzten 50 Einträge behalten
                keys_to_keep = list(self._deals_cache.keys())[-50:]
                self._deals_cache = {k: self._deals_cache[k] for k in keys_to_keep}
                logger.info("Deals-Cache-Größe reduziert")
            
            # Query-Cache TTL prüfen
            if hasattr(self, '_query_cache') and current_time - self._query_cache_timestamp > self._query_cache_ttl:
                self._query_cache.clear()
                self._query_cache_timestamp = current_time
                logger.info("Query-Cache geleert (TTL abgelaufen)")
            
            # Memory-Usage loggen
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self._performance_stats['memory_usage'] = memory_mb
            logger.info(f"Memory-Usage: {memory_mb:.2f} MB")
            
        except Exception as e:
            logger.error(f"Fehler beim Memory-Cleanup: {e}")

    def _get_connection(self, db_path: str = "SQL/database.db"):
        """Thread-sichere Datenbankverbindung aus dem Pool"""
        try:
            if db_path not in self._connection_pool:
                self._connection_pool[db_path] = []
            
            # Verfügbare Verbindung suchen
            for conn in self._connection_pool[db_path]:
                try:
                    # Verbindung testen
                    conn.execute("SELECT 1")
                    return conn
                except:
                    # Verbindung ist ungültig, entfernen
                    self._connection_pool[db_path].remove(conn)
                    try:
                        conn.close()
                    except:
                        pass
            
            # Neue Verbindung erstellen
            if len(self._connection_pool[db_path]) < self._max_connections:
                conn = sqlite3.connect(db_path, timeout=self._connection_timeout)
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA cache_size = 10000")
                conn.execute("PRAGMA temp_store = MEMORY")
                self._connection_pool[db_path].append(conn)
                return conn
            else:
                # Fallback: Neue Verbindung ohne Pool
                return sqlite3.connect(db_path, timeout=self._connection_timeout)
                
        except Exception as e:
            logger.error(f"Fehler beim Verbindungsaufbau: {e}")
            # Fallback
            return sqlite3.connect(db_path, timeout=self._connection_timeout)

    def _execute_query_with_cache(self, query: str, params: tuple = (), cache_key: str = None):
        """Führt Query mit Cache aus"""
        start_time = time.time()
        
        try:
            # Cache-Key generieren falls nicht angegeben
            if cache_key is None:
                cache_key = f"{query}_{hash(str(params))}"
            
            # Cache prüfen
            if cache_key in self._query_cache:
                cache_entry = self._query_cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self._query_cache_ttl:
                    self._performance_stats['cache_hits'] += 1
                    logger.debug(f"Cache-Hit für Query: {cache_key}")
                    return cache_entry['result']
            
            # Query ausführen
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            
            # Performance-Statistiken aktualisieren
            query_time = time.time() - start_time
            self._performance_stats['queries_executed'] += 1
            self._performance_stats['cache_misses'] += 1
            self._query_times.append(query_time)
            
            # Durchschnittliche Query-Zeit berechnen
            if len(self._query_times) > 10:
                self._query_times = self._query_times[-10:]  # Nur die letzten 10
            self._performance_stats['avg_query_time'] = sum(self._query_times) / len(self._query_times)
            
            # Ergebnis cachen
            self._query_cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            
            logger.debug(f"Query ausgeführt: {query_time:.3f}s - {cache_key}")
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei Query-Ausführung: {e}")
            raise e

    def _lazy_load_employees(self, page: int = 0, force_reload: bool = False):
        """Lazy Loading für Mitarbeiter-Daten"""
        try:
            if not force_reload and self._all_employees_cache:
                # Cache verwenden
                start_idx = page * self._page_size
                end_idx = start_idx + self._page_size
                return self._all_employees_cache[start_idx:end_idx]
            
            # Lazy Loading nur bei großen Datensätzen
            if self._lazy_loading_enabled:
                # Zuerst nur die Anzahl laden
                count_query = "SELECT COUNT(*) FROM drivers"
                if self._show_only_active:
                    count_query += " WHERE status = 'active'"
                
                count_result = self._execute_query_with_cache(count_query, cache_key=f"count_{self._show_only_active}")
                total_count = count_result[0][0] if count_result else 0
                
                if total_count > self._lazy_loading_threshold:
                    # Lazy Loading für große Datensätze
                    return self._load_employees_lazy(page)
            
            # Normales Laden für kleine Datensätze
            return self._load_employees_paginated(page, force_reload)
            
        except Exception as e:
            logger.error(f"Fehler beim Lazy Loading: {e}")
            return []

    def _load_employees_lazy(self, page: int = 0):
        """Lazy Loading-Implementierung für große Datensätze"""
        try:
            start_idx = page * self._page_size
            
            # Query mit LIMIT und OFFSET
            query = """
                SELECT driver_id, driver_license_number, first_name, last_name, 
                       phone, email, hire_date, status
                FROM drivers
            """
            
            if self._show_only_active:
                query += " WHERE status = 'active'"
            
            query += " ORDER BY last_name, first_name LIMIT ? OFFSET ?"
            
            result = self._execute_query_with_cache(
                query, 
                (self._page_size, start_idx),
                cache_key=f"lazy_employees_{self._show_only_active}_{page}"
            )
            
            # Daten formatieren
            employees = []
            for row in result:
                employee = {
                    "driver_id": row[0],
                    "driver_license_number": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "phone": row[4] or "",
                    "email": row[5] or "",
                    "hire_date": row[6] or "",
                    "status": row[7] or "active"
                }
                employees.append(employee)
            
            return employees
            
        except Exception as e:
            logger.error(f"Fehler beim Lazy Loading: {e}")
            return []

    @Slot(result='QVariant')
    def get_performance_stats(self):
        """Gibt Performance-Statistiken zurück"""
        return {
            'queries_executed': self._performance_stats['queries_executed'],
            'cache_hits': self._performance_stats['cache_hits'],
            'cache_misses': self._performance_stats['cache_misses'],
            'cache_hit_rate': (self._performance_stats['cache_hits'] / 
                              max(1, self._performance_stats['cache_hits'] + self._performance_stats['cache_misses'])) * 100,
            'avg_query_time': self._performance_stats['avg_query_time'],
            'memory_usage_mb': self._performance_stats['memory_usage'],
            'cache_size': len(self._all_employees_cache) + len(self._deals_cache),
            'query_cache_size': len(self._query_cache)
        }

    @Slot()
    def clear_performance_cache(self):
        """Leert alle Performance-Caches"""
        try:
            self._query_cache.clear()
            self._all_employees_cache.clear()
            self._deals_cache.clear()
            self._performance_stats['cache_hits'] = 0
            self._performance_stats['cache_misses'] = 0
            self._query_times.clear()
            logger.info("Alle Performance-Caches geleert")
            self.setStatusMessage("Performance-Caches geleert")
        except Exception as e:
            logger.error(f"Fehler beim Cache-Clear: {e}")
            self.setStatusMessage("Fehler beim Cache-Clear") 