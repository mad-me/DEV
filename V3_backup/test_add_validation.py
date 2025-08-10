#!/usr/bin/env python3
"""
Test-Skript für Task 2.3: Add-Funktionalität mit Echtzeit- und erweiterter Validierung
Testet die erweiterte Validierung der Add-Funktionalität
"""

import sys
import os
import re

def main():
    """Hauptfunktion für den Test"""
    print("🚀 Starte Test für Task 2.3: Add-Funktionalität mit erweiterter Validierung")
    
    # QML-Datei zu testen
    qml_file = "Style/TestMitarbeiterV2Cards.qml"
    
    if not os.path.exists(qml_file):
        print(f"❌ Fehler: QML-Datei {qml_file} nicht gefunden")
        return False
    
    print(f"✅ QML-Datei gefunden: {qml_file}")
    
    # QML-Inhalt lesen
    with open(qml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Validierungs-Properties
    validation_properties = [
        'isDriverIdValid',
        'isLicenseNumberValid', 
        'isFirstNameValid',
        'isLastNameValid',
        'isEmailValid',
        'isPhoneValid',
        'isDateValid'
    ]
    
    for prop in validation_properties:
        if prop in content:
            print(f"✅ Validierungs-Property gefunden: {prop}")
        else:
            print(f"❌ Validierungs-Property fehlt: {prop}")
            return False
    
    # Test 2: Error-Nachrichten Properties
    error_properties = [
        'driverIdError',
        'licenseNumberError',
        'firstNameError',
        'lastNameError',
        'emailError',
        'phoneError',
        'dateError'
    ]
    
    for prop in error_properties:
        if prop in content:
            print(f"✅ Error-Property gefunden: {prop}")
        else:
            print(f"❌ Error-Property fehlt: {prop}")
            return False
    
    # Test 3: Validierungs-Funktionen
    validation_functions = [
        'validateDriverId',
        'validateLicenseNumber',
        'validateFirstName',
        'validateLastName',
        'validateEmail',
        'validatePhone',
        'validateDate',
        'validateAllFields'
    ]
    
    for func in validation_functions:
        if func in content:
            print(f"✅ Validierungs-Funktion gefunden: {func}")
        else:
            print(f"❌ Validierungs-Funktion fehlt: {func}")
            return False
    
    # Test 4: Echtzeit-Validierung (onTextChanged)
    if 'onTextChanged:' in content:
        print("✅ Echtzeit-Validierung implementiert")
    else:
        print("❌ Echtzeit-Validierung fehlt")
        return False
    
    # Test 5: Visuelle Validierungs-Indikatoren
    visual_indicators = [
        'border.color: isDriverIdValid',
        'border.color: isLicenseNumberValid',
        'border.color: isFirstNameValid',
        'border.color: isLastNameValid',
        'border.color: isEmailValid',
        'border.color: isPhoneValid',
        'border.color: isDateValid'
    ]
    
    for indicator in visual_indicators:
        if indicator in content:
            print(f"✅ Visueller Indikator gefunden: {indicator.split(': ')[1]}")
        else:
            print(f"❌ Visueller Indikator fehlt: {indicator.split(': ')[1]}")
            return False
    
    # Test 6: Error-Nachrichten Anzeige
    error_displays = [
        'text: driverIdError',
        'text: licenseNumberError',
        'text: firstNameError',
        'text: lastNameError',
        'text: emailError',
        'text: phoneError',
        'text: dateError'
    ]
    
    for display in error_displays:
        if display in content:
            print(f"✅ Error-Anzeige gefunden: {display.split(': ')[1]}")
        else:
            print(f"❌ Error-Anzeige fehlt: {display.split(': ')[1]}")
            return False
    
    # Test 7: Erweiterte Validierungs-Regeln
    validation_rules = [
        'Driver ID darf nur Ziffern enthalten',
        'Führerscheinnummer muss mindestens 5 Zeichen haben',
        'Führerscheinnummer darf nur Großbuchstaben und Zahlen enthalten',
        'Vorname muss mindestens 2 Zeichen haben',
        'Vorname darf nur Buchstaben enthalten',
        'Nachname muss mindestens 2 Zeichen haben',
        'Nachname darf nur Buchstaben enthalten',
        'Ungültiges Email-Format',
        'Ungültiges Telefon-Format',
        'Telefonnummer muss mindestens 10 Zeichen haben',
        'Datum muss im Format YYYY-MM-DD sein'
    ]
    
    for rule in validation_rules:
        if rule in content:
            print(f"✅ Validierungs-Regel gefunden: {rule}")
        else:
            print(f"❌ Validierungs-Regel fehlt: {rule}")
            return False
    
    # Test 8: Farben für Validierung
    validation_colors = [
        '#4CAF50',  # Grün für gültig
        '#F44336'   # Rot für ungültig
    ]
    
    for color in validation_colors:
        if color in content:
            print(f"✅ Validierungs-Farbe gefunden: {color}")
        else:
            print(f"❌ Validierungs-Farbe fehlt: {color}")
            return False
    
    # Test 9: Erweiterte Speichern-Validierung
    if 'validateAllFields()' in content:
        print("✅ Erweiterte Speichern-Validierung implementiert")
    else:
        print("❌ Erweiterte Speichern-Validierung fehlt")
        return False
    
    # Test 10: Reset-Funktionalität
    if 'Validierung zurücksetzen' in content:
        print("✅ Validierungs-Reset implementiert")
    else:
        print("❌ Validierungs-Reset fehlt")
        return False
    
    print(f"\n📋 Test-Ergebnisse:")
    print("✅ Echtzeit-Validierung implementiert")
    print("✅ Erweiterte Validierungs-Regeln")
    print("✅ Visuelle Validierungs-Indikatoren")
    print("✅ Error-Nachrichten Anzeige")
    print("✅ Validierungs-Reset-Funktionalität")
    print("✅ Erweiterte Speichern-Validierung")
    
    print("\n🎯 Task 2.3: Add-Funktionalität mit erweiterter Validierung - ABGESCHLOSSEN")
    print("✅ Alle Test-Kriterien erfüllt")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 