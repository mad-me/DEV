#!/usr/bin/env python3
"""
Test für Task 4.1: Validierung erweitern
Testet alle neuen Validierungsfunktionen für Driver IDs und Mitarbeiterdaten
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from db_manager import DBManager
import unittest
import tempfile
import shutil

class TestValidationExtended(unittest.TestCase):
    """Test-Klasse für erweiterte Validierung (Task 4.1)"""
    
    def setUp(self):
        """Test-Setup mit temporärer Datenbank"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_validation.db")
        self.db_manager = DBManager(self.db_path)
        self.db_manager.initialize_database_tables()
        
        # Test-Mitarbeiter einfügen
        self.test_employee = {
            "driver_license_number": "B123456789",
            "first_name": "Max",
            "last_name": "Mustermann",
            "phone": "+43123456789",
            "email": "max.mustermann@test.com",
            "hire_date": "2024-01-15",
            "status": "active"
        }
        self.db_manager.insert_mitarbeiter(self.test_employee)
    
    def tearDown(self):
        """Test-Cleanup"""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_driver_id_valid(self):
        """Test: Gültige Driver IDs"""
        print("🧪 Teste gültige Driver IDs...")
        
        valid_ids = [1, 100, 999999, "123", "456789"]
        for driver_id in valid_ids:
            with self.subTest(driver_id=driver_id):
                result = self.db_manager._validate_driver_id(driver_id)
                self.assertTrue(result, f"Driver ID {driver_id} sollte gültig sein")
        
        print("✅ Gültige Driver IDs funktionieren")
    
    def test_validate_driver_id_invalid(self):
        """Test: Ungültige Driver IDs"""
        print("🧪 Teste ungültige Driver IDs...")
        
        invalid_ids = [0, -1, 1000000, "abc", "", None, "0", "-5"]
        for driver_id in invalid_ids:
            with self.subTest(driver_id=driver_id):
                result = self.db_manager._validate_driver_id(driver_id)
                self.assertFalse(result, f"Driver ID {driver_id} sollte ungültig sein")
        
        print("✅ Ungültige Driver IDs werden korrekt erkannt")
    
    def test_validate_email_valid(self):
        """Test: Gültige E-Mail-Adressen"""
        print("🧪 Teste gültige E-Mail-Adressen...")
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "user123@test-domain.com",
            ""  # Leere E-Mails sind erlaubt
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                result = self.db_manager._validate_email(email)
                self.assertTrue(result, f"E-Mail {email} sollte gültig sein")
        
        print("✅ Gültige E-Mail-Adressen funktionieren")
    
    def test_validate_email_invalid(self):
        """Test: Ungültige E-Mail-Adressen"""
        print("🧪 Teste ungültige E-Mail-Adressen...")
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
            "user@example..com"
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                result = self.db_manager._validate_email(email)
                self.assertFalse(result, f"E-Mail {email} sollte ungültig sein")
        
        print("✅ Ungültige E-Mail-Adressen werden korrekt erkannt")
    
    def test_validate_phone_valid(self):
        """Test: Gültige Telefonnummern"""
        print("🧪 Teste gültige Telefonnummern...")
        
        valid_phones = [
            "+43123456789",
            "0123456789",
            "+1-555-123-4567",
            "(01) 2345 6789",
            "0123 456 789",
            ""  # Leere Telefonnummern sind erlaubt
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                result = self.db_manager._validate_phone(phone)
                self.assertTrue(result, f"Telefonnummer {phone} sollte gültig sein")
        
        print("✅ Gültige Telefonnummern funktionieren")
    
    def test_validate_phone_invalid(self):
        """Test: Ungültige Telefonnummern"""
        print("🧪 Teste ungültige Telefonnummern...")
        
        invalid_phones = [
            "123",  # Zu kurz
            "abcdefghij",  # Keine Zahlen
            "+12345678901234567890",  # Zu lang
            "abc123def"
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                result = self.db_manager._validate_phone(phone)
                self.assertFalse(result, f"Telefonnummer {phone} sollte ungültig sein")
        
        print("✅ Ungültige Telefonnummern werden korrekt erkannt")
    
    def test_validate_name_valid(self):
        """Test: Gültige Namen"""
        print("🧪 Teste gültige Namen...")
        
        valid_names = [
            "Max",
            "Mustermann",
            "Max Mustermann",
            "Hans-Peter",
            "Müller",
            "François",
            "José María"
        ]
        
        for name in valid_names:
            with self.subTest(name=name):
                result = self.db_manager._validate_name(name)
                self.assertTrue(result, f"Name {name} sollte gültig sein")
        
        print("✅ Gültige Namen funktionieren")
    
    def test_validate_name_invalid(self):
        """Test: Ungültige Namen"""
        print("🧪 Teste ungültige Namen...")
        
        invalid_names = [
            "A",  # Zu kurz
            "X" * 51,  # Zu lang
            "Max123",  # Zahlen
            "Max@Mustermann",  # Sonderzeichen
            "",  # Leer
            None
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                result = self.db_manager._validate_name(name)
                self.assertFalse(result, f"Name {name} sollte ungültig sein")
        
        print("✅ Ungültige Namen werden korrekt erkannt")
    
    def test_validate_license_number_valid(self):
        """Test: Gültige Führerscheinnummern"""
        print("🧪 Teste gültige Führerscheinnummern...")
        
        valid_licenses = [
            "B123456789",
            "A987654321",
            "C-123-456-789",
            ""  # Leere Führerscheinnummern sind erlaubt
        ]
        
        for license_num in valid_licenses:
            with self.subTest(license_num=license_num):
                result = self.db_manager._validate_license_number(license_num)
                self.assertTrue(result, f"Führerscheinnummer {license_num} sollte gültig sein")
        
        print("✅ Gültige Führerscheinnummern funktionieren")
    
    def test_validate_license_number_invalid(self):
        """Test: Ungültige Führerscheinnummern"""
        print("🧪 Teste ungültige Führerscheinnummern...")
        
        invalid_licenses = [
            "1234",  # Zu kurz
            "B12345678901234567890",  # Zu lang
            "B123@456",  # Ungültige Zeichen
            "b123456789"  # Kleinbuchstaben
        ]
        
        for license_num in invalid_licenses:
            with self.subTest(license_num=license_num):
                result = self.db_manager._validate_license_number(license_num)
                self.assertFalse(result, f"Führerscheinnummer {license_num} sollte ungültig sein")
        
        print("✅ Ungültige Führerscheinnummern werden korrekt erkannt")
    
    def test_validate_date_valid(self):
        """Test: Gültige Daten"""
        print("🧪 Teste gültige Daten...")
        
        valid_dates = [
            "2024-01-15",
            "15.01.2024",
            "15/01/2024",
            "2024/01/15",
            ""  # Leere Daten sind erlaubt
        ]
        
        for date_str in valid_dates:
            with self.subTest(date_str=date_str):
                result = self.db_manager._validate_date(date_str)
                self.assertTrue(result, f"Datum {date_str} sollte gültig sein")
        
        print("✅ Gültige Daten funktionieren")
    
    def test_validate_date_invalid(self):
        """Test: Ungültige Daten"""
        print("🧪 Teste ungültige Daten...")
        
        invalid_dates = [
            "2024-13-01",  # Ungültiger Monat
            "32.01.2024",  # Ungültiger Tag
            "2024-02-30",  # Ungültiger Tag für Februar
            "invalid-date",
            "2024/13/01"
        ]
        
        for date_str in invalid_dates:
            with self.subTest(date_str=date_str):
                result = self.db_manager._validate_date(date_str)
                self.assertFalse(result, f"Datum {date_str} sollte ungültig sein")
        
        print("✅ Ungültige Daten werden korrekt erkannt")
    
    def test_validate_employee_data_complete(self):
        """Test: Vollständige Mitarbeiterdaten-Validierung"""
        print("🧪 Teste vollständige Mitarbeiterdaten-Validierung...")
        
        # Gültige Daten
        valid_data = {
            "driver_id": 123,
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max@example.com",
            "phone": "+43123456789",
            "driver_license_number": "B123456789",
            "hire_date": "2024-01-15",
            "status": "active"
        }
        
        errors = self.db_manager._validate_employee_data(valid_data)
        self.assertEqual(len(errors), 0, f"Keine Fehler erwartet, aber gefunden: {errors}")
        
        # Ungültige Daten
        invalid_data = {
            "driver_id": -1,
            "first_name": "A",
            "last_name": "B",
            "email": "invalid-email",
            "phone": "123",
            "driver_license_number": "1234",
            "hire_date": "invalid-date",
            "status": "invalid-status"
        }
        
        errors = self.db_manager._validate_employee_data(invalid_data)
        self.assertGreater(len(errors), 0, "Fehler sollten gefunden werden")
        
        print("✅ Vollständige Mitarbeiterdaten-Validierung funktioniert")
    
    def test_duplicate_checking(self):
        """Test: Duplikat-Prüfung"""
        print("🧪 Teste Duplikat-Prüfung...")
        
        # E-Mail-Duplikat prüfen
        result = self.db_manager._check_email_exists("max.mustermann@test.com")
        self.assertTrue(result, "E-Mail sollte als Duplikat erkannt werden")
        
        # E-Mail-Duplikat mit Ausschluss prüfen
        result = self.db_manager._check_email_exists("max.mustermann@test.com", exclude_driver_id=1)
        self.assertFalse(result, "E-Mail sollte nicht als Duplikat erkannt werden (Ausschluss)")
        
        # Führerscheinnummer-Duplikat prüfen
        result = self.db_manager._check_license_number_exists("B123456789")
        self.assertTrue(result, "Führerscheinnummer sollte als Duplikat erkannt werden")
        
        # Driver ID-Duplikat prüfen
        result = self.db_manager._check_driver_id_exists(1)
        self.assertTrue(result, "Driver ID sollte als existierend erkannt werden")
        
        print("✅ Duplikat-Prüfung funktioniert")
    
    def test_insert_with_validation(self):
        """Test: Mitarbeiter-Insert mit Validierung"""
        print("🧪 Teste Mitarbeiter-Insert mit Validierung...")
        
        # Gültiger Mitarbeiter
        valid_employee = {
            "driver_license_number": "C987654321",
            "first_name": "Anna",
            "last_name": "Schmidt",
            "phone": "+43987654321",
            "email": "anna.schmidt@test.com",
            "hire_date": "2024-02-01",
            "status": "active"
        }
        
        result = self.db_manager.insert_mitarbeiter(valid_employee)
        self.assertTrue(result, "Gültiger Mitarbeiter sollte eingefügt werden")
        
        # Ungültiger Mitarbeiter (E-Mail-Duplikat)
        invalid_employee = {
            "driver_license_number": "D111111111",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+43111111111",
            "email": "max.mustermann@test.com",  # Duplikat
            "hire_date": "2024-03-01",
            "status": "active"
        }
        
        with self.assertRaises(ValueError) as context:
            self.db_manager.insert_mitarbeiter(invalid_employee)
        
        self.assertIn("E-Mail-Adresse wird bereits verwendet", str(context.exception))
        
        print("✅ Mitarbeiter-Insert mit Validierung funktioniert")
    
    def test_update_with_validation(self):
        """Test: Mitarbeiter-Update mit Validierung"""
        print("🧪 Teste Mitarbeiter-Update mit Validierung...")
        
        # Gültiges Update
        valid_update = {
            "driver_license_number": "B123456789",
            "first_name": "Maximilian",  # Geändert
            "last_name": "Mustermann",
            "phone": "+43123456789",
            "email": "max.mustermann@test.com",
            "hire_date": "2024-01-15",
            "status": "active"
        }
        
        result = self.db_manager.update_mitarbeiter_by_id(1, valid_update)
        self.assertTrue(result, "Gültiges Update sollte funktionieren")
        
        # Ungültiges Update (ungültige E-Mail)
        invalid_update = {
            "driver_license_number": "B123456789",
            "first_name": "Max",
            "last_name": "Mustermann",
            "phone": "+43123456789",
            "email": "invalid-email",  # Ungültig
            "hire_date": "2024-01-15",
            "status": "active"
        }
        
        with self.assertRaises(ValueError) as context:
            self.db_manager.update_mitarbeiter_by_id(1, invalid_update)
        
        self.assertIn("Validierungsfehler", str(context.exception))
        
        print("✅ Mitarbeiter-Update mit Validierung funktioniert")
    
    def test_id_change_validation(self):
        """Test: Driver ID-Änderung mit Validierung"""
        print("🧪 Teste Driver ID-Änderung mit Validierung...")
        
        # Gültige ID-Änderung
        valid_data = {
            "driver_license_number": "B123456789",
            "first_name": "Max",
            "last_name": "Mustermann",
            "phone": "+43123456789",
            "email": "max.mustermann@test.com",
            "hire_date": "2024-01-15",
            "status": "active"
        }
        
        result = self.db_manager.update_mitarbeiter_id_and_data(1, 999, valid_data)
        self.assertTrue(result, "Gültige ID-Änderung sollte funktionieren")
        
        # Ungültige ID-Änderung (ID bereits verwendet)
        with self.assertRaises(ValueError) as context:
            self.db_manager.update_mitarbeiter_id_and_data(999, 1, valid_data)
        
        self.assertIn("Driver ID 1 wird bereits verwendet", str(context.exception))
        
        print("✅ Driver ID-Änderung mit Validierung funktioniert")

def run_validation_tests():
    """Führt alle Validierungstests aus"""
    print("🚀 Starte Task 4.1 Validierungstests...")
    print("=" * 60)
    
    # Test-Suite erstellen
    suite = unittest.TestLoader().loadTestsFromTestCase(TestValidationExtended)
    
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
        print("✅ Alle Validierungstests erfolgreich!")
        print("🎉 Task 4.1: Validierung erweitern - ABGESCHLOSSEN")
    else:
        print("❌ Einige Tests fehlgeschlagen")
        for test, traceback in result.failures + result.errors:
            print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # QApplication für PySide6 Tests
    app = QApplication([])
    
    # Tests ausführen
    success = run_validation_tests()
    
    # Cleanup
    app.quit()
    
    # Exit-Code setzen
    sys.exit(0 if success else 1) 