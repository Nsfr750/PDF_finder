#!/usr/bin/env python3
"""
Test script to verify that all imports work correctly.
"""

def test_imports():
    """Test all the imports that were causing issues."""
    try:
        print("Testing import of simple_lang_manager...")
        from script.simple_lang_manager import SimpleLanguageManager
        print("✓ simple_lang_manager imported successfully")
        
        print("Testing import of simple_translations...")
        from script.simple_translations import TRANSLATIONS, AVAILABLE_LANGUAGES
        print("✓ simple_translations imported successfully")
        
        print("Testing SimpleLanguageManager instantiation...")
        lang_manager = SimpleLanguageManager()
        print("✓ SimpleLanguageManager instantiated successfully")
        
        print("Testing translation functionality...")
        test_translation = lang_manager.tr("main_window.title")
        print(f"✓ Translation test successful: '{test_translation}'")
        
        print("Testing get_current_language method...")
        current_lang = lang_manager.get_current_language()
        print(f"✓ get_current_language test successful: '{current_lang}'")
        
        print("All imports and basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
