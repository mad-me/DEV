# Erweiterte Import-Funktionen

## Neue Features

### 1. 🚫 Duplikat-Prüfung

Das Import-Tool prüft jetzt automatisch auf bereits bestehende Einträge und überspringt diese.

#### Funktionsweise:
- **Prüfungskriterien**: DN-Nr. + Dienstnehmer-Name
- **Automatisches Überspringen**: Duplikate werden nicht eingefügt
- **Logging**: Detaillierte Protokollierung der übersprungenen Einträge

#### Beispiel:
```python
# Wenn bereits ein Eintrag mit DN-Nr. "12345" und Dienstnehmer "Max Mustermann" existiert
# wird ein neuer Eintrag mit denselben Daten übersprungen
logging.info("⏭️ Duplikat übersprungen: Max Mustermann (DN-Nr: 12345)")
```

### 2. 🆔 Driver-ID-Matching

Falls das Name-Matching fehlschlägt, wird automatisch versucht, mit der Driver-ID zu matchen.

#### Matching-Strategie:
1. **Name-Matching**: Zuerst wird versucht, den Namen zu matchen
2. **Driver-ID-Matching**: Falls Name-Matching fehlschlägt, wird die Driver-ID verwendet
3. **Kombiniertes Matching**: Beide Methoden werden nacheinander versucht

#### Regex-Muster für Driver-ID:
```python
'Driver-ID': r'Driver[- ]?ID\W*[:\-]?\s*(\d+)'
```

#### Beispiel:
```python
# Name-Matching fehlschlägt für "Unbekannter Name"
# Driver-ID "123" wird in der Datenbank gesucht
# Wenn gefunden: Driver-ID 123 wird zugeordnet
logging.info("✅ Driver-ID-Match gefunden: 123")
```

## Technische Details

### Erweiterte Regex-Muster

```python
patterns = {
    'Dienstnehmer': r'Dienstnehmer\W*[:\-]?\s*(.*?)(?=\s*DN[- ]?Nr|$)',
    'DN-Nr.': r'DN[- ]?Nr\.?\W*[:\-]?\s*(\d+)',
    'Driver-ID': r'Driver[- ]?ID\W*[:\-]?\s*(\d+)',  # NEU
    'Brutto': r'Brutto\W*[:\-]?\s*([\d\.,]+)',
    'Zahlbetrag': r'Zahlbetrag\W*[:\-]?\s*([\d\.,]+)'
}
```

### Erweiterte Driver-Matching-Funktion

```python
def match_driver(self, dienstnehmer: str, driver_id: str = None) -> Optional[int]:
    """Findet den passenden Fahrer - zuerst Name-Matching, dann Driver-ID-Matching"""
    
    # 1. Name-Matching
    tokens = self.normalize_name(dienstnehmer)
    if tokens:
        for cached_tokens, cached_driver_id in self.driver_cache.items():
            match_count = sum(1 for t in tokens if t in cached_tokens)
            if len(tokens) >= 3 and match_count >= 2:
                return cached_driver_id
            elif len(tokens) < 3 and match_count == len(tokens):
                return cached_driver_id
    
    # 2. Driver-ID-Matching (falls Name-Matching fehlschlägt)
    if driver_id and driver_id.strip():
        try:
            conn = sqlite3.connect(self.drivers_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT driver_id FROM drivers WHERE driver_id = ?", (driver_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                logging.info(f"✅ Driver-ID-Match gefunden: {driver_id}")
                return result[0]
            else:
                logging.warning(f"⚠️ Driver-ID {driver_id} nicht in Datenbank gefunden")
        except Exception as e:
            logging.error(f"❌ Fehler beim Driver-ID-Matching: {e}")
    
    return None
```

### Duplikat-Prüfung in der Datenbank

```python
# Prüfe auf Duplikate basierend auf DN-Nr. und Dienstnehmer
cursor.execute(f'''SELECT COUNT(*) FROM "{table_name}" 
    WHERE dn_nr = ? AND dienstnehmer = ?''', 
    (entry['dn_nr'], entry['dienstnehmer']))

if cursor.fetchone()[0] > 0:
    logging.info(f"⏭️ Duplikat übersprungen: {entry['dienstnehmer']} (DN-Nr: {entry['dn_nr']})")
    skipped_count += 1
    continue
```

## Logging und Monitoring

### Neue Log-Meldungen

```python
# Duplikat-Prüfung
logging.info(f"⏭️ Duplikat übersprungen: {dienstnehmer} (DN-Nr: {dn_nr})")

# Driver-ID-Matching
logging.info(f"✅ Driver-ID-Match gefunden: {driver_id}")
logging.warning(f"⚠️ Driver-ID {driver_id} nicht in Datenbank gefunden")

# Import-Statistiken
logging.info(f"✅ {inserted_count} neue Einträge in Tabelle {table_name} gespeichert")
logging.info(f"⏭️ {skipped_count} Duplikate übersprungen")
```

### Erweiterte Datenstruktur

```python
entry = {
    'dienstnehmer': current_entry['Dienstnehmer'],
    'dn_nr': current_entry['DN-Nr.'],
    'driver_id': current_entry.get('Driver-ID', ''),  # Optional Driver-ID
    'brutto': self.parse_amount(current_entry['Brutto']),
    'zahlbetrag': self.parse_amount(current_entry['Zahlbetrag'])
}
```

## Verwendung

### Automatische Integration

Das erweiterte Import-Tool ist automatisch in das Dashboard integriert und wird verwendet, wenn Sie über den Import-Wizard eine Gehaltsabrechnung importieren.

### Manuelle Verwendung

```python
from salary_import_simple import import_salary_pdf

result = import_salary_pdf("pfad/zur/abrechnung.pdf")
if result["success"]:
    print(f"✅ {result['imported_count']} neue Einträge importiert")
```

### Testen der neuen Funktionen

```python
# Führen Sie test_enhanced_import.py aus
python test_enhanced_import.py
```

## Vorteile

### 1. Datenintegrität
- **Keine Duplikate**: Automatische Vermeidung von doppelten Einträgen
- **Konsistente Daten**: Saubere Datenbank ohne Redundanzen

### 2. Bessere Driver-Zuordnung
- **Höhere Erfolgsrate**: Driver-ID-Matching als Fallback
- **Flexibilität**: Verschiedene Matching-Strategien
- **Robustheit**: Funktioniert auch bei OCR-Fehlern bei Namen

### 3. Detailliertes Monitoring
- **Transparenz**: Klare Protokollierung aller Aktionen
- **Debugging**: Einfache Fehleranalyse
- **Statistiken**: Übersicht über importierte und übersprungene Einträge

## Fallback-Mechanismus

Falls das erweiterte Import-Tool nicht verfügbar ist, greift das System automatisch auf das bewährte alte System zurück:

```python
except ImportError:
    # Fallback auf altes System
    # Verwendet das ursprüngliche import_salarie.py
```

## Nächste Schritte

1. **Testen**: Führen Sie `test_enhanced_import.py` aus
2. **Monitoring**: Überwachen Sie die Log-Datei `salary_import.log`
3. **Feedback**: Sammeln Sie Erfahrungen mit den neuen Funktionen
4. **Optimierung**: Weitere Verbesserungen basierend auf dem Feedback 