import os
import logging
import time
import tempfile
import shutil
import hashlib
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set, Callable
import concurrent.futures
from PyQt6.QtCore import QObject, pyqtSignal as Signal, QThreadPool, QRunnable, pyqtSlot as Slot, Qt
from PyQt6.QtWidgets import QProgressDialog, QMessageBox, QApplication

from app_qt.pdf_utils import (
    get_pdf_info, calculate_file_hash, extract_first_page_image,
    calculate_image_hash, find_duplicates
)

logger = logging.getLogger('PDFDuplicateFinder')

class ScanWorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    progress = Signal(int, int)  # current, total
    file_processed = Signal(str)  # path of processed file
    finished = Signal(list)  # list of duplicate groups
    error = Signal(str)  # error message

class ScanWorker(QRunnable):
    """
    Worker thread for scanning directories for duplicate PDFs.
    """
    def __init__(self, directories: List[str], min_similarity: float = 0.9):
        super().__init__()
        self.directories = directories
        self.min_similarity = min_similarity
        self._is_cancelled = False
        self.signals = ScanWorkerSignals()
        self.temp_dir = None
    
    @Slot()
    def run(self):
        """
        Run the scanning process.
        """
        try:
            # Step 1: Find all PDF files
            pdf_files = []
            for directory in self.directories:
                if self._is_cancelled:
                    return
                    
                for root, _, files in os.walk(directory):
                    if self._is_cancelled:
                        return
                        
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            pdf_files.append(os.path.join(root, file))
            
            if not pdf_files:
                self.signals.error.emit("No PDF files found in the selected directories.")
                return
            
            total_files = len(pdf_files)
            logger.info(f"Found {total_files} PDF files to process")
            
            # Step 2: Process files and find duplicates
            processed_files = []
            file_hashes = {}
            
            for i, file_path in enumerate(pdf_files, 1):
                if self._is_cancelled:
                    return
                
                try:
                    self.signals.progress.emit(i, total_files)
                    self.signals.file_processed.emit(file_path)
                    
                    try:
                        # Skip if file doesn't exist or is not a file
                        if not os.path.isfile(file_path):
                            logger.warning(f"Skipping non-existent file: {file_path}")
                            continue
                            
                        # Get file info and hashes
                        file_info = get_pdf_info(file_path)
                        if not file_info:  # If get_pdf_info returns None (error case)
                            logger.warning(f"Could not extract info from {file_path}")
                            continue
                            
                        file_hash = calculate_file_hash(file_path)
                        
                        # Create a temporary directory for extracted images if it doesn't exist
                        if self.temp_dir is None or not os.path.isdir(self.temp_dir):
                            self.temp_dir = tempfile.mkdtemp(prefix='pdf_finder_')
                            logger.debug(f"Created temporary directory: {self.temp_dir}")
                        
                        # Create a unique filename for the extracted image
                        base_name = os.path.basename(file_path)
                        image_path = os.path.join(self.temp_dir, f"{os.urandom(8).hex()}_{base_name}.png")
                        
                        # Extract first page image and calculate perceptual hash
                        if extract_first_page_image(file_path, image_path):
                            try:
                                image_hash = calculate_image_hash(image_path)
                                file_info['image_hash'] = image_hash
                            except Exception as e:
                                logger.warning(f"Could not calculate image hash for {file_path}: {e}")
                            finally:
                                # Clean up the temporary image file
                                try:
                                    if os.path.exists(image_path):
                                        os.remove(image_path)
                                except Exception as e:
                                    logger.warning(f"Could not delete temporary file {image_path}: {e}")
                        
                        processed_files.append(file_info)
                        file_hashes[file_path] = file_hash
                        
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}", exc_info=True)
                        continue
                    
                    logger.debug(f"Processed: {file_path}")
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    continue
            
            if self._is_cancelled:
                return
            
            # Step 3: Find duplicates
            logger.info("Finding duplicate PDFs...")
            duplicate_groups = find_duplicates(
                directory='',  # We're passing processed files directly, not scanning a directory
                recursive=False,
                threshold=self.min_similarity,
                processed_files=processed_files  # This parameter needs to be supported in find_duplicates
            )
            
            logger.info(f"Found {len(duplicate_groups)} groups of duplicates")
            self.signals.finished.emit(duplicate_groups)
            
        except Exception as e:
            logger.exception("Error in scan worker:")
            self.signals.error.emit(f"An error occurred during scanning: {str(e)}")
        finally:
            # Clean up the temporary directory if it was created
            if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
                except Exception as e:
                    logger.warning(f"Could not remove temporary directory {self.temp_dir}: {e}")
    
    def cancel(self):
        """Request cancellation of the scan."""
        self._is_cancelled = True

class ScanManager(QObject):
    """Manages PDF scanning operations with progress feedback."""
    
    # Signals
    progress = Signal(int, int)  # current, total
    file_processed = Signal(str)  # path of processed file
    scan_completed = Signal(list)  # list of duplicate groups
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool.globalInstance()
        self.current_worker = None
        self.progress_dialog = None
    
    def start_scan(self, directories: List[str], min_similarity: float = 0.9):
        """Start a new scan operation.
        
        Args:
            directories: List of directories to scan
            min_similarity: Minimum similarity score (0.0-1.0) to consider files as duplicates
            
        Returns:
            bool: True if scan started successfully
        """
        if not directories:
            return False
        
        # Cancel any existing scan
        self.cancel_scan()
        
        # Create and configure worker
        self.current_worker = ScanWorker(directories, min_similarity)
        self.current_worker.signals.progress.connect(self._on_progress)
        self.current_worker.signals.file_processed.connect(self._on_file_processed)
        self.current_worker.signals.finished.connect(self._on_finished)
        self.current_worker.signals.error.connect(self._on_error)
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            "Scanning for duplicate PDFs...",
            "Cancel",
            0, 100,
            None
        )
        self.progress_dialog.setWindowTitle("Scanning")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.canceled.connect(self.cancel_scan)
        self.progress_dialog.show()
        
        # Start the worker
        self.thread_pool.start(self.current_worker)
        return True
    
    def cancel_scan(self):
        """Cancel the current scan operation."""
        if self.current_worker:
            self.current_worker.cancel()
            self.current_worker = None
        
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
    
    def _on_progress(self, current: int, total: int):
        """Update progress dialog."""
        if self.progress_dialog:
            self.progress_dialog.setMaximum(total)
            self.progress_dialog.setValue(current)
            
            # Update label with current file being processed
            self.progress_dialog.setLabelText(
                f"Scanning... ({current}/{total} files)"
            )
    
    def _on_file_processed(self, file_path: str):
        """Handle file processed signal."""
        logger.debug(f"Processed: {file_path}")
        QApplication.processEvents()
    
    def _on_finished(self, duplicate_groups: list):
        """Handle scan completion."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        logger.info(f"Scan completed. Found {len(duplicate_groups)} duplicate groups.")
        self.scan_completed.emit(duplicate_groups)
    
    def _on_error(self, error_msg: str):
        """Handle scan error."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        QMessageBox.critical(
            None,
            "Scan Error",
            error_msg,
            QMessageBox.StandardButton.Ok
        )
    
    # Signals
    scan_completed = Signal(list)  # Emitted with list of duplicate groups when scan is complete
