import os
import sys

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from PySide6.QtQuickControls2 import QQuickStyle

from datenseite_v3 import DatenSeiteQMLV3, DatenSeiteStub


def main():
    # Arbeitsverzeichnis auf Skriptverzeichnis setzen
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Qt Quick Controls Style setzen
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    # QML-Debug aktivieren, um Ladeprobleme sichtbar zu machen
    os.environ["QML_IMPORT_TRACE"] = "1"
    os.environ["QT_LOGGING_RULES"] = "qt.qml=true;qt.quick=true;qt.scenegraph=true"
    QQuickStyle.setStyle("Basic")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    engine = QQmlApplicationEngine()

    # QML Import-Pfade
    style_path = os.path.join(os.getcwd(), "Style")
    engine.addImportPath(os.getcwd())
    engine.addImportPath(".")
    engine.addImportPath(style_path)

    # Backend registrieren
    use_live = "--live" in sys.argv
    daten_backend_v3 = DatenSeiteQMLV3() if use_live and 'DatenSeiteQMLV3' in globals() else DatenSeiteStub()
    print(f"Backend: {'LIVE' if isinstance(daten_backend_v3, DatenSeiteQMLV3) else 'STUB'}")
    engine.rootContext().setContextProperty("datenBackend", daten_backend_v3)

    # QML laden (isoliert)
    # FallBack: einfache Test-Window laden, um Renderfähigkeit sicherzustellen
    qml_file = os.path.join(style_path, "DatenseiteV3.qml")
    print(f"Lade QML: {qml_file}")
    engine.load(QUrl.fromLocalFile(qml_file))
    print(f"RootObjects nach Hauptladeversuch: {len(engine.rootObjects())}")
    if not engine.rootObjects():
        # Warnungen zur Hauptseite ausgeben
        try:
            errs = engine.warnings()
            if errs:
                print("QML-Warnungen/Fehler (DatenseiteV3.qml):")
                for e in errs:
                    print(str(e))
        except Exception:
            pass

        # Fallback auf minimales Fenster
        test_qml = os.path.join(style_path, "TestWindow.qml")
        print(f"Lade Fallback-QML: {test_qml}")
        engine.load(QUrl.fromLocalFile(test_qml))
        print(f"RootObjects nach Fallback: {len(engine.rootObjects())}")
        if not engine.rootObjects():
            # QML-Ladefehler ausgeben
            try:
                errs = engine.warnings()
                if errs:
                    print("QML-Warnungen/Fehler:")
                    for e in errs:
                        try:
                            print(str(e))
                        except Exception:
                            pass
            except Exception:
                pass
            sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


