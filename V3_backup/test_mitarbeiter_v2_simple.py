#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# PySide6 Import
from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

def main():
    # QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QGuiApplication(sys.argv)
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    
    # QML-Import-Pfade setzen
    current_dir = Path(__file__).parent
    qml_import_paths = [
        str(current_dir / "Style"),
        str(current_dir),
        str(Path(sys.executable).parent / "Lib" / "site-packages" / "PySide6" / "qml")
    ]
    
    print("QML-Import-Pfade:", qml_import_paths)
    
    for path in qml_import_paths:
        engine.addImportPath(path)
    
    # QML-Datei laden
    qml_file = current_dir / "Style" / "TestMitarbeiterV2Cards.qml"
    print(f"Lade QML-Datei: {qml_file}")
    print(f"Datei existiert: {qml_file.exists()}")
    
    if not qml_file.exists():
        print("❌ QML-Datei nicht gefunden!")
        return 1
    
    # QML-Datei laden
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        print("❌ QML-Datei konnte nicht geladen werden!")
        return 1
    
    print("✅ QML-Datei erfolgreich geladen!")
    print("🚀 Test-Anwendung gestartet!")
    
    # Anwendung starten
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 