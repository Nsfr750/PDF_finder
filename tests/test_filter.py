import os
import sys
import datetime
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import tkinter as tk
import tkinterdnd2 as tkdnd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main application
from main import PDFDuplicateApp

class MockPDFDuplicateApp:
    """Mock PDFDuplicateApp for testing filters without GUI."""
    def __init__(self, root):
        self.root = root
        # Initialize variables with default values
        self._filters_active = True
        self._size_min = ''
        self._size_max = ''
        self._date_from = ''
        self._date_to = ''
        self._pages_min = ''
        self._pages_max = ''
        
        # Create Tkinter variables if root is available
        if root is not None:
            self._init_tk_vars()
    
    def _init_tk_vars(self):
        """Initialize Tkinter variables."""
        self.filters_active = tk.BooleanVar(self.root, value=self._filters_active)
        self.size_min_var = tk.StringVar(self.root, value=self._size_min)
        self.size_max_var = tk.StringVar(self.root, value=self._size_max)
        self.date_from_var = tk.StringVar(self.root, value=self._date_from)
        self.date_to_var = tk.StringVar(self.root, value=self._date_to)
        self.pages_min_var = tk.StringVar(self.root, value=self._pages_min)
        self.pages_max_var = tk.StringVar(self.root, value=self._pages_max)
    
    def set_filters_active(self, value):
        """Set filters_active value."""
        self._filters_active = value
        if hasattr(self, 'filters_active'):
            self.filters_active.set(value)
    
    def get_filters_active(self):
        """Get filters_active value."""
        if hasattr(self, 'filters_active'):
            return self.filters_active.get()
        return self._filters_active
    
    def apply_filters(self, file_info):
        """Mock apply_filters method for testing."""
        if not self.get_filters_active():
            return True
            
        # Size filter
        if self.size_min_var.get() or self.size_max_var.get():
            try:
                size_kb = file_info['size'] / 1024
                min_size = float(self.size_min_var.get()) if self.size_min_var.get() else 0
                max_size = float(self.size_max_var.get()) if self.size_max_var.get() else float('inf')
                if not (min_size <= size_kb <= max_size):
                    return False
            except (ValueError, TypeError):
                pass
        
        # Date filter
        if self.date_from_var.get() or self.date_to_var.get():
            try:
                file_date = datetime.datetime.fromtimestamp(file_info['mtime']).date()
                
                if self.date_from_var.get():
                    from_date = datetime.datetime.strptime(self.date_from_var.get(), '%Y-%m-%d').date()
                    if file_date < from_date:
                        return False
                        
                if self.date_to_var.get():
                    to_date = datetime.datetime.strptime(self.date_to_var.get(), '%Y-%m-%d').date()
                    if file_date > to_date:
                        return False
            except (ValueError, TypeError, KeyError):
                pass
        
        # Page count filter
        if self.pages_min_var.get() or self.pages_max_var.get():
            try:
                pages = int(file_info['pages'])
                min_pages = int(self.pages_min_var.get()) if self.pages_min_var.get() else 0
                max_pages = int(self.pages_max_var.get()) if self.pages_max_var.get() else float('inf')
                if not (min_pages <= pages <= max_pages):
                    return False
            except (ValueError, TypeError, KeyError):
                pass
                
        return True


class TestPDFFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a root window for testing
        cls.root = tkdnd.Tk()
        # Don't show the window during tests
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except:
            pass
            
    def _create_mock_app(self):
        """Helper to create a mock app with proper Tkinter variable initialization."""
        app = MockPDFDuplicateApp(self.root)
        # Initialize Tkinter variables if not already done
        if not hasattr(app, 'filters_active'):
            app._init_tk_vars()
        return app

    def setUp(self):
        # Create a new mock app instance for each test
        self.app = self._create_mock_app()
        
        # Test data
        self.test_files = [
            {'path': 'test1.pdf', 'size': 1024, 'mtime': 1625000000, 'pages': 10},  # 1KB
            {'path': 'test2.pdf', 'size': 2048, 'mtime': 1625086400, 'pages': 5},   # 2KB
            {'path': 'test3.pdf', 'size': 5120, 'mtime': 1625172800, 'pages': 20}   # 5KB
        ]
    
    def tearDown(self):
        # Clean up after each test
        if hasattr(self, 'app') and hasattr(self.app, 'root'):
            try:
                self.app.root.destroy()
            except:
                pass

    def test_size_filter(self):
        """Test filtering by file size."""
        print("\n=== Testing Size Filter ===")
        self.app.size_min_var.set('1.5')
        self.app.size_max_var.set('3')
        
        for file in self.test_files:
            result = self.app.apply_filters(file)
            size_kb = file['size'] / 1024
            print(f"File: {file['path']} - Size: {size_kb:.1f}KB - Passes: {result}")
            
            # Verify the filter works as expected
            expected = 1.5 <= size_kb <= 3.0
            self.assertEqual(result, expected, f"Size filter failed for {file['path']}")

    def test_date_filter(self):
        """Test filtering by modification date."""
        print("\n=== Testing Date Filter ===")
        self.app.date_from_var.set('2021-06-29')
        self.app.date_to_var.set('2021-06-30')
        
        for file in self.test_files:
            result = self.app.apply_filters(file)
            mtime_str = datetime.datetime.fromtimestamp(file['mtime']).strftime('%Y-%m-%d')
            print(f"File: {file['path']} - Date: {mtime_str} - Passes: {result}")
            
            # Verify the filter works as expected
            file_date = datetime.datetime.fromtimestamp(file['mtime']).date()
            start_date = datetime.date(2021, 6, 29)
            end_date = datetime.date(2021, 6, 30)
            expected = start_date <= file_date <= end_date
            self.assertEqual(result, expected, f"Date filter failed for {file['path']}")

    def test_page_count_filter(self):
        """Test filtering by page count."""
        print("\n=== Testing Page Count Filter ===")
        self.app.pages_min_var.set('5')
        self.app.pages_max_var.set('15')
        
        for file in self.test_files:
            result = self.app.apply_filters(file)
            print(f"File: {file['path']} - Pages: {file['pages']} - Passes: {result}")
            
            # Verify the filter works as expected
            expected = 5 <= file['pages'] <= 15
            self.assertEqual(result, expected, f"Page count filter failed for {file['path']}")
            
    def test_filters_inactive(self):
        """Test that all files pass when filters are inactive."""
        self.app.set_filters_active(False)
        for file in self.test_files:
            self.assertTrue(self.app.apply_filters(file), 
                          f"Filter should pass when inactive for {file['path']}")
        
        # Also test with filters_active as a property
        if hasattr(self.app, 'filters_active'):
            self.app.filters_active.set(False)
            for file in self.test_files:
                self.assertTrue(self.app.apply_filters(file), 
                              f"Filter should pass when inactive (tkvar) for {file['path']}")

def test_filters():
    """Run the filter tests with console output."""
    # Create a root window for manual testing
    root = tkdnd.Tk()
    
    try:
        # Create a mock app instance
        app = MockPDFDuplicateApp(root)
        
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
    # Run the test suite
    unittest.main(verbosity=2)
    # Uncomment the following line to run the manual test function
    # test_filters()