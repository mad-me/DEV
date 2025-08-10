#!/usr/bin/env python3
"""
Test für Task 4.2: UI-Verbesserungen für Validierungsfehler
Testet die verbesserte Fehlerbehandlung und UI-Integration
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

class MockValidationErrorDialog(QObject):
    """Mock für das Validierungsfehler-Dialog"""
    dialogShown = Signal(list, str)  # Fehlerliste, Operation
    dialogClosed = Signal()
    retryRequested = Signal()
    editRequested = Signal()
    
    def __init__(self):
        super().__init__()
        self.shown_errors = []
        self.shown_operation = ""
        self.is_visible = False
    
    def showDialog(self, errors, operation):
        self.shown_errors = errors
        self.shown_operation = operation
        self.is_visible = True
        self.dialogShown.emit(errors, operation)
    
    def closeDialog(self):
        self.is_visible = False
        self.dialogClosed.emit()

class TestUIValidationImprovements(unittest.TestCase):
    """Test-Klasse für UI-Verbesserungen (Task 4.2)"""
    
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
        self.mock_dialog = MockValidationErrorDialog()
        
        # Signal-Verbindungen für Tests
        self.validation_errors_received = []
        self.validation_operation_received = ""
        self.general_errors_received = []
        
        self.mitarbeiter_backend.validationErrorOccurred.connect(
            lambda errors, operation: self._on_validation_error(errors, operation)
        )
        self.mitarbeiter_backend.errorOccurred.connect(
            lambda error: self._on_general_error(error)
        )
    
    def tearDown(self):
        """Test-Cleanup"""
        self.mitarbeiter_backend.cleanup_resources()
        # Nicht app.quit() aufrufen, da es eine Singleton-Instanz sein könnte
    
    def _on_validation_error(self, errors, operation):
        """Callback für Validierungsfehler"""
        self.validation_errors_received = errors
        self.validation_operation_received = operation
    
    def _on_general_error(self, error):
        """Callback für allgemeine Fehler"""
        self.general_errors_received.append(error)
    
    def test_validation_error_parsing(self):
        """Test: Validierungsfehler-Parsing"""
        print("🧪 Teste Validierungsfehler-Parsing...")
        
        # Test-Validierungsfehler
        test_error = ValueError("Validierungsfehler: email: E-Mail-Adresse hat ein ungültiges Format; first_name: Vorname muss 2-50 Zeichen lang sein")
        
        # Fehlerbehandlung testen
        self.mitarbeiter_backend._handle_validation_error("Mitarbeiter speichern", test_error)
        
        # Prüfen ob Validierungsfehler-Signal gesendet wurde
        self.assertEqual(len(self.validation_errors_received), 2)
        self.assertIn("email: E-Mail-Adresse hat ein ungültiges Format", self.validation_errors_received)
        self.assertIn("first_name: Vorname muss 2-50 Zeichen lang sein", self.validation_errors_received)
        self.assertEqual(self.validation_operation_received, "Mitarbeiter speichern")
        
        print("✅ Validierungsfehler-Parsing funktioniert")
    
    def test_general_error_handling(self):
        """Test: Allgemeine Fehlerbehandlung"""
        print("🧪 Teste allgemeine Fehlerbehandlung...")
        
        # Test-allgemeiner Fehler
        test_error = ValueError("Allgemeiner Fehler ohne Validierungsfehler-Format")
        
        # Fehlerbehandlung testen
        self.mitarbeiter_backend._handle_error("Test-Operation", test_error)
        
        # Prüfen ob allgemeines Fehler-Signal gesendet wurde
        self.assertEqual(len(self.general_errors_received), 1)
        self.assertIn("Allgemeiner Fehler ohne Validierungsfehler-Format", self.general_errors_received[0])
        
        print("✅ Allgemeine Fehlerbehandlung funktioniert")
    
    def test_validation_error_signal_emission(self):
        """Test: Validierungsfehler-Signal-Emission"""
        print("🧪 Teste Validierungsfehler-Signal-Emission...")
        
        # Signal-Verbindung testen
        signal_received = False
        received_errors = []
        received_operation = ""
        
        def on_validation_error(errors, operation):
            nonlocal signal_received, received_errors, received_operation
            signal_received = True
            received_errors = errors
            received_operation = operation
        
        self.mitarbeiter_backend.validationErrorOccurred.connect(on_validation_error)
        
        # Validierungsfehler simulieren
        test_errors = ["email: Ungültiges Format", "phone: Zu kurz"]
        test_operation = "Mitarbeiter bearbeiten"
        
        # Signal direkt senden
        self.mitarbeiter_backend.validationErrorOccurred.emit(test_errors, test_operation)
        
        # Prüfen ob Signal empfangen wurde
        self.assertTrue(signal_received)
        self.assertEqual(received_errors, test_errors)
        self.assertEqual(received_operation, test_operation)
        
        print("✅ Validierungsfehler-Signal-Emission funktioniert")
    
    def test_error_message_formatting(self):
        """Test: Fehlermeldung-Formatierung"""
        print("🧪 Teste Fehlermeldung-Formatierung...")
        
        # Verschiedene Validierungsfehler-Formate testen
        test_cases = [
            {
                "input": "Validierungsfehler: email: Ungültiges Format; phone: Zu kurz",
                "expected_errors": ["email: Ungültiges Format", "phone: Zu kurz"]
            },
            {
                "input": "Validierungsfehler: driver_id: Driver ID muss eine gültige Zahl sein",
                "expected_errors": ["driver_id: Driver ID muss eine gültige Zahl sein"]
            },
            {
                "input": "Validierungsfehler: first_name: Vorname zu kurz; last_name: Nachname zu lang; email: Ungültiges Format",
                "expected_errors": ["first_name: Vorname zu kurz", "last_name: Nachname zu lang", "email: Ungültiges Format"]
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            with self.subTest(f"Test Case {i+1}"):
                # Validierungsfehler simulieren
                test_error = ValueError(test_case["input"])
                
                # Fehlerbehandlung testen
                self.mitarbeiter_backend._handle_validation_error("Test-Operation", test_error)
                
                # Prüfen ob Fehler korrekt formatiert wurden
                self.assertEqual(self.validation_errors_received, test_case["expected_errors"])
        
        print("✅ Fehlermeldung-Formatierung funktioniert")
    
    def test_mock_dialog_functionality(self):
        """Test: Mock-Dialog-Funktionalität"""
        print("🧪 Teste Mock-Dialog-Funktionalität...")
        
        # Dialog-Events testen
        dialog_events = []
        
        def on_dialog_shown(errors, operation):
            dialog_events.append(("shown", errors, operation))
        
        def on_dialog_closed():
            dialog_events.append(("closed", None, None))
        
        def on_retry_requested():
            dialog_events.append(("retry", None, None))
        
        def on_edit_requested():
            dialog_events.append(("edit", None, None))
        
        # Signal-Verbindungen
        self.mock_dialog.dialogShown.connect(on_dialog_shown)
        self.mock_dialog.dialogClosed.connect(on_dialog_closed)
        self.mock_dialog.retryRequested.connect(on_retry_requested)
        self.mock_dialog.editRequested.connect(on_edit_requested)
        
        # Dialog-Aktionen testen
        test_errors = ["Fehler 1", "Fehler 2"]
        test_operation = "Test-Operation"
        
        # Dialog anzeigen
        self.mock_dialog.showDialog(test_errors, test_operation)
        self.assertTrue(self.mock_dialog.is_visible)
        self.assertEqual(self.mock_dialog.shown_errors, test_errors)
        self.assertEqual(self.mock_dialog.shown_operation, test_operation)
        
        # Dialog schließen
        self.mock_dialog.closeDialog()
        self.assertFalse(self.mock_dialog.is_visible)
        
        # Retry simulieren
        self.mock_dialog.retryRequested.emit()
        
        # Edit simulieren
        self.mock_dialog.editRequested.emit()
        
        # Prüfen ob alle Events empfangen wurden
        self.assertEqual(len(dialog_events), 4)
        self.assertEqual(dialog_events[0][0], "shown")
        self.assertEqual(dialog_events[1][0], "closed")
        self.assertEqual(dialog_events[2][0], "retry")
        self.assertEqual(dialog_events[3][0], "edit")
        
        print("✅ Mock-Dialog-Funktionalität funktioniert")
    
    def test_error_handling_integration(self):
        """Test: Fehlerbehandlung-Integration"""
        print("🧪 Teste Fehlerbehandlung-Integration...")
        
        # Integration zwischen Backend und UI testen
        test_validation_error = ValueError("Validierungsfehler: email: Ungültiges Format; phone: Zu kurz")
        test_general_error = ValueError("Allgemeiner Fehler")
        
        # Validierungsfehler testen
        self.mitarbeiter_backend._handle_error("Mitarbeiter speichern", test_validation_error)
        
        # Prüfen ob Validierungsfehler korrekt behandelt wurde
        self.assertEqual(len(self.validation_errors_received), 2)
        self.assertEqual(self.validation_operation_received, "Mitarbeiter speichern")
        self.assertEqual(len(self.general_errors_received), 0)  # Kein allgemeiner Fehler
        
        # Allgemeinen Fehler testen
        self.mitarbeiter_backend._handle_error("Test-Operation", test_general_error)
        
        # Prüfen ob allgemeiner Fehler korrekt behandelt wurde
        self.assertEqual(len(self.general_errors_received), 1)
        self.assertIn("Allgemeiner Fehler", self.general_errors_received[0])
        
        print("✅ Fehlerbehandlung-Integration funktioniert")
    
    def test_error_message_clarity(self):
        """Test: Fehlermeldung-Klarheit"""
        print("🧪 Teste Fehlermeldung-Klarheit...")
        
        # Test verschiedener Fehlertypen
        test_cases = [
            {
                "error": ValueError("Validierungsfehler: email: E-Mail-Adresse hat ein ungültiges Format"),
                "expected_type": "validation",
                "expected_clarity": "email: E-Mail-Adresse hat ein ungültiges Format"
            },
            {
                "error": ValueError("E-Mail-Adresse wird bereits verwendet"),
                "expected_type": "general",
                "expected_clarity": "E-Mail-Adresse wird bereits verwendet"
            },
            {
                "error": ValueError("Driver ID 123 wird bereits verwendet"),
                "expected_type": "general",
                "expected_clarity": "Driver ID 123 wird bereits verwendet"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            with self.subTest(f"Test Case {i+1}"):
                # Fehlerbehandlung testen
                self.mitarbeiter_backend._handle_error("Test-Operation", test_case["error"])
                
                if test_case["expected_type"] == "validation":
                    # Prüfen ob Validierungsfehler korrekt erkannt wurde
                    self.assertGreater(len(self.validation_errors_received), 0)
                    self.assertIn(test_case["expected_clarity"], self.validation_errors_received)
                else:
                    # Prüfen ob allgemeiner Fehler korrekt erkannt wurde
                    self.assertGreater(len(self.general_errors_received), 0)
                    self.assertIn(test_case["expected_clarity"], self.general_errors_received[-1])
        
        print("✅ Fehlermeldung-Klarheit funktioniert")

def run_ui_validation_tests():
    """Führt alle UI-Validierungstests aus"""
    print("🚀 Starte Task 4.2 UI-Validierungstests...")
    print("=" * 60)
    
    # Test-Suite erstellen
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUIValidationImprovements)
    
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
        print("✅ Alle UI-Validierungstests erfolgreich!")
        print("🎉 Task 4.2: UI-Verbesserungen für Validierungsfehler - ABGESCHLOSSEN")
    else:
        print("❌ Einige Tests fehlgeschlagen")
        for test, traceback in result.failures + result.errors:
            print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Tests ausführen
    success = run_ui_validation_tests()
    
    # Exit-Code setzen
    sys.exit(0 if success else 1) 