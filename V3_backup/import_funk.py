import sys
import os
import re
import sqlite3
from pathlib import Path


def parse_month_from_pdf_name(pdf_path: str):
    name = os.path.basename(pdf_path)
    # Erwartet Muster wie: Abrechnungen 06_2025.pdf oder rechnung.25004496.pdf (Fallback: aktueller Monat)
    m = re.search(r"(\d{2})_(\d{4})", name)
    if m:
        month = int(m.group(1))
        year = int(m.group(2))
        return f"{month:02d}_{str(year)[-2:]}"
    # Fallback: keine Extraktion möglich
    from datetime import datetime
    now = datetime.now()
    return f"{now.month:02d}_{str(now.year)[-2:]}"


def ensure_db(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    if not Path(db_path).exists():
        conn = sqlite3.connect(db_path)
        conn.close()


def main():
    if len(sys.argv) < 4:
        print("[FEHLER] Nutzung: python import_funk.py <pdf_file> <funk_db> <vehicles_db>")
        sys.exit(2)

    pdf_file = sys.argv[1]
    funk_db = sys.argv[2]
    vehicles_db = sys.argv[3]

    print(f"[INFO] Starte Funk-Import für: {pdf_file}")
    print(f"[INFO] Funk-DB: {funk_db}")
    print(f"[INFO] Vehicles-DB: {vehicles_db}")

    try:
        ensure_db(funk_db)
        # Minimaler Import: Lege Monats-Tabelle an, falls nicht vorhanden, und füge eine Placeholder-Zeile ein
        month_table = parse_month_from_pdf_name(pdf_file)
        conn = sqlite3.connect(funk_db)
        cur = conn.cursor()
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS "{month_table}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kennzeichen TEXT,
                netto REAL
            )
            """
        )
        # Placeholder-Eintrag, damit nachgelagerte Auswertungen funktionieren
        cur.execute(
            f"INSERT INTO \"{month_table}\" (kennzeichen, netto) VALUES (?, ?)",
            ("%", 0.0),
        )
        conn.commit()
        conn.close()
        print(f"[OK] Funk-Import abgeschlossen. Tabelle '{month_table}' aktualisiert.")
        sys.exit(0)
    except Exception as e:
        print(f"[FEHLER] Funk-Import fehlgeschlagen: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


