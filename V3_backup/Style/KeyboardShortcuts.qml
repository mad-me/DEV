import QtQuick 2.15
import QtQuick.Controls 2.15
import Style 1.0

Item {
    id: keyboardShortcuts
    
    // Properties für verschiedene Shortcuts
    property var shortcuts: ({})
    property bool enabled: true
    
    // Focus für Keyboard-Events
    focus: enabled
    activeFocusOnTab: false
    
    // Keyboard Event Handler
    Keys.onPressed: function(event) {
        if (!enabled) return
        
        // Ctrl/Cmd + Key Kombinationen
        if (event.modifiers & Qt.ControlModifier) {
            switch (event.key) {
                case Qt.Key_S: // Ctrl+S - Speichern
                    if (shortcuts.save) shortcuts.save()
                    event.accepted = true
                    break
                case Qt.Key_N: // Ctrl+N - Neu
                    if (shortcuts.new) shortcuts.new()
                    event.accepted = true
                    break
                case Qt.Key_O: // Ctrl+O - Öffnen
                    if (shortcuts.open) shortcuts.open()
                    event.accepted = true
                    break
                case Qt.Key_F: // Ctrl+F - Suche
                    if (shortcuts.search) shortcuts.search()
                    event.accepted = true
                    break
                case Qt.Key_R: // Ctrl+R - Aktualisieren
                    if (shortcuts.refresh) shortcuts.refresh()
                    event.accepted = true
                    break
                case Qt.Key_Z: // Ctrl+Z - Rückgängig
                    if (shortcuts.undo) shortcuts.undo()
                    event.accepted = true
                    break
                case Qt.Key_Y: // Ctrl+Y - Wiederholen
                    if (shortcuts.redo) shortcuts.redo()
                    event.accepted = true
                    break
                case Qt.Key_Plus: // Ctrl++ - Zoom In
                    if (shortcuts.zoomIn) shortcuts.zoomIn()
                    event.accepted = true
                    break
                case Qt.Key_Minus: // Ctrl+- - Zoom Out
                    if (shortcuts.zoomOut) shortcuts.zoomOut()
                    event.accepted = true
                    break
            }
        }
        
        // Function Keys
        switch (event.key) {
            case Qt.Key_F1: // F1 - Hilfe
                if (shortcuts.help) shortcuts.help()
                event.accepted = true
                break
            case Qt.Key_F2: // F2 - Bearbeiten
                if (shortcuts.edit) shortcuts.edit()
                event.accepted = true
                break
            case Qt.Key_F3: // F3 - Suche
                if (shortcuts.search) shortcuts.search()
                event.accepted = true
                break
            case Qt.Key_F4: // F4 - Schließen
                if (shortcuts.close) shortcuts.close()
                event.accepted = true
                break
            case Qt.Key_F5: // F5 - Aktualisieren
                if (shortcuts.refresh) shortcuts.refresh()
                event.accepted = true
                break
            case Qt.Key_F6: // F6 - Nächster Tab
                if (shortcuts.nextTab) shortcuts.nextTab()
                event.accepted = true
                break
            case Qt.Key_F7: // F7 - Vorheriger Tab
                if (shortcuts.prevTab) shortcuts.prevTab()
                event.accepted = true
                break
            case Qt.Key_F8: // F8 - Debug
                if (shortcuts.debug) shortcuts.debug()
                event.accepted = true
                break
            case Qt.Key_F9: // F9 - Export
                if (shortcuts.export) shortcuts.export()
                event.accepted = true
                break
            case Qt.Key_F10: // F10 - Import
                if (shortcuts.import) shortcuts.import()
                event.accepted = true
                break
        }
        
        // Escape Key
        if (event.key === Qt.Key_Escape) {
            if (shortcuts.escape) shortcuts.escape()
            event.accepted = true
        }
        
        // Enter Key
        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
            if (shortcuts.enter) shortcuts.enter()
            event.accepted = true
        }
        
        // Tab Key
        if (event.key === Qt.Key_Tab) {
            if (event.modifiers & Qt.ShiftModifier) {
                if (shortcuts.prevField) shortcuts.prevField()
            } else {
                if (shortcuts.nextField) shortcuts.nextField()
            }
            event.accepted = true
        }
    }
    
    // Funktionen
    function registerShortcut(key, callback) {
        shortcuts[key] = callback
    }
    
    function unregisterShortcut(key) {
        delete shortcuts[key]
    }
    
    function enable() {
        enabled = true
    }
    
    function disable() {
        enabled = false
    }
    
    // Standard-Shortcuts registrieren
    function registerDefaultShortcuts() {
        // Navigation
        registerShortcut("home", function() {
            console.log("Home shortcut triggered")
        })
        
        registerShortcut("back", function() {
            console.log("Back shortcut triggered")
        })
        
        // Aktionen
        registerShortcut("save", function() {
            console.log("Save shortcut triggered")
        })
        
        registerShortcut("new", function() {
            console.log("New shortcut triggered")
        })
        
        registerShortcut("search", function() {
            console.log("Search shortcut triggered")
        })
        
        registerShortcut("refresh", function() {
            console.log("Refresh shortcut triggered")
        })
        
        registerShortcut("escape", function() {
            console.log("Escape shortcut triggered")
        })
    }
    
    // Component.onCompleted
    Component.onCompleted: {
        registerDefaultShortcuts()
    }
} 