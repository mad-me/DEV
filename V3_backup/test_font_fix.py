#!/usr/bin/env python3
"""
Test-Skript für Task 1.1: Font-Definition hinzufügen
Testet die Mitarbeiterseite und das Driver ID Feld
"""

import sys
import os
from PySide6.QtCore import QObject, QCoreApplication, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QTimer

class TestBackend(QObject):
    """Mock-Backend für Tests"""
    
    def __init__(self):
        super().__init__()
        self._mitarbeiter_list = [
            {
                "driver_id": "40100",
                "driver_license_number": "B123456789",
                "first_name": "Max",
                "last_name": "Mustermann",
                "phone": "+43 123 456789",
                "email": "max@example.com",
                "hire_date": "2024-01-15",
                "status": "active"
            },
            {
                "driver_id": "40101", 
                "driver_license_number": "B987654321",
                "first_name": "Anna",
                "last_name": "Schmidt",
                "phone": "+43 987 654321",
                "email": "anna@example.com",
                "hire_date": "2024-02-01",
                "status": "active"
            }
        ]
    
    def get_mitarbeiter_list(self):
        return self._mitarbeiter_list

def main():
    """Hauptfunktion für den Test"""
    print("🚀 Starte Test für Task 1.1: Font-Definition hinzufügen")
    
    # QML-Datei-Pfad
    qml_file = "Style/TestMitarbeiterV2Cards.qml"
    
    # Prüfe ob QML-Datei existiert
    if not os.path.exists(qml_file):
        print(f"❌ Fehler: QML-Datei {qml_file} nicht gefunden")
        return False
    
    print(f"✅ QML-Datei gefunden: {qml_file}")
    
    # Prüfe Font-Datei
    font_file = "Style/assets/fonts/Ubuntu-Regular.ttf"
    if not os.path.exists(font_file):
        print(f"❌ Fehler: Font-Datei {font_file} nicht gefunden")
        return False
    
    print(f"✅ Font-Datei gefunden: {font_file}")
    
    # QML-Inhalt prüfen
    with open(qml_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'FontLoader' in content and 'ubuntuFont' in content:
        print("✅ FontLoader-Definition gefunden")
    else:
        print("❌ FontLoader-Definition fehlt")
        return False
    
    if 'font.family: ubuntuFont.name' in content:
        print("✅ Font-Verwendung gefunden")
    else:
        print("❌ Font-Verwendung fehlt")
        return False
    
    # Driver ID Feld prüfen
    if 'driverIdField' in content:
        print("✅ Driver ID Feld gefunden")
    else:
        print("❌ Driver ID Feld fehlt")
        return False
    
    print("\n📋 Test-Ergebnisse:")
    print("✅ QML-Datei existiert")
    print("✅ Font-Datei existiert") 
    print("✅ FontLoader ist definiert")
    print("✅ Font wird verwendet")
    print("✅ Driver ID Feld ist vorhanden")
    
    print("\n🎯 Task 1.1: Font-Definition hinzufügen - ABGESCHLOSSEN")
    print("✅ Alle Test-Kriterien erfüllt")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 