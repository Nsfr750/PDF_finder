"""Debug script to check imports and environment."""
import sys
import os
import logging

print("=== Python Environment ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print("\n=== System Path ===")
for i, path in enumerate(sys.path, 1):
    print(f"{i}. {path}")

print("\n=== Testing imports ===")
try:
    print("Importing PyQt6...")
    from PyQt6.QtWidgets import QApplication
    print("  - PyQt6.QtWidgets imported successfully")
    
    print("\nImporting PDFScanner...")
    from script.scanner import PDFScanner
    print("  - PDFScanner imported successfully")
    
    print("\nCreating PDFScanner instance...")
    scanner = PDFScanner()
    print("  - PDFScanner instance created successfully")
    
    # Test basic attributes
    print("\nTesting scanner attributes:")
    scanner.scan_directory = os.path.dirname(os.path.abspath(__file__))
    scanner.recursive = False
    print(f"  - scan_directory: {scanner.scan_directory}")
    print(f"  - recursive: {scanner.recursive}")
    
    # Test methods
    print("\nTesting scanner methods:")
    if hasattr(scanner, 'start_scan'):
        print("  - start_scan() method exists")
        print("  - Test completed successfully")
    else:
        print("  - ERROR: start_scan() method not found")
    
except ImportError as e:
    print(f"\nERROR: Failed to import: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
