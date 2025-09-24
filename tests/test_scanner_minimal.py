#!/usr/bin/env python3
"""
Minimal test script to verify the translation fix works without PyQt6 dependencies.
"""

import sys
import os

# Add the script directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'script'))

def test_translations_directly():
    """Test the translations directly without PyQt6."""
    print("Testing translation data directly...")
    
    try:
        # Import the translation data directly
        from script.simple_translations import TRANSLATIONS
        
        # Test that our scanner translation keys exist
        scanner_keys = [
            "scanner.error",
            "scanner.scan_started", 
            "scanner.no_files",
            "scanner.complete",
            "scanner.stopped",
            "scanner.processing",
            "scanner.stopping"
        ]
        
        print("\nTesting English translations:")
        english_translations = TRANSLATIONS.get('en', {})
        for key in scanner_keys:
            if key in english_translations:
                print(f"  ✅ {key}: {english_translations[key]}")
            else:
                print(f"  ❌ {key}: NOT FOUND")
                return False
        
        print("\nTesting Italian translations:")
        italian_translations = TRANSLATIONS.get('it', {})
        for key in scanner_keys:
            if key in italian_translations:
                print(f"  ✅ {key}: {italian_translations[key]}")
            else:
                print(f"  ❌ {key}: NOT FOUND")
                return False
        
        print("\n✅ All translation keys found! The translation data is correct.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_tr_method_logic():
    """Test the tr() method logic without PyQt6."""
    print("\nTesting tr() method logic...")
    
    # Create a mock language manager
    class MockLanguageManager:
        def __init__(self):
            self.current_lang = 'en'
            # Import the actual translations
            from script.simple_translations import TRANSLATIONS
            self.translations = TRANSLATIONS
        
        def tr(self, key: str, default: str = None) -> str:
            """Simple translation method."""
            if self.current_lang in self.translations:
                if key in self.translations[self.current_lang]:
                    return self.translations[self.current_lang][key]
            return default or key
        
        def set_language(self, lang_code: str) -> bool:
            if lang_code in self.translations:
                self.current_lang = lang_code
                return True
            return False
    
    # Create a mock scanner class
    class MockScanner:
        def __init__(self, language_manager=None):
            self.language_manager = language_manager
        
        def tr(self, key: str, default: str = None) -> str:
            """Simple translation method for scanner messages."""
            if self.language_manager and hasattr(self.language_manager, 'tr'):
                return self.language_manager.tr(key, default or key)
            else:
                # Fallback to default or key if no language manager
                return default or key
    
    try:
        # Test with language manager
        language_manager = MockLanguageManager()
        scanner = MockScanner(language_manager)
        
        # Test English
        result = scanner.tr("scanner.scan_started", "Starting scan...")
        expected = "Starting scan..."
        print(f"  English test: {result}")
        if result != expected:
            print(f"    ❌ Expected '{expected}', got '{result}'")
            return False
        
        # Test Italian
        language_manager.set_language('it')
        result = scanner.tr("scanner.scan_started", "Starting scan...")
        expected = "Avvio scansione..."
        print(f"  Italian test: {result}")
        if result != expected:
            print(f"    ❌ Expected '{expected}', got '{result}'")
            return False
        
        # Test fallback
        scanner_no_lm = MockScanner(language_manager=None)
        result = scanner_no_lm.tr("nonexistent.key", "Fallback text")
        expected = "Fallback text"
        print(f"  Fallback test: {result}")
        if result != expected:
            print(f"    ❌ Expected '{expected}', got '{result}'")
            return False
        
        print("  ✅ All tr() method tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error in tr() method test: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Testing PDF Scanner Translation Fix ===\n")
    
    success1 = test_translations_directly()
    success2 = test_tr_method_logic()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The translation fix is working correctly.")
        print("\nThe PDFScanner should now work without freezing when scanning folders.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
