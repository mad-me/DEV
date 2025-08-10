#!/usr/bin/env python3
"""
Test-Skript für Task 1.2: Datenstruktur vereinheitlichen
Testet die korrekte Verwendung von first_name und last_name in QML
"""

import sys
import os
import re

def main():
    """Hauptfunktion für den Test"""
    print("🚀 Starte Test für Task 1.2: Datenstruktur vereinheitlichen")
    
    # QML-Dateien zu testen
    qml_files = [
        "Style/MitarbeiterSeiteV2Cards.qml",
        "Style/TestMitarbeiterV2Cards.qml"
    ]
    
    all_tests_passed = True
    
    for qml_file in qml_files:
        print(f"\n📄 Teste {qml_file}:")
        
        if not os.path.exists(qml_file):
            print(f"❌ Fehler: QML-Datei {qml_file} nicht gefunden")
            all_tests_passed = False
            continue
        
        # QML-Inhalt lesen
        with open(qml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test 1: Prüfe ob modelData.name noch verwendet wird (sollte nicht)
        name_usage = re.findall(r'modelData\.name', content)
        if name_usage:
            print(f"❌ modelData.name wird noch verwendet: {len(name_usage)} mal")
            all_tests_passed = False
        else:
            print("✅ modelData.name wird nicht mehr verwendet")
        
        # Test 2: Prüfe ob modelData.first_name verwendet wird
        first_name_usage = re.findall(r'modelData\.first_name', content)
        if first_name_usage:
            print(f"✅ modelData.first_name wird verwendet: {len(first_name_usage)} mal")
        else:
            print("❌ modelData.first_name wird nicht verwendet")
            all_tests_passed = False
        
        # Test 3: Prüfe ob modelData.last_name verwendet wird
        last_name_usage = re.findall(r'modelData\.last_name', content)
        if last_name_usage:
            print(f"✅ modelData.last_name wird verwendet: {len(last_name_usage)} mal")
        else:
            print("❌ modelData.last_name wird nicht verwendet")
            all_tests_passed = False
        
        # Test 4: Prüfe Console-Logs
        console_logs = re.findall(r'console\.log\([^)]*modelData[^)]*\)', content)
        if console_logs:
            print(f"✅ Console-Logs gefunden: {len(console_logs)}")
            for log in console_logs:
                if 'modelData.name' in log:
                    print(f"❌ Console-Log verwendet noch modelData.name: {log}")
                    all_tests_passed = False
                else:
                    print(f"✅ Console-Log verwendet korrekte Felder: {log}")
        else:
            print("ℹ️ Keine Console-Logs gefunden")
    
    # Test 5: Backend-Datenstruktur prüfen
    print(f"\n🔧 Teste Backend-Datenstruktur:")
    backend_file = "mitarbeiter_seite_qml_v2.py"
    
    if os.path.exists(backend_file):
        with open(backend_file, 'r', encoding='utf-8') as f:
            backend_content = f.read()
        
        # Prüfe ob first_name und last_name im Backend definiert sind
        if 'first_name' in backend_content and 'last_name' in backend_content:
            print("✅ Backend definiert first_name und last_name")
        else:
            print("❌ Backend definiert nicht first_name und last_name")
            all_tests_passed = False
        
        # Prüfe ob name-Feld im Backend definiert ist (sollte nicht)
        if 'name' in backend_content:
            name_definitions = re.findall(r'"name":\s*[^,}]+', backend_content)
            if name_definitions:
                print(f"❌ Backend definiert noch name-Feld: {len(name_definitions)} mal")
                all_tests_passed = False
            else:
                print("✅ Backend definiert kein name-Feld")
        else:
            print("✅ Backend definiert kein name-Feld")
    else:
        print(f"❌ Backend-Datei {backend_file} nicht gefunden")
        all_tests_passed = False
    
    print(f"\n📋 Test-Ergebnisse:")
    if all_tests_passed:
        print("✅ Alle Tests bestanden")
        print("✅ Datenstruktur ist vereinheitlicht")
        print("✅ QML verwendet korrekte Feldnamen")
        print("✅ Backend liefert korrekte Daten")
        
        print("\n🎯 Task 1.2: Datenstruktur vereinheitlichen - ABGESCHLOSSEN")
        print("✅ Alle Test-Kriterien erfüllt")
    else:
        print("❌ Einige Tests fehlgeschlagen")
        print("❌ Datenstruktur muss noch korrigiert werden")
        
        print("\n🎯 Task 1.2: Datenstruktur vereinheitlichen - FEHLGESCHLAGEN")
        print("❌ Test-Kriterien nicht erfüllt")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 