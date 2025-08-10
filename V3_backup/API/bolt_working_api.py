#!/usr/bin/env python3
"""
Bolt Working API Integration
Kombiniert Session-basierte Downloads mit API-Daten
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
from bolt_api_manager import BoltAPIManager

class BoltWorkingAPI:
    def __init__(self):
        self.api_manager = BoltAPIManager()
        self.download_dir = Path("download/data/raw")
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_weekly_report_session(self, kw: int):
        """Lädt Wochenbericht über Session-basierten Download"""
        try:
            print(f"📥 Lade Wochenbericht KW{kw} über Session...")
            
            # Führe das bestehende Download-Skript aus
            result = subprocess.run([
                sys.executable, "download/src/DL_Bolt.py", str(kw)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Session-Download erfolgreich")
                return True
            else:
                print(f"❌ Session-Download fehlgeschlagen: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim Session-Download: {e}")
            return False
    
    def get_fleet_summary(self):
        """Holt Fleet-Zusammenfassung über API"""
        try:
            fleet_data = self.api_manager.get_fleet_data()
            print("✅ Fleet-Daten erfolgreich abgerufen")
            return fleet_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Fleet-Daten: {e}")
            return None
    
    def get_driver_list(self):
        """Holt Fahrer-Liste über API"""
        try:
            driver_data = self.api_manager.get_driver_data()
            print("✅ Fahrer-Daten erfolgreich abgerufen")
            return driver_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Fahrer-Daten: {e}")
            return None
    
    def get_vehicle_list(self):
        """Holt Fahrzeug-Liste über API"""
        try:
            vehicle_data = self.api_manager.get_vehicle_data()
            print("✅ Fahrzeug-Daten erfolgreich abgerufen")
            return vehicle_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Fahrzeug-Daten: {e}")
            return None
    
    def get_dashboard_data(self):
        """Holt Dashboard-Daten über API"""
        try:
            dashboard_data = self.api_manager.get_dashboard_data()
            print("✅ Dashboard-Daten erfolgreich abgerufen")
            return dashboard_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Dashboard-Daten: {e}")
            return None
    
    def get_performance_data(self):
        """Holt Performance-Daten über API"""
        try:
            performance_data = self.api_manager.get_performance_data()
            print("✅ Performance-Daten erfolgreich abgerufen")
            return performance_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Performance-Daten: {e}")
            return None
    
    def get_revenue_data(self):
        """Holt Revenue-Daten über API"""
        try:
            revenue_data = self.api_manager.get_revenue_data()
            print("✅ Revenue-Daten erfolgreich abgerufen")
            return revenue_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Revenue-Daten: {e}")
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
    
    def test_session_connection(self):
        """Testet die Session-Verbindung"""
        session_file = Path("download/data/sessions/session_bolt.json")
        if session_file.exists():
            print("✅ Session-Datei gefunden")
            return True
        else:
            print("❌ Keine Session-Datei gefunden")
            return False
    
    def get_system_status(self):
        """Zeigt den Status beider Systeme"""
        print("🔍 System-Status")
        print("=" * 30)
        
        api_status = self.test_api_connection()
        session_status = self.test_session_connection()
        
        if api_status and session_status:
            print("✅ Beide Systeme verfügbar")
            return "both"
        elif api_status:
            print("✅ Nur API verfügbar")
            return "api"
        elif session_status:
            print("✅ Nur Session verfügbar")
            return "session"
        else:
            print("❌ Kein System verfügbar")
            return "none"
    
    def get_all_api_data(self):
        """Holt alle verfügbaren API-Daten"""
        print("📊 Lade alle verfügbaren API-Daten...")
        
        data = {}
        
        # Fleet-Daten
        fleet_data = self.get_fleet_summary()
        if fleet_data:
            data['fleet'] = fleet_data
        
        # Fahrer-Daten
        driver_data = self.get_driver_list()
        if driver_data:
            data['drivers'] = driver_data
        
        # Fahrzeug-Daten
        vehicle_data = self.get_vehicle_list()
        if vehicle_data:
            data['vehicles'] = vehicle_data
        
        # Dashboard-Daten
        dashboard_data = self.get_dashboard_data()
        if dashboard_data:
            data['dashboard'] = dashboard_data
        
        # Performance-Daten
        performance_data = self.get_performance_data()
        if performance_data:
            data['performance'] = performance_data
        
        # Revenue-Daten
        revenue_data = self.get_revenue_data()
        if revenue_data:
            data['revenue'] = revenue_data
        
        return data

def main():
    api = BoltWorkingAPI()
    
    print("🔗 Bolt Working API Integration")
    print("=" * 40)
    
    # Prüfe System-Status
    status = api.get_system_status()
    
    if status == "none":
        print("❌ Kein System verfügbar")
        print("📝 Bitte führen Sie zuerst 'python download/src/DL_Bolt.py' aus")
        return
    
    print("\n📋 Verfügbare Aktionen:")
    print("  [1] Wochenbericht herunterladen (Session)")
    print("  [2] Fleet-Zusammenfassung abrufen (API)")
    print("  [3] Fahrer-Liste abrufen (API)")
    print("  [4] Fahrzeug-Liste abrufen (API)")
    print("  [5] Dashboard-Daten abrufen (API)")
    print("  [6] Performance-Daten abrufen (API)")
    print("  [7] Revenue-Daten abrufen (API)")
    print("  [8] Alle API-Daten abrufen")
    print("  [9] System-Status anzeigen")
    
    try:
        choice = int(input("\nAktion wählen (1-9): "))
        
        if choice == 1:
            if status in ["session", "both"]:
                kw = int(input("Kalenderwoche eingeben (z.B. 31): "))
                api.download_weekly_report_session(kw)
            else:
                print("❌ Session nicht verfügbar")
        
        elif choice == 2:
            if status in ["api", "both"]:
                fleet_data = api.get_fleet_summary()
                if fleet_data:
                    print("📊 Fleet-Zusammenfassung:")
                    print(json.dumps(fleet_data, indent=2, ensure_ascii=False))
            else:
                print("❌ API nicht verfügbar")
        
        elif choice == 3:
            if status in ["api", "both"]:
                driver_data = api.get_driver_list()
                if driver_data:
                    print("👥 Fahrer-Liste:")
                    print(json.dumps(driver_data, indent=2, ensure_ascii=False))
            else:
                print("❌ API nicht verfügbar")
        
        elif choice == 4:
            if status in ["api", "both"]:
                vehicle_data = api.get_vehicle_list()
                if vehicle_data:
                    print("🚗 Fahrzeug-Liste:")
                    print(json.dumps(vehicle_data, indent=2, ensure_ascii=False))
            else:
                print("❌ API nicht verfügbar")
        
        elif choice == 5:
            if status in ["api", "both"]:
                dashboard_data = api.get_dashboard_data()
                if dashboard_data:
                    print("📊 Dashboard-Daten:")
                    print(json.dumps(dashboard_data, indent=2, ensure_ascii=False))
            else:
                print("❌ API nicht verfügbar")
        
        elif choice == 6:
            if status in ["api", "both"]:
                performance_data = api.get_performance_data()
                if performance_data:
                    print("📈 Performance-Daten:")
                    print(json.dumps(performance_data, indent=2, ensure_ascii=False))
            else:
                print("❌ API nicht verfügbar")
        
        elif choice == 7:
            if status in ["api", "both"]:
                revenue_data = api.get_revenue_data()
                if revenue_data:
                    print("💰 Revenue-Daten:")
                    print(json.dumps(revenue_data, indent=2, ensure_ascii=False))
            else:
                print("❌ API nicht verfügbar")
        
        elif choice == 8:
            if status in ["api", "both"]:
                all_data = api.get_all_api_data()
                if all_data:
                    print("📊 Alle API-Daten:")
                    print(json.dumps(all_data, indent=2, ensure_ascii=False))
            else:
                print("❌ API nicht verfügbar")
        
        elif choice == 9:
            api.get_system_status()
        
        else:
            print("❌ Ungültige Auswahl")
    
    except ValueError:
        print("❌ Ungültige Eingabe")
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    main() 