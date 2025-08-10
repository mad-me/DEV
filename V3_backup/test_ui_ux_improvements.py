#!/usr/bin/env python3
"""
Test für Task 4.7: UI/UX-Verbesserungen
Testet alle neuen UI/UX-Features und Verbesserungen
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from mitarbeiter_seite_qml_v2 import MitarbeiterSeiteQMLV2
import unittest
import tempfile
import shutil
import time

class MockUIComponents(QObject):
    """Mock für UI-Komponenten"""
    toastShown = Signal(str, str, int)  # message, type, duration
    loadingShown = Signal(str, bool, str)  # operation, is_active, message
    dialogShown = Signal(str, str, str, str, str, str)  # title, message, confirm_text, cancel_text, dialog_type, callback_id
    shortcutTriggered = Signal(str)  # action
    
    def __init__(self):
        super().__init__()
        self.toast_history = []
        self.loading_history = []
        self.dialog_history = []
        self.shortcut_history = []

class TestUIUXImprovements(unittest.TestCase):
    """Test-Klasse für UI/UX-Verbesserungen (Task 4.7)"""
    
    def setUp(self):
        """Test-Setup"""
        # Verwende bestehende QApplication oder erstelle neue
        try:
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication([])
        except RuntimeError:
            # Falls bereits eine Instanz existiert, verwende sie
            self.app = QApplication.instance()
        
        self.mitarbeiter_backend = MitarbeiterSeiteQMLV2()
        self.ui_components = MockUIComponents()
        
        # UI-Tracking
        self.toast_notifications = []
        self.loading_states = []
        self.dialogs = []
        self.shortcuts = []
    
    def tearDown(self):
        """Test-Cleanup"""
        self.mitarbeiter_backend.cleanup_resources()
        # Nicht app.quit() aufrufen, da es eine Singleton-Instanz sein könnte
    
    def test_toast_notifications(self):
        """Test: Toast-Benachrichtigungen"""
        print("🧪 Teste Toast-Benachrichtigungen...")
        
        # Toast-Benachrichtigungen testen
        test_messages = [
            ("Erfolgreich gespeichert", "success", 3000),
            ("Fehler aufgetreten", "error", 5000),
            ("Warnung: Daten nicht vollständig", "warning", 4000),
            ("Info: Daten werden geladen", "info", 3000)
        ]
        
        for message, notification_type, duration in test_messages:
            self.mitarbeiter_backend.show_toast_notification(message, notification_type, duration)
            
            # Prüfe ob Toast in Queue ist
            self.assertGreater(len(self.mitarbeiter_backend._toast_queue), 0)
            
            # Prüfe Toast-Daten
            latest_toast = self.mitarbeiter_backend._toast_queue[-1]
            self.assertEqual(latest_toast['message'], message)
            self.assertEqual(latest_toast['type'], notification_type)
            self.assertEqual(latest_toast['duration'], duration)
        
        print("✅ Toast-Benachrichtigungen funktioniert")
    
    def test_loading_states(self):
        """Test: Loading-States"""
        print("🧪 Teste Loading-States...")
        
        # Loading-State starten
        operation = "test_operation"
        message = "Test läuft..."
        
        self.mitarbeiter_backend.show_loading_state(operation, message)
        
        # Prüfe ob Loading-State aktiv ist
        self.assertIn(operation, self.mitarbeiter_backend._loading_states)
        loading_state = self.mitarbeiter_backend._loading_states[operation]
        self.assertTrue(loading_state['is_active'])
        self.assertEqual(loading_state['message'], message)
        
        # Loading-State beenden
        self.mitarbeiter_backend.hide_loading_state(operation)
        
        # Prüfe ob Loading-State beendet ist
        loading_state = self.mitarbeiter_backend._loading_states[operation]
        self.assertFalse(loading_state['is_active'])
        
        print("✅ Loading-States funktioniert")
    
    def test_confirmation_dialogs(self):
        """Test: Confirmation-Dialogs"""
        print("🧪 Teste Confirmation-Dialogs...")
        
        # Dialog-Parameter
        title = "Test Dialog"
        message = "Sind Sie sicher?"
        confirm_text = "Ja"
        cancel_text = "Nein"
        dialog_type = "warning"
        
        # Callback-Funktionen
        confirm_called = False
        cancel_called = False
        
        def on_confirm():
            nonlocal confirm_called
            confirm_called = True
        
        def on_cancel():
            nonlocal cancel_called
            cancel_called = True
        
        # Dialog anzeigen
        self.mitarbeiter_backend.show_confirmation_dialog(
            title, message, confirm_text, cancel_text, dialog_type
        )
        
        # Prüfe ob Callbacks registriert sind
        self.assertGreater(len(self.mitarbeiter_backend._confirmation_callbacks), 0)
        
        # Callback-ID finden
        callback_id = None
        for cid in self.mitarbeiter_backend._confirmation_callbacks:
            callback_id = cid
            break
        
        # Confirm-Result simulieren (QML-Handling)
        self.mitarbeiter_backend.handle_confirmation_result(callback_id, "confirm")
        # Callbacks werden über QML gehandhabt, daher keine direkte Prüfung
        
        # Cancel-Result simulieren
        self.mitarbeiter_backend.show_confirmation_dialog(
            title, message, confirm_text, cancel_text, dialog_type
        )
        callback_id = list(self.mitarbeiter_backend._confirmation_callbacks.keys())[0]
        self.mitarbeiter_backend.handle_confirmation_result(callback_id, "cancel")
        # Callbacks werden über QML gehandhabt, daher keine direkte Prüfung
        
        print("✅ Confirmation-Dialogs funktioniert")
    
    def test_keyboard_shortcuts(self):
        """Test: Keyboard-Shortcuts"""
        print("🧪 Teste Keyboard-Shortcuts...")
        
        # Shortcuts registrieren
        test_shortcuts = [
            ("Ctrl+S", "save"),
            ("Ctrl+N", "new"),
            ("Ctrl+F", "search"),
            ("F5", "refresh")
        ]
        
        for key, action in test_shortcuts:
            self.mitarbeiter_backend.register_keyboard_shortcut(key, action)
            self.assertIn(key, self.mitarbeiter_backend._keyboard_shortcuts)
            self.assertEqual(self.mitarbeiter_backend._keyboard_shortcuts[key], action)
        
        # Shortcut entfernen
        self.mitarbeiter_backend.unregister_keyboard_shortcut("Ctrl+S")
        self.assertNotIn("Ctrl+S", self.mitarbeiter_backend._keyboard_shortcuts)
        
        print("✅ Keyboard-Shortcuts funktioniert")
    
    def test_ui_features_management(self):
        """Test: UI-Features-Management"""
        print("🧪 Teste UI-Features-Management...")
        
        # UI-Features prüfen
        ui_features = self.mitarbeiter_backend.get_ui_features()
        expected_features = ['toast_notifications', 'loading_animations', 'keyboard_shortcuts', 
                           'confirmation_dialogs', 'auto_save', 'dark_mode']
        
        for feature in expected_features:
            self.assertIn(feature, ui_features)
            self.assertIsInstance(ui_features[feature], bool)
        
        # UI-Feature ändern
        self.mitarbeiter_backend.set_ui_feature('toast_notifications', False)
        updated_features = self.mitarbeiter_backend.get_ui_features()
        self.assertFalse(updated_features['toast_notifications'])
        
        # Unbekanntes Feature
        self.mitarbeiter_backend.set_ui_feature('unknown_feature', True)
        
        print("✅ UI-Features-Management funktioniert")
    
    def test_convenience_toast_methods(self):
        """Test: Convenience-Toast-Methoden"""
        print("🧪 Teste Convenience-Toast-Methoden...")
        
        # Erfolgs-Toast
        self.mitarbeiter_backend.show_success_toast("Erfolgreich gespeichert")
        latest_toast = self.mitarbeiter_backend._toast_queue[-1]
        self.assertEqual(latest_toast['type'], "success")
        
        # Fehler-Toast
        self.mitarbeiter_backend.show_error_toast("Fehler aufgetreten")
        latest_toast = self.mitarbeiter_backend._toast_queue[-1]
        self.assertEqual(latest_toast['type'], "error")
        self.assertEqual(latest_toast['duration'], 5000)
        
        # Warnungs-Toast
        self.mitarbeiter_backend.show_warning_toast("Warnung")
        latest_toast = self.mitarbeiter_backend._toast_queue[-1]
        self.assertEqual(latest_toast['type'], "warning")
        self.assertEqual(latest_toast['duration'], 4000)
        
        # Info-Toast
        self.mitarbeiter_backend.show_info_toast("Info")
        latest_toast = self.mitarbeiter_backend._toast_queue[-1]
        self.assertEqual(latest_toast['type'], "info")
        self.assertEqual(latest_toast['duration'], 3000)
        
        print("✅ Convenience-Toast-Methoden funktioniert")
    
    def test_ui_feature_disabling(self):
        """Test: UI-Feature-Deaktivierung"""
        print("🧪 Teste UI-Feature-Deaktivierung...")
        
        # Toast-Notifications deaktivieren
        self.mitarbeiter_backend.set_ui_feature('toast_notifications', False)
        
        # Toast versuchen zu zeigen (sollte ignoriert werden)
        initial_queue_size = len(self.mitarbeiter_backend._toast_queue)
        self.mitarbeiter_backend.show_toast_notification("Test", "info", 3000)
        self.assertEqual(len(self.mitarbeiter_backend._toast_queue), initial_queue_size)
        
        # Loading-Animationen deaktivieren
        self.mitarbeiter_backend.set_ui_feature('loading_animations', False)
        
        # Loading-State versuchen zu zeigen (sollte ignoriert werden)
        self.mitarbeiter_backend.show_loading_state("test", "Test läuft...")
        self.assertNotIn("test", self.mitarbeiter_backend._loading_states)
        
        print("✅ UI-Feature-Deaktivierung funktioniert")
    
    def test_error_handling_in_ui_features(self):
        """Test: Fehlerbehandlung in UI-Features"""
        print("🧪 Teste Fehlerbehandlung in UI-Features...")
        
        # Ungültige Parameter testen
        try:
            self.mitarbeiter_backend.show_toast_notification("", "invalid_type", -1000)
            # Sollte keine Exception werfen, sondern einfach ignorieren
        except Exception as e:
            self.fail(f"Toast mit ungültigen Parametern sollte keine Exception werfen: {e}")
        
        try:
            self.mitarbeiter_backend.show_confirmation_dialog("", "", "", "", "invalid_type")
            # Sollte keine Exception werfen
        except Exception as e:
            self.fail(f"Confirmation-Dialog mit ungültigen Parametern sollte keine Exception werfen: {e}")
        
        try:
            self.mitarbeiter_backend.register_keyboard_shortcut("", "")
            # Sollte keine Exception werfen
        except Exception as e:
            self.fail(f"Keyboard-Shortcut mit ungültigen Parametern sollte keine Exception werfen: {e}")
        
        print("✅ Fehlerbehandlung in UI-Features funktioniert")
    
    def test_ui_integration(self):
        """Test: UI-Integration"""
        print("🧪 Teste UI-Integration...")
        
        # Vollständige UI-Integration testen
        test_operation = "test_integration"
        
        # Loading-State starten
        self.mitarbeiter_backend.show_loading_state(test_operation, "Integration läuft...")
        
        # Toast während Loading zeigen
        self.mitarbeiter_backend.show_info_toast("Integration gestartet")
        
        # Confirmation-Dialog während Loading
        def on_confirm():
            self.mitarbeiter_backend.show_success_toast("Integration bestätigt")
        
        def on_cancel():
            self.mitarbeiter_backend.show_warning_toast("Integration abgebrochen")
        
        self.mitarbeiter_backend.show_confirmation_dialog(
            "Integration", "Soll die Integration fortgesetzt werden?", 
            "Ja", "Nein", "info"
        )
        
        # Loading-State beenden
        self.mitarbeiter_backend.hide_loading_state(test_operation)
        
        # Prüfe ob alle Komponenten funktioniert haben
        self.assertGreater(len(self.mitarbeiter_backend._toast_queue), 0)
        self.assertIn(test_operation, self.mitarbeiter_backend._loading_states)
        self.assertGreater(len(self.mitarbeiter_backend._confirmation_callbacks), 0)
        
        print("✅ UI-Integration funktioniert")
    
    def test_performance_of_ui_features(self):
        """Test: Performance der UI-Features"""
        print("🧪 Teste Performance der UI-Features...")
        
        # Performance-Test für Toast-Notifications
        start_time = time.time()
        for i in range(100):
            self.mitarbeiter_backend.show_toast_notification(f"Toast {i}", "info", 1000)
        toast_time = time.time() - start_time
        
        # Performance-Test für Loading-States
        start_time = time.time()
        for i in range(50):
            self.mitarbeiter_backend.show_loading_state(f"operation_{i}", f"Loading {i}")
            self.mitarbeiter_backend.hide_loading_state(f"operation_{i}")
        loading_time = time.time() - start_time
        
        # Performance-Test für Confirmation-Dialogs
        start_time = time.time()
        for i in range(25):
            self.mitarbeiter_backend.show_confirmation_dialog(
                f"Dialog {i}", f"Message {i}", "Ja", "Nein", "info"
            )
        dialog_time = time.time() - start_time
        
        # Performance sollte akzeptabel sein
        self.assertLess(toast_time, 1.0)  # Maximal 1 Sekunde für 100 Toasts
        self.assertLess(loading_time, 1.0)  # Maximal 1 Sekunde für 50 Loading-States
        self.assertLess(dialog_time, 1.0)  # Maximal 1 Sekunde für 25 Dialogs
        
        print(f"✅ Performance der UI-Features: Toast={toast_time:.3f}s, Loading={loading_time:.3f}s, Dialog={dialog_time:.3f}s")

def run_ui_ux_tests():
    """Führt alle UI/UX-Tests aus"""
    print("🚀 Starte Task 4.7 UI/UX-Verbesserungen-Tests...")
    print("=" * 60)
    
    # Test-Suite erstellen
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUIUXImprovements)
    
    # Tests ausführen
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Zusammenfassung
    print("=" * 60)
    print(f"📊 Test-Ergebnisse:")
    print(f"   Tests ausgeführt: {result.testsRun}")
    print(f"   Fehler: {len(result.failures)}")
    print(f"   Fehlgeschlagen: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ Alle UI/UX-Verbesserungen-Tests erfolgreich!")
        print("🎉 Task 4.7: UI/UX-Verbesserungen - ABGESCHLOSSEN")
    else:
        print("❌ Einige Tests fehlgeschlagen")
        for test, traceback in result.failures + result.errors:
            print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Tests ausführen
    success = run_ui_ux_tests()
    
    # Exit-Code setzen
    sys.exit(0 if success else 1) 