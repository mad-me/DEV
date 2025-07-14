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

class AbrechnungsWizard(QDialog):
    def __init__(self, fahrer_list, fahrzeug_list, kw_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Abrechnungs-Auswertung")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # Daten
        self.fahrer_list = fahrer_list
        self.fahrzeug_list = fahrzeug_list
        self.kw_list = kw_list
        self.result_data = {}
        
        # UI erstellen
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Titel
        title = QLabel("Abrechnungs-Auswertung")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffffff; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Fahrer Auswahl
        fahrer_layout = QHBoxLayout()
        fahrer_label = QLabel("Fahrer:")
        fahrer_label.setStyleSheet("color: #ffffff; font-size: 12pt;")
        fahrer_label.setFixedWidth(120)
        self.fahrer_combo = QComboBox()
        self.fahrer_combo.addItems(self.fahrer_list)
        self.fahrer_combo.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 12pt;
            }
            QComboBox:hover {
                border-color: #f79009;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
        """)
        fahrer_layout.addWidget(fahrer_label)
        fahrer_layout.addWidget(self.fahrer_combo)
        layout.addLayout(fahrer_layout)
        
        # Fahrzeug Auswahl
        fahrzeug_layout = QHBoxLayout()
        fahrzeug_label = QLabel("Fahrzeug:")
        fahrzeug_label.setStyleSheet("color: #ffffff; font-size: 12pt;")
        fahrzeug_label.setFixedWidth(120)
        self.fahrzeug_combo = QComboBox()
        self.fahrzeug_combo.addItems(self.fahrzeug_list)
        self.fahrzeug_combo.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 12pt;
            }
            QComboBox:hover {
                border-color: #f79009;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
        """)
        fahrzeug_layout.addWidget(fahrzeug_label)
        fahrzeug_layout.addWidget(self.fahrzeug_combo)
        layout.addLayout(fahrzeug_layout)
        
        # Kalenderwoche Auswahl
        kw_layout = QHBoxLayout()
        kw_label = QLabel("Kalenderwoche:")
        kw_label.setStyleSheet("color: #ffffff; font-size: 12pt;")
        kw_label.setFixedWidth(120)
        self.kw_combo = QComboBox()
        self.kw_combo.addItems(self.kw_list)
        self.kw_combo.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 12pt;
            }
            QComboBox:hover {
                border-color: #f79009;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
        """)
        kw_layout.addWidget(kw_label)
        kw_layout.addWidget(self.kw_combo)
        layout.addLayout(kw_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setStyleSheet("""
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
        self.cancel_button.clicked.connect(self.reject)
        
        self.ok_button = QPushButton("Auswerten")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #f79009;
                border-radius: 4px;
                padding: 10px 20px;
                color: #f79009;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(247, 144, 9, 0.1);
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
        
        # Dialog-Styling
        self.setStyleSheet("""
            QDialog {
                background: #000000;
            }
        """)
        
    def get_data(self):
        return {
            "fahrer": self.fahrer_combo.currentText(),
            "fahrzeug": self.fahrzeug_combo.currentText(),
            "kw": self.kw_combo.currentText()
        }

class AbrechnungsModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._data = []
        self._current_page = 0
        
    def rowCount(self, parent=None):
        return len(self._data)
        
    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()]
        return None
        
    def update_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()
        
    def set_current_page(self, page):
        self._current_page = page

class AbrechnungsSeiteQML(QObject):
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
        self._inputGas = 0.0
        self._inputGasText = ""
        self._inputEinsteiger = 0.0
        self._inputEinsteigerText = ""
        self._inputExpenseText = ""
        self._expense_cache = []  # Zwischenspeicher für neue Ausgaben
        # Daten laden
        self.load_fahrer()
        self.load_fahrzeuge()
        self.load_kalenderwochen()
        
    # Properties für QML
    def fahrer_list(self):
        return self._fahrer_list
        
    def fahrzeug_list(self):
        return self._fahrzeug_list
        
    def kw_list(self):
        return self._kw_list
        
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
        return getattr(self, '_headcard_deal_icon', 'assets/icons/receipt_gray.svg')
        
    @Property(str, notify=headcardDealLabelChanged)
    def headcard_deal_label(self):
        return getattr(self, '_headcard_deal_label', 'Umsatz')
        
    @Property(float, notify=ergebnisChanged)
    def ergebnis(self):
        return self._ergebnis
        
    @Property(str, notify=inputGasChanged)
    def inputGas(self):
        return self._inputGasText
    @inputGas.setter
    def inputGas(self, value):
        self._inputGasText = value
        try:
            self._inputGas = float(value.replace(",", ".")) if value else 0.0
        except Exception:
            self._inputGas = 0.0
        self.inputGasChanged.emit()
        self.update_ergebnis()

    @Property(str, notify=inputEinsteigerChanged)
    def inputEinsteiger(self):
        return self._inputEinsteigerText
    @inputEinsteiger.setter
    def inputEinsteiger(self, value):
        self._inputEinsteigerText = value
        try:
            self._inputEinsteiger = float(value.replace(",", ".")) if value else 0.0
        except Exception:
            self._inputEinsteiger = 0.0
        self.inputEinsteigerChanged.emit()
        self.update_ergebnis()

    @Property(str, notify=inputExpenseChanged)
    def inputExpense(self):
        return getattr(self, '_inputExpenseText', "")
    @inputExpense.setter
    def inputExpense(self, value):
        self._inputExpenseText = value
        self.inputExpenseChanged.emit()
        self.update_ergebnis()

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
            self._wizard_data = data
            self.wizardDataChanged.emit()
            print(f"Wizard-Daten: {data}")

            # --- Direkt nach dem Wizard den Deal-Typ und weitere Werte abfragen ---
            fahrer = data["fahrer"]
            try:
                conn = sqlite3.connect("SQL/database.db")
                cursor = conn.cursor()
                cursor.execute("SELECT deal, pauschale, umsatzgrenze, garage FROM deals WHERE name = ?", (fahrer,))
                row = cursor.fetchone()
                if row:
                    self._deal = row[0]
                    self._pauschale = float(row[1]) if row[1] is not None else 0.0
                    self._umsatzgrenze = float(row[2]) if row[2] is not None else 0.0
                    self._garage = float(row[3]) if row[3] is not None else 0.0
                else:
                    self._deal = "%"
                    self._pauschale = 0.0
                    self._umsatzgrenze = 0.0
                    self._garage = 0.0
            except Exception as e:
                self._deal = "%"
                self._pauschale = 0.0
                self._umsatzgrenze = 0.0
                self._garage = 0.0
            finally:
                try:
                    conn.close()
                except:
                    pass

            # Hier könntest du UI/Logik je nach self._deal anpassen
            self.auswerten(data["fahrer"], data["fahrzeug"], data["kw"])
            self.wizardFertig.emit()
        parent = None
        wizard = GenericWizard(fields, callback=wizard_callback, parent=parent, title="Abrechnungs-Auswertung")
        wizard.show()

    @Slot(str, str, str)
    def auswerten(self, fahrer, fahrzeug, kw):
        print(f"Auswertung für Fahrer: {fahrer}, Fahrzeug: {fahrzeug}, KW: {kw}")
        
        if not kw or not fahrer:
            return
            
        self._fahrer_label = fahrer
        self._found_pages = []
        
        # 1. Fahrer-Deal aus database.db holen
        deal = None
        try:
            conn_deal = sqlite3.connect("SQL/database.db")
            cursor_deal = conn_deal.cursor()
            cursor_deal.execute("SELECT deal FROM deals WHERE name = ?", (fahrer,))
            row = cursor_deal.fetchone()
            if row:
                deal = row[0]
        except Exception as e:
            deal = None
        finally:
            try:
                conn_deal.close()
            except:
                pass
                
        # 2. Fahrzeug in 40100.sqlite suchen
        kennzeichen_match = re.search(r"(\d+)", fahrzeug or "")
        kennzeichen_nummer = kennzeichen_match.group(1) if kennzeichen_match else None
        if kennzeichen_nummer:
            table_name = f"report_KW{kw}"
            db_path = os.path.abspath(os.path.join("SQL", "40100.sqlite"))
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE Fahrzeug LIKE ?", conn, params=[f"%{kennzeichen_nummer}%"])
                if not df.empty:
                    self._found_pages.append(("40100", df.copy(), deal))
            except Exception as e:
                pass
            finally:
                try:
                    conn.close()
                except:
                    pass
                    
        # 3. Fahrer in Uber und Bolt suchen (angepasstes Matching mit Bereinigung)
        def clean_name(name):
            # Entfernt doppelte Leerzeichen, trimmt und wandelt in Kleinbuchstaben um
            return re.sub(r"\s+", " ", str(name)).strip().lower()

        clean_fahrer_label = clean_name(fahrer)

        def debug_matching(df, label, db_name):
            print(f"\n--- Matching-Debug für {db_name} ---")
            print(f"Suchwert (ComboBox, bereinigt): '{label}'")
            if db_name == "Uber" and "_combo_name" in df.columns and "_match" in df.columns:
                for idx_row, row in df.iterrows():
                    print(f"Name in DB: '{row['_combo_name']}' | Match-Score: {row['_match']}")
            elif db_name == "Bolt" and "_driver_name_clean" in df.columns and "_match" in df.columns:
                for idx_row, row in df.iterrows():
                    print(f"Name in DB: '{row['_driver_name_clean']}' | Match-Score: {row['_match']}")

        for db_name, db_file in [("Uber", "uber.sqlite"), ("Bolt", "bolt.sqlite")]:
            db_path = os.path.abspath(os.path.join("SQL", db_file))
            table_name = f"report_KW{kw}"
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                if db_name == "Uber":
                    if "first_name" in df.columns and "last_name" in df.columns:
                        df["_combo_name"] = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).apply(clean_name)
                        def match_score(name):
                            such_tokens = clean_fahrer_label.split()
                            name_tokens = name.split()
                            return sum(1 for t in such_tokens if t in name_tokens)
                        df["_match"] = df["_combo_name"].apply(match_score)
                        debug_matching(df, clean_fahrer_label, db_name)
                        max_score = df["_match"].max() if not df.empty else 0
                        if max_score >= 2:
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
                        def match_score(name):
                            such_tokens = clean_fahrer_label.split()
                            name_tokens = name.split()
                            return sum(1 for t in such_tokens if t in name_tokens)
                        df["_match"] = df["_driver_name_clean"].apply(match_score)
                        debug_matching(df, clean_fahrer_label, db_name)
                        max_score = df["_match"].max() if not df.empty else 0
                        if max_score >= 2:
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
            
        # Übersichtsseite anzeigen
        self.show_overview_page()
        
    def auswerten_from_wizard(self):
        """Auswertung basierend auf Wizard-Daten"""
        data = self._wizard_data
        self.auswerten(data.get("fahrer", ""), data.get("fahrzeug", ""), data.get("kw", ""))
        
    @Slot()
    def show_overview_page(self):
        """Zeigt die Übersichtsseite mit allen Plattformen"""
        print("show_overview_page() aufgerufen")
        self._current_page = -1  # Übersichtsseite
        self.currentPageChanged.emit()
        # Summen für HeadCard
        uber_gross_total = 0.0
        bolt_echter_umsatz = 0.0
        bolt_rider_tips = 0.0
        bolt_cash_collected = 0.0
        _40100_real = 0.0
        _40100_trinkgeld = 0.0
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
        print(f"Gefundene Seiten: {len(self._found_pages)}")
        for db_name, df, deal in self._found_pages:
            print(f"Verarbeite {db_name} mit {len(df) if df is not None else 0} Zeilen")
            if db_name == "40100" and df is not None:
                sum_40100 += df["Umsatz"].sum() if "Umsatz" in df.columns else 0
                sum_bargeld += df["Bargeld"].sum() if "Bargeld" in df.columns else 0  # NEU
                _40100_trinkgeld += df["Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
                _40100_bargeld += df["Bargeld"].sum() if "Bargeld" in df.columns else 0
                _40100_real += (df["Umsatz"].sum() if "Umsatz" in df.columns else 0) - (df["Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0)
                details_40100 = self.calculate_40100_details(df, deal)
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
        total_summe = sum_40100 + sum_uber + sum_bolt
        # HeadCard Summen berechnen
        self._headcard_umsatz = uber_gross_total + bolt_echter_umsatz + _40100_real
        self._headcard_trinkgeld = bolt_rider_tips + _40100_trinkgeld
        self._headcard_bargeld = uber_cash_collected + bolt_cash_collected + _40100_bargeld
        self.headcardUmsatzChanged.emit()
        self.headcardTrinkgeldChanged.emit()
        self.headcardBargeldChanged.emit()
        
        # HeadCard je nach Deal-Typ aktualisieren
        self.update_headcard_for_deal()
        
        print(f"Summen: 40100={sum_40100}, Uber={sum_uber}, Bolt={sum_bolt}, Bargeld={sum_bargeld}, Total={total_summe}")
        print(f"HeadCard: Umsatz={self._headcard_umsatz}, Trinkgeld={self._headcard_trinkgeld}, Bargeld={self._headcard_bargeld}")
        # Übersicht mit detaillierten Ergebnissen
        self._ergebnisse = [
            {"type": "title", "text": "Übersicht"},
            {"type": "summary", "label": "40100", "value": f"{sum_40100:.2f} €", "details": details_40100},
            {"type": "summary", "label": "Uber", "value": f"{sum_uber:.2f} €", "details": details_uber},
            {"type": "summary", "label": "Bolt", "value": f"{sum_bolt:.2f} €", "details": details_bolt},
            {"type": "summary", "label": "Bargeld", "value": f"{sum_bargeld:.2f} €"},  # NEU: Bargeld in HeadCard
            {"type": "summary", "label": "Gesamt", "value": f"{total_summe:.2f} €"}
        ]
        print(f"Ergebnisse gesetzt: {len(self._ergebnisse)} Einträge")
        print(f"Ergebnisse: {self._ergebnisse}")
        self.ergebnisseChanged.emit()
        self.update_ergebnis()
        
    def calculate_40100_details(self, df, deal):
        """Berechnet detaillierte 40100-Ergebnisse für die Card"""
        def safe_float(val):
            if val is None or str(val).strip() == '' or str(val).lower() == 'nan' or (isinstance(val, float) and math.isnan(val)):
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        gesamt_umsatz = df["Umsatz"].sum() if "Umsatz" in df.columns else 0
        trinkgeld = df["Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
        bargeld = df["Bargeld"].sum() if "Bargeld" in df.columns else 0
        echter_umsatz = gesamt_umsatz - trinkgeld
        anteil = echter_umsatz / 2
        restbetrag = anteil - bargeld + trinkgeld
        return [
            {"label": "Real", "value": f"{echter_umsatz:.2f} €"},
            {"label": "Anteil", "value": f"{anteil:.2f} €"},
            {"label": "Bargeld", "value": f"{bargeld:.2f} €"},  # NEU
            {"label": "Rest", "value": f"{restbetrag:.2f} €"}
        ]
        
    def calculate_uber_details(self, df):
        """Berechnet detaillierte Uber-Ergebnisse für die Card"""
        def safe_float(val):
            if val is None or str(val).strip() == '' or str(val).lower() == 'nan' or (isinstance(val, float) and math.isnan(val)):
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        if df.empty:
            return [{"label": "Keine Daten", "value": "0.00 €"}]
        row_data = df.iloc[0]
        gross_total = safe_float(row_data.get("gross_total", 0))
        cash_collected = safe_float(row_data.get("cash_collected", 0))
        anteil = gross_total / 2
        restbetrag = anteil - cash_collected
        return [
            {"label": "Total", "value": f"{gross_total:.2f} €"},
            {"label": "Anteil", "value": f"{anteil:.2f} €"},
            {"label": "Bargeld", "value": f"{cash_collected:.2f} €"},  # NEU
            {"label": "Restbetrag", "value": f"{restbetrag:.2f} €"}
        ]
        
    def calculate_bolt_details(self, df):
        """Berechnet detaillierte Bolt-Ergebnisse für die Card"""
        def safe_float(val):
            if val is None or str(val).strip() == '' or str(val).lower() == 'nan' or (isinstance(val, float) and math.isnan(val)):
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        if df.empty:
            return [{"label": "Keine Daten", "value": "0.00 €"}]
        row_data = df.iloc[0]
        net_earnings = safe_float(row_data.get("net_earnings", 0))
        rider_tips = safe_float(row_data.get("rider_tips", 0))
        cash_collected = safe_float(row_data.get("cash_collected", 0))
        echter_umsatz = net_earnings - rider_tips
        anteil = echter_umsatz / 2
        restbetrag = anteil - cash_collected
        return [
            {"label": "Echter Umsatz", "value": f"{echter_umsatz:.2f} €"},
            {"label": "Anteil", "value": f"{anteil:.2f} €"},
            {"label": "Bargeld", "value": f"{cash_collected:.2f} €"},  # NEU
            {"label": "Rest", "value": f"{restbetrag:.2f} €"}
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
        
    def calculate_40100_results(self, df, deal):
        def safe_float(val):
            if val is None or str(val).strip() == '' or str(val).lower() == 'nan' or (isinstance(val, float) and math.isnan(val)):
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
                
        gesamt_umsatz = df["Umsatz"].sum() if "Umsatz" in df.columns else 0
        trinkgeld = df["Trinkgeld"].sum() if "Trinkgeld" in df.columns else 0
        bargeld = df["Bargeld"].sum() if "Bargeld" in df.columns else 0
        echter_umsatz = gesamt_umsatz - trinkgeld
        anteil = echter_umsatz / 2
        
        # Umsatzgrenze prüfen
        umsatzgrenze = None
        try:
            conn = sqlite3.connect("SQL/database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT umsatzgrenze FROM deals WHERE name = ?", (self._fahrer_label,))
            row_deal = cursor.fetchone()
            if row_deal and row_deal[0] is not None:
                umsatzgrenze = float(row_deal[0])
        except Exception as e:
            umsatzgrenze = None
        finally:
            try:
                conn.close()
            except:
                pass
                
        anteil_firma = 0
        if umsatzgrenze is not None and float(gesamt_umsatz) > float(umsatzgrenze):
            anteil_firma = (gesamt_umsatz - umsatzgrenze) * 0.1
            
        restbetrag = anteil - bargeld + trinkgeld
        
        ergebnisse = [
            {"type": "title", "text": "40100"}
        ]
        
        # Anteil Firma hinzufügen wenn vorhanden
        if anteil_firma > 0:
            ergebnisse.append({"type": "value", "label": "Anteil Firma", "value": f"{anteil_firma:.2f} €", "hint": ""})
            
        ergebnisse.extend([
            {"type": "value", "label": "Total", "value": f"{gesamt_umsatz:.2f} €", "hint": "- Trinkgeld"},
            {"type": "value", "label": "Real", "value": f"{echter_umsatz:.2f} €", "hint": "/ 2"},
            {"type": "value", "label": "Anteil", "value": f"{anteil:.2f} €", "hint": "- Auszahlung"},
            {"type": "value", "label": "Rest", "value": f"{restbetrag:.2f} €", "hint": ""}
        ])
        
        return ergebnisse
        
    def calculate_uber_results(self, df):
        def safe_float(val):
            if val is None or str(val).strip() == '' or str(val).lower() == 'nan' or (isinstance(val, float) and math.isnan(val)):
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
                
        if df.empty:
            return [{"type": "error", "message": "Keine Uber-Daten gefunden."}]
            
        row_data = df.iloc[0]
        gross_total = safe_float(row_data.get("gross_total", 0))
        cash_collected = safe_float(row_data.get("cash_collected", 0))
        anteil = gross_total / 2
        restbetrag = anteil - cash_collected
        
        return [
            {"type": "title", "text": "Uber"},
            {"type": "value", "label": "Total", "value": f"{gross_total:.2f} €", "hint": "/ 2"},
            {"type": "value", "label": "Anteil", "value": f"{anteil:.2f} €", "hint": "- Auszahlung"},
            {"type": "value", "label": "Restbetrag", "value": f"{restbetrag:.2f} €", "hint": ""}
        ]
        
    def calculate_bolt_results(self, df):
        def safe_float(val):
            if val is None or str(val).strip() == '' or str(val).lower() == 'nan' or (isinstance(val, float) and math.isnan(val)):
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
                
        if df.empty:
            return [{"type": "error", "message": "Keine Bolt-Daten gefunden."}]
            
        row_data = df.iloc[0]
        net_earnings = safe_float(row_data.get("net_earnings", 0))
        rider_tips = safe_float(row_data.get("rider_tips", 0))
        cash_collected = safe_float(row_data.get("cash_collected", 0))
        echter_umsatz = net_earnings - rider_tips
        anteil = echter_umsatz / 2
        restbetrag = anteil - cash_collected
        
        return [
            {"type": "title", "text": "Bolt"},
            {"type": "value", "label": "Total", "value": f"{net_earnings:.2f} €", "hint": ""},
            {"type": "value", "label": "Echter Umsatz", "value": f"{echter_umsatz:.2f} €", "hint": "/ 2"},
            {"type": "value", "label": "Anteil", "value": f"{anteil:.2f} €", "hint": "- Bargeld"},
            {"type": "value", "label": "Rest", "value": f"{restbetrag:.2f} €", "hint": ""}
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

    @Slot(result=list)
    def get_ergebnisse(self):
        """Gibt die aktuellen Ergebnisse zurück"""
        print(f"get_ergebnisse() aufgerufen, {len(self._ergebnisse)} Ergebnisse")
        return self._ergebnisse

    @Slot(result=dict)
    def get_current_selection(self):
        """Gibt die aktuelle Auswahl zurück"""
        return {
            "fahrer": self._fahrer_label,
            "fahrzeug": self._wizard_data.get("fahrzeug", ""),
            "kw": self._wizard_data.get("kw", "")
        }

    def set_root_window(self, root_window):
        self._root_window = root_window

    def berechne_ergebnis(self, umsatz, bargeld, trinkgeld, fahrer, kw, deal, pauschale=0.0, umsatzgrenze=0.0, garage=0.0):
        if deal == "%":
            # Bisherige Berechnung
            try:
                jahr = datetime.now().year
                kw_int = int(kw)
                erster_tag_kw = datetime.strptime(f'{jahr}-W{kw_int}-1', "%Y-W%W-%w")
                monat = erster_tag_kw.month
                cal = calendar.Calendar(firstweekday=0)
                montage = [d for d in cal.itermonthdates(jahr, monat) if d.weekday() == 0 and d.month == monat]
                anzahl_montage = len(montage)
            except Exception as e:
                anzahl_montage = 4  # Fallback
            zuschlag = (garage / anzahl_montage) / 2 if anzahl_montage > 0 else 0.0
            ergebnis = (umsatz / 2) - bargeld + trinkgeld + zuschlag
            ergebnis += self._inputGas / 2
            ergebnis -= self._inputEinsteiger / 2
            expense_sum = 0.0
            for e in getattr(self, '_expense_cache', []):
                try:
                    expense_sum += float(str(e.get("amount", "0")).replace(",", ".") or 0)
                except Exception:
                    pass
            ergebnis -= expense_sum
            return ergebnis
        elif deal == "P":
            # Neue Berechnung für P-Deal
            try:
                jahr = datetime.now().year
                kw_int = int(kw)
                erster_tag_kw = datetime.strptime(f'{jahr}-W{kw_int}-1', "%Y-W%W-%w")
                monat = erster_tag_kw.month
                cal = calendar.Calendar(firstweekday=0)
                montage = [d for d in cal.itermonthdates(jahr, monat) if d.weekday() == 0 and d.month == monat]
                anzahl_montage = len(montage)
            except Exception as e:
                anzahl_montage = 4  # Fallback
            bankomat = umsatz - bargeld
            grenzabzug = (umsatz - umsatzgrenze) * 0.1 if umsatz > umsatzgrenze else 0.0
            zuschlag = (garage / (2 * anzahl_montage)) if anzahl_montage > 0 else 0.0
            ergebnis = bankomat - pauschale - grenzabzug + zuschlag
            return ergebnis
        else:
            # Standardfall
            return 0.0

    def update_ergebnis(self):
        # Werte aus aktueller Auswertung holen
        umsatz = self._headcard_umsatz if hasattr(self, '_headcard_umsatz') else 0.0
        bargeld = self._headcard_bargeld if hasattr(self, '_headcard_bargeld') else 0.0
        trinkgeld = self._headcard_trinkgeld if hasattr(self, '_headcard_trinkgeld') else 0.0
        fahrer = self._fahrer_label if hasattr(self, '_fahrer_label') else ""
        kw = self._wizard_data.get("kw", "") if hasattr(self, '_wizard_data') else ""
        deal = getattr(self, '_deal', '%')
        pauschale = getattr(self, '_pauschale', 0.0)
        umsatzgrenze = getattr(self, '_umsatzgrenze', 0.0)
        garage = getattr(self, '_garage', 0.0)
        self._ergebnis = self.berechne_ergebnis(umsatz, bargeld, trinkgeld, fahrer, kw, deal, pauschale, umsatzgrenze, garage)
        self.ergebnisChanged.emit()

    @Slot()
    def speichereUmsatz(self):
        try:
            import sqlite3
            db_path = os.path.join("SQL", "report.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Hole aktuelle Werte
            kw = self._wizard_data.get("kw", None)
            fahrzeug_raw = self._wizard_data.get("fahrzeug", None)
            # Extrahiere nur das Kennzeichen (vor erstem Leerzeichen oder Klammer)
            fahrzeug = None
            if fahrzeug_raw:
                if " " in fahrzeug_raw:
                    fahrzeug = fahrzeug_raw.split(" ")[0]
                elif "(" in fahrzeug_raw:
                    fahrzeug = fahrzeug_raw.split("(")[0].strip()
                else:
                    fahrzeug = fahrzeug_raw
            deal = self._wizard_data.get("deal", None)
            fahrer = self._wizard_data.get("fahrer", None)
            # total = headcard_umsatz + Einsteiger
            total = self._headcard_umsatz + self._inputEinsteiger
            # Income-Berechnung je nach Deal
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
                anzahl_montage = 4  # Fallback
            if deal == "%":
                income = (total / 2) - (self._garage / (anzahl_montage * 2)) - (self._inputGas / 2)
            elif deal == "P":
                income = self._pauschale - (self._garage / (anzahl_montage * 2))
            else:
                income = self._ergebnis
            cursor.execute("""
                INSERT INTO revenue (cw, vehicle, deal, driver, total, income)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (int(kw) if kw else None, fahrzeug, deal, fahrer, total, income))
            # NEU: expenses speichern
            jahr = None
            if kw:
                try:
                    jahr = datetime.now().year
                except Exception:
                    jahr = None
            for eintrag in getattr(self, '_expense_cache', []):
                try:
                    cursor.execute("""
                        INSERT INTO expenses (vehicle, year, cw, amount, category, details)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        fahrzeug,
                        jahr,
                        int(kw) if kw else None,
                        float(eintrag.get("amount", 0)),
                        eintrag.get("category", ""),
                        eintrag.get("details", "")
                    ))
                except Exception as e:
                    print(f"Fehler beim Speichern eines Expense-Eintrags: {e}")
            # NEU: Gas als eigenen Expense speichern
            if hasattr(self, '_inputGas') and self._inputGas:
                try:
                    cursor.execute("""
                        INSERT INTO expenses (vehicle, year, cw, amount, category, details)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        fahrzeug,
                        jahr,
                        int(kw) if kw else None,
                        float(self._inputGas),
                        "Gas",
                        ""
                    ))
                except Exception as e:
                    print(f"Fehler beim Speichern des Gas-Eintrags: {e}")
            self._expense_cache = []  # Cache leeren
            self.inputGas = ""
            self.inputEinsteiger = ""
            self.inputExpense = ""
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Fehler beim Speichern in report.db: {e}")

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
        
        if deal == 'P':
            # Für P-Deal: Bankomatwert (Umsatz - Bargeld) anzeigen
            self._headcard_deal_value = self._headcard_umsatz - self._headcard_bargeld
            self._headcard_deal_icon = 'assets/icons/credit_card_gray.svg'
            self._headcard_deal_label = 'Bankomat'
        else:
            # Für %-Deal: Bargeld als dritter Wert anzeigen (Standard)
            self._headcard_deal_value = self._headcard_bargeld
            self._headcard_deal_icon = 'assets/icons/cash_gray.svg'
            self._headcard_deal_label = 'Bargeld'
            
        # Signals emittieren
        self.headcardDealValueChanged.emit()
        self.headcardDealIconChanged.emit()
        self.headcardDealLabelChanged.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    abrechnung = AbrechnungsSeiteQML()
    engine.rootContext().setContextProperty("abrechnungBackend", abrechnung)
    engine.load('Style/Abrechnungsseite.qml')
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec()) 