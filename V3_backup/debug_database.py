#!/usr/bin/env python3
"""
Debug-Script für die Datenbank
Überprüft die drivers Tabelle und zeigt alle vorhandenen Daten an
"""

import sqlite3
import os
from db_manager import DBManager

def debug_database():
    """Debug-Funktion für die Datenbank"""
    print("🔍 Debug: Datenbank überprüfen")
    print("=" * 50)
    
    # Datenbankpfad
    db_path = "SQL/database.db"
    print(f"📁 Datenbankpfad: {db_path}")
    print(f"📁 Datei existiert: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Datenbankdatei existiert nicht!")
        return
    
    try:
        # Direkte SQLite-Verbindung
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tabellen auflisten
        print("\n📋 Verfügbare Tabellen:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        # drivers Tabelle Schema
        print("\n📋 drivers Tabelle Schema:")
        cursor.execute("PRAGMA table_info(drivers);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Anzahl Einträge in drivers
        print("\n📊 Anzahl Einträge in drivers:")
        cursor.execute("SELECT COUNT(*) FROM drivers;")
        count = cursor.fetchone()[0]
        print(f"  - {count} Einträge")
        
        # Alle Einträge anzeigen
        if count > 0:
            print("\n📋 Alle Einträge in drivers:")
            cursor.execute("""
                SELECT driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status
                FROM drivers
                ORDER BY last_name, first_name
            """)
            rows = cursor.fetchall()
            
            for i, row in enumerate(rows, 1):
                print(f"  {i}. ID: {row[0]}, Name: {row[2]} {row[3]}, Telefon: {row[4]}, Status: {row[7]}")
        else:
            print("  ⚠️  Keine Einträge in der drivers Tabelle!")
            
            # Testdaten einfügen
            print("\n🧪 Testdaten einfügen...")
            test_data = [
                ("DL001", "Max", "Mustermann", "+43 123 456 789", "max@example.com", "2024-01-01", "active"),
                ("DL002", "Anna", "Schmidt", "+43 987 654 321", "anna@example.com", "2024-02-01", "active"),
                ("DL003", "Peter", "Müller", "+43 555 123 456", "peter@example.com", "2024-03-01", "suspended"),
            ]
            
            for data in test_data:
                cursor.execute("""
                    INSERT INTO drivers (driver_license_number, first_name, last_name, phone, email, hire_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
            
            conn.commit()
            print("✅ Testdaten eingefügt!")
            
            # Erneut alle Einträge anzeigen
            cursor.execute("SELECT COUNT(*) FROM drivers;")
            count = cursor.fetchone()[0]
            print(f"📊 Neue Anzahl: {count} Einträge")
            
            cursor.execute("""
                SELECT driver_id, driver_license_number, first_name, last_name, phone, email, hire_date, status
                FROM drivers
                ORDER BY last_name, first_name
            """)
            rows = cursor.fetchall()
            
            for i, row in enumerate(rows, 1):
                print(f"  {i}. ID: {row[0]}, Name: {row[2]} {row[3]}, Telefon: {row[4]}, Status: {row[7]}")
        
        # DBManager Test
        print("\n🔧 DBManager Test:")
        db_manager = DBManager()
        mitarbeiter = db_manager.get_all_mitarbeiter()
        print(f"  - DBManager.get_all_mitarbeiter(): {len(mitarbeiter)} Einträge")
        
        if mitarbeiter:
            print("  - Erste 3 Einträge:")
            for i, row in enumerate(mitarbeiter[:3], 1):
                print(f"    {i}. {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database() 