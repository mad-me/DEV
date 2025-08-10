# Archiv - Alte Datenseite

## Übersicht
Dieses Verzeichnis enthält die archivierte Version der alten Datenseite, die durch die neue DatenseiteV3 ersetzt wurde.

## Dateien
- `datenseite_qml_old.py` - Die ursprüngliche Datenseite-Implementierung (1416 Zeilen)

## Warum wurde archiviert?
Die alte Datenseite wurde durch die neue DatenseiteV3 ersetzt, die folgende Verbesserungen bietet:

### ✅ Neue Features:
- **Drag & Drop Import**: Direktes Ziehen von Dateien in die Anwendung
- **Plattform-Auswahl-Dialog**: Benutzerfreundliche Auswahl zwischen 40100/31300
- **Verbesserte Kalenderwochen-Erkennung**: Unterstützt verschiedene Datumsformate
- **Moderne UI**: Kompakteres und benutzerfreundlicheres Design
- **Bessere Fehlerbehandlung**: Robuste Verarbeitung von Import-Fehlern

### 🔧 Technische Verbesserungen:
- **Kompaktere Codebase**: Weniger Code, mehr Funktionalität
- **Bessere Modularität**: Getrennte Backend- und Frontend-Logik
- **Asynchrone Verarbeitung**: Nicht-blockierende UI während Imports
- **Konsistente Datenbank-Pfade**: Alle Datenbanken im SQL/ Unterordner

## Migration
Die neue Implementierung ist vollständig kompatibel mit dem bestehenden Hauptprogramm (`main.py`). Die alte Schnittstelle wurde beibehalten, sodass keine Änderungen an anderen Teilen der Anwendung erforderlich sind.

## Wiederherstellung
Falls eine Wiederherstellung der alten Implementierung nötig ist:
1. Sichern Sie die aktuelle `datenseite_qml.py`
2. Kopieren Sie `datenseite_qml_old.py` zurück zu `datenseite_qml.py`
3. Starten Sie die Anwendung neu

## Datum der Archivierung
10. August 2025
