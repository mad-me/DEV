import sqlite3
import pandas as pd
import threading
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

# Logger für bessere Fehlerbehandlung
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception für Datenbankfehler"""
    pass

class DatabaseConnectionPool:
    """Connection Pool für bessere Performance und Thread-Safety"""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections = []
        self._lock = threading.Lock()
        self._active_connections = 0
        
    def get_connection(self) -> sqlite3.Connection:
        """Thread-safe Connection aus dem Pool holen"""
        with self._lock:
            if self._connections:
                return self._connections.pop()
            elif self._active_connections < self.max_connections:
                self._active_connections += 1
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row  # Named columns
                return conn
            else:
                raise RuntimeError("Keine verfügbaren Datenbankverbindungen")
    
    def return_connection(self, conn: sqlite3.Connection):
        """Connection zurück in den Pool geben"""
        with self._lock:
            if self._active_connections > 0:
                self._active_connections -= 1
                if len(self._connections) < self.max_connections:
                    self._connections.append(conn)
                else:
                    conn.close()

class DBManager:
    def __init__(self, db_path="SQL/database.db"):
        self.db_path = db_path
        self._pool = DatabaseConnectionPool(db_path)
        self._setup_logging()
        # Initialisiere Tabellen beim Start
        self.initialize_database_tables()
    
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
    
    def initialize_database_tables(self):
        """Initialisiert alle erforderlichen Tabellen in der Hauptdatenbank"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                
                # 1. DRIVERS Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS drivers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        driver_id INTEGER UNIQUE NOT NULL,
                        driver_license_number TEXT UNIQUE NOT NULL,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        phone TEXT,
                        email TEXT,
                        hire_date DATE,
                        status TEXT CHECK(status IN ('active', 'inactive', 'suspended'))
                    )
                """)
                
                # Falls die Tabelle bereits existiert, migriere zu neuem Schema
                try:
                    cursor.execute("""
                        CREATE TABLE drivers_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            driver_id INTEGER UNIQUE NOT NULL,
                            driver_license_number TEXT UNIQUE NOT NULL,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            phone TEXT,
                            email TEXT,
                            hire_date DATE,
                            status TEXT CHECK(status IN ('active', 'inactive', 'suspended'))
                        )
                    """)
                    
                    # Daten migrieren falls Tabelle existiert
                    cursor.execute("""
                        INSERT INTO drivers_new (driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status)
                        SELECT driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status 
                        FROM drivers
                    """)
                    
                    cursor.execute("DROP TABLE drivers")
                    cursor.execute("ALTER TABLE drivers_new RENAME TO drivers")
                    
                except sqlite3.OperationalError:
                    # Tabelle existiert nicht oder ist bereits korrekt
                    pass
                
                # Indizes für drivers
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_drivers_name
                    ON drivers(first_name, last_name)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_drivers_status
                    ON drivers(status)
                """)
                
                # 2. VEHICLES Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vehicles (
                        vehicle_id INTEGER PRIMARY KEY,
                        license_plate TEXT UNIQUE NOT NULL,
                        rfrnc TEXT,
                        model TEXT,
                        year INTEGER,
                        insurance TEXT NOT NULL,
                        credit TEXT,
                        status TEXT DEFAULT 'Aktiv',
                        notes TEXT DEFAULT '',
                        created_at TEXT DEFAULT '',
                        updated_at TEXT DEFAULT '',
                        stammfahrer TEXT
                    )
                """)
                
                # Migration: Füge stammfahrer Spalte hinzu falls sie nicht existiert
                try:
                    cursor.execute("ALTER TABLE vehicles ADD COLUMN stammfahrer TEXT")
                    logger.info("✅ stammfahrer Spalte zur vehicles Tabelle hinzugefügt")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        # Spalte existiert bereits - kein Log nötig für normale Operation
                        pass
                    else:
                        logger.warning(f"⚠️ Fehler beim Hinzufügen der stammfahrer Spalte: {e}")
                
                # 3. DEALS Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS deals (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        deal TEXT NOT NULL CHECK (deal IN ('P', '%', 'C')),
                        pauschale REAL,
                        umsatzgrenze REAL,
                        garage REAL,
                        FOREIGN KEY (id) REFERENCES drivers(driver_id) ON DELETE CASCADE,
                        CHECK (
                            (deal = 'P' AND pauschale IS NOT NULL AND umsatzgrenze IS NOT NULL) OR
                            (deal = '%' AND pauschale IS NULL AND umsatzgrenze IS NULL) OR
                            (deal = 'C')
                        )
                    )
                """)
                
                # 4. CUSTOM_DEAL_CONFIG Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_deal_config (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fahrer TEXT UNIQUE,
                        config_json TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 5. DEAL_TEMPLATES Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS deal_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        deal_type TEXT UNIQUE,
                        template_json TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 6. OVERLAY_CONFIGS Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS overlay_configs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        driver_id INTEGER,
                        config_json TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(driver_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_overlay_configs_driver 
                    ON overlay_configs(driver_id)
                """)
                
                # Nur bei Debug-Modus oder ersten Start loggen
                # logger.info("✅ Alle Datenbank-Tabellen erfolgreich initialisiert")
                
        except Exception as e:
            logger.error(f"❌ Fehler bei der Datenbank-Initialisierung: {e}")
            raise DatabaseError(f"Datenbank-Initialisierung fehlgeschlagen: {e}") from e
    
    @contextmanager
    def _connect(self):
        """Context Manager für sichere Datenbankverbindungen"""
        conn = None
        try:
            conn = self._pool.get_connection()
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                try:
                    conn.commit()
                except sqlite3.Error as e:
                    logger.error(f"Commit error: {e}")
                    conn.rollback()
                finally:
                    self._pool.return_connection(conn)
    
    def _handle_database_error(self, operation: str, error: Exception) -> None:
        """Zentrale Fehlerbehandlung für alle DB-Operationen"""
        error_msg = f"Database error during {operation}: {error}"
        logger.error(error_msg, exc_info=True)
        raise DatabaseError(error_msg) from error
    
    def _sanitize_input(self, value: Any, max_length: int = 255) -> str:
        """Sanitized einen Eingabewert"""
        if value is None:
            return ""
        return str(value).strip()[:max_length]

    def _validate_driver_id(self, driver_id: Any) -> bool:
        """Validiert eine Driver ID"""
        try:
            if driver_id is None or str(driver_id).strip() == "":
                return False
            driver_id_int = int(driver_id)
            return 1 <= driver_id_int <= 999999  # Realistische Range für Driver IDs
        except (ValueError, TypeError):
            return False

    def _validate_email(self, email: str) -> bool:
        """Validiert eine E-Mail-Adresse"""
        if not email or not isinstance(email, str):
            return True  # Leere E-Mails sind erlaubt
        
        import re
        # Striktere E-Mail-Validierung
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email.strip()):
            return False
        
        # Zusätzliche Checks für ungültige Muster
        email_clean = email.strip()
        if '..' in email_clean or email_clean.startswith('.') or email_clean.endswith('.'):
            return False
        
        return True

    def _validate_phone(self, phone: str) -> bool:
        """Validiert eine Telefonnummer"""
        if not phone or not isinstance(phone, str):
            return True  # Leere Telefonnummern sind erlaubt
        
        import re
        # Entferne alle Leerzeichen, Klammern, Bindestriche
        cleaned = re.sub(r'[\s\(\)\-]', '', phone.strip())
        # Prüfe ob nur Zahlen und + am Anfang
        return bool(re.match(r'^\+?[\d]{7,15}$', cleaned))

    def _validate_name(self, name: str) -> bool:
        """Validiert einen Namen"""
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        if len(name) < 2 or len(name) > 50:
            return False
        
        # Erweiterte Zeichenunterstützung für internationale Namen
        import re
        # Unicode-Zeichen für internationale Namen (Buchstaben, Leerzeichen, Bindestriche, Akzente)
        return bool(re.match(r'^[\p{L}\s\-]+$', name, re.UNICODE))

    def _validate_license_number(self, license_number: str) -> bool:
        """Validiert eine Führerscheinnummer"""
        if not license_number or not isinstance(license_number, str):
            return True  # Leere Führerscheinnummern sind erlaubt
        
        license_number = license_number.strip()
        if len(license_number) < 5 or len(license_number) > 20:
            return False
        
        # Nur Buchstaben, Zahlen und Bindestriche erlaubt
        import re
        return bool(re.match(r'^[A-Z0-9\-]+$', license_number))

    def _validate_license_plate(self, license_plate: str) -> bool:
        """Validiert ein Kfz-Kennzeichen"""
        if not license_plate or not isinstance(license_plate, str):
            return False  # Kennzeichen sind erforderlich
        
        license_plate = license_plate.strip().upper()
        if len(license_plate) < 3 or len(license_plate) > 12:
            return False
        
        # Deutsche Kennzeichen: Verschiedene Formate
        import re
        # Erlaubt verschiedene deutsche Kennzeichenformate
        patterns = [
            # Standard-Kennzeichen: AB CD 123, AB CD 123H/E
            r'^[A-Z]{1,3}[\s\-]?[A-Z]{1,2}[\s\-]?\d{1,4}[HE]?$',
            # Kurz-Kennzeichen: AB 123, AB 123H/E  
            r'^[A-Z]{1,3}[\s\-]?\d{1,4}[HE]?$',
            # Kompakte Kennzeichen ohne Leerzeichen: W588BTX, B123ABC
            r'^[A-Z]{1,3}\d{1,4}[A-Z]{1,3}$',
            # Saisonkennzeichen: AB CD 123/04-10
            r'^[A-Z]{1,3}[\s\-]?[A-Z]{1,2}[\s\-]?\d{1,4}/\d{2}\-\d{2}$',
            # Wechselkennzeichen: AB CD 123W
            r'^[A-Z]{1,3}[\s\-]?[A-Z]{1,2}[\s\-]?\d{1,4}W$',
        ]
        
        # Normalisiere Trennzeichen für Pattern-Matching
        normalized = license_plate.replace('-', ' ').replace('  ', ' ')
        
        for pattern in patterns:
            if re.match(pattern, license_plate) or re.match(pattern, normalized):
                return True
        
        return False

    def _validate_date(self, date_str: str) -> bool:
        """Validiert ein Datum"""
        if not date_str or not isinstance(date_str, str):
            return True  # Leere Daten sind erlaubt
        
        import re
        from datetime import datetime
        
        # Verschiedene Datumsformate unterstützen
        date_formats = [
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%Y/%m/%d'
        ]
        
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        
        return False

    def _validate_employee_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Validiert alle Mitarbeiterdaten und gibt Fehlermeldungen zurück"""
        errors = {}
        
        # Driver ID Validierung
        if "driver_id" in data:
            if not self._validate_driver_id(data["driver_id"]):
                errors["driver_id"] = "Driver ID muss eine gültige Zahl zwischen 1 und 999999 sein"
        
        # Name Validierung
        if "first_name" in data:
            if not self._validate_name(data["first_name"]):
                errors["first_name"] = "Vorname muss 2-50 Zeichen lang sein und nur Buchstaben enthalten"
        
        if "last_name" in data:
            if not self._validate_name(data["last_name"]):
                errors["last_name"] = "Nachname muss 2-50 Zeichen lang sein und nur Buchstaben enthalten"
        
        # E-Mail Validierung
        if "email" in data:
            if not self._validate_email(data["email"]):
                errors["email"] = "E-Mail-Adresse hat ein ungültiges Format"
        
        # Telefon Validierung
        if "phone" in data:
            if not self._validate_phone(data["phone"]):
                errors["phone"] = "Telefonnummer hat ein ungültiges Format"
        
        # Führerscheinnummer Validierung
        if "driver_license_number" in data:
            if not self._validate_license_number(data["driver_license_number"]):
                errors["driver_license_number"] = "Führerscheinnummer hat ein ungültiges Format"
        
        # Datum Validierung
        if "hire_date" in data:
            if not self._validate_date(data["hire_date"]):
                errors["hire_date"] = "Datum hat ein ungültiges Format (erwartet: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY)"
        
        # Status Validierung
        if "status" in data:
            valid_statuses = ["active", "inactive", "suspended"]
            if data["status"] not in valid_statuses:
                errors["status"] = f"Status muss einer der folgenden Werte sein: {', '.join(valid_statuses)}"
        
        return errors

    def _check_driver_id_exists(self, driver_id: int) -> bool:
        """Prüft ob eine Driver ID bereits existiert"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM drivers WHERE driver_id = ?", (driver_id,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            self._handle_database_error("_check_driver_id_exists", e)
            return False

    def _check_email_exists(self, email: str, exclude_driver_id: Optional[int] = None) -> bool:
        """Prüft ob eine E-Mail-Adresse bereits existiert"""
        if not email:
            return False
        
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                if exclude_driver_id:
                    cursor.execute("SELECT COUNT(*) FROM drivers WHERE email = ? AND driver_id != ?", 
                                 (email, exclude_driver_id))
                else:
                    cursor.execute("SELECT COUNT(*) FROM drivers WHERE email = ?", (email,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            self._handle_database_error("_check_email_exists", e)
            return False

    def _check_license_number_exists(self, license_number: str, exclude_driver_id: Optional[int] = None) -> bool:
        """Prüft ob eine Führerscheinnummer bereits existiert"""
        if not license_number:
            return False
        
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                if exclude_driver_id:
                    cursor.execute("SELECT COUNT(*) FROM drivers WHERE driver_license_number = ? AND driver_id != ?", 
                                 (license_number, exclude_driver_id))
                else:
                    cursor.execute("SELECT COUNT(*) FROM drivers WHERE driver_license_number = ?", (license_number,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            self._handle_database_error("_check_license_number_exists", e)
            return False

    def _generate_next_driver_id(self) -> int:
        """Generiert die nächste verfügbare Driver ID"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(driver_id) FROM drivers")
                result = cursor.fetchone()
                max_id = result[0] if result[0] else 0
                return max_id + 1
        except Exception as e:
            self._handle_database_error("_generate_next_driver_id", e)
            return 1  # Fallback

    # 🚗 Fahrzeuge

    def get_all_fahrzeuge(self) -> List[Tuple]:
        """Gibt alle Fahrzeuge als Liste von Tupeln zurück"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT license_plate, rfrnc, model, year, insurance, credit, 
                           COALESCE(status, 'Aktiv') as status,
                           COALESCE(stammfahrer, '') as stammfahrer,
                           COALESCE(notes, '') as notes,
                           COALESCE(created_at, '') as created_at,
                           COALESCE(updated_at, '') as updated_at
                    FROM vehicles
                    ORDER BY license_plate
                """)
                return cursor.fetchall()
        except Exception as e:
            self._handle_database_error("get_all_fahrzeuge", e)

    def get_fahrzeug_by_plate(self, license_plate: str) -> Optional[Tuple]:
        """Gibt ein Fahrzeug als Tupel anhand des Kennzeichens zurück"""
        try:
            # Validierung entfernt - wird bereits in insert_fahrzeug durchgeführt
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT license_plate, rfrnc, model, year, insurance, credit,
                           COALESCE(status, 'Aktiv') as status,
                           COALESCE(stammfahrer, '') as stammfahrer,
                           COALESCE(notes, '') as notes,
                           COALESCE(created_at, '') as created_at,
                           COALESCE(updated_at, '') as updated_at
                    FROM vehicles
                    WHERE license_plate = ?
                """, (license_plate,))
                return cursor.fetchone()
        except Exception as e:
            self._handle_database_error("get_fahrzeug_by_plate", e)

    def insert_fahrzeug(self, data: Dict[str, Any]) -> bool:
        """Fügt ein neues Fahrzeug ein. data ist ein dict mit passenden Keys."""
        try:
            # Validierung
            if not data.get("license_plate"):
                raise ValueError("Kennzeichen ist erforderlich")
            
            if not self._validate_license_plate(data["license_plate"]):
                raise ValueError(f"Ungültiges Kennzeichen: {data['license_plate']}")
            
            # Daten sanitieren
            sanitized_data = {
                "license_plate": self._sanitize_input(data["license_plate"]),
                "rfrnc": self._sanitize_input(data.get("rfrnc", "")),
                "model": self._sanitize_input(data.get("model", "")),
                "year": self._sanitize_input(data.get("year", "")),
                "insurance": self._sanitize_input(data.get("insurance", "")),
                "credit": self._sanitize_input(data.get("credit", "")),
                "status": self._sanitize_input(data.get("status", "Aktiv")),
                "stammfahrer": self._sanitize_input(data.get("stammfahrer", "")),
                "notes": self._sanitize_input(data.get("notes", ""))
            }
            
            # Prüfen ob Fahrzeug bereits existiert
            existing = self.get_fahrzeug_by_plate(sanitized_data["license_plate"])
            if existing:
                raise ValueError(f"Fahrzeug mit Kennzeichen {sanitized_data['license_plate']} existiert bereits")
            
            # Korrigiere Dezimaltrennzeichen und Typen
            def fix_num(val):
                if isinstance(val, str):
                    val = val.replace(",", ".")
                try:
                    return float(val) if val else None
                except Exception:
                    return None
            
            insurance = fix_num(sanitized_data["insurance"])
            if insurance is None:
                insurance = ""  # Leerer String statt None für NOT NULL Constraint
            credit = fix_num(sanitized_data["credit"])
            year = sanitized_data["year"]
            try:
                year = int(year) if year else None
            except Exception:
                year = None
            
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO vehicles (
                        license_plate, rfrnc, model, year, insurance, credit, 
                        status, stammfahrer, notes, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    sanitized_data["license_plate"],
                    sanitized_data["rfrnc"],
                    sanitized_data["model"],
                    year,
                    insurance,
                    credit,
                    sanitized_data["status"],
                    sanitized_data["stammfahrer"],
                    sanitized_data["notes"]
                ))
                
                logger.info(f"Fahrzeug {sanitized_data['license_plate']} erfolgreich eingefügt")
                return True
                
        except Exception as e:
            self._handle_database_error("insert_fahrzeug", e)

    def update_fahrzeug_by_plate(self, license_plate: str, data: Dict[str, Any]) -> bool:
        """Aktualisiert ein Fahrzeug anhand des Kennzeichens"""
        try:
            if not self._validate_license_plate(license_plate):
                raise ValueError(f"Ungültiges Kennzeichen: {license_plate}")
            
            # Prüfen ob nur Status-Update
            if len(data) == 1 and "status" in data:
                # Nur Status aktualisieren
                with self._connect() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE vehicles
                        SET status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE license_plate = ?
                    """, (data["status"], license_plate))
                    
                    if cursor.rowcount == 0:
                        raise ValueError(f"Fahrzeug mit Kennzeichen {license_plate} nicht gefunden")
                    
                    logger.info(f"Status von Fahrzeug {license_plate} auf {data['status']} aktualisiert")
                    return True
            else:
                # Vollständiges Update
                # Daten sanitieren
                sanitized_data = {
                    "rfrnc": self._sanitize_input(data.get("rfrnc", "")),
                    "model": self._sanitize_input(data.get("model", "")),
                    "year": self._sanitize_input(data.get("year", "")),
                    "insurance": self._sanitize_input(data.get("insurance", "")),
                    "credit": self._sanitize_input(data.get("credit", "")),
                    "status": self._sanitize_input(data.get("status", "Aktiv")),
                    "stammfahrer": self._sanitize_input(data.get("stammfahrer", "")),
                    "notes": self._sanitize_input(data.get("notes", ""))
                }
                
                # Korrigiere Dezimaltrennzeichen und Typen
                def fix_num(val):
                    if isinstance(val, str):
                        val = val.replace(",", ".")
                    try:
                        return float(val) if val else None
                    except Exception:
                        return None
                
                insurance = fix_num(sanitized_data["insurance"])
                if insurance is None:
                    insurance = ""  # Leerer String statt None für NOT NULL Constraint
                credit = fix_num(sanitized_data["credit"])
                year = sanitized_data["year"]
                try:
                    year = int(year) if year else None
                except Exception:
                    year = None
                
                with self._connect() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE vehicles
                        SET rfrnc = ?, model = ?, year = ?, insurance = ?, credit = ?,
                            status = ?, stammfahrer = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE license_plate = ?
                    """, (
                        sanitized_data["rfrnc"],
                        sanitized_data["model"],
                        year,
                        insurance,
                        credit,
                        sanitized_data["status"],
                        sanitized_data["stammfahrer"],
                        sanitized_data["notes"],
                        license_plate
                    ))
                    
                    if cursor.rowcount == 0:
                        raise ValueError(f"Fahrzeug mit Kennzeichen {license_plate} nicht gefunden")
                    
                    logger.info(f"Fahrzeug {license_plate} erfolgreich aktualisiert")
                    return True
                
        except Exception as e:
            self._handle_database_error("update_fahrzeug_by_plate", e)

    def delete_fahrzeug_by_plate(self, license_plate: str) -> bool:
        """Löscht ein Fahrzeug anhand des Kennzeichens"""
        try:
            if not self._validate_license_plate(license_plate):
                raise ValueError(f"Ungültiges Kennzeichen: {license_plate}")
            
            # Prüfen ob abhängige Daten existieren
            if self._has_dependent_data(license_plate):
                raise ValueError(f"Fahrzeug {license_plate} hat abhängige Daten und kann nicht gelöscht werden")
            
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM vehicles WHERE license_plate = ?", (license_plate,))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Fahrzeug mit Kennzeichen {license_plate} nicht gefunden")
                
                logger.info(f"Fahrzeug {license_plate} erfolgreich gelöscht")
                return True
                
        except Exception as e:
            self._handle_database_error("delete_fahrzeug_by_plate", e)
    
    def _has_dependent_data(self, license_plate: str) -> bool:
        """Prüft ob abhängige Daten für ein Fahrzeug existieren"""
        try:
            # Prüfen in revenue.db
            revenue_conn = sqlite3.connect("SQL/revenue.db")
            revenue_cursor = revenue_conn.cursor()
            revenue_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            if revenue_cursor.fetchone():
                revenue_cursor.execute("SELECT COUNT(*) FROM [{}]".format(license_plate))
                if revenue_cursor.fetchone()[0] > 0:
                    revenue_conn.close()
                    return True
            revenue_conn.close()
            
            # Prüfen in running_costs.db
            running_costs_conn = sqlite3.connect("SQL/running_costs.db")
            running_costs_cursor = running_costs_conn.cursor()
            running_costs_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (license_plate,))
            if running_costs_cursor.fetchone():
                running_costs_cursor.execute("SELECT COUNT(*) FROM [{}]".format(license_plate))
                if running_costs_cursor.fetchone()[0] > 0:
                    running_costs_conn.close()
                    return True
            running_costs_conn.close()
            
            return False
        except Exception as e:
            logger.warning(f"Fehler beim Prüfen abhängiger Daten: {e}")
            return False

    def get_dataframe_from_table(self, table_name: str) -> pd.DataFrame:
        """
        Liest eine komplette Tabelle aus der Datenbank und gibt sie als
        einen pandas DataFrame zurück.
        """
        try:
            with self._connect() as conn:
                query = f"SELECT * FROM {table_name}"
                df = pd.read_sql_query(query, conn)
                return df
        except Exception as e:
            self._handle_database_error("get_dataframe_from_table", e)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Führt eine beliebige SQL-Abfrage aus.
        Ideal für INSERT, UPDATE, DELETE.
        Gibt die lastrowid für INSERTs zurück.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.lastrowid
        except Exception as e:
            self._handle_database_error("execute_query", e)

    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Tuple]:
        """Führt eine SELECT-Abfrage aus und gibt alle Ergebnisse zurück."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            self._handle_database_error("fetch_all", e)

    def generic_insert(self, table_name: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Fügt einen neuen Datensatz in eine beliebige Tabelle ein.
        :param table_name: Name der Tabelle.
        :param data: Ein Dictionary, bei dem die Schlüssel die Spaltennamen
                     und die Werte die einzufügenden Daten sind.
        """
        if not data:
            return None

        # Sanitize table name
        table_name = self._sanitize_input(table_name, 50)
        
        # Sanitize data
        sanitized_data = {
            key: self._sanitize_input(value) 
            for key, value in data.items()
        }

        columns = ', '.join(sanitized_data.keys())
        placeholders = ', '.join(['?' for _ in sanitized_data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            last_row_id = self.execute_query(query, list(sanitized_data.values()))
            return last_row_id
        except Exception as e:
            self._handle_database_error("generic_insert", e)

    def get_all_records(self, table_name: str, columns: str = '*') -> List[Tuple]:
        try:
            query = f"SELECT {columns} FROM {table_name}"
            return self.fetch_all(query)
        except Exception as e:
            self._handle_database_error("get_all_records", e)

    def get_all_mitarbeiter(self) -> List[Tuple]:
        """Gibt alle Mitarbeiter als Liste von Tupeln zurück"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status
                    FROM drivers
                    ORDER BY last_name, first_name
                """)
                return cursor.fetchall()
        except Exception as e:
            self._handle_database_error("get_all_mitarbeiter", e)

    def insert_mitarbeiter(self, data: Dict[str, Any]) -> bool:
        """Fügt einen neuen Mitarbeiter ein. data ist ein dict mit passenden Keys."""
        try:
            # Umfassende Validierung
            validation_errors = self._validate_employee_data(data)
            if validation_errors:
                error_messages = "; ".join([f"{field}: {msg}" for field, msg in validation_errors.items()])
                raise ValueError(f"Validierungsfehler: {error_messages}")
            
            # Duplikat-Prüfung
            if "email" in data and data["email"]:
                if self._check_email_exists(data["email"]):
                    raise ValueError("E-Mail-Adresse wird bereits verwendet")
            
            if "driver_license_number" in data and data["driver_license_number"]:
                if self._check_license_number_exists(data["driver_license_number"]):
                    raise ValueError("Führerscheinnummer wird bereits verwendet")
            
            # Driver ID generieren falls nicht vorhanden
            driver_id = data.get("driver_id")
            if not driver_id:
                driver_id = self._generate_next_driver_id()
            
            # Daten sanitieren
            sanitized_data = {
                "driver_id": driver_id,
                "driver_license_number": self._sanitize_input(data["driver_license_number"]),
                "first_name": self._sanitize_input(data["first_name"]),
                "last_name": self._sanitize_input(data["last_name"]),
                "phone": self._sanitize_input(data.get("phone", "")),
                "email": self._sanitize_input(data.get("email", "")),
                "hire_date": self._sanitize_input(data.get("hire_date", "")),
                "status": self._sanitize_input(data.get("status", "active"))
            }
            
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO drivers (driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sanitized_data["driver_id"],
                    sanitized_data["driver_license_number"],
                    sanitized_data["first_name"],
                    sanitized_data["last_name"],
                    sanitized_data["phone"],
                    sanitized_data["email"],
                    sanitized_data["hire_date"],
                    sanitized_data["status"]
                ))
                
                logger.info(f"Mitarbeiter {sanitized_data['first_name']} {sanitized_data['last_name']} (ID: {driver_id}) erfolgreich eingefügt")
                return True
                
        except Exception as e:
            self._handle_database_error("insert_mitarbeiter", e)

    def update_mitarbeiter_by_id(self, driver_id: int, data: Dict[str, Any]) -> bool:
        """Aktualisiert einen Mitarbeiter anhand der ID."""
        try:
            # Umfassende Validierung
            validation_errors = self._validate_employee_data(data)
            if validation_errors:
                error_messages = "; ".join([f"{field}: {msg}" for field, msg in validation_errors.items()])
                raise ValueError(f"Validierungsfehler: {error_messages}")
            
            # Duplikat-Prüfung (ausschließlich aktueller Mitarbeiter)
            if "email" in data and data["email"]:
                if self._check_email_exists(data["email"], exclude_driver_id=driver_id):
                    raise ValueError("E-Mail-Adresse wird bereits von einem anderen Mitarbeiter verwendet")
            
            if "driver_license_number" in data and data["driver_license_number"]:
                if self._check_license_number_exists(data["driver_license_number"], exclude_driver_id=driver_id):
                    raise ValueError("Führerscheinnummer wird bereits von einem anderen Mitarbeiter verwendet")
            
            # Daten sanitieren
            sanitized_data = {
                "driver_license_number": self._sanitize_input(data["driver_license_number"]),
                "first_name": self._sanitize_input(data["first_name"]),
                "last_name": self._sanitize_input(data["last_name"]),
                "phone": self._sanitize_input(data.get("phone", "")),
                "email": self._sanitize_input(data.get("email", "")),
                "hire_date": self._sanitize_input(data.get("hire_date", "")),
                "status": self._sanitize_input(data.get("status", "active"))
            }
            
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE drivers
                    SET driver_license_number = ?, first_name = ?, last_name = ?, phone = ?, email = ?, hire_date = ?, status = ?
                    WHERE driver_id = ?
                """, (
                    sanitized_data["driver_license_number"],
                    sanitized_data["first_name"],
                    sanitized_data["last_name"],
                    sanitized_data["phone"],
                    sanitized_data["email"],
                    sanitized_data["hire_date"],
                    sanitized_data["status"],
                    driver_id
                ))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Mitarbeiter mit ID {driver_id} nicht gefunden")
                
                logger.info(f"Mitarbeiter {driver_id} erfolgreich aktualisiert")
                return True
                
        except Exception as e:
            self._handle_database_error("update_mitarbeiter_by_id", e)

    def get_mitarbeiter_by_id(self, driver_id: int) -> Optional[Tuple]:
        """Gibt einen Mitarbeiter als Tupel anhand der ID zurück"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status
                    FROM drivers
                    WHERE driver_id = ?
                """, (driver_id,))
                return cursor.fetchone()
        except Exception as e:
            self._handle_database_error("get_mitarbeiter_by_id", e)

    def update_mitarbeiter_id_and_data(self, alte_id: int, neue_id: int, data: Dict[str, Any]) -> bool:
        """Aktualisiert alle Felder eines Mitarbeiters und setzt auch die ID neu."""
        try:
            # Umfassende Validierung
            validation_errors = self._validate_employee_data(data)
            if validation_errors:
                error_messages = "; ".join([f"{field}: {msg}" for field, msg in validation_errors.items()])
                raise ValueError(f"Validierungsfehler: {error_messages}")
            
            # Driver ID Validierung für neue ID
            if not self._validate_driver_id(neue_id):
                raise ValueError("Neue Driver ID muss eine gültige Zahl zwischen 1 und 999999 sein")
            
            # Prüfen ob neue ID bereits existiert
            if self._check_driver_id_exists(neue_id):
                raise ValueError(f"Driver ID {neue_id} wird bereits verwendet")
            
            # Duplikat-Prüfung (ausschließlich aktueller Mitarbeiter)
            if "email" in data and data["email"]:
                if self._check_email_exists(data["email"], exclude_driver_id=alte_id):
                    raise ValueError("E-Mail-Adresse wird bereits von einem anderen Mitarbeiter verwendet")
            
            if "driver_license_number" in data and data["driver_license_number"]:
                if self._check_license_number_exists(data["driver_license_number"], exclude_driver_id=alte_id):
                    raise ValueError("Führerscheinnummer wird bereits von einem anderen Mitarbeiter verwendet")
            
            # Daten sanitieren
            sanitized_data = {
                "driver_license_number": self._sanitize_input(data["driver_license_number"]),
                "first_name": self._sanitize_input(data["first_name"]),
                "last_name": self._sanitize_input(data["last_name"]),
                "phone": self._sanitize_input(data.get("phone", "")),
                "email": self._sanitize_input(data.get("email", "")),
                "hire_date": self._sanitize_input(data.get("hire_date", "")),
                "status": self._sanitize_input(data.get("status", "active"))
            }
            
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE drivers
                    SET driver_id = ?, driver_license_number = ?, first_name = ?, last_name = ?, phone = ?, email = ?, hire_date = ?, status = ?
                    WHERE driver_id = ?
                """, (
                    neue_id,
                    sanitized_data["driver_license_number"],
                    sanitized_data["first_name"],
                    sanitized_data["last_name"],
                    sanitized_data["phone"],
                    sanitized_data["email"],
                    sanitized_data["hire_date"],
                    sanitized_data["status"],
                    alte_id
                ))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Mitarbeiter mit ID {alte_id} nicht gefunden")
                
                logger.info(f"Mitarbeiter {alte_id} → {neue_id} erfolgreich aktualisiert")
                return True
                
        except Exception as e:
            self._handle_database_error("update_mitarbeiter_id_and_data", e) 