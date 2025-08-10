#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vereinfachte externe Test-Datei für Schnellabrechnung
Funktioniert ohne Abhängigkeiten zur Hauptklasse
"""

import sys
import os
import math
from datetime import datetime

def safe_float(val):
    """Sichere Float-Konvertierung"""
    if val is None or str(val).strip() == '' or str(val).lower() == 'nan' or (isinstance(val, float) and math.isnan(val)):
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

class SchnellabrechnungSimpleTester:
    """
    Vereinfachte Test-Klasse für Schnellabrechnung
    Funktioniert ohne Hauptklasse-Abhängigkeiten
    """
    
    def __init__(self):
        self.test_results = []
        
    def test_schnellabrechnung(self, fahrer, fahrzeug, kalenderwochen, deal_typ, tank_prozent, einsteiger_prozent, expense_fix):
        """
        Testet die Schnellabrechnung für mehrere Kalenderwochen
        
        Args:
            fahrer: Fahrername
            fahrzeug: Fahrzeugname  
            kalenderwochen: Liste der KW-Strings ["KW26", "KW27", ...]
            deal_typ: "P", "%", oder "C"
            tank_prozent: Prozentsatz vom Umsatz für Tank (0.0-1.0)
            einsteiger_prozent: Prozentsatz vom Umsatz für Einsteiger (0.0-1.0)
            expense_fix: Fixer Betrag für Ausgaben
        """
        try:
            print(f"\n🚀 Schnellabrechnung Test gestartet:")
            print(f"  Fahrer: {fahrer}")
            print(f"  Fahrzeug: {fahrzeug}")
            print(f"  Kalenderwochen: {kalenderwochen}")
            print(f"  Deal-Typ: {deal_typ}")
            print(f"  Tank-Prozent: {tank_prozent*100}%")
            print(f"  Einsteiger-Prozent: {einsteiger_prozent*100}%")
            print(f"  Fixe Ausgaben: {expense_fix}€")
            
            results = []
            
            for kw in kalenderwochen:
                print(f"\n📊 Verarbeite {kw}...")
                
                # 1. Daten für diese KW laden (Simulation)
                kw_data = self._load_mock_week_data(kw)
                if not kw_data:
                    print(f"  ⚠️ Keine Daten für {kw} gefunden")
                    continue
                    
                # 2. Umsatz berechnen
                total_umsatz = self._calculate_total_umsatz(kw_data)
                print(f"  💰 Gesamtumsatz: {total_umsatz:.2f}€")
                
                # 3. Auto-Fill basierend auf Deal-Typ
                tank_value, einsteiger_value = self._calculate_auto_fill(
                    total_umsatz, deal_typ, tank_prozent, einsteiger_prozent
                )
                
                # 4. Ergebnis berechnen
                ergebnis = self._calculate_result(total_umsatz, tank_value, einsteiger_value, expense_fix, deal_typ)
                
                # 5. Ergebnis sammeln
                result = {
                    'kalenderwoche': kw,
                    'umsatz': total_umsatz,
                    'tank': tank_value,
                    'einsteiger': einsteiger_value,
                    'expense': expense_fix,
                    'ergebnis': ergebnis,
                    'deal_typ': deal_typ
                }
                results.append(result)
                
                print(f"  ✅ {kw} abgeschlossen:")
                print(f"    Tank: {tank_value:.2f}€")
                print(f"    Einsteiger: {einsteiger_value:.2f}€")
                print(f"    Ergebnis: {ergebnis:.2f}€")
            
            print(f"\n🎉 Schnellabrechnung Test abgeschlossen für {len(results)} Wochen")
            self.test_results.extend(results)
            return results
            
        except Exception as e:
            print(f"❌ Fehler bei Schnellabrechnung Test: {e}")
            return []
    
    def clear_test_results(self):
        """Leert die Testergebnisse"""
        self.test_results = []
        print("🧹 Testergebnisse geleert")
    
    def _load_mock_week_data(self, kw):
        """Lädt Mock-Daten für eine spezifische KW"""
        try:
            print(f"  📂 Lade Mock-Daten für {kw}...")
            
            # Verschiedene Mock-Daten für verschiedene Wochen
            mock_data_sets = {
                "KW26": [
                    {'type': 'summary', 'label': 'Taxi', 'details': [{'label': 'Real', 'value': '450.00 €'}]},
                    {'type': 'summary', 'label': 'Uber', 'details': [{'label': 'Echter Umsatz', 'value': '380.00 €'}]},
                    {'type': 'summary', 'label': 'Bolt', 'details': [{'label': 'Echter Umsatz', 'value': '290.00 €'}]}
                ],
                "KW27": [
                    {'type': 'summary', 'label': 'Taxi', 'details': [{'label': 'Real', 'value': '520.00 €'}]},
                    {'type': 'summary', 'label': 'Uber', 'details': [{'label': 'Echter Umsatz', 'value': '410.00 €'}]},
                    {'type': 'summary', 'label': 'Bolt', 'details': [{'label': 'Echter Umsatz', 'value': '320.00 €'}]}
                ],
                "KW28": [
                    {'type': 'summary', 'label': 'Taxi', 'details': [{'label': 'Real', 'value': '480.00 €'}]},
                    {'type': 'summary', 'label': 'Uber', 'details': [{'label': 'Echter Umsatz', 'value': '360.00 €'}]},
                    {'type': 'summary', 'label': 'Bolt', 'details': [{'label': 'Echter Umsatz', 'value': '280.00 €'}]}
                ],
                "KW29": [
                    {'type': 'summary', 'label': 'Taxi', 'details': [{'label': 'Real', 'value': '550.00 €'}]},
                    {'type': 'summary', 'label': 'Uber', 'details': [{'label': 'Echter Umsatz', 'value': '430.00 €'}]},
                    {'type': 'summary', 'label': 'Bolt', 'details': [{'label': 'Echter Umsatz', 'value': '340.00 €'}]}
                ],
                "KW30": [
                    {'type': 'summary', 'label': 'Taxi', 'details': [{'label': 'Real', 'value': '490.00 €'}]},
                    {'type': 'summary', 'label': 'Uber', 'details': [{'label': 'Echter Umsatz', 'value': '390.00 €'}]},
                    {'type': 'summary', 'label': 'Bolt', 'details': [{'label': 'Echter Umsatz', 'value': '300.00 €'}]}
                ],
                "KW31": [
                    {'type': 'summary', 'label': 'Taxi', 'details': [{'label': 'Real', 'value': '600.00 €'}]},
                    {'type': 'summary', 'label': 'Uber', 'details': [{'label': 'Echter Umsatz', 'value': '450.00 €'}]},
                    {'type': 'summary', 'label': 'Bolt', 'details': [{'label': 'Echter Umsatz', 'value': '380.00 €'}]}
                ]
            }
            
            # Verwende spezifische Daten oder Standard-Daten
            if kw in mock_data_sets:
                mock_data = mock_data_sets[kw]
            else:
                # Standard-Daten für unbekannte Wochen
                mock_data = [
                    {'type': 'summary', 'label': 'Taxi', 'details': [{'label': 'Real', 'value': '500.00 €'}]},
                    {'type': 'summary', 'label': 'Uber', 'details': [{'label': 'Echter Umsatz', 'value': '400.00 €'}]},
                    {'type': 'summary', 'label': 'Bolt', 'details': [{'label': 'Echter Umsatz', 'value': '300.00 €'}]}
                ]
            
            print(f"  ✅ Mock-Daten für {kw} geladen")
            return mock_data
            
        except Exception as e:
            print(f"Fehler beim Laden der Mock-Daten für {kw}: {e}")
            return None
    
    def _calculate_total_umsatz(self, kw_data):
        """Berechnet den Gesamtumsatz aus allen Plattformen"""
        total = 0.0
        
        for platform_data in kw_data:
            if platform_data.get('type') == 'summary':
                # Umsatz aus Details extrahieren
                details = platform_data.get('details', [])
                for detail in details:
                    if detail.get('label') in ['Echter Umsatz', 'Total', 'Real']:
                        value_str = detail.get('value', '0')
                        # Bereinige String und konvertiere zu Float
                        value = safe_float(value_str.replace('€', '').replace(' ', ''))
                        total += value
                        break
        
        return total
    
    def _calculate_auto_fill(self, total_umsatz, deal_typ, tank_prozent, einsteiger_prozent):
        """Berechnet Auto-Fill Werte basierend auf Deal-Typ und Umsatz"""
        
        if deal_typ == "P":
            # P-Deal: Tank und Einsteiger als Prozentsatz vom Umsatz (nicht Einkommen)
            tank_value = total_umsatz * tank_prozent
            einsteiger_value = total_umsatz * einsteiger_prozent
            
        elif deal_typ == "%":
            # %-Deal: 50% von jedem Umsatz
            tank_value = total_umsatz * tank_prozent
            einsteiger_value = total_umsatz * einsteiger_prozent
            
        elif deal_typ == "C":
            # C-Deal: Individuelle Prozentsätze
            tank_value = total_umsatz * tank_prozent
            einsteiger_value = total_umsatz * einsteiger_prozent
            
        else:
            # Fallback: Standard-Prozentsätze
            tank_value = total_umsatz * 0.15  # 15% für Tank
            einsteiger_value = total_umsatz * 0.25  # 25% für Einsteiger
        
        return tank_value, einsteiger_value
    
    def _calculate_result(self, total_umsatz, tank_value, einsteiger_value, expense_fix, deal_typ):
        """Berechnet das finale Ergebnis"""
        
        if deal_typ == "P":
            # P-Deal: Pauschale + Grenzzuschlag - Abzüge
            pauschale = 500
            umsatzgrenze = 1200
            income = pauschale
            
            if total_umsatz > umsatzgrenze:
                bonus = (total_umsatz - umsatzgrenze) * 0.1
                income += bonus
            
            result = income - tank_value - einsteiger_value - expense_fix
            
        elif deal_typ == "%":
            # %-Deal: 50% vom Umsatz - Abzüge
            income = total_umsatz * 0.5
            result = income - tank_value - einsteiger_value - expense_fix
            
        elif deal_typ == "C":
            # C-Deal: Individuelle Berechnung (60% vom Umsatz)
            income = total_umsatz * 0.6
            result = income - tank_value - einsteiger_value - expense_fix
            
        else:
            result = total_umsatz - tank_value - einsteiger_value - expense_fix
        
        return max(0, result)  # Nicht negativ
    
    def print_test_summary(self):
        """Gibt eine Zusammenfassung aller Tests aus"""
        if not self.test_results:
            print("📊 Keine Testergebnisse vorhanden")
            return
        
        print(f"\n📊 TEST-ZUSAMMENFASSUNG")
        print("=" * 60)
        
        total_ergebnis = 0
        total_umsatz = 0
        
        for result in self.test_results:
            print(f"{result['kalenderwoche']}:")
            print(f"  Umsatz: {result['umsatz']:.2f}€")
            print(f"  Tank: {result['tank']:.2f}€")
            print(f"  Einsteiger: {result['einsteiger']:.2f}€")
            print(f"  Ausgaben: {result['expense']:.2f}€")
            print(f"  Ergebnis: {result['ergebnis']:.2f}€")
            print(f"  Deal-Typ: {result['deal_typ']}")
            print()
            
            total_ergebnis += result['ergebnis']
            total_umsatz += result['umsatz']
        
        print("=" * 60)
        print(f"📈 GESAMT:")
        print(f"  Wochen: {len(self.test_results)}")
        print(f"  Gesamtumsatz: {total_umsatz:.2f}€")
        print(f"  Gesamtergebnis: {total_ergebnis:.2f}€")
        print(f"  Durchschnitt pro Woche: {total_ergebnis/len(self.test_results):.2f}€")
    
    def export_results_to_csv(self, filename="schnellabrechnung_results.csv"):
        """Exportiert Ergebnisse in CSV-Datei"""
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['kalenderwoche', 'umsatz', 'tank', 'einsteiger', 'expense', 'ergebnis', 'deal_typ']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in self.test_results:
                    writer.writerow(result)
            
            print(f"✅ Ergebnisse exportiert nach {filename}")
            
        except Exception as e:
            print(f"❌ Fehler beim Export: {e}")

def main():
    """Hauptfunktion für Tests"""
    print("🧪 SCHNELLABRECHNUNG SIMPLE TESTER")
    print("=" * 60)
    
    tester = SchnellabrechnungSimpleTester()
    
    # Test 1: P-Deal
    print("\n🔵 TEST 1: P-Deal")
    kalenderwochen = ["KW26", "KW27", "KW28"]
    tester.test_schnellabrechnung(
        fahrer="Max Mustermann",
        fahrzeug="W132CTX",
        kalenderwochen=kalenderwochen,
        deal_typ="P",
        tank_prozent=0.15,  # 15% vom Einkommen
        einsteiger_prozent=0.25,  # 25% vom Einkommen
        expense_fix=12.50
    )
    
    # Zwischenergebnisse leeren
    tester.clear_test_results()
    
    # Test 2: %-Deal
    print("\n🟡 TEST 2: %-Deal")
    tester.test_schnellabrechnung(
        fahrer="Max Mustermann",
        fahrzeug="W132CTX",
        kalenderwochen=["KW29", "KW30"],
        deal_typ="%",
        tank_prozent=0.10,  # 10% vom Umsatz
        einsteiger_prozent=0.20,  # 20% vom Umsatz
        expense_fix=15.00
    )
    
    # Zwischenergebnisse leeren
    tester.clear_test_results()
    
    # Test 3: C-Deal
    print("\n🟢 TEST 3: C-Deal")
    tester.test_schnellabrechnung(
        fahrer="Max Mustermann",
        fahrzeug="W132CTX",
        kalenderwochen=["KW31"],
        deal_typ="C",
        tank_prozent=0.12,  # 12% vom Umsatz
        einsteiger_prozent=0.18,  # 18% vom Umsatz
        expense_fix=18.00
    )
    
    # Zusammenfassung ausgeben
    tester.print_test_summary()
    
    # Ergebnisse exportieren
    tester.export_results_to_csv()

if __name__ == "__main__":
    main()
