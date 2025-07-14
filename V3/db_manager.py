import sqlite3
import pandas as pd


class DBManager:
    def __init__(self, db_path="SQL/database.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # 🚗 Fahrzeuge

    def get_all_fahrzeuge(self):
        """Gibt alle Fahrzeuge als Liste von Tupeln zurück"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT license_plate, rfrnc, model, year, insurance, credit
                FROM vehicles
                ORDER BY license_plate
            """)
            return cursor.fetchall()

    def get_fahrzeug_by_plate(self, license_plate):
        """Gibt ein Fahrzeug als Tupel anhand des Kennzeichens zurück"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT license_plate, brand, model, year, insurance, credit
                FROM vehicles
                WHERE license_plate = ?
            """, (license_plate,))
            return cursor.fetchone()

    def insert_fahrzeug(self, data):
        """Fügt ein neues Fahrzeug ein. data ist ein dict mit passenden Keys."""
        # Korrigiere Dezimaltrennzeichen und Typen
        def fix_num(val):
            if isinstance(val, str):
                val = val.replace(",", ".")
            try:
                return float(val)
            except Exception:
                return val
        insurance = fix_num(data.get("insurance", ""))
        credit = fix_num(data.get("credit", ""))
        year = data.get("year", None)
        try:
            year = int(year)
        except Exception:
            year = None
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vehicles (license_plate, rfrnc, model, year, insurance, credit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["license_plate"],
                data.get("rfrnc", ""),
                data.get("model", ""),
                year,
                insurance,
                credit
            ))
            conn.commit()

    def update_fahrzeug_by_plate(self, license_plate, data):
        """Aktualisiert ein Fahrzeug anhand des Kennzeichens"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE vehicles
                SET rfrnc = ?, model = ?, year = ?, insurance = ?, credit = ?
                WHERE license_plate = ?
            """, (
                data.get("rfrnc", ""),
                data.get("model", ""),
                int(data["year"]) if data.get("year") else None,
                float(str(data.get("insurance", "")).replace(",", ".")) if data.get("insurance") else None,
                float(str(data.get("credit", "")).replace(",", ".")) if data.get("credit") else None,
                license_plate
            ))
            conn.commit()

    def delete_fahrzeug_by_plate(self, license_plate):
        """Löscht ein Fahrzeug anhand des Kennzeichens"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vehicles WHERE license_plate = ?", (license_plate,))
            conn.commit()

    def get_dataframe_from_table(self, table_name: str) -> pd.DataFrame:
        """
        Liest eine komplette Tabelle aus der Datenbank und gibt sie als
        einen pandas DataFrame zurück.
        """
        with self._connect() as conn:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, conn)
            return df

    def execute_query(self, query, params=None):
        """
        Führt eine beliebige SQL-Abfrage aus.
        Ideal für INSERT, UPDATE, DELETE.
        Gibt die lastrowid für INSERTs zurück.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid

    def fetch_all(self, query, params=None):
        """Führt eine SELECT-Abfrage aus und gibt alle Ergebnisse zurück."""
        with self._connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def generic_insert(self, table_name, data):
        """
        Fügt einen neuen Datensatz in eine beliebige Tabelle ein.
        :param table_name: Name der Tabelle.
        :param data: Ein Dictionary, bei dem die Schlüssel die Spaltennamen
                     und die Werte die einzufügenden Daten sind.
        """
        if not data:
            return None

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            last_row_id = self.execute_query(query, list(data.values()))
            return last_row_id
        except sqlite3.Error as e:
            print(f"Database error during generic insert into '{table_name}': {e}")
            return None

    def get_all_records(self, table_name, columns='*'):
        query = f"SELECT {columns} FROM {table_name}"
        return self.fetch_all(query)

    def get_all_mitarbeiter(self):
        """Gibt alle Mitarbeiter als Liste von Tupeln zurück"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status
                FROM drivers
                ORDER BY last_name, first_name
            """)
            return cursor.fetchall()

    def insert_mitarbeiter(self, data):
        """Fügt einen neuen Mitarbeiter ein. data ist ein dict mit passenden Keys."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO drivers (driver_license_number, first_name, last_name, phone, email, hire_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["driver_license_number"],
                data["first_name"],
                data["last_name"],
                data.get("phone", ""),
                data.get("email", ""),
                data.get("hire_date", None),
                data.get("status", "active")
            ))
            conn.commit()

    def update_mitarbeiter_by_id(self, driver_id, data):
        """Aktualisiert einen Mitarbeiter anhand der ID."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE drivers
                SET driver_license_number = ?, first_name = ?, last_name = ?, phone = ?, email = ?, hire_date = ?, status = ?
                WHERE driver_id = ?
            """, (
                data["driver_license_number"],
                data["first_name"],
                data["last_name"],
                data.get("phone", ""),
                data.get("email", ""),
                data.get("hire_date", None),
                data.get("status", "active"),
                driver_id
            ))
            conn.commit() 