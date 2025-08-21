"""Test script for PDFScanner functionality."""
import sys
import os
import logging
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QCoreApplication
from script.scanner import PDFScanner
from script.logger import setup_logger

# Ensure logs directory exists
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# Set up file handler for test logs
file_handler = logging.FileHandler(log_dir / 'test_scanner.log', mode='w')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

logger = logging.getLogger('test_scanner')
logger.info("Starting PDFScanner test")

class TestApp:
    def __init__(self):
        # Initialize QApplication first
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.scanner = None
        
    def run_test(self):
        try:
            logger.info("Creating PDFScanner instance...")
            self.scanner = PDFScanner()
            logger.info("PDFScanner instance created successfully")
            
            # Set up test directory (use the project directory for testing)
            test_dir = os.path.dirname(os.path.abspath(__file__))
            logger.info(f"Test directory: {test_dir}")
            
            if not os.path.isdir(test_dir):
                raise ValueError(f"Test directory does not exist: {test_dir}")
            
            # Set scan parameters as instance variables
            logger.info("Setting scan parameters...")
            self.scanner.scan_directory = test_dir  # This should be a directory path
            self.scanner.recursive = True
            self.scanner.min_file_size = 0
            self.scanner.max_file_size = 10 * 1024 * 1024  # 10MB
            
            # Log scanner attributes
            logger.info("Scanner attributes:")
            for attr in ['scan_directory', 'recursive', 'min_file_size', 'max_file_size']:
                logger.info(f"  {attr}: {getattr(self.scanner, attr, 'Not set')}")
            
            # Connect signals
            logger.info("Connecting signals...")
            self.scanner.progress_updated.connect(self.on_progress)
            self.scanner.status_updated.connect(self.on_status)
            self.scanner.finished.connect(self.on_finished)
            
            logger.info("Starting scan...")
            self.scanner.start_scan()
            
            logger.info("Entering application event loop")
            return self.app.exec()
            
        except Exception as e:
            error_msg = f"Test failed: {str(e)}\n\n{traceback.format_exc()}"
            logger.error(error_msg)
            QMessageBox.critical(
                None,
                "Test Failed",
                f"The test encountered an error:\n\n{error_msg}"
            )
            return 1
    
    def on_progress(self, current, total, path):
        logger.debug(f"Progress: {current}/{total} - {path}")
        
    def on_status(self, message, current, total):
        logger.info(f"Status: {message} ({current}/{total})")
        
    def on_finished(self, results):
        logger.info(f"Scan finished. Found {len(results)} duplicate groups")
        for i, group in enumerate(results, 1):
            logger.info(f"Group {i}:")
            for file_info in group:
                logger.info(f"  - {file_info.get('path')}")
        self.app.quit()

if __name__ == "__main__":
    test_app = TestApp()
    sys.exit(test_app.run_test())
