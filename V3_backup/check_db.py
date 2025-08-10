import sqlite3

try:
    conn = sqlite3.connect('SQL/database.db')
    cursor = conn.cursor()
    
    # Alle Tabellen auflisten
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Verfügbare Tabellen:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Prüfen ob vehicles-Tabelle existiert
    if ('vehicles',) in tables:
        print("\nvehicles-Tabelle gefunden!")
        cursor.execute("SELECT * FROM vehicles LIMIT 3")
        vehicles = cursor.fetchall()
        print(f"Anzahl Fahrzeuge: {len(vehicles)}")
        if vehicles:
            print("Erste 3 Fahrzeuge:")
            for vehicle in vehicles:
                print(f"  {vehicle}")
    else:
        print("\nvehicles-Tabelle NICHT gefunden!")
    
    # Prüfen ob drivers-Tabelle existiert
    if ('drivers',) in tables:
        print("\ndrivers-Tabelle gefunden!")
        cursor.execute("SELECT * FROM drivers LIMIT 3")
        drivers = cursor.fetchall()
        print(f"Anzahl Fahrer: {len(drivers)}")
        if drivers:
            print("Erste 3 Fahrer:")
            for driver in drivers:
                print(f"  {driver}")
    else:
        print("\ndrivers-Tabelle NICHT gefunden!")
    
    conn.close()
    
except Exception as e:
    print(f"Fehler: {e}")
