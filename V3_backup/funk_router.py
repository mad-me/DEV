import sys
import os
import subprocess
from pathlib import Path


def is_31300_csv(name: str) -> bool:
    n = name.lower()
    return "31300" in n


def is_40100_csv(name: str) -> bool:
    n = name.lower()
    return ("40100" in n) or ("taxi" in n and "31300" not in n)


def run_cmd(args, cwd=None):
    proc = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print(line.rstrip())
    return proc.wait()


def handle_pdf(pdf_file: str) -> int:
    """PDF-Verarbeitung: zuerst SQL/Scanner.py versuchen, dann Fallback auf import_funk.py."""
    base_dir = Path(__file__).resolve().parent
    sql_dir = base_dir / "SQL"
    scanner = sql_dir / "Scanner.py"

    if scanner.exists():
        print(f"[INFO] Versuche Scanner.py für PDF: {pdf_file}")
        rc = run_cmd([sys.executable, str(scanner), pdf_file], cwd=str(sql_dir))
        if rc == 0:
            return 0
        print(f"[WARN] Scanner.py schlug fehl (rc={rc}) – Fallback auf import_funk.py")

    # Fallback auf minimalen Funk-Import für Monatswerte
    funk_db = str(sql_dir / "funk.db")
    vehicles_db = str(sql_dir / "database.db")
    import_funk = base_dir / "import_funk.py"
    return run_cmd([sys.executable, str(import_funk), pdf_file, funk_db, vehicles_db], cwd=str(base_dir))


def handle_csv(csv_file: str) -> int:
    name = os.path.basename(csv_file)
    base_dir = str(Path(__file__).resolve().parent / "SQL")

    if is_31300_csv(name):
        print(f"[INFO] Erkannt: 31300 CSV – verwende import_31300.py")
        return run_cmd([sys.executable, os.path.join(base_dir, "import_31300.py"), csv_file], cwd=base_dir)
    elif is_40100_csv(name):
        print(f"[INFO] Erkannt: 40100 CSV – verwende smart_import.py")
        return run_cmd([sys.executable, os.path.join(base_dir, "smart_import.py"), csv_file], cwd=base_dir)
    else:
        print(f"[INFO] Unbekanntes CSV-Format – versuche smart_import.py (Auto-Erkennung)")
        return run_cmd([sys.executable, os.path.join(base_dir, "smart_import.py"), csv_file], cwd=base_dir)


def main():
    if len(sys.argv) < 2:
        print("[FEHLER] Nutzung: python funk_router.py <datei1> [datei2 ...]")
        sys.exit(2)

    exit_code = 0
    for f in sys.argv[1:]:
        if not os.path.exists(f):
            print(f"[FEHLER] Datei nicht gefunden: {f}")
            exit_code = 1
            continue
        ext = Path(f).suffix.lower()
        try:
            if ext == ".pdf":
                rc = handle_pdf(f)
            elif ext == ".csv":
                rc = handle_csv(f)
            else:
                print(f"[FEHLER] Nicht unterstützte Datei (nur PDF/CSV): {f}")
                rc = 1
            if rc != 0:
                exit_code = rc
        except Exception as e:
            print(f"[FEHLER] Verarbeitung fehlgeschlagen für {f}: {e}")
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()


