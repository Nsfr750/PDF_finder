"""
Test script to diagnose application startup issues.
"""
import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_app.log')
    ]
)
logger = logging.getLogger('test_app')

def test_imports():
    """Test importing all required modules."""
    logger.info("Testing imports...")
    try:
        # Test PyQt6 imports
        from PyQt6 import QtWidgets, QtCore, QtGui
        logger.info("PyQt6 imports successful")
        
        # Test custom module imports
        from script.main_window import MainWindow
        from script.settings import AppSettings
        from lang.language_manager import LanguageManager
        from script.logger import get_logger
        logger.info("Custom module imports successful")
        
        # Test third-party imports
        from tqdm import tqdm
        import fitz  # PyMuPDF
        logger.info("Third-party imports successful")
        
        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during imports: {e}")
        return False

def test_app_init():
    """Test application initialization."""
    logger.info("Testing application initialization...")
    try:
        app = QApplication(sys.argv)
        logger.info("QApplication created successfully")
        
        # Import settings after QApplication is created
        from script.settings import AppSettings
        from lang.language_manager import LanguageManager
        from script.main_window import MainWindow
        
        settings = AppSettings()
        logger.info(f"Settings loaded. Current language: {settings.get_language()}")
        
        # Test language manager
        language_manager = LanguageManager(app, settings.get_language())
        logger.info("Language manager initialized")
        
        # Test main window
        window = MainWindow(language_manager=language_manager)
        logger.info("MainWindow created successfully")
        
        window.show()
        logger.info("Window shown")
        
        return app.exec()
    except Exception as e:
        logger.error(f"Error during app initialization: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    logger.info("Starting test application...")
    
    if not test_imports():
        logger.error("Import tests failed. Check the logs for details.")
        sys.exit(1)
    
    logger.info("All imports successful. Testing application initialization...")
    sys.exit(test_app_init())
