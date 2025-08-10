"""
Zentrale Datenbankverwaltung für optimiertes Datenmanagement
"""
import sqlite3
import pandas as pd
import threading
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import time

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Konfiguration für Datenbankverbindungen"""
    main_db: str = "SQL/database.db"
    uber_db: str = "SQL/uber.sqlite"
    bolt_db: str = "SQL/bolt.sqlite"
    taxi_db: str = "SQL/40100.sqlite"
    taxi2_db: str = "SQL/31300.sqlite"  # Zweigstelle
    salaries_db: str = "SQL/salaries.db"
    revenue_db: str = "SQL/revenue.db"
    revenue1_db: str = "SQL/revenue1.db"  # Erweiterte Revenue
    running_costs_db: str = "SQL/running_costs.db"  # Betriebskosten
    funk_db: str = "SQL/funk.db"  # Funk-Daten
    report_db: str = "SQL/report.db"  # Report-Daten
    ekk_db: str = "SQL/EKK.db"  # EKK-Daten
    max_connections: int = 10
    connection_timeout: int = 30
    cache_timeout: int = 300  # 5 Minuten

class ConnectionPool:
    """Thread-sicheres Connection Pool für effiziente Datenbankverbindungen"""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._lock = threading.Lock()
        self._thread_local = threading.local()
        self._active_connections = 0
        
    def _create_connection(self) -> sqlite3.Connection:
        """Erstellt eine neue Datenbankverbindung"""
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        return conn
    
    @contextmanager
    def get_connection(self):
        """Thread-sicherer Context Manager für Datenbankverbindungen"""
        conn = None
        try:
            # Thread-lokale Verbindung verwenden
            if not hasattr(self._thread_local, 'connection'):
                with self._lock:
                    if self._active_connections < self.max_connections:
                        self._thread_local.connection = self._create_connection()
                        self._active_connections += 1
                    else:
                        # Fallback: Neue Verbindung für diesen Thread
                        self._thread_local.connection = self._create_connection()
            
            conn = self._thread_local.connection
            yield conn
        except Exception as e:
            logger.error(f"Datenbankfehler: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise
        finally:
            # Verbindung bleibt für den Thread bestehen
            pass
    
    def close_thread_connection(self):
        """Schließt die thread-lokale Verbindung"""
        if hasattr(self._thread_local, 'connection'):
            try:
                self._thread_local.connection.close()
                delattr(self._thread_local, 'connection')
                with self._lock:
                    self._active_connections = max(0, self._active_connections - 1)
            except:
                pass

class DataCache:
    """Intelligenter Cache für häufig verwendete Daten"""
    
    def __init__(self, timeout: int = 300):
        self._cache = {}
        self._timestamps = {}
        self._timeout = timeout
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Holt Daten aus dem Cache"""
        with self._lock:
            if key in self._cache:
                if time.time() - self._timestamps[key] < self._timeout:
                    return self._cache[key]
                else:
                    # Cache abgelaufen
                    del self._cache[key]
                    del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Speichert Daten im Cache"""
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def invalidate(self, pattern: str = None) -> None:
        """Invalidiert Cache-Einträge"""
        with self._lock:
            if pattern:
                keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            else:
                keys_to_remove = list(self._cache.keys())
            
            for key in keys_to_remove:
                del self._cache[key]
                del self._timestamps[key]
    
    def clear(self) -> None:
        """Leert den gesamten Cache"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()

class DataManager:
    """Zentrale Datenverwaltungsklasse"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self._pools = {}
        self._cache = DataCache(self.config.cache_timeout)
        self._lock = threading.Lock()
        
        # Initialisiere Connection Pools
        self._init_connection_pools()
    
    def _init_connection_pools(self):
        """Initialisiert Connection Pools für alle Datenbanken"""
        databases = {
            'main': self.config.main_db,
            'uber': self.config.uber_db,
            'bolt': self.config.bolt_db,
            'taxi': self.config.taxi_db,
            'taxi2': self.config.taxi2_db,  # Zweigstelle
            'salaries': self.config.salaries_db,
            'revenue': self.config.revenue_db,
            'revenue1': self.config.revenue1_db,  # Erweiterte Revenue
            'running_costs': self.config.running_costs_db,  # Betriebskosten
            'funk': self.config.funk_db,  # Funk-Daten
            'report': self.config.report_db,  # Report-Daten
            'ekk': self.config.ekk_db  # EKK-Daten
        }
        
        for name, path in databases.items():
            # Erstelle Verzeichnis falls nicht vorhanden
            db_path = Path(path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Erstelle leere Datenbankdatei falls nicht vorhanden
            if not db_path.exists():
                try:
                    # Erstelle leere SQLite-Datenbank
                    conn = sqlite3.connect(path)
                    conn.close()
                    logger.info(f"Neue Datenbank erstellt: {path}")
                except Exception as e:
                    logger.warning(f"Konnte Datenbank {path} nicht erstellen: {e}")
                    continue
            
            # Initialisiere Connection Pool
            try:
                self._pools[name] = ConnectionPool(path, self.config.max_connections)
                logger.info(f"Connection Pool für {name} initialisiert: {path}")
            except Exception as e:
                logger.warning(f"Connection Pool für {name} fehlgeschlagen: {e}")
        
        # Initialisiere alle Datenbanken
        self.initialize_all_databases()
    
    def initialize_all_databases(self):
        """Initialisiert alle Datenbanken mit erforderlichen Tabellen"""
        try:
            # Hauptdatenbank wird bereits durch DBManager initialisiert
            logger.info("✅ Hauptdatenbank bereits initialisiert")
            
            # Salaries-Datenbank initialisieren
            self._initialize_salaries_db()
            
            # Revenue-Datenbank initialisieren
            self._initialize_revenue_db()
            
            # Running Costs-Datenbank initialisieren
            self._initialize_running_costs_db()
            
            # Report-Datenbank initialisieren
            self._initialize_report_db()
            
            logger.info("✅ Alle Datenbanken erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Datenbank-Initialisierung: {e}")
            raise
    
    def _initialize_salaries_db(self):
        """Initialisiert die Salaries-Datenbank"""
        try:
            if 'salaries' in self._pools:
                with self.get_connection('salaries') as conn:
                    cursor = conn.cursor()
                    
                    # Beispiel-Tabelle für Gehälter (wird dynamisch erstellt)
                    # Die Tabellen werden normalerweise beim Import erstellt
                    logger.info("✅ Salaries-Datenbank bereit")
                    
        except Exception as e:
            logger.warning(f"Salaries-Datenbank-Initialisierung: {e}")
    
    def _initialize_revenue_db(self):
        """Initialisiert die Revenue-Datenbank"""
        try:
            if 'revenue' in self._pools:
                with self.get_connection('revenue') as conn:
                    cursor = conn.cursor()
                    
                    # Beispiel-Tabelle für Revenue (wird dynamisch erstellt)
                    # Die Tabellen werden normalerweise beim Import erstellt
                    logger.info("✅ Revenue-Datenbank bereit")
                    
        except Exception as e:
            logger.warning(f"Revenue-Datenbank-Initialisierung: {e}")
    
    def _initialize_running_costs_db(self):
        """Initialisiert die Running Costs-Datenbank"""
        try:
            if 'running_costs' in self._pools:
                with self.get_connection('running_costs') as conn:
                    cursor = conn.cursor()
                    
                    # Beispiel-Tabelle für Betriebskosten (wird dynamisch erstellt)
                    # Die Tabellen werden normalerweise beim Import erstellt
                    logger.info("✅ Running Costs-Datenbank bereit")
                    
        except Exception as e:
            logger.warning(f"Running Costs-Datenbank-Initialisierung: {e}")
    
    def _initialize_report_db(self):
        """Initialisiert die Report-Datenbank"""
        try:
            if 'report' in self._pools:
                with self.get_connection('report') as conn:
                    cursor = conn.cursor()
                    
                    # Expenses Tabelle
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS expenses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date DATE NOT NULL,
                            description TEXT,
                            amount DECIMAL(10,2) NOT NULL,
                            category TEXT,
                            vehicle TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Revenue Tabelle
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS revenue (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date DATE NOT NULL,
                            platform TEXT,
                            amount DECIMAL(10,2) NOT NULL,
                            vehicle TEXT,
                            driver TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    logger.info("✅ Report-Datenbank initialisiert")
                    
        except Exception as e:
            logger.warning(f"Report-Datenbank-Initialisierung: {e}")
    
    def get_connection(self, db_name: str = 'main'):
        """Holt eine Datenbankverbindung aus dem Pool"""
        if db_name not in self._pools:
            raise ValueError(f"Unbekannte Datenbank: {db_name}")
        return self._pools[db_name].get_connection()
    
    # === FAHRER-MANAGEMENT ===
    
    def get_fahrer_list(self, force_reload: bool = False) -> List[str]:
        """Lädt die Fahrerliste mit Caching"""
        cache_key = "fahrer_list"
        
        if not force_reload:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            with self.get_connection('main') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT first_name, last_name, status 
                    FROM drivers 
                    WHERE status = 'active' 
                    ORDER BY last_name, first_name
                """)
                rows = cursor.fetchall()
                
                fahrer_list = []
                for first_name, last_name, status in rows:
                    if status and status.lower() == 'active':
                        label = f"{first_name or ''} {last_name or ''}".strip()
                        if label:
                            fahrer_list.append(label)
                
                self._cache.set(cache_key, fahrer_list)
                logger.info(f"Fahrerliste geladen: {len(fahrer_list)} aktive Fahrer")
                return fahrer_list
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Fahrerliste: {e}")
            return []
    
    def get_fahrzeug_list(self, force_reload: bool = False) -> List[str]:
        """Lädt die Fahrzeugliste mit Caching"""
        cache_key = "fahrzeug_list"
        
        if not force_reload:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            with self.get_connection('main') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT license_plate, rfrnc 
                    FROM vehicles 
                    WHERE license_plate IS NOT NULL 
                    ORDER BY license_plate
                """)
                rows = cursor.fetchall()
                
                fahrzeug_list = [row[0] for row in rows if row[0]]
                
                self._cache.set(cache_key, fahrzeug_list)
                logger.info(f"Fahrzeugliste geladen: {len(fahrzeug_list)} Fahrzeuge")
                return fahrzeug_list
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Fahrzeugliste: {e}")
            return []
    
    def get_kalenderwochen(self, force_reload: bool = False) -> List[str]:
        """Lädt die Kalenderwochen mit Caching"""
        cache_key = "kalenderwochen"
        
        if not force_reload:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            with self.get_connection('taxi') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'report_KW%'
                    ORDER BY name DESC
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                kw_list = sorted([
                    t.replace("report_KW", "") for t in tables
                ], reverse=True)
                
                self._cache.set(cache_key, kw_list)
                logger.info(f"Kalenderwochen geladen: {len(kw_list)} Wochen")
                return kw_list
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Kalenderwochen: {e}")
            return []
    
    # === FAHRER-MATCHING ===
    
    def get_driver_id(self, fahrer_name: str) -> Optional[int]:
        """Findet die Fahrer-ID anhand des Namens"""
        cache_key = f"driver_id_{fahrer_name}"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            with self.get_connection('main') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT driver_id FROM drivers 
                    WHERE first_name || ' ' || last_name = ? AND status = 'active'
                """, (fahrer_name,))
                result = cursor.fetchone()
                
                driver_id = result[0] if result else None
                if driver_id:
                    self._cache.set(cache_key, driver_id)
                
                return driver_id
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Fahrer-ID für {fahrer_name}: {e}")
            return None
    
    # === PLATTFORM-DATEN ===
    
    def get_platform_data(self, platform: str, kw: str) -> pd.DataFrame:
        """Lädt Plattformdaten mit Caching"""
        cache_key = f"platform_data_{platform}_{kw}"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            db_mapping = {
                'uber': 'uber',
                'bolt': 'bolt', 
                'taxi': 'taxi',
                'taxi2': 'taxi2',  # Zweigstelle
                '40100': 'taxi',
                '31300': 'taxi2'  # Neue Zweigstelle
            }
            
            db_name = db_mapping.get(platform)
            if not db_name or db_name not in self._pools:
                logger.error(f"Unbekannte Plattform: {platform}")
                return pd.DataFrame()
            
            table_name = f"report_KW{kw}"
            
            with self.get_connection(db_name) as conn:
                # Prüfe ob Tabelle existiert
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name = ?
                """, (table_name,))
                
                if not cursor.fetchone():
                    logger.warning(f"Tabelle {table_name} nicht gefunden")
                    return pd.DataFrame()
                
                # Lade Daten
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                
                self._cache.set(cache_key, df)
                logger.info(f"Plattformdaten geladen: {platform} KW{kw} - {len(df)} Zeilen")
                return df
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Plattformdaten {platform} KW{kw}: {e}")
            return pd.DataFrame()
    
    # === NEUE DATENBANK-METHODEN ===
    
    def get_revenue_data(self, vehicle: str = None) -> pd.DataFrame:
        """Lädt Revenue-Daten"""
        cache_key = f"revenue_data_{vehicle or 'all'}"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            with self.get_connection('revenue') as conn:
                if vehicle:
                    df = pd.read_sql_query(f'SELECT * FROM "{vehicle}"', conn)
                else:
                    # Alle Revenue-Tabellen laden
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    all_data = []
                    for table in tables:
                        try:
                            df_part = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
                            df_part['vehicle'] = table
                            all_data.append(df_part)
                        except Exception as e:
                            logger.warning(f"Fehler beim Laden von {table}: {e}")
                    
                    df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
                
                self._cache.set(cache_key, df)
                logger.info(f"Revenue-Daten geladen: {len(df)} Zeilen")
                return df
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Revenue-Daten: {e}")
            return pd.DataFrame()
    
    def get_running_costs_data(self, vehicle: str = None) -> pd.DataFrame:
        """Lädt Betriebskosten-Daten"""
        cache_key = f"running_costs_data_{vehicle or 'all'}"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            with self.get_connection('running_costs') as conn:
                if vehicle:
                    df = pd.read_sql_query(f'SELECT * FROM "{vehicle}"', conn)
                else:
                    # Alle Betriebskosten-Tabellen laden
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    all_data = []
                    for table in tables:
                        try:
                            df_part = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
                            df_part['vehicle'] = table
                            all_data.append(df_part)
                        except Exception as e:
                            logger.warning(f"Fehler beim Laden von {table}: {e}")
                    
                    df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
                
                self._cache.set(cache_key, df)
                logger.info(f"Betriebskosten-Daten geladen: {len(df)} Zeilen")
                return df
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Betriebskosten-Daten: {e}")
            return pd.DataFrame()
    
    def get_salary_data(self, month: str = None) -> pd.DataFrame:
        """Lädt Gehalts-Daten"""
        cache_key = f"salary_data_{month or 'all'}"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            with self.get_connection('salaries') as conn:
                if month:
                    df = pd.read_sql_query(f'SELECT * FROM "{month}"', conn)
                else:
                    # Alle Gehalts-Tabellen laden
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    all_data = []
                    for table in tables:
                        try:
                            df_part = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
                            df_part['month'] = table
                            all_data.append(df_part)
                        except Exception as e:
                            logger.warning(f"Fehler beim Laden von {table}: {e}")
                    
                    df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
                
                self._cache.set(cache_key, df)
                logger.info(f"Gehalts-Daten geladen: {len(df)} Zeilen")
                return df
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Gehalts-Daten: {e}")
            return pd.DataFrame()
    
    def get_funk_data(self, month: str = None) -> pd.DataFrame:
        """Lädt Funk-Daten"""
        cache_key = f"funk_data_{month or 'all'}"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            with self.get_connection('funk') as conn:
                if month:
                    df = pd.read_sql_query(f'SELECT * FROM "{month}"', conn)
                else:
                    # Alle Funk-Tabellen laden
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    all_data = []
                    for table in tables:
                        try:
                            df_part = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
                            df_part['month'] = table
                            all_data.append(df_part)
                        except Exception as e:
                            logger.warning(f"Fehler beim Laden von {table}: {e}")
                    
                    df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
                
                self._cache.set(cache_key, df)
                logger.info(f"Funk-Daten geladen: {len(df)} Zeilen")
                return df
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Funk-Daten: {e}")
            return pd.DataFrame()
    
    def get_ekk_data(self) -> pd.DataFrame:
        """Lädt EKK-Daten"""
        cache_key = "ekk_data"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            with self.get_connection('ekk') as conn:
                # Beide EKK-Tabellen laden
                uber_df = pd.read_sql_query('SELECT * FROM umsatz_uber', conn)
                bolt_df = pd.read_sql_query('SELECT * FROM umsatz_bolt', conn)
                
                uber_df['platform'] = 'uber'
                bolt_df['platform'] = 'bolt'
                
                df = pd.concat([uber_df, bolt_df], ignore_index=True)
                
                self._cache.set(cache_key, df)
                logger.info(f"EKK-Daten geladen: {len(df)} Zeilen")
                return df
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der EKK-Daten: {e}")
            return pd.DataFrame()
    
    def get_report_data(self) -> Dict:
        """Lädt Report-Daten"""
        cache_key = "report_data"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            with self.get_connection('report') as conn:
                expenses_df = pd.read_sql_query('SELECT * FROM expenses', conn)
                revenue_df = pd.read_sql_query('SELECT * FROM revenue', conn)
                
                report_data = {
                    'expenses': expenses_df,
                    'revenue': revenue_df
                }
                
                self._cache.set(cache_key, report_data)
                logger.info(f"Report-Daten geladen: {len(expenses_df)} Expenses, {len(revenue_df)} Revenue")
                return report_data
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Report-Daten: {e}")
            return {'expenses': pd.DataFrame(), 'revenue': pd.DataFrame()}
    
    # === KONFIGURATION ===
    
    def save_overlay_config(self, driver_id: int, config: Dict) -> bool:
        """Speichert Overlay-Konfiguration"""
        try:
            with self.get_connection('main') as conn:
                cursor = conn.cursor()
                
                # Erstelle Tabelle falls nicht vorhanden
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
                
                config_json = json.dumps(config)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO overlay_configs 
                    (driver_id, config_json, updated_at) 
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (driver_id, config_json))
                
                conn.commit()
                
                # Cache invalidieren
                self._cache.invalidate("overlay_config")
                logger.info(f"Overlay-Konfiguration für Fahrer {driver_id} gespeichert")
                return True
                
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Overlay-Konfiguration: {e}")
            return False
    
    def load_overlay_config(self, driver_id: int) -> Optional[Dict]:
        """Lädt Overlay-Konfiguration"""
        cache_key = f"overlay_config_{driver_id}"
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            with self.get_connection('main') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT config_json FROM overlay_configs 
                    WHERE driver_id = ?
                """, (driver_id,))
                
                result = cursor.fetchone()
                if result:
                    config = json.loads(result[0])
                    self._cache.set(cache_key, config)
                    logger.info(f"Overlay-Konfiguration für Fahrer {driver_id} geladen")
                    return config
                
                return None
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der Overlay-Konfiguration: {e}")
            return None
    
    # === CACHE-MANAGEMENT ===
    
    def invalidate_cache(self, pattern: str = None) -> None:
        """Invalidiert Cache-Einträge"""
        self._cache.invalidate(pattern)
        logger.info(f"Cache invalidiert: {pattern or 'alle'}")
    
    def clear_cache(self) -> None:
        """Leert den gesamten Cache"""
        self._cache.clear()
        logger.info("Cache geleert")
    
    # === PERFORMANCE-MONITORING ===
    
    def get_performance_stats(self) -> Dict:
        """Gibt Performance-Statistiken zurück"""
        stats = {
            'cache_size': len(self._cache._cache),
            'active_connections': sum(pool._active_connections for pool in self._pools.values()),
            'total_connections': sum(len(pool._connections) + pool._active_connections for pool in self._pools.values()),
            'databases': list(self._pools.keys())
        }
        return stats

# Globale Instanz
_data_manager = None

def get_data_manager() -> DataManager:
    """Gibt die globale DataManager-Instanz zurück"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager 