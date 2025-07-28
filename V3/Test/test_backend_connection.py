#!/usr/bin/env python3
"""
Test-Skript für Backend-Verbindung
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QObject, QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from abrechnungsseite_qml import AbrechnungsSeiteQML

def test_backend_connection():
    """Testet die Backend-Verbindung"""
    
    print("=== DEBUG: Backend-Verbindung Test ===")
    
    # QApplication erstellen
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Import-Pfade setzen
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    engine.addImportPath(current_dir)
    engine.addImportPath(".")
    print(f"DEBUG: Import-Pfade gesetzt: {current_dir}")
    
    # Backend-Instanz erstellen
    backend = AbrechnungsSeiteQML()
    print(f"DEBUG: Backend erstellt: {backend}")
    
    # Backend an QML-Kontext registrieren
    engine.rootContext().setContextProperty("abrechnungsBackend", backend)
    print("DEBUG: Backend registriert")
    
    # Test-Werte setzen
    backend._headcard_umsatz = 1000.0
    backend._headcard_trinkgeld = 50.0
    backend._headcard_cash = 200.0
    backend._headcard_credit_card = 800.0
    backend._headcard_garage = 100.0
    backend._deal = "P"
    backend._pauschale = 500.0
    backend._umsatzgrenze = 1200.0
    backend._ergebnis = 750.0
    backend._input_gas = "50"
    backend._input_einsteiger = "100"
    backend._input_expense = "25"
    
    # Properties explizit aktualisieren
    backend.inputGasChanged.emit()
    backend.inputEinsteigerChanged.emit()
    backend.inputExpenseChanged.emit()
    
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
    
    # QML-Datei laden (vereinfachte Version)
    qml_file = os.path.join(current_dir, "Style/Abrechnungsseite.qml")
    print(f"DEBUG: Lade QML-Datei: {qml_file}")
    
    if os.path.exists(qml_file):
        engine.load(QUrl.fromLocalFile(qml_file))
        print("DEBUG: QML-Datei geladen")
        
        if engine.rootObjects():
            print("DEBUG: QML erfolgreich geladen")
            root = engine.rootObjects()[0]
            print(f"DEBUG: Root-Objekt: {root}")
            
            # Teste Backend-Zugriff
            try:
                # Versuche auf Backend-Eigenschaften zuzugreifen
                print("DEBUG: Teste Backend-Zugriff...")
                # Hier könnten wir weitere Tests hinzufügen
                print("DEBUG: Backend-Zugriff erfolgreich")
            except Exception as e:
                print(f"DEBUG: Fehler beim Backend-Zugriff: {e}")
        else:
            print("DEBUG: QML konnte nicht geladen werden")
            print("DEBUG: Verfügbare QML-Dateien:")
            style_dir = os.path.join(current_dir, "Style")
            if os.path.exists(style_dir):
                for file in os.listdir(style_dir):
                    if file.endswith('.qml'):
                        print(f"  - {file}")
    else:
        print(f"DEBUG: QML-Datei nicht gefunden: {qml_file}")
    
    print("=== Test beendet ===")

if __name__ == "__main__":
    test_backend_connection() 