#!/usr/bin/env python3
"""
Bolt API Integration
Integration der Bolt API mit dem bestehenden Download-System
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from bolt_api_manager import BoltAPIManager

class BoltAPIIntegration:
    def __init__(self):
        self.api_manager = BoltAPIManager()
        self.download_dir = Path("download/data/raw")
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_weekly_report(self, kw: int):
        """Lädt Wochenbericht für Kalenderwoche"""
        # Berechne Datum für Kalenderwoche
        year = datetime.now().year
        start_date = datetime.strptime(f"{year}-W{kw:02d}-1", "%Y-W%W-%w")
        end_date = start_date + timedelta(days=6)
        
        filename = f"Bolt_API_KW{kw:02d}.csv"
        save_path = self.download_dir / filename
        
        try:
            self.api_manager.download_csv_report(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                str(save_path)
            )
            print(f"✅ Wochenbericht KW{kw} erfolgreich heruntergeladen")
            return str(save_path)
        except Exception as e:
            print(f"❌ Fehler beim Download: {e}")
            return None
    
    def get_fleet_summary(self):
        """Holt Fleet-Zusammenfassung"""
        try:
            fleet_data = self.api_manager.get_fleet_data()
            print("✅ Fleet-Daten erfolgreich abgerufen")
            return fleet_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Fleet-Daten: {e}")
            return None
    
    def get_driver_list(self):
        """Holt Fahrer-Liste"""
        try:
            driver_data = self.api_manager.get_driver_data()
            print("✅ Fahrer-Daten erfolgreich abgerufen")
            return driver_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Fahrer-Daten: {e}")
            return None
    
    def get_vehicle_list(self):
        """Holt Fahrzeug-Liste"""
        try:
            vehicle_data = self.api_manager.get_vehicle_data()
            print("✅ Fahrzeug-Daten erfolgreich abgerufen")
            return vehicle_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Fahrzeug-Daten: {e}")
            return None
    
    def test_api_connection(self):
        """Testet die API-Verbindung"""
        try:
            token = self.api_manager.get_valid_token()
            if token:
                print("✅ API-Verbindung funktioniert")
                print(f"✅ Token verfügbar: {token[:20]}...")
                return True
            else:
                print("❌ Kein gültiger Token verfügbar")
                return False
        except Exception as e:
            print(f"❌ API-Verbindung fehlgeschlagen: {e}")
            return False
    
    def compare_with_session_data(self):
        """Vergleicht API-Daten mit Session-basierten Daten"""
        print("🔄 Vergleiche API-Daten mit Session-Daten...")
        
        # Lade Session-basierte Daten
        session_file = Path("download/data/sessions/session_bolt.json")
        if session_file.exists():
            print("✅ Session-Daten gefunden")
        else:
            print("❌ Keine Session-Daten verfügbar")
        
        # Teste API-Daten
        try:
            fleet_data = self.get_fleet_summary()
            if fleet_data:
                print("✅ API-Daten verfügbar")
                print("📊 Datenvergleich möglich")
            else:
                print("❌ Keine API-Daten verfügbar")
        except Exception as e:
            print(f"❌ Fehler beim API-Datenabruf: {e}")

def main():
    integration = BoltAPIIntegration()
    
    print("🔗 Bolt API Integration")
    print("=" * 30)
    
    # Teste Verbindung
    if not integration.test_api_connection():
        print("❌ API-Verbindung nicht verfügbar")
        print("📝 Führen Sie zuerst 'python API/bolt_api_manager.py' aus")
        return
    
    print("\n📋 Verfügbare Aktionen:")
    print("  [1] Wochenbericht herunterladen")
    print("  [2] Fleet-Zusammenfassung abrufen")
    print("  [3] Fahrer-Liste abrufen")
    print("  [4] Fahrzeug-Liste abrufen")
    print("  [5] API-Verbindung testen")
    print("  [6] Datenvergleich mit Session")
    
    try:
        choice = int(input("\nAktion wählen (1-6): "))
        
        if choice == 1:
            kw = int(input("Kalenderwoche eingeben (z.B. 26): "))
            integration.download_weekly_report(kw)
        
        elif choice == 2:
            fleet_data = integration.get_fleet_summary()
            if fleet_data:
                print("📊 Fleet-Zusammenfassung:")
                print(json.dumps(fleet_data, indent=2, ensure_ascii=False))
        
        elif choice == 3:
            driver_data = integration.get_driver_list()
            if driver_data:
                print("👥 Fahrer-Liste:")
                print(json.dumps(driver_data, indent=2, ensure_ascii=False))
        
        elif choice == 4:
            vehicle_data = integration.get_vehicle_list()
            if vehicle_data:
                print("🚗 Fahrzeug-Liste:")
                print(json.dumps(vehicle_data, indent=2, ensure_ascii=False))
        
        elif choice == 5:
            integration.test_api_connection()
        
        elif choice == 6:
            integration.compare_with_session_data()
        
        else:
            print("❌ Ungültige Auswahl")
    
    except ValueError:
        print("❌ Ungültige Eingabe")
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    main() 