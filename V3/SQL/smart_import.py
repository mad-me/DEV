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
    # Verschiedene Formate unterstützen
    patterns = [
        r"kw(\d+)",           # kw23
        r"woche(\d+)",        # woche23
        r"week(\d+)",         # week23
        r"(\d{2})",           # 23 (alleinstehend)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename.lower())
        if match:
            return match.group(1)
    
    return None

def verarbeite_uber_daten(df, kalenderwoche):
    """Verarbeitet Uber-Daten"""
    print("🔍 Erkenne Uber-Format...")
    
    # Spalten-Mapping
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
    
    # Zielspalten definieren
    zielspalten = [
        "first_name", "last_name", "gross_total", "gross_per_hour",
        "cash_collected", "hours_online", "drive_time",
        "total_trips", "acceptance_rate"
    ]
    
    # Nur vorhandene Spalten behalten
    df = df[[col for col in zielspalten if col in df.columns]].copy()
    
    # Fahrermatching (nur für interne Verarbeitung, nicht für DB)
    fahrerliste = lade_fahrerliste()
    if "first_name" in df.columns and "last_name" in df.columns:
        df["import_name"] = df["first_name"].fillna("") + " " + df["last_name"].fillna("")
        matched_names = df["import_name"].apply(lambda n: match_name(n, fahrerliste))
        print(f"   Fahrermatching: {len(matched_names[matched_names != ''])} von {len(df)} Fahrern gematcht")
        df.drop(columns=["import_name"], inplace=True)
    
    df["week"] = kalenderwoche
    return df, "uber.sqlite"

def verarbeite_bolt_daten(df, kalenderwoche):
    """Verarbeitet Bolt-Daten"""
    print("🔍 Erkenne Bolt-Format...")
    
    # Spalten-Mapping
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
    
    # Zielspalten definieren
    zielspalten = [
        "driver_name", "gross_total", "net_earnings",
        "gross_per_hour", "net_per_hour", "rider_tips", "cash_collected"
    ]
    
    # Nur vorhandene Spalten behalten
    df = df[[col for col in zielspalten if col in df.columns]].copy()
    
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
    }
    
    cursor = conn.cursor()
    cursor.execute(create_sql[platform])

def verarbeite_datei(csv_datei):
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
    
    # Plattform erkennen
    platform = erkenne_plattform_aus_spalten(df)
    if not platform:
        print(f"⚠️ Plattform für {filename} nicht erkannt")
        print(f"   Verfügbare Spalten: {list(df.columns)}")
        return
    
    print(f"✅ Plattform erkannt: {platform}")
    
    # Daten verarbeiten
    if platform == "uber":
        df, db_name = verarbeite_uber_daten(df, kalenderwoche)
    elif platform == "bolt":
        df, db_name = verarbeite_bolt_daten(df, kalenderwoche)
    elif platform == "40100":
        df, db_name = verarbeite_40100_daten(df, kalenderwoche)
    
    # In Datenbank speichern
    try:
        conn = sqlite3.connect(db_name)
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
        
        try:
            existing = pd.read_sql_query(check_sql, conn, params=[kalenderwoche])
            if not existing.empty:
                df = df.merge(existing, on=merge_cols, how="left", indicator=True)
                df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])
        except Exception as e:
            print(f"⚠️ Fehler bei Duplikatsprüfung: {e}")
        
        if not df.empty:
            df.to_sql(tabelle, conn, if_exists="append", index=False)
            print(f"✅ {len(df)} Zeilen importiert: {filename} → {db_name} → {tabelle}")
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