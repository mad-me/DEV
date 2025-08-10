#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Externe Test-Datei für Schnellabrechnung
Kann unabhängig vom Hauptprogramm ausgeführt werden
"""

import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import math
import configparser
from typing import List, Dict, Any, Optional

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import der Hauptklasse
from abrechnungsseite_qml_optimized import AbrechnungsSeiteQML, safe_float

class TestConfig:
    """Konfigurationsklasse für die Schnellabrechnung-Tests"""
    
    def __init__(self, config_file: str = "test_config.ini"):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Lädt die Konfiguration aus der INI-Datei"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
                print(f"Konfiguration geladen: {self.config_file}")
                # Mindest-Schwelle für Fuzzy-Matching durchsetzen, um Fehlmatches zu vermeiden
                if 'Fuzzy_Matching' not in self.config:
                    self.config['Fuzzy_Matching'] = {}
                try:
                    current_min = int(self.config['Fuzzy_Matching'].get('min_match_score', '65'))
                except Exception:
                    current_min = 65
                if current_min < 65:
                    self.config['Fuzzy_Matching']['min_match_score'] = '65'
                    with open(self.config_file, 'w', encoding='utf-8') as configfile:
                        self.config.write(configfile)
            else:
                print(f"Konfigurationsdatei nicht gefunden: {self.config_file}")
                self.create_default_config()
        except Exception as e:
            print(f"Fehler beim Laden der Konfiguration: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Erstellt eine Standard-Konfiguration"""
        self.config['Test'] = {
            'fahrer': 'Awes Ahmadeey',
            'fahrzeug': 'W135CTX',
            'kalenderwochen': 'KW22,KW23,KW24,KW25,KW26,KW27,KW28,KW29,KW30,KW31',
            'tank_prozent': '0.13',
            'einsteiger_prozent': '0.20',
            'expense_fix': '0.00'
        }
        self.config['Deals'] = {
            'p_deal_pauschale': '650.0',
            'p_deal_umsatzgrenze': '1200.0',
            'p_deal_bonus_prozent': '0.1',
            'percent_deal_anteil': '0.5',
            'percent_deal_einsteiger_faktor': '0.5',
            'custom_deal_anteil': '0.6'
        }
        self.config['Garage'] = {
            'monatliche_garage': '80.0',
            'garage_faktor': '0.5',
            'max_montage_pro_monat': '5'
        }
        self.config['Umsatz'] = {
            'max_umsatz_pro_fahrt': '250',
            'min_umsatz_pro_fahrt': '-250',
            'umsatz_filter_aktiv': 'true'
        }
        self.config['Fuzzy_Matching'] = {
            'min_match_score': '65',
            'max_distance': '3',
            'arabic_name_bonus': '20'
        }
        self.config['Security'] = {
            'sql_injection_protection': 'true',
            'input_validation': 'true',
            'max_kalenderwochen': '52',
            'max_fahrer_name_length': '100',
            'max_fahrzeug_name_length': '50'
        }
        print(" Standard-Konfiguration erstellt")
    
    def get_test_params(self) -> Dict[str, Any]:
        """Gibt die Test-Parameter zurück"""
        if 'Test' not in self.config:
            return {}
        
        test_section = self.config['Test']
        return {
            'fahrer': test_section.get('fahrer', 'Awes Ahmadeey'),
            'fahrzeug': test_section.get('fahrzeug', 'W135CTX'),
            'kalenderwochen': test_section.get('kalenderwochen', 'KW22,KW23,KW24,KW25,KW26,KW27,KW28,KW29,KW30,KW31').split(','),
            'tank_prozent': float(test_section.get('tank_prozent', '0.13')),
            'einsteiger_prozent': float(test_section.get('einsteiger_prozent', '0.20')),
            'expense_fix': float(test_section.get('expense_fix', '0.00'))
        }
    
    def get_deal_params(self) -> Dict[str, Any]:
        """Gibt die Deal-Parameter zurück"""
        if 'Deals' not in self.config:
            return {}
        
        deals_section = self.config['Deals']
        return {
            'p_deal_pauschale': float(deals_section.get('p_deal_pauschale', '650.0')),
            'p_deal_umsatzgrenze': float(deals_section.get('p_deal_umsatzgrenze', '1200.0')),
            'p_deal_bonus_prozent': float(deals_section.get('p_deal_bonus_prozent', '0.1')),
            'percent_deal_anteil': float(deals_section.get('percent_deal_anteil', '0.5')),
            'percent_deal_einsteiger_faktor': float(deals_section.get('percent_deal_einsteiger_faktor', '0.5')),
            'custom_deal_anteil': float(deals_section.get('custom_deal_anteil', '0.6'))
        }
    
    def get_garage_params(self) -> Dict[str, Any]:
        """Gibt die Garage-Parameter zurück"""
        if 'Garage' not in self.config:
            return {}
        
        garage_section = self.config['Garage']
        return {
            'monatliche_garage': float(garage_section.get('monatliche_garage', '80.0')),
            'garage_faktor': float(garage_section.get('garage_faktor', '0.5')),
            'max_montage_pro_monat': int(garage_section.get('max_montage_pro_monat', '5'))
        }
    
    def get_umsatz_params(self) -> Dict[str, Any]:
        """Gibt die Umsatz-Parameter zurück"""
        if 'Umsatz' not in self.config:
            return {}
        
        umsatz_section = self.config['Umsatz']
        return {
            'max_umsatz_pro_fahrt': float(umsatz_section.get('max_umsatz_pro_fahrt', '250')),
            'min_umsatz_pro_fahrt': float(umsatz_section.get('min_umsatz_pro_fahrt', '-250')),
            'umsatz_filter_aktiv': umsatz_section.get('umsatz_filter_aktiv', 'true').lower() == 'true'
        }
    
    def get_fuzzy_params(self) -> Dict[str, Any]:
        """Gibt die Fuzzy-Matching-Parameter zurück"""
        if 'Fuzzy_Matching' not in self.config:
            return {}
        
        fuzzy_section = self.config['Fuzzy_Matching']
        return {
            'min_match_score': int(fuzzy_section.get('min_match_score', '50')),
            'max_distance': int(fuzzy_section.get('max_distance', '3')),
            'arabic_name_bonus': int(fuzzy_section.get('arabic_name_bonus', '20'))
        }
    
    def get_security_params(self) -> Dict[str, Any]:
        """Gibt die Sicherheits-Parameter zurück"""
        if 'Security' not in self.config:
            return {}
        
        security_section = self.config['Security']
        return {
            'sql_injection_protection': security_section.get('sql_injection_protection', 'true').lower() == 'true',
            'input_validation': security_section.get('input_validation', 'true').lower() == 'true',
            'max_kalenderwochen': int(security_section.get('max_kalenderwochen', '52')),
            'max_fahrer_name_length': int(security_section.get('max_fahrer_name_length', '100')),
            'max_fahrzeug_name_length': int(security_section.get('max_fahrzeug_name_length', '50'))
        }
    
    def save_config(self):
        """Speichert die aktuelle Konfiguration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            print(f" Konfiguration gespeichert: {self.config_file}")
        except Exception as e:
            print(f" Fehler beim Speichern der Konfiguration: {e}")
    
    def update_test_params(self, **kwargs):
        """Aktualisiert Test-Parameter"""
        if 'Test' not in self.config:
            self.config['Test'] = {}
        
        for key, value in kwargs.items():
            self.config['Test'][key] = str(value)
        
        self.save_config()
        print(" Test-Parameter aktualisiert")
    
    def print_current_config(self):
        """Zeigt die aktuelle Konfiguration an"""
        print("\n AKTUELLE KONFIGURATION:")
        print("=" * 50)
        
        for section in self.config.sections():
            print(f"\n[{section}]")
            for key, value in self.config[section].items():
                print(f"  {key} = {value}")
        
        print("\n" + "=" * 50)

class SchnellabrechnungTester:
    """
    Externe Test-Klasse für Schnellabrechnung
    Kann unabhängig vom Hauptprogramm verwendet werden
    """
    
    # Whitelist für erlaubte Tabellennamen (Sicherheit gegen SQL-Injection)
    ALLOWED_TABLES = {f"report_KW{i}" for i in range(1, 53)}
    
    def __init__(self, config_file: str = "test_config.ini"):
        self.abrechnungs_backend = None
        self.test_results = []
        self.config = TestConfig(config_file)
        self.deal_params = self.config.get_deal_params()
        self.garage_params = self.config.get_garage_params()
        self.umsatz_params = self.config.get_umsatz_params()
        self.fuzzy_params = self.config.get_fuzzy_params()
        self.security_params = self.config.get_security_params()
        
    def initialize_backend(self):
        """Initialisiert das Backend für Tests"""
        try:
            print(" Initialisiere Abrechnungs-Backend...")
            
            # Unterdrücke QML-Logs während der Initialisierung
            import os
            original_qt_logging = os.environ.get('QT_LOGGING_RULES', '')
            os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
            
            # Unterdrücke stdout während der Backend-Initialisierung
            import sys
            from io import StringIO
            
            # Temporär stdout umleiten
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                self.abrechnungs_backend = AbrechnungsSeiteQML()
                success = True
            finally:
                # stdout wiederherstellen
                sys.stdout = old_stdout
                # Qt-Logging wiederherstellen
                if original_qt_logging:
                    os.environ['QT_LOGGING_RULES'] = original_qt_logging
                else:
                    os.environ.pop('QT_LOGGING_RULES', None)
            
            if success:
                print(" Backend erfolgreich initialisiert")
                return True
            else:
                print(" Backend-Initialisierung fehlgeschlagen")
                return False
                
        except Exception as e:
            print(f" Fehler beim Initialisieren des Backends: {e}")
            return False
    
    def test_schnellabrechnung(self, fahrer, fahrzeug, kalenderwochen, tank_prozent, einsteiger_prozent, expense_fix):
        """
        Testet die Schnellabrechnung für mehrere Kalenderwochen
        
        Args:
            fahrer: Fahrername
            fahrzeug: Fahrzeugname  
            kalenderwochen: Liste der KW-Strings ["KW26", "KW27", ...]
            tank_prozent: Prozentsatz vom Umsatz für Tank (0.0-1.0)
            einsteiger_prozent: Prozentsatz vom Umsatz für Einsteiger (0.0-1.0)
            expense_fix: Fixer Betrag für Ausgaben
        """
        if not self.abrechnungs_backend:
            print(" Backend nicht initialisiert")
            return []
        
        try:
            print(f"\n Schnellabrechnung Test gestartet:")
            print(f"  Fahrer: {fahrer}")
            print(f"  Fahrzeug: {fahrzeug}")
            print(f"  Kalenderwochen: {kalenderwochen}")
            print(f"  Tank-Prozent: {tank_prozent*100}%")
            print(f"  Einsteiger-Prozent: {einsteiger_prozent*100}%")
            print(f"  Fixe Ausgaben: {expense_fix}€")
            
            # Deal-Typ aus Datenbank laden
            deal_typ, garage, pauschale, umsatzgrenze = self._load_deal_from_database(fahrer)
            print(f"   Deal-Typ aus Datenbank: {deal_typ}")
            
            results = []
            
            for kw in kalenderwochen:
                print(f"\n Verarbeite {kw}...")
                
                # 1. Daten für diese KW laden
                kw_data = self._load_week_data(fahrer, fahrzeug, kw)
                if not kw_data:
                    print(f"   Keine Daten für {kw} gefunden")
                    continue
                    
                # 2. Umsatz berechnen (Plattform-Summe)
                total_umsatz = self._calculate_total_umsatz(kw_data)
                
                # 3. HeadCard-Werte berechnen (wie in echter Abrechnung) – maßgeblich für Anzeige
                headcard_values = self._calculate_headcard_values(kw_data)
                headcard_umsatz = headcard_values['headcard_umsatz']
                credit_card = headcard_values['headcard_credit_card']
                
                # WICHTIG: Für QML-Parsing – "Gesamtumsatz" = HeadCard-Umsatz (Uber + Bolt + Taxi echt)
                print(f"   Gesamtumsatz: {headcard_umsatz:.2f}€")
                # Optional: zusätzliche Transparenz
                print(f"   Plattform-Umsatz-Summe: {total_umsatz:.2f}€")
                print(f"   Credit Card: {credit_card:.2f}€")
                print(f"   HeadCard Umsatz: {headcard_umsatz:.2f}€")
                print(f"   HeadCard Bargeld: {headcard_values['headcard_bargeld']:.2f}€")
                print(f"   HeadCard Trinkgeld: {headcard_values['headcard_trinkgeld']:.2f}€")
                
                # 4. Auto-Fill basierend auf Deal-Typ
                tank_value, einsteiger_value = self._calculate_auto_fill(
                    total_umsatz, deal_typ, tank_prozent, einsteiger_prozent, pauschale, umsatzgrenze
                )
                
                # 5. Garage-Abzug berechnen
                garage_abzug = self._calculate_garage_abzug(garage, kw)
                
                # 6. Echte Abrechnungslogik verwenden
                print(f"\n ERGEBNIS-BERECHNUNG STARTET:")
                
                # Anteil berechnen
                anteil = self._calculate_anteil_once(total_umsatz, deal_typ, pauschale, umsatzgrenze, einsteiger_prozent)
                print(f"    ANTEIL: {anteil:.2f}€")
                
                # Income berechnen
                income = self._calculate_income_once(anteil, tank_value, einsteiger_value, expense_fix, garage_abzug, deal_typ, tank_prozent, total_umsatz)
                print(f"    INCOME: {income:.2f} EUR")
                
                # Abrechnungsergebnis berechnen
                abrechnungsergebnis = self._calculate_abrechnungsergebnis_once(
                    credit_card, income, deal_typ, headcard_values['headcard_trinkgeld']
                )
                print(f"    ABRECHNUNGSERGEBNIS: {abrechnungsergebnis:.2f}€")
                
                print(f"\n ERGEBNIS-BERECHNUNG ABGESCHLOSSEN:")
                print(f"    Anteil: {anteil:.2f}€")
                print(f"    Income: {income:.2f} EUR")
                print(f"    Abrechnungsergebnis: {abrechnungsergebnis:.2f}€")
                
                # 7. Ergebnis sammeln
                result = {
                    'kalenderwoche': kw,
                    'umsatz': total_umsatz,
                    'credit_card': credit_card,
                    'anteil': anteil,
                    'tank': tank_value,
                    'einsteiger': einsteiger_value,
                    'garage': garage_abzug,
                    'expense': expense_fix,
                    'income': income,
                    'abrechnungsergebnis': abrechnungsergebnis,
                    'deal_typ': deal_typ
                }
                results.append(result)
                
                print(f"   {kw} abgeschlossen - Abrechnungsergebnis: {result['abrechnungsergebnis']:.2f}€")
            
            print(f"\n Schnellabrechnung Test abgeschlossen für {len(results)} Wochen")
            self.test_results.extend(results)
            return results
            
        except Exception as e:
            print(f" Fehler bei Schnellabrechnung Test: {e}")
            return []
    
    def _validate_table_name(self, kw):
        """Validiert und erstellt sicheren Tabellennamen (Schutz gegen SQL-Injection)"""
        kw_nummer = kw.replace("KW", "")
        table_name = f"report_KW{kw_nummer}"
        
        if table_name not in self.ALLOWED_TABLES:
            raise ValueError(f"Ungültiger Tabellenname: {table_name}. Erlaubte Tabellen: {sorted(self.ALLOWED_TABLES)}")
        
        return table_name
    
    def _load_week_data(self, fahrer, fahrzeug, kw):
        """Lädt echte Daten für eine spezifische KW aus der Datenbank"""
        try:
            print(f"   Lade echte Daten für {kw}...")
            
            # Extrahiere Kennzeichen-Nummer aus Fahrzeug
            kennzeichen_nummer = "".join(filter(str.isdigit, fahrzeug))
            # Sichere Tabellennamen-Validierung
            table_name = self._validate_table_name(kw)
            
            # Daten-Container für alle Plattformen
            platform_data = []
            
            # 1. 40100-Daten laden
            db_path_40100 = os.path.abspath(os.path.join("SQL", "40100.sqlite"))
            try:
                conn = sqlite3.connect(db_path_40100)
                df_40100 = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE Fahrzeug LIKE ?", conn, params=[f"%{kennzeichen_nummer}%"])
                if not df_40100.empty:
                    print(f"     40100: {len(df_40100)} Datensätze gefunden")
                    # 40100-Daten verarbeiten
                    if "Umsatz" in df_40100.columns:
                        df_40100["Umsatz"] = pd.to_numeric(df_40100["Umsatz"].astype(str).str.replace(",", "."), errors="coerce")
                        umsatz_mask = (df_40100["Umsatz"] <= 250) & (df_40100["Umsatz"] >= -250)
                        umsatz_40100 = df_40100.loc[umsatz_mask, "Umsatz"].sum()
                        
                        # Trinkgeld berechnen (gefiltert wie in echter Abrechnung)
                        trinkgeld_fuer_umsatz_40100 = df_40100["Trinkgeld"].sum() if "Trinkgeld" in df_40100.columns else 0
                        echter_umsatz_40100 = umsatz_40100 - trinkgeld_fuer_umsatz_40100
                        
                        # Trinkgeld für Anzeige (gefiltert wie in echter Abrechnung)
                        trinkgeld_mask = umsatz_mask
                        if "Buchungsart" in df_40100.columns:
                            trinkgeld_mask = trinkgeld_mask & ~df_40100["Buchungsart"].str.contains("Bar", na=False)
                        trinkgeld_40100 = df_40100.loc[trinkgeld_mask, "Trinkgeld"].sum() if "Trinkgeld" in df_40100.columns else 0
                        
                        bargeld_40100 = df_40100.loc[umsatz_mask, "Bargeld"].sum() if "Bargeld" in df_40100.columns else 0
                        platform_data.append({
                             'type': 'summary',
                             'label': '40100',
                             'details': [
                                 {'label': 'Echter Umsatz', 'value': f'{echter_umsatz_40100:.2f} €'},
                                 {'label': 'Bargeld', 'value': f'{bargeld_40100:.2f} €'}
                             ]
                         })
                else:
                    print(f"     40100: Keine Daten für {fahrzeug} in {kw}")
            except Exception as e:
                print(f"     40100 Fehler: {e}")
            finally:
                try:
                    conn.close()
                except:
                    pass
            
            # 2. 31300-Daten laden
            db_path_31300 = os.path.abspath(os.path.join("SQL", "31300.sqlite"))
            try:
                conn = sqlite3.connect(db_path_31300)
                df_31300 = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE Fahrzeug LIKE ?", conn, params=[f"%{kennzeichen_nummer}%"])
                if not df_31300.empty:
                    print(f"     31300: {len(df_31300)} Datensätze gefunden")
                    # 31300-Daten verarbeiten
                    if "Gesamt" in df_31300.columns:
                        df_31300['Gesamt'] = pd.to_numeric(df_31300['Gesamt'], errors='coerce')
                        gesamt_mask = (df_31300["Gesamt"] <= 250) & (df_31300["Gesamt"] >= -250)
                        gesamt_31300 = df_31300.loc[gesamt_mask, "Gesamt"].sum()
                        
                        # Trinkgeld berechnen (gefiltert wie in echter Abrechnung)
                        trinkgeld_fuer_umsatz_31300 = df_31300["Trinkgeld"].sum() if "Trinkgeld" in df_31300.columns else 0
                        echter_umsatz_31300 = gesamt_31300 - trinkgeld_fuer_umsatz_31300
                        
                        # Trinkgeld für Anzeige (gefiltert wie in echter Abrechnung)
                        trinkgeld_mask = gesamt_mask
                        if "Buchungsart" in df_31300.columns:
                            trinkgeld_mask = trinkgeld_mask & ~df_31300["Buchungsart"].str.contains("Bar", na=False)
                        trinkgeld_31300 = df_31300.loc[trinkgeld_mask, "Trinkgeld"].sum() if "Trinkgeld" in df_31300.columns else 0
                        
                        # Bargeld berechnen
                        bargeld_31300 = df_31300.loc[df_31300["Buchungsart"].str.contains("Bar", na=False), "Gesamt"].sum() if "Buchungsart" in df_31300.columns and "Gesamt" in df_31300.columns else 0
                        
                        # WICHTIG: Für HeadCard verwenden wir den ROHEM Umsatz (wie in echter Abrechnung)
                        # Für die Anzeige verwenden wir den echten Umsatz
                        platform_data.append({
                            'type': 'summary',
                            'label': '31300',
                            'details': [
                                {'label': 'Echter Umsatz', 'value': f'{echter_umsatz_31300:.2f} €'},
                                {'label': 'Bargeld', 'value': f'{bargeld_31300:.2f} €'},
                                {'label': 'Trinkgeld', 'value': f'{trinkgeld_31300:.2f} €'},
                                {'label': 'Roher Umsatz', 'value': f'{gesamt_31300:.2f} €'}  # Für HeadCard
                            ]
                        })
                else:
                    print(f"     31300: Keine Daten für {fahrzeug} in {kw}")
            except Exception as e:
                print(f"     31300 Fehler: {e}")
            finally:
                try:
                    conn.close()
                except:
                    pass
            
            # 3. Uber und Bolt Daten laden (mit echten Matching-Logik)
            for db_name, db_file in [("Uber", "uber.sqlite"), ("Bolt", "bolt.sqlite")]:
                db_path = os.path.abspath(os.path.join("SQL", db_file))
                try:
                    conn = sqlite3.connect(db_path)
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    
                    if db_name == "Uber":
                        if "first_name" in df.columns and "last_name" in df.columns:
                            df["_combo_name"] = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).apply(self._clean_name)
                            search_clean = self._clean_name(fahrer)
                            df["_match"] = df["_combo_name"].apply(lambda name: self._fuzzy_match_score(search_clean, name))
                            max_score = df["_match"].max() if not df.empty else 0
                            min_score = int(self.fuzzy_params.get('min_match_score', 50))
                            if max_score >= min_score:
                                df = df[df["_match"] == max_score]
                                df = df.iloc[[0]] if len(df) > 1 else df
                                try:
                                    matched_label = df["_combo_name"].iloc[0]
                                except Exception:
                                    matched_label = "?"
                                # Uber-Daten verarbeiten (erst Daten anhängen, dann loggen – vermeidet Abbruch bei Encoding-Problemen)
                                gross_total = df["gross_total"].sum() if "gross_total" in df.columns else 0
                                cash_collected = df["cash_collected"].sum() if "cash_collected" in df.columns else 0
                                tips = df["tips"].sum() if "tips" in df.columns else 0
                                
                                platform_data.append({
                                    'type': 'summary',
                                    'label': 'Uber',
                                    'details': [
                                        {'label': 'Echter Umsatz', 'value': f'{gross_total:.2f} €'},
                                        {'label': 'Bargeld', 'value': f'{cash_collected:.2f} €'},
                                        {'label': 'Trinkgeld', 'value': f'{tips:.2f} €'}
                                    ]
                                })
                                # Robustes Logging ohne Emojis (Windows cp1252)
                                try:
                                    print(f"     Uber: {len(df)} Datensätze gefunden (Score: {max_score:.1f})")
                                    print(f"     OK Uber-Match: '{search_clean}' -> '{matched_label}' (Score: {max_score:.1f})")
                                except Exception:
                                    pass
                            else:
                                print(f"     Uber: Keine guten Matches für {fahrer} in {kw} (bester Score: {max_score:.1f})")
                        else:
                            print(f"     Uber: Keine first_name/last_name Spalten in {kw}")
                    elif db_name == "Bolt":
                        if "driver_name" in df.columns:
                            df["_driver_name_clean"] = df["driver_name"].apply(self._clean_name)
                            search_clean = self._clean_name(fahrer)
                            df["_match"] = df["_driver_name_clean"].apply(lambda name: self._fuzzy_match_score(search_clean, name))
                            max_score = df["_match"].max() if not df.empty else 0
                            min_score = int(self.fuzzy_params.get('min_match_score', 50))
                            if max_score >= min_score:
                                df = df[df["_match"] == max_score]
                                df = df.iloc[[0]] if len(df) > 1 else df
                                try:
                                    matched_label = df["_driver_name_clean"].iloc[0]
                                except Exception:
                                    matched_label = "?"
                                # Bolt-Daten verarbeiten (erst Daten anhängen, dann loggen)
                                net_earnings = df["net_earnings"].sum() if "net_earnings" in df.columns else 0
                                rider_tips = df["rider_tips"].sum() if "rider_tips" in df.columns else 0
                                cash_collected = df["cash_collected"].sum() if "cash_collected" in df.columns else 0
                                echter_umsatz_bolt = net_earnings - rider_tips
                                
                                platform_data.append({
                                    'type': 'summary',
                                    'label': 'Bolt',
                                    'details': [
                                        {'label': 'Echter Umsatz', 'value': f'{echter_umsatz_bolt:.2f} €'},
                                        {'label': 'Bargeld', 'value': f'{cash_collected:.2f} €'},
                                        {'label': 'Trinkgeld', 'value': f'{rider_tips:.2f} €'}
                                    ]
                                })
                                try:
                                    print(f"     Bolt: {len(df)} Datensätze gefunden (Score: {max_score:.1f})")
                                    print(f"     OK Bolt-Match: '{search_clean}' -> '{matched_label}' (Score: {max_score:.1f})")
                                except Exception:
                                    pass
                            else:
                                print(f"     Bolt: Keine guten Matches für {fahrer} in {kw} (bester Score: {max_score:.1f})")
                        else:
                            print(f"     Bolt: Keine driver_name Spalte in {kw}")
                except Exception as e:
                    print(f"     {db_name} Fehler: {e}")
                finally:
                    try:
                        conn.close()
                    except:
                        pass
            
            if platform_data:
                print(f"   Echte Daten für {kw} geladen: {len(platform_data)} Plattformen")
                return platform_data
            else:
                print(f"   Keine echten Daten für {kw} gefunden - verwende Mock-Daten")
                # Fallback zu Mock-Daten wenn keine echten Daten gefunden wurden
                return [
                    {
                        'type': 'summary',
                        'label': 'Taxi',
                        'details': [
                            {'label': 'Real', 'value': '450.00 €'},
                            {'label': 'Bargeld', 'value': '120.00 €'},
                            {'label': 'Trinkgeld', 'value': '25.00 €'}
                        ]
                    },
                    {
                        'type': 'summary', 
                        'label': 'Uber',
                        'details': [
                            {'label': 'Echter Umsatz', 'value': '380.00 €'},
                            {'label': 'Bargeld', 'value': '95.00 €'},
                            {'label': 'Trinkgeld', 'value': '15.00 €'}
                        ]
                    },
                    {
                        'type': 'summary',
                        'label': 'Bolt', 
                        'details': [
                            {'label': 'Echter Umsatz', 'value': '290.00 €'},
                            {'label': 'Bargeld', 'value': '75.00 €'},
                            {'label': 'Trinkgeld', 'value': '10.00 €'}
                        ]
                    }
                ]
            
        except Exception as e:
            print(f" Fehler beim Laden der echten Daten für {kw}: {e}")
            return None
    
    def _load_deal_from_database(self, fahrer):
        """
        Lädt den Deal-Typ aus der Datenbank, genau wie in der echten Abrechnung
        
        Args:
            fahrer: Fahrername
            
        Returns:
            tuple: (deal, garage, pauschale, umsatzgrenze)
        """
        deal = None
        garage = 0.0
        pauschale = 500.0  # Standard-Wert
        umsatzgrenze = 1200.0  # Standard-Wert
        
        try:
            conn_deal = sqlite3.connect("SQL/database.db")
            cursor_deal = conn_deal.cursor()
            cursor_deal.execute("SELECT deal, garage, pauschale, umsatzgrenze FROM deals WHERE name = ?", (fahrer,))
            row = cursor_deal.fetchone()
            if row:
                deal = row[0]
                garage = row[1] if row[1] is not None else 0.0
                pauschale = row[2] if row[2] is not None else 500.0
                umsatzgrenze = row[3] if row[3] is not None else 1200.0
                print(f"   Deal aus Datenbank geladen: {deal}")
                print(f"   Garage: {garage}€")
                print(f"   Pauschale: {pauschale}€")
                print(f"   Umsatzgrenze: {umsatzgrenze}€")
            else:
                print(f"   Kein Deal-Eintrag für {fahrer} gefunden - verwende Standard")
        except Exception as e:
            print(f"   Fehler beim Laden der Deal-Daten: {e}")
            deal = None
            garage = 0.0
            pauschale = 500.0
            umsatzgrenze = 1200.0
        finally:
            try:
                conn_deal.close()
            except:
                pass
                
        return deal, garage, pauschale, umsatzgrenze
    
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
    
    def _calculate_auto_fill(self, total_umsatz, deal_typ, tank_prozent, einsteiger_prozent, pauschale=500, umsatzgrenze=1200):
        """Berechnet Auto-Fill Werte basierend auf Deal-Typ und Umsatz (wie in echter Abrechnung)"""
        
        if deal_typ == "P":
            # P-Deal: Kein automatischer Einsteiger-Wert
            tank_value = total_umsatz * tank_prozent
            einsteiger_value = 0.0
            
        elif deal_typ == "%":
            # %-Deal: Tank und Einsteiger als Prozentsatz vom Umsatz
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
    
    def _set_abrechnung_values(self, tank_value, einsteiger_value, expense_fix, deal_typ):
        """Setzt die Abrechnungswerte (Simulation)"""
        
        print(f"   Werte gesetzt:")
        print(f"    Tank: {tank_value:.2f}€")
        print(f"    Einsteiger: {einsteiger_value:.2f}€")
        print(f"    Ausgaben: {expense_fix:.2f}€")
        print(f"    Deal-Typ: {deal_typ}")
    
    def _simulate_abrechnung(self, fahrer, fahrzeug, kw):
        """Simuliert die Abrechnung ohne Speichern"""
        print(f"   Simuliere Abrechnung für {kw}...")
        # Hier würde die echte Abrechnung stattfinden
        # Für den Test überspringen wir das Speichern
    
    def _calculate_simulated_result(self, total_umsatz, tank_value, einsteiger_value, expense_fix, deal_typ, pauschale=500, umsatzgrenze=1200):
        """Berechnet das simulierte Ergebnis"""
        
        if deal_typ == "P":
            # P-Deal: Pauschale + Grenzzuschlag - Abzüge
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
            # C-Deal: Individuelle Berechnung
            income = total_umsatz * 0.6  # Beispiel: 60% vom Umsatz
            result = income - tank_value - einsteiger_value - expense_fix
            
        else:
            result = total_umsatz - tank_value - einsteiger_value - expense_fix
        
        return max(0, result)  # Nicht negativ
    
    def print_test_summary(self):
        """Gibt eine Zusammenfassung aller Tests aus"""
        if not self.test_results:
            print(" Keine Testergebnisse vorhanden")
            return
        
        print(f"\n TEST-ZUSAMMENFASSUNG")
        print("=" * 60)
        
        total_ergebnis = 0
        total_umsatz = 0
        
        for result in self.test_results:
            print(f"{result['kalenderwoche']}:")
            print(f"  Umsatz: {result['umsatz']:.2f}€")
            print(f"  Credit Card: {result['credit_card']:.2f}€")
            print(f"  Anteil: {result['anteil']:.2f}€")
            print(f"  Tank: {result['tank']:.2f}€")
            print(f"  Einsteiger: {result['einsteiger']:.2f}€")
            print(f"  Garage: {result['garage']:.2f}€")
            print(f"  Ausgaben: {result['expense']:.2f}€")
            print(f"  Income: {result['income']:.2f} EUR")
            print(f"  Abrechnungsergebnis: {result['abrechnungsergebnis']:.2f}€")
            print(f"  Deal-Typ: {result['deal_typ']}")
            print()
            
            total_ergebnis += result['abrechnungsergebnis']
            total_umsatz += result['umsatz']
        
        print("=" * 60)
        print(f" GESAMT:")
        print(f"  Wochen: {len(self.test_results)}")
        print(f"  Gesamtumsatz: {total_umsatz:.2f}€")
        print(f"  Gesamtergebnis: {total_ergebnis:.2f}€")
        print(f"  Durchschnitt pro Woche: {total_ergebnis/len(self.test_results):.2f}€")

    def _clean_name(self, name):
        """Normalisierung konsistent mit test_umsatzmatching.clean_name."""
        import re
        s = str(name).lower()
        s = s.replace("-", " ").replace("_", " ")
        s = re.sub(r"\s+", " ", s)
        s = re.sub(r"\bal\s+", "el ", s)
        s = s.strip()
        return s
    
    def _levenshtein_distance(self, s1, s2):
        """Berechnet die Levenshtein-Distanz zwischen zwei Strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _fuzzy_match_score(self, search_name, target_name, max_distance=3):
        """Konsistenter Score zur Logik in test_umsatzmatching.fuzzy_match_score."""
        if not search_name or not target_name:
            return 0.0

        if search_name == target_name:
            return 100.0

        def clean(s: str) -> str:
            import re
            s = s.lower().replace('-', ' ').replace('_', ' ')
            s = re.sub(r"\s+", " ", s)
            s = re.sub(r"\bal\s+", "el ", s)
            return s.strip()

        search_tokens = clean(search_name).split()
        target_tokens = clean(target_name).split()

        def extend_el(tokens):
            ext = tokens.copy()
            for i, token in enumerate(tokens):
                if token == 'el' and i + 1 < len(tokens):
                    ext.append('el' + tokens[i + 1])
            return ext

        search_ext = extend_el(search_tokens)
        target_ext = extend_el(target_tokens)

        set_search = set(search_ext)
        set_target = set(target_ext)
        inter = set_search & set_target
        union = set_search | set_target

        inter_size = len(inter)
        # Distanz-Grenze nur, wenn gar keine Token-Überlappung
        if inter_size == 0 and self._levenshtein_distance(search_name, target_name) > int(self.fuzzy_params.get('max_distance', max_distance)):
            return 0.0

        # Ähnlichkeitsmaße
        dice = (2 * inter_size) / max(1, (len(set_search) + len(set_target)))
        jaccard = inter_size / max(1, len(union))
        coverage = inter_size / max(1, len(set_search))

        # Reihenfolge-Bonus
        order_bonus = 0.0
        if search_tokens and target_tokens and search_tokens[0] == target_tokens[0]:
            order_bonus += 8.0
        if search_tokens and target_tokens and search_tokens[-1] == target_tokens[-1]:
            order_bonus += 8.0

        # Präfix-Bonus
        prefix_bonus = 0.0
        for st in search_tokens:
            if any(tt.startswith(st) or st.startswith(tt) for tt in target_tokens):
                prefix_bonus += 2.0
        prefix_bonus = min(prefix_bonus, 8.0)

        # Arabisch-Bonus
        arabic_bonus = 0.0
        if any(t == 'el' or t.startswith('el') for t in search_tokens) and any(t == 'el' or t.startswith('el') for t in target_tokens):
            arabic_bonus = float(self.fuzzy_params.get('arabic_name_bonus', 20))

        # Distanz (leichter Einfluss)
        distance = self._levenshtein_distance(search_name, target_name)
        max_len = max(len(search_name), len(target_name))
        norm_dist = (distance / max_len) if max_len else 1.0
        distance_score = max(0.0, 100.0 - (norm_dist * 100.0)) / 100.0

        base = (0.55 * dice + 0.20 * coverage + 0.10 * jaccard + 0.15 * distance_score) * 100.0
        score = base + order_bonus + prefix_bonus + arabic_bonus
        return float(max(0.0, min(100.0, score)))

    def _calculate_garage_abzug(self, garage, kw):
        """Berechnet Garage-Abzug wie in der echten Abrechnung"""
        try:
            if garage > 0:
                daily_garage = self._calculate_daily_garage_cost(garage, kw)
                garage_faktor = 0.5  # Standard-Faktor
                garage_abzug = daily_garage * garage_faktor
                print(f"Garage-Berechnung: Monatlich={garage}€, Montage=4, Täglich={daily_garage:.2f}€")
                print(f"Garage-Cache-Update für {kw}: {daily_garage:.2f}€")
                print(f"Garage-Abzug berechnet: {daily_garage:.2f}€ × {garage_faktor} = {garage_abzug:.2f}€")
                return garage_abzug
            else:
                print("Garage-Abzug: Keine monatlichen Garage-Kosten konfiguriert")
                return 0.0
        except Exception as e:
            print(f"Fehler bei Garage-Abzug-Berechnung: {e}")
            return 0.0
    
    def _calculate_daily_garage_cost(self, monthly_garage, kw):
        """Berechnet die täglichen Garage-Kosten"""
        try:
            import calendar
            from datetime import datetime
            
            # Jahr und Monat aus KW berechnen
            jahr = datetime.now().year
            kw_int = int(kw.replace("KW", "")) if kw else None
            if kw_int is None:
                return 0.0
            
            # Ersten Tag der KW berechnen
            erster_tag_kw = datetime.strptime(f'{jahr}-W{kw_int}-1', "%Y-W%W-%w")
            monat = erster_tag_kw.month
            
            # Anzahl Montage im Monat berechnen
            cal = calendar.Calendar(firstweekday=0)
            montage = [d for d in cal.itermonthdates(jahr, monat) if d.weekday() == 0 and d.month == monat]
            anzahl_montage = len(montage)
            
            if anzahl_montage > 0:
                # Tägliche Garage-Kosten = Monatliche Kosten ÷ Anzahl Montage
                daily_garage = monthly_garage / anzahl_montage
                return daily_garage
            else:
                print(f"Keine Montage im Monat {monat} gefunden")
                return 0.0
                
        except Exception as e:
            print(f"Fehler bei Garage-Berechnung-Impl: {e}")
            return 0.0
    
    def _calculate_headcard_values(self, kw_data):
        """Berechnet HeadCard-Werte genau wie in der echten Abrechnung"""
        # Initialisiere Daten-Container wie in echter Abrechnung
        data = {
            'sum_40100': 0.0,
            'sum_31300': 0.0,
            'sum_uber': 0.0,
            'sum_bolt': 0.0,
            'sum_bargeld': 0.0,
            '_40100_trinkgeld': 0.0,
            '_31300_trinkgeld': 0.0,
            '_40100_trinkgeld_gesamt': 0.0,
            '_31300_trinkgeld_gesamt': 0.0,
            '_40100_bargeld': 0.0,
            '_31300_bargeld': 0.0,
            'uber_cash_collected': 0.0,
            'bolt_cash_collected': 0.0,
            'bolt_rider_tips': 0.0
        }
        
        # Verarbeite jede Plattform wie in echter Abrechnung
        for platform_data in kw_data:
            if platform_data.get('type') == 'summary':
                platform_label = platform_data.get('label', '')
                details = platform_data.get('details', [])
                
                # Extrahiere Werte aus Details
                umsatz = 0.0
                bargeld = 0.0
                trinkgeld = 0.0
                roher_umsatz = 0.0  # Für 31300
                
                for detail in details:
                    if detail.get('label') in ['Echter Umsatz', 'Total', 'Real']:
                        value_str = detail.get('value', '0')
                        umsatz = safe_float(value_str.replace('€', '').replace(' ', ''))
                    elif detail.get('label') in ['Bargeld', 'Cash']:
                        value_str = detail.get('value', '0')
                        bargeld = safe_float(value_str.replace('€', '').replace(' ', ''))
                    elif detail.get('label') in ['Trinkgeld', 'Tips']:
                        value_str = detail.get('value', '0')
                        trinkgeld = safe_float(value_str.replace('€', '').replace(' ', ''))
                    elif detail.get('label') == 'Roher Umsatz':  # Für 31300
                        value_str = detail.get('value', '0')
                        roher_umsatz = safe_float(value_str.replace('€', '').replace(' ', ''))
                
                # Plattform-spezifische Verarbeitung wie in echter Abrechnung
                if platform_label == '40100':
                    data['sum_40100'] += umsatz
                    data['sum_bargeld'] += bargeld
                    data['_40100_trinkgeld'] += trinkgeld  # Gefiltertes Trinkgeld
                    data['_40100_trinkgeld_gesamt'] += trinkgeld  # Gefiltertes Trinkgeld
                    data['_40100_bargeld'] += bargeld
                elif platform_label == '31300':
                    # KORREKTUR: Für 31300 gilt HeadCard = echter Umsatz (ohne Trinkgeld), konsistent mit echter Abrechnung
                    data['sum_31300'] += umsatz  # Echter Umsatz
                    data['sum_bargeld'] += bargeld
                    data['_31300_trinkgeld'] += trinkgeld  # Gefiltertes Trinkgeld
                    data['_31300_trinkgeld_gesamt'] += trinkgeld  # Gefiltertes Trinkgeld
                    data['_31300_bargeld'] += bargeld
                elif platform_label == 'Uber':
                    data['sum_uber'] += umsatz
                    data['sum_bargeld'] += bargeld
                    data['uber_cash_collected'] += bargeld
                elif platform_label == 'Bolt':
                    data['sum_bolt'] += umsatz
                    data['sum_bargeld'] += bargeld
                    data['bolt_cash_collected'] += bargeld
                    data['bolt_rider_tips'] += trinkgeld
        
        # HeadCard-Werte berechnen wie in echter Abrechnung
        taxi_total = data['sum_40100'] + data['sum_31300']
        
        headcard_umsatz = float(data['sum_uber']) + float(data['sum_bolt']) + float(taxi_total)
        headcard_trinkgeld = data['bolt_rider_tips'] + data['_40100_trinkgeld'] + data['_31300_trinkgeld']
        headcard_bargeld = data['uber_cash_collected'] + data['bolt_cash_collected'] + data['_40100_bargeld'] + data['_31300_bargeld']
        
        # Credit Card = (Umsatz + Trinkgeld) - Bargeld (wie in echter Abrechnung)
        headcard_credit_card = (headcard_umsatz + headcard_trinkgeld) - headcard_bargeld
        
        return {
            'headcard_umsatz': headcard_umsatz,
            'headcard_trinkgeld': headcard_trinkgeld,
            'headcard_bargeld': headcard_bargeld,
            'headcard_credit_card': headcard_credit_card
        }
    
    def _calculate_anteil_once(self, total_umsatz, deal_typ, pauschale, umsatzgrenze, einsteiger_prozent=0.0):
        """Berechnet den Anteil wie in der echten Abrechnung"""
        try:
            print(f"    ANTEIL-BERECHNUNG (Deal: {deal_typ}):")
            
            if deal_typ == "P":
                print(f"    P-DEAL ANTEIL:")
                # Pauschale
                result = pauschale
                print(f"      Pauschale: {result:.2f}€")
                
                # Umsatzgrenze prüfen
                print(f"      Gesamtumsatz: {total_umsatz:.2f}€")
                print(f"      Umsatzgrenze: {umsatzgrenze:.2f}€")
                
                if total_umsatz > umsatzgrenze:
                    bonus = (total_umsatz - umsatzgrenze) * 0.1
                    result += bonus
                    print(f"      Bonus: {bonus:.2f}€ (10% von Überschuss)")
                else:
                    print(f"      Kein Bonus (Umsatz unter Grenze)")
                
                print(f"      Berechneter Anteil: {result:.2f}€")
                print(f"      Hinweis: Bei P-Deals gibt es keinen Einsteiger-Wert und Tank beeinflusst das Ergebnis nicht")
                return result
                
            elif deal_typ == "%":
                print(f"    %-DEAL ANTEIL:")
                print(f"      Gesamtumsatz: {total_umsatz:.2f}€")
                
                # 50% Anteil
                anteil_50 = total_umsatz * 0.5
                print(f"      50% Anteil: {anteil_50:.2f}€")
                
                # Einsteiger-Plus (50%) - NUR BEI %-DEALS (wie in echter Abrechnung)
                einsteiger_input = total_umsatz * einsteiger_prozent  # Prozentsatz als Input simulieren
                einsteiger_plus = einsteiger_input * 0.5
                print(f"      Einsteiger-Input: {einsteiger_input:.2f}€ (Umsatz × {einsteiger_prozent*100}%)")
                print(f"      Einsteiger-Plus (50%): {einsteiger_input:.2f}€ × 0.5 = {einsteiger_plus:.2f}€")
                
                # Finaler Anteil (wie in echter Abrechnung)
                result = anteil_50 + einsteiger_plus
                print(f"      Tank: Wird nur als Ausgabe in der Income-Berechnung behandelt")
                print(f"      Berechneter Anteil: {result:.2f}€")
                return result
                
            elif deal_typ == "C":
                print(f"    C-DEAL ANTEIL:")
                # Custom-Deal Logik (vereinfacht)
                result = total_umsatz * 0.6  # Beispiel: 60%
                print(f"      Custom-Deal Anteil: {result:.2f}€")
                return result
                
            else:
                print(f"    DEFAULT ANTEIL:")
                result = total_umsatz * 0.5
                print(f"      Default Anteil: {result:.2f}€")
                return result
                
        except Exception as e:
            print(f"Fehler bei Anteil-Berechnung: {e}")
            return 0.0
    
    def _calculate_income_once(self, anteil, tank_value, einsteiger_value, expense_fix, garage_abzug, deal_typ, tank_prozent=0.0, total_umsatz=0.0):
        """Berechnet das Income wie in der echten Abrechnung"""
        try:
            print(f"    INCOME-BERECHNUNG:")
            
            # Start mit dem Anteil
            income = anteil
            
            # Tank-Abzug (Deal-abhängig wie in echter Abrechnung)
            if deal_typ == "P":
                # Bei P-Deals: Kein Tank-Abzug
                tank_abzug = 0.0
                print(f"      Tank-Abzug: {tank_abzug:.2f}€ (Bei P-Deals wird Tank nicht abgezogen)")
            elif deal_typ == "%":
                # Bei %-Deals: 50% Tank-Abzug
                tank_abzug = tank_value * 0.5
                print(f"      Tank-Abzug: {tank_abzug:.2f}€ (50% von {tank_value:.2f}€)")
            elif deal_typ == "C":
                # Bei C-Deals: Kein Tank-Abzug
                tank_abzug = 0.0
                print(f"      Tank-Abzug: {tank_abzug:.2f}€ (Bei C-Deals wird Tank nicht abgezogen)")
            else:
                # Fallback: Kein Abzug
                tank_abzug = 0.0
                print(f"      Tank-Abzug: {tank_abzug:.2f}€ (Unbekannter Deal-Typ)")
            
            income -= tank_abzug
            
            # Garage-Abzug
            income -= garage_abzug
            print(f"      Garage-Abzug: {garage_abzug:.2f}€")
            
            # Expenses vom Income abziehen
            income -= expense_fix
            print(f"      Expenses-Abzug: -{expense_fix:.2f}€")
            
            print(f"    INCOME: {income:.2f} EUR")
            return income
            
        except Exception as e:
            print(f"Fehler bei Income-Berechnung: {e}")
            return 0.0
    
    def _calculate_abrechnungsergebnis_once(self, credit_card, income, deal_typ, headcard_trinkgeld=0.0):
        """Berechnet das finale Abrechnungsergebnis wie in der echten Abrechnung"""
        try:
            print(f"    ABRECHNUNGSERGEBNIS-BERECHNUNG:")
            
            # Finale Berechnung: Credit Card - Income
            result = credit_card - income
            
            # Bei %-Deals: Trinkgeld zum Abrechnungsergebnis hinzufügen
            if deal_typ == "%":
                result += headcard_trinkgeld
                print(f"      Credit Card: {credit_card:.2f}€")
                print(f"      Income: {income:.2f} EUR (bereits mit Expenses-Abzug)")
                print(f"      Trinkgeld hinzugefügt: +{headcard_trinkgeld:.2f}€ (%-Deal)")
                print(f"    ABRECHNUNGSERGEBNIS: {result:.2f}€")
            else:
                print(f"      Credit Card: {credit_card:.2f}€")
                print(f"      Income: {income:.2f} EUR (bereits mit Expenses-Abzug)")
                print(f"    ABRECHNUNGSERGEBNIS: {result:.2f}€")
            
            return result
            
        except Exception as e:
            print(f"Fehler bei Abrechnungsergebnis-Berechnung: {e}")
            return 0.0

def main():
    """Hauptfunktion für Tests"""
    print("SCHNELLABRECHNUNG TESTER")
    print("=" * 60)
    
    # Konfiguration laden
    tester = SchnellabrechnungTester()
    
    # Aktuelle Konfiguration anzeigen
    tester.config.print_current_config()
    
    # Backend initialisieren
    if not tester.initialize_backend():
        print(" Test abgebrochen - Backend konnte nicht initialisiert werden")
        return
    
    # Test-Parameter aus Konfiguration laden
    test_params = tester.config.get_test_params()
    
    print(f"\n TEST: {test_params.get('fahrer', 'Awes Ahmadeey')} - {test_params.get('fahrzeug', 'W135CTX')}")
    print(f" Kalenderwochen: {len(test_params.get('kalenderwochen', []))} Wochen")
    print(f" Tank-Prozent: {test_params.get('tank_prozent', 0.13)*100}%")
    print(f" Einsteiger-Prozent: {test_params.get('einsteiger_prozent', 0.20)*100}%")
    print(f" Fixe Ausgaben: {test_params.get('expense_fix', 0.00)}€")
    
    # Test mit Konfigurationsparametern
    print("\n Deal-Typ wird aus Datenbank geladen...")
    print("-" * 30)
    
    tester.test_schnellabrechnung(
        fahrer=test_params.get('fahrer', 'Awes Ahmadeey'),
        fahrzeug=test_params.get('fahrzeug', 'W135CTX'),
        kalenderwochen=test_params.get('kalenderwochen', ['KW22', 'KW23', 'KW24', 'KW25', 'KW26', 'KW27', 'KW28', 'KW29', 'KW30', 'KW31']),
        tank_prozent=test_params.get('tank_prozent', 0.13),
        einsteiger_prozent=test_params.get('einsteiger_prozent', 0.20),
        expense_fix=test_params.get('expense_fix', 0.00)
    )
    
    # Zusammenfassung ausgeben
    tester.print_test_summary()
    
    print("\n" + "=" * 50)
    print(" Test abgeschlossen")

def interactive_config():
    """Interaktive Konfiguration"""
    print(" INTERAKTIVE KONFIGURATION")
    print("=" * 50)
    
    config = TestConfig()
    
    while True:
        print("\n Verfügbare Aktionen:")
        print("1. Aktuelle Konfiguration anzeigen")
        print("2. Test-Parameter ändern")
        print("3. Deal-Parameter ändern")
        print("4. Garage-Parameter ändern")
        print("5. Fuzzy-Matching-Parameter ändern")
        print("6. Sicherheits-Parameter ändern")
        print("7. Test ausführen")
        print("8. Konfiguration speichern")
        print("9. Beenden")
        
        choice = input("\n Ihre Wahl (1-9): ").strip()
        
        if choice == "1":
            config.print_current_config()
            
        elif choice == "2":
            print("\n Test-Parameter ändern:")
            fahrer = input(f"Fahrer (aktuell: {config.get_test_params().get('fahrer', 'Awes Ahmadeey')}): ").strip()
            fahrzeug = input(f"Fahrzeug (aktuell: {config.get_test_params().get('fahrzeug', 'W135CTX')}): ").strip()
            kalenderwochen = input(f"Kalenderwochen (aktuell: {','.join(config.get_test_params().get('kalenderwochen', []))}): ").strip()
            tank_prozent = input(f"Tank-Prozent (aktuell: {config.get_test_params().get('tank_prozent', 0.13)*100}%): ").strip()
            einsteiger_prozent = input(f"Einsteiger-Prozent (aktuell: {config.get_test_params().get('einsteiger_prozent', 0.20)*100}%): ").strip()
            expense_fix = input(f"Expense-Fix (aktuell: {config.get_test_params().get('expense_fix', 0.00)}€): ").strip()
            
            updates = {}
            if fahrer: updates['fahrer'] = fahrer
            if fahrzeug: updates['fahrzeug'] = fahrzeug
            if kalenderwochen: updates['kalenderwochen'] = kalenderwochen
            if tank_prozent: updates['tank_prozent'] = float(tank_prozent) / 100
            if einsteiger_prozent: updates['einsteiger_prozent'] = float(einsteiger_prozent) / 100
            if expense_fix: updates['expense_fix'] = float(expense_fix)
            
            config.update_test_params(**updates)
            
        elif choice == "7":
            print("\n Test wird ausgeführt...")
            main()
            
        elif choice == "8":
            config.save_config()
            
        elif choice == "9":
            print(" Auf Wiedersehen!")
            break
            
        else:
            print(" Ungültige Wahl. Bitte 1-9 eingeben.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Interaktive Konfiguration
        interactive_config()
    else:
        # Standard-Test ausführen
        main()
