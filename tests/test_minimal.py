"""Minimal test script for PDFScanner functionality."""
import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from script.scanner import PDFScanner

# Configure basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_minimal')

def main():
    logger.info("Starting minimal test")
    
    # Create application instance
    app = QApplication(sys.argv)
    
    try:
        logger.info("Creating PDFScanner instance")
        scanner = PDFScanner()
        
        # Set up test directory (current directory)
        test_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Test directory: {test_dir}")
        
        # Set scan parameters
        scanner.scan_directory = test_dir
        scanner.recursive = False
        scanner.min_file_size = 0
        scanner.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Define signal handlers
        def on_progress(current, total, path):
            logger.info(f"Progress: {current}/{total} - {path}")
            
        def on_status(message, current, total):
            logger.info(f"Status: {message} ({current}/{total})")
            
        def on_finished(results):
            logger.info(f"Scan finished. Found {len(results)} duplicate groups")
            for i, group in enumerate(results, 1):
                logger.info(f"Group {i}:")
                for file_info in group:
                    logger.info(f"  - {file_info.get('path')}")
            QApplication.quit()
        
        # Connect signals
        scanner.progress_updated.connect(on_progress)
        scanner.status_updated.connect(on_status)
        scanner.finished.connect(on_finished)
        
        # Start the scan
        logger.info("Starting scan...")
        scanner.start_scan()
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
