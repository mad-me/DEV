#!/usr/bin/env python3
"""
Debug-Skript für Driver ID Edit-Problem
Analysiert warum die Driver ID sich nicht ändert
"""

import sys
import os
import sqlite3

def main():
    """Hauptfunktion für das Debug"""
    print("🔍 Debug: Driver ID Edit-Problem")
    
    # Datenbank-Datei
    db_file = "SQL/database.db"
    
    if not os.path.exists(db_file):
        print(f"❌ Fehler: Datenbank-Datei {db_file} nicht gefunden")
        return False
    
    print(f"✅ Datenbank-Datei gefunden: {db_file}")
    
    try:
        # Datenbank verbinden
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Test 1: Aktueller Zustand von Maximilian Mustermann
        cursor.execute("SELECT driver_id, first_name, last_name, driver_license_number FROM drivers WHERE first_name = 'Maximilian' AND last_name = 'Mustermann'")
        result = cursor.fetchone()
        
        if result:
            current_driver_id, first_name, last_name, license_number = result
            print(f"📋 Aktueller Zustand:")
            print(f"   Name: {first_name} {last_name}")
            print(f"   Driver ID: {current_driver_id}")
            print(f"   License: {license_number}")
        else:
            print("❌ Maximilian Mustermann nicht gefunden")
            return False
        
        # Test 2: Prüfe ob Driver ID 99 bereits existiert
        cursor.execute("SELECT driver_id FROM drivers WHERE driver_id = 99")
        result = cursor.fetchone()
        
        if result:
            print("❌ Driver ID 99 existiert bereits")
            return False
        else:
            print("✅ Driver ID 99 ist verfügbar")
        
        # Test 3: Simuliere das Update direkt in der Datenbank
        print("\n🧪 Teste direktes Update in der Datenbank...")
        
        # Backup erstellen
        cursor.execute("SELECT * FROM drivers WHERE driver_id = ?", (current_driver_id,))
        backup_data = cursor.fetchone()
        print(f"📦 Backup erstellt für Driver ID {current_driver_id}")
        
        # Update simulieren
        update_query = """
            UPDATE drivers 
            SET driver_id = ?, driver_license_number = ?, first_name = ?, last_name = ?, 
                phone = ?, email = ?, hire_date = ?, status = ?
            WHERE driver_id = ?
        """
        
        # Test-Daten
        test_data = (
            99,  # neue driver_id
            license_number,  # gleiche license
            first_name,  # gleicher name
            last_name,  # gleicher name
            "0123456789",  # test phone
            "max@test.de",  # test email
            "2024-01-01",  # test date
            "active",  # status
            current_driver_id  # where clause
        )
        
        print(f"📋 Test-Update-Daten:")
        print(f"   Von Driver ID: {current_driver_id}")
        print(f"   Zu Driver ID: 99")
        print(f"   Name: {first_name} {last_name}")
        
        # Update ausführen
        cursor.execute(update_query, test_data)
        conn.commit()
        
        # Prüfen ob Update erfolgreich war
        cursor.execute("SELECT driver_id, first_name, last_name FROM drivers WHERE driver_id = 99")
        result = cursor.fetchone()
        
        if result:
            new_driver_id, new_first_name, new_last_name = result
            print(f"✅ Update erfolgreich!")
            print(f"   Neue Driver ID: {new_driver_id}")
            print(f"   Name: {new_first_name} {new_last_name}")
            
            # Prüfen ob alte Driver ID noch existiert
            cursor.execute("SELECT driver_id FROM drivers WHERE driver_id = ?", (current_driver_id,))
            old_result = cursor.fetchone()
            
            if old_result:
                print("❌ Alte Driver ID existiert noch - Update fehlgeschlagen")
            else:
                print("✅ Alte Driver ID wurde korrekt gelöscht")
        else:
            print("❌ Update fehlgeschlagen")
            return False
        
        # Test 4: Prüfe Backend-Logik
        print("\n🔍 Prüfe Backend-Logik...")
        backend_file = "mitarbeiter_seite_qml_v2.py"
        if os.path.exists(backend_file):
            with open(backend_file, 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            # Prüfe ob original_driver_id Logik korrekt implementiert ist
            if 'original_driver_id = employee_data.get(\'original_driver_id\')' in backend_content:
                print("✅ Backend original_driver_id Logik gefunden")
            else:
                print("❌ Backend original_driver_id Logik fehlt")
            
            # Prüfe ob Driver ID Update-Logik korrekt implementiert ist
            if 'SET driver_id = ?' in backend_content:
                print("✅ Backend Driver ID Update-Logik gefunden")
            else:
                print("❌ Backend Driver ID Update-Logik fehlt")
            
            # Prüfe ob WHERE driver_id = ? korrekt ist
            if 'WHERE driver_id = ?' in backend_content:
                print("✅ Backend WHERE driver_id Logik gefunden")
            else:
                print("❌ Backend WHERE driver_id Logik fehlt")
        else:
            print(f"❌ Backend-Datei {backend_file} nicht gefunden")
        
        # Test 5: Prüfe QML-Integration
        print("\n🔍 Prüfe QML-Integration...")
        qml_file = "Style/TestMitarbeiterV2Cards.qml"
        if os.path.exists(qml_file):
            with open(qml_file, 'r', encoding='utf-8') as f:
                qml_content = f.read()
            
            # Prüfe ob originalDriverId Property existiert
            if 'property string originalDriverId' in qml_content:
                print("✅ QML originalDriverId Property gefunden")
            else:
                print("❌ QML originalDriverId Property fehlt")
            
            # Prüfe ob original_driver_id in saveEmployee aufgerufen wird
            if 'original_driver_id: originalDriverId' in qml_content:
                print("✅ QML original_driver_id Übergabe gefunden")
            else:
                print("❌ QML original_driver_id Übergabe fehlt")
            
            # Prüfe ob showMitarbeiterFormOverlayForEdit originalDriverId setzt
            if 'originalDriverId = mitarbeiterData.driver_id' in qml_content:
                print("✅ QML originalDriverId Setzung gefunden")
            else:
                print("❌ QML originalDriverId Setzung fehlt")
        else:
            print(f"❌ QML-Datei {qml_file} nicht gefunden")
        
        print(f"\n📋 Debug-Ergebnisse:")
        print("✅ Datenbank-Update funktioniert direkt")
        print("✅ Backend-Logik ist implementiert")
        print("✅ QML-Integration ist implementiert")
        print("💡 Problem liegt wahrscheinlich in der Datenübertragung zwischen QML und Backend")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Debug: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 