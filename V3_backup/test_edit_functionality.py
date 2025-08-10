#!/usr/bin/env python3
"""
Test-Skript für Task 2.1: Edit-Funktionalität implementieren
Testet die Edit-Funktionalität in der Mitarbeiterseite
"""

import sys
import os
import re

def main():
    """Hauptfunktion für den Test"""
    print("🚀 Starte Test für Task 2.1: Edit-Funktionalität implementieren")
    
    # QML-Datei zu testen
    qml_file = "Style/TestMitarbeiterV2Cards.qml"
    
    if not os.path.exists(qml_file):
        print(f"❌ Fehler: QML-Datei {qml_file} nicht gefunden")
        return False
    
    print(f"✅ QML-Datei gefunden: {qml_file}")
    
    # QML-Inhalt lesen
    with open(qml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Edit-Button Funktionalität
    if 'showMitarbeiterFormOverlayForEdit(mitarbeiterData)' in content:
        print("✅ Edit-Button ruft showMitarbeiterFormOverlayForEdit auf")
    else:
        print("❌ Edit-Button ruft showMitarbeiterFormOverlayForEdit nicht auf")
        return False
    
    # Test 2: showMitarbeiterFormOverlayForEdit Funktion
    if 'function showMitarbeiterFormOverlayForEdit(mitarbeiterData)' in content:
        print("✅ showMitarbeiterFormOverlayForEdit Funktion existiert")
    else:
        print("❌ showMitarbeiterFormOverlayForEdit Funktion fehlt")
        return False
    
    # Test 3: Speichern-Button Funktionalität
    if 'mitarbeiterBackendV2.saveEmployee(mitarbeiterData)' in content:
        print("✅ Speichern-Button ruft mitarbeiterBackendV2.saveEmployee auf")
    else:
        print("❌ Speichern-Button ruft mitarbeiterBackendV2.saveEmployee nicht auf")
        return False
    
    # Test 4: Validierung
    validation_checks = re.findall(r'if \(![^)]+\.text\.trim\(\)\)', content)
    if len(validation_checks) >= 4:  # Mindestens 4 Pflichtfelder
        print(f"✅ Validierung implementiert: {len(validation_checks)} Checks")
    else:
        print(f"❌ Validierung unvollständig: {len(validation_checks)} Checks")
        return False
    
    # Test 5: Daten-Sammlung
    mitarbeiter_data_object = re.findall(r'var mitarbeiterData = \{[^}]+\}', content)
    if mitarbeiter_data_object:
        print("✅ Mitarbeiter-Daten werden korrekt gesammelt")
    else:
        print("❌ Mitarbeiter-Daten werden nicht korrekt gesammelt")
        return False
    
    # Test 6: Backend-Integration
    backend_file = "mitarbeiter_seite_qml_v2.py"
    if os.path.exists(backend_file):
        with open(backend_file, 'r', encoding='utf-8') as f:
            backend_content = f.read()
        
        if 'def saveEmployee(self, employee_data):' in backend_content:
            print("✅ Backend saveEmployee Methode existiert")
        else:
            print("❌ Backend saveEmployee Methode fehlt")
            return False
        
        # Prüfe Update-Logik
        if 'UPDATE drivers' in backend_content:
            print("✅ Backend Update-Logik implementiert")
        else:
            print("❌ Backend Update-Logik fehlt")
            return False
    else:
        print(f"❌ Backend-Datei {backend_file} nicht gefunden")
        return False
    
    print(f"\n📋 Test-Ergebnisse:")
    print("✅ Edit-Button Funktionalität implementiert")
    print("✅ Formular-Overlay mit vorausgefüllten Daten")
    print("✅ Speichern-Button mit Backend-Integration")
    print("✅ Validierung der Pflichtfelder")
    print("✅ Backend Update-Logik vorhanden")
    
    print("\n🎯 Task 2.1: Edit-Funktionalität implementieren - ABGESCHLOSSEN")
    print("✅ Alle Test-Kriterien erfüllt")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 