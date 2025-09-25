"""
PDF Scanner Module - Enhanced with Hash Caching

This module provides the PDFScanner class for scanning directories for duplicate PDF files.
It includes improved error handling, logging, and hash caching for performance optimization.
"""
import os
import logging
import traceback
from typing import Dict, Any, List, Optional, Callable
from PyQt6.QtCore import pyqtSignal, QObject

from .hash_cache import HashCache
from .text_processor import TextProcessor

# Set up logging
logger = logging.getLogger(__name__)

class PDFScanner(QObject):
    """
    A class to handle scanning of PDF files and finding duplicates.
    
    This class is designed to run in a separate thread to keep the UI responsive.
    Enhanced with hash caching for improved performance and memory optimization.
    """
    
    # Signals
    status_updated = pyqtSignal(str, int, int)  # message, current, total
    progress_updated = pyqtSignal(int, int, str)  # current, total, current_file
    duplicates_found = pyqtSignal(list)  # list of duplicate groups
    finished = pyqtSignal(list)  # list of duplicate groups (emitted when scan is complete)
    
    def __init__(self, threshold: float = 0.8, dpi: int = 150, 
                 enable_hash_cache: bool = True, cache_dir: Optional[str] = None,
                 language_manager=None):
        """Initialize the PDF scanner with the given settings.
        
        Args:
            threshold: Similarity threshold for considering PDFs as duplicates (0.0 to 1.0)
            dpi: DPI resolution for image-based comparison
            enable_hash_cache: Whether to enable hash caching for performance
            cache_dir: Directory to store cache files (defaults to ~/.pdf_finder_cache)
            language_manager: Language manager for translations
        """
        super().__init__()
        self.threshold = threshold
        self.dpi = dpi
        self.enable_hash_cache = enable_hash_cache
        self.scan_parameters: Dict[str, Any] = {}
        self._stop_requested = False
        
        # Initialize hash cache if enabled
        self.hash_cache = None
        if enable_hash_cache:
            try:
                logger.debug(f"PDFScanner: Initializing hash cache with cache_dir: {cache_dir}")
                self.hash_cache = HashCache(cache_dir=cache_dir)
                logger.info(f"PDFScanner: Hash cache initialized successfully, available: {self.hash_cache.is_available()}")
                if not self.hash_cache.is_available():
                    logger.warning("PDFScanner: Hash cache is not available after initialization")
            except Exception as e:
                logger.error(f"PDFScanner: Failed to initialize hash cache: {e}", exc_info=True)
                self.enable_hash_cache = False
        else:
            logger.info("PDFScanner: Hash cache is disabled")
        
        # Text processor for content comparison
        self.text_processor = TextProcessor()
        
        # Language manager for translations
        self.language_manager = language_manager
        
        logger.debug(f"PDFScanner initialized with threshold={threshold}, dpi={dpi}, "
                    f"hash_cache={'enabled' if enable_hash_cache else 'disabled'}")
    
    def tr(self, key: str, default: str = None) -> str:
        """Simple translation method for scanner messages.
        
        Args:
            key: Translation key
            default: Default text if key not found
            
        Returns:
            Translated text or default
        """
        if self.language_manager and hasattr(self.language_manager, 'tr'):
            return self.language_manager.tr(key, default or key)
        else:
            # Fallback to default or key if no language manager
            return default or key
    
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
            logger.debug("start_scan: Starting scan process...")
            
            # Get scan parameters with defaults
            logger.debug("start_scan: Retrieving scan parameters")
            scan_dir = self.scan_parameters.get('directory', '')
            recursive = self.scan_parameters.get('recursive', True)
            min_size = self.scan_parameters.get('min_file_size', 1024)  # 1KB
            max_size = self.scan_parameters.get('max_file_size', 1024 * 1024 * 1024)  # 1GB
            min_similarity = self.scan_parameters.get('min_similarity', 0.8)
            enable_text_compare = self.scan_parameters.get('enable_text_compare', True)
            
            logger.debug(f"start_scan: Parameters - Directory: {scan_dir}, Recursive: {recursive}, "
                        f"Min size: {min_size}, Max size: {max_size}, "
                        f"Min similarity: {min_similarity}, Text compare: {enable_text_compare}")
            
            # Validate scan directory
            logger.debug("start_scan: Validating scan directory")
            if not scan_dir or not os.path.isdir(scan_dir):
                error_msg = f"Invalid or non-existent scan directory: {scan_dir}"
                logger.error(f"start_scan: {error_msg}")
                self.status_updated.emit(
                    self.tr("scanner.error", f"Error: {error_msg}"), 
                    0, 0
                )
                self.finished.emit([])
                return
                
            if not os.access(scan_dir, os.R_OK):
                error_msg = f"No read permissions for directory: {scan_dir}"
                logger.error(f"start_scan: {error_msg}")
                self.status_updated.emit(
                    self.tr("scanner.error", f"Error: {error_msg}"), 
                    0, 0
                )
                self.finished.emit([])
                return
            
            logger.info(f"start_scan: Starting PDF scan in directory: {scan_dir}")
            self.status_updated.emit(
                self.tr("scanner.scan_started", "Starting scan..."),
                0, 0
            )
            
            # Reset state before starting new scan
            logger.debug("start_scan: Resetting scan state")
            self._reset_scan_state()
            
            # Start the scan with all parameters
            logger.debug("start_scan: Calling scan_directory")
            self.scan_directory(
                directory=scan_dir, 
                recursive=recursive,
                min_file_size=min_size,
                max_file_size=max_size,
                min_similarity=min_similarity,
                enable_text_compare=enable_text_compare
            )
            
            logger.info("start_scan: PDF scan completed successfully")
            
        except Exception as e:
            error_msg = f"Error during scan: {str(e)}"
            logger.error(f"start_scan: {error_msg}", exc_info=True)
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
        based on content similarity. Uses hash caching for improved performance.
        
        Args:
            directory: Path to the directory to scan
            recursive: Whether to scan subdirectories recursively
            min_file_size: Minimum file size in bytes to include in the scan
            max_file_size: Maximum file size in bytes to include in the scan
            min_similarity: Minimum similarity threshold (0.0 to 1.0) to consider files as duplicates
            enable_text_compare: Whether to enable text-based comparison
        """
        try:
            logger.info(f"scan_directory: Starting PDF scan in directory: {directory}")
            
            # Validate directory exists
            if not os.path.exists(directory):
                logger.error(f"scan_directory: Directory does not exist: {directory}")
                self.status_updated.emit(
                    self.tr("scanner.error", "Error: Directory does not exist: {dir}").format(dir=directory),
                    0, 0
                )
                self.finished.emit([])
                return
            
            if not os.path.isdir(directory):
                logger.error(f"scan_directory: Path is not a directory: {directory}")
                self.status_updated.emit(
                    self.tr("scanner.error", "Error: Path is not a directory: {dir}").format(dir=directory),
                    0, 0
                )
                self.finished.emit([])
                return
            
            # Find all PDF files
            logger.debug("scan_directory: Finding all PDF files")
            pdf_files = []
            try:
                if recursive:
                    logger.debug("scan_directory: Scanning recursively")
                    for root, _, files in os.walk(directory):
                        for file in files:
                            if file.lower().endswith('.pdf'):
                                file_path = os.path.join(root, file)
                                try:
                                    file_size = os.path.getsize(file_path)
                                    if min_file_size <= file_size <= max_file_size:
                                        pdf_files.append(file_path)
                                except (OSError, Exception) as e:
                                    logger.warning(f"scan_directory: Error accessing {file_path}: {e}")
                else:
                    logger.debug("scan_directory: Scanning non-recursively")
                    for file in os.listdir(directory):
                        if file.lower().endswith('.pdf'):
                            file_path = os.path.join(directory, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                if min_file_size <= file_size <= max_file_size:
                                    pdf_files.append(file_path)
                            except (OSError, Exception) as e:
                                logger.warning(f"scan_directory: Error accessing {file_path}: {e}")
            except Exception as e:
                logger.error(f"scan_directory: Error finding PDF files: {e}", exc_info=True)
                self.status_updated.emit(
                    self.tr("scanner.error", "Error finding PDF files: {error}").format(error=str(e)),
                    0, 0
                )
                self.finished.emit([])
                return
            
            total_files = len(pdf_files)
            logger.info(f"scan_directory: Found {total_files} PDF files to process")
            
            if total_files == 0:
                logger.info("scan_directory: No PDF files found in the specified directory")
                self.status_updated.emit(
                    self.tr("scanner.no_files", "No PDF files found in the specified directory"),
                    0, 0
                )
                self.finished.emit([])
                return
                
            logger.info(f"scan_directory: Found {total_files} PDF files to process")
            
            # Use hash cache if available for faster duplicate detection
            logger.debug("scan_directory: Checking hash cache availability")
            logger.debug(f"scan_directory: enable_hash_cache={self.enable_hash_cache}, hash_cache={self.hash_cache is not None}")
            if self.hash_cache:
                logger.debug(f"scan_directory: hash_cache.is_available()={self.hash_cache.is_available()}")
            
            try:
                if self.enable_hash_cache and self.hash_cache and self.hash_cache.is_available():
                    logger.info("scan_directory: Using hash cache for duplicate detection")
                    duplicates = self._find_duplicates_with_cache(pdf_files, min_similarity, enable_text_compare)
                else:
                    logger.info("scan_directory: Hash cache not available, using traditional scanning")
                    logger.debug(f"scan_directory: Cache status - enabled: {self.enable_hash_cache}, cache_exists: {self.hash_cache is not None}, available: {self.hash_cache.is_available() if self.hash_cache else False}")
                    duplicates = self._find_duplicates_traditional(pdf_files, min_similarity, enable_text_compare)
            except Exception as e:
                logger.error(f"scan_directory: Error during duplicate detection: {e}", exc_info=True)
                self.status_updated.emit(
                    self.tr("scanner.error", "Error during duplicate detection: {error}").format(error=str(e)),
                    0, 0
                )
                self.finished.emit([])
                return
            
            if not self._stop_requested:
                logger.info(f"scan_directory: Scan complete. Found {len(duplicates)} groups of duplicate files")
                self.status_updated.emit(
                    self.tr("scanner.complete", "Scan complete. Found {count} groups of duplicates").format(
                        count=len(duplicates)
                    ),
                    total_files, total_files
                )
                self.duplicates_found.emit(duplicates)
                self.finished.emit(duplicates)
            else:
                logger.info("scan_directory: Scan was stopped by user")
                self.finished.emit([])
                
        except Exception as e:
            error_msg = f"Error scanning directory: {str(e)}"
            logger.error(f"scan_directory: {error_msg}", exc_info=True)
            self.status_updated.emit(
                self.tr("scanner.error", "Error: {error}").format(error=error_msg), 
                0, 0
            )
            self.finished.emit([])
    
    def _find_duplicates_with_cache(self, pdf_files: List[str], min_similarity: float, 
                                   enable_text_compare: bool) -> List[List[str]]:
        """Find duplicates using hash cache for improved performance."""
        duplicates = []
        
        # Emit initial progress
        self.progress_updated.emit(0, len(pdf_files), "")
        self.status_updated.emit(
            self.tr("scanner.processing_cache", "Processing files with cache..."),
            0, len(pdf_files)
        )
        
        if enable_text_compare:
            # Use content-based duplicate detection with cache
            # Process files in smaller batches to provide progress updates
            batch_size = max(1, len(pdf_files) // 20)  # Update progress every ~5%
            for i in range(0, len(pdf_files), batch_size):
                if self._stop_requested:
                    break
                    
                batch_end = min(i + batch_size, len(pdf_files))
                batch_files = pdf_files[i:batch_end]
                
                # Update progress
                self.progress_updated.emit(batch_end, len(pdf_files), batch_files[-1] if batch_files else "")
                self.status_updated.emit(
                    self.tr("scanner.processing_cache", "Processing files with cache: {current} of {total}").format(
                        current=batch_end, total=len(pdf_files)
                    ),
                    batch_end, len(pdf_files)
                )
                
                # Process this batch
                content_groups = self.hash_cache.find_duplicates_by_content(batch_files, min_similarity)
                duplicates.extend(list(content_groups.values()))
                
                # Process events to keep UI responsive
                if hasattr(self, 'thread') and self.thread():
                    self.thread().msleep(1)  # Small delay to allow UI updates
        else:
            # Use hash-based duplicate detection
            hash_groups = self.hash_cache.find_duplicates_by_hash(pdf_files)
            duplicates = list(hash_groups.values())
            
            # Emit final progress for hash-based method
            self.progress_updated.emit(len(pdf_files), len(pdf_files), "")
            self.status_updated.emit(
                self.tr("scanner.complete_cache", "Cache processing complete"),
                len(pdf_files), len(pdf_files)
            )
        
        return duplicates
    
    def _find_duplicates_traditional(self, pdf_files: List[str], min_similarity: float, 
                                    enable_text_compare: bool) -> List[List[str]]:
        """Find duplicates using traditional method without cache."""
        logger.debug(f"_find_duplicates_traditional: Starting with {len(pdf_files)} files")
        duplicates = []
        
        try:
            for i, file_path in enumerate(pdf_files, 1):
                if self._stop_requested:
                    logger.info("_find_duplicates_traditional: Scan stopped by user")
                    self.status_updated.emit(
                        self.tr("scanner.stopped", "Scan stopped"), 
                        i, len(pdf_files)
                    )
                    break
                    
                # Update progress
                self.progress_updated.emit(i, len(pdf_files), file_path)
                self.status_updated.emit(
                    self.tr("scanner.processing", "Processing {current} of {total}: {file}").format(
                        current=i, total=len(pdf_files), file=os.path.basename(file_path)
                    ),
                    i, len(pdf_files)
                )
                
                try:
                    # Check if this file is a duplicate of any processed file
                    is_duplicate = False
                    for group in duplicates:
                        if enable_text_compare:
                            # Compare text content
                            try:
                                logger.debug(f"_find_duplicates_traditional: Comparing text content for {file_path}")
                                text1 = self.text_processor.extract_text(file_path)
                                text2 = self.text_processor.extract_text(group[0])
                                similarity = self.text_processor.compare_texts(text1, text2)
                                
                                if similarity >= min_similarity:
                                    logger.debug(f"_find_duplicates_traditional: Found duplicate with similarity {similarity}")
                                    group.append(file_path)
                                    is_duplicate = True
                                    break
                            except Exception as e:
                                logger.warning(f"_find_duplicates_traditional: Error comparing text content: {e}")
                                # Fall back to file size comparison
                                try:
                                    if os.path.getsize(file_path) == os.path.getsize(group[0]):
                                        group.append(file_path)
                                        is_duplicate = True
                                        break
                                except Exception as size_error:
                                    logger.warning(f"_find_duplicates_traditional: Error comparing file sizes: {size_error}")
                        else:
                            # Simple file size comparison
                            try:
                                if os.path.getsize(file_path) == os.path.getsize(group[0]):
                                    group.append(file_path)
                                    is_duplicate = True
                                    break
                            except Exception as size_error:
                                logger.warning(f"_find_duplicates_traditional: Error getting file size: {size_error}")
                    
                    if not is_duplicate:
                        # Start a new duplicate group
                        logger.debug(f"_find_duplicates_traditional: Starting new group for {file_path}")
                        duplicates.append([file_path])
                        
                except Exception as e:
                    logger.error(f"_find_duplicates_traditional: Error processing {file_path}: {e}", exc_info=True)
            
            # Filter out groups with only one file (no duplicates)
            duplicates = [group for group in duplicates if len(group) > 1]
            logger.debug(f"_find_duplicates_traditional: Found {len(duplicates)} duplicate groups")
            
        except Exception as e:
            logger.error(f"_find_duplicates_traditional: Unexpected error: {e}", exc_info=True)
            # Return empty list on error
            return []
        
        return duplicates
    
    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """Get cache statistics if hash cache is enabled."""
        if self.enable_hash_cache and self.hash_cache and self.hash_cache.is_available():
            try:
                return self.hash_cache.get_cache_stats()
            except Exception as e:
                logger.error(f"Error getting cache stats: {e}")
        return None
    
    def clear_cache(self) -> bool:
        """Clear the hash cache if enabled."""
        if self.enable_hash_cache and self.hash_cache and self.hash_cache.is_available():
            try:
                self.hash_cache.clear_cache()
                logger.info("Hash cache cleared successfully")
                return True
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
                return False
        return False
    
    def stop_scan(self) -> None:
        """Request the scan to stop at the next opportunity."""
        logger.info("Stop requested for current scan")
        self._stop_requested = True
        self.status_updated.emit(
            self.tr("scanner.stopping", "Stopping scan..."), 
            0, 0
        )
