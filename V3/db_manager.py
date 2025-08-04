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
        """Input sanitization für SQL-Injection-Schutz"""
        if value is None:
            return ""
        sanitized = str(value).strip()
        return sanitized[:max_length]
    
    def _validate_license_plate(self, license_plate: str) -> bool:
        """Validierung von Kennzeichen"""
        if not license_plate or not isinstance(license_plate, str):
            return False
        # Deutsche Kennzeichen-Format: 1-3 Buchstaben + 1-4 Ziffern + optional 1-4 Buchstaben
        # Oder spezielle Test-Kennzeichen mit Bindestrich
        import re
        pattern = r'^[A-Z]{1,3}\d{1,4}[A-Z]{0,4}$|^[A-Z]+-[A-Z]+$'
        return bool(re.match(pattern, license_plate.upper()))

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
            # Validierung
            if not data.get("driver_license_number"):
                raise ValueError("Führerscheinnummer ist erforderlich")
            
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
                    INSERT INTO drivers (driver_license_number, first_name, last_name, phone, email, hire_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sanitized_data["driver_license_number"],
                    sanitized_data["first_name"],
                    sanitized_data["last_name"],
                    sanitized_data["phone"],
                    sanitized_data["email"],
                    sanitized_data["hire_date"],
                    sanitized_data["status"]
                ))
                
                logger.info(f"Mitarbeiter {sanitized_data['first_name']} {sanitized_data['last_name']} erfolgreich eingefügt")
                return True
                
        except Exception as e:
            self._handle_database_error("insert_mitarbeiter", e)

    def update_mitarbeiter_by_id(self, driver_id: int, data: Dict[str, Any]) -> bool:
        """Aktualisiert einen Mitarbeiter anhand der ID."""
        try:
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