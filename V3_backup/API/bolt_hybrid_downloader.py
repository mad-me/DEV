#!/usr/bin/env python3
"""
Bolt Hybrid Downloader
Kombiniert API- und Session-basierte Downloads für maximale Kompatibilität
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from bolt_api_manager import BoltAPIManager
import subprocess
import sys

class BoltHybridDownloader:
    def __init__(self):
        self.api_manager = BoltAPIManager()
        self.download_dir = Path("download/data/raw")
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_weekly_report_api(self, kw: int):
        """Versucht API-basierten Download"""
        try:
            print(f"🔄 Versuche API-Download für KW{kw}...")
            
            # Berechne Datum für Kalenderwoche
            year = datetime.now().year
            start_date = datetime.strptime(f"{year}-W{kw:02d}-1", "%Y-W%W-%w")
            end_date = start_date + timedelta(days=6)
            
            filename = f"Bolt_API_KW{kw:02d}.csv"
            save_path = self.download_dir / filename
            
            # Versuche API-Download
            response = self.api_manager.make_api_request(
                f"companies/{self.api_manager.config['company_id']}/reports",
                params={
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "format": "csv"
                }
            )
            
            # Speichere CSV-Daten
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(response.get('data', ''))
            
            print(f"✅ API-Download erfolgreich: {save_path}")
            return str(save_path)
            
        except Exception as e:
            print(f"❌ API-Download fehlgeschlagen: {e}")
            return None
    
    def download_weekly_report_session(self, kw: int):
        """Führt Session-basierten Download durch"""
        try:
            print(f"🔄 Führe Session-Download für KW{kw} durch...")
            
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
    
    def download_weekly_report(self, kw: int):
        """Hybrid-Download: API zuerst, dann Session-Fallback"""
        print(f"📥 Starte Hybrid-Download für KW{kw}")
        print("=" * 40)
        
        # Versuche API-Download zuerst
        api_result = self.download_weekly_report_api(kw)
        
        if api_result:
            print("✅ API-Download erfolgreich!")
            return api_result
        
        print("🔄 API-Download fehlgeschlagen, versuche Session-Download...")
        
        # Fallback auf Session-Download
        session_result = self.download_weekly_report_session(kw)
        
        if session_result:
            print("✅ Session-Download erfolgreich!")
            return "session_download"
        else:
            print("❌ Beide Download-Methoden fehlgeschlagen")
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

def main():
    downloader = BoltHybridDownloader()
    
    print("🔗 Bolt Hybrid Downloader")
    print("=" * 30)
    
    # Prüfe System-Status
    status = downloader.get_system_status()
    
    if status == "none":
        print("❌ Kein Download-System verfügbar")
        print("📝 Bitte führen Sie zuerst 'python download/src/DL_Bolt.py' aus")
        return
    
    print("\n📋 Verfügbare Aktionen:")
    print("  [1] Hybrid-Download (API + Session)")
    print("  [2] Nur API-Download")
    print("  [3] Nur Session-Download")
    print("  [4] System-Status anzeigen")
    
    try:
        choice = int(input("\nAktion wählen (1-4): "))
        
        if choice == 1:
            kw = int(input("Kalenderwoche eingeben (z.B. 31): "))
            downloader.download_weekly_report(kw)
        
        elif choice == 2:
            if status in ["api", "both"]:
                kw = int(input("Kalenderwoche eingeben (z.B. 31): "))
                downloader.download_weekly_report_api(kw)
            else:
                print("❌ API nicht verfügbar")
        
        elif choice == 3:
            if status in ["session", "both"]:
                kw = int(input("Kalenderwoche eingeben (z.B. 31): "))
                downloader.download_weekly_report_session(kw)
            else:
                print("❌ Session nicht verfügbar")
        
        elif choice == 4:
            downloader.get_system_status()
        
        else:
            print("❌ Ungültige Auswahl")
    
    except ValueError:
        print("❌ Ungültige Eingabe")
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    main() 