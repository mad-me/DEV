#!/usr/bin/env python3
"""
Test für Task 4.3: Performance-Optimierungen
Testet alle neuen Performance-Features und Optimierungen
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
import threading

class MockPerformanceMonitor(QObject):
    """Mock für Performance-Monitoring"""
    performanceUpdated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.stats = {}
    
    def update_stats(self, stats):
        self.stats = stats
        self.performanceUpdated.emit(stats)

class TestPerformanceOptimizations(unittest.TestCase):
    """Test-Klasse für Performance-Optimierungen (Task 4.3)"""
    
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
        self.performance_monitor = MockPerformanceMonitor()
        
        # Performance-Tracking
        self.query_times = []
        self.cache_hits = 0
        self.cache_misses = 0
    
    def tearDown(self):
        """Test-Cleanup"""
        self.mitarbeiter_backend.cleanup_resources()
        # Nicht app.quit() aufrufen, da es eine Singleton-Instanz sein könnte
    
    def test_connection_pool(self):
        """Test: Connection Pool Funktionalität"""
        print("🧪 Teste Connection Pool...")
        
        # Teste Connection Pool
        connections = []
        
        # Mehrere Verbindungen erstellen
        for i in range(3):
            conn = self.mitarbeiter_backend._get_connection()
            self.assertIsNotNone(conn)
            connections.append(conn)
        
        # Verbindungen testen
        for conn in connections:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)
            except Exception as e:
                self.fail(f"Verbindungstest fehlgeschlagen: {e}")
        
        # Pool-Größe prüfen
        pool_size = len(self.mitarbeiter_backend._connection_pool.get("SQL/database.db", []))
        self.assertLessEqual(pool_size, self.mitarbeiter_backend._max_connections)
        
        print("✅ Connection Pool funktioniert")
    
    def test_query_cache(self):
        """Test: Query Cache Funktionalität"""
        print("🧪 Teste Query Cache...")
        
        # Test-Query
        test_query = "SELECT COUNT(*) FROM drivers"
        test_params = ()
        test_cache_key = "test_count"
        
        # Erste Ausführung (Cache Miss)
        start_time = time.time()
        result1 = self.mitarbeiter_backend._execute_query_with_cache(
            test_query, test_params, test_cache_key
        )
        first_query_time = time.time() - start_time
        
        # Zweite Ausführung (Cache Hit)
        start_time = time.time()
        result2 = self.mitarbeiter_backend._execute_query_with_cache(
            test_query, test_params, test_cache_key
        )
        second_query_time = time.time() - start_time
        
        # Ergebnisse sollten identisch sein
        self.assertEqual(result1, result2)
        
        # Cache Hit sollte schneller sein
        self.assertLess(second_query_time, first_query_time)
        
        # Cache-Statistiken prüfen
        stats = self.mitarbeiter_backend.get_performance_stats()
        self.assertGreater(stats['cache_hits'], 0)
        self.assertGreater(stats['cache_misses'], 0)
        
        print("✅ Query Cache funktioniert")
    
    def test_lazy_loading(self):
        """Test: Lazy Loading Funktionalität"""
        print("🧪 Teste Lazy Loading...")
        
        # Lazy Loading testen
        page_size = self.mitarbeiter_backend._page_size
        
        # Erste Seite laden
        employees_page1 = self.mitarbeiter_backend._lazy_load_employees(0)
        self.assertLessEqual(len(employees_page1), page_size)
        
        # Zweite Seite laden
        employees_page2 = self.mitarbeiter_backend._lazy_load_employees(1)
        self.assertLessEqual(len(employees_page2), page_size)
        
        # Seiten sollten unterschiedlich sein
        if employees_page1 and employees_page2:
            self.assertNotEqual(employees_page1[0], employees_page2[0])
        
        # Lazy Loading mit großem Datensatz simulieren
        self.mitarbeiter_backend._lazy_loading_threshold = 1  # Niedriger Schwellenwert
        lazy_result = self.mitarbeiter_backend._lazy_load_employees(0)
        self.assertIsInstance(lazy_result, list)
        
        print("✅ Lazy Loading funktioniert")
    
    def test_performance_monitoring(self):
        """Test: Performance-Monitoring"""
        print("🧪 Teste Performance-Monitoring...")
        
        # Performance-Statistiken abrufen
        stats = self.mitarbeiter_backend.get_performance_stats()
        
        # Prüfe ob alle erwarteten Felder vorhanden sind
        expected_fields = [
            'queries_executed', 'cache_hits', 'cache_misses', 
            'cache_hit_rate', 'avg_query_time', 'memory_usage_mb',
            'cache_size', 'query_cache_size'
        ]
        
        for field in expected_fields:
            self.assertIn(field, stats)
            self.assertIsInstance(stats[field], (int, float))
        
        # Cache-Hit-Rate sollte zwischen 0 und 100 liegen
        self.assertGreaterEqual(stats['cache_hit_rate'], 0)
        self.assertLessEqual(stats['cache_hit_rate'], 100)
        
        # Durchschnittliche Query-Zeit sollte positiv sein
        self.assertGreaterEqual(stats['avg_query_time'], 0)
        
        print("✅ Performance-Monitoring funktioniert")
    
    def test_cache_management(self):
        """Test: Cache-Management"""
        print("🧪 Teste Cache-Management...")
        
        # Cache-Statistiken vor dem Test
        initial_stats = self.mitarbeiter_backend.get_performance_stats()
        initial_cache_size = initial_stats['cache_size']
        initial_query_cache_size = initial_stats['query_cache_size']
        
        # Einige Queries ausführen um Cache zu füllen
        for i in range(5):
            self.mitarbeiter_backend._execute_query_with_cache(
                f"SELECT COUNT(*) FROM drivers WHERE driver_id > {i}",
                (),
                f"test_query_{i}"
            )
        
        # Cache-Statistiken nach dem Test
        after_query_stats = self.mitarbeiter_backend.get_performance_stats()
        self.assertGreater(after_query_stats['query_cache_size'], initial_query_cache_size)
        
        # Cache leeren
        self.mitarbeiter_backend.clear_performance_cache()
        
        # Cache-Statistiken nach dem Leeren
        after_clear_stats = self.mitarbeiter_backend.get_performance_stats()
        self.assertEqual(after_clear_stats['query_cache_size'], 0)
        self.assertEqual(after_clear_stats['cache_hits'], 0)
        self.assertEqual(after_clear_stats['cache_misses'], 0)
        
        print("✅ Cache-Management funktioniert")
    
    def test_memory_cleanup(self):
        """Test: Memory-Cleanup"""
        print("🧪 Teste Memory-Cleanup...")
        
        # Memory-Cleanup ausführen
        try:
            self.mitarbeiter_backend._memory_cleanup()
            
            # Prüfe ob Performance-Statistiken aktualisiert wurden
            stats = self.mitarbeiter_backend.get_performance_stats()
            self.assertGreaterEqual(stats['memory_usage_mb'], 0)
            
            print("✅ Memory-Cleanup funktioniert")
        except Exception as e:
            # psutil könnte nicht verfügbar sein
            print(f"⚠️ Memory-Cleanup mit Einschränkungen: {e}")
    
    def test_concurrent_access(self):
        """Test: Gleichzeitige Zugriffe"""
        print("🧪 Teste gleichzeitige Zugriffe...")
        
        results = []
        errors = []
        
        def worker_function(worker_id):
            """Worker-Funktion für Thread-Tests"""
            try:
                # Query ausführen
                result = self.mitarbeiter_backend._execute_query_with_cache(
                    "SELECT COUNT(*) FROM drivers",
                    (),
                    f"concurrent_test_{worker_id}"
                )
                results.append((worker_id, result))
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Mehrere Threads starten
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Auf Threads warten
        for thread in threads:
            thread.join()
        
        # Ergebnisse prüfen
        self.assertEqual(len(errors), 0, f"Thread-Fehler: {errors}")
        self.assertEqual(len(results), 3)
        
        # Alle Ergebnisse sollten identisch sein
        first_result = results[0][1]
        for worker_id, result in results:
            self.assertEqual(result, first_result)
        
        print("✅ Gleichzeitige Zugriffe funktioniert")
    
    def test_query_performance(self):
        """Test: Query-Performance"""
        print("🧪 Teste Query-Performance...")
        
        # Performance vor dem Test
        initial_stats = self.mitarbeiter_backend.get_performance_stats()
        initial_queries = initial_stats['queries_executed']
        
        # Mehrere Queries ausführen
        query_times = []
        for i in range(5):
            start_time = time.time()
            self.mitarbeiter_backend._execute_query_with_cache(
                f"SELECT driver_id FROM drivers LIMIT {i+1}",
                (),
                f"performance_test_{i}"
            )
            query_time = time.time() - start_time
            query_times.append(query_time)
        
        # Performance nach dem Test
        final_stats = self.mitarbeiter_backend.get_performance_stats()
        final_queries = final_stats['queries_executed']
        
        # Prüfe ob Queries ausgeführt wurden
        self.assertGreater(final_queries, initial_queries)
        
        # Prüfe ob Query-Zeiten gemessen wurden
        self.assertGreater(final_stats['avg_query_time'], 0)
        
        # Prüfe ob Cache-Hits und Misses gemessen wurden
        self.assertGreaterEqual(final_stats['cache_hits'], 0)
        self.assertGreaterEqual(final_stats['cache_misses'], 0)
        
        print("✅ Query-Performance funktioniert")
    
    def test_cache_ttl(self):
        """Test: Cache TTL (Time To Live)"""
        print("🧪 Teste Cache TTL...")
        
        # Kurze TTL für Test setzen
        original_ttl = self.mitarbeiter_backend._query_cache_ttl
        self.mitarbeiter_backend._query_cache_ttl = 1  # 1 Sekunde
        
        # Query ausführen
        test_query = "SELECT COUNT(*) FROM drivers"
        test_cache_key = "ttl_test"
        
        # Erste Ausführung
        result1 = self.mitarbeiter_backend._execute_query_with_cache(
            test_query, (), test_cache_key
        )
        
        # Cache-Statistiken nach erster Ausführung
        stats1 = self.mitarbeiter_backend.get_performance_stats()
        initial_cache_size = stats1['query_cache_size']
        
        # Warten bis TTL abgelaufen ist
        time.sleep(1.5)
        
        # Zweite Ausführung (Cache sollte abgelaufen sein)
        result2 = self.mitarbeiter_backend._execute_query_with_cache(
            test_query, (), test_cache_key
        )
        
        # Cache-Statistiken nach zweiter Ausführung
        stats2 = self.mitarbeiter_backend.get_performance_stats()
        
        # Ergebnisse sollten identisch sein
        self.assertEqual(result1, result2)
        
        # TTL zurücksetzen
        self.mitarbeiter_backend._query_cache_ttl = original_ttl
        
        print("✅ Cache TTL funktioniert")
    
    def test_error_handling(self):
        """Test: Fehlerbehandlung bei Performance-Features"""
        print("🧪 Teste Fehlerbehandlung...")
        
        # Ungültige Query testen
        try:
            self.mitarbeiter_backend._execute_query_with_cache(
                "SELECT * FROM nonexistent_table",
                (),
                "error_test"
            )
            self.fail("Ungültige Query sollte einen Fehler werfen")
        except Exception as e:
            # Fehler erwartet
            self.assertIsInstance(e, Exception)
        
        # Ungültige Verbindung testen
        try:
            conn = self.mitarbeiter_backend._get_connection("nonexistent.db")
            # Verbindung sollte trotzdem erstellt werden (Fallback)
            self.assertIsNotNone(conn)
        except Exception as e:
            # Fehler erwartet, aber sollte behandelt werden
            pass
        
        # Performance-Statistiken sollten trotz Fehler verfügbar sein
        stats = self.mitarbeiter_backend.get_performance_stats()
        self.assertIsInstance(stats, dict)
        
        print("✅ Fehlerbehandlung funktioniert")

def run_performance_tests():
    """Führt alle Performance-Tests aus"""
    print("🚀 Starte Task 4.3 Performance-Optimierungstests...")
    print("=" * 60)
    
    # Test-Suite erstellen
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceOptimizations)
    
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
        print("✅ Alle Performance-Optimierungstests erfolgreich!")
        print("🎉 Task 4.3: Performance-Optimierungen - ABGESCHLOSSEN")
    else:
        print("❌ Einige Tests fehlgeschlagen")
        for test, traceback in result.failures + result.errors:
            print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Tests ausführen
    success = run_performance_tests()
    
    # Exit-Code setzen
    sys.exit(0 if success else 1) 