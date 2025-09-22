#!/usr/bin/env python3
"""
Test script to verify that all translation keys are working correctly.
"""

import sys
import os

# Add the script directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'script'))

def test_translations():
    """Test all translation keys."""
    try:
        print("Testing import of simple_lang_manager...")
        from simple_lang_manager import SimpleLanguageManager
        print("✓ simple_lang_manager imported successfully")

        print("Testing import of simple_translations...")
        from simple_translations import TRANSLATIONS, AVAILABLE_LANGUAGES
        print("✓ simple_translations imported successfully")

        print("Testing SimpleLanguageManager instantiation...")
        lang_manager = SimpleLanguageManager()
        print("✓ SimpleLanguageManager instantiated successfully")

        # Test English translations
        print("\n--- Testing English translations ---")
        lang_manager.set_language('en')
        
        # Test some common keys
        test_keys = [
            "main_window.title",
            "common.ok", 
            "common.cancel",
            "settings.title",
            "file.open",
            "help.about"
        ]
        
        for key in test_keys:
            translation = lang_manager.tr(key)
            print(f"  {key}: '{translation}'")
        
        # Test Italian translations
        print("\n--- Testing Italian translations ---")
        lang_manager.set_language('it')
        
        for key in test_keys:
            translation = lang_manager.tr(key)
            print(f"  {key}: '{translation}'")
        
        # Test sponsor dialog translations
        print("\n--- Testing Sponsor dialog translations ---")
        sponsor_keys = [
            "sponsor.window_title",
            "sponsor.title", 
            "sponsor.message",
            "sponsor.links.github_sponsors",
            "sponsor.links.paypal",
            "sponsor.monero.label",
            "sponsor.qr_tooltip",
            "sponsor.ways_to_support",
            "sponsor.other_ways.title",
            "sponsor.other_ways.star",
            "sponsor.other_ways.report",
            "sponsor.other_ways.share",
            "sponsor.buttons.donate_paypal",
            "sponsor.buttons.copy_monero"
        ]
        
        print("English sponsor translations:")
        lang_manager.set_language('en')
        for key in sponsor_keys:
            translation = lang_manager.tr(key)
            print(f"  {key}: '{translation}'")
        
        print("Italian sponsor translations:")
        lang_manager.set_language('it')
        for key in sponsor_keys:
            translation = lang_manager.tr(key)
            print(f"  {key}: '{translation}'")
        
        # Test about dialog translations
        print("\n--- Testing About dialog translations ---")
        about_keys = [
            "about.title",
            "about.version",
            "about.description", 
            "about.system_info",
            "about.copyright",
            "about.close"
        ]
        
        print("English about translations:")
        lang_manager.set_language('en')
        for key in about_keys:
            translation = lang_manager.tr(key)
            print(f"  {key}: '{translation}'")
        
        print("Italian about translations:")
        lang_manager.set_language('it')
        for key in about_keys:
            translation = lang_manager.tr(key)
            print(f"  {key}: '{translation}'")
        
        print("\n✓ All translation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_translations()
    sys.exit(0 if success else 1)
