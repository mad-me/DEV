#!/usr/bin/env python3
"""
Bolt API Analyzer
Analysiert die tatsächlichen API-Aufrufe von Bolt
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BoltAPIAnalyzer:
    def __init__(self):
        self.base_url = "https://fleets.bolt.eu"
        self.session_file = Path("download/data/sessions/session_bolt.json")
        self.load_session_data()
    
    def load_session_data(self):
        """Lädt Session-Daten"""
        if not self.session_file.exists():
            print("❌ Keine Bolt Session gefunden")
            return
        
        with open(self.session_file, 'r') as f:
            self.session_data = json.load(f)
        
        # Extrahiere wichtige Daten
        self.token = None
        self.company_id = None
        
        for origin in self.session_data.get("origins", []):
            if origin.get("origin") == "https://fleets.bolt.eu":
                for item in origin.get("localStorage", []):
                    if item.get("name") == "taxifyFleetOwnerPortal_refresh_token":
                        self.token = item.get("value")
                    elif item.get("name") == "FOP_active_company_id":
                        self.company_id = item.get("value")
        
        print(f"🔍 Session-Daten analysiert:")
        print(f"   Company ID: {self.company_id}")
        print(f"   Token verfügbar: {'Ja' if self.token else 'Nein'}")
    
    def make_request(self, url: str, method: str = "GET", data: dict = None, params: dict = None):
        """Macht einen Request mit Session-Daten"""
        if not self.token:
            print("❌ Kein Token verfügbar")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://fleets.bolt.eu/",
            "Origin": "https://fleets.bolt.eu"
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            else:
                raise ValueError(f"Nicht unterstützte HTTP-Methode: {method}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request fehlgeschlagen: {e}")
            return None
    
    def test_api_endpoints(self):
        """Testet verschiedene API-Endpunkte"""
        print("\n🧪 Teste API-Endpunkte...")
        print("=" * 50)
        
        # Teste verschiedene Endpunkte
        endpoints = [
            # Standard API-Endpunkte
            f"api/companies/{self.company_id}/reports",
            f"api/reports",
            f"api/fleet/reports",
            
            # GraphQL-Endpunkte (falls Bolt GraphQL verwendet)
            "graphql",
            "api/graphql",
            
            # REST-API-Endpunkte
            f"api/v1/companies/{self.company_id}/reports",
            f"api/v1/reports",
            f"api/v2/companies/{self.company_id}/reports",
            f"api/v2/reports",
            
            # Dashboard-Endpunkte
            f"api/companies/{self.company_id}/dashboard",
            "api/dashboard",
            f"api/v1/companies/{self.company_id}/dashboard",
            f"api/v1/dashboard",
            
            # Performance-Endpunkte
            f"api/companies/{self.company_id}/performance",
            "api/performance",
            f"api/v1/companies/{self.company_id}/performance",
            f"api/v1/performance",
            
            # CSV-Endpunkte
            f"api/companies/{self.company_id}/reports/csv",
            "api/reports/csv",
            f"api/v1/companies/{self.company_id}/reports/csv",
            f"api/v1/reports/csv"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            url = f"{self.base_url}/{endpoint}"
            print(f"\n🔍 Teste: {endpoint}")
            
            # Teste GET-Request
            response = self.make_request(url, "GET")
            if response:
                print(f"   📊 Status: {response.status_code}")
                print(f"   📋 Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ JSON-Daten erhalten")
                        print(f"   📋 Datenstruktur: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                        results[endpoint] = data
                    except:
                        print(f"   📄 HTML/Text-Daten erhalten")
                        print(f"   📊 Länge: {len(response.text)} Zeichen")
                        results[endpoint] = {"data": response.text[:200] + "..."}
                else:
                    print(f"   ❌ Fehler: {response.status_code}")
                    print(f"   📄 Response: {response.text[:100]}...")
            else:
                print(f"   ❌ Request fehlgeschlagen")
        
        return results
    
    def test_graphql(self):
        """Testet GraphQL-Endpunkte"""
        print("\n🧪 Teste GraphQL-Endpunkte...")
        print("=" * 50)
        
        graphql_endpoints = [
            "graphql",
            "api/graphql",
            "api/v1/graphql"
        ]
        
        # GraphQL Query für Reports
        query = """
        query GetReports($companyId: String!, $startDate: String!, $endDate: String!) {
            reports(companyId: $companyId, startDate: $startDate, endDate: $endDate) {
                id
                date
                revenue
                trips
            }
        }
        """
        
        variables = {
            "companyId": self.company_id,
            "startDate": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "endDate": datetime.now().strftime("%Y-%m-%d")
        }
        
        for endpoint in graphql_endpoints:
            url = f"{self.base_url}/{endpoint}"
            print(f"\n🔍 Teste GraphQL: {endpoint}")
            
            data = {
                "query": query,
                "variables": variables
            }
            
            response = self.make_request(url, "POST", data=data)
            if response:
                print(f"   📊 Status: {response.status_code}")
                if response.status_code == 200:
                    try:
                        result = response.json()
                        print(f"   ✅ GraphQL-Daten erhalten")
                        print(f"   📋 Datenstruktur: {list(result.keys()) if isinstance(result, dict) else 'Array'}")
                    except:
                        print(f"   📄 Nicht-JSON Response")
                        print(f"   📊 Länge: {len(response.text)} Zeichen")
                else:
                    print(f"   ❌ Fehler: {response.status_code}")
                    print(f"   📄 Response: {response.text[:100]}...")
            else:
                print(f"   ❌ Request fehlgeschlagen")
    
    def analyze_existing_download(self):
        """Analysiert das bestehende Download-System"""
        print("\n🔍 Analysiere bestehendes Download-System...")
        print("=" * 50)
        
        # Lade das bestehende Download-Skript
        dl_script = Path("download/src/DL_Bolt.py")
        if dl_script.exists():
            print(f"✅ Download-Skript gefunden: {dl_script}")
            
            # Zeige wichtige URLs aus dem Skript
            print(f"📋 Wichtige URLs:")
            print(f"   - Base URL: https://fleets.bolt.eu/")
            print(f"   - Reports URL: https://fleets.bolt.eu/{self.company_id}/reports")
            print(f"   - Session-Datei: {self.session_file}")
        else:
            print(f"❌ Download-Skript nicht gefunden")
    
    def run_analysis(self):
        """Führt die vollständige Analyse durch"""
        print("🔍 Bolt API Analyzer")
        print("=" * 40)
        
        # Analysiere Session-Daten
        self.load_session_data()
        
        # Analysiere bestehendes System
        self.analyze_existing_download()
        
        # Teste API-Endpunkte
        api_results = self.test_api_endpoints()
        
        # Teste GraphQL
        self.test_graphql()
        
        # Zusammenfassung
        print(f"\n📋 Zusammenfassung:")
        successful_api = sum(1 for result in api_results.values() if result is not None)
        print(f"✅ Erfolgreiche API-Endpunkte: {successful_api}/{len(api_results)}")
        
        if successful_api > 0:
            print(f"\n🎯 Empfehlung:")
            print(f"   - Verwenden Sie die erfolgreichen API-Endpunkte")
            print(f"   - Falls alle fehlschlagen, verwenden Sie das bestehende Session-System")
        else:
            print(f"\n🎯 Empfehlung:")
            print(f"   - Bolt hat wahrscheinlich keine direkte REST-API")
            print(f"   - Verwenden Sie das bestehende Session-basierte System")
            print(f"   - Oder implementieren Sie Browser-Automation mit Playwright")

def main():
    analyzer = BoltAPIAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 