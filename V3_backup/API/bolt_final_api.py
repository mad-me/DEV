#!/usr/bin/env python3
"""
Bolt Final API
Verwendet das bestehende System mit API-ähnlicher Schnittstelle
"""

import asyncio
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

class BoltFinalAPI:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.dl_script = self.base_dir / "download" / "src" / "DL_Bolt.py"
        self.temp_dir = self.base_dir / "SQL" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 Final API konfiguriert:")
        print(f"   Download-Skript: {self.dl_script}")
        print(f"   Temp-Verzeichnis: {self.temp_dir}")
    
    def run_download_script(self, kw: int):
        """Führt das bestehende Download-Skript aus"""
        try:
            print(f"📥 Führe Download-Skript für KW {kw:02d} aus...")
            
            # Führe das bestehende Skript aus
            result = subprocess.run([
                sys.executable, str(self.dl_script), str(kw)
            ], capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                print("✅ Download-Skript erfolgreich")
                return True
            else:
                print(f"❌ Download-Skript fehlgeschlagen: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim Ausführen des Download-Skripts: {e}")
            return False
    
    def find_latest_csv(self):
        """Findet die neueste CSV-Datei"""
        try:
            csv_files = list(self.temp_dir.glob("Bolt_KW*.csv"))
            if csv_files:
                # Sortiere nach Änderungsdatum
                latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
                return latest_file
            return None
        except Exception as e:
            print(f"❌ Fehler beim Finden der CSV-Datei: {e}")
            return None
    
    def parse_csv_to_json(self, csv_path: str):
        """Konvertiert CSV zu JSON"""
        try:
            df = pd.read_csv(csv_path)
            
            # Konvertiere zu JSON
            json_data = {
                "metadata": {
                    "source": "bolt_final_api",
                    "file": str(csv_path),
                    "rows": len(df),
                    "columns": list(df.columns),
                    "generated_at": datetime.now().isoformat()
                },
                "data": df.to_dict('records')
            }
            
            return json_data
            
        except Exception as e:
            print(f"❌ Fehler beim Parsen der CSV: {e}")
            return None
    
    def get_reports_data(self, kw: int = None):
        """Holt Reports-Daten"""
        if not kw:
            # Verwende aktuelle Kalenderwoche
            kw = datetime.now().isocalendar()[1]
        
        print(f"📊 Hole Reports-Daten für KW {kw:02d}")
        
        # Führe Download aus
        success = self.run_download_script(kw)
        
        if success:
            # Finde CSV-Datei
            csv_file = self.find_latest_csv()
            if csv_file:
                print(f"✅ CSV-Datei gefunden: {csv_file.name}")
                
                # Konvertiere zu JSON
                json_data = self.parse_csv_to_json(str(csv_file))
                return json_data
            else:
                print("❌ Keine CSV-Datei gefunden")
        
        return None
    
    def get_dashboard_data(self):
        """Simuliert Dashboard-Daten"""
        dashboard_data = {
            "metadata": {
                "source": "bolt_final_api",
                "type": "dashboard_simulation",
                "generated_at": datetime.now().isoformat()
            },
            "data": {
                "total_revenue": 0,
                "total_trips": 0,
                "active_drivers": 0,
                "active_vehicles": 0,
                "note": "Dashboard-Daten sind nicht über API verfügbar"
            }
        }
        
        return dashboard_data
    
    def get_performance_data(self):
        """Simuliert Performance-Daten"""
        performance_data = {
            "metadata": {
                "source": "bolt_final_api",
                "type": "performance_simulation",
                "generated_at": datetime.now().isoformat()
            },
            "data": {
                "average_rating": 0,
                "completion_rate": 0,
                "response_time": 0,
                "note": "Performance-Daten sind nicht über API verfügbar"
            }
        }
        
        return performance_data
    
    def test_api(self):
        """Testet die Final API"""
        print("🧪 Teste Bolt Final API")
        print("=" * 40)
        
        # Teste Reports-Daten
        print("\n📊 Teste Reports-Daten...")
        current_kw = datetime.now().isocalendar()[1]
        reports_data = self.get_reports_data(current_kw)
        
        if reports_data:
            print("✅ Reports-Daten erfolgreich")
            print(f"📊 Daten: {reports_data['metadata']['rows']} Zeilen, {len(reports_data['metadata']['columns'])} Spalten")
            
            # Zeige erste Zeile als Beispiel
            if reports_data['data']:
                first_row = reports_data['data'][0]
                print(f"📋 Beispiel-Daten: {list(first_row.keys())}")
        else:
            print("❌ Reports-Daten fehlgeschlagen")
        
        # Teste Dashboard-Daten
        print("\n📊 Teste Dashboard-Daten...")
        dashboard_data = self.get_dashboard_data()
        if dashboard_data:
            print("✅ Dashboard-Daten erfolgreich")
        
        # Teste Performance-Daten
        print("\n📊 Teste Performance-Daten...")
        performance_data = self.get_performance_data()
        if performance_data:
            print("✅ Performance-Daten erfolgreich")
        
        return {
            'reports': reports_data,
            'dashboard': dashboard_data,
            'performance': performance_data
        }
    
    def show_json_example(self):
        """Zeigt ein Beispiel der JSON-Daten"""
        print("\n🔍 JSON-Daten Beispiel:")
        print("=" * 40)
        
        current_kw = datetime.now().isocalendar()[1]
        reports_data = self.get_reports_data(current_kw)
        
        if reports_data:
            print("📊 Reports-Daten Struktur:")
            print(json.dumps(reports_data, indent=2, ensure_ascii=False)[:1000] + "...")
        else:
            print("❌ Keine Reports-Daten verfügbar")

def main():
    api = BoltFinalAPI()
    
    print("🔗 Bolt Final API")
    print("=" * 30)
    
    # Teste API
    results = api.test_api()
    
    print(f"\n📋 Zusammenfassung:")
    successful = sum(1 for result in results.values() if result is not None)
    print(f"✅ Erfolgreiche Operationen: {successful}/{len(results)}")
    
    if successful > 0:
        print(f"\n🎯 Empfehlung:")
        print(f"   - Verwenden Sie die Final API")
        print(f"   - CSV-Daten werden automatisch zu JSON konvertiert")
        print(f"   - Dashboard/Performance-Daten sind simuliert")
        
        # Zeige JSON-Beispiel
        api.show_json_example()

if __name__ == "__main__":
    main() 