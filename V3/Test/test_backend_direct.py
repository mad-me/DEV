#!/usr/bin/env python3
"""
Direkter Backend-Test ohne QML
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abrechnungsseite_qml import AbrechnungsSeiteQML

def test_backend_direct():
    """Testet das Backend direkt ohne QML"""
    
    print("=== DEBUG: Direkter Backend-Test ===")
    
    # Backend-Instanz erstellen
    backend = AbrechnungsSeiteQML()
    print(f"DEBUG: Backend erstellt: {backend}")
    
    # Test-Werte direkt setzen
    print("DEBUG: Setze Test-Werte...")
    
    # Headcard-Werte
    backend._headcard_umsatz = 1000.0
    backend._headcard_trinkgeld = 50.0
    backend._headcard_cash = 200.0
    backend._headcard_credit_card = 800.0
    backend._headcard_garage = 100.0
    
    # Deal-Werte
    backend._deal = "P"
    backend._pauschale = 500.0
    backend._umsatzgrenze = 1200.0
    backend._ergebnis = 750.0
    
    # Input-Werte
    backend._input_gas = "50"
    backend._input_einsteiger = "100"
    backend._input_expense = "25"
    
    print("DEBUG: Test-Werte gesetzt")
    print(f"  Umsatz: {backend.headcard_umsatz}")
    print(f"  Trinkgeld: {backend.headcard_trinkgeld}")
    print(f"  Bargeld: {backend.headcard_cash}")
    print(f"  Kreditkarte: {backend.headcard_credit_card}")
    print(f"  Garage: {backend.headcard_garage}")
    print(f"  Deal: {backend.deal}")
    print(f"  Pauschale: {backend.pauschale}")
    print(f"  Umsatzgrenze: {backend.umsatzgrenze}")
    print(f"  Ergebnis: {backend.ergebnis}")
    print(f"  Input Gas: '{backend.inputGas}'")
    print(f"  Input Einsteiger: '{backend.inputEinsteiger}'")
    print(f"  Input Expense: '{backend.inputExpense}'")
    
    # Teste Faktor-Setter
    print("\nDEBUG: Teste Faktor-Setter...")
    backend.setTaxiFaktor(0.8)
    backend.setUberFaktor(0.6)
    backend.setBoltFaktor(0.7)
    backend.setEinsteigerFaktor(0.5)
    backend.setTankFaktor(0.9)
    backend.setGarageFaktor(1.0)
    backend.setOverlayIncomeOhneEinsteiger(600.0)
    
    print("DEBUG: Faktoren gesetzt")
    print(f"  Taxi-Faktor: {backend._taxi_faktor}")
    print(f"  Uber-Faktor: {backend._uber_faktor}")
    print(f"  Bolt-Faktor: {backend._bolt_faktor}")
    print(f"  Einsteiger-Faktor: {backend._einsteiger_faktor}")
    print(f"  Tank-Faktor: {backend._tank_faktor}")
    print(f"  Garage-Faktor: {backend._garage_faktor}")
    print(f"  OverlayIncomeOhneEinsteiger: {backend._overlay_income_ohne_einsteiger}")
    
    # Teste Datenbank-Operationen
    print("\nDEBUG: Teste Datenbank-Operationen...")
    try:
        # Teste das Laden einer Konfiguration
        config = backend.ladeOverlayKonfiguration(999)
        print(f"DEBUG: Geladene Konfiguration für ID 999: {config}")
    except Exception as e:
        print(f"DEBUG: Fehler beim Laden der Konfiguration: {e}")
    
    print("=== Test beendet ===")

if __name__ == "__main__":
    test_backend_direct() 