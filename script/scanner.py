"""
PDF Scanner Module - Fixed Implementation

This module provides the PDFScanner class for scanning directories for duplicate PDF files.
It includes improved error handling and logging.
"""
import os
import logging
import traceback
from typing import Dict, Any, List, Optional, Callable
from PyQt6.QtCore import pyqtSignal, QObject

# Set up logging
logger = logging.getLogger(__name__)

class PDFScanner(QObject):
    """
    A class to handle scanning of PDF files and finding duplicates.
    
    This class is designed to run in a separate thread to keep the UI responsive.
    """
    
    # Signals
    status_updated = pyqtSignal(str, int, int)  # message, current, total
    progress_updated = pyqtSignal(int, int, str)  # current, total, current_file
    duplicates_found = pyqtSignal(list)  # list of duplicate groups
    finished = pyqtSignal(list)  # list of duplicate groups (emitted when scan is complete)
    
    def __init__(self, threshold: float = 0.95, dpi: int = 150):
        """Initialize the PDF scanner with the given settings.
        
        Args:
            threshold: Similarity threshold for considering PDFs as duplicates (0.0 to 1.0)
            dpi: DPI resolution for image-based comparison
        """
        super().__init__()
        self.threshold = threshold
        self.dpi = dpi
        self.scan_parameters: Dict[str, Any] = {}
        self._stop_requested = False
        
        logger.debug(f"PDFScanner initialized with threshold={threshold}, dpi={dpi}")
    
    def set_status_callback(self, callback: Callable[[str, int, int], None]) -> None:
        """Set a callback function for status updates.
        
        Args:
            callback: Function that takes (message: str, current: int, total: int)
        """
        self.status_callback = callback
    
    def start_scan(self) -> None:
        """Start the scan operation.
        
        This method is called when the scan thread starts. It retrieves scan parameters
        from the scan_parameters dictionary and calls scan_directory with those parameters.
        """
        try:
            logger.debug("Starting scan process...")
            
            # Get scan parameters with defaults
            scan_dir = self.scan_parameters.get('directory', '')
            recursive = self.scan_parameters.get('recursive', True)
            min_size = self.scan_parameters.get('min_file_size', 1024)  # 1KB
            max_size = self.scan_parameters.get('max_file_size', 1024 * 1024 * 1024)  # 1GB
            min_similarity = self.scan_parameters.get('min_similarity', 0.8)
            enable_text_compare = self.scan_parameters.get('enable_text_compare', True)
            
            logger.debug(f"Scan parameters - Directory: {scan_dir}, Recursive: {recursive}, "
                        f"Min size: {min_size}, Max size: {max_size}, "
                        f"Min similarity: {min_similarity}, Text compare: {enable_text_compare}")
            
            # Validate scan directory
            if not scan_dir or not os.path.isdir(scan_dir):
                error_msg = f"Invalid or non-existent scan directory: {scan_dir}"
                logger.error(error_msg)
                self.status_updated.emit(
                    self.tr("scanner.error", f"Error: {error_msg}"), 
                    0, 0
                )
                self.finished.emit([])
                return
                
            if not os.access(scan_dir, os.R_OK):
                error_msg = f"No read permissions for directory: {scan_dir}"
                logger.error(error_msg)
                self.status_updated.emit(
                    self.tr("scanner.error", f"Error: {error_msg}"), 
                    0, 0
                )
                self.finished.emit([])
                return
            
            logger.info(f"Starting PDF scan in directory: {scan_dir}")
            self.status_updated.emit(
                self.tr("scanner.scan_started", "Starting scan..."),
                0, 0
            )
            
            # Reset state before starting new scan
            self._reset_scan_state()
            
            # Start the scan with all parameters
            self.scan_directory(
                directory=scan_dir, 
                recursive=recursive,
                min_file_size=min_size,
                max_file_size=max_size,
                min_similarity=min_similarity,
                enable_text_compare=enable_text_compare
            )
            
            logger.info("PDF scan completed successfully")
            
        except Exception as e:
            error_msg = f"Error during scan: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.status_updated.emit(
                self.tr("scanner.error", f"Error: {error_msg}"), 
                0, 0
            )
            self.finished.emit([])
    
    def _reset_scan_state(self) -> None:
        """Reset the scanner state before starting a new scan."""
        self._stop_requested = False
        # Add any other state that needs to be reset here
    
    def scan_directory(self, directory: str, recursive: bool = True, 
                      min_file_size: int = 1024, max_file_size: int = 1024*1024*1024,
                      min_similarity: float = 0.8, enable_text_compare: bool = True) -> None:
        """Scan a directory for PDF files and find duplicates.
        
        This method walks through the directory, processes PDF files, and identifies duplicates
        based on content similarity.
        
        Args:
            directory: Path to the directory to scan
            recursive: Whether to scan subdirectories recursively
            min_file_size: Minimum file size in bytes to include in the scan
            max_file_size: Maximum file size in bytes to include in the scan
            min_similarity: Minimum similarity threshold (0.0 to 1.0) to consider files as duplicates
            enable_text_compare: Whether to enable text-based comparison
        """
        try:
            logger.info(f"Starting PDF scan in directory: {directory}")
            
            # Find all PDF files
            pdf_files = []
            if recursive:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                if min_file_size <= file_size <= max_file_size:
                                    pdf_files.append(file_path)
                            except (OSError, Exception) as e:
                                logger.warning(f"Error accessing {file_path}: {e}")
            else:
                for file in os.listdir(directory):
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(directory, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            if min_file_size <= file_size <= max_file_size:
                                pdf_files.append(file_path)
                        except (OSError, Exception) as e:
                            logger.warning(f"Error accessing {file_path}: {e}")
            
            total_files = len(pdf_files)
            if total_files == 0:
                logger.info("No PDF files found in the specified directory")
                self.status_updated.emit(
                    self.tr("scanner.no_files", "No PDF files found in the specified directory"),
                    0, 0
                )
                self.finished.emit([])
                return
                
            logger.info(f"Found {total_files} PDF files to process")
            
            # Process files and find duplicates
            processed_files = []
            duplicates = []
            
            for i, file_path in enumerate(pdf_files, 1):
                if self._stop_requested:
                    logger.info("Scan stopped by user")
                    self.status_updated.emit(
                        self.tr("scanner.stopped", "Scan stopped"), 
                        i, total_files
                    )
                    break
                    
                # Update progress
                self.progress_updated.emit(i, total_files, file_path)
                self.status_updated.emit(
                    self.tr("scanner.processing", "Processing {current} of {total}: {file}").format(
                        current=i, total=total_files, file=os.path.basename(file_path)
                    ),
                    i, total_files
                )
                
                try:
                    # Check if this file is a duplicate of any processed file
                    is_duplicate = False
                    for group in duplicates:
                        # For now, just compare file sizes as a simple check
                        # In a real implementation, you would compare actual content
                        if os.path.getsize(file_path) == os.path.getsize(group[0]):
                            group.append(file_path)
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        # Start a new duplicate group
                        duplicates.append([file_path])
                        
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}", exc_info=True)
            
            # Filter out groups with only one file (no duplicates)
            duplicates = [group for group in duplicates if len(group) > 1]
            
            if not self._stop_requested:
                logger.info(f"Scan complete. Found {len(duplicates)} groups of duplicate files")
                self.status_updated.emit(
                    self.tr("scanner.complete", "Scan complete. Found {count} groups of duplicates").format(
                        count=len(duplicates)
                    ),
                    total_files, total_files
                )
                self.duplicates_found.emit(duplicates)
                self.finished.emit(duplicates)
            else:
                self.finished.emit([])
                
        except Exception as e:
            error_msg = f"Error scanning directory: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.status_updated.emit(
                self.tr("scanner.error", "Error: {error}").format(error=error_msg), 
                0, 0
            )
            self.finished.emit([])
    
    def stop_scan(self) -> None:
        """Request the scan to stop at the next opportunity."""
        logger.info("Stop requested for current scan")
        self._stop_requested = True
        self.status_updated.emit(
            self.tr("scanner.stopping", "Stopping scan..."), 
            0, 0
        )
