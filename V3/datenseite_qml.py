from PySide6.QtCore import QObject, Slot, Signal, Property
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
import sys
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
import json
from generic_wizard import GenericWizard
import subprocess

class DatenSeiteQML(QObject):
    # Signals für QML
    dataChanged = Signal()
    loadingChanged = Signal()
    chartDataChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._is_loading = False
        self._chart_data = []
        self._filtered_data = []
        self._statistics = {
            'total_earnings': 0.0,
            'total_trips': 0,
            'total_hours': 0.0,
            'avg_per_hour': 0.0,
            'growth_rate': 0.0
        }
        
    # Properties für QML
    @Property(bool, notify=loadingChanged)
    def isLoading(self):
        return self._is_loading
        
    @Property(list, notify=chartDataChanged)
    def chartData(self):
        return self._chart_data
        
    @Property(dict, notify=dataChanged)
    def statistics(self):
        return self._statistics
        
    @Slot(str, str, str)
    def loadData(self, time_range, driver, platform):
        """Lädt Daten basierend auf den Filtern"""
        self._is_loading = True
        self.loadingChanged.emit()
        
        try:
            # Simuliere Datenladung
            self._load_sample_data(time_range, driver, platform)
            
            # Berechne Statistiken
            self._calculate_statistics()
            
            # Erstelle Chart-Daten
            self._create_chart_data()
            
        except Exception as e:
            print(f"Fehler beim Laden der Daten: {e}")
            self.showMessage("Fehler", f"Fehler beim Laden der Daten: {e}")
        finally:
            self._is_loading = False
            self.loadingChanged.emit()
            self.dataChanged.emit()
            self.chartDataChanged.emit()
    
    def _load_sample_data(self, time_range, driver, platform):
        """Lädt Beispieldaten für die Demo"""
        # Simuliere verschiedene Datensätze basierend auf Filtern
        sample_data = []
        
        if time_range == "week":
            days = 7
        elif time_range == "month":
            days = 30
        elif time_range == "quarter":
            days = 90
        else:  # year
            days = 365
            
        base_date = datetime.now()
        
        for i in range(days):
            date = base_date - timedelta(days=i)
            
            # Verschiedene Platforms
            platforms = ["Uber", "Bolt", "40100"] if platform == "all" else [platform]
            
            for p in platforms:
                # Verschiedene Fahrer
                drivers = ["Max Mustermann", "Anna Schmidt"] if driver == "all" else [driver]
                
                for d in drivers:
                    # Simuliere realistische Daten
                    earnings = round(20 + (i % 7) * 5 + hash(f"{p}{d}") % 30, 2)
                    hours = round(2 + (i % 5) * 0.5, 1)
                    
                    sample_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'platform': p,
                        'driver': d,
                        'earnings': earnings,
                        'hours': hours,
                        'status': 'Abgeschlossen'
                    })
        
        self._filtered_data = sample_data
    
    def _calculate_statistics(self):
        """Berechnet Statistiken aus den gefilterten Daten"""
        if not self._filtered_data:
            return
            
        total_earnings = sum(item['earnings'] for item in self._filtered_data)
        total_trips = len(self._filtered_data)
        total_hours = sum(item['hours'] for item in self._filtered_data)
        avg_per_hour = total_earnings / total_hours if total_hours > 0 else 0
        
        # Simuliere Wachstumsrate
        growth_rate = 12.5  # Prozent
        
        self._statistics = {
            'total_earnings': round(total_earnings, 2),
            'total_trips': total_trips,
            'total_hours': round(total_hours, 1),
            'avg_per_hour': round(avg_per_hour, 2),
            'growth_rate': growth_rate
        }
    
    def _create_chart_data(self):
        """Erstellt Daten für Charts"""
        if not self._filtered_data:
            return
            
        # Gruppiere nach Datum für Umsatz-Chart
        daily_earnings = {}
        platform_distribution = {}
        
        for item in self._filtered_data:
            date = item['date']
            earnings = item['earnings']
            platform = item['platform']
            
            # Tägliche Umsätze
            if date not in daily_earnings:
                daily_earnings[date] = 0
            daily_earnings[date] += earnings
            
            # Platform-Verteilung
            if platform not in platform_distribution:
                platform_distribution[platform] = 0
            platform_distribution[platform] += earnings
        
        # Erstelle Chart-Daten
        self._chart_data = {
            'daily_earnings': [
                {'date': date, 'earnings': earnings}
                for date, earnings in sorted(daily_earnings.items())
            ],
            'platform_distribution': [
                {'platform': platform, 'earnings': earnings}
                for platform, earnings in platform_distribution.items()
            ]
        }
    
    @Slot()
    def exportData(self):
        """Exportiert die aktuellen Daten"""
        try:
            if not self._filtered_data:
                self.showMessage("Export", "Keine Daten zum Exportieren verfügbar.")
                return
            
            # Erstelle Export-Daten
            export_data = {
                'export_date': datetime.now().isoformat(),
                'statistics': self._statistics,
                'data': self._filtered_data,
                'chart_data': self._chart_data
            }
            
            # Öffne Datei-Dialog
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Daten exportieren",
                f"daten_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Dateien (*.json);;CSV Dateien (*.csv)"
            )
            
            if file_path:
                if file_path.endswith('.json'):
                    # Export als JSON
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                elif file_path.endswith('.csv'):
                    # Export als CSV
                    df = pd.DataFrame(self._filtered_data)
                    df.to_csv(file_path, index=False, encoding='utf-8')
                
                self.showMessage("Export erfolgreich", f"Daten wurden nach {file_path} exportiert.")
                
        except Exception as e:
            print(f"Fehler beim Export: {e}")
            self.showMessage("Export Fehler", f"Fehler beim Exportieren: {e}")
    
    @Slot(str, str)
    def showMessage(self, title, message):
        """Zeigt eine Nachricht an"""
        print(f"{title}: {message}")
        # Hier könnte ein QML-Dialog implementiert werden
    
    @Slot()
    def refreshData(self):
        """Aktualisiert die Daten"""
        self.loadData("week", "all", "all")
    
    @Slot(str)
    def updateTimeRange(self, time_range):
        """Aktualisiert den Zeitraum"""
        # Hier würde die Datenladung mit neuem Zeitraum implementiert werden
        print(f"Zeitraum geändert zu: {time_range}")
    
    @Slot(str)
    def updateDriverFilter(self, driver):
        """Aktualisiert den Fahrer-Filter"""
        print(f"Fahrer-Filter geändert zu: {driver}")
    
    @Slot(str)
    def updatePlatformFilter(self, platform):
        """Aktualisiert den Platform-Filter"""
        print(f"Platform-Filter geändert zu: {platform}")

    def get_recent_weeks(self, n=8):
        today = datetime.now()
        current_kw = today.isocalendar()[1]
        last_kw = current_kw - 1 if current_kw > 1 else 53
        weeks = []
        for i in range(n):
            kw = last_kw - i
            if kw < 1:
                kw += 53
            weeks.append(f"KW {kw}")
        return weeks

    @Slot()
    def show_import_wizard(self):
        print('show_import_wizard aufgerufen')
        # Zuerst nur Import-Typ abfragen
        fields = [
            ("Import-Typ", "import_typ", "combo", ["Umsatz", "Gehalt", "Funk"])
        ]
        def import_typ_callback(data):
            print(f"[ImportWizard] Auswahl: {data}")
            if data["import_typ"] == "Gehalt":
                # Wizard sofort schließen und nur Datei-Dialog öffnen
                pdf_file, _ = QFileDialog.getOpenFileName(
                    None,
                    "Bitte Gehaltsabrechnungs-PDF auswählen",
                    "",
                    "PDF-Dateien (*.pdf)"
                )
                if not pdf_file:
                    print("Keine Datei ausgewählt. Abbruch.")
                    return
                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL")
                salaries_db = os.path.join(base_dir, "salaries.db")
                drivers_db = os.path.join(base_dir, "database.db")
                import_salarie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_salarie.py")
                try:
                    subprocess.Popen([
                        sys.executable,
                        import_salarie_path,
                        pdf_file,
                        salaries_db,
                        drivers_db
                    ])
                    print(f"import_salarie.py mit {pdf_file}, {salaries_db}, {drivers_db} gestartet.")
                except Exception as e:
                    print(f"Fehler beim Start von import_salarie.py: {e}")
                return  # Wizard beenden
            elif data["import_typ"] == "Funk":
                # Wizard sofort schließen und nur Datei-Dialog öffnen
                pdf_file, _ = QFileDialog.getOpenFileName(
                    None,
                    "Bitte Funk/ARF-PDF auswählen",
                    "",
                    "PDF-Dateien (*.pdf)"
                )
                if not pdf_file:
                    print("Keine Datei ausgewählt. Abbruch.")
                    return
                base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL")
                funk_db = os.path.join(base_dir, "funk.db")
                vehicles_db = os.path.join(base_dir, "database.db")
                import_funk_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_funk.py")
                try:
                    subprocess.Popen([
                        sys.executable,
                        import_funk_path,
                        pdf_file,
                        funk_db,
                        vehicles_db
                    ])
                    print(f"import_funk.py mit {pdf_file}, {funk_db}, {vehicles_db} gestartet.")
                except Exception as e:
                    print(f"Fehler beim Start von import_funk.py: {e}")
                return  # Wizard beenden
            elif data["import_typ"] == "Umsatz":
                # Zweiten Wizard für Umsatz-spezifische Felder öffnen
                umsatz_fields = [
                    ("Plattform", "plattform", "combo", ["Alle", "Uber", "40100", "Bolt"]),
                    ("Kalenderwoche", "kalenderwoche", "combo", self.get_recent_weeks())
                ]
                def umsatz_callback(umsatz_data):
                    plattform_map = {"Alle": "0", "Uber": "1", "40100": "2", "Bolt": "3"}
                    plattform_num = plattform_map.get(umsatz_data["plattform"], "0")
                    kw_num = ''.join(filter(str.isdigit, umsatz_data["kalenderwoche"]))
                    dl_path = os.path.join("download", "src", "DL.py")
                    try:
                        subprocess.Popen([
                            sys.executable,
                            dl_path,
                            kw_num,
                            plattform_num
                        ])
                        print(f"DL.py mit KW {kw_num} und Plattform {plattform_num} gestartet.")
                    except Exception as e:
                        print(f"Fehler beim Start von DL.py: {e}")
                parent = None
                self._umsatz_wizard = GenericWizard(umsatz_fields, callback=umsatz_callback, parent=parent, title="Umsatz Import Wizard")
                self._umsatz_wizard.show()
            else:
                print("Plattform/Kalenderwoche nicht relevant für diesen Import-Typ.")
        parent = None
        self._import_wizard = GenericWizard(fields, callback=import_typ_callback, parent=parent, title="Import Wizard")
        self._import_wizard.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    daten = DatenSeiteQML()
    engine.rootContext().setContextProperty("datenBackend", daten)
    engine.load('Style/Datenseite.qml')
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec()) 