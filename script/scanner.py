"""PDF scanning and comparison functionality."""
import os
import time
import logging
from typing import List, Dict, Set, Tuple, Optional, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue

from .pdf_utils import PDFDocument, PDFUtils

logger = logging.getLogger('PDFDuplicateFinder')

# Import language manager
from lang.language_manager import LanguageManager

class PDFScanner:
    """Handles scanning for duplicate PDFs in directories."""
    
    def __init__(self):
        self.stop_event = threading.Event()
        self.progress_callback = None
        self.status_callback = None
        self.found_callback = None
        self.scan_complete = False
        self.scan_results = {}
        self.duplicate_groups = []
        self.scanned_files = 0
        self.total_files = 0
        self.start_time = 0
        self.lock = threading.Lock()
        self.language_manager = LanguageManager()
        self.tr = self.language_manager.tr
    
    def scan_directory(self, directory: str, recursive: bool = True, 
                      min_file_size: int = 1024, max_file_size: int = 1024*1024*1024) -> None:
        """
        Scan a directory for PDF files and find duplicates.
        
        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories
            min_file_size: Minimum file size in bytes
            max_file_size: Maximum file size in bytes
        """
        self.stop_event.clear()
        self.scan_results = {}
        self.duplicate_groups = []
        self.scanned_files = 0
        self.total_files = 0
        self.start_time = time.time()
        self.scan_complete = False
        
        try:
            # First, collect all PDF files
            pdf_files = self._collect_pdf_files(directory, recursive, min_file_size, max_file_size)
            self.total_files = len(pdf_files)
            
            if self.status_callback:
                self.status_callback(self.tr("scanner.scanning_pdfs", "Scanning PDF files..."), 0, self.total_files)
            
            # Process files in parallel
            self._process_files(pdf_files)
            
            # Group similar PDFs
            if not self.stop_event.is_set():
                if self.status_callback:
                    self.status_callback(self.tr("scanner.finding_duplicates", "Finding duplicates..."), 0, 0)
                self._find_duplicates()
            
            self.scan_complete = True
            if self.status_callback:
                self.status_callback(self.tr("scanner.scan_complete", "Scan complete!"), 
                                  self.scanned_files, self.total_files)
                
        except Exception as e:
            error_msg = self.tr("scanner.scan_error", "Error during scanning: {error}").format(error=str(e))
            logger.error(error_msg)
            if self.status_callback:
                self.status_callback(self.tr("scanner.error_prefix", "Error: {error}").format(error=str(e)), 0, 0)
        finally:
            self.stop_event.set()
    
    def stop_scan(self):
        """Stop the current scan operation."""
        self.stop_event.set()
    
    def _collect_pdf_files(self, directory: str, recursive: bool, 
                          min_size: int, max_size: int) -> List[str]:
        """Collect all PDF files in the specified directory."""
        pdf_files = []
        
        def scan_dir(path):
            if self.stop_event.is_set():
                return
                
            try:
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_file() and entry.name.lower().endswith('.pdf'):
                            try:
                                file_size = entry.stat().st_size
                                if min_size <= file_size <= max_size:
                                    pdf_files.append(entry.path)
                            except (OSError, AttributeError):
                                continue
                        elif entry.is_dir() and recursive:
                            scan_dir(entry.path)
            except (PermissionError, OSError) as e:
                warning_msg = self.tr("scanner.access_error", "Cannot access {path}: {error}").format(
                    path=path, error=str(e))
                logger.warning(warning_msg)
        
        scan_dir(directory)
        return pdf_files
    
    def _process_files(self, file_paths: List[str], max_workers: int = 4):
        """Process PDF files in parallel."""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self._process_single_file, path): path 
                for path in file_paths
            }
            
            for future in as_completed(future_to_path):
                if self.stop_event.is_set():
                    executor.shutdown(wait=False)
                    break
                    
                path = future_to_path[future]
                try:
                    doc = future.result()
                    if doc:
                        with self.lock:
                            self.scanned_files += 1
                            if self.progress_callback:
                                self.progress_callback(self.scanned_files, self.total_files, path)
                            
                            # Group by content hash
                            if doc.content_hash not in self.scan_results:
                                self.scan_results[doc.content_hash] = []
                            self.scan_results[doc.content_hash].append(doc)
                except Exception as e:
                    error_msg = self.tr("scanner.processing_error", "Error processing {path}: {error}").format(
                        path=path, error=str(e))
                    logger.error(error_msg)
    
    def _process_single_file(self, file_path: str) -> Optional[PDFDocument]:
        """Process a single PDF file."""
        if self.stop_event.is_set() or not PDFUtils.is_pdf(file_path):
            return None
            
        try:
            return PDFDocument(file_path)
        except Exception as e:
            error_msg = self.tr("scanner.load_error", "Error loading PDF {file}: {error}").format(
                file=file_path, error=str(e))
            logger.warning(error_msg)
            return None
    
    def _find_duplicates(self):
        """Find duplicate PDFs based on content hashes."""
        self.duplicate_groups = []
        
        for content_hash, docs in self.scan_results.items():
            if len(docs) > 1:  # We have potential duplicates
                # Group by image hash for more precise matching
                image_hash_groups = {}
                
                for doc in docs:
                    if doc.image_hash not in image_hash_groups:
                        image_hash_groups[doc.image_hash] = []
                    image_hash_groups[doc.image_hash].append(doc)
                
                # Add groups with more than one document
                for group in image_hash_groups.values():
                    if len(group) > 1:
                        # Sort by file size (smallest first)
                        group.sort(key=lambda x: x.file_size)
                        self.duplicate_groups.append(group)
                        
                        if self.found_callback:
                            self.found_callback(group)
    
    def get_duplicate_groups(self) -> List[List[PDFDocument]]:
        """Get the list of duplicate groups found."""
        return self.duplicate_groups
    
    def get_scan_summary(self) -> dict:
        """Get a summary of the scan results."""
        total_duplicates = sum(len(group) for group in self.duplicate_groups)
        space_savings = sum(group[0].file_size * (len(group) - 1) for group in self.duplicate_groups)
        
        return {
            'total_files': self.total_files,
            'scanned_files': self.scanned_files,
            'duplicate_groups': len(self.duplicate_groups),
            'total_duplicates': total_duplicates,
            'space_savings': space_savings,
            'scan_time': time.time() - self.start_time if self.start_time else 0
        }
