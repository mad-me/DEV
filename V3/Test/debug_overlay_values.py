#!/usr/bin/env python3
"""
Debug-Skript für Overlay-Werteübertragung
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abrechnungsseite_qml import AbrechnungsSeiteQML
import sqlite3

def test_overlay_values():
    """Testet die Werteübertragung an das Overlay"""
    
    print("=== DEBUG: Overlay-Werteübertragung Test ===")
    
    # Backend-Instanz erstellen
    backend = AbrechnungsSeiteQML()
    
    # Test-Daten simulieren
    test_data = {
        "fahrer": "Test Fahrer",
        "fahrzeug": "Test Fahrzeug",
        "kw": "KW26",
        "deal": "C",  # Custom Deal
        "pauschale": "600",
        "umsatzgrenze": "1500"
    }
    
    print(f"Test-Daten: {test_data}")
    
    # Wizard-Callback simulieren
    print("\n--- Simuliere Wizard-Callback ---")
    
    # Fahrer-ID in Datenbank einfügen (falls nicht vorhanden)
    try:
        conn = sqlite3.connect("SQL/database.db")
        cursor = conn.cursor()
        
        # Erstelle custom_deal_config Tabelle falls nicht vorhanden
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_deal_config (
                id INTEGER PRIMARY KEY,
                fahrer TEXT NOT NULL,
                taxi_deal INTEGER,
                taxi_slider REAL,
                uber_deal INTEGER,
                uber_slider REAL,
                bolt_deal INTEGER,
                bolt_slider REAL,
                einsteiger_deal INTEGER,
                einsteiger_slider REAL,
                garage_slider REAL,
                tank_slider REAL
            )
        """)
        
        # Füge Test-Konfiguration direkt hinzu (ohne Foreign Key)
        cursor.execute("""
            INSERT OR REPLACE INTO custom_deal_config
            (id, fahrer, taxi_deal, taxi_slider, uber_deal, uber_slider, bolt_deal, bolt_slider, einsteiger_deal, einsteiger_slider, garage_slider, tank_slider)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (999, test_data["fahrer"], 1, 60.0, 2, 70.0, 0, 80.0, 1, 50.0, 30.0, 40.0))
        
        conn.commit()
        conn.close()
        print("Test-Daten in Datenbank eingefügt")
        
    except Exception as e:
        print(f"Fehler beim Einfügen der Test-Daten: {e}")
    
    # Simuliere den Wizard-Callback
    def simulate_wizard_callback():
        print(f"DEBUG: Simuliere Wizard-Callback mit Daten: {test_data}")
        fahrer = test_data["fahrer"]
        fahrzeug = test_data["fahrzeug"]
        kw = test_data["kw"]
        
        print(f"DEBUG: Setze Backend-Werte:")
        print(f"  Fahrer: {fahrer}")
        print(f"  Fahrzeug: {fahrzeug}")
        print(f"  KW: {kw}")
        
        backend._fahrer_label = fahrer
        backend._fahrzeug_label = fahrzeug
        backend._kw_label = kw
        
        # Fahrer-ID setzen (für Test verwenden wir 999)
        backend._fahrer_id = 999
        print(f"DEBUG: Fahrer-ID gesetzt auf: {backend._fahrer_id}")
        
        # Deal-Typ setzen basierend auf der Auswahl
        if "deal" in test_data:
            backend._deal = test_data["deal"]
            print(f"DEBUG: Deal-Typ gesetzt auf: {backend._deal}")
        else:
            print(f"DEBUG: Kein Deal-Typ in Daten gefunden, verwende Standard")
            backend._deal = "P"  # Standard
        
        # Pauschale und Umsatzgrenze setzen
        if "pauschale" in test_data:
            backend._pauschale = float(test_data["pauschale"])
            print(f"DEBUG: Pauschale gesetzt auf: {backend._pauschale}")
        else:
            print(f"DEBUG: Keine Pauschale in Daten, verwende Standard: 500")
            backend._pauschale = 500.0
            
        if "umsatzgrenze" in test_data:
            backend._umsatzgrenze = float(test_data["umsatzgrenze"])
            print(f"DEBUG: Umsatzgrenze gesetzt auf: {backend._umsatzgrenze}")
        else:
            print(f"DEBUG: Keine Umsatzgrenze in Daten, verwende Standard: 1200")
            backend._umsatzgrenze = 1200.0
        
        # Deal-spezifische Konfiguration setzen
        if backend._deal == "C":
            print(f"DEBUG: Custom-Deal erkannt, lade gespeicherte Konfiguration")
            # Custom-Deal: Lade gespeicherte Konfiguration über Namen
            config = backend.ladeOverlayKonfigurationByName(fahrer)
            print(f"DEBUG: Geladene Konfiguration: {config}")
            if config and len(config) == 10:
                # Alle Plattform-Faktoren aus der Config laden
                backend._taxi_deal = config[0]
                backend._taxi_slider = config[1]
                backend._uber_deal = config[2]
                backend._uber_slider = config[3]
                backend._bolt_deal = config[4]
                backend._bolt_slider = config[5]
                backend._einsteiger_deal = config[6]
                backend._einsteiger_slider = config[7]
                backend._garage_slider = config[8]
                backend._tank_slider = config[9]
                
                # Faktoren berechnen (Slider / 100)
                backend._taxi_faktor = backend._taxi_slider / 100.0
                backend._uber_faktor = backend._uber_slider / 100.0
                backend._bolt_faktor = backend._bolt_slider / 100.0
                backend._einsteiger_faktor = backend._einsteiger_slider / 100.0
                backend._tank_faktor = backend._tank_slider / 100.0
                backend._garage_faktor = backend._garage_slider / 100.0
                
                # Debug-Ausgabe aller Faktoren
                print(f"DEBUG: Alle Faktoren geladen:")
                print(f"  Taxi: Deal={backend._taxi_deal}, Slider={backend._taxi_slider}, Faktor={backend._taxi_faktor}")
                print(f"  Uber: Deal={backend._uber_deal}, Slider={backend._uber_slider}, Faktor={backend._uber_faktor}")
                print(f"  Bolt: Deal={backend._bolt_deal}, Slider={backend._bolt_slider}, Faktor={backend._bolt_faktor}")
                print(f"  Einsteiger: Deal={backend._einsteiger_deal}, Slider={backend._einsteiger_slider}, Faktor={backend._einsteiger_faktor}")
                print(f"  Tank: Slider={backend._tank_slider}, Faktor={backend._tank_faktor}")
                print(f"  Garage: Slider={backend._garage_slider}, Faktor={backend._garage_faktor}")
                
                # overlayIncomeOhneEinsteiger aus Umsätzen berechnen
                # (wird nach der Auswertung korrekt berechnet, da Umsätze erst dann verfügbar sind)
                backend._overlay_income_ohne_einsteiger = 0.0  # Wird in update_ergebnis berechnet
                
                print(f"DEBUG: Faktoren für Ergebnisberechnung gesetzt")
            else:
                print(f"DEBUG: Keine Config gefunden für Fahrer '{fahrer}'")
                # Default-Faktoren setzen
                backend._taxi_faktor = 1.0
                backend._uber_faktor = 1.0
                backend._bolt_faktor = 1.0
                backend._einsteiger_faktor = 1.0
                backend._tank_faktor = 1.0
                backend._garage_faktor = 1.0
                backend._overlay_income_ohne_einsteiger = 0.0
        
        print(f"DEBUG: Backend-Werte nach Setup:")
        print(f"  Deal: {backend._deal}")
        print(f"  Pauschale: {backend._pauschale}")
        print(f"  Umsatzgrenze: {backend._umsatzgrenze}")
        print(f"  Fahrer-ID: {backend._fahrer_id}")
        
        # Teste ladeOverlayKonfiguration
        print(f"\n--- Teste ladeOverlayKonfiguration ---")
        if backend._fahrer_id:
            config = backend.ladeOverlayKonfiguration(backend._fahrer_id)
            print(f"Geladene Konfiguration für ID {backend._fahrer_id}: {config}")
        else:
            print("Keine Fahrer-ID verfügbar")
    
    # Führe Test aus
    simulate_wizard_callback()
    
    print("\n=== Test beendet ===")

if __name__ == "__main__":
    test_overlay_values() 