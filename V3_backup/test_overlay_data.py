import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fahrzeug_seite_qml_v2 import FahrzeugSeiteQMLV2

def test_overlay_data():
    print("Teste Overlay-Daten für W135CTX KW 31...")
    
    # Backend-Instanz erstellen
    backend = FahrzeugSeiteQMLV2()
    
    # Teste loadWeekDataForOverlay
    print("Rufe loadWeekDataForOverlay auf...")
    backend.loadWeekDataForOverlay("W135CTX", 31)
    
    print("Test abgeschlossen")

if __name__ == "__main__":
    test_overlay_data()
