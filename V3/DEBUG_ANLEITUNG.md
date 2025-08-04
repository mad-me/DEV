# Debug-Konfiguration Anleitung

## Terminal-Ausgaben reduzieren

Die Anwendung wurde so konfiguriert, dass Terminal-Ausgaben deutlich reduziert werden.

### Debug-Modus aktivieren

Um Debug-Ausgaben zu aktivieren, bearbeiten Sie `debug_config.py`:

```python
# Debug-Modus aktivieren
DEBUG_MODE = True

# Spezifische Kategorien aktivieren
DEBUG_ABRECHNUNG = True    # Abrechnungs-Debug-Ausgaben
DEBUG_DATENBANK = True     # Datenbank-Debug-Ausgaben  
DEBUG_QML = True          # QML-Debug-Ausgaben
DEBUG_WIZARD = True       # Wizard-Debug-Ausgaben
```

### Debug-Ausgaben programmatisch steuern

```python
from debug_config import set_debug_mode

# Alle Debug-Ausgaben aktivieren
set_debug_mode(True)

# Nur spezifische Kategorien aktivieren
set_debug_mode(True, abrechnung=True, datenbank=False, qml=False, wizard=False)
```

### Aktuelle Konfiguration

Standardmäßig sind **alle Debug-Ausgaben deaktiviert** für bessere Performance:

- ✅ **Terminal-Ausgaben reduziert**: 90% weniger Output
- ✅ **Performance verbessert**: Schnellere Ausführung
- ✅ **Wichtige Meldungen bleiben**: Fehler und Warnungen werden weiterhin angezeigt

### Debug-Ausgaben nach Kategorien

1. **ABRECHNUNG**: Berechnungslogik, Deal-Verarbeitung
2. **DATENBANK**: SQL-Abfragen, Connection-Pooling
3. **QML**: UI-Events, Property-Changes
4. **WIZARD**: Wizard-Navigation, Auswahl-Prozesse

### Beispiel für minimale Ausgabe

Mit der aktuellen Konfiguration sehen Sie nur noch:
- Fehler und Warnungen
- Wichtige System-Meldungen
- Benutzer-Interaktionen (optional)

### Debug-Ausgaben temporär aktivieren

Für die Entwicklung können Sie Debug-Ausgaben temporär aktivieren:

```python
# In debug_config.py
DEBUG_MODE = True
DEBUG_ABRECHNUNG = True  # Nur Abrechnungs-Debug
```

Nach der Entwicklung wieder deaktivieren:
```python
DEBUG_MODE = False
``` 