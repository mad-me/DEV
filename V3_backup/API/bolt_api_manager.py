#!/usr/bin/env python3
"""
Bolt API Manager
OAuth2-basierte API-Integration für Bolt Fleet Management
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BoltAPIManager:
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
                "company_id": "30496",  # Standard aus Ihrer Session
                "redirect_uri": "https://fleets.bolt.eu"
            }
    
    def save_config(self):
        """Speichert die Bolt API-Konfiguration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_credentials(self, client_id: str, client_secret: str, company_id: str = "30496"):
        """Konfiguriert Bolt API-Credentials"""
        self.config.update({
            "client_id": client_id,
            "client_secret": client_secret,
            "company_id": company_id
        })
        self.save_config()
        print("✅ Bolt API-Credentials konfiguriert")
    
    def get_access_token(self):
        """Holt einen neuen Access Token aus der Session"""
        try:
            # Lade Session-Daten
            session_file = Path("download/data/sessions/session_bolt.json")
            if not session_file.exists():
                print("❌ Keine Bolt Session gefunden")
                print("📝 Bitte führen Sie zuerst 'python download/src/DL_Bolt.py' aus")
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
                                    "expires_at": time.time() + 3600,  # 1 Stunde
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
        """Holt einen gültigen Token (neu oder aus Cache)"""
        if self.token_file.exists():
            with open(self.token_file, 'r') as f:
                token_info = json.load(f)
            
            # Prüfe ob Token noch gültig ist (5 Minuten Puffer)
            if time.time() < token_info["expires_at"] - 300:
                return token_info["access_token"]
        
        # Neuer Token erforderlich
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
            
            # Prüfe ob Response JSON ist
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return {"data": response.text}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API-Request fehlgeschlagen: {e}")
            raise
    
    def get_fleet_data(self, start_date: str = None, end_date: str = None):
        """Holt Fleet-Daten von Bolt API"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = "api/companies/30496/fleet/reports"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "format": "json"
        }
        
        return self.make_api_request(endpoint, params=params)
    
    def get_driver_data(self):
        """Holt Fahrer-Daten von Bolt API"""
        endpoint = "api/companies/30496/drivers"
        return self.make_api_request(endpoint)
    
    def get_vehicle_data(self):
        """Holt Fahrzeug-Daten von Bolt API"""
        endpoint = "api/companies/30496/vehicles"
        return self.make_api_request(endpoint)
    
    def get_dashboard_data(self):
        """Holt Dashboard-Daten von Bolt API"""
        endpoint = "api/companies/30496/dashboard"
        return self.make_api_request(endpoint)
    
    def get_performance_data(self):
        """Holt Performance-Daten von Bolt API"""
        endpoint = "api/companies/30496/performance"
        return self.make_api_request(endpoint)
    
    def get_revenue_data(self):
        """Holt Revenue-Daten von Bolt API"""
        endpoint = "api/companies/30496/revenue"
        return self.make_api_request(endpoint)
    
    def download_csv_report(self, start_date: str, end_date: str, save_path: str = None):
        """Lädt CSV-Report herunter (kompatibel mit bestehendem System)"""
        if not save_path:
            save_path = f"download/data/raw/Bolt_API_{start_date}_{end_date}.csv"
        
        endpoint = "api/reports/csv"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "format": "csv"
        }
        
        try:
            response = self.make_api_request(endpoint, params=params)
            
            # CSV-Daten speichern
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(response.get('data', ''))
            
            print(f"✅ CSV-Report gespeichert: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Fehler beim CSV-Download: {e}")
            raise

def setup_bolt_api():
    """Interaktives Setup für Bolt API"""
    manager = BoltAPIManager()
    
    print("🔐 Bolt API Setup")
    print("=" * 30)
    
    client_id = input("Bolt Client ID: ").strip()
    client_secret = input("Bolt Client Secret: ").strip()
    company_id = input("Company ID (Standard: 30496): ").strip() or "30496"
    
    if client_id and client_secret:
        manager.setup_credentials(client_id, client_secret, company_id)
        
        # Teste API-Verbindung
        print("\n🧪 Teste API-Verbindung...")
        try:
            token = manager.get_access_token()
            if token:
                print("✅ API-Verbindung erfolgreich!")
                print("✅ Token erhalten und gespeichert")
            else:
                print("❌ API-Verbindung fehlgeschlagen")
        except Exception as e:
            print(f"❌ Fehler beim API-Test: {e}")
    else:
        print("❌ Client ID und Secret erforderlich")

if __name__ == "__main__":
    setup_bolt_api() 