from PySide6.QtCore import QObject, Slot, Signal, Property
import sqlite3
from generic_wizard import GenericWizard
from db_manager import DBManager

class FahrzeugSeiteQML(QObject):
    fahrzeugListChanged = Signal()

    def __init__(self):
        super().__init__()
        self._fahrzeug_list = []

    @Property('QVariantList', notify=fahrzeugListChanged)
    def fahrzeugList(self):
        return self._fahrzeug_list

    @Slot()
    def showVehicleWizard(self):
        print("Fahrzeug-Wizard wird geöffnet...")
        fields = [
            ("Kennzeichen", "license_plate", "text"),
            ("Referenz", "rfrnc", "text"),
            ("Modell", "model", "text"),
            ("Baujahr", "year", "text"),
            ("Versicherung", "insurance", "text"),
            ("Finanzierung", "credit", "text")
        ]
        def wizard_callback(data):
            print(f"[DEBUG] Neues Fahrzeug-Dict: {data}")
            for k, v in data.items():
                print(f"[DEBUG] Key: {k}, Value: {v}, Type: {type(v)}")
            db = DBManager()
            try:
                db.insert_fahrzeug(data)
                print("Fahrzeug erfolgreich in DB gespeichert.")
            except Exception as e:
                print(f"Fehler beim Speichern des Fahrzeugs: {e}")
            self.anzeigenFahrzeuge()
        wizard = GenericWizard(fields, callback=wizard_callback, title="Fahrzeug anlegen")
        wizard.show()

    @Slot()
    def anzeigenFahrzeuge(self):
        try:
            conn = sqlite3.connect("SQL/database.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT license_plate, rfrnc, model, year, insurance, credit 
                FROM vehicles
                ORDER BY license_plate
            """)
            rows = cursor.fetchall()
            self._fahrzeug_list = []
            for row in rows:
                fahrzeug = {
                    "kennzeichen": row[0] or "",
                    "rfrnc": row[1] or "",
                    "modell": row[2] or "",
                    "baujahr": str(row[3]) if row[3] else "",
                    "versicherung": row[4] or "",
                    "finanzierung": row[5] or ""
                }
                self._fahrzeug_list.append(fahrzeug)
            self.fahrzeugListChanged.emit()
            print(f"{len(self._fahrzeug_list)} Fahrzeuge geladen")
            for fzg in self._fahrzeug_list:
                print(fzg)
        except Exception as e:
            print(f"Fehler beim Laden der Fahrzeuge: {e}")
        finally:
            try:
                conn.close()
            except:
                pass

    @Slot()
    def editVehicleWizard(self):
        from generic_wizard import GenericWizard
        from db_manager import DBManager
        print("Fahrzeug bearbeiten Wizard wird geöffnet...")
        db = DBManager()
        # Alle Fahrzeuge laden
        alle_fahrzeuge = db.get_all_fahrzeuge()
        kennzeichen_liste = [row[0] for row in alle_fahrzeuge]
        # Felder für den Wizard
        fields = [
            ("Kennzeichen", "license_plate", "combo", kennzeichen_liste),
            ("Referenz", "rfrnc", "text"),
            ("Modell", "model", "text"),
            ("Baujahr", "year", "text"),
            ("Versicherung", "insurance", "text"),
            ("Finanzierung", "credit", "text")
        ]
        def wizard_callback(data):
            print(f"[DEBUG] Bearbeitetes Fahrzeug: {data}")
            # Update in DB
            try:
                db.update_fahrzeug_by_plate(data["license_plate"], data)
                print("Fahrzeug erfolgreich aktualisiert.")
            except Exception as e:
                print(f"Fehler beim Aktualisieren des Fahrzeugs: {e}")
            self.anzeigenFahrzeuge()
        # Vorbelegung der Felder nach Auswahl
        def on_combo_change(index):
            if index < 0 or index >= len(alle_fahrzeuge):
                return
            row = alle_fahrzeuge[index]
            # Mapping: (license_plate, rfrnc, model, year, insurance, credit)
            if "rfrnc" in wizard.inputs:
                wizard.inputs["rfrnc"].setText(row[1] or "")
            if "model" in wizard.inputs:
                wizard.inputs["model"].setText(row[2] or "")
            if "year" in wizard.inputs:
                wizard.inputs["year"].setText(str(row[3]) if row[3] else "")
            if "insurance" in wizard.inputs:
                wizard.inputs["insurance"].setText(str(row[4]) if row[4] else "")
            if "credit" in wizard.inputs:
                wizard.inputs["credit"].setText(str(row[5]) if row[5] else "")
        wizard = GenericWizard(fields, callback=wizard_callback, title="Fahrzeug bearbeiten")
        # ComboBox-Change-Handler setzen
        if hasattr(wizard, "inputs") and "license_plate" in wizard.inputs:
            combo = wizard.inputs["license_plate"]
            combo.currentIndexChanged.connect(on_combo_change)
        wizard.show() 