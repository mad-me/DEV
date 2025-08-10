import sqlite3
import pandas as pd
import re
from pathlib import Path
from tkinter.filedialog import askopenfilenames
from tkinter import Tk, messagebox
import os

# === Fahrermatching-Funktionen ===
def lade_fahrerliste():
    """Lädt die Fahrerliste aus der Hauptdatenbank"""
    try:
        conn = sqlite3.connect("database.db")
        df = pd.read_sql_query("SELECT first_name, last_name FROM drivers", conn)
        conn.close()
        return df.apply(lambda row: f"{row['first_name']} {row['last_name']}", axis=1).tolist()
    except Exception as e:
        print(f"⚠️ Fehler beim Laden der Fahrerliste: {e}")
        return []

def match_name(import_name, fahrerliste):
    """Führt Fahrermatching durch"""
    if not fahrerliste:
        return ""
    
    tokens = [t.strip().lower() for t in re.split(r"[ ,]+", str(import_name)) if t.strip()]
    best_match = ""
    best_score = 0
    
    for fahrer in fahrerliste:
        fahrer_tokens = [t.strip().lower() for t in fahrer.split() if t.strip()]
        matches = sum(1 for t in tokens if t in fahrer_tokens)
        if matches > best_score:
            best_score = matches
            best_match = fahrer
    
    if best_score >= 2 and len(tokens) >= 2:
        return best_match
    else:
        return ""

def erkenne_plattform_aus_spalten(df):
    """Erkennt die Plattform basierend auf den vorhandenen Spalten"""
    spalten = [col.lower().strip() for col in df.columns]
    
    # Uber-Erkennung
    uber_indikatoren = [
        "vorname des fahrers", "nachname des fahrers", "gesamtumsätze",
        "umsätze/std", "eingenommenes bargeld", "stunden online",
        "stunden fahrtzeit", "unternommene fahrten", "annahmerate"
    ]
    uber_score = sum(1 for ind in uber_indikatoren if any(ind in spalte for spalte in spalten))
    
    # Bolt-Erkennung
    bolt_indikatoren = [
        "driver", "gross earnings", "net earnings", "rider tips",
        "collected cash", "gross earnings per hour", "net earnings per hour"
    ]
    bolt_score = sum(1 for ind in bolt_indikatoren if any(ind in spalte for spalte in spalten))
    
    # 40100/Taxi-Erkennung
    taxi_indikatoren = [
        "fahrzeug", "fahrer", "fahrername", "abschluss", "buchungsart",
        "zahlungsmittel", "belegtext", "fahrtkosten", "trinkgeld", "umsatz",
        "bargeld", "auftragsart", "status"
    ]
    taxi_score = sum(1 for ind in taxi_indikatoren if any(ind in spalte for spalte in spalten))
    
    # Beste Übereinstimmung finden
    scores = {
        "uber": uber_score,
        "bolt": bolt_score,
        "40100": taxi_score
    }
    
    best_platform = max(scores, key=scores.get)
    best_score = scores[best_platform]
    
    # Mindestens 3 Spalten müssen übereinstimmen
    if best_score >= 3:
        return best_platform
    else:
        return None

def extrahiere_kalenderwoche(filename):
    """Extrahiert die Kalenderwoche aus dem Dateinamen"""
    # Taxi-Umsatz-Format: 2025.07.28_0000_2025.08.04_0000
    taxi_date_pattern = r"(\d{4})\.(\d{2})\.(\d{2})_0000_(\d{4})\.(\d{2})\.(\d{2})_0000"
    taxi_match = re.search(taxi_date_pattern, filename)
    if taxi_match:
        start_year, start_month, start_day = taxi_match.group(1), taxi_match.group(2), taxi_match.group(3)
        end_year, end_month, end_day = taxi_match.group(4), taxi_match.group(5), taxi_match.group(6)
        
        try:
            from datetime import datetime
            start_date = datetime.strptime(f"{start_year}{start_month}{start_day}", "%Y%m%d")
            end_date = datetime.strptime(f"{end_year}{end_month}{end_day}", "%Y%m%d")
            
            # Kalenderwoche manuell berechnen (wie im echten import.py)
            # Verwende das Startdatum für die KW-Berechnung
            from datetime import datetime, timedelta
            
            # Ersten Tag des Jahres finden
            year_start = datetime(end_date.year, 1, 1)
            
            # Ersten Montag des Jahres finden
            while year_start.weekday() != 0:  # 0 = Montag
                year_start += timedelta(days=1)
            
            # Tage seit dem ersten Montag zählen
            days_since_monday = (end_date - year_start).days
            
            # Kalenderwoche berechnen
            kw = (days_since_monday // 7) + 1
            
            # Wenn das Datum vor dem ersten Montag liegt, ist es KW 1 des Vorjahres
            if days_since_monday < 0:
                # Vorjahres-Logik
                prev_year_start = datetime(end_date.year - 1, 1, 1)
                while prev_year_start.weekday() != 0:
                    prev_year_start += timedelta(days=1)
                days_since_prev_monday = (end_date - prev_year_start).days
                kw = (days_since_prev_monday // 7) + 1
            
            print(f"   📅 Taxi-Datum: {end_date} → KW {kw}")
            return f"{kw:02d}"
            
        except ValueError as e:
            print(f"   ⚠️ Fehler beim Parsen des Taxi-Datums: {e}")
            return None
    
    # Datumsbereich-Format: 20250728-20250803 (Bolt-Format)
    date_range_pattern = r"(\d{8})-(\d{8})"
    date_match = re.search(date_range_pattern, filename)
    if date_match:
        start_date_str = date_match.group(1)
        end_date_str = date_match.group(2)
        
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, "%Y%m%d")
            end_date = datetime.strptime(end_date_str, "%Y%m%d")
            
            # Kalenderwoche manuell berechnen (wie im echten import.py)
            from datetime import datetime, timedelta
            
            # Ersten Tag des Jahres finden
            year_start = datetime(end_date.year, 1, 1)
            
            # Ersten Montag des Jahres finden
            while year_start.weekday() != 0:  # 0 = Montag
                year_start += timedelta(days=1)
            
            # Tage seit dem ersten Montag zählen
            days_since_monday = (end_date - year_start).days
            
            # Kalenderwoche berechnen
            kw = (days_since_monday // 7) + 1
            
            # Wenn das Datum vor dem ersten Montag liegt, ist es KW 1 des Vorjahres
            if days_since_monday < 0:
                # Vorjahres-Logik
                prev_year_start = datetime(end_date.year - 1, 1, 1)
                while prev_year_start.weekday() != 0:
                    prev_year_start += timedelta(days=1)
                days_since_prev_monday = (end_date - prev_year_start).days
                kw = (days_since_prev_monday // 7) + 1
            
            print(f"   📅 Datum: {end_date} → KW {kw}")
            return f"{kw:02d}"
            
        except ValueError as e:
            print(f"   ⚠️ Fehler beim Parsen des Datums: {e}")
            return None
    
    # Verschiedene Formate unterstützen (allgemeinere Patterns danach)
    patterns = [
        r"kw(\d+)",           # kw23
        r"woche(\d+)",        # woche23
        r"week(\d+)",         # week23
        r"w(\d+)",            # W31 (Bolt-Format)
        r"(\d{2})",           # 23 (alleinstehend)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename.lower())
        if match:
            return match.group(1)
    
    return None

def verarbeite_uber_daten(df, kalenderwoche):
    """Verarbeitet Uber-Daten (wie in echter Abrechnung)"""
    print("🔍 Erkenne Uber-Format...")
    
    # Debug: Zeige verfügbare Spalten
    print(f"   Verfügbare Spalten: {list(df.columns)}")
    
    # Prüfe, ob es sich um Performance-Daten handelt
    is_performance_data = "Driver score|%" in df.columns or "Finished rides" in df.columns
    
    if is_performance_data:
        print("   📊 Performance-Daten erkannt - verwende alternative Verarbeitung")
        
        # Für Performance-Daten: Nur Driver-Name und grundlegende Metriken
        spalten_mapping = {
            "Driver": "driver_name",
            "Finished rides": "total_trips",
            "Online time (min)": "hours_online",
            "Total acceptance rate|%": "acceptance_rate",
            "Average driver rating|★": "driver_rating"
        }
        
        # Verfügbare Spalten umbenennen
        for alt, neu in spalten_mapping.items():
            if alt in df.columns:
                df.rename(columns={alt: neu}, inplace=True)
                print(f"   Spalte umbenannt: {alt} → {neu}")
        
        # Zielspalten für Performance-Daten
        zielspalten = ["driver_name", "total_trips", "hours_online", "acceptance_rate", "driver_rating"]
        
    else:
        print("   💰 Umsatz-Daten erkannt - verwende Standard-Verarbeitung")
        
        # Standard Umsatz-Spalten-Mapping (wie in echter Abrechnung)
        spalten_mapping = {
            "Vorname des Fahrers": "first_name",
            "Nachname des Fahrers": "last_name",
            "Gesamtumsätze": "gross_total",
            "Umsätze/Std": "gross_per_hour",
            "Eingenommenes Bargeld": "cash_collected",
            "Stunden online": "hours_online",
            "Stunden Fahrtzeit": "drive_time",
            "Unternommene Fahrten": "total_trips",
            "Annahmerate": "acceptance_rate"
        }
        
        # Verfügbare Spalten umbenennen
        for alt, neu in spalten_mapping.items():
            if alt in df.columns:
                df.rename(columns={alt: neu}, inplace=True)
                print(f"   Spalte umbenannt: {alt} → {neu}")
        
        # Zielspalten für Umsatz-Daten
        zielspalten = [
            "first_name", "last_name", "gross_total", "gross_per_hour",
            "cash_collected", "hours_online", "drive_time",
            "total_trips", "acceptance_rate"
        ]
    
    # Nur vorhandene Spalten behalten
    available_spalten = [col for col in zielspalten if col in df.columns]
    df = df[available_spalten].copy()
    print(f"   Verwendete Spalten: {available_spalten}")
    
    # Numerische Spalten bereinigen
    numeric_cols = [col for col in available_spalten if col not in ["first_name", "last_name", "driver_name"]]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(",", ".")
                .str.replace(" ", "")
                .replace("nan", None)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Fahrermatching (nur für interne Verarbeitung, nicht für DB)
    fahrerliste = lade_fahrerliste()
    if "first_name" in df.columns and "last_name" in df.columns:
        df["import_name"] = df["first_name"].fillna("") + " " + df["last_name"].fillna("")
        matched_names = df["import_name"].apply(lambda n: match_name(n, fahrerliste))
        print(f"   Fahrermatching: {len(matched_names[matched_names != ''])} von {len(df)} Fahrern gematcht")
        df.drop(columns=["import_name"], inplace=True)
    elif "driver_name" in df.columns:
        matched_names = df["driver_name"].apply(lambda n: match_name(n, fahrerliste))
        print(f"   Fahrermatching: {len(matched_names[matched_names != ''])} von {len(df)} Fahrern gematcht")
    
    df["week"] = kalenderwoche
    return df, "uber.sqlite"

def verarbeite_bolt_daten(df, kalenderwoche):
    """Verarbeitet Bolt-Daten (inkl. neue Performance-Dateien)"""
    print("🔍 Erkenne Bolt-Format...")
    
    # Debug: Zeige verfügbare Spalten
    print(f"   Verfügbare Spalten: {list(df.columns)}")
    
    # Prüfe, ob es sich um Performance-Daten handelt
    is_performance_data = "Driver score|%" in df.columns or "Finished rides" in df.columns
    
    if is_performance_data:
        print("   📊 Performance-Daten erkannt - verwende alternative Verarbeitung")
        
        # Für Performance-Daten: Nur Driver-Name und grundlegende Metriken
        spalten_mapping = {
            "Driver": "driver_name",
            "Finished rides": "total_trips",
            "Online time (min)": "hours_online",
            "Total acceptance rate|%": "acceptance_rate",
            "Average driver rating|★": "driver_rating"
        }
        
        # Verfügbare Spalten umbenennen
        for alt, neu in spalten_mapping.items():
            if alt in df.columns:
                df.rename(columns={alt: neu}, inplace=True)
                print(f"   Spalte umbenannt: {alt} → {neu}")
        
        # Zielspalten für Performance-Daten
        zielspalten = ["driver_name", "total_trips", "hours_online", "acceptance_rate", "driver_rating"]
        
    else:
        print("   💰 Umsatz-Daten erkannt - verwende Standard-Verarbeitung")
        
        # Standard Umsatz-Spalten-Mapping
        spalten_mapping = {
            "Driver": "driver_name",
            "Gross earnings (total)|€": "gross_total",
            "Net earnings|€": "net_earnings",
            "Gross earnings per hour|€/h": "gross_per_hour",
            "Net earnings per hour|€/h": "net_per_hour",
            "Rider tips|€": "rider_tips",
            "Collected cash|€": "cash_collected"
        }
        
        # Verfügbare Spalten umbenennen
        for alt, neu in spalten_mapping.items():
            if alt in df.columns:
                df.rename(columns={alt: neu}, inplace=True)
                print(f"   Spalte umbenannt: {alt} → {neu}")
        
        # Zielspalten für Umsatz-Daten
        zielspalten = ["driver_name", "gross_total", "net_earnings", "gross_per_hour", "net_per_hour", "rider_tips", "cash_collected"]
    
    # Nur vorhandene Spalten behalten
    available_spalten = [col for col in zielspalten if col in df.columns]
    df = df[available_spalten].copy()
    print(f"   Verwendete Spalten: {available_spalten}")
    
    # Numerische Spalten bereinigen
    numeric_cols = [col for col in available_spalten if col != "driver_name"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(",", ".")
                .str.replace(" ", "")
                .replace("nan", None)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Fahrermatching (nur für interne Verarbeitung, nicht für DB)
    fahrerliste = lade_fahrerliste()
    if "driver_name" in df.columns:
        matched_names = df["driver_name"].apply(lambda n: match_name(n, fahrerliste))
        print(f"   Fahrermatching: {len(matched_names[matched_names != ''])} von {len(df)} Fahrern gematcht")
    
    df["week"] = kalenderwoche
    return df, "bolt.sqlite"

def verarbeite_40100_daten(df, kalenderwoche):
    """Verarbeitet 40100/Taxi-Daten"""
    print("🔍 Erkenne 40100/Taxi-Format...")
    
    # Zielspalten definieren
    zielspalten = [
        "Fahrzeug", "Fahrer", "Fahrername", "Abschluss", "Buchungsart",
        "Zahlungsmittel", "Belegtext", "Fahrtkosten", "Trinkgeld", "Umsatz",
        "Bargeld", "Auftragsart", "Status"
    ]
    
    # Nur vorhandene Spalten behalten
    df = df[[col for col in zielspalten if col in df.columns]].copy()
    
    # Numerische Spalten bereinigen
    for col in ["Fahrtkosten", "Trinkgeld", "Umsatz", "Bargeld"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(",", ".")
                .str.replace(" ", "")
                .replace("nan", None)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df["week"] = kalenderwoche
    return df, "40100.sqlite"

def verarbeite_31300_daten(df, kalenderwoche):
    """Verarbeitet 31300-Daten"""
    print("🔍 Erkenne 31300-Format...")
    
    # Zielspalten definieren (wie in import.py)
    zielspalten = [
        "Fahrzeug", "Fahrer", "Fahrername", "Abschluss", "Beleg", "Zeitpunkt", "Leistung", "Tour",
        "Buchungsart", "Zahlungsmittel", "Belegtext", "Gesamt", "Kst", "10%", "20%", "Fahrtkosten",
        "Trinkgeld", "Auftragsart", "Status", "Bemerkung"
    ]
    
    # Nur vorhandene Spalten behalten
    df = df[[col for col in zielspalten if col in df.columns]].copy()
    
    # Numerische Spalten bereinigen
    numeric_cols = ["Fahrtkosten", "Trinkgeld", "Gesamt", "10%", "20%"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(",", ".")
                .str.replace(" ", "")
                .replace("nan", None)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Kein Fahrermatching für 31300 (wie im echten import.py)
    
    df["week"] = kalenderwoche
    return df, "31300.sqlite"

def erstelle_tabelle(conn, platform, tabelle):
    """Erstellt die entsprechende Tabelle"""
    create_sql = {
        "uber": f"""
            CREATE TABLE IF NOT EXISTS {tabelle} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                gross_total REAL,
                gross_per_hour REAL,
                cash_collected REAL,
                hours_online REAL,
                drive_time REAL,
                total_trips INTEGER,
                acceptance_rate REAL,
                driver_name TEXT,
                driver_rating REAL,
                week TEXT
            );
        """,
        "bolt": f"""
            CREATE TABLE IF NOT EXISTS {tabelle} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_name TEXT,
                gross_total REAL,
                net_earnings REAL,
                gross_per_hour REAL,
                net_per_hour REAL,
                rider_tips REAL,
                cash_collected REAL,
                total_trips INTEGER,
                hours_online REAL,
                acceptance_rate REAL,
                driver_rating REAL,
                week TEXT
            );
        """,
        "40100": f"""
            CREATE TABLE IF NOT EXISTS {tabelle} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Fahrzeug TEXT,
                Fahrer TEXT,
                Fahrername TEXT,
                Abschluss TEXT,
                Buchungsart TEXT,
                Zahlungsmittel TEXT,
                Belegtext TEXT,
                Fahrtkosten REAL,
                Trinkgeld REAL,
                Umsatz REAL,
                Bargeld REAL,
                Auftragsart TEXT,
                Status TEXT,
                week TEXT
            );
        """,
        "31300": f"""
            CREATE TABLE IF NOT EXISTS {tabelle} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Fahrzeug TEXT,
                Fahrer TEXT,
                Fahrername TEXT,
                Abschluss TEXT,
                Beleg TEXT,
                Zeitpunkt TEXT,
                Leistung TEXT,
                Tour TEXT,
                Buchungsart TEXT,
                Zahlungsmittel TEXT,
                Belegtext TEXT,
                Gesamt REAL,
                Kst TEXT,
                "10%" REAL,
                "20%" REAL,
                Fahrtkosten REAL,
                Trinkgeld REAL,
                Auftragsart TEXT,
                Status TEXT,
                Bemerkung TEXT,
                week TEXT
            );
        """,
    }
    
    cursor = conn.cursor()
    cursor.execute(create_sql[platform])

def verarbeite_datei(csv_datei, platform_choice=None):
    """Hauptfunktion zur Dateiverarbeitung"""
    filename = Path(csv_datei).name
    print(f"\n📁 Verarbeite: {filename}")
    
    # Kalenderwoche extrahieren
    kw = extrahiere_kalenderwoche(filename)
    if not kw:
        print(f"⚠️ Keine Kalenderwoche im Dateinamen {filename} gefunden")
        return
    
    kalenderwoche = f"KW{kw}"
    tabelle = f"report_KW{kw}"
    
    # Trennzeichen erkennen
    try:
        with open(csv_datei, "r", encoding="utf-8") as f:
            header = f.readline()
            sep = ";" if header.count(";") > header.count(",") else ","
    except UnicodeDecodeError:
        # Fallback für andere Kodierungen
        with open(csv_datei, "r", encoding="latin-1") as f:
            header = f.readline()
            sep = ";" if header.count(";") > header.count(",") else ","
    
    # CSV laden
    try:
        df = pd.read_csv(csv_datei, sep=sep, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_datei, sep=sep, encoding="latin-1")
    
    df.columns = df.columns.str.strip()
    
    # Plattform erkennen (wie in import.py - Dateinamen-basiert)
    filename_lower = filename.lower()
    
    # Spezielle Erkennung für Taxi-Umsatz-Dateien
    if "uportal_getumsatzliste" in filename_lower:
        if platform_choice:
            # Plattform wurde bereits ausgewählt (z.B. aus GUI)
            platform = platform_choice
            print(f"   🔍 Taxi-Umsatz-Datei erkannt: {filename}")
            print(f"   ✅ Plattform bereits ausgewählt: {platform}")
        else:
            # Interaktive Auswahl (für Kommandozeile)
            print(f"   🔍 Taxi-Umsatz-Datei erkannt: {filename}")
            print(f"   Bitte wählen Sie die Quelle:")
            print(f"   1. 40100 (Hauptstelle)")
            print(f"   2. 31300 (Zweigstelle)")
            
            while True:
                try:
                    choice = input("   Ihre Wahl (1 oder 2): ").strip()
                    if choice == "1":
                        platform = "40100"
                        print(f"   ✅ Ausgewählt: 40100 (Hauptstelle)")
                        break
                    elif choice == "2":
                        platform = "31300"
                        print(f"   ✅ Ausgewählt: 31300 (Zweigstelle)")
                        break
                    else:
                        print(f"   ⚠️ Bitte geben Sie 1 oder 2 ein.")
                except KeyboardInterrupt:
                    print(f"\n   ❌ Import abgebrochen.")
                    return
                except EOFError:
                    print(f"\n   ❌ Import abgebrochen.")
                    return
    elif "uber" in filename_lower or "driver_performance" in filename_lower:
        platform = "uber"
    elif "bolt" in filename_lower or "drivers performance" in filename_lower or "earnings per driver" in filename_lower:
        platform = "bolt"
    elif "31300" in filename_lower:
        platform = "31300"
    elif "40100" in filename_lower or "taxi" in filename_lower:
        platform = "40100"
    else:
        print(f"⚠️ Plattform für {filename} nicht erkannt")
        print(f"   Dateiname: {filename}")
        return
    
    print(f"✅ Plattform erkannt: {platform}")
    
    # Daten verarbeiten
    if platform == "uber":
        df, db_name = verarbeite_uber_daten(df, kalenderwoche)
    elif platform == "bolt":
        df, db_name = verarbeite_bolt_daten(df, kalenderwoche)
    elif platform == "40100":
        df, db_name = verarbeite_40100_daten(df, kalenderwoche)
    elif platform == "31300":
        df, db_name = verarbeite_31300_daten(df, kalenderwoche)
    
    # In Datenbank speichern (im SQL-Ordner)
    try:
        # Stelle sicher, dass der SQL-Ordner existiert
        sql_dir = Path(__file__).parent
        db_path = sql_dir / db_name
        conn = sqlite3.connect(db_path)
        erstelle_tabelle(conn, platform, tabelle)
        
        # Duplikate prüfen
        if platform == "uber":
            check_sql = f"SELECT first_name, last_name FROM {tabelle} WHERE week = ?"
            merge_cols = ["first_name", "last_name"]
        elif platform == "bolt":
            check_sql = f"SELECT driver_name FROM {tabelle} WHERE week = ?"
            merge_cols = ["driver_name"]
        elif platform == "40100":
            check_sql = f"SELECT Fahrername, Abschluss FROM {tabelle} WHERE week = ?"
            merge_cols = ["Fahrername", "Abschluss"]
        elif platform == "31300":
            check_sql = f"SELECT Fahrername, Abschluss FROM {tabelle} WHERE week = ?"
            merge_cols = ["Fahrername", "Abschluss"]
        
        try:
            existing = pd.read_sql_query(check_sql, conn, params=[kalenderwoche])
            if not existing.empty:
                df = df.merge(existing, on=merge_cols, how="left", indicator=True)
                df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])
        except Exception as e:
            print(f"⚠️ Fehler bei Duplikatsprüfung: {e}")
        
        if not df.empty:
            df.to_sql(tabelle, conn, if_exists="append", index=False)
            print(f"✅ {len(df)} Zeilen importiert: {filename} → {db_path} → {tabelle}")
        else:
            print(f"ℹ️ Keine neuen Daten importiert: {filename}")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")

def main():
    """Hauptfunktion"""
    print("🚀 Intelligenter CSV-Import gestartet")
    print("=" * 50)
    
    # Dateien auswählen
    Tk().withdraw()
    dateien = askopenfilenames(
        title="CSV-Dateien auswählen", 
        filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
    )
    
    if not dateien:
        print("❌ Keine Dateien ausgewählt.")
        return
    
    print(f"📁 {len(dateien)} Datei(en) ausgewählt")
    
    # Dateien verarbeiten
    for datei in dateien:
        try:
            verarbeite_datei(datei)
        except Exception as e:
            print(f"❌ Fehler bei {Path(datei).name}: {e}")
    
    print("\n✅ Import abgeschlossen!")

if __name__ == "__main__":
    main() 