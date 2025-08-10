#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isolierter Test für das Umsatzmatching (Uber/Bolt) je Kalenderwoche.

Nutzung (Beispiele):
  python test_umsatzmatching.py --fahrer "Hersi Omar Mohamud" --kws 31
  python test_umsatzmatching.py --fahrer "Hersi Omar Mohamud" --kws 25,26,27 --top 5
  python test_umsatzmatching.py --list     # Verfügbare KWs in uber.sqlite/bolt.sqlite
"""

import os
import re
import sys
import sqlite3
import argparse
import configparser
from typing import Dict, List, Tuple

import pandas as pd


ALLOWED_TABLES = {f"report_KW{i}" for i in range(1, 53)}


def read_fuzzy_params(config_file: str = "test_config.ini") -> Dict[str, int]:
    params = {"min_match_score": 50, "max_distance": 3, "arabic_name_bonus": 20}
    try:
        if os.path.exists(config_file):
            cfg = configparser.ConfigParser()
            cfg.read(config_file, encoding="utf-8")
            if "Fuzzy_Matching" in cfg:
                sect = cfg["Fuzzy_Matching"]
                params["min_match_score"] = int(sect.get("min_match_score", params["min_match_score"]))
                params["max_distance"] = int(sect.get("max_distance", params["max_distance"]))
                params["arabic_name_bonus"] = int(sect.get("arabic_name_bonus", params["arabic_name_bonus"]))
    except Exception:
        pass
    return params


def clean_name(name: str) -> str:
    """Normalisiert Namen für robustes Matching.
    - Kleinbuchstaben, Mehrfach-Leerzeichen → ein Leerzeichen
    - Bindestriche/Unterstriche → Leerzeichen
    - 'al' Präfix → 'el' (häufige Variante)
    - Trimmt führende/trailing Spaces
    """
    s = str(name).lower()
    s = s.replace("-", " ").replace("_", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\bal\s+", "el ", s)
    s = s.strip()
    return s


def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            ins = previous_row[j + 1] + 1
            dele = current_row[j] + 1
            sub = previous_row[j] + (c1 != c2)
            current_row.append(min(ins, dele, sub))
        previous_row = current_row
    return previous_row[-1]


def fuzzy_match_score(search_name: str, target_name: str, fuzzy_params: Dict[str, int]) -> float:
    """Verbesserter Fuzzy-Score für Fahrernamen.

    Komponenten:
    - Dice-Koeffizient der Token (starker Einfluss)
    - Jaccard/Abdeckung (stärker, wenn alle Such-Tokens im Ziel enthalten sind)
    - Reihenfolge-Bonus (erster/letzter Token deckungsgleich)
    - Präfix-Bonus (beginnender Token-Match)
    - Levenshtein-Distanz (leichter Einfluss)
    - Arabisch-Bonus bei „el“-Strukturen
    """
    if not search_name or not target_name:
        return 0.0

    if search_name == target_name:
        return 100.0

    search_tokens = clean_name(search_name).split()
    target_tokens = clean_name(target_name).split()

    # Erweiterte Token-Varianten für "el"-Präfix
    def extend_el(tokens: List[str]) -> List[str]:
        ext = tokens.copy()
        for i, token in enumerate(tokens):
            if token == "el" and i + 1 < len(tokens):
                ext.append("el" + tokens[i + 1])
        return ext

    search_ext = extend_el(search_tokens)
    target_ext = extend_el(target_tokens)

    set_search = set(search_ext)
    set_target = set(target_ext)
    inter = set_search & set_target
    union = set_search | set_target

    inter_size = len(inter)
    if inter_size == 0 and levenshtein_distance(search_name, target_name) > int(fuzzy_params.get("max_distance", 3)):
        return 0.0

    # Ähnlichkeitsmaße
    dice = (2 * inter_size) / max(1, (len(set_search) + len(set_target)))  # 0..1
    jaccard = inter_size / max(1, len(union))                               # 0..1
    coverage = inter_size / max(1, len(set_search))                        # 0..1 (alle Such-Tokens enthalten?)

    # Reihenfolge-Bonus (erster/letzter Token)
    order_bonus = 0.0
    if search_tokens and target_tokens and search_tokens[0] == target_tokens[0]:
        order_bonus += 8.0
    if search_tokens and target_tokens and search_tokens[-1] == target_tokens[-1]:
        order_bonus += 8.0

    # Präfix-Bonus (z. B. "yass" ~ "yasser")
    prefix_bonus = 0.0
    for st in search_tokens:
        if any(tt.startswith(st) or st.startswith(tt) for tt in target_tokens):
            prefix_bonus += 2.0
    prefix_bonus = min(prefix_bonus, 8.0)

    # Arabisch-Bonus
    arabic_bonus = 0.0
    if any(t == "el" or t.startswith("el") for t in search_tokens) and any(t == "el" or t.startswith("el") for t in target_tokens):
        arabic_bonus = float(fuzzy_params.get("arabic_name_bonus", 20))

    # Distanz (leichter Einfluss)
    distance = levenshtein_distance(search_name, target_name)
    max_len = max(len(search_name), len(target_name))
    norm_dist = (distance / max_len) if max_len else 1.0
    distance_score = max(0.0, 100.0 - (norm_dist * 100.0)) / 100.0  # 0..1

    # Gewichtung
    base = (
        0.55 * dice +
        0.20 * coverage +
        0.10 * jaccard +
        0.15 * distance_score
    ) * 100.0

    score = base + order_bonus + prefix_bonus + arabic_bonus
    return float(max(0.0, min(100.0, score)))


def list_available_kws(db_path: str) -> List[int]:
    if not os.path.exists(db_path):
        return []
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'report_KW%' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
        conn.close()
    except Exception:
        return []
    kws = []
    for t in tables:
        kw = t.replace("report_KW", "")
        if kw.isdigit():
            kws.append(int(kw))
    return kws


def validate_table_name(kw: int) -> str:
    table = f"report_KW{kw}"
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Ungültiger Tabellenname: {table}")
    return table


def match_uber(kw: int, driver_label: str, fuzzy_params: Dict[str, int]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    db_path = os.path.abspath(os.path.join("SQL", "uber.sqlite"))
    if not os.path.exists(db_path):
        return pd.DataFrame(), {}
    table = validate_table_name(kw)
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    if df.empty or not {"first_name", "last_name"}.issubset(set(df.columns)):
        return pd.DataFrame(), {}

    search_clean = clean_name(driver_label)
    df["_combo_name"] = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).apply(clean_name)
    df["_match"] = df["_combo_name"].apply(lambda n: fuzzy_match_score(search_clean, n, fuzzy_params))

    if df["_match"].empty:
        return pd.DataFrame(), {}

    max_score = df["_match"].max()
    if max_score < int(fuzzy_params.get("min_match_score", 50)):
        return df.sort_values("_match", ascending=False), {}

    best = df[df["_match"] == max_score]
    best = best.iloc[[0]] if len(best) > 1 else best

    gross_total = float(best.get("gross_total", pd.Series([0.0])).iloc[0]) if "gross_total" in best.columns else 0.0
    cash_collected = float(best.get("cash_collected", pd.Series([0.0])).iloc[0]) if "cash_collected" in best.columns else 0.0
    tips = float(best.get("tips", pd.Series([0.0])).iloc[0]) if "tips" in best.columns else 0.0

    details = {
        "matched_name": best["_combo_name"].iloc[0],
        "score": float(max_score),
        "gross_total": gross_total,
        "cash_collected": cash_collected,
        "tips": tips,
        "echter_umsatz": gross_total  # Uber: gross_total
    }
    return df.sort_values("_match", ascending=False), details


def match_bolt(kw: int, driver_label: str, fuzzy_params: Dict[str, int]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    db_path = os.path.abspath(os.path.join("SQL", "bolt.sqlite"))
    if not os.path.exists(db_path):
        return pd.DataFrame(), {}
    table = validate_table_name(kw)
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    if df.empty or "driver_name" not in df.columns:
        return pd.DataFrame(), {}

    search_clean = clean_name(driver_label)
    df["_driver_name_clean"] = df["driver_name"].apply(clean_name)
    df["_match"] = df["_driver_name_clean"].apply(lambda n: fuzzy_match_score(search_clean, n, fuzzy_params))

    if df["_match"].empty:
        return pd.DataFrame(), {}

    max_score = df["_match"].max()
    if max_score < int(fuzzy_params.get("min_match_score", 50)):
        return df.sort_values("_match", ascending=False), {}

    best = df[df["_match"] == max_score]
    best = best.iloc[[0]] if len(best) > 1 else best

    net_earnings = float(best.get("net_earnings", pd.Series([0.0])).iloc[0]) if "net_earnings" in best.columns else 0.0
    rider_tips = float(best.get("rider_tips", pd.Series([0.0])).iloc[0]) if "rider_tips" in best.columns else 0.0
    cash_collected = float(best.get("cash_collected", pd.Series([0.0])).iloc[0]) if "cash_collected" in best.columns else 0.0
    echter_umsatz = net_earnings - rider_tips

    details = {
        "matched_name": best["_driver_name_clean"].iloc[0],
        "score": float(max_score),
        "net_earnings": net_earnings,
        "rider_tips": rider_tips,
        "cash_collected": cash_collected,
        "echter_umsatz": echter_umsatz
    }
    return df.sort_values("_match", ascending=False), details


def main():
    parser = argparse.ArgumentParser(description="Isolierter Umsatzmatching-Test (Uber/Bolt)")
    parser.add_argument("--fahrer", required=False, default="", help="Fahrername für Matching")
    parser.add_argument("--kws", required=False, default="", help="Kommagetrennte KW-Liste, z. B. 25,26,31")
    parser.add_argument("--top", type=int, default=5, help="Top-N Kandidaten mit Score anzeigen")
    parser.add_argument("--list", action="store_true", help="Verfügbare KWs in uber.sqlite/bolt.sqlite anzeigen")
    args = parser.parse_args()

    if args.list:
        uber_kws = list_available_kws(os.path.join("SQL", "uber.sqlite"))
        bolt_kws = list_available_kws(os.path.join("SQL", "bolt.sqlite"))
        print("Verfügbare KWs:")
        print(f"  Uber: {sorted(uber_kws)}")
        print(f"  Bolt: {sorted(bolt_kws)}")
        return

    if not args.fahrer or not args.kws:
        print("Bitte --fahrer und --kws angeben (oder --list verwenden).")
        sys.exit(1)

    try:
        kws = [int(x.strip()) for x in args.kws.split(",") if x.strip()]
    except Exception:
        print("Ungültiges --kws Format. Beispiel: --kws 25,26,31")
        sys.exit(1)

    fuzzy_params = read_fuzzy_params()
    print("Fuzzy-Parameter:")
    print(f"  min_match_score = {fuzzy_params['min_match_score']}")
    print(f"  max_distance    = {fuzzy_params['max_distance']}")
    print(f"  arabic_bonus    = {fuzzy_params['arabic_name_bonus']}")
    print()

    total_uber = 0.0
    total_bolt = 0.0
    for kw in kws:
        print(f"KW {kw:02d}:")
        # Uber
        uber_df, uber = match_uber(kw, args.fahrer, fuzzy_params)
        if uber:
            print(f"  ✅ Uber-Match: '{clean_name(args.fahrer)}' → '{uber['matched_name']}' (Score: {uber['score']:.1f})")
            print(f"     gross_total={uber['gross_total']:.2f}€  cash_collected={uber['cash_collected']:.2f}€  tips={uber['tips']:.2f}€")
            print(f"     Echter Umsatz (Uber) = {uber['echter_umsatz']:.2f}€")
            total_uber += uber['echter_umsatz']
        else:
            print("  ⚠️  Kein ausreichender Uber-Match")
        if not uber_df.empty:
            print("  Top-Kandidaten (Uber):")
            for i, row in uber_df.head(args.top).iterrows():
                label = row.get("_combo_name", "?")
                print(f"    - {label:<30} Score={row['_match']:.1f}")

        # Bolt
        bolt_df, bolt = match_bolt(kw, args.fahrer, fuzzy_params)
        if bolt:
            print(f"  ✅ Bolt-Match: '{clean_name(args.fahrer)}' → '{bolt['matched_name']}' (Score: {bolt['score']:.1f})")
            print(f"     net_earnings={bolt['net_earnings']:.2f}€  rider_tips={bolt['rider_tips']:.2f}€  cash_collected={bolt['cash_collected']:.2f}€")
            print(f"     Echter Umsatz (Bolt) = {bolt['echter_umsatz']:.2f}€")
            total_bolt += bolt['echter_umsatz']
        else:
            print("  ⚠️  Kein ausreichender Bolt-Match")
        if not bolt_df.empty:
            print("  Top-Kandidaten (Bolt):")
            for i, row in bolt_df.head(args.top).iterrows():
                label = row.get("_driver_name_clean", "?")
                print(f"    - {label:<30} Score={row['_match']:.1f}")

        print()

    print("Gesamtsummen über angegebene KWs:")
    print(f"  Uber (echter Umsatz) = {total_uber:.2f}€")
    print(f"  Bolt (echter Umsatz) = {total_bolt:.2f}€")
    print(f"  Summe                = {total_uber + total_bolt:.2f}€")


if __name__ == "__main__":
    main()


