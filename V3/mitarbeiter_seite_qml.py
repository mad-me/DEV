from PySide6.QtCore import QObject, Slot, Signal, Property
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
import sys
import sqlite3
import pandas as pd
import os
from db_manager import DBManager

class MitarbeiterSeiteQML(QObject):
    # Signals für QML
    mitarbeiterListChanged = Signal()
    toggleViewChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._mitarbeiter_list = []
        self._toggle_view = False
        
    # Properties für QML
    @Property('QVariantList', notify=mitarbeiterListChanged)
    def mitarbeiterList(self):
        return self._mitarbeiter_list
        
    @Property(bool, notify=toggleViewChanged)
    def toggleView(self):
        return self._toggle_view
        
    def setToggleView(self, value):
        if self._toggle_view != value:
            self._toggle_view = value
            self.toggleViewChanged.emit()
            self.anzeigenMitarbeiter()
        
    @Slot()
    def toggleViewMode(self):
        self.setToggleView(not self._toggle_view)
        
    @Slot()
    def showMitarbeiterWizard(self):
        from generic_wizard import GenericWizard
        print("Mitarbeiter-Wizard wird geöffnet...")
        fields = [
            ("Führerscheinnummer", "driver_license_number", "text"),
            ("Vorname", "first_name", "text"),
            ("Nachname", "last_name", "text"),
            ("Telefon", "phone", "text"),
            ("E-Mail", "email", "text"),
            ("Einstellungsdatum", "hire_date", "text"),
            ("Status", "status", "combo", ["active", "inactive", "suspended"])
        ]
        def wizard_callback(data):
            db = DBManager()
            try:
                db.insert_mitarbeiter(data)
                print("Mitarbeiter erfolgreich in DB gespeichert.")
            except Exception as e:
                print(f"Fehler beim Speichern des Mitarbeiters: {e}")
            self.anzeigenMitarbeiter()
        wizard = GenericWizard(fields, callback=wizard_callback, title="Mitarbeiter anlegen")
        wizard.show()

    @Slot()
    def anzeigenMitarbeiter(self):
        db = DBManager()
        rows = db.get_all_mitarbeiter()
        self._mitarbeiter_list = []
        
        for row in rows:
            mitarbeiter = {
                "driver_id": row[0],
                "driver_license_number": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "phone": row[4],
                "email": row[5],
                "hire_date": row[6],
                "status": row[7]
            }
            
            # Wenn Toggle aktiv ist, lade Deals-Daten
            if self._toggle_view:
                try:
                    conn = sqlite3.connect("SQL/database.db")
                    cursor = conn.cursor()
                    fahrer_name = f"{row[2]} {row[3]}"
                    cursor.execute("SELECT deal, pauschale, umsatzgrenze, garage FROM deals WHERE name = ?", (fahrer_name,))
                    deal_row = cursor.fetchone()
                    if deal_row:
                        mitarbeiter["deal"] = deal_row[0] or "-"
                        mitarbeiter["pauschale"] = f"{deal_row[1]:.2f} €" if deal_row[1] is not None else "-"
                        mitarbeiter["umsatzgrenze"] = f"{deal_row[2]:.2f} €" if deal_row[2] is not None else "-"
                        mitarbeiter["garage"] = f"{deal_row[3]:.2f} €" if deal_row[3] is not None else "-"
                    else:
                        mitarbeiter["deal"] = "-"
                        mitarbeiter["pauschale"] = "-"
                        mitarbeiter["umsatzgrenze"] = "-"
                        mitarbeiter["garage"] = "-"
                    conn.close()
                except Exception as e:
                    print(f"Fehler beim Laden der Deals-Daten: {e}")
                    mitarbeiter["deal"] = "-"
                    mitarbeiter["pauschale"] = "-"
                    mitarbeiter["umsatzgrenze"] = "-"
                    mitarbeiter["garage"] = "-"
            
            self._mitarbeiter_list.append(mitarbeiter)
        self.mitarbeiterListChanged.emit()

    @Slot()
    def editMitarbeiterWizard(self):
        self.editMitarbeiterWizard_with_index(-1)

    @Slot(int)
    def editMitarbeiterWizard_with_index(self, vorwahl_index):
        from generic_wizard import GenericWizard
        db = DBManager()
        alle_mitarbeiter = db.get_all_mitarbeiter()
        name_liste = [f"{row[2]} {row[3]}" for row in alle_mitarbeiter]
        fields = [
            ("Mitarbeiter", "mitarbeiter_combo", "combo", name_liste),
            ("Führerscheinnummer", "driver_license_number", "text"),
            ("Vorname", "first_name", "text"),
            ("Nachname", "last_name", "text"),
            ("Telefon", "phone", "text"),
            ("E-Mail", "email", "text"),
            ("Einstellungsdatum", "hire_date", "text"),
            ("Status", "status", "combo", ["active", "inactive", "suspended"])
        ]
        def wizard_callback(data):
            try:
                index = name_liste.index(data["mitarbeiter_combo"])
                driver_id = alle_mitarbeiter[index][0]
                db.update_mitarbeiter_by_id(driver_id, data)
                print("Mitarbeiter erfolgreich aktualisiert.")
            except Exception as e:
                print(f"Fehler beim Aktualisieren des Mitarbeiters: {e}")
            self.anzeigenMitarbeiter()
        def on_combo_change(index):
            if index < 0 or index >= len(alle_mitarbeiter):
                return
            row = alle_mitarbeiter[index]
            if "driver_license_number" in wizard.inputs:
                wizard.inputs["driver_license_number"].setText(row[1] or "")
            if "first_name" in wizard.inputs:
                wizard.inputs["first_name"].setText(row[2] or "")
            if "last_name" in wizard.inputs:
                wizard.inputs["last_name"].setText(row[3] or "")
            if "phone" in wizard.inputs:
                wizard.inputs["phone"].setText(row[4] or "")
            if "email" in wizard.inputs:
                wizard.inputs["email"].setText(row[5] or "")
            if "hire_date" in wizard.inputs:
                wizard.inputs["hire_date"].setText(str(row[6]) if row[6] else "")
            if "status" in wizard.inputs:
                wizard.inputs["status"].setCurrentText(row[7] or "active")
        wizard = GenericWizard(fields, callback=wizard_callback, title="Mitarbeiter bearbeiten")
        if hasattr(wizard, "inputs") and "mitarbeiter_combo" in wizard.inputs:
            combo = wizard.inputs["mitarbeiter_combo"]
            combo.currentIndexChanged.connect(on_combo_change)
            # Vorwahl setzen, falls Index übergeben
            if vorwahl_index >= 0 and vorwahl_index < len(name_liste):
                combo.setCurrentIndex(vorwahl_index)
                on_combo_change(vorwahl_index)
        wizard.show()

    @Slot(int)
    def editDealsWizard(self, vorwahl_index):
        from generic_wizard import GenericWizard
        db = DBManager()
        alle_mitarbeiter = db.get_all_mitarbeiter()
        name_liste = [f"{row[2]} {row[3]}" for row in alle_mitarbeiter]
        
        fields = [
            ("Mitarbeiter", "mitarbeiter_combo", "combo", name_liste),
            ("Deal-Typ", "deal", "combo", ["P", "%"]),
            ("Pauschale (€)", "pauschale", "text"),
            ("Umsatzgrenze (€)", "umsatzgrenze", "text"),
            ("Garage (€)", "garage", "text")
        ]
        
        def wizard_callback(data):
            try:
                # Hole die aktuellen Deals-Daten für den Mitarbeiter
                fahrer_name = data["mitarbeiter_combo"]
                deal_type = data["deal"]
                pauschale = float(data["pauschale"]) if data["pauschale"] and deal_type == "P" else None
                umsatzgrenze = float(data["umsatzgrenze"]) if data["umsatzgrenze"] and deal_type == "P" else None
                garage = float(data["garage"]) if data["garage"] else None
                
                # Validiere die Daten je nach Deal-Typ
                if deal_type == "P":
                    if pauschale is None or umsatzgrenze is None:
                        print("Fehler: Bei P-Deal müssen Pauschale und Umsatzgrenze angegeben werden.")
                        return
                elif deal_type == "%":
                    # Bei %-Deal werden Pauschale und Umsatzgrenze automatisch auf None gesetzt
                    pass
                
                # Speichere in deals-Tabelle
                conn = sqlite3.connect("SQL/database.db")
                cursor = conn.cursor()
                
                # Prüfe ob Eintrag bereits existiert
                cursor.execute("SELECT id FROM deals WHERE name = ?", (fahrer_name,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update bestehenden Eintrag
                    cursor.execute("""
                        UPDATE deals 
                        SET deal = ?, pauschale = ?, umsatzgrenze = ?, garage = ?
                        WHERE name = ?
                    """, (deal_type, pauschale, umsatzgrenze, garage, fahrer_name))
                else:
                    # Erstelle neuen Eintrag
                    cursor.execute("""
                        INSERT INTO deals (name, deal, pauschale, umsatzgrenze, garage)
                        VALUES (?, ?, ?, ?, ?)
                    """, (fahrer_name, deal_type, pauschale, umsatzgrenze, garage))
                
                conn.commit()
                conn.close()
                print("Deals-Daten erfolgreich gespeichert.")
                
            except Exception as e:
                print(f"Fehler beim Speichern der Deals-Daten: {e}")
            
            self.anzeigenMitarbeiter()
        
        def on_combo_change(index):
            if index < 0 or index >= len(alle_mitarbeiter):
                return
            
            # Lade bestehende Deals-Daten für den Mitarbeiter
            fahrer_name = name_liste[index]
            try:
                conn = sqlite3.connect("SQL/database.db")
                cursor = conn.cursor()
                cursor.execute("SELECT deal, pauschale, umsatzgrenze, garage FROM deals WHERE name = ?", (fahrer_name,))
                row = cursor.fetchone()
                conn.close()
                
                if row and "deal" in wizard.inputs:
                    wizard.inputs["deal"].setCurrentText(row[0] or "P")
                if row and "pauschale" in wizard.inputs:
                    wizard.inputs["pauschale"].setText(f"{row[1]:.2f}" if row[1] is not None else "")
                if row and "umsatzgrenze" in wizard.inputs:
                    wizard.inputs["umsatzgrenze"].setText(f"{row[2]:.2f}" if row[2] is not None else "")
                if row and "garage" in wizard.inputs:
                    wizard.inputs["garage"].setText(f"{row[3]:.2f}" if row[3] is not None else "")
                    
            except Exception as e:
                print(f"Fehler beim Laden der Deals-Daten: {e}")
        
        def on_deal_change(deal_type):
            # Zeige/Verstecke Felder je nach Deal-Typ
            if hasattr(wizard, "inputs"):
                if "pauschale" in wizard.inputs:
                    wizard.inputs["pauschale"].setVisible(deal_type == "P")
                if "umsatzgrenze" in wizard.inputs:
                    wizard.inputs["umsatzgrenze"].setVisible(deal_type == "P")
        
        wizard = GenericWizard(fields, callback=wizard_callback, title="Deals bearbeiten")
        if hasattr(wizard, "inputs") and "mitarbeiter_combo" in wizard.inputs:
            combo = wizard.inputs["mitarbeiter_combo"]
            combo.currentIndexChanged.connect(on_combo_change)
            # Vorwahl setzen, falls Index übergeben
            if vorwahl_index >= 0 and vorwahl_index < len(name_liste):
                combo.setCurrentIndex(vorwahl_index)
                on_combo_change(vorwahl_index)
        
        # Deal-Typ Änderung überwachen
        if hasattr(wizard, "inputs") and "deal" in wizard.inputs:
            deal_combo = wizard.inputs["deal"]
            deal_combo.currentTextChanged.connect(on_deal_change)
            # Initiale Sichtbarkeit setzen
            on_deal_change(deal_combo.currentText())
        
        wizard.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    mitarbeiter = MitarbeiterSeiteQML()
    engine.rootContext().setContextProperty("mitarbeiterBackend", mitarbeiter)
    engine.load('Style/MitarbeiterSeite.qml')
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec()) 