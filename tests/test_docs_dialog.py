import sys
import logging
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from script.docs import DocsDialog
from script.logger import setup_logger

def setup_test_logger():
    """Set up a dedicated logger for testing."""
    logger = logging.getLogger('PDFDuplicateFinderTest')
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Create file handler
    log_file = log_dir / 'test_docs_dialog.log'
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def test_documentation_dialog(language='en'):
    """Test the documentation dialog with the specified language."""
    logger = logging.getLogger('PDFDuplicateFinderTest')
    logger.info(f"Testing documentation dialog with language: {language}")
    
    try:
        dialog = DocsDialog(current_lang=language)
        dialog.setWindowTitle(f"Documentation Dialog Test - {language.upper()}")
        
        def on_language_changed(lang):
            logger.info(f"Language changed to: {lang}")
            
        dialog.language_changed.connect(on_language_changed)
        
        # Test document loading
        doc_text = dialog.text_browser.toPlainText()
        logger.info(f"Document loaded. Content length: {len(doc_text)} characters")
        
        return dialog
        
    except Exception as e:
        logger.error(f"Error in test_documentation_dialog: {e}\n{traceback.format_exc()}")
        raise

def main():
    # Set up test logger
    logger = setup_test_logger()
    logger.info("Starting documentation dialog tests")
    
    # Create application
    app = QApplication(sys.argv)
    
    try:
        # Test with English
        logger.info("\n=== Testing English Documentation ===")
        dialog_en = test_documentation_dialog('en')
        
        # Test with Italian
        logger.info("\n=== Testing Italian Documentation ===")
        dialog_it = test_documentation_dialog('it')
        
        # Show both dialogs
        dialog_en.show()
        dialog_it.show()
        
        logger.info("\nDocumentation dialogs opened successfully")
        logger.info("Please verify the following manually:")
        logger.info("1. Both dialogs are visible and responsive")
        logger.info("2. English and Italian content is displayed correctly")
        logger.info("3. Check the logs for any warnings or errors")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Critical error in main: {e}\n{traceback.format_exc()}")
        QMessageBox.critical(
            None,
            "Test Error",
            f"An error occurred during testing:\n{str(e)}\n\nCheck the log file for details."
        )
        return 1

if __name__ == "__main__":
    sys.exit(main())
