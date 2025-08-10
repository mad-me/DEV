#!/usr/bin/env python3
"""
Test-Skript für direkten saveEmployee Aufruf
Testet die saveEmployee Methode direkt ohne QML
"""

import sys
import os

# Arbeitsverzeichnis setzen
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import der MitarbeiterSeiteQMLV2
from mitarbeiter_seite_qml_v2 import MitarbeiterSeiteQMLV2

def main():
    """Hauptfunktion für den Test"""
    print("🚀 Starte direkten saveEmployee Test")
    
    try:
        # Backend-Instanz erstellen
        backend = MitarbeiterSeiteQMLV2()
        print("✅ Backend-Instanz erstellt")
        
        # Test-Daten für Driver ID Update (99 → 100)
        test_data = {
            'driver_id': '100',
            'original_driver_id': '99',
            'driver_license_number': 'XXX443',
            'first_name': 'Maximilian',
            'last_name': 'Mustermann',
            'phone': '0123456789',
            'email': 'max@test.de',
            'hire_date': '2024-01-01',
            'status': 'active'
        }
        
        # Debug: Prüfe die Daten vor dem Aufruf
        print(f"🔍 DEBUG: Test-Daten vor Aufruf:")
        for key, value in test_data.items():
            print(f"   {key}: {value} (Type: {type(value)})")
        
        # Debug: Prüfe die Bedingung
        print(f"🔍 DEBUG: Test der Bedingung:")
        print(f"   original_driver_id = {test_data['original_driver_id']}")
        print(f"   driver_id = {test_data['driver_id']}")
        print(f"   original_driver_id != driver_id = {test_data['original_driver_id'] != test_data['driver_id']}")
        print(f"   Bedingung: {test_data['original_driver_id'] and test_data['original_driver_id'] != test_data['driver_id']}")
        
        print(f"📋 Test-Daten:")
        print(f"   Driver ID: {test_data['driver_id']}")
        print(f"   Original Driver ID: {test_data['original_driver_id']}")
        print(f"   Name: {test_data['first_name']} {test_data['last_name']}")
        
        # saveEmployee direkt aufrufen
        print("\n🔍 Rufe saveEmployee auf...")
        
        # Debug: Prüfe ob die Methode existiert
        if hasattr(backend, 'saveEmployee'):
            print("✅ saveEmployee Methode existiert")
        else:
            print("❌ saveEmployee Methode existiert nicht")
            return False
        
        # Debug: Prüfe die Methode direkt
        print(f"🔍 DEBUG: Methode-Typ: {type(backend.saveEmployee)}")
        
        # Aufruf mit Exception-Handling
        try:
            backend.saveEmployee(test_data)
            print("✅ saveEmployee Aufruf erfolgreich")
        except Exception as e:
            print(f"❌ Exception beim saveEmployee Aufruf: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ saveEmployee Aufruf abgeschlossen")
        print("💡 Prüfe die Debug-Ausgaben oben")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 