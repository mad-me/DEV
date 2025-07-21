from PySide6.QtCore import QObject, Slot, Signal, Property
import sqlite3
from generic_wizard import GenericWizard
from db_manager import DBManager
import difflib

class FahrzeugSeiteQML(QObject):
    fahrzeugListChanged = Signal()
    filterTextChanged = Signal()
    showOnlyActiveChanged = Signal()

    def __init__(self):
        super().__init__()
        self._fahrzeug_list = []
        self._filter_text = ""
        self._show_only_active = True

    @Property('QVariantList', notify=fahrzeugListChanged)
    def fahrzeugList(self):
        return self._fahrzeug_list

    def getFilterText(self):
        return getattr(self, '_filter_text', "")
    def setFilterText(self, value):
        if getattr(self, '_filter_text', "") != value:
            self._filter_text = value
            self.filterTextChanged.emit()
            self.anzeigenFahrzeuge()
    @Property(str, fget=getFilterText, fset=setFilterText, notify=filterTextChanged)
    def filterText(self):
        return self.getFilterText()

    def getShowOnlyActive(self):
        return getattr(self, '_show_only_active', True)
    def setShowOnlyActive(self, value):
        if getattr(self, '_show_only_active', True) != value:
            self._show_only_active = value
            self.showOnlyActiveChanged.emit()
            self.anzeigenFahrzeuge()
    @Property(bool, fget=getShowOnlyActive, fset=setShowOnlyActive, notify=showOnlyActiveChanged)
    def showOnlyActive(self):
        return self.getShowOnlyActive()

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
            filter_text = getattr(self, '_filter_text', "").lower()
            filter_text_no_space = filter_text.replace(" ", "")
            filter_text_alt = filter_text_no_space.replace("+43", "0") if "+43" in filter_text_no_space else filter_text_no_space.replace("0", "+43")
            fuzzy_threshold = 0.8
            
            for row in rows:
                fahrzeug = {
                    "kennzeichen": row[0] or "",
                    "rfrnc": row[1] or "",
                    "modell": row[2] or "",
                    "baujahr": str(row[3]) if row[3] else "",
                    "versicherung": row[4] or "",
                    "finanzierung": row[5] or ""
                }
                
                # Filter anwenden
                if filter_text:
                    suchfelder = [
                        str(fahrzeug["kennzeichen"]),
                        str(fahrzeug["rfrnc"]),
                        str(fahrzeug["modell"]),
                        str(fahrzeug["baujahr"]),
                        str(fahrzeug["versicherung"]),
                        str(fahrzeug["finanzierung"])
                    ]
                    # Normale Teilstring-Suche
                    match = any(filter_text in feld.lower() for feld in suchfelder)
                    # Fuzzy-Suche
                    if not match:
                        for feld in suchfelder:
                            ratio = difflib.SequenceMatcher(None, filter_text, feld.lower()).ratio()
                            if ratio >= fuzzy_threshold:
                                match = True
                                break
                    if not match:
                        continue
                
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

    @Slot(str)
    def editVehicleWizard_by_id(self, license_plate):
        from generic_wizard import GenericWizard
        from db_manager import DBManager
        print(f"Fahrzeug bearbeiten Wizard für Kennzeichen {license_plate} wird geöffnet...")
        db = DBManager()
        row = db.get_fahrzeug_by_plate(license_plate)
        if not row:
            print(f"Kein Fahrzeug mit Kennzeichen {license_plate} gefunden.")
            return
        # Felder für den Wizard
        fields = [
            ("Kennzeichen", "license_plate", "text"),
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
                db.update_fahrzeug_by_plate(license_plate, data)
                print("Fahrzeug erfolgreich aktualisiert.")
            except Exception as e:
                print(f"Fehler beim Aktualisieren des Fahrzeugs: {e}")
            self.anzeigenFahrzeuge()
        wizard = GenericWizard(fields, callback=wizard_callback, title=f"Fahrzeug bearbeiten: {license_plate}")
        # Vorbelegung der Felder
        if hasattr(wizard, "inputs"):
            if "license_plate" in wizard.inputs:
                wizard.inputs["license_plate"].setText(row[0] or "")
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
        wizard.show() 