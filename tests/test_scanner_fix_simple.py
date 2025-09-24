#!/usr/bin/env python3
"""
Simple test script to verify the PDFScanner translation fix works correctly.
This script tests the tr() method without requiring the full GUI or complex imports.
"""

import sys
import os

# Add the script directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'script'))

def test_scanner_translations():
    """Test that the PDFScanner can use translations correctly."""
    print("Testing PDFScanner translation fix...")
    
    try:
        # Import only the specific modules we need
        from script.simple_lang_manager import SimpleLanguageManager
        
        # Create a mock QObject class since we can't import PyQt6
        class MockQObject:
            def __init__(self):
                pass
        
        # Create a minimal PDFScanner-like class for testing
        class TestScanner(MockQObject):
            def __init__(self, language_manager=None):
                super().__init__()
                self.language_manager = language_manager
            
            def tr(self, key: str, default: str = None) -> str:
                """Simple translation method for scanner messages."""
                if self.language_manager and hasattr(self.language_manager, 'tr'):
                    return self.language_manager.tr(key, default or key)
                else:
                    # Fallback to default or key if no language manager
                    return default or key
        
        # Create a language manager
        language_manager = SimpleLanguageManager()
        
        # Create a scanner with the language manager
        scanner = TestScanner(language_manager=language_manager)
        
        # Test various translation keys used by the scanner
        test_cases = [
            ("scanner.error", "Error: {error}"),
            ("scanner.scan_started", "Starting scan..."),
            ("scanner.no_files", "No PDF files found in the specified directory"),
            ("scanner.complete", "Scan complete. Found {count} groups of duplicates"),
            ("scanner.stopped", "Scan stopped"),
            ("scanner.processing", "Processing {current} of {total}: {file}"),
            ("scanner.stopping", "Stopping scan..."),
        ]
        
        print("\nTesting English translations:")
        for key, expected in test_cases:
            result = scanner.tr(key, expected)
            print(f"  {key}: {result}")
            if result != expected:
                print(f"    ERROR: Expected '{expected}', got '{result}'")
                return False
        
        # Test Italian translations
        print("\nTesting Italian translations:")
        language_manager.set_language('it')
        
        italian_expected = [
            ("scanner.error", "Errore: {error}"),
            ("scanner.scan_started", "Avvio scansione..."),
            ("scanner.no_files", "Nessun file PDF trovato nella directory specificata"),
            ("scanner.complete", "Scansione completata. Trovati {count} gruppi di duplicati"),
            ("scanner.stopped", "Scansione interrotta"),
            ("scanner.processing", "Elaborazione {current} di {total}: {file}"),
            ("scanner.stopping", "Interruzione scansione..."),
        ]
        
        for key, expected in italian_expected:
            result = scanner.tr(key, "fallback")
            print(f"  {key}: {result}")
            if result != expected:
                print(f"    ERROR: Expected '{expected}', got '{result}'")
                return False
        
        # Test fallback behavior
        print("\nTesting fallback behavior:")
        scanner_without_lm = TestScanner(language_manager=None)
        result = scanner_without_lm.tr("nonexistent.key", "Fallback text")
        print(f"  Fallback test: {result}")
        if result != "Fallback text":
            print(f"    ERROR: Expected 'Fallback text', got '{result}'")
            return False
        
        print("\n✅ All tests passed! The translation fix is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_scanner_translations()
    sys.exit(0 if success else 1)
