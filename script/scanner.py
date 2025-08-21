"""PDF scanning and comparison functionality."""
import os
import time
import logging
from typing import List, Dict, Set, Tuple, Optional, Any, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
from PyQt6.QtCore import QObject, pyqtSignal

from .pdf_utils import PDFDocument, PDFUtils
from .pdf_comparison import PDFComparator, PDFType

logger = logging.getLogger('PDFDuplicateFinder')

# Import language manager
from script.lang_mgr import LanguageManager

class PDFScanner(QObject):
    """Handles scanning for duplicate PDFs in directories."""
    
    # Define signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, path
    status_updated = pyqtSignal(str, int, int)    # message, current, total
    finished = pyqtSignal(list)  # Emit list of duplicate groups
    
    def __init__(self, comparison_threshold: float = 0.95, dpi: int = 200):
        """Initialize the PDF scanner.
        
        Args:
            comparison_threshold: Similarity threshold (0-1) for considering PDFs as duplicates
            dpi: DPI to use for image-based comparison
        """
        super().__init__()
        self.stop_event = threading.Event()
        self.scan_complete = False
        self.scan_results = {}
        self.duplicate_groups = []
        self.scanned_files = 0
        self.total_files = 0
        self.start_time = 0
        self.lock = threading.Lock()
        self.language_manager = LanguageManager()
        self.tr = self.language_manager.tr
        self.comparator = PDFComparator(threshold=comparison_threshold, dpi=dpi)
        self.status_callback = None
        
    def set_status_callback(self, callback):
        """Set the status callback function.
        
        Args:
            callback: Function to call with status updates (message, current, total)
        """
        self.status_callback = callback
    
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
            self.status_updated.emit(
                self.tr("scanner.scanning_pdfs", "Scanning for PDF files..."), 
                0, 0
            )
            
            pdf_files = self._collect_pdf_files(directory, recursive, min_file_size, max_file_size)
            self.total_files = len(pdf_files)
            
            if self.total_files == 0:
                self.status_updated.emit(
                    self.tr("scanner.no_pdfs_found", "No PDF files found in the selected directory."),
                    0, 0
                )
                self.finished.emit()
                return
                
            self.status_updated.emit(
                self.tr("scanner.processing_pdfs", "Processing {count} PDF files...").format(count=self.total_files),
                0, self.total_files
            )
            
            # Process files in parallel
            self._process_files(pdf_files)
            
            # Group similar PDFs if not stopped
            if not self.stop_event.is_set():
                self.status_updated.emit(
                    self.tr("scanner.finding_duplicates", "Finding duplicates..."),
                    0, 0
                )
                self._find_duplicates()
            
            # Emit final status
            self.scan_complete = True
            self.status_updated.emit(
                self.tr("scanner.scan_complete", "Scan complete! Found {groups} duplicate groups.").format(
                    groups=len(self.duplicate_groups)
                ),
                self.scanned_files, self.total_files
            )
                
        except Exception as e:
            error_msg = self.tr("scanner.scan_error", "Error during scanning: {error}").format(error=str(e))
            logger.error(error_msg)
            if self.status_callback:
                self.status_callback(self.tr("scanner.error_prefix", "Error: {error}").format(error=str(e)), 0, 0)
        finally:
            self.stop_event.set()
    
    def start_scan(self):
        """Start the scan operation."""
        try:
            if not hasattr(self, 'scan_directory'):
                logger.error("scan_directory method not found in PDFScanner")
                return
                
            # Get scan parameters (these should be set before starting the scan)
            scan_dir = getattr(self, 'scan_directory', '')
            recursive = getattr(self, 'recursive', True)
            min_size = getattr(self, 'min_file_size', 1024)  # 1KB default min
            max_size = getattr(self, 'max_file_size', 1024*1024*1024)  # 1GB default max
            
            if not scan_dir or not os.path.isdir(scan_dir):
                logger.error(f"Invalid scan directory: {scan_dir}")
                return
                
            logger.info(f"Starting scan in directory: {scan_dir}")
            self.scan_directory(
                directory=scan_dir,
                recursive=recursive,
                min_file_size=min_size,
                max_file_size=max_size
            )
            
            # Emit finished signal with results
            self.finished.emit(self.duplicate_groups)
            
        except Exception as e:
            logger.error(f"Error in start_scan: {e}", exc_info=True)
            self.finished.emit([])
    
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
    
    def _process_files(self, file_paths: List[str]) -> None:
        """Process PDF files in parallel."""
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._process_single_file, path): path for path in file_paths}
            
            for future in as_completed(futures):
                if self.stop_event.is_set():
                    break
                    
                path = futures[future]
                try:
                    result = future.result()
                    if result and not self.stop_event.is_set():
                        with self.lock:
                            self.scanned_files += 1
                            
                        # Emit progress update
                        self.progress_updated.emit(
                            self.scanned_files, 
                            self.total_files, 
                            path
                        )
                            
                except Exception as e:
                    error_msg = self.tr("scanner.file_error", "Error processing {file}: {error}").format(
                        file=os.path.basename(path), error=str(e)
                    )
                    logger.error(error_msg)
    
    def _update_status(self, message: str):
        """Update the status using the status callback if available.
        
        Args:
            message: Status message to display
        """
        if self.status_callback:
            try:
                self.status_callback(message, self.scanned_files, self.total_files)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def _process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Process a single PDF file and extract its metadata."""
        try:
            if not file_path or not isinstance(file_path, str):
                logger.warning(f"Received invalid file_path: {file_path}. Expected non-empty string.")
                return None
            
            if self.stop_event.is_set():
                return None
                
            # Update status
            self._update_status(
                self.tr("scanner.status.processing_file", "Processing {current}/{total}: {file}")
                .format(
                    current=self.scanned_files + 1, 
                    total=self.total_files, 
                    file=os.path.basename(file_path)
                )
            )
            
            # Process the file
            doc = self._process_single_file(file_path)
            if doc is None:
                return None
            
            # Get document info with safe defaults
            try:
                # Get file stats
                file_stats = os.stat(file_path)
                file_size = file_stats.st_size
                created = getattr(file_stats, 'st_ctime', 0)
                modified = getattr(file_stats, 'st_mtime', 0)
                
                # Get PDF type
                try:
                    pdf_type = self.comparator.detect_pdf_type(file_path)
                    pdf_type_str = pdf_type.value if hasattr(pdf_type, 'value') else 'unknown'
                except Exception as e:
                    logger.warning(f"Could not detect PDF type for {file_path}: {e}")
                    pdf_type_str = 'unknown'
                
                # Get document attributes with safe defaults
                file_info = {
                    'path': file_path,
                    'size': file_size,
                    'pages': 0,  # Not available in PDFDocument
                    'title': os.path.basename(file_path),
                    'author': '',
                    'created': created,
                    'modified': modified,
                    'hash': getattr(doc, 'content_hash', ''),
                    'image_hash': getattr(doc, 'image_hash', ''),
                    'type': pdf_type_str
                }
                
                # Update scan counter
                with self.lock:
                    self.scanned_files += 1
                
                return file_info
                
            except Exception as e:
                logger.error(f"Error processing file info for {file_path}: {e}", exc_info=True)
                return None
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)
            return None
    
    def _process_single_file(self, file_path: str) -> Optional[PDFDocument]:
        """Process a single PDF file.
        
        Args:
            file_path: Path to the PDF file to process
            
        Returns:
            PDFDocument instance if successful, None otherwise
        """
        # Validate input
        if not file_path or not isinstance(file_path, str):
            logger.warning(f"Invalid file path: {file_path}")
            return None
            
        if not os.path.isfile(file_path):
            logger.warning(f"File not found: {file_path}")
            return None
            
        if not file_path.lower().endswith('.pdf'):
            logger.debug(f"Skipping non-PDF file: {file_path}")
            return None
            
        # Track the last status message to avoid duplicates
        last_status = [None]  # Using a list to work around Python's scoping rules
        
        def _progress(msg: str):
            try:
                if self.status_callback and isinstance(msg, str) and msg and msg != last_status[0]:
                    # Add file count to the status message
                    status_msg = f"[{self.scanned_files+1}/{self.total_files}] {msg}"
                    self.status_callback(status_msg, self.scanned_files, self.total_files)
                    last_status[0] = msg  # Store the base message to avoid duplicates
            except Exception as e:
                logger.debug(f"Error in progress callback: {e}")
        
        # Process the PDF document with our progress callback
        try:
            logger.debug(f"Processing PDF: {file_path}")
            doc = PDFDocument(file_path, progress_callback=_progress)
            if doc is None:
                logger.warning(f"Failed to load PDF: {file_path}")
            return doc
            
        except Exception as e:
            error_msg = self.tr("scanner.load_error", "Error loading PDF {file}: {error}").format(
                file=os.path.basename(file_path), error=str(e))
            logger.error(error_msg, exc_info=True)
            return None
    
    def _compare_files(self, file1: Dict[str, Any], file2: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Compare two PDF files and return comparison results.
        
        Args:
            file1: First file info dict
            file2: Second file info dict
            
        Returns:
            Dictionary with comparison results or None if comparison failed
        """
        try:
            # Skip if files are the same
            if file1['path'] == file2['path']:
                return None
                
            # Compare the files
            result = self.comparator.compare_pdfs(file1['path'], file2['path'])
            
            # Log the comparison result
            logger.debug(f"Compared {file1['path']} with {file2['path']}: "
                       f"similarity={result['similarity']:.2f}, match={result['match']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error comparing {file1['path']} with {file2['path']}: {e}", exc_info=True)
            return None
    
    def _find_duplicates(self) -> None:
        """Find duplicate PDFs using content hash, image hash, and direct comparison."""
        try:
            # First pass: Group by content hash (exact matches)
            content_hash_groups = {}
            all_files = []
            
            # Update status
            self.status_updated.emit(
                self.tr("scanner.status.analyzing_files", "Analyzing files..."),
                0, 0
            )
            
            # Ensure scan_results is a dictionary
            if not isinstance(self.scan_results, dict):
                error_msg = self.tr("scanner.error.invalid_scan_results", "Invalid scan results format")
                logger.error(f"{error_msg}: {type(self.scan_results)}")
                self.status_updated.emit(error_msg, 0, 0)
                return
            
            # Flatten the scan_results into a single list of files
            for key, value in self.scan_results.items():
                if self.stop_event.is_set():
                    return
                    
                if isinstance(value, list):
                    all_files.extend([f for f in value if isinstance(f, dict) and 'path' in f])
                elif isinstance(value, dict) and 'path' in value:
                    all_files.append(value)
                else:
                    logger.warning(f"Unexpected item in scan_results: {value}")
            
            total_files = len(all_files)
            if total_files == 0:
                self.status_updated.emit(
                    self.tr("scanner.status.no_files_found", "No PDF files found to analyze"),
                    0, 0
                )
                return
                
            # Group files by content hash
            for file_info in all_files:
                if not isinstance(file_info, dict) or 'hash' not in file_info:
                    continue
                    
                content_hash = file_info['hash']
                if content_hash not in content_hash_groups:
                    content_hash_groups[content_hash] = []
                content_hash_groups[content_hash].append(file_info)
            
            # Add content hash groups as duplicate groups
            for file_list in content_hash_groups.values():
                if len(file_list) > 1:
                    self.duplicate_groups.append({
                        'type': 'content',
                        'files': file_list,
                        'similarity': 1.0,
                        'method': 'content_hash',
                        'details': {'message': 'Exact content match'}
                    })
                    
        except Exception as e:
            error_msg = self.tr("scanner.error.duplicate_find_error", "Error finding duplicates: {error}").format(
                error=str(e)
            )
            logger.error(error_msg, exc_info=True)
            self.status_updated.emit(error_msg, 0, 0)
            if len(file_list) > 1:
                self.duplicate_groups.append({
                    'type': 'content',
                    'files': file_list,
                    'similarity': 1.0,
                    'method': 'content_hash',
                    'details': {'message': 'Exact content match'}
                })
        
        # Second pass: For files with unique content hashes, group by image hash
        try:
            # Get files that weren't already matched by content hash
            unmatched_files = []
            for file_list in content_hash_groups.values():
                if len(file_list) == 1:
                    unmatched_files.append(file_list[0])
            
            if len(unmatched_files) > 1:
                self.status_updated.emit(
                    self.tr("scanner.status.comparing_images", "Comparing images for {count} files...").format(
                        count=len(unmatched_files)
                    ),
                    0, 0
                )
                
                # Group by image hash
                image_hash_groups = {}
                for i, file_info in enumerate(unmatched_files):
                    if self.stop_event.is_set():
                        return
                        
                    # Update progress
                    if i % 10 == 0:  # Update progress every 10 files
                        progress = int((i / len(unmatched_files)) * 100)
                        self.progress_updated.emit(i, len(unmatched_files))
                    
                    if 'image_hash' not in file_info:
                        continue
                        
                    img_hash = file_info['image_hash']
                    if img_hash not in image_hash_groups:
                        image_hash_groups[img_hash] = []
                    image_hash_groups[img_hash].append(file_info)
                
                # Add image hash groups as duplicate groups
                for file_list in image_hash_groups.values():
                    if len(file_list) > 1:
                        self.duplicate_groups.append({
                            'type': 'image',
                            'files': file_list,
                            'similarity': 0.95,  # High confidence for exact image hash match
                            'method': 'image_hash',
                            'details': {'message': 'Similar image content'}
                        })
        except Exception as e:
            error_msg = self.tr("scanner.error.image_comparison_error", "Error during image comparison: {error}").format(
                error=str(e)
            )
            logger.error(error_msg, exc_info=True)
            self.status_updated.emit(error_msg, 0, 0)
        # Final cleanup and emit completion
        try:
            # Emit final status
            self.status_updated.emit(
                self.tr("scanner.status.completed", "Scan completed. Found {count} duplicate groups").format(
                    count=len(self.duplicate_groups)
                ),
                100, 100  # 100% progress
            )
            
            # Log completion
            logger.info(f"Scan completed. Found {len(self.duplicate_groups)} duplicate groups")
            
            # Emit finished signal with results
            self.finished.emit(self.duplicate_groups)
            
        except Exception as e:
            error_msg = self.tr("scanner.error.finalize_error", "Error finalizing scan: {error}").format(
                error=str(e)
            )
            logger.error(error_msg, exc_info=True)
            self.status_updated.emit(error_msg, 0, 0)
            self.finished.emit([])  # Emit empty results on error
        
        # All done - the finished signal has been emitted
        return
    
    def _compare_and_group_files(self, file_list: List[Dict[str, Any]]) -> None:
        """Compare files in a group and create duplicate groups based on similarity.
        
        Args:
            file_list: List of file info dicts to compare
        """
        if len(file_list) < 2:
            return
            
        # Sort files by size to compare similar-sized files first
        file_list.sort(key=lambda x: x['size'])
        
        # Compare each file with others in the group
        processed = set()
        for i, file1 in enumerate(file_list):
            if file1['path'] in processed:
                continue
                
            # Create a new group for this file
            group = [file1]
            processed.add(file1['path'])
            
            # Compare with other files
            for file2 in file_list[i+1:]:
                if file2['path'] in processed:
                    continue
                    
                # Skip if file sizes are too different
                if abs(file1['size'] - file2['size']) / max(file1['size'], 1) > 0.5:
                    continue
                    
                # Compare the files
                result = self._compare_files(file1, file2)
                if result and result['match']:
                    group.append(file2)
                    processed.add(file2['path'])
            
            # If we found duplicates, add them to the results
            if len(group) > 1:
                # Calculate average similarity
                similarities = []
                for file2 in group[1:]:
                    result = self._compare_files(file1, file2)
                    if result:
                        similarities.append(result['similarity'])
                
                avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
                
                # Add to duplicate groups
                self.duplicate_groups.append({
                    'type': group[0]['type'],
                    'files': group,
                    'similarity': avg_similarity,
                    'method': 'direct_comparison',
                    'details': {
                        'message': f"Found {len(group)} similar files",
                        'comparison_method': 'direct_comparison'
                    }
                })
    
    def get_duplicate_groups(self) -> List[List[PDFDocument]]:
        """Get the list of duplicate groups found."""
        return self.duplicate_groups
    
    def get_scan_summary(self) -> dict:
        """Get a summary of the scan results.
        
        Returns:
            Dictionary containing scan summary information
        """
        # Calculate basic statistics
        total_files = len(self.scan_results)
        total_duplicates = sum(len(group['files']) - 1 for group in self.duplicate_groups)
        space_savings = sum(
            group['files'][0]['size'] * (len(group['files']) - 1) 
            for group in self.duplicate_groups
        )
        
        # Count files by type
        file_types = {}
        for file_info in self.scan_results.values():
            file_type = file_info.get('type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        # Count comparison methods
        comparison_methods = {}
        for group in self.duplicate_groups:
            method = group.get('method', 'unknown')
            comparison_methods[method] = comparison_methods.get(method, 0) + len(group['files'])
        
        # Calculate average similarity for each group
        avg_similarities = []
        for group in self.duplicate_groups:
            if 'similarity' in group:
                avg_similarities.append(group['similarity'])
        
        avg_similarity = sum(avg_similarities) / len(avg_similarities) if avg_similarities else 0.0
        
        # Format the summary
        summary = {
            'total_files': total_files,
            'scanned_files': self.scanned_files,
            'duplicate_groups': len(self.duplicate_groups),
            'total_duplicates': total_duplicates,
            'space_savings': space_savings,
            'file_types': file_types,
            'comparison_methods': comparison_methods,
            'avg_similarity': avg_similarity,
            'scan_time': time.time() - self.start_time if self.start_time else 0,
            'details': {
                'file_types': file_types,
                'comparison_methods': comparison_methods,
                'avg_similarity': avg_similarity,
                'total_potential_savings': f"{space_savings / (1024 * 1024):.2f} MB"
            }
        }
        
        # Add human-readable statistics
        summary['stats'] = [
            f"Total files scanned: {total_files}",
            f"Duplicate groups found: {len(self.duplicate_groups)}",
            f"Total duplicate files: {total_duplicates}",
            f"Potential space savings: {space_savings / (1024 * 1024):.2f} MB",
            f"Average similarity in duplicate groups: {avg_similarity:.1%}",
            f"Scan time: {time.time() - self.start_time:.2f} seconds" if self.start_time else ""
        ]
        
        # Add file type breakdown
        if file_types:
            summary['stats'].append("\nFile types:")
            for file_type, count in file_types.items():
                summary['stats'].append(f"  - {file_type}: {count} files")
        
        # Add comparison methods breakdown
        if comparison_methods:
            summary['stats'].append("\nComparison methods:")
            for method, count in comparison_methods.items():
                summary['stats'].append(f"  - {method}: {count} files")
        
        return summary
