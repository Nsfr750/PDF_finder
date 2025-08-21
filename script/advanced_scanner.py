"""Enhanced PDF scanner with text comparison and filtering."""
import os
import logging
from typing import List, Dict, Optional, Callable, Tuple
from pathlib import Path
from datetime import datetime

from .text_processor import TextProcessor, TextExtractionOptions
from .filters import FileFilter, FilterBuilder
from .pdf_comparator import PDFComparator, PDFComparisonResult

logger = logging.getLogger('PDFDuplicateFinder')

class AdvancedPDFScanner:
    """Enhanced PDF scanner with text comparison and filtering."""
    
    def __init__(self, 
                 comparison_threshold: float = 0.9,
                 text_similarity_threshold: float = 0.85,
                 enable_text_comparison: bool = True):
        """Initialize the advanced PDF scanner."""
        self.comparator = PDFComparator()
        self.text_processor = TextProcessor()
        self.comparison_threshold = comparison_threshold
        self.text_similarity_threshold = text_similarity_threshold
        self.enable_text_comparison = enable_text_comparison
        self.file_filters: List[FileFilter] = []
        
    def add_file_filter(self, file_filter: FileFilter) -> None:
        """Add a file filter."""
        self.file_filters.append(file_filter)
        
    def clear_filters(self) -> None:
        """Remove all file filters."""
        self.file_filters = []
        
    def _apply_filters(self, filepath: str) -> bool:
        """Check if file passes all filters."""
        if not self.file_filters:
            return True
        return all(f.matches(filepath) for f in self.file_filters)
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[Tuple[str, str, float]]:
        """Scan directory for duplicate PDFs with text comparison."""
        if not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")
            
        # Get all PDF files
        pdf_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    if self._apply_filters(file_path):
                        pdf_files.append(file_path)
            if not recursive:
                break
                
        # Find duplicates
        return self.find_duplicates(pdf_files)
    
    def find_duplicates(self, file_paths: List[str]) -> List[Tuple[str, str, float]]:
        """Find duplicate PDFs with text comparison."""
        duplicates = []
        processed = set()
        
        for i, file1 in enumerate(file_paths):
            if file1 in processed:
                continue
                
            group = [file1]
            
            for file2 in file_paths[i+1:]:
                if file2 in processed:
                    continue
                    
                # Compare files
                result = self.compare_files(file1, file2)
                if result.similarity >= self.comparison_threshold:
                    group.append(file2)
                    processed.add(file2)
            
            # Add all pairs in the group
            if len(group) > 1:
                for j in range(len(group)):
                    for k in range(j+1, len(group)):
                        result = self.compare_files(group[j], group[k])
                        duplicates.append((group[j], group[k], result.similarity))
                
                processed.add(file1)
        
        return duplicates
    
    def compare_files(self, file1: str, file2: str) -> PDFComparisonResult:
        """Compare two PDF files with both content and text analysis."""
        # Basic file comparison first
        result = self.comparator.compare_files(file1, file2)
        
        # Add text comparison if enabled
        if self.enable_text_comparison:
            text1 = self.text_processor.extract_text(file1)
            text2 = self.text_processor.extract_text(file2)
            text_sim = self.text_processor.compare_texts(text1, text2)
            
            # Update the similarity score with text comparison
            result.similarity = (result.similarity + text_sim) / 2
            result.text_similarity = text_sim
        
        return result
