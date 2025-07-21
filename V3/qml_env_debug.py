import sys
import os
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

print("Python-Interpreter:", sys.executable)
print("Python-Version:", sys.version)
print("Arbeitsverzeichnis:", os.getcwd())
print("--- Umgebungsvariablen ---")
for k, v in os.environ.items():
    print(f"{k}={v}")
print("--------------------------")

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()

# Importpfade ausgeben
print("QML-Importpfade:", engine.importPathList())

# Importpfad für Style explizit setzen
style_path = os.path.join(os.path.dirname(__file__), "Style")
engine.addImportPath(style_path)
print("QML-Importpfade nach addImportPath:", engine.importPathList())

# Test: Lade das Style-Modul
try:
    from PySide6.QtCore import QUrl
    qml_file = os.path.join(style_path, "MainMenu.qml")
    print("Lade QML-Datei:", qml_file)
    engine.load(QUrl.fromLocalFile(qml_file))
    if not engine.rootObjects():
        print("[ERROR] QML konnte nicht geladen werden!")
    else:
        print("QML erfolgreich geladen!")
except Exception as e:
    print("[ERROR] Ausnahme beim Laden der QML:", e)
    import traceback; traceback.print_exc() 