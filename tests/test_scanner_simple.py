"""Simple test for PDFScanner initialization and basic functionality."""
import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_scanner')

def test_scanner():
    try:
        logger.info("Testing PDFScanner initialization...")
        
        # Import PDFScanner
        from script.scanner import PDFScanner
        logger.info("Successfully imported PDFScanner")
        
        # Create QApplication instance
        app = QApplication(sys.argv)
        
        # Create scanner instance
        scanner = PDFScanner()
        logger.info("Successfully created PDFScanner instance")
        
        # Test setting attributes
        test_dir = os.path.dirname(os.path.abspath(__file__))
        scanner.scan_directory = test_dir
        scanner.recursive = True
        scanner.min_file_size = 0
        scanner.max_file_size = 10 * 1024 * 1024  # 10MB
        
        logger.info("PDFScanner attributes set successfully")
        logger.info(f"scan_directory: {scanner.scan_directory}")
        logger.info(f"recursive: {scanner.recursive}")
        logger.info(f"min_file_size: {scanner.min_file_size}")
        logger.info(f"max_file_size: {scanner.max_file_size}")
        
        # Test method existence
        if hasattr(scanner, 'start_scan'):
            logger.info("start_scan() method exists")
        else:
            logger.error("start_scan() method not found")
            
        # Test signal connections
        def on_progress(current, total, path):
            logger.debug(f"Progress: {current}/{total} - {path}")
            
        def on_status(message, current, total):
            logger.info(f"Status: {message} ({current}/{total})")
            
        def on_finished(results):
            logger.info(f"Scan finished with {len(results)} duplicate groups")
            QApplication.quit()
            
        # Connect signals
        scanner.progress_updated.connect(on_progress)
        scanner.status_updated.connect(on_status)
        scanner.finished.connect(on_finished)
        
        logger.info("All signals connected successfully")
        
        # Start the scan
        logger.info("Starting scan...")
        scanner.start_scan()
        
        # Start the event loop
        logger.info("Starting application event loop")
        return app.exec()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(test_scanner())
