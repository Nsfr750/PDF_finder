#!/usr/bin/env python3
"""
Test script to verify that the updates.py correctly saves and reads configuration files 
in the config/ directory at the project root.
"""

import os
import sys
import json
from pathlib import Path

# Add the script directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'script'))

from utils.updates import UpdateChecker, CONFIG_DIR, UPDATES_FILE

def test_updates_config():
    """Test that the updates module correctly uses the config/ directory."""
    
    print("Testing updates configuration...")
    
    # Check the CONFIG_DIR path
    print(f"CONFIG_DIR: {CONFIG_DIR}")
    print(f"CONFIG_DIR absolute path: {CONFIG_DIR.absolute()}")
    print(f"CONFIG_DIR exists: {CONFIG_DIR.exists()}")
    
    # Expected config directory should be at project root
    expected_config_dir = Path(__file__).parent / 'config'
    print(f"Expected config directory: {expected_config_dir}")
    print(f"Expected config directory absolute path: {expected_config_dir.absolute()}")
    
    # Check if the paths match
    if CONFIG_DIR.absolute() == expected_config_dir.absolute():
        print("✓ Updates module correctly points to the project root config/ directory")
    else:
        print("✗ Updates module does not point to the expected config/ directory")
        return False
    
    # Check the UPDATES_FILE path
    print(f"UPDATES_FILE: {UPDATES_FILE}")
    print(f"UPDATES_FILE absolute path: {UPDATES_FILE.absolute()}")
    
    # Expected updates file should be at project root config
    expected_updates_file = expected_config_dir / 'updates.json'
    print(f"Expected updates file: {expected_updates_file}")
    print(f"Expected updates file absolute path: {expected_updates_file.absolute()}")
    
    # Check if the paths match
    if UPDATES_FILE.absolute() == expected_updates_file.absolute():
        print("✓ Updates file correctly points to the project root config/updates.json")
    else:
        print("✗ Updates file does not point to the expected config/updates.json")
        return False
    
    # Test the UpdateChecker functionality
    print("\nTesting UpdateChecker...")
    
    # Create an UpdateChecker instance
    checker = UpdateChecker(current_version="1.0.0")
    
    # Check the config path
    print(f"Checker config path: {checker.config_path}")
    print(f"Checker config path absolute: {checker.config_path.absolute()}")
    
    if checker.config_path.absolute() == expected_updates_file.absolute():
        print("✓ UpdateChecker correctly uses the project root config/updates.json")
    else:
        print("✗ UpdateChecker does not use the expected config/updates.json")
        return False
    
    # Test loading and saving configuration
    print("\nTesting configuration loading and saving...")
    
    # Load initial config
    initial_config = checker._load_config()
    print(f"Initial config: {initial_config}")
    
    # Modify and save config
    test_config = {
        'last_checked': '2025-01-01T00:00:00',
        'last_version': '1.0.0',
        'dont_ask_until': '2025-12-31T23:59:59'
    }
    
    checker.config = test_config
    checker._save_config()
    
    # Check if the file was created
    if UPDATES_FILE.exists():
        print("✓ Config file was created successfully")
        
        # Read and verify the content
        try:
            with open(UPDATES_FILE, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            
            print(f"Saved config: {saved_config}")
            
            if saved_config == test_config:
                print("✓ Config content matches what was saved")
            else:
                print("✗ Config content does not match what was saved")
                return False
                
        except Exception as e:
            print(f"✗ Error reading config file: {e}")
            return False
    else:
        print("✗ Config file was not created")
        return False
    
    # Test loading the saved config
    new_checker = UpdateChecker(current_version="1.0.0")
    loaded_config = new_checker._load_config()
    
    if loaded_config == test_config:
        print("✓ Config was loaded successfully")
    else:
        print("✗ Config was not loaded correctly")
        print(f"Expected: {test_config}")
        print(f"Got: {loaded_config}")
        return False
    
    print("✓ All updates configuration tests passed!")
    return True

if __name__ == "__main__":
    success = test_updates_config()
    sys.exit(0 if success else 1)
