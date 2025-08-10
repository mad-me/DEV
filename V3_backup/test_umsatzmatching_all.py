#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isolierter Matching-Gesamttest für ALLE Fahrer und ALLE Plattformen pro Kalenderwoche.

Erzeugt einen CSV-Audit-Report mit einem Eintrag pro (Fahrer, KW, Plattform).

Nutzung (Beispiele):
  python test_umsatzmatching_all.py --export matching_audit.csv
  python test_umsatzmatching_all.py --min-score 55 --top 3 --export matching_audit.csv

Hinweise:
- Fuzzy-Parameter werden aus test_config.ini (Sektion [Fuzzy_Matching]) gelesen, falls vorhanden
- Fahrer werden vorrangig aus 'database.db' (Tabelle drivers) geladen, Fallback: 'SQL/database.db' oder 'deals.name'
- Verfügbare KWs werden aus allen vorhandenen Files (uber.sqlite, bolt.sqlite, 40100.sqlite, 31300.sqlite) ermittelt (Union)
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

# Re-Use Matching Logik aus dem Einzelskript
from test_umsatzmatching import (
    read_fuzzy_params,
    list_available_kws,
    clean_name,
    fuzzy_match_score,
    match_uber,
    match_bolt,
)


ALLOWED_TABLES = {f"report_KW{i}" for i in range(1, 53)}

# Plattform → DB-Datei Mapping
PLATFORM_TO_DB = {
    "Uber": "uber.sqlite",
    "Bolt": "bolt.sqlite",
    "40100": "40100.sqlite",
    "31300": "31300.sqlite",
}


def safe_exists(path: str) -> bool:
    try:
        return os.path.exists(path)
    except Exception:
        return False


def load_driver_labels() -> List[str]:
    """Lädt Fahrernamen ("first last").

    Reihenfolge der Versuche:
    1) Root 'database.db' → SELECT first_name,last_name FROM drivers
    2) 'SQL/database.db'  → SELECT first_name,last_name FROM drivers
    3) 'SQL/database.db'  → SELECT name FROM deals
    """
    candidates: List[str] = []

    def _try_db(db_path: str) -> Optional[List[str]]:
        try:
            if not safe_exists(db_path):
                return None
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # bevorzugt drivers
            try:
                cur.execute("SELECT first_name, last_name FROM drivers")
                rows = cur.fetchall()
                conn.close()
                if rows:
                    return [f"{(r[0] or '').strip()} {(r[1] or '').strip()}".strip() for r in rows if (r and (r[0] or r[1]))]
            except Exception:
                pass

            # fallback deals.name
            try:
                cur.execute("SELECT name FROM deals")
                rows = cur.fetchall()
                conn.close()
                if rows:
                    return [str(r[0]).strip() for r in rows if r and r[0]]
            except Exception:
                pass

            try:
                conn.close()
            except Exception:
                pass
        except Exception:
            return None
        return None

    # 1) Root DB
    labels = _try_db(os.path.abspath("database.db"))
    if labels:
        candidates.extend(labels)

    # 2) SQL/database.db
    if not candidates:
        labels = _try_db(os.path.abspath(os.path.join("SQL", "database.db")))
        if labels:
            candidates.extend(labels)

    # Bereinigen und einzigartige, nicht leere Namen
    result = []
    seen = set()
    for name in candidates:
        n = " ".join(str(name).split()).strip()
        if n and n.lower() not in seen:
            result.append(n)
            seen.add(n.lower())
    return result


def list_available_kws_union(selected_platforms: List[str]) -> List[int]:
    """Union aller KWs aus den vorhandenen Plattform-DBs, gefiltert nach ausgewählten Plattformen."""
    kws: set[int] = set()
    for plat in selected_platforms:
        db = PLATFORM_TO_DB.get(plat)
        if not db:
            continue
        db_path = os.path.abspath(os.path.join("SQL", db))
        kws.update(list_available_kws(db_path))
    return sorted(kws)


def validate_table_name(kw: int) -> str:
    table = f"report_KW{kw}"
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Ungültiger Tabellenname: {table}")
    return table


def match_40100(kw: int, driver_label: str, fuzzy_params: Dict[str, int]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Fuzzy-Match gegen 40100 nach Fahrername/Fahrer und Berechnung 'echter Umsatz'."""
    db_path = os.path.abspath(os.path.join("SQL", "40100.sqlite"))
    if not safe_exists(db_path):
        return pd.DataFrame(), {}
    table = validate_table_name(kw)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cur.fetchone() is None:
            return pd.DataFrame(), {}
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    finally:
        conn.close()
    if df.empty:
        return pd.DataFrame(), {}

    search_clean = clean_name(driver_label)
    name_col = None
    for cand in ("Fahrername", "Fahrer"):
        if cand in df.columns:
            name_col = cand
            break
    if not name_col:
        return pd.DataFrame(), {}

    df["_name_clean"] = df[name_col].fillna("").astype(str).apply(clean_name)
    df["_match"] = df["_name_clean"].apply(lambda n: fuzzy_match_score(search_clean, n, fuzzy_params))

    if df["_match"].empty:
        return pd.DataFrame(), {}

    max_score = df["_match"].max()
    if max_score < int(fuzzy_params.get("min_match_score", 50)):
        return df.sort_values("_match", ascending=False), {}

    best = df[df["_match"] == max_score]
    best = best.iloc[[0]] if len(best) > 1 else best

    # Echter Umsatz: Umsatz - Trinkgeld (falls vorhanden)
    umsatz = 0.0
    trinkgeld = 0.0
    if "Umsatz" in best.columns:
        try:
            umsatz = pd.to_numeric(best["Umsatz"], errors="coerce").fillna(0).sum()
        except Exception:
            umsatz = 0.0
    if "Trinkgeld" in best.columns:
        try:
            trinkgeld = pd.to_numeric(best["Trinkgeld"], errors="coerce").fillna(0).sum()
        except Exception:
            trinkgeld = 0.0

    details = {
        "matched_name": best["_name_clean"].iloc[0],
        "score": float(max_score),
        "echter_umsatz": float(umsatz - trinkgeld),
        "bargeld": float(pd.to_numeric(best.get("Bargeld", pd.Series([0.0])), errors="coerce").fillna(0).sum()) if "Bargeld" in best.columns else 0.0,
        "trinkgeld": float(trinkgeld),
    }
    return df.sort_values("_match", ascending=False), details


def match_31300(kw: int, driver_label: str, fuzzy_params: Dict[str, int]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Fuzzy-Match gegen 31300 nach Fahrername/Fahrer und Berechnung 'echter Umsatz'."""
    db_path = os.path.abspath(os.path.join("SQL", "31300.sqlite"))
    if not safe_exists(db_path):
        return pd.DataFrame(), {}
    table = validate_table_name(kw)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cur.fetchone() is None:
            return pd.DataFrame(), {}
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    finally:
        conn.close()
    if df.empty:
        return pd.DataFrame(), {}

    search_clean = clean_name(driver_label)
    name_col = None
    for cand in ("Fahrername", "Fahrer"):
        if cand in df.columns:
            name_col = cand
            break
    if not name_col:
        return pd.DataFrame(), {}

    df["_name_clean"] = df[name_col].fillna("").astype(str).apply(clean_name)
    df["_match"] = df["_name_clean"].apply(lambda n: fuzzy_match_score(search_clean, n, fuzzy_params))

    if df["_match"].empty:
        return pd.DataFrame(), {}

    max_score = df["_match"].max()
    if max_score < int(fuzzy_params.get("min_match_score", 50)):
        return df.sort_values("_match", ascending=False), {}

    best = df[df["_match"] == max_score]
    best = best.iloc[[0]] if len(best) > 1 else best

    # Echter Umsatz: Gesamt - Trinkgeld (falls vorhanden)
    gesamt = 0.0
    trinkgeld = 0.0
    if "Gesamt" in best.columns:
        try:
            gesamt = pd.to_numeric(best["Gesamt"], errors="coerce").fillna(0).sum()
        except Exception:
            gesamt = 0.0
    if "Trinkgeld" in best.columns:
        try:
            trinkgeld = pd.to_numeric(best["Trinkgeld"], errors="coerce").fillna(0).sum()
        except Exception:
            trinkgeld = 0.0

    details = {
        "matched_name": best["_name_clean"].iloc[0],
        "score": float(max_score),
        "echter_umsatz": float(gesamt - trinkgeld),
        "bargeld": float(pd.to_numeric(best.get("Gesamt", pd.Series([0.0])), errors="coerce").fillna(0).sum()) if "Gesamt" in best.columns else 0.0,
        "trinkgeld": float(trinkgeld),
    }
    return df.sort_values("_match", ascending=False), details


def run_audit(min_score: int, top_n: int, export_path: Optional[str], selected_platforms: Optional[List[str]] = None) -> pd.DataFrame:
    fuzzy_params = read_fuzzy_params()
    # Overwrite Mindestscore via CLI
    fuzzy_params["min_match_score"] = int(min_score)

    drivers = load_driver_labels()
    if not drivers:
        print("⚠️ Keine Fahrer gefunden (drivers/deals). Abbruch.")
        return pd.DataFrame()

    selected_platforms = selected_platforms or ["Uber", "Bolt", "40100", "31300"]
    # Normalisiere Schreibweise
    selected_platforms = [p.strip() for p in selected_platforms if p.strip() in PLATFORM_TO_DB]
    if not selected_platforms:
        print("⚠️ Keine gültigen Plattformen ausgewählt. Abbruch.")
        return pd.DataFrame()

    kws = list_available_kws_union(selected_platforms)
    if not kws:
        print("⚠️ Keine Kalenderwochen in Plattform-DBs gefunden. Abbruch.")
        return pd.DataFrame()

    print(f"Fahrer: {len(drivers)} | KWs: {len(kws)}")

    rows: List[Dict[str, object]] = []

    def _append(platform: str, driver: str, kw: int, details: Dict[str, float], best_df: pd.DataFrame, error: str = ""):
        if details:
            rows.append({
                "kw": kw,
                "platform": platform,
                "driver": driver,
                "matched_name": details.get("matched_name", ""),
                "score": details.get("score", 0.0),
                "echter_umsatz": details.get("echter_umsatz", 0.0),
                "bargeld": details.get("bargeld", 0.0),
                "trinkgeld": details.get("trinkgeld", 0.0),
                "status": "OK",
                "error": error,
            })
        else:
            # Kein ausreichender Match – optional top-N Kandidaten protokollieren (nur Anzeige)
            top_preview = []
            if isinstance(best_df, pd.DataFrame) and not best_df.empty:
                col = "_combo_name" if "_combo_name" in best_df.columns else ("_driver_name_clean" if "_driver_name_clean" in best_df.columns else ("_name_clean" if "_name_clean" in best_df.columns else None))
                if col:
                    for _, r in best_df.head(top_n).iterrows():
                        try:
                            top_preview.append(f"{r.get(col, '?')}|{r.get('_match', 0):.1f}")
                        except Exception:
                            pass
            rows.append({
                "kw": kw,
                "platform": platform,
                "driver": driver,
                "matched_name": "",
                "score": 0.0,
                "echter_umsatz": 0.0,
                "bargeld": 0.0,
                "trinkgeld": 0.0,
                "status": "NO_MATCH",
                "error": error,
                "candidates": ", ".join(top_preview) if top_preview else "",
            })

    for driver in drivers:
        driver_label = " ".join(str(driver).split())
        print(f"→ Prüfe Fahrer: {driver_label}")
        for kw in kws:
            # Uber
            if "Uber" in selected_platforms:
                try:
                    uber_df, uber_details = match_uber(kw, driver_label, fuzzy_params)
                    _append("Uber", driver_label, kw, uber_details, uber_df)
                except Exception as e:
                    _append("Uber", driver_label, kw, {}, pd.DataFrame(), error=str(e))

            # Bolt
            if "Bolt" in selected_platforms:
                try:
                    bolt_df, bolt_details = match_bolt(kw, driver_label, fuzzy_params)
                    _append("Bolt", driver_label, kw, bolt_details, bolt_df)
                except Exception as e:
                    _append("Bolt", driver_label, kw, {}, pd.DataFrame(), error=str(e))

            # 40100
            if "40100" in selected_platforms:
                try:
                    df_40100, det_40100 = match_40100(kw, driver_label, fuzzy_params)
                    _append("40100", driver_label, kw, det_40100, df_40100)
                except Exception as e:
                    _append("40100", driver_label, kw, {}, pd.DataFrame(), error=str(e))

            # 31300
            if "31300" in selected_platforms:
                try:
                    df_31300, det_31300 = match_31300(kw, driver_label, fuzzy_params)
                    _append("31300", driver_label, kw, det_31300, df_31300)
                except Exception as e:
                    _append("31300", driver_label, kw, {}, pd.DataFrame(), error=str(e))

    report = pd.DataFrame(rows)
    if not report.empty:
        # Spaltenreihenfolge
        cols = [
            "kw", "platform", "driver", "matched_name", "score",
            "echter_umsatz", "bargeld", "trinkgeld", "status", "error", "candidates",
        ]
        for c in cols:
            if c not in report.columns:
                report[c] = None
        report = report[cols]

        if export_path:
            try:
                report.to_csv(export_path, index=False, encoding="utf-8")
                print(f"✅ Report gespeichert: {export_path} ({len(report)} Zeilen)")
            except Exception as e:
                print(f"❌ Konnte Report nicht speichern: {e}")
    else:
        print("ℹ️ Kein Inhalt für den Report erzeugt.")
    return report


def main():
    parser = argparse.ArgumentParser(description="Isolierter Matching-Gesamttest (alle Fahrer × alle Plattformen × KWs)")
    parser.add_argument("--min-score", type=int, default=50, help="Mindestscore für akzeptierten Match (Default: 50)")
    parser.add_argument("--top", type=int, default=5, help="Top-N Kandidaten bei NO_MATCH in candidates anzeigen")
    parser.add_argument("--export", type=str, default="", help="Pfad zur CSV-Ausgabe")
    parser.add_argument("--platforms", type=str, default="Uber,Bolt,40100,31300", help="Kommagetrennte Liste der zu prüfenden Plattformen (z. B. 'Uber,Bolt')")
    args = parser.parse_args()

    export_path = args.export if args.export else None
    selected_platforms = [p.strip() for p in args.platforms.split(',') if p.strip()]
    run_audit(min_score=args.min_score, top_n=args.top, export_path=export_path, selected_platforms=selected_platforms)


if __name__ == "__main__":
    main()


