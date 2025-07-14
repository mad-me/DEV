# Dashboard V3 - QML-basierte Version

Ein modernes Dashboard-System mit QML-UI und Python-Backend, das die Funktionalität des V2-Dashboards erweitert und modernisiert.

## 🎨 Design-System

Das Dashboard verwendet ein zentrales Styling-System mit einheitlichen Farben und Design-Komponenten:

### Farbpalette
- **Hintergrund**: `#000000` (Schwarz)
- **Primärfarbe**: `#f79009` (Orange)
- **Primärfarbe Hover**: `#ffa733` (Helleres Orange)
- **Text**: `#ffffff` (Weiß)
- **Text gedämpft**: `#aaaaaa` (Grau)
- **Rahmen**: `#2a2a2a` (Dunkelgrau)
- **Akzent**: `#00c2ff` (Blau)
- **Erfolg**: `#22c55e` (Grün)
- **Fehler**: `#ef4444` (Rot)

### Seitenspezifische Farben
- **Daten**: `#22c55e` (Grün)
- **Mitarbeiter**: `#f79009` (Orange)
- **Fahrzeuge**: `#8b5cf6` (Lila)
- **Uber**: `#00c2ff` (Blau)
- **Bolt**: `#f59e0b` (Gelb)

### Design-Komponenten
- **Schriftgrößen**: 12px bis 48px
- **Abstände**: 5px bis 30px
- **Radien**: 4px bis 16px
- **Button-Höhen**: 40px bis 80px
- **Animationen**: 200ms bis 400ms

## 📁 Projektstruktur

```
V3/
├── Style.qml                 # Zentrale Styling-Datei
├── qmldir                    # QML-Modul-Registrierung
├── MainMenu.qml             # Hauptmenü mit animierter Sidebar
├── Abrechnungsseite.qml     # Abrechnungsseite
├── Datenseite.qml           # Datenseite
├── MitarbeiterSeite.qml     # Mitarbeiterseite
├── FahrzeugSeite.qml        # Fahrzeugseite
├── dashboard_complete.py    # Hauptanwendung
├── main_menu_qml.py         # MainMenu Backend
├── abrechnungsseite_qml.py  # Abrechnungsseite Backend
├── datenseite_qml.py        # Datenseite Backend
├── mitarbeiter_seite_qml.py # Mitarbeiterseite Backend
├── fahrzeug_seite_qml.py    # Fahrzeugseite Backend
├── SQL/
│   ├── database.db          # SQLite-Datenbank
└── README.md               # Diese Datei
```

## 🚀 Installation und Start

### Voraussetzungen
- Python 3.8+
- PySide6
- SQLite3

### Installation
```bash
pip install PySide6
```

### Start der Anwendung
```bash
python dashboard_complete.py
```

## 🎯 Funktionen

### MainMenu
- **Animierte Sidebar**: Elegante Slide-in/out Animation
- **Start-Buttons**: Große, farbige Buttons für jede Seite
- **Navigation**: Einfache Navigation zwischen allen Seiten
- **Responsive Design**: Passt sich an verschiedene Bildschirmgrößen an

### Abrechnungsseite
- **Dynamische Auswahlfelder**: Fahrer, Datum, Platform
- **Echtzeit-Berechnungen**: Automatische Aktualisierung der Ergebnisse
- **Vollständige Auswertung**: Gesamteinnahmen, Stunden, Stundensatz, Bargeld, Restbetrag
- **Uber-Block-Unterstützung**: Spezielle Berechnung für Uber-Fahrten

### Datenseite
- **Datenauswertung**: Umfassende Statistiken und Analysen
- **Filterfunktionen**: Nach Fahrer, Datum und Platform
- **Durchschnittswerte**: Berechnung von Durchschnittseinnahmen und -stunden

### Mitarbeiterseite
- **Mitarbeiterverwaltung**: Hinzufügen, Anzeigen, Löschen von Mitarbeitern
- **Moderne Listenansicht**: Übersichtliche Darstellung mit Icons und Status
- **Hover-Effekte**: Interaktive Elemente mit visueller Rückmeldung

### Fahrzeugseite
- **Fahrzeugverwaltung**: Hinzufügen, Anzeigen, Löschen von Fahrzeugen
- **Detaillierte Informationen**: Marke, Modell, Kennzeichen, Baujahr, Versicherung
- **Status-Anzeige**: Verfügbarkeit und Reparaturstatus

## 🎨 Styling-System

### Style.qml
Die zentrale Styling-Datei definiert alle Design-Konstanten:

```qml
// Farben
readonly property color background: '#000000'
readonly property color primary: '#f79009'
readonly property color text: '#ffffff'

// Schriftgrößen
readonly property int fontSizeNormal: 14
readonly property int fontSizeTitle: 18

// Abstände
readonly property int spacingNormal: 10
readonly property int spacingLarge: 15

// Funktionen
function getHoverColor(baseColor) {
    return Qt.lighter(baseColor, 1.2)
}
```

### Verwendung in QML
```qml
Rectangle {
    color: Style.background
    radius: Style.radiusNormal
    
    Text {
        color: Style.text
        font.pixelSize: Style.fontSizeTitle
    }
}
```

## 🔧 Backend-Integration

### Python-Backend
Jede Seite hat ein entsprechendes Python-Backend:
- **Datenbankverbindung**: SQLite für persistente Datenspeicherung
- **Business Logic**: Berechnungen und Datenverarbeitung
- **QML-Integration**: Signal/Slot-Verbindungen für Echtzeit-Updates

### Signal/Slot-System
```python
# Python Backend
class AbrechnungsSeiteQML(QObject):
    resultsChanged = Signal()
    
    def calculateResults(self, driver, date, platform):
        # Berechnungen durchführen
        self.resultsChanged.emit()
```

```qml
// QML Frontend
Connections {
    target: abrechnungsBackend
    function onResultsChanged() {
        updateResults()
    }
}
```

## 📊 Datenbank

Die Anwendung verwendet eine SQLite-Datenbank (`SQL/database.db`) mit Tabellen für:
- Mitarbeiter
- Fahrzeuge
- Fahrten
- Abrechnungen

## 🎯 Besonderheiten

### Uber-Block-Berechnung
Die Abrechnungsseite enthält eine spezielle Berechnung für Uber-Fahrten:
- **Anteil-Berechnung**: Automatische Berechnung des Fahreranteils
- **Bargeld-Integration**: Berücksichtigung von Bargeldzahlungen
- **Restbetrag**: Berechnung des verbleibenden Betrags

### Responsive Design
- **Flexible Layouts**: Anpassung an verschiedene Bildschirmgrößen
- **Touch-optimiert**: Große Buttons und Touch-freundliche Bedienung
- **Dark Mode**: Dunkles Design für bessere Lesbarkeit

## 🔄 Updates und Wartung

### Styling-Änderungen
Alle Design-Änderungen können zentral in `Style.qml` vorgenommen werden:
1. Farbe in `Style.qml` ändern
2. Alle QML-Dateien verwenden automatisch die neue Farbe
3. Keine manuellen Änderungen in einzelnen Dateien nötig

### Neue Seiten hinzufügen
1. QML-Datei erstellen (z.B. `NeueSeite.qml`)
2. Python-Backend erstellen (z.B. `neue_seite_qml.py`)
3. In `dashboard_complete.py` registrieren
4. In `MainMenu.qml` Button hinzufügen

## 🐛 Bekannte Probleme

- Beim Uber-Block in der Abrechnungsseite wurde der Restbetrag korrekt als anteil - cash_collected berechnet, aber die Anzeige war fehlerhaft, da der Wert von cash_collected manchmal als String oder NaN vorliegt. Die Umwandlung in float ist jetzt explizit eingebaut, um Fehler zu vermeiden.

## 📝 Changelog

### Version 3.0
- ✅ Zentrale Styling-Datei implementiert
- ✅ Einheitliche Farbpalette eingeführt
- ✅ Alle Seiten mit neuem Design aktualisiert
- ✅ Responsive Design verbessert
- ✅ Hover-Effekte hinzugefügt
- ✅ Animationen optimiert

### Version 2.0
- ✅ QML-UI implementiert
- ✅ Python-Backend erstellt
- ✅ Alle Seiten portiert
- ✅ Navigation implementiert

### Version 1.0
- ✅ Grundfunktionalität implementiert
- ✅ Datenbank-Integration
- ✅ Basis-UI erstellt

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Implementiere deine Änderungen
4. Teste gründlich
5. Erstelle einen Pull Request

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.