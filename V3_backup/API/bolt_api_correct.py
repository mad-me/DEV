#!/usr/bin/env python3
"""
Bolt API Correct Implementation
Verwendet die korrekten API-Endpunkte für Bolt
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BoltAPICorrect:
    def __init__(self):
        self.base_url = "https://fleets.bolt.eu"
        self.config_file = Path("API/bolt_api_config.json")
        self.token_file = Path("API/bolt_token.json")
        self.load_config()
    
    def load_config(self):
        """Lädt die Bolt API-Konfiguration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "client_id": "",
                "client_secret": "",
                "company_id": "30496",
                "redirect_uri": "https://fleets.bolt.eu"
            }
    
    def get_access_token(self):
        """Holt einen neuen Access Token aus der Session"""
        try:
            # Lade Session-Daten
            session_file = Path("download/data/sessions/session_bolt.json")
            if not session_file.exists():
                print("❌ Keine Bolt Session gefunden")
                return None
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Extrahiere Token aus Session
            for origin in session_data.get("origins", []):
                if origin.get("origin") == "https://fleets.bolt.eu":
                    for item in origin.get("localStorage", []):
                        if item.get("name") == "taxifyFleetOwnerPortal_refresh_token":
                            token = item.get("value")
                            if token:
                                # Token speichern
                                token_info = {
                                    "access_token": token,
                                    "expires_at": time.time() + 3600,
                                    "token_type": "Bearer"
                                }
                                
                                self.token_file.parent.mkdir(parents=True, exist_ok=True)
                                with open(self.token_file, 'w') as f:
                                    json.dump(token_info, f, indent=2)
                                
                                print("✅ Bolt Token aus Session extrahiert")
                                return token
            
            print("❌ Kein Token in Session gefunden")
            return None
            
        except Exception as e:
            logger.error(f"Fehler beim Token-Extraktion: {e}")
            return None
    
    def get_valid_token(self):
        """Holt einen gültigen Token"""
        if self.token_file.exists():
            with open(self.token_file, 'r') as f:
                token_info = json.load(f)
            
            if time.time() < token_info["expires_at"] - 300:
                return token_info["access_token"]
        
        return self.get_access_token()
    
    def make_api_request(self, endpoint: str, method: str = "GET", data: dict = None, params: dict = None):
        """Macht einen API-Request an Bolt"""
        token = self.get_valid_token()
        if not token:
            raise Exception("Kein gültiger Token verfügbar")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://fleets.bolt.eu/"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            else:
                raise ValueError(f"Nicht unterstützte HTTP-Methode: {method}")
            
            response.raise_for_status()
            
            # Prüfe Content-Type
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                return response.json()
            elif 'text/csv' in content_type:
                return {"data": response.text}
            else:
                # Versuche JSON zu parsen, auch wenn Content-Type nicht stimmt
                try:
                    return response.json()
                except:
                    return {"data": response.text}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API-Request fehlgeschlagen: {e}")
            raise
    
    def get_reports_data(self, start_date: str = None, end_date: str = None):
        """Holt Reports-Daten von Bolt API"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Versuche verschiedene Endpunkte
        endpoints = [
            f"api/companies/{self.config['company_id']}/reports",
            f"api/reports",
            f"api/fleet/reports",
            f"api/companies/{self.config['company_id']}/fleet/reports"
        ]
        
        for endpoint in endpoints:
            try:
                params = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "format": "json"
                }
                
                response = self.make_api_request(endpoint, params=params)
                if response and isinstance(response, dict):
                    print(f"✅ Erfolgreich: {endpoint}")
                    return response
                    
            except Exception as e:
                print(f"❌ Fehlgeschlagen: {endpoint} - {e}")
                continue
        
        return None
    
    def get_dashboard_data(self):
        """Holt Dashboard-Daten von Bolt API"""
        endpoints = [
            f"api/companies/{self.config['company_id']}/dashboard",
            "api/dashboard",
            "api/fleet/dashboard"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.make_api_request(endpoint)
                if response and isinstance(response, dict):
                    print(f"✅ Erfolgreich: {endpoint}")
                    return response
                    
            except Exception as e:
                print(f"❌ Fehlgeschlagen: {endpoint} - {e}")
                continue
        
        return None
    
    def get_performance_data(self):
        """Holt Performance-Daten von Bolt API"""
        endpoints = [
            f"api/companies/{self.config['company_id']}/performance",
            "api/performance",
            "api/fleet/performance"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.make_api_request(endpoint)
                if response and isinstance(response, dict):
                    print(f"✅ Erfolgreich: {endpoint}")
                    return response
                    
            except Exception as e:
                print(f"❌ Fehlgeschlagen: {endpoint} - {e}")
                continue
        
        return None
    
    def download_csv_report(self, start_date: str, end_date: str, save_path: str = None):
        """Lädt CSV-Report herunter"""
        if not save_path:
            save_path = f"download/data/raw/Bolt_API_{start_date}_{end_date}.csv"
        
        # Versuche verschiedene CSV-Endpunkte
        endpoints = [
            f"api/companies/{self.config['company_id']}/reports/csv",
            "api/reports/csv",
            "api/fleet/reports/csv",
            f"api/companies/{self.config['company_id']}/fleet/reports/csv"
        ]
        
        for endpoint in endpoints:
            try:
                params = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "format": "csv"
                }
                
                response = self.make_api_request(endpoint, params=params)
                
                if response and response.get('data'):
                    # CSV-Daten speichern
                    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(response['data'])
                    
                    print(f"✅ CSV-Report gespeichert: {save_path}")
                    return save_path
                    
            except Exception as e:
                print(f"❌ Fehlgeschlagen: {endpoint} - {e}")
                continue
        
        return None
    
    def test_all_endpoints(self):
        """Testet alle verfügbaren Endpunkte"""
        print("🧪 Teste alle Bolt API-Endpunkte")
        print("=" * 50)
        
        # Teste Reports
        print("\n📊 Teste Reports-Endpunkte...")
        reports_data = self.get_reports_data()
        if reports_data:
            print("✅ Reports-Daten erfolgreich")
            print(f"📋 Datenstruktur: {list(reports_data.keys())}")
        
        # Teste Dashboard
        print("\n📊 Teste Dashboard-Endpunkte...")
        dashboard_data = self.get_dashboard_data()
        if dashboard_data:
            print("✅ Dashboard-Daten erfolgreich")
            print(f"📋 Datenstruktur: {list(dashboard_data.keys())}")
        
        # Teste Performance
        print("\n📊 Teste Performance-Endpunkte...")
        performance_data = self.get_performance_data()
        if performance_data:
            print("✅ Performance-Daten erfolgreich")
            print(f"📋 Datenstruktur: {list(performance_data.keys())}")
        
        # Teste CSV-Download
        print("\n📥 Teste CSV-Download...")
        today = datetime.now()
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        csv_result = self.download_csv_report(start_date, end_date)
        if csv_result:
            print("✅ CSV-Download erfolgreich")
        
        return {
            'reports': reports_data,
            'dashboard': dashboard_data,
            'performance': performance_data,
            'csv': csv_result
        }

def main():
    api = BoltAPICorrect()
    
    print("🔗 Bolt API Correct Implementation")
    print("=" * 40)
    
    # Teste alle Endpunkte
    results = api.test_all_endpoints()
    
    print(f"\n📋 Zusammenfassung:")
    successful = sum(1 for result in results.values() if result is not None)
    print(f"✅ Erfolgreiche Endpunkte: {successful}/{len(results)}")
    
    # Zeige erfolgreiche Daten
    for name, data in results.items():
        if data:
            print(f"✅ {name}: Daten verfügbar")
            if isinstance(data, dict) and 'data' in data:
                print(f"   📊 Datenlänge: {len(str(data['data']))} Zeichen")

if __name__ == "__main__":
    main() 