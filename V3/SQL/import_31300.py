import sqlite3
import pandas as pd
import re
from pathlib import Path
from tkinter.filedialog import askopenfilenames
from tkinter import Tk
import sys

def verarbeite_datei(csv_datei):
    filename = Path(csv_datei).name.lower()

    # === Nur 31300-Dateien verarbeiten
    if "31300" in filename:
        db_name = "31300.sqlite"
        platform = "31300"
    else:
        print(f"⚠️ Keine 31300-Datei: {filename} – übersprungen.")
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

    # === Spalten wie bei 40100 behandeln
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

    df = df[[col for col in zielspalten if col in df.columns]]

    # === Verbindung zur Datenbank
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # === Tabelle anlegen, wenn nicht vorhanden
    create_sql = f"""
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
    """
    cursor.execute(create_sql)

    # === Duplikate prüfen
    check_sql = f"SELECT Fahrername, Abschluss FROM {tabelle} WHERE week = ?"
    merge_cols = ["Fahrername", "Abschluss"]

    try:
        existing = pd.read_sql_query(check_sql, conn, params=[kalenderwoche])
        if not existing.empty:
            df = df.merge(existing, on=merge_cols, how="left", indicator=True)
            df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])
    except:
        pass

    if not df.empty:
        df.to_sql(tabelle, conn, if_exists="append", index=False)
        print(f"✅ {len(df)} Zeilen importiert: {filename} → {db_name} → {tabelle}")
    else:
        print(f"ℹ️ Keine neuen Daten importiert: {filename}")

    conn.commit()
    conn.close()

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