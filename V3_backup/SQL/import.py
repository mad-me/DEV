import sqlite3
import pandas as pd
import re
from pathlib import Path
from tkinter.filedialog import askopenfilenames
from tkinter import Tk
import sys

# === NEU: Fahrermatching-Funktionen ===
def lade_fahrerliste():
    db_path = Path(__file__).resolve().parent / "database.db"
    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql_query("SELECT first_name, last_name FROM drivers", conn)
    conn.close()
    return df.apply(lambda row: f"{row['first_name']} {row['last_name']}", axis=1).tolist()

def match_name(import_name, fahrerliste):
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

def verarbeite_datei(csv_datei):
    filename = Path(csv_datei).name.lower()

    # === Plattform erkennen
    if "uber" in filename:
        db_name = "uber.sqlite"
        platform = "uber"
    elif "bolt" in filename:
        db_name = "bolt.sqlite"
        platform = "bolt"
    elif "40100" in filename or "taxi" in filename:
        db_name = "40100.sqlite"
        platform = "40100"
    elif "31300" in filename:
        db_name = "31300.sqlite"
        platform = "31300"
    else:
        print(f"⚠️ Plattform für Datei {filename} nicht erkannt – übersprungen.")
        return

    # === Kalenderwoche erkennen
    match = re.search(r"kw(\d+)", filename)
    if not match:
        print(f"⚠️ Keine Kalenderwoche im Dateinamen {filename} gefunden – übersprungen.")
        return
    kw = match.group(1)
    tabelle = f"report_KW{kw}"
    kalenderwoche = f"KW{kw}"

    # === Trennzeichen erkennen
    with open(csv_datei, "r", encoding="utf-8") as f:
        header = f.readline()
        sep = ";" if header.count(";") > header.count(",") else ","

    # === CSV laden
    df = pd.read_csv(csv_datei, sep=sep)
    df.columns = df.columns.str.strip()
    df["week"] = kalenderwoche

    # === Plattform-spezifisch: Spalten umbenennen + bereinigen
    if platform == "uber":
        df.rename(columns={
            "Vorname des Fahrers": "first_name",
            "Nachname des Fahrers": "last_name",
            "Gesamtumsätze": "gross_total",
            "Umsätze/Std": "gross_per_hour",
            "Eingenommenes Bargeld": "cash_collected",
            "Stunden online": "hours_online",
            "Stunden Fahrtzeit": "drive_time",
            "Unternommene Fahrten": "total_trips",
            "Annahmerate": "acceptance_rate"
        }, inplace=True)
        zielspalten = [
            "first_name", "last_name", "gross_total", "gross_per_hour",
            "cash_collected", "hours_online", "drive_time",
            "total_trips", "acceptance_rate", "week"
        ]
        # === Fahrermatching für Uber ===
        fahrerliste = lade_fahrerliste()
        df["import_name"] = df["first_name"].fillna("") + " " + df["last_name"].fillna("")
        df["name"] = df["import_name"].apply(lambda n: match_name(n, fahrerliste))
        df.drop(columns=["import_name"], inplace=True)

    elif platform == "bolt":

        df.rename(columns={

            "Driver": "driver_name",
            "Gross earnings (total)|€": "gross_total",
            "Net earnings|€": "net_earnings",
            "Gross earnings per hour|€/h": "gross_per_hour",
            "Net earnings per hour|€/h": "net_per_hour",
            "Rider tips|€": "rider_tips",
            "Collected cash|€": "cash_collected"

        }, inplace=True)

        zielspalten = [
            "driver_name", "gross_total", "net_earnings",
            "gross_per_hour", "net_per_hour", "rider_tips",
            "cash_collected", "week"
        ]
        # === Fahrermatching für Bolt ===
        fahrerliste = lade_fahrerliste()
        df["name"] = df["driver_name"].apply(lambda n: match_name(n, fahrerliste))

    elif platform == "40100":
        zielspalten = [
            "Fahrzeug", "Fahrer", "Fahrername", "Abschluss", "Buchungsart",
            "Zahlungsmittel", "Belegtext", "Fahrtkosten", "Trinkgeld", "Umsatz",
            "Bargeld", "Auftragsart", "Status", "week"
        ]
        for col in ["Fahrtkosten", "Trinkgeld", "Umsatz", "Bargeld"]:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                    .str.replace(",", ".")
                    .str.replace(" ", "")
                    .replace("nan", None)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")
    elif platform == "31300":
        zielspalten = [
            "Fahrzeug", "Fahrer", "Fahrername", "Abschluss", "Beleg", "Zeitpunkt", "Leistung", "Tour",
            "Buchungsart", "Zahlungsmittel", "Belegtext", "Gesamt", "Kst", "10%", "20%", "Fahrtkosten",
            "Trinkgeld", "Auftragsart", "Status", "Bemerkung", "week"
        ]
        for col in ["Fahrtkosten", "Trinkgeld", "Gesamt", "10%", "20%"]:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                    .str.replace(",", ".")
                    .str.replace(" ", "")
                    .replace("nan", None)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[[col for col in zielspalten if col in df.columns]]

    # === Verbindung zur Datenbank
    db_path = Path(__file__).resolve().parent / db_name
    print(f"Importiere in Datenbank: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Prüfen, ob die Tabelle schon existiert
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabelle,))
    if cursor.fetchone():
        print(f"⚠️ Tabelle {tabelle} existiert bereits in {db_name} – Import übersprungen.")
        conn.close()
        return

    # === Tabelle anlegen, wenn nicht vorhanden
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
    cursor.execute(create_sql[platform])

    # Duplikatprüfung entfernt: Es werden alle Zeilen importiert

    if not df.empty:
        df.to_sql(tabelle, conn, if_exists="append", index=False)
        print(f"✅ {len(df)} Zeilen importiert: {filename} → {db_name} → {tabelle}")
    else:
        print(f"ℹ️ Keine neuen Daten importiert: {filename}")

    conn.commit()
    conn.close()

# === Automatischer Import ===
def main():
    if len(sys.argv) > 1:
        # Datei(en) als Argument übergeben
        for datei in sys.argv[1:]:
            verarbeite_datei(datei)
    else:
        # Alle CSVs im temp-Ordner importieren
        temp_dir = Path(__file__).resolve().parent / "temp"
        for fpath in temp_dir.glob("*.csv"):
            if fpath.is_file():
                verarbeite_datei(str(fpath))

if __name__ == "__main__":
    main()
