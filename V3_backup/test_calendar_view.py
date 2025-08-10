import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fahrzeug_seite_qml_v2 import FahrzeugSeiteQMLV2

def test_calendar_view():
    print("Teste Kalenderwochen-Ansicht...")
    
    # Backend-Instanz erstellen
    backend = FahrzeugSeiteQMLV2()
    
    print("Initiale Ansicht:", backend.isCalendarView)
    
    # Kalenderwochen-Ansicht aktivieren
    print("Aktiviere Kalenderwochen-Ansicht...")
    backend.toggleViewMode()
    
    print("Nach Toggle:", backend.isCalendarView)
    print("Fahrzeug-Liste Länge:", len(backend.fahrzeugList))
    
    # Prüfe ob Kalenderwochen-Daten vorhanden sind
    if backend.fahrzeugList:
        first_vehicle = backend.fahrzeugList[0]
        print("Erstes Fahrzeug:", first_vehicle.get("kennzeichen", "N/A"))
        print("Kalenderwochen:", len(first_vehicle.get("calendar_weeks", [])))
        
        if first_vehicle.get("calendar_weeks"):
            for week in first_vehicle["calendar_weeks"][:5]:  # Erste 5 Wochen
                print(f"  KW {week['week']}: has_data={week['has_data']}")
    
    print("Test abgeschlossen")

if __name__ == "__main__":
    test_calendar_view()
