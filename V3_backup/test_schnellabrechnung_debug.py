#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def test_schnellabrechnung():
    """Testet die Schnellabrechnung direkt"""
    try:
        # Test-Konfiguration erstellen
        config_content = """[Test]
fahrer = Test Fahrer
fahrzeug = TEST-123
kalenderwochen = 26,27
tank_prozent = 0.13
einsteiger_prozent = 0.20
expense_fix = 0.0

[Deals]
p_deal_pauschale = 650.0
p_deal_umsatzgrenze = 1200.0
p_deal_bonus_prozent = 0.1
percent_deal_anteil = 0.5
percent_deal_einsteiger_faktor = 0.5
custom_deal_anteil = 0.6

[Garage]
monatliche_garage = 80.0
garage_faktor = 0.5
max_montage_pro_monat = 5

[Umsatz]
max_umsatz_pro_fahrt = 250
min_umsatz_pro_fahrt = -250
umsatz_filter_aktiv = true

[Fuzzy_Matching]
min_match_score = 50
max_distance = 3
arabic_name_bonus = 20

[Security]
sql_injection_protection = true
input_validation = true
max_kalenderwochen = 52
max_fahrer_name_length = 100
max_fahrzeug_name_length = 50
"""
        
        # Konfigurationsdatei speichern
        config_file = "test_config.ini"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✅ Konfigurationsdatei erstellt")
        
        # Schnellabrechnung-Skript ausführen
        cmd = [sys.executable, 'test_schnellabrechnung.py']
        print(f"🚀 Führe aus: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("📊 Ausgabe:")
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn Code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Schnellabrechnung erfolgreich ausgeführt")
        else:
            print("❌ Schnellabrechnung fehlgeschlagen")
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout: Schnellabrechnung wurde nach 5 Minuten abgebrochen")
    except Exception as e:
        print(f"💥 Fehler: {e}")

if __name__ == "__main__":
    test_schnellabrechnung()
