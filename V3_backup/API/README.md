# Bolt API Integration

Dieser Ordner enthält die API-Integration für Bolt Fleet Management.

## Dateien

- `bolt_api_manager.py` - Hauptklasse für Bolt API-Verwaltung
- `bolt_api_integration.py` - Integration mit bestehendem System
- `bolt_api_config.json` - API-Konfiguration (wird automatisch erstellt)
- `bolt_token.json` - Token-Cache (wird automatisch erstellt)

## Setup

### 1. API-Credentials konfigurieren

```bash
python API/bolt_api_manager.py
```

Geben Sie Ihre Bolt Client ID und Secret ein.

### 2. API testen

```bash
python API/bolt_api_integration.py
```

## Features

### ✅ OAuth2-Authentifizierung
- Automatische Token-Verwaltung
- Token-Cache mit Ablaufzeit
- Sichere Credential-Speicherung

### ✅ API-Endpunkte
- Fleet-Daten abrufen
- Fahrer-Liste abrufen
- Fahrzeug-Liste abrufen
- CSV-Reports herunterladen

### ✅ Integration
- Kompatibel mit bestehendem Download-System
- Wochenbericht-Download wie bisher
- Fallback auf Session-basierte Downloads

## Verwendung

### Wochenbericht herunterladen
```python
from API.bolt_api_integration import BoltAPIIntegration

integration = BoltAPIIntegration()
integration.download_weekly_report(26)  # KW26
```

### Fleet-Daten abrufen
```python
fleet_data = integration.get_fleet_summary()
```

### API-Verbindung testen
```python
if integration.test_api_connection():
    print("✅ API funktioniert")
```

## Sicherheit

- Credentials werden lokal gespeichert
- Tokens werden automatisch erneuert
- Keine Credentials im Code

## Fehlerbehebung

### Token-Fehler
```bash
# Token löschen und neu erstellen
rm API/bolt_token.json
python API/bolt_api_manager.py
```

### API-Verbindungsfehler
1. Prüfen Sie Ihre Client ID und Secret
2. Stellen Sie sicher, dass die API aktiviert ist
3. Kontaktieren Sie Bolt Business Support

## Nächste Schritte

- [ ] Uber API Integration
- [ ] Erweiterte Berichte
- [ ] Automatisierte Downloads
- [ ] Datenbank-Integration 