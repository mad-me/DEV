#!/usr/bin/env python3
"""
Bolt API Test
Testet verschiedene API-Endpunkte um die korrekten URLs zu finden
"""

import requests
import json
from pathlib import Path
from bolt_api_manager import BoltAPIManager

class BoltAPITester:
    def __init__(self):
        self.api_manager = BoltAPIManager()
    
    def test_endpoint(self, endpoint: str, method: str = "GET", params: dict = None):
        """Testet einen API-Endpunkt"""
        try:
            print(f"🧪 Teste Endpunkt: {method} {endpoint}")
            
            response = self.api_manager.make_api_request(endpoint, method, params=params)
            
            print(f"✅ Erfolgreich: {endpoint}")
            print(f"📊 Response-Typ: {type(response)}")
            if isinstance(response, dict):
                print(f"📋 Keys: {list(response.keys())}")
            return response
            
        except Exception as e:
            print(f"❌ Fehlgeschlagen: {endpoint} - {e}")
            return None
    
    def test_all_endpoints(self):
        """Testet alle möglichen API-Endpunkte"""
        print("🔍 Teste alle Bolt API-Endpunkte")
        print("=" * 50)
        
        # Teste verschiedene Endpunkte
        endpoints = [
            # Berichte
            "api/reports",
            "api/companies/30496/reports",
            "api/fleet/reports",
            "api/companies/30496/fleet/reports",
            
            # Fahrer
            "api/drivers",
            "api/companies/30496/drivers",
            "api/fleet/drivers",
            
            # Fahrzeuge
            "api/vehicles",
            "api/companies/30496/vehicles",
            "api/fleet/vehicles",
            
            # Dashboard
            "api/dashboard",
            "api/companies/30496/dashboard",
            
            # Performance
            "api/performance",
            "api/companies/30496/performance",
            
            # Einnahmen
            "api/revenue",
            "api/companies/30496/revenue",
            
            # CSV-Download
            "api/reports/csv",
            "api/companies/30496/reports/csv",
            "api/fleet/reports/csv"
        ]
        
        successful_endpoints = []
        
        for endpoint in endpoints:
            result = self.test_endpoint(endpoint)
            if result:
                successful_endpoints.append(endpoint)
        
        print(f"\n📊 Ergebnisse:")
        print(f"✅ Erfolgreiche Endpunkte: {len(successful_endpoints)}")
        print(f"❌ Fehlgeschlagene Endpunkte: {len(endpoints) - len(successful_endpoints)}")
        
        if successful_endpoints:
            print(f"\n✅ Funktionsfähige Endpunkte:")
            for endpoint in successful_endpoints:
                print(f"   - {endpoint}")
        
        return successful_endpoints
    
    def test_csv_download(self):
        """Testet CSV-Download spezifisch"""
        print("\n📥 Teste CSV-Download")
        print("=" * 30)
        
        # Teste verschiedene CSV-Endpunkte
        csv_endpoints = [
            "api/reports/csv",
            "api/companies/30496/reports/csv",
            "api/fleet/reports/csv",
            "api/companies/30496/fleet/reports/csv"
        ]
        
        for endpoint in csv_endpoints:
            try:
                print(f"🧪 Teste CSV-Download: {endpoint}")
                
                # Teste mit aktueller Woche
                from datetime import datetime, timedelta
                today = datetime.now()
                start_date = today - timedelta(days=7)
                end_date = today
                
                params = {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "format": "csv"
                }
                
                response = self.api_manager.make_api_request(endpoint, params=params)
                
                if response and response.get('data'):
                    print(f"✅ CSV-Download erfolgreich: {endpoint}")
                    print(f"📊 Datenlänge: {len(response['data'])} Zeichen")
                    return endpoint
                else:
                    print(f"❌ Keine CSV-Daten erhalten: {endpoint}")
                    
            except Exception as e:
                print(f"❌ CSV-Download fehlgeschlagen: {endpoint} - {e}")
        
        return None
    
    def test_authentication(self):
        """Testet die Authentifizierung"""
        print("🔐 Teste Authentifizierung")
        print("=" * 30)
        
        try:
            token = self.api_manager.get_valid_token()
            if token:
                print(f"✅ Token verfügbar: {token[:20]}...")
                
                # Teste einfachen Request
                response = self.api_manager.make_api_request("api/status")
                print("✅ Authentifizierung erfolgreich")
                return True
            else:
                print("❌ Kein Token verfügbar")
                return False
                
        except Exception as e:
            print(f"❌ Authentifizierung fehlgeschlagen: {e}")
            return False

def main():
    tester = BoltAPITester()
    
    print("🧪 Bolt API Tester")
    print("=" * 30)
    
    # Teste Authentifizierung
    if not tester.test_authentication():
        print("❌ Authentifizierung fehlgeschlagen")
        return
    
    # Teste alle Endpunkte
    successful_endpoints = tester.test_all_endpoints()
    
    # Teste CSV-Download
    csv_endpoint = tester.test_csv_download()
    
    print(f"\n📋 Zusammenfassung:")
    print(f"✅ Erfolgreiche Endpunkte: {len(successful_endpoints)}")
    if csv_endpoint:
        print(f"✅ CSV-Download-Endpunkt: {csv_endpoint}")
    else:
        print("❌ Kein CSV-Download-Endpunkt gefunden")

if __name__ == "__main__":
    main() 