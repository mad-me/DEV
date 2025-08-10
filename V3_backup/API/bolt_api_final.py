#!/usr/bin/env python3
"""
Bolt API Final Integration
Vollständige API-Integration mit allen funktionsfähigen Endpunkten
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from bolt_api_manager import BoltAPIManager

class BoltAPIFinal:
    def __init__(self):
        self.api_manager = BoltAPIManager()
        self.download_dir = Path("download/data/raw")
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_weekly_report(self, kw: int):
        """Lädt Wochenbericht für Kalenderwoche"""
        try:
            print(f"📥 Lade Wochenbericht KW{kw}...")
            
            # Berechne Datum für Kalenderwoche
            year = datetime.now().year
            start_date = datetime.strptime(f"{year}-W{kw:02d}-1", "%Y-W%W-%w")
            end_date = start_date + timedelta(days=6)
            
            filename = f"Bolt_API_KW{kw:02d}.csv"
            save_path = self.download_dir / filename
            
            # API-CSV-Download
            result = self.api_manager.download_csv_report(
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
    
    def get_dashboard_data(self):
        """Holt Dashboard-Daten"""
        try:
            dashboard_data = self.api_manager.get_dashboard_data()
            print("✅ Dashboard-Daten erfolgreich abgerufen")
            return dashboard_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Dashboard-Daten: {e}")
            return None
    
    def get_performance_data(self):
        """Holt Performance-Daten"""
        try:
            performance_data = self.api_manager.get_performance_data()
            print("✅ Performance-Daten erfolgreich abgerufen")
            return performance_data
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Performance-Daten: {e}")
            return None
    
    def get_revenue_data(self):
        """Holt Revenue-Daten"""
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
    
    def get_all_data(self):
        """Holt alle verfügbaren Daten"""
        print("📊 Lade alle verfügbaren Daten...")
        
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
    api = BoltAPIFinal()
    
    print("🔗 Bolt API Final Integration")
    print("=" * 40)
    
    # Teste Verbindung
    if not api.test_api_connection():
        print("❌ API-Verbindung nicht verfügbar")
        return
    
    print("\n📋 Verfügbare Aktionen:")
    print("  [1] Wochenbericht herunterladen")
    print("  [2] Fleet-Zusammenfassung abrufen")
    print("  [3] Fahrer-Liste abrufen")
    print("  [4] Fahrzeug-Liste abrufen")
    print("  [5] Dashboard-Daten abrufen")
    print("  [6] Performance-Daten abrufen")
    print("  [7] Revenue-Daten abrufen")
    print("  [8] Alle Daten abrufen")
    print("  [9] API-Verbindung testen")
    
    try:
        choice = int(input("\nAktion wählen (1-9): "))
        
        if choice == 1:
            kw = int(input("Kalenderwoche eingeben (z.B. 31): "))
            api.download_weekly_report(kw)
        
        elif choice == 2:
            fleet_data = api.get_fleet_summary()
            if fleet_data:
                print("📊 Fleet-Zusammenfassung:")
                print(json.dumps(fleet_data, indent=2, ensure_ascii=False))
        
        elif choice == 3:
            driver_data = api.get_driver_list()
            if driver_data:
                print("👥 Fahrer-Liste:")
                print(json.dumps(driver_data, indent=2, ensure_ascii=False))
        
        elif choice == 4:
            vehicle_data = api.get_vehicle_list()
            if vehicle_data:
                print("🚗 Fahrzeug-Liste:")
                print(json.dumps(vehicle_data, indent=2, ensure_ascii=False))
        
        elif choice == 5:
            dashboard_data = api.get_dashboard_data()
            if dashboard_data:
                print("📊 Dashboard-Daten:")
                print(json.dumps(dashboard_data, indent=2, ensure_ascii=False))
        
        elif choice == 6:
            performance_data = api.get_performance_data()
            if performance_data:
                print("📈 Performance-Daten:")
                print(json.dumps(performance_data, indent=2, ensure_ascii=False))
        
        elif choice == 7:
            revenue_data = api.get_revenue_data()
            if revenue_data:
                print("💰 Revenue-Daten:")
                print(json.dumps(revenue_data, indent=2, ensure_ascii=False))
        
        elif choice == 8:
            all_data = api.get_all_data()
            if all_data:
                print("📊 Alle Daten:")
                print(json.dumps(all_data, indent=2, ensure_ascii=False))
        
        elif choice == 9:
            api.test_api_connection()
        
        else:
            print("❌ Ungültige Auswahl")
    
    except ValueError:
        print("❌ Ungültige Eingabe")
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    main() 