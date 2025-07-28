from PySide6.QtCore import QObject, Slot, Signal, Property, QAbstractListModel, Qt
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QWidget
from PySide6.QtGui import Qt
import sys
import sqlite3
import pandas as pd
import re
import os
import math
from generic_wizard import GenericWizard
from datetime import datetime, timedelta
import calendar
import json

def safe_float(val):
    """Globale Hilfsfunktion für sichere Float-Konvertierung"""
    if val is None or str(val).strip() == '' or str(val).lower() == 'nan' or (isinstance(val, float) and math.isnan(val)):
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

class AbrechnungsSeiteQML(QObject): # AbrechnungsSeiteQML-Klasse
    # Signals für QML       
    fahrerChanged = Signal()
    fahrzeugChanged = Signal()
    kwChanged = Signal()
    ergebnisseChanged = Signal()
    currentPageChanged = Signal()
    foundPagesChanged = Signal()
    wizardDataChanged = Signal()
    wizardFertig = Signal()
    headcardUmsatzChanged = Signal()
    headcardTrinkgeldChanged = Signal()
    headcardBargeldChanged = Signal()
    ergebnisChanged = Signal()
    inputGasChanged = Signal()
    inputEinsteigerChanged = Signal()
    inputExpenseChanged = Signal()
    # Neue Signals für Deal-spezifische HeadCard
    headcardDealValueChanged = Signal()
    headcardDealIconChanged = Signal()
    headcardDealLabelChanged = Signal()
    headcardGarageChanged = Signal()
    # Neue Signals für separate Bargeld und Kreditkarte Anzeige
    headcardCashChanged = Signal()
    headcardCreditCardChanged = Signal()
    pauschaleChanged = Signal()
    umsatzgrenzeChanged = Signal()
    dealChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._fahrer_list = []
        self._fahrzeug_list = []
        self._kw_list = []
        self._ergebnisse = []
        self._current_page = 0
        self._found_pages = []
        self._fahrer_label = ""
        self._wizard_data = {}
        self._show_wizard = True
        self._root_window = None
        # HeadCard Summen
        self._headcard_umsatz = 0.0
        self._headcard_trinkgeld = 0.0
        self._headcard_bargeld = 0.0
        self._ergebnis = 0.0
        self._input_gas = 0.0
        self._input_gas_text = ""
        self._input_einsteiger = 0.0
        self._input_einsteiger_text = ""
        self._input_expense = 0.0
        self._expense_cache = []  # Zwischenspeicher für neue Ausgaben
        # Daten laden
        self.load_fahrer()
        self.load_fahrzeuge()
        self.load_kalenderwochen()
        self._overlay_config_cache = []  # Session-Cache für Overlay-Konfiguration
        self._overlay_income_ohne_einsteiger = 0.0
        self._einsteiger_faktor = 1.0
        self._tank_faktor = 1.0
    
    # Properties für QML
    def fahrer_list(self):
        return self._fahrer_list
        
    def fahrzeug_list(self):
        return self._fahrzeug_list
        
    def kw_list(self):
        return self._kw_list
        
    @Property(list, notify=ergebnisseChanged)
    def ergebnisse(self):
        return self._ergebnisse
        
    def current_page(self):
        return self._current_page
        
    def found_pages(self):
        return [page[0] for page in self._found_pages]  # Nur die Namen zurückgeben
        
    def wizard_data(self):
        return self._wizard_data
        
    def show_wizard(self):
        return self._show_wizard
        
    @Property(float, notify=headcardUmsatzChanged)
    def headcard_umsatz(self):
        return self._headcard_umsatz

    @Property(float, notify=headcardTrinkgeldChanged)
    def headcard_trinkgeld(self):
        return self._headcard_trinkgeld

    @Property(float, notify=headcardBargeldChanged)
    def headcard_bargeld(self):
        return self._headcard_bargeld
        
    @Property(float, notify=headcardDealValueChanged)
    def headcard_deal_value(self):
        return getattr(self, '_headcard_deal_value', self._headcard_umsatz)
        
    @Property(str, notify=headcardDealIconChanged)
    def headcard_deal_icon(self):
        deal = getattr(self, '_deal', '%')
        if deal == 'P':
            return 'assets/icons/credit_card_gray.svg'
        else:
            return 'assets/icons/cash_gray.svg'
        
    @Property(str, notify=headcardDealLabelChanged)
    def headcard_deal_label(self):
        return getattr(self, '_headcard_deal_label', 'Umsatz')
        
    @Property(float, notify=headcardGarageChanged)
    def headcard_garage(self):
        try:
            kw = getattr(self, '_kw_label', "") if hasattr(self, '_kw_label') else ""
            jahr = datetime.now().year
            kw_int = int(kw) if kw else None
            if kw_int is not None:
                erster_tag_kw = datetime.strptime(f'{jahr}-W{kw_int}-1', "%Y-W%W-%w")
                monat = erster_tag_kw.month
                cal = calendar.Calendar(firstweekday=0)
                montage = [d for d in cal.itermonthdates(jahr, monat) if d.weekday() == 0 and d.month == monat]
                anzahl_montage = len(montage)
                if anzahl_montage > 0:
                    return getattr(self, '_garage', 0.0) / anzahl_montage
            return getattr(self, '_garage', 0.0)
        except Exception as e:
            print(f"Fehler bei Garage-Berechnung: {e}")
            return getattr(self, '_garage', 0.0)
            
    @headcard_garage.setter
    def headcard_garage(self, value):
        if getattr(self, '_garage', 0.0) != value:
            self._garage = value
            print(f"DEBUG: headcard_garage auf '{value}' gesetzt")
        self.headcardGarageChanged.emit()
            
    @Property(float, notify=headcardCashChanged)
    def headcard_cash(self):
        """Bargeld-Wert für die Summenzeile"""
        return getattr(self, '_headcard_cash', getattr(self, '_headcard_bargeld', 0.0))
        
    @Property(float, notify=headcardCreditCardChanged)
    def headcard_credit_card(self):
        """Kreditkarte/Bankomat-Wert für die Summenzeile"""
        return getattr(self, '_headcard_credit_card', 0.0)
        
    @Property(float, notify=ergebnisChanged)
    def ergebnis(self):
        return self._ergebnis
        
    @Property(str, notify=inputGasChanged)
    def inputGas(self):
        return self._input_gas

    @inputGas.setter
    def inputGas(self, value):
        if self._input_gas != value:
            self._input_gas = value
            print(f"DEBUG: inputGas auf '{value}' gesetzt")
        self.inputGasChanged.emit()

    @Property(str, notify=inputEinsteigerChanged)
    def inputEinsteiger(self):
        return self._input_einsteiger

    @inputEinsteiger.setter
    def inputEinsteiger(self, value):
        if self._input_einsteiger != value:
            self._input_einsteiger = value
            print(f"DEBUG: inputEinsteiger auf '{value}' gesetzt")
        self.inputEinsteigerChanged.emit()

    @Property(str, notify=inputExpenseChanged)
    def inputExpense(self):
        return self._input_expense

    @inputExpense.setter
    def inputExpense(self, value):
        if self._input_expense != value:
            self._input_expense = value
            print(f"DEBUG: inputExpense auf '{value}' gesetzt")
        self.inputExpenseChanged.emit()

    @Property(str, notify=dealChanged)
    def deal(self):
        return getattr(self, '_deal', '%')

    @Property(float, notify=pauschaleChanged)
    def pauschale(self):
        return getattr(self, '_pauschale', 0.0)

    @Property(float, notify=umsatzgrenzeChanged)
    def umsatzgrenze(self):
        return getattr(self, '_umsatzgrenze', 0.0)
        
    # Properties für QML-Zugriff auf Faktoren
    @Property(float, notify=ergebnisChanged)
    def taxi_faktor(self):
        return getattr(self, '_taxi_faktor', 0.0)
        
    @Property(float, notify=ergebnisChanged)
    def uber_faktor(self):
        return getattr(self, '_uber_faktor', 0.0)
        
    @Property(float, notify=ergebnisChanged)
    def bolt_faktor(self):
        return getattr(self, '_bolt_faktor', 0.0)
        
    @Property(float, notify=ergebnisChanged)
    def einsteiger_faktor(self):
        return getattr(self, '_einsteiger_faktor', 0.0)
        
    @Property(float, notify=ergebnisChanged)
    def tank_faktor(self):
        return getattr(self, '_tank_faktor', 0.0)
        
    @Property(float, notify=ergebnisChanged)
    def garage_faktor(self):
        return getattr(self, '_garage_faktor', 0.5)
        
    @Property(float, notify=ergebnisChanged)
    def expenses(self):
        """Summe aller Expenses für QML-Zugriff"""
        try:
            if hasattr(self, '_expense_cache') and self._expense_cache:
                return sum(float(e.get('amount', 0)) for e in self._expense_cache)
            return 0.0
        except Exception:
            return 0.0

    def load_fahrer(self):
        try:
            # Direkte SQLite-Verbindung statt DBManager
            conn = sqlite3.connect("SQL/database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT first_name, last_name, status FROM drivers")
            rows = cursor.fetchall()
            self._fahrer_list = []
            for row in rows:
                first_name, last_name, status = row
                if status and status.lower() == 'active':
                    label = f"{first_name or ''} {last_name or ''}".strip()
                    if label:
                        self._fahrer_list.append(label)
            self._fahrer_list.sort(key=lambda x: x.lower())
            self.fahrerChanged.emit()
        except Exception as e:
            print(f"Fehler beim Laden der Fahrer: {e}")
        finally:
            try:
                conn.close()
            except:
                pass
            
    def load_fahrzeuge(self):
        try:
            # Direkte SQLite-Verbindung statt DBManager
            conn = sqlite3.connect("SQL/database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT license_plate, rfrnc FROM vehicles")
            rows = cursor.fetchall()
            self._fahrzeug_list = []
            for row in rows:
                kennzeichen, rfrnc = row
                if kennzeichen:
                    label = f"{kennzeichen}"
                    self._fahrzeug_list.append(label)
            self._fahrzeug_list.sort(key=lambda x: x.lower())
            self.fahrzeugChanged.emit()
        except Exception as e:
            print(f"Fehler beim Laden der Fahrzeuge: {e}")
        finally:
            try:
                conn.close()
            except:
                pass
            
    def load_kalenderwochen(self):
        try:
            db_path = os.path.join("SQL", "40100.sqlite")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'report_KW%'")
            tables = [row[0] for row in cursor.fetchall()]
            self._kw_list = sorted([t.replace("report_KW", "") for t in tables], reverse=True)
            self.kwChanged.emit()
        except Exception as e:
            print(f"Fehler beim Laden der Kalenderwochen: {e}")
        finally:
            try:
                conn.close()
            except:
                pass

    @Slot()
    def show_wizard_and_load_page(self):
        """Zeigt den V2-GenericWizard an und lädt danach die Abrechnungsseite"""
        # Felder und Cache leeren, wenn Wizard neu gestartet wird
        self._expense_cache = []
        self.inputGas = ""
        self.inputEinsteiger = ""
        self.inputExpense = ""
        fields = [
            ("Fahrer", "fahrer", "combo", self._fahrer_list),
            ("Fahrzeug", "fahrzeug", "combo", self._fahrzeug_list),
            ("Kalenderwoche", "kw", "combo", self._kw_list)
        ]
        def wizard_callback(data):
            print("=" * 60)
            print("🚀 WIZARD-CALLBACK GESTARTET")
            print("=" * 60)
            print(f"📋 Eingabedaten:")
            print(f"   👤 Fahrer: {data['fahrer']}")
            print(f"   🚗 Fahrzeug: {data['fahrzeug']}")
            print(f"   📅 KW: {data['kw']}")
            
            # WICHTIG: _wizard_data setzen für Speicherung
            self._wizard_data = data
            
            fahrer = data["fahrer"]
            fahrzeug = data["fahrzeug"]
            kw = data["kw"]
            
            self._fahrer_label = fahrer
            self._fahrzeug_label = fahrzeug
            self._kw_label = kw
            
            # Fahrer-ID aus der Datenbank holen
            print(f"🔍 Suche Fahrer-ID in Datenbank...")
            try:
                conn = sqlite3.connect("SQL/database.db")
                cursor = conn.cursor()
                cursor.execute("SELECT driver_id FROM drivers WHERE first_name || ' ' || last_name = ?", (fahrer,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    self._fahrer_id = result[0]
                    print(f"   ✅ Fahrer-ID gefunden: {self._fahrer_id}")
                else:
                    print(f"   ⚠️  Keine Fahrer-ID gefunden für: {fahrer}")
                    self._fahrer_id = hash(fahrer) % 10000
                    print(f"   🔧 Verwende Hash-ID: {self._fahrer_id}")
            except Exception as e:
                print(f"   ❌ Fehler beim Laden der Fahrer-ID: {e}")
                self._fahrer_id = hash(fahrer) % 10000
                print(f"   🔧 Verwende Hash-ID nach Fehler: {self._fahrer_id}")
            
            print(f"⚙️  Konfiguration:")
            print(f"   📊 Deal-Typ: wird in _lade_deal_aus_datenbank() geladen")
            print(f"   💰 Pauschale/Umsatzgrenze: wird in _lade_deal_aus_datenbank() geladen")
            print(f"   🔧 Deal-Konfiguration: wird in _lade_deal_aus_datenbank() gesetzt")
            
            # Deal-Konfiguration laden (wie bei Redo)
            print(f"🔍 Lade Deal-Konfiguration aus Datenbank für Fahrer '{data['fahrer']}'...")
            self._lade_deal_aus_datenbank(data["fahrer"])
            
            print(f"🚀 Starte Auswertung...")
            self.auswerten(data["fahrer"], data["fahrzeug"], data.get("kw", ""))
            
            if hasattr(self, 'overlayConfigCacheChanged'):
                self.overlayConfigCacheChanged.emit()
            self.wizardFertig.emit()
            
            print("=" * 60)
            print("✅ WIZARD-CALLBACK BEENDET")
            print("=" * 60)
        parent = None
        wizard = GenericWizard(fields, callback=wizard_callback, parent=parent, title="Abrechnungs-Auswertung")
        wizard.show()

    @Slot()
    def show_wizard_only(self):
        """Zeigt den Wizard an und startet danach eine komplette Neuauswertung"""
        fields = [
            ("Fahrer", "fahrer", "combo", self._fahrer_list),
            ("Fahrzeug", "fahrzeug", "combo", self._fahrzeug_list),
            ("Kalenderwoche", "kw", "combo", self._kw_list)
        ]
        def wizard_callback(data):
            # 1. ALLE WERTE BEREINIGEN
            
            # Cache und Zwischenspeicher leeren
            self._expense_cache = []
            self._overlay_config_cache = []
            self._overlay_income_ohne_einsteiger = 0.0
            
            # Input-Felder zurücksetzen
            self.inputGas = ""
            self.inputEinsteiger = ""
            self.inputExpense = ""
            
            # Ergebnisse und Seiten zurücksetzen
            self._ergebnisse = []
            self._found_pages = []
            self._current_page = 0
            
            # WICHTIG: Auch die Input-Werte zurücksetzen, die von _get_platform_umsatz verwendet werden
            self._input_einsteiger = ""
            self._input_gas = ""
            
            # HeadCard-Werte zurücksetzen
            self._headcard_umsatz = 0.0
            self._headcard_trinkgeld = 0.0
            self._headcard_bargeld = 0.0
            self._headcard_cash = 0.0
            self._headcard_credit_card = 0.0
            self._headcard_garage = 0.0
            self._headcard_trinkgeld_gesamt = 0.0
            self._headcard_deal_value = 0.0
            self._headcard_deal_icon = ""
            self._headcard_deal_label = ""
            self._ergebnis = 0.0
            
            # WICHTIG: Auch die Input-Werte zurücksetzen, die von _get_platform_umsatz verwendet werden
            self._input_einsteiger = ""
            self._input_gas = ""
            
            # Deal-Werte zurücksetzen
            self._deal = ""
            self._pauschale = 500.0
            self._umsatzgrenze = 1200.0
            self._garage = 0.0
            
            # Deal-spezifische Faktoren zurücksetzen (werden in _lade_deal_aus_datenbank() neu gesetzt)
            self._taxi_faktor = 0.0
            self._uber_faktor = 0.0
            self._bolt_faktor = 0.0
            self._einsteiger_faktor = 0.0
            self._tank_faktor = 0.0
            self._garage_faktor = 0.5
            
            # Deal-spezifische Slider zurücksetzen
            self._taxi_deal = ""
            self._taxi_slider = 0.0
            self._uber_deal = ""
            self._uber_slider = 0.0
            self._bolt_deal = ""
            self._bolt_slider = 0.0
            self._einsteiger_deal = ""
            self._einsteiger_slider = 0.0
            self._garage_slider = 0.0
            self._tank_slider = 0.0
            
            # Wizard-Daten zurücksetzen
            self._wizard_data = data  # WICHTIG: data setzen für Speicherung
            self._fahrer_label = ""
            self._fahrzeug_label = ""
            self._kw_label = ""
            self._fahrer_id = None
            
            # WerteGeladen zurücksetzen (wichtig für QML-Sichtbarkeit)
            self._werte_geladen = False
            
            # Signals emittieren um QML zu aktualisieren
            self.headcardUmsatzChanged.emit()
            self.headcardTrinkgeldChanged.emit()
            self.headcardBargeldChanged.emit()
            self.headcardCashChanged.emit()
            self.headcardCreditCardChanged.emit()
            self.headcardGarageChanged.emit()
            self.headcardDealValueChanged.emit()
            self.headcardDealIconChanged.emit()
            self.headcardDealLabelChanged.emit()
            self.ergebnisChanged.emit()
            self.dealChanged.emit()
            self.pauschaleChanged.emit()
            self.umsatzgrenzeChanged.emit()
            self.ergebnisseChanged.emit()
            self.foundPagesChanged.emit()
            self.currentPageChanged.emit()
            self.inputGasChanged.emit()
            self.inputEinsteigerChanged.emit()
            self.inputExpenseChanged.emit()
            self.wizardDataChanged.emit()
            
            # 2. DEAL-KONFIGURATION SOFORT NACH WIZARD LADEN (VOR ALLEM ANDEREN)
            print(f"🔍 Lade Deal-Konfiguration aus Datenbank für Fahrer '{data['fahrer']}'...")
            self._lade_deal_aus_datenbank(data["fahrer"])
            
            print(f"   📊 Geladener Deal: {self._deal}")
            print(f"   🔧 Gesetzte Faktoren:")
            print(f"      🚕 Taxi: {getattr(self, '_taxi_faktor', 'N/A')}")
            print(f"      🚗 Uber: {getattr(self, '_uber_faktor', 'N/A')}")
            print(f"      ⚡ Bolt: {getattr(self, '_bolt_faktor', 'N/A')}")
            print(f"      🆕 Einsteiger: {getattr(self, '_einsteiger_faktor', 'N/A')}")
            print(f"      ⛽ Tank: {getattr(self, '_tank_faktor', 'N/A')}")
            print(f"      🏢 Garage: {getattr(self, '_garage_faktor', 'N/A')}")
            
            # 3. LABELS AKTUALISIEREN
            print(f"🏷️  Aktualisiere Labels...")
            self._fahrer_label = data["fahrer"]
            self._fahrzeug_label = data["fahrzeug"]
            self._kw_label = data["kw"]
            
            # 4. QML-WERTE ZURÜCKSETZEN
            # Diese Werte werden über QML geleert, aber wir können sie hier auch zurücksetzen
            # overlayConfigCache = [] wird in QML gemacht
            
            # 5. KOMPLETTE NEUAUSWERTUNG MIT GLEICHEM WORKFLOW WIE ERSTE SUCHE
            self.auswerten(data["fahrer"], data["fahrzeug"], data.get("kw", ""))
            
            # 6. QML-STATUS AKTUALISIEREN
            if hasattr(self, 'overlayConfigCacheChanged'):
                self.overlayConfigCacheChanged.emit()
            self.wizardFertig.emit()
            
            # Zusätzliche Sicherheit: Alle relevanten Signals emittieren
            self.ergebnisseChanged.emit()
            self.headcardUmsatzChanged.emit()
            self.headcardTrinkgeldChanged.emit()
            self.headcardBargeldChanged.emit()
            self.headcardCashChanged.emit()
            self.headcardCreditCardChanged.emit()
            self.headcardGarageChanged.emit()
            self.ergebnisChanged.emit()
            self.dealChanged.emit()
            
        parent = None
        wizard = GenericWizard(fields, callback=wizard_callback, parent=parent, title="Abrechnungs-Auswertung")
        wizard.show()

    @Slot(str, str, str)
    def auswerten(self, fahrer, fahrzeug, kw):
        # Auswertung gestartet
        
        if not kw or not fahrer:
            print("   ❌ Fehlende Parameter - Auswertung abgebrochen")
            return
            
        self._fahrer_label = fahrer
        self._found_pages = []
        
        # 1. Fahrer-Deal aus database.db holen
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
                # Deal-Daten geladen
            else:
                # Kein Deal-Eintrag gefunden
                pass
        except Exception as e:
            deal = None
            garage = 0.0
            pauschale = 500.0
            umsatzgrenze = 1200.0
            # Fehler beim Laden der Deal-Daten
        finally:
            try:
                conn_deal.close()
            except:
                pass
                
        # Setze die Backend-Variablen
        self._garage = garage
        self._pauschale = pauschale
        self._umsatzgrenze = umsatzgrenze
        self._deal = deal  # Deal aus Datenbank setzen
        
        # Deal-spezifische Konfiguration wird bereits in _lade_deal_aus_datenbank() gesetzt
        
        # 2. Fahrzeug-Daten aus 40100 und 31300 laden
        if fahrzeug and kw:
            kennzeichen_nummer = "".join(filter(str.isdigit, fahrzeug))
            table_name = f"report_KW{kw}"
            db_path_40100 = os.path.abspath(os.path.join("SQL", "40100.sqlite"))
            db_path_31300 = os.path.abspath(os.path.join("SQL", "31300.sqlite"))
            
            # In 40100 suchen
            try:
                conn = sqlite3.connect(db_path_40100)
                df_40100 = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE Fahrzeug LIKE ?", conn, params=[f"%{kennzeichen_nummer}%"])
                if not df_40100.empty:
                    self._found_pages.append(("40100", df_40100.copy(), deal))
            except Exception as e:
                print(f"[INFO] Keine Daten in 40100 für KW{kw} gefunden oder Fehler: {e}")
            finally:
                try: 
                    conn.close()
                except: 
                    pass
            
            # In 31300 suchen
            try:
                conn = sqlite3.connect(db_path_31300)
                df_31300 = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE Fahrzeug LIKE ?", conn, params=[f"%{kennzeichen_nummer}%"])
                if not df_31300.empty:
                    print(f"[DEBUG] 31300-Matching: Fahrzeug={fahrzeug}, KW={kw}, Treffer={len(df_31300) if df_31300 is not None else 0}")
                    if not df_31300.empty:
                        print(f"[DEBUG] 31300-Matching: Erste Zeilen:\n{df_31300.head().to_string()}")
                        self._found_pages.append(("31300", df_31300.copy(), deal))
                    else:
                        print(f"[DEBUG] 31300-Matching: Keine Einträge gefunden.")
            except Exception as e:
                print(f"[INFO] Keine Daten in 31300 für KW{kw} gefunden oder Fehler: {e}")
            finally:
                try: 
                    conn.close()
                except: 
                    pass
                    
        # 3. Fahrer in Uber und Bolt suchen (angepasstes Matching mit Bereinigung)
        def clean_name(name):
            # Entfernt doppelte Leerzeichen, trimmt und wandelt in Kleinbuchstaben um
            cleaned = re.sub(r"\s+", " ", str(name)).strip().lower()
            
            # Spezielle Behandlung für arabische Namen mit "el" Präfix
            # Normalisiert "al" zu "el" (häufige Variante)
            cleaned = re.sub(r'\bal\s+', 'el ', cleaned)
            
            return cleaned

        def levenshtein_distance(s1, s2):
            """Berechnet die Levenshtein-Distanz zwischen zwei Strings"""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
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

        def fuzzy_match_score(search_name, target_name, max_distance=3):
            """Berechnet einen Fuzzy-Match-Score basierend auf Levenshtein-Distanz"""
            if not search_name or not target_name:
                return 0
            
            # Direkte Übereinstimmung
            if search_name == target_name:
                return 100
            
            # Token-basierte Übereinstimmung (bestehende Logik)
            search_tokens = search_name.split()
            target_tokens = target_name.split()
            
            # Spezielle Behandlung für arabische Namen mit "el" Präfix
            # Erstellt alternative Token-Varianten für besseres Matching
            search_tokens_extended = search_tokens.copy()
            target_tokens_extended = target_tokens.copy()
            
            # Fügt "el" + folgendes Token als kombiniertes Token hinzu
            for i, token in enumerate(search_tokens):
                if token == "el" and i + 1 < len(search_tokens):
                    search_tokens_extended.append("el" + search_tokens[i + 1])
            
            for i, token in enumerate(target_tokens):
                if token == "el" and i + 1 < len(target_tokens):
                    target_tokens_extended.append("el" + target_tokens[i + 1])
            
            # Berechnet Token-Matches mit erweiterten Tokens
            token_matches = sum(1 for t in search_tokens_extended if t in target_tokens_extended)
            
            # Zusätzlicher Bonus für arabische Namen
            arabic_bonus = 0
            if any('el' in token for token in search_tokens) and any('el' in token for token in target_tokens):
                # Prüft auf ähnliche Struktur bei arabischen Namen
                search_el_count = sum(1 for token in search_tokens if token == 'el')
                target_el_count = sum(1 for token in target_tokens if token == 'el')
                if search_el_count == target_el_count:
                    arabic_bonus = 20
            
            # Levenshtein-Distanz für ähnliche Namen
            distance = levenshtein_distance(search_name, target_name)
            max_len = max(len(search_name), len(target_name))
            
            if max_len == 0:
                return 0
            
            # Normalisierte Distanz (0-1, wobei 0 = perfekt)
            normalized_distance = distance / max_len
            
            # Score basierend auf Distanz (höher = besser)
            distance_score = max(0, 100 - (normalized_distance * 100))
            
            # Kombinierter Score: Token-Matches + Distanz-Score + Arabischer Bonus
            combined_score = (token_matches * 30) + (distance_score * 0.7) + arabic_bonus
            
            return combined_score

        clean_fahrer_label = clean_name(fahrer)

        def debug_matching(df, label, db_name):
            print(f"\n--- Matching-Debug für {db_name} ---")
            print(f"Suchwert (ComboBox, bereinigt): '{label}'")
            if db_name == "Uber" and "_combo_name" in df.columns and "_match" in df.columns:
                for idx_row, row in df.iterrows():
                    print(f"Name in DB: '{row['_combo_name']}' | Match-Score: {row['_match']}")
                    # Zusätzliche Debug-Info für arabische Namen
                    if 'el' in row['_combo_name'] or 'el' in label:
                        print(f"  -> Arabischer Name erkannt: '{row['_combo_name']}' vs '{label}'")
            elif db_name == "Bolt" and "_driver_name_clean" in df.columns and "_match" in df.columns:
                for idx_row, row in df.iterrows():
                    print(f"Name in DB: '{row['_driver_name_clean']}' | Match-Score: {row['_match']}")
                    # Zusätzliche Debug-Info für arabische Namen
                    if 'el' in row['_driver_name_clean'] or 'el' in label:
                        print(f"  -> Arabischer Name erkannt: '{row['_driver_name_clean']}' vs '{label}'")

        for db_name, db_file in [("Uber", "uber.sqlite"), ("Bolt", "bolt.sqlite")]:
            db_path = os.path.abspath(os.path.join("SQL", db_file))
            table_name = f"report_KW{kw}"
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                if db_name == "Uber":
                    if "first_name" in df.columns and "last_name" in df.columns:
                        df["_combo_name"] = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).apply(clean_name)
                        df["_match"] = df["_combo_name"].apply(lambda name: fuzzy_match_score(clean_fahrer_label, name))
                        debug_matching(df, clean_fahrer_label, db_name)
                        max_score = df["_match"].max() if not df.empty else 0
                        # Niedrigere Schwelle für Fuzzy-Matching (50 statt 2)
                        if max_score >= 50:
                            df = df[df["_match"] == max_score]
                            df = df.iloc[[0]] if len(df) > 1 else df
                        else:
                            df = df.iloc[0:0]
                        df = df.drop(columns=["_match", "_combo_name"])
                    else:
                        df = df.iloc[0:0]
                elif db_name == "Bolt":
                    if "driver_name" in df.columns:
                        df["_driver_name_clean"] = df["driver_name"].apply(clean_name)
                        df["_match"] = df["_driver_name_clean"].apply(lambda name: fuzzy_match_score(clean_fahrer_label, name))
                        debug_matching(df, clean_fahrer_label, db_name)
                        max_score = df["_match"].max() if not df.empty else 0
                        # Niedrigere Schwelle für Fuzzy-Matching (50 statt 2)
                        if max_score >= 50:
                            df = df[df["_match"] == max_score]
                            df = df.iloc[[0]] if len(df) > 1 else df
                        else:
                            df = df.iloc[0:0]
                        df = df.drop(columns=["_match", "_driver_name_clean"])
                    else:
                        df = df.iloc[0:0]
                if not df.empty:
                    self._found_pages.append((db_name, df.copy(), deal))
            except Exception as e:
                pass
            finally:
                try:
                    conn.close()
                except:
                    pass
                    
        self.foundPagesChanged.emit()
            
        if not self._found_pages:
            self._ergebnisse = [{"type": "error", "message": "Keine Einträge gefunden."}]
            self.ergebnisseChanged.emit()
            return
        # Deal ist bereits in auswerten() aus der Datenbank gesetzt
        # Übersichtsseite anzeigen
        self.show_overview_page()
        
    def auswerten_from_wizard(self):
        """Auswertung basierend auf Wizard-Daten"""
        data = self._wizard_data
        self.auswerten(data.get("fahrer", ""), data.get("fahrzeug", ""), data.get("kw", ""))
        
    @Slot()
    def show_overview_page(self):
        """Zeigt die Übersichtsseite mit allen Plattformen"""
        print("📋 ÜBERSICHTS-SEITE WIRD ANGEZEIGT")
        self._current_page = -1  # Übersichtsseite
        self.currentPageChanged.emit()
        # Summen für HeadCard
        uber_gross_total = 0.0
        bolt_echter_umsatz = 0.0
        bolt_rider_tips = 0.0
        bolt_cash_collected = 0.0
        _40100_real = 0.0
        _40100_trinkgeld = 0.0
        _40100_trinkgeld_gesamt = 0.0  # Gesamttrinkgeld für Berechnungen
        _40100_bargeld = 0.0
        uber_cash_collected = 0.0
        sum_40100 = 0
        sum_uber = 0
        sum_bolt = 0
        sum_bargeld = 0  # NEU: Summe aller Bargeldwerte
        # Detaillierte Ergebnisse für jede Plattform
        details_40100 = []
        details_uber = []
        details_bolt = []
        sum_31300 = 0
        _31300_trinkgeld = 0
        _31300_trinkgeld_gesamt = 0  # Gesamttrinkgeld für Berechnungen
        _31300_bargeld = 0
        _31300_real = 0
        # Detaillierte Ergebnisse für 31300
        details_31300 = []
        print(f"📊 Gefundene Datenquellen: {len(self._found_pages)}")
        for db_name, df, deal in self._found_pages:
            print(f"   🔍 Verarbeite {db_name}: {len(df) if df is not None else 0} Datensätze")
            if db_name == "40100" and df is not None:
                # 40100-Logik: Verwende Umsatz-Spalte statt Fahrtkosten
                # Filter: Nur Werte zwischen -250 und 250 berücksichtigen
                if "Umsatz" in df.columns:
                    df["Umsatz"] = pd.to_numeric(df["Umsatz"].astype(str).str.replace(",", "."), errors="coerce")
                    umsatz_mask = (df["Umsatz"] <= 250) & (df["Umsatz"] >= -250)
                    umsatz_40100 = df.loc[umsatz_mask, "Umsatz"]
                else:
                    umsatz_40100 = pd.Series(dtype=float)
                
                sum_40100 += umsatz_40100.sum()
                # Bargeld und Trinkgeld auch nur für gefilterte Werte berechnen
                bargeld_40100 = df.loc[umsatz_mask, "Bargeld"].sum() if "Bargeld" in df.columns else 0
                # Trinkgeld für echten Umsatz: Gesamtsumme (ohne Filter)
                trinkgeld_fuer_umsatz_40100 = df["Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
                
                # Trinkgeld für Anzeige: Summe nur wenn Buchungsart nicht 'Bar' enthält und Umsatz zwischen -250 und 250
                trinkgeld_mask = umsatz_mask
                if "Buchungsart" in df.columns:
                    trinkgeld_mask = trinkgeld_mask & ~df["Buchungsart"].str.contains("Bar", na=False)
                trinkgeld_40100 = df.loc[trinkgeld_mask, "Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
                sum_bargeld += bargeld_40100
                _40100_trinkgeld += trinkgeld_40100
                _40100_trinkgeld_gesamt += trinkgeld_fuer_umsatz_40100  # Gesamttrinkgeld für Berechnungen
                _40100_bargeld += bargeld_40100
                _40100_real += umsatz_40100.sum() - trinkgeld_fuer_umsatz_40100
                details_40100 = self.calculate_40100_details(df, deal)
            elif db_name == "31300" and df is not None:
                # Umsatz = Summe Gesamt (vorher Typumwandlung!)
                if "Gesamt" in df.columns:
                    df['Gesamt'] = pd.to_numeric(df['Gesamt'], errors='coerce')
                    # Filter: Nur Werte zwischen -250 und 250 berücksichtigen
                    gesamt_mask = (df["Gesamt"] <= 250) & (df["Gesamt"] >= -250)
                    gesamt_31300 = df.loc[gesamt_mask, "Gesamt"]
                else:
                    gesamt_31300 = pd.Series(dtype=float)
                umsatz_31300 = gesamt_31300.sum()
                # Bargeld = Summe Gesamt, wenn Buchungsart 'Bar' enthält
                if "Buchungsart" in df.columns and "Gesamt" in df.columns:
                    bargeld_31300 = df.loc[df["Buchungsart"].str.contains("Bar", na=False), "Gesamt"].sum()
                else:
                    bargeld_31300 = 0
                # Trinkgeld für echten Umsatz: Gesamtsumme (ohne Filter)
                trinkgeld_fuer_umsatz_31300 = df["Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
                
                # Trinkgeld für Anzeige: Summe nur wenn Buchungsart nicht 'Bar' enthält und Umsatz zwischen -250 und 250
                trinkgeld_mask = gesamt_mask
                if "Buchungsart" in df.columns:
                    trinkgeld_mask = trinkgeld_mask & ~df["Buchungsart"].str.contains("Bar", na=False)
                trinkgeld_31300 = df.loc[trinkgeld_mask, "Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
                echter_umsatz_31300 = umsatz_31300 - trinkgeld_fuer_umsatz_31300
                anteil_31300 = echter_umsatz_31300 / 2
                restbetrag_31300 = anteil_31300 - bargeld_31300 + trinkgeld_31300
                sum_31300 += umsatz_31300
                sum_bargeld += bargeld_31300
                _31300_trinkgeld += trinkgeld_31300
                _31300_trinkgeld_gesamt += trinkgeld_fuer_umsatz_31300  # Gesamttrinkgeld für Berechnungen
                _31300_bargeld += bargeld_31300
                _31300_real += echter_umsatz_31300
                details_31300 = [
                    {"label": "Real", "value": f"{echter_umsatz_31300:.2f} €"},
                    {"label": "Anteil", "value": f"{anteil_31300:.2f} €"},
                    {"label": "Bargeld", "value": f"{bargeld_31300:.2f} €"},
                    {"label": "Rest", "value": f"{restbetrag_31300:.2f} €"}
                ]
            elif db_name == "Uber" and df is not None:
                sum_uber += df["gross_total"].sum() if "gross_total" in df.columns else 0
                sum_bargeld += df["cash_collected"].sum() if "cash_collected" in df.columns else 0  # NEU
                uber_gross_total += df["gross_total"].sum() if "gross_total" in df.columns else 0
                uber_cash_collected += df["cash_collected"].sum() if "cash_collected" in df.columns else 0
                details_uber = self.calculate_uber_details(df)
            elif db_name == "Bolt" and df is not None:
                sum_bolt += df["net_earnings"].sum() if "net_earnings" in df.columns else 0
                sum_bargeld += df["cash_collected"].sum() if "cash_collected" in df.columns else 0  # NEU
                bolt_rider_tips += df["rider_tips"].sum() if "rider_tips" in df.columns else 0
                bolt_cash_collected += df["cash_collected"].sum() if "cash_collected" in df.columns else 0
                bolt_echter_umsatz += (df["net_earnings"].sum() if "net_earnings" in df.columns else 0) - (df["rider_tips"].sum() if "rider_tips" in df.columns else 0)
                details_bolt = self.calculate_bolt_details(df)
        # Summen für HeadCard und Gesamtzeile
        total_summe = sum_40100 + sum_31300 + sum_uber + sum_bolt
        taxi_real = _40100_real + _31300_real
        taxi_total = sum_40100 + sum_31300
        if taxi_total is None or not isinstance(taxi_total, (int, float)):
            taxi_total = 0.0

        # HeadCard Summen berechnen
        self._headcard_umsatz = float(sum_uber) + float(sum_bolt) + float(taxi_total)
        self._headcard_trinkgeld = bolt_rider_tips + _40100_trinkgeld + _31300_trinkgeld
        # Gesamttrinkgeld für Berechnungen (ohne Filter)
        self._headcard_trinkgeld_gesamt = bolt_rider_tips + _40100_trinkgeld_gesamt + _31300_trinkgeld_gesamt
        self._headcard_bargeld = uber_cash_collected + bolt_cash_collected + _40100_bargeld + _31300_bargeld
        self.headcardUmsatzChanged.emit()
        self.headcardTrinkgeldChanged.emit()
        self.headcardBargeldChanged.emit()
        
        # Neue Signals für separate Bargeld und Kreditkarte emittieren
        self.headcardCashChanged.emit()
        self.headcardCreditCardChanged.emit()
        
        # HeadCard Garage setzen (analog zur Property)
        try:
            kw = getattr(self, '_kw_label', "") if hasattr(self, '_kw_label') else ""
            jahr = datetime.now().year
            kw_int = int(kw) if kw else None
            if kw_int is not None:
                erster_tag_kw = datetime.strptime(f'{jahr}-W{kw_int}-1', "%Y-W%W-%w")
                monat = erster_tag_kw.month
                cal = calendar.Calendar(firstweekday=0)
                montage = [d for d in cal.itermonthdates(jahr, monat) if d.weekday() == 0 and d.month == monat]
                anzahl_montage = len(montage)
                print(f"DEBUG: Garage-Berechnung - KW: {kw_int}, Jahr: {jahr}, Monat: {monat}, Montage: {montage}, Anzahl: {anzahl_montage}")
                if anzahl_montage > 0:
                    self._headcard_garage = getattr(self, '_garage', 0.0) / anzahl_montage
                    print(f"DEBUG: Garage pro Montag berechnet: {getattr(self, '_garage', 0.0)} / {anzahl_montage} = {self._headcard_garage}")
                else:
                    self._headcard_garage = getattr(self, '_garage', 0.0)
                    print(f"DEBUG: Keine Montage gefunden, verwende Gesamt-Garage: {self._headcard_garage}")
            else:
                self._headcard_garage = getattr(self, '_garage', 0.0)
                print(f"DEBUG: Keine KW verfügbar, verwende Gesamt-Garage: {self._headcard_garage}")
        except Exception as e:
            print(f"Fehler bei Headcard-Garage-Berechnung: {e}")
            self._headcard_garage = getattr(self, '_garage', 0.0)
        print(f"DEBUG: Finale HeadCard Garage: {self._headcard_garage}")
        self.headcardGarageChanged.emit()
        
        # HeadCard je nach Deal-Typ aktualisieren
        self.update_headcard_for_deal()
        
        # Neue Summenzeile mit Bargeld und Kreditkarte
        headcard_cash = self._headcard_bargeld
        headcard_credit_card = (self._headcard_umsatz + self._headcard_trinkgeld) - self._headcard_bargeld
        
        print(f"💰 ERGEBNIS-ZUSAMMENFASSUNG:")
        print(f"   📊 Plattformen:")
        print(f"      🚕 Taxi (40100): {sum_40100:.2f} €")
        print(f"      🚕 Taxi (31300): {sum_31300:.2f} €")
        print(f"      🚗 Uber: {sum_uber:.2f} €")
        print(f"      ⚡ Bolt: {sum_bolt:.2f} €")
        print(f"      💵 Bargeld: {sum_bargeld:.2f} €")
        print(f"      📈 Gesamt: {total_summe:.2f} €")
        print(f"   📋 HeadCard:")
        print(f"      💰 Umsatz: {self._headcard_umsatz:.2f} €")
        print(f"      💸 Trinkgeld: {self._headcard_trinkgeld:.2f} €")
        print(f"      💵 Bargeld: {self._headcard_bargeld:.2f} €")
        print(f"   💳 Zahlungsarten:")
        print(f"      💵 Bargeld: {headcard_cash:.2f} €")
        print(f"      💳 Kreditkarte: {headcard_credit_card:.2f} €")
        
        # Übersicht mit detaillierten Ergebnissen
        # Kombiniere 40100 und 31300 zu einem einzigen Taxi-Eintrag
        taxi_summe = sum_40100 + sum_31300
        taxi_details = []
        if sum_40100 > 0 and sum_31300 > 0:
            # Wenn beide Datenquellen vorhanden sind, kombiniere die Details.
            # Dies ist eine vereinfachte Darstellung, die wichtigste Info ist die Summe.
            taxi_details = details_40100 + details_31300
        elif sum_40100 > 0:
            taxi_details = details_40100
        else:
            taxi_details = details_31300
            
        self._ergebnisse = [
            {"type": "title", "text": "Übersicht"},
            # Verwende den kombinierten Taxi-Eintrag
            *([{"type": "summary", "label": "Taxi", "value": f"{taxi_summe:.2f} €", "details": taxi_details}] if taxi_summe > 0 else []),
            {"type": "summary", "label": "Uber", "value": f"{sum_uber:.2f} €", "details": details_uber},
            {"type": "summary", "label": "Bolt", "value": f"{sum_bolt:.2f} €", "details": details_bolt},
            {"type": "summary", "label": "Bargeld", "value": f"{headcard_cash:.2f} €", "icon": "assets/icons/cash_gray.svg"},
            {"type": "summary", "label": "Kreditkarte", "value": f"{headcard_credit_card:.2f} €", "icon": "assets/icons/credit_card_gray.svg"},
            {"type": "summary", "label": "Gesamt", "value": f"{total_summe:.2f} €"}
        ]
        print(f"✅ Ergebnisse erstellt: {len(self._ergebnisse)} Einträge")
        self.ergebnisseChanged.emit()
        self.update_ergebnis(taxi_total=float(taxi_total))
        

        
    def calculate_uber_details(self, df):
        werte = self._berechne_platform_werte(df, "Uber")
        return [
            {"label": "Total", "value": f"{werte['gross_total']:.2f} €"},
            {"label": "Anteil", "value": f"{werte['anteil']:.2f} €"},
            {"label": "Bargeld", "value": f"{werte['cash_collected']:.2f} €"},
            {"label": "Restbetrag", "value": f"{werte['restbetrag']:.2f} €"}
        ]
        

        
    def show_page(self, idx):
        if idx >= len(self._found_pages):
            return
            
        self._current_page = idx
        self.currentPageChanged.emit()
        
        db_name, df, deal = self._found_pages[idx]
        
        ergebnisse = []
        
        if db_name == "40100":
            ergebnisse = self.calculate_40100_results(df, deal)
        elif db_name == "Uber":
            ergebnisse = self.calculate_uber_results(df)
        elif db_name == "Bolt":
            ergebnisse = self.calculate_bolt_results(df)
            
        self._ergebnisse = ergebnisse
        self.ergebnisseChanged.emit()
        

        
    def calculate_uber_results(self, df):
        werte = self._berechne_platform_werte(df, "Uber")
        return [
            {"type": "title", "text": "Uber"},
            {"type": "value", "label": "Total", "value": f"{werte['gross_total']:.2f} €", "hint": "/ 2"},
            {"type": "value", "label": "Anteil", "value": f"{werte['anteil']:.2f} €", "hint": "- Auszahlung"},
            {"type": "value", "label": "Restbetrag", "value": f"{werte['restbetrag']:.2f} €", "hint": ""}
        ]
        

        
    @Slot(int)
    def change_page(self, page_idx):
        if page_idx == -1:
            self.show_overview_page()
        else:
            self.show_page(page_idx)
        
    @Slot()
    def show_details(self):
        if self._current_page >= 0 and self._current_page < len(self._found_pages):
            db_name, df, deal = self._found_pages[self._current_page]
            if df is not None:
                print(f"Details für {db_name}:")
                print(df.to_string())

    @Slot(result=dict)
    def get_current_selection(self):
        """Gibt die aktuelle Auswahl zurück"""
        # Fahrer-ID-Laden entfernt, da fehlerhaft und nicht benötigt
        return {
            "fahrer": self._fahrer_label,
            "fahrer_id": None,
            "fahrzeug": self._wizard_data.get("fahrzeug", ""),
            "kw": self._wizard_data.get("kw", "")
        }

    def set_root_window(self, root_window):
        self._root_window = root_window

    @Slot()
    def update_ergebnis(self, taxi_total=None):
        """Aktualisiert das Ergebnis basierend auf aktuellen Werten und Overlay-Konfiguration"""
        try:
            # Overlay-Logik aus QML integrieren
            overlay_income = self._calculate_overlay_income()
            print(f"💰 Overlay Income berechnet: {overlay_income:.2f} €")
            
            # Basis-Werte
            credit_card = self._headcard_credit_card if hasattr(self, '_headcard_credit_card') else 0.0
            trinkgeld = self._headcard_trinkgeld if hasattr(self, '_headcard_trinkgeld') else 0.0
            
            # Expenses
            expenses_sum = 0.0
            if hasattr(self, '_expense_cache') and self._expense_cache:
                try:
                    expenses_sum = sum(float(e.get('amount', 0)) for e in self._expense_cache)
                except Exception:
                    expenses_sum = 0.0
            print(f"💸 Expenses: {expenses_sum:.2f} €")
            
            # Ergebnis mit Overlay-Logik
            self._ergebnis = credit_card - overlay_income + trinkgeld + expenses_sum
            print(f"📊 ERGEBNIS-BERECHNUNG:")
            print(f"   💳 Kreditkarte: {credit_card:.2f} €")
            print(f"   💰 Overlay Income: -{overlay_income:.2f} €")
            print(f"   💸 Trinkgeld: +{trinkgeld:.2f} €")
            print(f"   💸 Expenses: +{expenses_sum:.2f} €")
            print(f"   📈 Finales Ergebnis: {self._ergebnis:.2f} €")
            self.ergebnisChanged.emit()
            
        except Exception as e:
            print(f"❌ Fehler bei Overlay-Berechnung: {e}")
            # Fallback: Setze Ergebnis auf 0
            self._ergebnis = 0.0
            self.ergebnisChanged.emit()

    def _calculate_overlay_income(self):
        """Berechnet das Overlay-Income basierend auf den aktuellen Faktoren (P-Deal und C-Deal Logik)"""
        try:
            income = 0.0
            
            # Pauschale und Umsatzgrenze aus den aktuellen Werten
            pauschale = getattr(self, '_pauschale', 500.0)
            umsatzgrenze = getattr(self, '_umsatzgrenze', 1200.0)
            
            # Aktuelle Faktoren aus dem Backend holen
            taxi_faktor = getattr(self, '_taxi_faktor', 0.0)
            uber_faktor = getattr(self, '_uber_faktor', 0.0)
            bolt_faktor = getattr(self, '_bolt_faktor', 0.0)
            einsteiger_faktor = getattr(self, '_einsteiger_faktor', 0.0)
            tank_faktor = getattr(self, '_tank_faktor', 0.0)
            garage_faktor = getattr(self, '_garage_faktor', 0.5)
            
            # Prüfen, ob mindestens eine relevante Plattform auf P steht (Faktor = 0.0)
            has_any_p_deal = (taxi_faktor == 0.0 or uber_faktor == 0.0 or 
                             bolt_faktor == 0.0 or einsteiger_faktor == 0.0)
            
            # 1. Pauschale und Grenzzuschlag (nur wenn mindestens eine Plattform auf P steht)
            if has_any_p_deal:
                # Pauschale hinzufügen
                income += pauschale
                
                # Grenzzuschlag prüfen
                summe_umsatz = 0.0
                taxi_umsatz = self._get_platform_umsatz('Taxi')
                uber_umsatz = self._get_platform_umsatz('Uber')
                bolt_umsatz = self._get_platform_umsatz('Bolt')
                summe_umsatz = taxi_umsatz + uber_umsatz + bolt_umsatz
                
                if summe_umsatz > umsatzgrenze:
                    bonus = (summe_umsatz - umsatzgrenze) * 0.1
                    income += bonus
            
            # 2. Faktor-basierte Berechnung für alle Plattformen
            platform_income = 0.0
            
            # Taxi
            if taxi_faktor > 0:
                taxi_umsatz = self._get_platform_umsatz('Taxi')
                taxi_income = taxi_umsatz * taxi_faktor
                platform_income += taxi_income
            
            # Uber
            if uber_faktor > 0:
                uber_umsatz = self._get_platform_umsatz('Uber')
                uber_income = uber_umsatz * uber_faktor
                platform_income += uber_income
            
            # Bolt
            if bolt_faktor > 0:
                bolt_umsatz = self._get_platform_umsatz('Bolt')
                bolt_income = bolt_umsatz * bolt_faktor
                platform_income += bolt_income
            
            # Einsteiger
            if einsteiger_faktor > 0:
                einsteiger_umsatz = self._get_platform_umsatz('Einsteiger')
                einsteiger_income = einsteiger_umsatz * einsteiger_faktor
                platform_income += einsteiger_income
            
            income += platform_income
            
            # 3. Abzüge für Tank und Garage
            abzuege = 0.0
            
            if tank_faktor > 0:
                tank_umsatz = float(self._input_gas) if hasattr(self, '_input_gas') and self._input_gas else 0.0
                tank_abzug = tank_umsatz * tank_faktor
                abzuege += tank_abzug
            
            if garage_faktor > 0:
                garage_umsatz = self.headcard_garage
                garage_abzug = garage_umsatz * garage_faktor
                abzuege += garage_abzug
            
            # Finales Ergebnis = Overlay Income - Abzüge
            final_income = income - abzuege
            return final_income
            
        except Exception as e:
            print(f"      ❌ Fehler bei _calculate_overlay_income: {e}")
            return 0.0
    
    def _get_platform_umsatz(self, platform):
        """Holt den Umsatz für eine bestimmte Plattform"""
        try:
            if platform == 'Einsteiger':
                return float(self._input_einsteiger) if hasattr(self, '_input_einsteiger') and self._input_einsteiger else 0.0
            
            # Aus den Ergebnissen holen
            if hasattr(self, '_ergebnisse') and self._ergebnisse:
                for ergebnis in self._ergebnisse:
                    if ergebnis.get('label') == platform:
                        details = ergebnis.get('details', [])
                        for detail in details:
                            if platform == 'Taxi' and detail.get('label') == 'Real':
                                value_str = detail.get('value', '0').replace('€', '').replace(' ', '').strip()
                                return float(value_str) if value_str else 0.0
                            elif platform in ['Uber', 'Bolt'] and detail.get('label') == 'Total':
                                value_str = detail.get('value', '0').replace('€', '').replace(' ', '').strip()
                                return float(value_str) if value_str else 0.0
            
            # Fallback: Aus HeadCard-Werten holen (für den Fall, dass _ergebnisse noch nicht aktualisiert ist)
            if platform == 'Taxi':
                return getattr(self, '_headcard_umsatz', 0.0) - getattr(self, '_headcard_trinkgeld', 0.0)
            elif platform == 'Uber':
                # Uber-Umsatz ist Teil des Gesamtumsatzes, aber wir haben keine separate Variable
                return 0.0  # Wird aus _ergebnisse gelesen
            elif platform == 'Bolt':
                # Bolt-Umsatz ist Teil des Gesamtumsatzes, aber wir haben keine separate Variable
                return 0.0  # Wird aus _ergebnisse gelesen
            
            return 0.0
            
        except Exception as e:
            print(f"DEBUG: Fehler bei _get_platform_umsatz für {platform}: {e}")
            return 0.0

    def show_duplicate_comparison_dialog(self, existing_entry, new_entry, fahrzeug, kw, fahrer, deal):
        """Zeigt einen Dialog zur Auswahl zwischen bestehendem und neuem Eintrag"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
        from PySide6.QtCore import Qt
        
        dialog = QDialog()
        dialog.setWindowTitle("Duplikat gefunden - Eintrag auswählen")
        dialog.setModal(True)
        dialog.resize(700, 500)
        dialog.setFixedSize(700, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Überschrift
        title = QLabel(f"Für {fahrer} - {fahrzeug} - KW {kw} existiert bereits ein Eintrag:")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffffff; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Vergleichsbereich
        comparison_layout = QHBoxLayout()
        comparison_layout.setSpacing(20)
        
        # Bestehender Eintrag
        existing_layout = QVBoxLayout()
        existing_title = QLabel("Bestehender Eintrag:")
        existing_title.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; margin-bottom: 5px;")
        existing_layout.addWidget(existing_title)
        
        existing_text = QTextEdit()
        existing_text.setReadOnly(True)
        existing_text.setMaximumHeight(200)
        existing_text.setStyleSheet("""
            QTextEdit {
                background: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 10px;
                color: #ffffff;
                font-size: 11pt;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        # Expenses für bestehenden Eintrag abrufen
        existing_expenses = self._get_expenses_for_week(fahrzeug, existing_entry[1])
        existing_expenses_text = ""
        if existing_expenses:
            existing_expenses_text = "\n\n📋 Ausgaben:\n" + "\n".join([f"  • {exp[3]}: {exp[2]:.2f} €" for exp in existing_expenses])
        
        existing_text.setPlainText(f"""💰 Deal: {existing_entry[2]}
💵 Total: {existing_entry[4]:.2f} €
💸 Income: {existing_entry[5]:.2f} €
⏰ Timestamp: {existing_entry[6]}{existing_expenses_text}""")
        existing_layout.addWidget(existing_text)
        
        # Neuer Eintrag
        new_layout = QVBoxLayout()
        new_title = QLabel("Neuer Eintrag:")
        new_title.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; margin-bottom: 5px;")
        new_layout.addWidget(new_title)
        
        new_text = QTextEdit()
        new_text.setReadOnly(True)
        new_text.setMaximumHeight(200)
        new_text.setStyleSheet("""
            QTextEdit {
                background: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 10px;
                color: #ffffff;
                font-size: 11pt;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        # Expenses für neuen Eintrag (aus Cache) formatieren
        new_expenses_text = ""
        if hasattr(self, '_expense_cache') and self._expense_cache:
            new_expenses_text = "\n\n📋 Ausgaben:\n" + "\n".join([f"  • {exp.get('category', 'Unbekannt')}: {float(exp.get('amount', 0)):.2f} €" for exp in self._expense_cache])
        
        # Gas hinzufügen
        if hasattr(self, '_input_gas') and self._input_gas:
            gas_amount = float(self._input_gas)
            if gas_amount > 0:
                if new_expenses_text:
                    new_expenses_text += f"\n  • Gas: {gas_amount:.2f} €"
                else:
                    new_expenses_text = f"\n\n📋 Ausgaben:\n  • Gas: {gas_amount:.2f} €"
        
        new_text.setPlainText(f"""💰 Deal: {new_entry['deal']}
💵 Total: {new_entry['total']:.2f} €
💸 Income: {new_entry['income']:.2f} €
⏰ Timestamp: {new_entry['timestamp']}{new_expenses_text}""")
        new_layout.addWidget(new_text)
        
        comparison_layout.addLayout(existing_layout)
        comparison_layout.addLayout(new_layout)
        layout.addLayout(comparison_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        keep_existing_btn = QPushButton("Bestehenden behalten")
        keep_existing_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #2E86AB;
                border-radius: 4px;
                padding: 10px 20px;
                color: #2E86AB;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(46, 134, 171, 0.1);
            }
        """)
        keep_existing_btn.clicked.connect(lambda: self._handle_duplicate_choice(dialog, "keep_existing", existing_entry, new_entry, fahrzeug))
        
        replace_btn = QPushButton("Durch neuen ersetzen")
        replace_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #A23B72;
                border-radius: 4px;
                padding: 10px 20px;
                color: #A23B72;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(162, 59, 114, 0.1);
            }
        """)
        replace_btn.clicked.connect(lambda: self._handle_duplicate_choice(dialog, "replace", existing_entry, new_entry, fahrzeug))
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 10px 20px;
                color: #ffffff;
                font-size: 12pt;
            }
            QPushButton:hover {
                border-color: #f79009;
                background: rgba(247, 144, 9, 0.1);
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(keep_existing_btn)
        button_layout.addWidget(replace_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Dialog-Styling
        dialog.setStyleSheet("""
            QDialog {
                background: #000000;
            }
        """)
        
        dialog.setLayout(layout)
        return dialog.exec()

    def _handle_duplicate_choice(self, dialog, choice, existing_entry, new_entry, fahrzeug):
        """Behandelt die Benutzerauswahl bei Duplikaten"""
        try:
            import sqlite3
            db_path = os.path.join("SQL", "revenue.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            if choice == "replace":
                # Bestehenden Eintrag löschen und neuen einfügen
                cursor.execute(f"DELETE FROM '{fahrzeug}' WHERE id = ?", (existing_entry[0],))
                cursor.execute(f"""
                    INSERT INTO '{fahrzeug}' (cw, deal, driver, total, income, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (new_entry['cw'], new_entry['deal'], new_entry['driver'], 
                      new_entry['total'], new_entry['income'], new_entry['timestamp']))
                
                # Flag setzen für Expenses-Behandlung
                self._duplicate_replaced = True
                
                # Auch Expenses ersetzen
                self._replace_expenses(fahrzeug, new_entry['cw'], new_entry['driver'])
                
                print(f"Eintrag ersetzt: Neuer Eintrag für {new_entry['driver']} - KW {new_entry['cw']}")
                
            elif choice == "keep_existing":
                # Flag setzen für Expenses-Behandlung
                self._duplicate_replaced = False
                print(f"Bestehender Eintrag beibehalten für {existing_entry[3]} - KW {existing_entry[1]}")
            
            conn.commit()
            conn.close()
            dialog.accept()
            
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Duplikat-Auswahl: {e}")
            dialog.reject()

    def _replace_expenses(self, fahrzeug, cw, driver):
        """Ersetzt Expenses für eine bestimmte KW"""
        try:
            db_path_exp = os.path.join("SQL", "running_costs.db")
            conn_exp = sqlite3.connect(db_path_exp)
            cursor_exp = conn_exp.cursor()
            
            # Erst prüfen, wie viele alte Expenses existieren
            cursor_exp.execute(f"SELECT COUNT(*) FROM '{fahrzeug}' WHERE cw = ?", (cw,))
            old_count = cursor_exp.fetchone()[0]
            print(f"Gefundene alte Expenses für KW {cw}: {old_count}")
            
            # Alte Expenses für diese KW löschen
            cursor_exp.execute(f"DELETE FROM '{fahrzeug}' WHERE cw = ?", (cw,))
            deleted_count = cursor_exp.rowcount
            print(f"Gelöschte Expenses: {deleted_count}")
            
            # Neue Expenses einfügen
            new_count = 0
            for eintrag in getattr(self, '_expense_cache', []):
                exp_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor_exp.execute(f"""
                    INSERT INTO '{fahrzeug}' (cw, amount, category, details, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (cw, float(eintrag.get("amount", 0)),
                      eintrag.get("category", ""), eintrag.get("details", ""), exp_timestamp))
                new_count += 1
            
            # Gas als eigenen Expense speichern
            if hasattr(self, '_input_gas') and self._input_gas:
                exp_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor_exp.execute(f"""
                    INSERT INTO '{fahrzeug}' (cw, amount, category, details, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (cw, float(self._input_gas), "Gas", "", exp_timestamp))
                new_count += 1
            
            print(f"Neue Expenses eingefügt: {new_count}")
            
            conn_exp.commit()
            conn_exp.close()
            
        except Exception as e:
            print(f"Fehler beim Ersetzen der Expenses: {e}")
            import traceback
            traceback.print_exc()

    def _get_expenses_for_week(self, fahrzeug, cw):
        """Holt alle Expenses für eine bestimmte KW"""
        try:
            db_path_exp = os.path.join("SQL", "running_costs.db")
            conn_exp = sqlite3.connect(db_path_exp)
            cursor_exp = conn_exp.cursor()
            
            cursor_exp.execute(f"SELECT * FROM '{fahrzeug}' WHERE cw = ? ORDER BY category, amount", (cw,))
            expenses = cursor_exp.fetchall()
            conn_exp.close()
            return expenses
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Expenses: {e}")
            return []

    def _clear_expenses_for_week(self, fahrzeug, cw):
        """Löscht alle Expenses für eine bestimmte KW"""
        try:
            db_path_exp = os.path.join("SQL", "running_costs.db")
            conn_exp = sqlite3.connect(db_path_exp)
            cursor_exp = conn_exp.cursor()
            
            cursor_exp.execute(f"DELETE FROM '{fahrzeug}' WHERE cw = ?", (cw,))
            conn_exp.commit()
            conn_exp.close()
            
        except Exception as e:
            print(f"Fehler beim Löschen der Expenses: {e}")

    @Slot()
    def speichereUmsatz(self):
        """
        Generische Speichermethode: Führt alle generischen Aufgaben aus und ruft die deal-spezifische Logik ab.
        """
        print("🔵 SPEICHEREUMSATZ GESTARTET")
        print(f"📋 _wizard_data: {self._wizard_data}")
        
        # 1. Deal-spezifische Werte berechnen lassen
        deal_result = self._berechne_deal_result()
        if not deal_result:
            print("❌ Fehler: Keine Deal-Ergebnisse berechnet.")
            return

        print(f"✅ Deal-Ergebnis berechnet: {deal_result}")

        # 2. Umsatz/Income in revenue.db speichern
        print("💾 Speichere Revenue-Eintrag...")
        self._speichere_revenue_entry(deal_result)

        # 3. Expenses (inkl. Garage) in running_costs.db speichern
        print("💾 Speichere Expenses...")
        self._speichere_expenses(deal_result)

        # 4. Pauschale und Umsatzgrenze in deals Tabelle speichern, falls verändert
        print("💾 Prüfe Pauschale und Umsatzgrenze für Speicherung...")
        self._speichere_pauschale_umsatzgrenze(deal_result)
        
        # 5. Den letzten Speicherstand in custom_deal_config speichern
        print("💾 Speichere letzten Speicherstand in custom_deal_config...")
        self._speichere_letzten_speicherstand(deal_result)
        
        # 6. Felder und Caches leeren
        print("🧹 Leere Caches und Felder...")
        self._expense_cache = []
        self._custom_deal_cache = {}
        self.inputGas = ""
        self.inputEinsteiger = ""
        self.inputExpense = ""
        
        print("✅ SPEICHEREUMSATZ BEENDET")

    def _berechne_deal_result(self):
        """
        Deal-spezifische Logik: Gibt ein dict mit allen für die Speicherung nötigen Werten zurück.
        Unterstützt %, C und P Deals.
        """
        deal = getattr(self, '_deal', '%')
        # Sicherstellen, dass beide Werte als Float behandelt werden
        headcard_umsatz = float(getattr(self, '_headcard_umsatz', 0.0))
        
        # Sichere Konvertierung von input_einsteiger (kann leerer String sein)
        input_einsteiger_raw = getattr(self, '_input_einsteiger', 0.0)
        if input_einsteiger_raw == '' or input_einsteiger_raw is None:
            input_einsteiger = 0.0
        else:
            input_einsteiger = float(input_einsteiger_raw)
            
        total = headcard_umsatz + input_einsteiger
        
        if deal == "%":
            # %-Deal: 50% vom Gesamtumsatz
            income = total / 2
            return {
                "deal": deal,
                "income": income,
                "total": total,
                "fahrer": self._wizard_data.get("fahrer", ""),
                "fahrzeug": self._wizard_data.get("fahrzeug", ""),
                "kw": self._wizard_data.get("kw", ""),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        elif deal == "C":
            # Custom-Deal: income aus overlayIncome (custom_income im Cache)
            income = self._custom_deal_cache.get('custom_income', 0.0)
            return {
                "deal": deal,
                "income": income,
                "total": total,
                "fahrer": self._wizard_data.get("fahrer", ""),
                "fahrzeug": self._wizard_data.get("fahrzeug", ""),
                "kw": self._wizard_data.get("kw", ""),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        elif deal == "P":
            # P-Deal: Pauschale + Faktor-basierte Berechnung
            income = self._calculate_overlay_income()
            return {
                "deal": deal,
                "income": income,
                "total": total,
                "fahrer": self._wizard_data.get("fahrer", ""),
                "fahrzeug": self._wizard_data.get("fahrzeug", ""),
                "kw": self._wizard_data.get("kw", ""),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            # Fallback für unbekannte Deal-Typen
            print(f"Warnung: Unbekannter Deal-Typ '{deal}', verwende Standard-Berechnung")
            income = total / 2
            return {
                "deal": deal,
                "income": income,
                "total": total,
                "fahrer": self._wizard_data.get("fahrer", ""),
                "fahrzeug": self._wizard_data.get("fahrzeug", ""),
                "kw": self._wizard_data.get("kw", ""),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def _speichere_revenue_entry(self, deal_result):
        """
        Speichert den Umsatz/Income-Eintrag in revenue.db (generisch), inkl. neuer Spalte 'taxed'.
        Überschreibt immer alte Einträge für die Kombination (cw, fahrer), unabhängig vom Deal-Typ.
        Aktualisiert nach dem Speichern auch den Deal in database.db.
        Zeigt vor dem Überschreiben einen Vergleichsdialog an, falls bereits ein Eintrag existiert.
        """
        import sqlite3
        import os
        from datetime import datetime
        db_path = os.path.join("SQL", "revenue.db")
        table_vehicle = deal_result["fahrzeug"]
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS '{table_vehicle}' (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cw INTEGER NOT NULL CHECK (cw BETWEEN 1 AND 52),
                deal TEXT,
                driver TEXT,
                total DECIMAL(10,2),
                taxed DECIMAL(10,2),
                income DECIMAL(10,2) NOT NULL,
                timestamp DATETIME
            )
        """)
        # Prüfe, ob bereits ein Eintrag für diese KW und Fahrer existiert
        cursor.execute(f"""
            SELECT * FROM '{table_vehicle}' WHERE cw = ? AND driver = ?
        """, (
            int(deal_result["kw"]) if deal_result["kw"] else None,
            deal_result["fahrer"]
        ))
        existing_entry = cursor.fetchone()
        if existing_entry:
            # Vergleichsdialog anzeigen
            result = self.show_duplicate_comparison_dialog(
                existing_entry,
                {
                    'cw': int(deal_result["kw"]) if deal_result["kw"] else None,
                    'deal': deal_result["deal"],
                    'driver': deal_result["fahrer"],
                    'total': deal_result["total"],
                    'income': deal_result["income"],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                table_vehicle,
                deal_result["kw"],
                deal_result["fahrer"],
                deal_result["deal"]
            )
            from PySide6.QtWidgets import QDialog
            if result != QDialog.Accepted:
                conn.close()
                return  # Speichern abbrechen, wenn nicht ersetzt werden soll
            # Wenn ersetzt werden soll, alten Eintrag löschen
            cursor.execute(f"""
                DELETE FROM '{table_vehicle}' WHERE cw = ? AND driver = ?
            """, (
                int(deal_result["kw"]) if deal_result["kw"] else None,
                deal_result["fahrer"]
            ))
        # Neuen Eintrag einfügen
        cursor.execute(f"""
            INSERT INTO '{table_vehicle}' (cw, deal, driver, total, taxed, income, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            int(deal_result["kw"]) if deal_result["kw"] else None,
            deal_result["deal"],
            deal_result["fahrer"],
            deal_result["total"],
            self._headcard_umsatz,
            deal_result["income"],
            deal_result["timestamp"]
        ))
        conn.commit()
        conn.close()
        # Deal in database.db aktualisieren
        db_path_db = os.path.join("SQL", "database.db")
        conn_db = sqlite3.connect(db_path_db)
        cursor_db = conn_db.cursor()
        cursor_db.execute("""
            UPDATE deals SET deal = ? WHERE name = ?
        """, (deal_result["deal"], deal_result["fahrer"]))
        conn_db.commit()
        conn_db.close()

    def _speichere_pauschale_umsatzgrenze(self, deal_result):
        """
        Speichert Pauschale und Umsatzgrenze in der deals Tabelle, falls sie verändert wurden.
        """
        import sqlite3
        import os
        
        # Hole aktuelle Werte
        aktuelle_pauschale = getattr(self, '_pauschale', 500.0)
        aktuelle_umsatzgrenze = getattr(self, '_umsatzgrenze', 1200.0)
        fahrer = deal_result["fahrer"]
        
        # Prüfe, ob Werte geändert wurden (Standardwerte: Pauschale=500, Umsatzgrenze=1200)
        if aktuelle_pauschale != 500.0 or aktuelle_umsatzgrenze != 1200.0:
            print(f"💾 Speichere geänderte Werte: Pauschale={aktuelle_pauschale}, Umsatzgrenze={aktuelle_umsatzgrenze}")
            
            db_path = os.path.join("SQL", "database.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Prüfe, ob deals Tabelle existiert (Spalten pauschale und umsatzgrenze sind bereits vorhanden)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    deal TEXT,
                    pauschale REAL DEFAULT 500.0,
                    umsatzgrenze REAL DEFAULT 1200.0
                )
            """)
            
            # Prüfe, ob Eintrag für diesen Fahrer existiert
            cursor.execute("SELECT * FROM deals WHERE name = ?", (fahrer,))
            existing_entry = cursor.fetchone()
            
            if existing_entry:
                # Update bestehenden Eintrag
                cursor.execute("""
                    UPDATE deals SET pauschale = ?, umsatzgrenze = ? WHERE name = ?
                """, (aktuelle_pauschale, aktuelle_umsatzgrenze, fahrer))
                print(f"✅ Pauschale und Umsatzgrenze für {fahrer} aktualisiert")
            else:
                # Erstelle neuen Eintrag
                cursor.execute("""
                    INSERT INTO deals (name, deal, pauschale, umsatzgrenze) 
                    VALUES (?, ?, ?, ?)
                """, (fahrer, deal_result["deal"], aktuelle_pauschale, aktuelle_umsatzgrenze))
                print(f"✅ Neuer Eintrag für {fahrer} mit Pauschale und Umsatzgrenze erstellt")
            
            conn.commit()
            conn.close()
        else:
            print("ℹ️ Pauschale und Umsatzgrenze unverändert, keine Speicherung nötig")

    def _speichere_letzten_speicherstand(self, deal_result):
        """
        Speichert den letzten Speicherstand in custom_deal_config.
        """
        import sqlite3
        import os
        import json
        
        fahrer = deal_result["fahrer"]
        
        # Hole aktuelle Werte für den letzten Speicherstand
        aktueller_cache = getattr(self, '_overlay_config_cache', [])
        
        if aktueller_cache:
            print(f"💾 Speichere letzten Speicherstand für {fahrer}")
            
            db_path = os.path.join("SQL", "database.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Prüfe, ob custom_deal_config Tabelle existiert
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_deal_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fahrer TEXT UNIQUE,
                    config_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Konvertiere Cache zu JSON
            config_json = json.dumps(aktueller_cache)
            
            # Prüfe, ob Eintrag für diesen Fahrer existiert
            cursor.execute("SELECT * FROM custom_deal_config WHERE fahrer = ?", (fahrer,))
            existing_entry = cursor.fetchone()
            
            if existing_entry:
                # Update bestehenden Eintrag
                cursor.execute("""
                    UPDATE custom_deal_config SET config_json = ?, timestamp = CURRENT_TIMESTAMP 
                    WHERE fahrer = ?
                """, (config_json, fahrer))
                print(f"✅ Letzten Speicherstand für {fahrer} aktualisiert")
            else:
                # Erstelle neuen Eintrag
                cursor.execute("""
                    INSERT INTO custom_deal_config (fahrer, config_json) 
                    VALUES (?, ?)
                """, (fahrer, config_json))
                print(f"✅ Neuer Eintrag für {fahrer} mit letztem Speicherstand erstellt")
            
            conn.commit()
            conn.close()
        else:
            print("ℹ️ Kein Cache vorhanden, kein letzter Speicherstand zu speichern")

    def _speichere_expenses(self, deal_result):
        """
        Speichert alle Expenses (inkl. Garage und Tank) in running_costs.db (generisch).
        Kategorie für Garage: 'Parking', für Tank: 'Gas'.
        Beschreibung (details): Faktor aus Overlay (Sliderwert, falls vorhanden).
        """
        import sqlite3
        import os
        from datetime import datetime
        db_path = os.path.join("SQL", "running_costs.db")
        table_vehicle = deal_result["fahrzeug"]
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS '{table_vehicle}' (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cw INTEGER,
                amount DECIMAL(10,2),
                category TEXT,
                details TEXT,
                timestamp DATETIME
            )
        """)
        kw = int(deal_result["kw"]) if deal_result["kw"] else None
        # 1. Alle Einträge aus _expense_cache speichern
        for eintrag in getattr(self, '_expense_cache', []):
            exp_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(f"""
                INSERT INTO '{table_vehicle}' (cw, amount, category, details, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                kw,
                float(eintrag.get("amount", 0)),
                eintrag.get("category", ""),
                eintrag.get("details", ""),
                exp_timestamp
            ))
        # 2. Garage speichern (Kategorie 'Parking', details = Faktor)
        garage_amount = getattr(self, '_headcard_garage', 0.0)
        tank_amount = getattr(self, '_input_gas', 0.0)
        print(f"[DEBUG] Speichere Garage-Expense: amount={garage_amount}, Tank-Expense: amount={tank_amount}")
        if garage_amount:
            # Faktor aus Overlay-Konfiguration holen, falls vorhanden
            garage_faktor = 1.0
            if hasattr(self, '_overlay_config_cache') and self._overlay_config_cache:
                for item in self._overlay_config_cache:
                    if item.get('platform') == 'Garage':
                        garage_faktor = item.get('slider', 100) / 100.0
            exp_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(f"""
                INSERT INTO '{table_vehicle}' (cw, amount, category, details, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                kw,
                garage_amount,  # explizit _headcard_garage
                "Parking",
                f"Faktor: {garage_faktor}",
                exp_timestamp
            ))
        # 3. Tank speichern (Kategorie 'Gas', details = Faktor)
        if tank_amount:
            tank_faktor = 1.0
            if hasattr(self, '_overlay_config_cache') and self._overlay_config_cache:
                for item in self._overlay_config_cache:
                    if item.get('platform') == 'Tank':
                        tank_faktor = item.get('slider', 100) / 100.0
            exp_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(f"""
                INSERT INTO '{table_vehicle}' (cw, amount, category, details, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                kw,
                tank_amount,  # explizit _input_gas (unverändert)
                "Gas",
                f"Faktor: {tank_faktor}",
                exp_timestamp
            ))


    @Slot()
    def show_wizard_add_cost(self):
        """Zeigt einen GenericWizard für Kosten-Eintrag (Kategorie + Details) an."""
        kategorien = ["Service", "Parking", "Interior", "Sonstiges"]
        fields = [
            ("Kategorie", "kategorie", "combo", kategorien),
            ("Details", "details", "text")
        ]
        def wizard_callback(data):
            betrag = self.inputExpense
            print(f"[DEBUG] Ergebnis vor Hinzufügen: {self._ergebnis}")
            eintrag = {
                "amount": betrag,
                "category": data.get("kategorie", ""),
                "details": data.get("details", "")
            }
            self._expense_cache.append(eintrag)
            print(f"Kosten-Eintrag zwischengespeichert: {eintrag}")
            self.inputExpense = ""  # Eingabefeld leeren
            self.update_ergebnis()  # Ergebnis sofort neu berechnen
            print(f"[DEBUG] Ergebnis nach Hinzufügen: {self._ergebnis}")
        parent = None
        wizard = GenericWizard(fields, callback=wizard_callback, parent=parent, title="Kosten-Eintrag")
        wizard.show()

    def update_headcard_for_deal(self):
        """Aktualisiert die HeadCard-Werte je nach Deal-Typ"""
        deal = getattr(self, '_deal', '%')
        
        # Berechne beide Werte unabhängig vom Deal-Typ
        total_umsatz = self._headcard_umsatz + self._headcard_trinkgeld
        bargeld = self._headcard_bargeld
        kreditkarte = total_umsatz - bargeld
        
        # Setze beide Werte für die Summenzeile
        self._headcard_cash = bargeld
        self._headcard_credit_card = kreditkarte
        
        # Für die alte HeadCard-Logik (falls noch verwendet)
        if deal == 'P':
            self._headcard_deal_value = kreditkarte
            self._headcard_deal_icon = 'assets/icons/credit_card_gray.svg'
            self._headcard_deal_label = 'Bankomat'
        else:
            self._headcard_deal_value = bargeld
            self._headcard_deal_icon = 'assets/icons/cash_gray.svg'
            self._headcard_deal_label = 'Bargeld'
            
        # Signals emittieren
        self.headcardDealValueChanged.emit()
        self.headcardDealIconChanged.emit()
        self.headcardDealLabelChanged.emit()
        self.headcardCashChanged.emit()
        self.headcardCreditCardChanged.emit()

    @Slot(float)
    def speichereUmsatzCustom(self, custom_income, config_json=None):
        try:
            # Deal-Typ sofort setzen und Signal emittieren
            self._deal = "C"
            self.dealChanged.emit()
            print(f"Deal-Typ auf 'C' gesetzt: {self._deal}")
            
            # Cache für Custom-Deal anlegen/aktualisieren
            if not hasattr(self, '_custom_deal_cache'):
                self._custom_deal_cache = {}
            self._custom_deal_cache['custom_income'] = custom_income
            # Slider-Konfiguration als JSON-String speichern
            import json
            if config_json is not None:
                print("PYTHON: empfangenes config_json:", config_json)
                config = json.loads(config_json)
                print("PYTHON: geparster config:", config)
                self._custom_deal_cache['config'] = config
            else:
                print("PYTHON: config_json ist None!")
                # Fallback: leeres Array
                self._custom_deal_cache['config'] = []
            
            # HeadCard für Custom-Deal aktualisieren
            self.update_headcard_for_deal()
            
            # Ergebnis sofort neu berechnen
            self.update_ergebnis()
            
            print(f"Custom-Deal Cache aktualisiert: {self._custom_deal_cache}")
            # Die eigentliche Speicherung in die Datenbank erfolgt erst beim finalen Speichern (z.B. in speichereUmsatz)
        except Exception as e:
            print(f"Fehler beim Zwischenspeichern des Custom-Income: {e}")

    @Slot(int, str, int, float, int, float, int, float, int, float, float, float)
    def speichereOverlayKonfiguration(self, driver_id, fahrer, taxi_deal, taxi_slider, uber_deal, uber_slider, bolt_deal, bolt_slider, einsteiger_deal, einsteiger_slider, garage_slider, tank_slider):
        import sqlite3
        db_path = os.path.join("SQL", "database.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_deal_config (
                id INTEGER PRIMARY KEY,
                fahrer TEXT NOT NULL,
                taxi_deal INTEGER,
                taxi_slider REAL,
                uber_deal INTEGER,
                uber_slider REAL,
                bolt_deal INTEGER,
                bolt_slider REAL,
                einsteiger_deal INTEGER,
                einsteiger_slider REAL,
                garage_slider REAL,
                tank_slider REAL,
                FOREIGN KEY (id) REFERENCES drivers(driver_id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO custom_deal_config
            (id, fahrer, taxi_deal, taxi_slider, uber_deal, uber_slider, bolt_deal, bolt_slider, einsteiger_deal, einsteiger_slider, garage_slider, tank_slider)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (driver_id, fahrer, taxi_deal, taxi_slider, uber_deal, uber_slider, bolt_deal, bolt_slider, einsteiger_deal, einsteiger_slider, garage_slider, tank_slider))
        conn.commit()
        conn.close()
        
        # Faktoren im Backend aktualisieren
        self._taxi_deal = taxi_deal
        self._taxi_slider = taxi_slider
        self._uber_deal = uber_deal
        self._uber_slider = uber_slider
        self._bolt_deal = bolt_deal
        self._bolt_slider = bolt_slider
        self._einsteiger_deal = einsteiger_deal
        self._einsteiger_slider = einsteiger_slider
        self._garage_slider = garage_slider
        self._tank_slider = tank_slider
        
        # Faktoren berechnen (Slider / 100)
        self._taxi_faktor = taxi_slider / 100.0
        self._uber_faktor = uber_slider / 100.0
        self._bolt_faktor = bolt_slider / 100.0
        self._einsteiger_faktor = einsteiger_slider / 100.0
        self._tank_faktor = tank_slider / 100.0
        self._garage_faktor = garage_slider / 100.0
        
        print(f"DEBUG: Overlay-Konfiguration gespeichert und Backend aktualisiert:")
        print(f"  Taxi: Deal={taxi_deal}, Slider={taxi_slider}, Faktor={self._taxi_faktor}")
        print(f"  Uber: Deal={uber_deal}, Slider={uber_slider}, Faktor={self._uber_faktor}")
        print(f"  Bolt: Deal={bolt_deal}, Slider={bolt_slider}, Faktor={self._bolt_faktor}")
        print(f"  Einsteiger: Deal={einsteiger_deal}, Slider={einsteiger_slider}, Faktor={self._einsteiger_faktor}")
        print(f"  Tank: Slider={tank_slider}, Faktor={self._tank_faktor}")
        print(f"  Garage: Slider={garage_slider}, Faktor={self._garage_faktor}")
        
        # WICHTIG: Signal emittieren, damit QML über die Änderungen informiert wird
        self.ergebnisChanged.emit()
        print(f"DEBUG: ergebnisChanged Signal emittiert")
        
        # Ergebnis neu berechnen
        self.update_ergebnis()

    @Slot(int, result='QVariantList')
    def ladeOverlayKonfiguration(self, driver_id):
        import sqlite3
        db_path = os.path.join("SQL", "database.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Erstelle die Tabelle falls sie nicht existiert
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_deal_config (
                id INTEGER PRIMARY KEY,
                fahrer TEXT NOT NULL,
                taxi_deal INTEGER,
                taxi_slider REAL,
                uber_deal INTEGER,
                uber_slider REAL,
                bolt_deal INTEGER,
                bolt_slider REAL,
                einsteiger_deal INTEGER,
                einsteiger_slider REAL,
                garage_slider REAL,
                tank_slider REAL,
                FOREIGN KEY (id) REFERENCES drivers(driver_id) ON DELETE CASCADE
            )
        """)
        
        try:
            cursor.execute("""
                SELECT taxi_deal, taxi_slider, uber_deal, uber_slider, bolt_deal, bolt_slider, einsteiger_deal, einsteiger_slider, garage_slider, tank_slider
                FROM custom_deal_config WHERE id = ?
            """, (driver_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Backend-Variablen setzen
                self._taxi_deal = row[0] if row[0] is not None else 0
                self._taxi_slider = row[1] if row[1] is not None else 0.0
                self._uber_deal = row[2] if row[2] is not None else 0
                self._uber_slider = row[3] if row[3] is not None else 0.0
                self._bolt_deal = row[4] if row[4] is not None else 0
                self._bolt_slider = row[5] if row[5] is not None else 0.0
                self._einsteiger_deal = row[6] if row[6] is not None else 0
                self._einsteiger_slider = row[7] if row[7] is not None else 0.0
                self._garage_slider = row[8] if row[8] is not None else 0.0
                self._tank_slider = row[9] if row[9] is not None else 0.0
                
                # Faktoren berechnen
                self._taxi_faktor = self._taxi_slider / 100.0
                self._uber_faktor = self._uber_slider / 100.0
                self._bolt_faktor = self._bolt_slider / 100.0
                self._einsteiger_faktor = self._einsteiger_slider / 100.0
                self._tank_faktor = self._tank_slider / 100.0
                self._garage_faktor = self._garage_slider / 100.0
                
                print(f"DEBUG: Overlay-Konfiguration geladen:")
                print(f"  Taxi: Deal={self._taxi_deal}, Slider={self._taxi_slider}, Faktor={self._taxi_faktor}")
                print(f"  Uber: Deal={self._uber_deal}, Slider={self._uber_slider}, Faktor={self._uber_faktor}")
                print(f"  Bolt: Deal={self._bolt_deal}, Slider={self._bolt_slider}, Faktor={self._bolt_faktor}")
                print(f"  Einsteiger: Deal={self._einsteiger_deal}, Slider={self._einsteiger_slider}, Faktor={self._einsteiger_faktor}")
                print(f"  Tank: Slider={self._tank_slider}, Faktor={self._tank_faktor}")
                print(f"  Garage: Slider={self._garage_slider}, Faktor={self._garage_faktor}")
                
                # WICHTIG: Signal emittieren, damit QML über die Änderungen informiert wird
                self.ergebnisChanged.emit()
                print(f"DEBUG: ergebnisChanged Signal emittiert")
            
            return row if row else []
        except Exception as e:
            print(f"Fehler beim Laden der Overlay-Konfiguration: {e}")
            conn.close()
            return []

    def _speichere_custom_deal(self):
        try:
            self._duplicate_replaced = False
            import sqlite3
            db_path = os.path.join("SQL", "report.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            kw = self._wizard_data.get("kw", None)
            fahrzeug_raw = self._wizard_data.get("fahrzeug", None)
            fahrzeug = None
            if fahrzeug_raw:
                if " " in fahrzeug_raw:
                    fahrzeug = fahrzeug_raw.split(" ")[0]
                elif "(" in fahrzeug_raw:
                    fahrzeug = fahrzeug_raw.split("(")[0].strip()
                else:
                    fahrzeug = fahrzeug_raw
            deal = getattr(self, '_deal', '%')
            fahrer = self._wizard_data.get("fahrer", None)
            total = self._headcard_umsatz + self._input_einsteiger
            try:
                jahr = datetime.now().year
                kw_int = int(kw) if kw else None
                if kw_int is not None:
                    erster_tag_kw = datetime.strptime(f'{jahr}-W{kw_int}-1', "%Y-W%W-%w")
                    monat = erster_tag_kw.month
                    cal = calendar.Calendar(firstweekday=0)
                    montage = [d for d in cal.itermonthdates(jahr, monat) if d.weekday() == 0 and d.month == monat]
                    anzahl_montage = len(montage)
                else:
                    anzahl_montage = 4
            except Exception:
                anzahl_montage = 4
            income = self._custom_deal_cache.get('custom_income', 0.0)
            db_path = os.path.join("SQL", "revenue.db")
            table_vehicle = fahrzeug
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS '{table_vehicle}' (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cw INTEGER NOT NULL CHECK (cw BETWEEN 1 AND 52),
                    deal TEXT,
                    driver TEXT,
                    total DECIMAL(10,2),
                    income DECIMAL(10,2) NOT NULL,
                    timestamp DATETIME
                )
            """)
            cursor.execute(f"""
                SELECT * FROM '{table_vehicle}' 
                WHERE cw = ? AND driver = ? AND deal = ?
            """, (int(kw) if kw else None, fahrer, deal))
            existing_entry = cursor.fetchone()
            if existing_entry:
                new_entry = {
                    'cw': int(kw) if kw else None,
                    'deal': deal,
                    'driver': fahrer,
                    'total': total,
                    'income': income,
                    'timestamp': timestamp
                }
                result = self.show_duplicate_comparison_dialog(existing_entry, new_entry, table_vehicle, kw, fahrer, deal)
                if result == QDialog.Accepted:
                    print("Duplikat wurde verarbeitet")
                else:
                    print("Speichern abgebrochen")
                    conn.close()
                    return
            else:
                cursor.execute(f"""
                    INSERT INTO '{table_vehicle}' (cw, deal, driver, total, income, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (int(kw) if kw else None, deal, fahrer, total, income, timestamp))
            conn.commit()
            conn.close()
            if not existing_entry or (existing_entry and hasattr(self, '_duplicate_replaced') and self._duplicate_replaced):
                db_path_exp = os.path.join("SQL", "running_costs.db")
                conn_exp = sqlite3.connect(db_path_exp)
                cursor_exp = conn_exp.cursor()
                cursor_exp.execute(f"""
                    CREATE TABLE IF NOT EXISTS '{table_vehicle}' (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cw INTEGER,
                        amount DECIMAL(10,2),
                        category TEXT,
                        details TEXT,
                        timestamp DATETIME
                    )
                """)
                for eintrag in getattr(self, '_expense_cache', []):
                    try:
                        exp_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor_exp.execute(f"""
                            INSERT INTO '{table_vehicle}' (cw, amount, category, details, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            int(kw) if kw else None,
                            float(eintrag.get("amount", 0)),
                            eintrag.get("category", ""),
                            eintrag.get("details", ""),
                            exp_timestamp
                        ))
                    except Exception as e:
                        print(f"Fehler beim Speichern eines Expense-Eintrags: {e}")
                # Garage als eigene Expense speichern
                if hasattr(self, '_garage') and self._garage and anzahl_montage > 0:
                    try:
                        exp_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        garage_betrag = self._garage / anzahl_montage
                        cursor_exp.execute(f"""
                            INSERT INTO '{table_vehicle}' (cw, amount, category, details, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            int(kw) if kw else None,
                            garage_betrag,
                            "Parking",
                            "50%",
                            exp_timestamp
                        ))
                    except Exception as e:
                        print(f"Fehler beim Speichern der Garage als Expense: {e}")
                if hasattr(self, '_input_gas') and self._input_gas:
                    try:
                        exp_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor_exp.execute(f"""
                            INSERT INTO '{table_vehicle}' (cw, amount, category, details, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            int(kw) if kw else None,
                            float(self._input_gas),
                            "Gas",
                            "",
                            exp_timestamp
                        ))
                    except Exception as e:
                        print(f"Fehler beim Speichern des Gas-Eintrags: {e}")
                conn_exp.commit()
                conn_exp.close()
            self._expense_cache = []
            self.inputGas = ""
            self.inputEinsteiger = ""
            self.inputExpense = ""
        except Exception as e:
            pass

    def get_overlay_config(self, driver_id):
        if getattr(self, '_deal', None) == 'C':
            if not self._overlay_config_cache:
                print('[OverlayConfig] Lade Konfiguration aus Datenbank (custom_deal_config) ...')
                config = self.ladeOverlayKonfiguration(driver_id)
                self._overlay_config_cache = config if config else []
            else:
                print('[OverlayConfig] Verwende Session-Cache für Overlay-Konfiguration.')
            return self._overlay_config_cache
        else:
            print(f'[OverlayConfig] Verwende Standard-Konfiguration für Deal {getattr(self, "_deal", None)}.')
            return self.get_standard_config_for_deal(getattr(self, '_deal', None))

    def update_overlay_config_cache(self, new_config):
        print('[OverlayConfig] Aktualisiere Session-Cache für Overlay-Konfiguration.')
        self._overlay_config_cache = new_config

    def save_overlay_config_to_db(self, driver_id):
        if self._deal == 'C' and self._overlay_config_cache:
            print('[OverlayConfig] Speichere Overlay-Konfiguration aus Cache in Datenbank ...')
            # Extrahiere Werte wie in saveOverlayConfigToDatabase in QML
            # Annahme: new_config ist ein Array von Dicts mit platform, slider, ggf. deal
            # Extrahiere die Werte für speichereOverlayKonfiguration
            def get_slider(platform):
                for item in self._overlay_config_cache:
                    if item.get('platform') == platform:
                        return item.get('slider', 0)
                return 0
            def get_deal(platform):
                for item in self._overlay_config_cache:
                    if item.get('platform') == platform:
                        return item.get('deal', 0)
                return 0
            # Hole Fahrer-Name
            fahrer = getattr(self, '_fahrer_label', '')
            # Hole alle Werte
            taxi_deal = get_deal('Taxi')
            taxi_slider = get_slider('Taxi')
            uber_deal = get_deal('Uber')
            uber_slider = get_slider('Uber')
            bolt_deal = get_deal('Bolt')
            bolt_slider = get_slider('Bolt')
            einsteiger_deal = get_deal('Einsteiger')
            einsteiger_slider = get_slider('Einsteiger')
            garage_slider = get_slider('Garage')
            tank_slider = get_slider('Tank')
            # Speichere in DB
            self.speichereOverlayKonfiguration(driver_id, fahrer, taxi_deal, taxi_slider, uber_deal, uber_slider, bolt_deal, bolt_slider, einsteiger_deal, einsteiger_slider, garage_slider, tank_slider)
            print('[OverlayConfig] Overlay-Konfiguration erfolgreich gespeichert!')
            self._overlay_config_cache = []
        else:
            print('[OverlayConfig] Kein Custom-Deal oder leerer Cache, nichts gespeichert.')

    def get_standard_config_for_deal(self, deal):
        # Dummy-Implementierung: Liefere Standardwerte für P- oder %-Deal
        # Hier kannst du die gewünschte Logik für Standard-Deals einbauen
        # Beispiel: leere Liste oder vordefinierte Defaults
        return []

    @Slot(float)
    def setOverlayIncomeOhneEinsteiger(self, value):
        self._overlay_income_ohne_einsteiger = value
        self.update_ergebnis()
        
    @Slot(float)
    def setEinsteigerFaktor(self, value):
        self._einsteiger_faktor = value
        self.ergebnisChanged.emit()  # Signal für QML-Properties
        self.update_ergebnis()
        
    @Slot(float)
    def setTankFaktor(self, value):
        self._tank_faktor = value
        self.ergebnisChanged.emit()  # Signal für QML-Properties
        self.update_ergebnis()

    @Slot(float)
    def setTaxiFaktor(self, value):
        self._taxi_faktor = value
        self.ergebnisChanged.emit()  # Signal für QML-Properties
        self.update_ergebnis()
        
    @Slot(float)
    def setUberFaktor(self, value):
        self._uber_faktor = value
        self.ergebnisChanged.emit()  # Signal für QML-Properties
        self.update_ergebnis()
        
    @Slot(float)
    def setBoltFaktor(self, value):
        self._bolt_faktor = value
        self.ergebnisChanged.emit()  # Signal für QML-Properties
        self.update_ergebnis()

    @Slot(str)
    def setDeal(self, value):
        self._deal = value
        self.dealChanged.emit()

    @Slot(float)
    def setGarageFaktor(self, value):
        self._garage_faktor = value
        self.ergebnisChanged.emit()  # Signal für QML-Properties
        self.update_ergebnis()
        
    @Slot(float)
    def setPauschale(self, value):
        self._pauschale = value
        self.pauschaleChanged.emit()
        self.update_ergebnis()
        
    @Slot(float)
    def setUmsatzgrenze(self, value):
        self._umsatzgrenze = value
        self.umsatzgrenzeChanged.emit()
        self.update_ergebnis()



    def _lade_deal_aus_datenbank(self, fahrername):
        """Lädt den Deal-Typ und die entsprechenden Faktoren aus der Datenbank"""
        
        deal = None
        garage = 0.0
        pauschale = 500.0
        umsatzgrenze = 1200.0
        
        try:
            conn = sqlite3.connect("SQL/database.db")
            cursor = conn.cursor()
            
            # Lade Deal-Daten aus deals Tabelle
            cursor.execute("SELECT deal, garage, pauschale, umsatzgrenze FROM deals WHERE name = ?", (fahrername,))
            row = cursor.fetchone()
            
            if row:
                deal = row[0]
                garage = row[1] if row[1] is not None else 0.0
                pauschale = row[2] if row[2] is not None else 500.0
                umsatzgrenze = row[3] if row[3] is not None else 1200.0
                # Deal-Daten geladen
            else:
                # Kein Deal-Eintrag gefunden, verwende Standard-Deal 'P'
                deal = "P"
                
        except Exception as e:
            # Fehler beim Laden der Deal-Daten
            deal = "P"
        finally:
            try:
                conn.close()
            except:
                pass
        
        # Setze Backend-Variablen
        self._garage = garage
        self._pauschale = pauschale
        self._umsatzgrenze = umsatzgrenze
        self._deal = deal
        
        # Deal-spezifische Faktoren setzen
        
        if deal == "P":
            self._taxi_faktor = 0.0
            self._uber_faktor = 0.0
            self._bolt_faktor = 0.0
            self._einsteiger_faktor = 0.0
            self._tank_faktor = 0.0
            self._garage_faktor = 0.5
            
            # Overlay-Config für P-Deal setzen
            self._overlay_config_cache = [
                {"platform": "Taxi", "deal": "P", "slider": 0.0},
                {"platform": "Uber", "deal": "P", "slider": 0.0},
                {"platform": "Bolt", "deal": "P", "slider": 0.0},
                {"platform": "Einsteiger", "deal": "P", "slider": 0.0},
                {"platform": "Tank", "deal": "C", "slider": 0.0},
                {"platform": "Garage", "deal": "C", "slider": 50.0}
            ]
            self._overlay_income_ohne_einsteiger = 0.0
            
        elif deal == "%":
            self._taxi_faktor = 0.5
            self._uber_faktor = 0.5
            self._bolt_faktor = 0.5
            self._einsteiger_faktor = 0.5
            self._tank_faktor = 0.5
            self._garage_faktor = 0.5
            
            # Overlay-Config für %-Deal setzen
            self._overlay_config_cache = [
                {"platform": "Taxi", "deal": "%", "slider": 50.0},
                {"platform": "Uber", "deal": "%", "slider": 50.0},
                {"platform": "Bolt", "deal": "%", "slider": 50.0},
                {"platform": "Einsteiger", "deal": "%", "slider": 50.0},
                {"platform": "Tank", "deal": "C", "slider": 50.0},
                {"platform": "Garage", "deal": "C", "slider": 50.0}
            ]
            self._overlay_income_ohne_einsteiger = 0.0
            
        elif deal == "C":
            # NEU: Verwende die neue ladeCustomDealConfig Funktion
            config = self.ladeCustomDealConfig(fahrername)
            if config and len(config) > 0:
                # Config ist jetzt ein Array von Objekten mit platform, deal, slider
                self._overlay_config_cache = config
                
                # Faktoren aus der Config berechnen
                for item in config:
                    platform = item.get("platform", "")
                    slider = item.get("slider", 0.0)
                    deal_type = item.get("deal", "")
                    
                    # Faktor berechnen (Slider / 100)
                    faktor = slider / 100.0
                    
                    # Faktor der entsprechenden Plattform zuweisen
                    if platform == "Taxi":
                        self._taxi_faktor = faktor
                        self._taxi_deal = deal_type
                    elif platform == "Uber":
                        self._uber_faktor = faktor
                        self._uber_deal = deal_type
                    elif platform == "Bolt":
                        self._bolt_faktor = faktor
                        self._bolt_deal = deal_type
                    elif platform == "Einsteiger":
                        self._einsteiger_faktor = faktor
                        self._einsteiger_deal = deal_type
                    elif platform == "Tank":
                        self._tank_faktor = faktor
                    elif platform == "Garage":
                        self._garage_faktor = faktor
                
                print(f"[CustomDealConfig] Faktoren für {fahrername} geladen:")
                print(f"  Taxi: {self._taxi_faktor} ({self._taxi_deal})")
                print(f"  Uber: {self._uber_faktor} ({self._uber_deal})")
                print(f"  Bolt: {self._bolt_faktor} ({self._bolt_deal})")
                print(f"  Einsteiger: {self._einsteiger_faktor} ({self._einsteiger_deal})")
                print(f"  Tank: {self._tank_faktor}")
                print(f"  Garage: {self._garage_faktor}")
                
            else:
                # Keine Custom-Config gefunden, verwende Standard-Faktoren
                self._taxi_faktor = self._uber_faktor = self._bolt_faktor = 1.0
                self._einsteiger_faktor = self._tank_faktor = self._garage_faktor = 1.0
                print(f"[CustomDealConfig] Keine Konfiguration für {fahrername} gefunden, verwende Standard-Faktoren")
        else:
            # Unbekannter Deal-Typ, verwende Standard-Faktoren
            self._taxi_faktor = self._uber_faktor = self._bolt_faktor = 1.0
            self._einsteiger_faktor = self._tank_faktor = self._garage_faktor = 1.0
        
        # Deal-Konfiguration geladen
        
        # WICHTIG: Alle relevanten Signals emittieren für QML-Properties
        self.ergebnisChanged.emit()
        self.dealChanged.emit()
        print(f"DEBUG: Alle Signals für Deal-Konfiguration emittiert")

    # --- NEU: Overlay-Konfiguration über Fahrernamen laden ---
    def ladeOverlayKonfigurationByName(self, fahrername):
        """
        Lädt die custom_deal_config für einen Fahrer anhand des Namens.
        """
        import sqlite3
        import os
        import json
        
        db_path = os.path.join("SQL", "database.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe, ob custom_deal_config Tabelle existiert
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_deal_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fahrer TEXT UNIQUE,
                config_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Lade Konfiguration für den Fahrer
        cursor.execute("SELECT config_json FROM custom_deal_config WHERE fahrer = ?", (fahrername,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result and result[0]:
            try:
                config = json.loads(result[0])
                print(f"[CustomDealConfig] Konfiguration für {fahrername} geladen: {config}")
                return config
            except json.JSONDecodeError:
                print(f"[CustomDealConfig] Fehler beim Parsen der JSON-Konfiguration für {fahrername}")
                return []
        else:
            print(f"[CustomDealConfig] Keine Konfiguration für {fahrername} gefunden")
            return []

    @Slot(str, result='QVariantList')
    def ladeCustomDealConfig(self, fahrername):
        """
        Lädt die custom_deal_config für einen Fahrer und gibt sie als QVariantList zurück.
        """
        config = self.ladeOverlayKonfigurationByName(fahrername)
        return config

    def _berechne_platform_werte(self, df, platform):
        """Zentrale Berechnung für Plattformen wie Uber, Bolt, 40100"""
        if df.empty:
            if platform == "Bolt":
                return {
                    "net_earnings": 0.0,
                    "rider_tips": 0.0,
                    "cash_collected": 0.0,
                    "echter_umsatz": 0.0,
                    "anteil": 0.0,
                    "restbetrag": 0.0
                }
            elif platform == "40100":
                return {
                    "gesamt_umsatz": 0.0,
                    "trinkgeld": 0.0,
                    "bargeld": 0.0,
                    "echter_umsatz": 0.0,
                    "anteil": 0.0,
                    "restbetrag": 0.0
                }
            else:
                return {
                    "gross_total": 0.0,
                    "cash_collected": 0.0,
                    "anteil": 0.0,
                    "restbetrag": 0.0
                }
        row_data = df.iloc[0]
        if platform == "Uber":
            gross_total = safe_float(row_data.get("gross_total", 0))
            cash_collected = safe_float(row_data.get("cash_collected", 0))
            anteil = gross_total / 2
            restbetrag = anteil - cash_collected
            return {
                "gross_total": gross_total,
                "cash_collected": cash_collected,
                "anteil": anteil,
                "restbetrag": restbetrag
            }
        elif platform == "Bolt":
            net_earnings = safe_float(row_data.get("net_earnings", 0))
            rider_tips = safe_float(row_data.get("rider_tips", 0))
            cash_collected = safe_float(row_data.get("cash_collected", 0))
            echter_umsatz = net_earnings - rider_tips
            anteil = echter_umsatz / 2
            restbetrag = anteil - cash_collected
            return {
                "net_earnings": net_earnings,
                "rider_tips": rider_tips,
                "cash_collected": cash_collected,
                "echter_umsatz": echter_umsatz,
                "anteil": anteil,
                "restbetrag": restbetrag
            }
        elif platform == "40100":
            if "Umsatz" in df.columns:
                df["Umsatz"] = pd.to_numeric(df["Umsatz"].astype(str).str.replace(",", "."), errors="coerce")
                umsatz_mask = (df["Umsatz"] <= 250) & (df["Umsatz"] >= -250)
                umsatz_40100 = df.loc[umsatz_mask, "Umsatz"]
            else:
                umsatz_40100 = pd.Series(dtype=float)
            gesamt_umsatz = umsatz_40100.sum()
            # Trinkgeld für echten Umsatz: Gesamtsumme (ohne Filter)
            trinkgeld_fuer_umsatz = df["Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
            
            # Trinkgeld für Anzeige: Summe nur wenn Buchungsart nicht 'Bar' enthält und Umsatz zwischen -250 und 250
            trinkgeld_mask = umsatz_mask
            if "Buchungsart" in df.columns:
                trinkgeld_mask = trinkgeld_mask & ~df["Buchungsart"].str.contains("Bar", na=False)
            trinkgeld = df.loc[trinkgeld_mask, "Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
            bargeld = df.loc[umsatz_mask, "Bargeld"].sum() if "Bargeld" in df.columns else 0
            echter_umsatz = gesamt_umsatz - trinkgeld_fuer_umsatz
            anteil = echter_umsatz / 2
            restbetrag = anteil - bargeld + trinkgeld
            return {
                "echter_umsatz": echter_umsatz,  # Erste Position für Card-Anzeige
                "gesamt_umsatz": gesamt_umsatz,
                "trinkgeld": trinkgeld,
                "bargeld": bargeld,
                "anteil": anteil,
                "restbetrag": restbetrag
            }
        return {}

    def calculate_bolt_details(self, df):
        werte = self._berechne_platform_werte(df, "Bolt")
        return [
            {"label": "Echter Umsatz", "value": f"{werte['echter_umsatz']:.2f} €"},
            {"label": "Anteil", "value": f"{werte['anteil']:.2f} €"},
            {"label": "Bargeld", "value": f"{werte['cash_collected']:.2f} €"},
            {"label": "Rest", "value": f"{werte['restbetrag']:.2f} €"}
        ]

    def calculate_bolt_results(self, df):
        werte = self._berechne_platform_werte(df, "Bolt")
        return [
            {"type": "title", "text": "Bolt"},
            {"type": "value", "label": "Total", "value": f"{werte['net_earnings']:.2f} €", "hint": ""},
            {"type": "value", "label": "Echter Umsatz", "value": f"{werte['echter_umsatz']:.2f} €", "hint": "/ 2"},
            {"type": "value", "label": "Anteil", "value": f"{werte['anteil']:.2f} €", "hint": "- Bargeld"},
            {"type": "value", "label": "Rest", "value": f"{werte['restbetrag']:.2f} €", "hint": ""}
        ]

    def calculate_40100_details(self, df, deal):
        werte = self._berechne_platform_werte(df, "40100")
        return [
            {"label": "Real", "value": f"{werte['echter_umsatz']:.2f} €"},
            {"label": "Anteil", "value": f"{werte['anteil']:.2f} €"},
            {"label": "Bargeld", "value": f"{werte['bargeld']:.2f} €"},
            {"label": "Rest", "value": f"{werte['restbetrag']:.2f} €"}
        ]

    def calculate_40100_results(self, df, deal):
        werte = self._berechne_platform_werte(df, "40100")
        return [
            {"type": "value", "label": "Total", "value": f"{werte['gesamt_umsatz']:.2f} €", "hint": "- Trinkgeld"},
            {"type": "value", "label": "Real", "value": f"{werte['echter_umsatz']:.2f} €", "hint": "/ 2"},
            {"type": "value", "label": "Anteil", "value": f"{werte['anteil']:.2f} €", "hint": "- Auszahlung"},
            {"type": "value", "label": "Rest", "value": f"{werte['restbetrag']:.2f} €", "hint": ""}
        ]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    abrechnung = AbrechnungsSeiteQML()
    engine.rootContext().setContextProperty("abrechnungBackend", abrechnung)
    engine.load('Style/Abrechnungsseite.qml')
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec()) 