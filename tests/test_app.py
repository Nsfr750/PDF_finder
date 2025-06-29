import os
import sys
import unittest
import tkinter as tk
import tkinterdnd2 as tkdnd
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import PDFDuplicateApp, t

class TestPDFDuplicateApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a root window for testing
        cls.root = tkdnd.Tk()
        # Don't show the window during tests
        cls.root.withdraw()
        
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Create a new app instance for each test
        self.app = PDFDuplicateApp(self.root)
        
    def tearDown(self):
        # Clean up after each test
        if hasattr(self, 'app') and hasattr(self.app, 'root'):
            self.app.root.destroy()
            del self.app

    def test_app_initialization(self):
        """Test that the application initializes correctly."""
        # Verify the app has been created
        self.assertIsNotNone(self.app)
        # Verify the window title is set
        self.assertEqual(self.app.root.title(), "PDF Duplicate Finder")
        # Verify the treeview exists
        self.assertTrue(hasattr(self.app, 'tree'))
        # Verify the menu bar exists
        self.assertTrue(hasattr(self.app, 'menu_manager'))

    @patch('tkinter.messagebox.showerror')
    def test_show_error_message(self, mock_showerror):
        """Test error message display."""
        error_message = "Test error message"
        self.app.show_status(error_message, "error")
        # Verify the error message was shown
        mock_showerror.assert_called_once()

def test_app():
    """Run the application for manual testing."""
    root = tkdnd.Tk()
    app = PDFDuplicateApp(root)
    print("Application started successfully!")
    root.mainloop()

if __name__ == "__main__":
    # Run the test suite
    unittest.main()
    # Uncomment the following line to run the app for manual testing
    # test_app()
