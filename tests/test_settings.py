#!/usr/bin/env python3
"""
Test script to verify that the settings.py correctly saves and reads configuration files 
in the config/ directory at the project root.
"""

import os
import sys
import json
from pathlib import Path

# Add the script directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'script'))

from utils.settings import AppSettings

def test_settings_config():
    """Test that the settings module correctly uses the config/ directory."""
    
    print("Testing settings configuration...")
    
    # Create an AppSettings instance
    settings = AppSettings()
    
    # Check the config path
    print(f"Settings config path: {settings._config_path}")
    print(f"Settings config path absolute: {settings._config_path.absolute()}")
    
    # Expected config directory should be at project root
    expected_config_dir = Path(__file__).parent / 'config'
    expected_settings_file = expected_config_dir / 'settings.json'
    
    print(f"Expected config directory: {expected_config_dir}")
    print(f"Expected settings file: {expected_settings_file}")
    print(f"Expected settings file absolute: {expected_settings_file.absolute()}")
    
    # Check if the paths match
    if settings._config_path.absolute() == expected_settings_file.absolute():
        print("✓ Settings module correctly points to the project root config/settings.json")
    else:
        print("✗ Settings module does not point to the expected config/settings.json")
        return False
    
    # Check if the config directory exists
    if expected_config_dir.exists():
        print("✓ Config directory exists")
    else:
        print("✗ Config directory does not exist")
        return False
    
    # Test setting and getting values
    print("\nTesting setting and getting values...")
    
    # Test simple key-value
    settings.set('test_key', 'test_value')
    retrieved_value = settings.get('test_key')
    
    if retrieved_value == 'test_value':
        print("✓ Simple key-value set/get works")
    else:
        print("✗ Simple key-value set/get failed")
        print(f"Expected: test_value, Got: {retrieved_value}")
        return False
    
    # Test nested key-value
    settings.set('nested.deep.key', 'nested_value')
    retrieved_nested = settings.get('nested.deep.key')
    
    if retrieved_nested == 'nested_value':
        print("✓ Nested key-value set/get works")
    else:
        print("✗ Nested key-value set/get failed")
        print(f"Expected: nested_value, Got: {retrieved_nested}")
        return False
    
    # Test default value
    default_value = settings.get('nonexistent.key', 'default_value')
    if default_value == 'default_value':
        print("✓ Default value works")
    else:
        print("✗ Default value failed")
        print(f"Expected: default_value, Got: {default_value}")
        return False
    
    # Test window geometry
    print("\nTesting window geometry...")
    test_geometry = b'\x01\x02\x03\x04\x05'
    settings.set_window_geometry(test_geometry)
    retrieved_geometry = settings.get_window_geometry()
    
    if retrieved_geometry == test_geometry:
        print("✓ Window geometry set/get works")
    else:
        print("✗ Window geometry set/get failed")
        print(f"Expected: {test_geometry}, Got: {retrieved_geometry}")
        return False
    
    # Test window state
    print("\nTesting window state...")
    test_state = b'\x05\x04\x03\x02\x01'
    settings.set_window_state(test_state)
    retrieved_state = settings.get_window_state()
    
    if retrieved_state == test_state:
        print("✓ Window state set/get works")
    else:
        print("✗ Window state set/get failed")
        print(f"Expected: {test_state}, Got: {retrieved_state}")
        return False
    
    # Test language settings
    print("\nTesting language settings...")
    settings.set_language('it')
    retrieved_language = settings.get_language()
    
    if retrieved_language == 'it':
        print("✓ Language set/get works")
    else:
        print("✗ Language set/get failed")
        print(f"Expected: it, Got: {retrieved_language}")
        return False
    
    # Test persistence - check if the file was actually saved
    print("\nTesting persistence...")
    if expected_settings_file.exists():
        print("✓ Settings file was created")
        
        try:
            with open(expected_settings_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            print(f"Saved data: {saved_data}")
            
            # Check if our test values are in the saved data
            if saved_data.get('test_key') == 'test_value':
                print("✓ Test value was saved correctly")
            else:
                print("✗ Test value was not saved correctly")
                return False
                
            if saved_data.get('nested', {}).get('deep', {}).get('key') == 'nested_value':
                print("✓ Nested test value was saved correctly")
            else:
                print("✗ Nested test value was not saved correctly")
                return False
                
        except Exception as e:
            print(f"✗ Error reading settings file: {e}")
            return False
    else:
        print("✗ Settings file was not created")
        return False
    
    # Test loading from a new instance
    print("\nTesting loading from new instance...")
    new_settings = AppSettings()
    
    # Check if the values were loaded correctly
    if new_settings.get('test_key') == 'test_value':
        print("✓ Values were loaded correctly from new instance")
    else:
        print("✗ Values were not loaded correctly from new instance")
        return False
    
    print("✓ All settings configuration tests passed!")
    return True

if __name__ == "__main__":
    success = test_settings_config()
    sys.exit(0 if success else 1)
