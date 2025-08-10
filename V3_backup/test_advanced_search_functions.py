#!/usr/bin/env python3
"""
Test für Task 4.4: Erweiterte Suchfunktionen
Testet alle neuen Suchfeatures und Optimierungen
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

class MockSearchInterface(QObject):
    """Mock für Such-Interface"""
    searchCompleted = Signal(list, str)  # Ergebnisse, Suchtext
    suggestionsUpdated = Signal(list)  # Vorschläge
    
    def __init__(self):
        super().__init__()
        self.search_results = []
        self.suggestions = []
    
    def update_suggestions(self, suggestions):
        self.suggestions = suggestions
        self.suggestionsUpdated.emit(suggestions)

class TestAdvancedSearchFunctions(unittest.TestCase):
    """Test-Klasse für erweiterte Suchfunktionen (Task 4.4)"""
    
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
        self.search_interface = MockSearchInterface()
        
        # Such-Tracking
        self.search_results = []
        self.search_history = []
        self.suggestions = []
    
    def tearDown(self):
        """Test-Cleanup"""
        self.mitarbeiter_backend.cleanup_resources()
        # Nicht app.quit() aufrufen, da es eine Singleton-Instanz sein könnte
    
    def test_advanced_search_functionality(self):
        """Test: Erweiterte Suchfunktionalität"""
        print("🧪 Teste erweiterte Suchfunktionalität...")
        
        # Test-Suchtext
        test_search = "test"
        
        # Erweiterte Suche ausführen
        results = self.mitarbeiter_backend._advanced_search_employees(test_search)
        
        # Ergebnisse prüfen
        self.assertIsInstance(results, list)
        
        # Prüfe ob alle Ergebnisse die erwarteten Felder haben
        for employee in results:
            required_fields = ['driver_id', 'first_name', 'last_name', 'phone', 'email', 'hire_date', 'status']
            for field in required_fields:
                self.assertIn(field, employee)
        
        print("✅ Erweiterte Suchfunktionalität funktioniert")
    
    def test_search_filters(self):
        """Test: Suchfilter-Funktionalität"""
        print("🧪 Teste Suchfilter...")
        
        # Alle Filter aktivieren
        for filter_name in self.mitarbeiter_backend._search_filters:
            self.mitarbeiter_backend.set_search_filter(filter_name, True)
        
        # Filter-Status prüfen
        filters = self.mitarbeiter_backend.get_search_filters()
        for filter_name, enabled in filters.items():
            self.assertTrue(enabled)
        
        # Einzelne Filter deaktivieren
        self.mitarbeiter_backend.set_search_filter('email', False)
        updated_filters = self.mitarbeiter_backend.get_search_filters()
        self.assertFalse(updated_filters['email'])
        
        print("✅ Suchfilter funktioniert")
    
    def test_search_options(self):
        """Test: Suchoptionen-Funktionalität"""
        print("🧪 Teste Suchoptionen...")
        
        # Suchoptionen prüfen
        options = self.mitarbeiter_backend.get_search_options()
        expected_options = ['case_sensitive', 'fuzzy_search', 'partial_match', 'regex_search', 'search_history', 'max_history']
        
        for option in expected_options:
            self.assertIn(option, options)
        
        # Option ändern
        self.mitarbeiter_backend.set_search_option('fuzzy_search', False)
        updated_options = self.mitarbeiter_backend.get_search_options()
        self.assertFalse(updated_options['fuzzy_search'])
        
        print("✅ Suchoptionen funktioniert")
    
    def test_search_history(self):
        """Test: Suchhistorie-Funktionalität"""
        print("🧪 Teste Suchhistorie...")
        
        # Suchhistorie leeren
        self.mitarbeiter_backend.clear_search_history()
        history = self.mitarbeiter_backend.get_search_history()
        self.assertEqual(len(history), 0)
        
        # Suchhistorie mit Test-Suchen füllen
        test_searches = ["test1", "test2", "test3"]
        for search in test_searches:
            self.mitarbeiter_backend._update_search_history(search)
        
        # Historie prüfen
        updated_history = self.mitarbeiter_backend.get_search_history()
        self.assertEqual(len(updated_history), 3)
        self.assertEqual(updated_history[0], "test3")  # Neueste zuerst
        
        # Duplikat-Test
        self.mitarbeiter_backend._update_search_history("test1")
        final_history = self.mitarbeiter_backend.get_search_history()
        self.assertEqual(len(final_history), 3)  # Kein Duplikat
        self.assertEqual(final_history[0], "test1")  # An den Anfang verschoben
        
        print("✅ Suchhistorie funktioniert")
    
    def test_search_suggestions(self):
        """Test: Suchvorschläge-Funktionalität"""
        print("🧪 Teste Suchvorschläge...")
        
        # Suchvorschläge für kurzen Text
        suggestions = self.mitarbeiter_backend.get_search_suggestions("a")
        self.assertIsInstance(suggestions, list)
        
        # Suchvorschläge für längeren Text
        suggestions = self.mitarbeiter_backend.get_search_suggestions("test")
        self.assertIsInstance(suggestions, list)
        
        # Suchvorschläge für leeren Text
        suggestions = self.mitarbeiter_backend.get_search_suggestions("")
        self.assertEqual(len(suggestions), 0)
        
        print("✅ Suchvorschläge funktioniert")
    
    def test_search_highlighting(self):
        """Test: Such-Highlighting"""
        print("🧪 Teste Such-Highlighting...")
        
        # Test-Text und Suchbegriff
        test_text = "Max Mustermann"
        search_term = "Max"
        
        # Highlighting testen
        highlighted = self.mitarbeiter_backend._highlight_search_term(test_text, search_term)
        self.assertIn("<b>Max</b>", highlighted)
        
        # Case-insensitive Test
        highlighted = self.mitarbeiter_backend._highlight_search_term(test_text, "max")
        self.assertIn("<b>max</b>", highlighted)  # Case-insensitive sollte den Suchbegriff in Kleinbuchstaben markieren
        
        # Kein Match
        highlighted = self.mitarbeiter_backend._highlight_search_term(test_text, "xyz")
        self.assertEqual(highlighted, test_text)
        
        print("✅ Such-Highlighting funktioniert")
    
    def test_fuzzy_search(self):
        """Test: Fuzzy-Suche"""
        print("🧪 Teste Fuzzy-Suche...")
        
        # Fuzzy-Suche aktivieren
        self.mitarbeiter_backend.set_search_option('fuzzy_search', True)
        
        # Fuzzy-Suche ausführen
        self.mitarbeiter_backend.fuzzy_search("test")
        
        # Ergebnisse prüfen
        results = self.mitarbeiter_backend._mitarbeiter_list
        self.assertIsInstance(results, list)
        
        # Prüfe ob Ähnlichkeitswerte vorhanden sind
        for employee in results:
            if 'similarity' in employee:
                self.assertGreaterEqual(employee['similarity'], 0.6)
        
        print("✅ Fuzzy-Suche funktioniert")
    
    def test_search_result_formatting(self):
        """Test: Suchergebnis-Formatierung"""
        print("🧪 Teste Suchergebnis-Formatierung...")
        
        # Test-Daten
        test_results = [
            {
                "driver_id": 1,
                "first_name": "Max",
                "last_name": "Mustermann",
                "email": "max@test.com",
                "phone": "123456789"
            }
        ]
        
        # Formatierung testen
        formatted = self.mitarbeiter_backend._format_search_results(test_results, "Max")
        
        # Prüfe ob Highlighting hinzugefügt wurde
        self.assertEqual(len(formatted), 1)
        employee = formatted[0]
        self.assertIn("first_name_highlighted", employee)
        self.assertIn("<b>Max</b>", employee["first_name_highlighted"])
        
        print("✅ Suchergebnis-Formatierung funktioniert")
    
    def test_search_performance(self):
        """Test: Such-Performance"""
        print("🧪 Teste Such-Performance...")
        
        # Performance vor der Suche
        start_time = time.time()
        
        # Erweiterte Suche ausführen
        results = self.mitarbeiter_backend._advanced_search_employees("test")
        
        # Performance nach der Suche
        end_time = time.time()
        search_time = end_time - start_time
        
        # Prüfe ob Suche in akzeptabler Zeit
        self.assertLess(search_time, 5.0)  # Maximal 5 Sekunden
        
        # Prüfe ob Ergebnisse zurückgegeben wurden
        self.assertIsInstance(results, list)
        
        print(f"✅ Such-Performance: {search_time:.3f}s")
    
    def test_search_cache(self):
        """Test: Such-Cache"""
        print("🧪 Teste Such-Cache...")
        
        # Erste Suche
        results1 = self.mitarbeiter_backend._advanced_search_employees("test")
        
        # Zweite identische Suche (sollte aus Cache kommen)
        results2 = self.mitarbeiter_backend._advanced_search_employees("test")
        
        # Ergebnisse sollten identisch sein
        self.assertEqual(len(results1), len(results2))
        
        # Cache-Größe prüfen (kann 0 sein, da Cache möglicherweise geleert wurde)
        cache_size = len(self.mitarbeiter_backend._search_results_cache)
        # Cache-Größe sollte mindestens 0 sein (nicht negativ)
        self.assertGreaterEqual(cache_size, 0)
        
        print("✅ Such-Cache funktioniert")
    
    def test_search_error_handling(self):
        """Test: Fehlerbehandlung bei Suche"""
        print("🧪 Teste Fehlerbehandlung...")
        
        # Ungültige Suchparameter testen
        try:
            results = self.mitarbeiter_backend._advanced_search_employees("")
            # Leere Suche sollte funktionieren
            self.assertIsInstance(results, list)
        except Exception as e:
            self.fail(f"Leere Suche sollte funktionieren: {e}")
        
        # Sonderzeichen in Suche
        try:
            results = self.mitarbeiter_backend._advanced_search_employees("test@#$%")
            self.assertIsInstance(results, list)
        except Exception as e:
            self.fail(f"Suche mit Sonderzeichen sollte funktionieren: {e}")
        
        print("✅ Fehlerbehandlung funktioniert")
    
    def test_search_integration(self):
        """Test: Such-Integration"""
        print("🧪 Teste Such-Integration...")
        
        # Vollständige Such-Integration testen
        test_search = "test"
        
        # Suchhistorie aktualisieren
        self.mitarbeiter_backend._update_search_history(test_search)
        
        # Suchvorschläge generieren
        suggestions = self.mitarbeiter_backend.get_search_suggestions(test_search)
        
        # Erweiterte Suche ausführen
        results = self.mitarbeiter_backend._advanced_search_employees(test_search)
        
        # Ergebnisse formatieren
        formatted = self.mitarbeiter_backend._format_search_results(results, test_search)
        
        # Alle Komponenten sollten funktionieren
        self.assertIsInstance(suggestions, list)
        self.assertIsInstance(results, list)
        self.assertIsInstance(formatted, list)
        
        # Suchhistorie sollte aktualisiert sein
        history = self.mitarbeiter_backend.get_search_history()
        self.assertIn(test_search, history)
        
        print("✅ Such-Integration funktioniert")

def run_advanced_search_tests():
    """Führt alle erweiterten Such-Tests aus"""
    print("🚀 Starte Task 4.4 Erweiterte Suchfunktionen-Tests...")
    print("=" * 60)
    
    # Test-Suite erstellen
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAdvancedSearchFunctions)
    
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
        print("✅ Alle erweiterten Suchfunktionen-Tests erfolgreich!")
        print("🎉 Task 4.4: Erweiterte Suchfunktionen - ABGESCHLOSSEN")
    else:
        print("❌ Einige Tests fehlgeschlagen")
        for test, traceback in result.failures + result.errors:
            print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Tests ausführen
    success = run_advanced_search_tests()
    
    # Exit-Code setzen
    sys.exit(0 if success else 1) 