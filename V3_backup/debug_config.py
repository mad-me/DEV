# Debug-Konfiguration für die Anwendung
# Setzen Sie DEBUG_MODE = True für Debug-Ausgaben

DEBUG_MODE = False  # Standardmäßig deaktiviert

# Spezifische Debug-Einstellungen
DEBUG_ABRECHNUNG = False
DEBUG_DATENBANK = False
DEBUG_QML = False
DEBUG_WIZARD = False

def debug_print(message, category="GENERAL"):
    """Zentrale Debug-Ausgabe-Funktion"""
    if not DEBUG_MODE:
        return
    
    # Kategorie-spezifische Debug-Ausgaben
    if category == "ABRECHNUNG" and not DEBUG_ABRECHNUNG:
        return
    elif category == "DATENBANK" and not DEBUG_DATENBANK:
        return
    elif category == "QML" and not DEBUG_QML:
        return
    elif category == "WIZARD" and not DEBUG_WIZARD:
        return
    
    print(f"DEBUG [{category}]: {message}")

def set_debug_mode(enabled=True, **kwargs):
    """Debug-Modus global aktivieren/deaktivieren"""
    global DEBUG_MODE, DEBUG_ABRECHNUNG, DEBUG_DATENBANK, DEBUG_QML, DEBUG_WIZARD
    
    DEBUG_MODE = enabled
    
    # Spezifische Kategorien setzen
    if 'abrechnung' in kwargs:
        DEBUG_ABRECHNUNG = kwargs['abrechnung']
    if 'datenbank' in kwargs:
        DEBUG_DATENBANK = kwargs['datenbank']
    if 'qml' in kwargs:
        DEBUG_QML = kwargs['qml']
    if 'wizard' in kwargs:
        DEBUG_WIZARD = kwargs['wizard'] 