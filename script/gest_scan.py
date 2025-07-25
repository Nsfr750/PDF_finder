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

from script.pdf_utils import (
    get_pdf_info, calculate_file_hash, extract_first_page_image,
    calculate_image_hash, find_duplicates
)
from script.language_manager import LanguageManager

logger = logging.getLogger('PDFDuplicateFinder')

def _tr(key, default_text):
    """Helper function to translate text using the language manager."""
    return LanguageManager().tr(key, default_text)

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
        self.language_manager = LanguageManager()
    
    def tr(self, key, default_text):
        """Translate text using the language manager."""
        return self.language_manager.tr(key, default_text)
    
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
                self.signals.error.emit(self.tr(
                    "scan.no_pdf_files_found", 
                    "No PDF files found in the selected directories."
                ))
                return
            
            total_files = len(pdf_files)
            logger.info(self.tr(
                "scan.found_pdf_files",
                "Found {count} PDF files to process"
            ).format(count=total_files))
            
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
                            logger.warning(self.tr(
                                "scan.skipping_nonexistent_file",
                                "Skipping non-existent file: {path}"
                            ).format(path=file_path))
                            continue
                            
                        # Get file info and hashes
                        file_info = get_pdf_info(file_path)
                        if not file_info:  # If get_pdf_info returns None (error case)
                            logger.warning(self.tr(
                                "scan.could_not_extract_info",
                                "Could not extract info from {path}"
                            ).format(path=file_path))
                            continue
                            
                        file_hash = calculate_file_hash(file_path)
                        
                        # Create a temporary directory for extracted images if it doesn't exist
                        if self.temp_dir is None or not os.path.isdir(self.temp_dir):
                            self.temp_dir = tempfile.mkdtemp(prefix='pdf_finder_')
                            logger.debug(self.tr(
                                "scan.created_temp_dir",
                                "Created temporary directory: {path}"
                            ).format(path=self.temp_dir))
                        
                        # Create a unique filename for the extracted image
                        base_name = os.path.basename(file_path)
                        image_path = os.path.join(self.temp_dir, f"{os.urandom(8).hex()}_{base_name}.png")
                        
                        # Extract first page image and calculate perceptual hash
                        if extract_first_page_image(file_path, image_path):
                            try:
                                image_hash = calculate_image_hash(image_path)
                                file_info['image_hash'] = image_hash
                            except Exception as e:
                                logger.warning(self.tr(
                                    "scan.could_not_calculate_hash",
                                    "Could not calculate image hash for {path}: {error}"
                                ).format(path=file_path, error=str(e)))
                            finally:
                                # Clean up the temporary image file
                                try:
                                    if os.path.exists(image_path):
                                        os.remove(image_path)
                                except Exception as e:
                                    logger.warning(self.tr(
                                        "scan.could_not_delete_temp_file",
                                        "Could not delete temporary file {path}: {error}"
                                    ).format(path=image_path, error=str(e)))
                        
                        processed_files.append(file_info)
                        file_hashes[file_path] = file_hash
                        
                    except Exception as e:
                        logger.error(self.tr(
                            "scan.error_processing_file",
                            "Error processing {path}: {error}"
                        ).format(path=file_path, error=str(e)), exc_info=True)
                        continue
                    
                    logger.debug(self.tr(
                        "scan.processed_file",
                        "Processed: {path}"
                    ).format(path=file_path))
                    
                except Exception as e:
                    logger.error(self.tr(
                        "scan.error_processing_file",
                        "Error processing {path}: {error}"
                    ).format(path=file_path, error=str(e)))
                    continue
            
            if self._is_cancelled:
                return
            
            # Step 3: Find duplicates
            logger.info(self.tr("scan.finding_duplicates", "Finding duplicate PDFs..."))
            duplicate_groups = find_duplicates(
                directory='',  # We're passing processed files directly, not scanning a directory
                recursive=False,
                threshold=self.min_similarity,
                processed_files=processed_files  # This parameter needs to be supported in find_duplicates
            )
            
            logger.info(self.tr(
                "scan.found_duplicate_groups",
                "Found {count} groups of duplicates"
            ).format(count=len(duplicate_groups)))
            
            self.signals.finished.emit(duplicate_groups)
            
        except Exception as e:
            logger.exception(self.tr("scan.error_in_scan_worker", "Error in scan worker:"))
            self.signals.error.emit(self.tr(
                "scan.scan_error_message",
                "An error occurred during scanning: {error}"
            ).format(error=str(e)))
        finally:
            # Clean up the temporary directory if it was created
            if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                    logger.debug(self.tr(
                        "scan.cleaned_up_temp_dir",
                        "Cleaned up temporary directory: {path}"
                    ).format(path=self.temp_dir))
                except Exception as e:
                    logger.warning(self.tr(
                        "scan.could_not_remove_temp_dir",
                        "Could not remove temporary directory {path}: {error}"
                    ).format(path=self.temp_dir, error=str(e)))
    
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
        self.language_manager = LanguageManager()
    
    def tr(self, key, default_text):
        """Translate text using the language manager."""
        return self.language_manager.tr(key, default_text)
    
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
            self.tr("scan.scanning_dialog_text", "Scanning for duplicate PDFs..."),
            self.tr("common.cancel", "Cancel"),
            0, 100,
            None
        )
        self.progress_dialog.setWindowTitle(self.tr("scan.scanning_title", "Scanning"))
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
                self.tr(
                    "scan.scanning_progress", 
                    "Scanning... ({current}/{total} files)"
                ).format(current=current, total=total)
            )
    
    def _on_file_processed(self, file_path: str):
        """Handle file processed signal."""
        logger.debug(self.tr(
            "scan.processed_file",
            "Processed: {path}"
        ).format(path=file_path))
        QApplication.processEvents()
    
    def _on_finished(self, duplicate_groups: list):
        """Handle scan completion."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        logger.info(self.tr(
            "scan.scan_completed",
            "Scan completed. Found {count} duplicate groups."
        ).format(count=len(duplicate_groups)))
        
        self.scan_completed.emit(duplicate_groups)
    
    def _on_error(self, error_msg: str):
        """Handle scan error."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        QMessageBox.critical(
            None,
            self.tr("scan.scan_error_title", "Scan Error"),
            error_msg,
            QMessageBox.StandardButton.Ok
        )
    
    # Signals
    scan_completed = Signal(list)  # Emitted with list of duplicate groups when scan is complete
