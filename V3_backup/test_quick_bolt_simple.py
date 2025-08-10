#!/usr/bin/env python3
"""
Einfaches Test-Skript für die runQuickBolt Funktionalität
"""

import sys
from PySide6.QtCore import QCoreApplication
from fahrzeug_seite_qml_v2 import FahrzeugSeiteQMLV2

def test_quick_bolt():
    """Testet die runQuickBolt Funktionalität"""
    print("🧪 Teste runQuickBolt Funktionalität...")
    
    # QApplication für Qt-Funktionalität
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    
    # Backend erstellen
    backend = FahrzeugSeiteQMLV2()
    
    # Test-Parameter
    license_plate = "W132CTX"
    driver = "Test Fahrer"
    week_from = 26
    week_to = 28
    tank_percent = 0.1
    starter_percent = 0.05
    expense = 50.0
    
    print(f"📋 Test-Parameter:")
    print(f"   🚗 Fahrzeug: {license_plate}")
    print(f"   👤 Fahrer: {driver}")
    print(f"   📅 Kalenderwochen: {week_from}-{week_to}")
    print(f"   ⛽ Tank-Prozent: {tank_percent*100:.1f}%")
    print(f"   🎯 Einsteiger-Prozent: {starter_percent*100:.1f}%")
    print(f"   💰 Expense: {expense:.2f} €")
    print()
    
    # Signal-Handler für Ergebnisse
    def on_result(output):
        print("📊 ERGEBNIS:")
        print("=" * 50)
        print(output)
        print("=" * 50)
        print("✅ Test erfolgreich abgeschlossen!")
        app.quit()
    
    # Signal verbinden
    backend.quickResultReady.connect(on_result)
    
    # Funktion aufrufen
    print("🚀 Starte runQuickBolt...")
    backend.runQuickBolt(license_plate, driver, week_from, week_to, tank_percent, starter_percent, expense)
    
    # Event-Loop starten
    app.exec()

if __name__ == "__main__":
    test_quick_bolt()

