import os
import sys
import datetime
import tkinter as tk
from tkinter import messagebox

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main application
from main import PDFDuplicateApp

def test_filters():
    """Test the filter functionality with sample data."""
    # Create a test app instance
    root = tk.Tk()
    root.withdraw()  # Hide the main window during tests
    
    try:
        app = PDFDuplicateApp(root)
        
        # Test data
        test_files = [
            {'path': 'test1.pdf', 'size': 1024, 'mtime': 1625000000, 'pages': 10},  # 1KB
            {'path': 'test2.pdf', 'size': 2048, 'mtime': 1625086400, 'pages': 5},   # 2KB
            {'path': 'test3.pdf', 'size': 5120, 'mtime': 1625172800, 'pages': 20}   # 5KB
        ]
        
        # Enable filters
        app.filters_active.set(True)
        
        # Test 1: Size filter
        print("\n=== Testing Size Filter ===")
        app.size_min_var.set('1.5')
        app.size_max_var.set('3')
        for file in test_files:
            result = app.apply_filters(file)
            print(f"File: {file['path']} - Size: {file['size']/1024:.1f}KB - Passes: {result}")
        
        # Test 2: Date filter
        print("\n=== Testing Date Filter ===")
        app.date_from_var.set('2021-06-29')
        app.date_to_var.set('2021-06-30')
        for file in test_files:
            result = app.apply_filters(file)
            mtime_str = datetime.datetime.fromtimestamp(file['mtime']).strftime('%Y-%m-%d')
            print(f"File: {file['path']} - Date: {mtime_str} - Passes: {result}")
        
        # Test 3: Page count filter
        print("\n=== Testing Page Count Filter ===")
        app.pages_min_var.set('5')
        app.pages_max_var.set('15')
        for file in test_files:
            result = app.apply_filters(file)
            print(f"File: {file['path']} - Pages: {file['pages']} - Passes: {result}")
    
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    test_filters()
    print("\nAll tests completed!")