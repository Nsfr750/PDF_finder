#!/usr/bin/env python3
"""
Test script to check if imports work correctly
"""
print("Starting import test...")

try:
    print("Importing standard libraries...")
    import os
    import sys
    from pathlib import Path
    print("✓ Standard libraries imported successfully")
except Exception as e:
    print(f"✗ Error importing standard libraries: {e}")
    sys.exit(1)

try:
    print("Importing PyQt6...")
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    print("✓ PyQt6 imported successfully")
except Exception as e:
    print(f"✗ Error importing PyQt6: {e}")
    sys.exit(1)

try:
    print("Importing custom modules...")
    from script.settings import AppSettings
    print("✓ AppSettings imported successfully")
except Exception as e:
    print(f"✗ Error importing AppSettings: {e}")
    sys.exit(1)

try:
    print("Importing SimpleLanguageManager...")
    from script.simple_lang_manager import SimpleLanguageManager
    print("✓ SimpleLanguageManager imported successfully")
except Exception as e:
    print(f"✗ Error importing SimpleLanguageManager: {e}")
    sys.exit(1)

try:
    print("Importing MainWindow...")
    from script.main_window import MainWindow
    print("✓ MainWindow imported successfully")
except Exception as e:
    print(f"✗ Error importing MainWindow: {e}")
    sys.exit(1)

print("All imports successful!")
