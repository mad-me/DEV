#!/usr/bin/env python3
"""
Test-Skript für Task 1.3: Status-Konsistenz beheben
Testet die einheitliche Verwendung englischer Status-Werte
"""

import sys
import os
import re

def main():
    """Hauptfunktion für den Test"""
    print("🚀 Starte Test für Task 1.3: Status-Konsistenz beheben")
    
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
        
        # Test 1: Prüfe ob deutsche Status-Werte verwendet werden (sollte nicht)
        german_status = re.findall(r'["\'](Aktiv|Wartung|Inaktiv|Suspendiert)["\']', content)
        if german_status:
            print(f"❌ Deutsche Status-Werte gefunden: {german_status}")
            all_tests_passed = False
        else:
            print("✅ Keine deutschen Status-Werte gefunden")
        
        # Test 2: Prüfe ob englische Status-Werte verwendet werden
        english_status = re.findall(r'["\'](active|suspended|inactive)["\']', content)
        if english_status:
            print(f"✅ Englische Status-Werte gefunden: {english_status}")
        else:
            print("❌ Keine englischen Status-Werte gefunden")
            all_tests_passed = False
        
        # Test 3: Prüfe Status-Vergleiche
        status_comparisons = re.findall(r'modelData\.status\s*===\s*["\'][^"\']+["\']', content)
        if status_comparisons:
            print(f"✅ Status-Vergleiche gefunden: {len(status_comparisons)}")
            for comp in status_comparisons:
                if any(german in comp for german in ["Aktiv", "Wartung", "Inaktiv", "Suspendiert"]):
                    print(f"❌ Status-Vergleich verwendet deutsche Werte: {comp}")
                    all_tests_passed = False
                else:
                    print(f"✅ Status-Vergleich verwendet englische Werte: {comp}")
        else:
            print("ℹ️ Keine Status-Vergleiche gefunden")
        
        # Test 4: Prüfe Status-Display-Logik
        display_logic = re.findall(r'text:\s*modelData\.status', content)
        if display_logic:
            print(f"✅ Status-Display-Logik gefunden: {len(display_logic)}")
        else:
            print("ℹ️ Keine Status-Display-Logik gefunden")
    
    # Test 5: Backend-Status-Werte prüfen
    print(f"\n🔧 Teste Backend-Status-Werte:")
    backend_file = "mitarbeiter_seite_qml_v2.py"
    
    if os.path.exists(backend_file):
        with open(backend_file, 'r', encoding='utf-8') as f:
            backend_content = f.read()
        
        # Prüfe ob Backend englische Status-Werte verwendet
        backend_english_status = re.findall(r'["\'](active|suspended|inactive)["\']', backend_content)
        if backend_english_status:
            print(f"✅ Backend verwendet englische Status-Werte: {len(backend_english_status)}")
        else:
            print("❌ Backend verwendet keine englischen Status-Werte")
            all_tests_passed = False
        
        # Prüfe ob Backend deutsche Status-Werte verwendet (sollte nicht)
        backend_german_status = re.findall(r'["\'](Aktiv|Wartung|Inaktiv)["\']', backend_content)
        if backend_german_status:
            print(f"❌ Backend verwendet deutsche Status-Werte: {backend_german_status}")
            all_tests_passed = False
        else:
            print("✅ Backend verwendet keine deutschen Status-Werte")
        
        # Prüfe Status-Validierung
        status_validation = re.findall(r'valid_statuses\s*=\s*\[[^\]]*\]', backend_content)
        if status_validation:
            print("✅ Status-Validierung gefunden")
            for validation in status_validation:
                if "active" in validation and "suspended" in validation and "inactive" in validation:
                    print("✅ Status-Validierung verwendet korrekte englische Werte")
                else:
                    print(f"❌ Status-Validierung verwendet inkorrekte Werte: {validation}")
                    all_tests_passed = False
        else:
            print("ℹ️ Keine Status-Validierung gefunden")
    else:
        print(f"❌ Backend-Datei {backend_file} nicht gefunden")
        all_tests_passed = False
    
    print(f"\n📋 Test-Ergebnisse:")
    if all_tests_passed:
        print("✅ Alle Tests bestanden")
        print("✅ Status-Werte sind konsistent")
        print("✅ QML verwendet englische Status-Werte")
        print("✅ Backend verwendet englische Status-Werte")
        
        print("\n🎯 Task 1.3: Status-Konsistenz beheben - ABGESCHLOSSEN")
        print("✅ Alle Test-Kriterien erfüllt")
    else:
        print("❌ Einige Tests fehlgeschlagen")
        print("❌ Status-Konsistenz muss noch korrigiert werden")
        
        print("\n🎯 Task 1.3: Status-Konsistenz beheben - FEHLGESCHLAGEN")
        print("❌ Test-Kriterien nicht erfüllt")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 