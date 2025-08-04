# 🔄 Wiederherstellungs-Anleitung

## Übersicht der Wiederherstellungsoptionen

### 1. **Automatisches Backup-System** (Empfohlen)
Das `safe_cleanup.py` Skript erstellt automatisch Backups vor jeder Löschung.

#### Wiederherstellung über das Skript:
```bash
# Komplettes Backup wiederherstellen
python safe_cleanup.py --restore

# Einzelne Datei wiederherstellen
python safe_cleanup.py --restore-item backup_original/

# Einzelne Datei wiederherstellen
python safe_cleanup.py --restore-item archive/debug_import.py
```

### 2. **Git-Versionierung** (Falls verfügbar)
```bash
# Einzelne Datei wiederherstellen
git checkout HEAD -- backup_original/abrechnungsseite_qml.py.backup

# Komplettes Verzeichnis wiederherstellen
git checkout HEAD -- backup_original/

# Alle gelöschten Dateien wiederherstellen
git checkout HEAD -- .
```

### 3. **Windows-Papierkorb**
- Gelöschte Dateien landen automatisch im Papierkorb
- Rechtsklick → "Wiederherstellen"
- **Vorteil**: Einfach und automatisch verfügbar

### 4. **Manuelle Wiederherstellung**
Falls Sie ein eigenes Backup erstellt haben:
```bash
# Backup-Verzeichnis kopieren
cp -r cleanup_backup_YYYYMMDD_HHMMSS/backup_original/ ./

# Einzelne Dateien kopieren
cp cleanup_backup_YYYYMMDD_HHMMSS/archive/debug_import.py ./
```

## 📋 Backup-Verzeichnis-Struktur

Nach dem Cleanup finden Sie ein Backup-Verzeichnis wie:
```
cleanup_backup_20241201_143022/
├── backup_original/
│   ├── abrechnungsseite_qml.py.backup
│   ├── datenseite_qml.py.backup
│   ├── db_manager.py.backup
│   ├── fahrzeug_seite_qml.py.backup
│   └── mitarbeiter_seite_qml.py.backup
├── archive/
│   ├── debug_import.log
│   ├── debug_import.py
│   ├── import_funk.py
│   ├── import_salarie.py
│   ├── salary_import.log
│   └── salary_loader.log
├── download/
│   ├── data/
│   ├── dumps/
│   ├── errors/
│   └── src/
└── abrechnungsseite_qml.py
```

## ⚠️ Wichtige Hinweise

### Vor der Wiederherstellung:
1. **Anwendung stoppen**: Stellen Sie sicher, dass die Hauptanwendung nicht läuft
2. **Backup prüfen**: Überprüfen Sie, ob das Backup-Verzeichnis existiert
3. **Platz prüfen**: Stellen Sie sicher, dass genug Speicherplatz vorhanden ist

### Nach der Wiederherstellung:
1. **Anwendung testen**: Starten Sie die Anwendung und testen Sie die Funktionalität
2. **Import-Tests**: Testen Sie kritische Funktionen wie Datenimport
3. **Dependencies prüfen**: Stellen Sie sicher, dass alle Abhängigkeiten korrekt sind

## 🚨 Notfall-Wiederherstellung

Falls alle anderen Methoden fehlschlagen:

### 1. **Systemwiederherstellung** (Windows)
- Windows-Einstellungen → Update und Sicherheit → Wiederherstellung
- Systemwiederherstellungspunkt auswählen

### 2. **Datei-Wiederherstellungssoftware**
- Recuva (kostenlos)
- TestDisk & PhotoRec
- EaseUS Data Recovery

### 3. **Cloud-Backup** (Falls verfügbar)
- OneDrive, Google Drive, Dropbox
- Git-Repository (GitHub, GitLab)

## 📞 Support

Falls Sie Probleme bei der Wiederherstellung haben:
1. Prüfen Sie die Backup-Verzeichnis-Struktur
2. Überprüfen Sie die Berechtigungen
3. Testen Sie die Wiederherstellung in einem separaten Verzeichnis
4. Dokumentieren Sie alle Fehlermeldungen 