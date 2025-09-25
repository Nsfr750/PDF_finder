"""PDF comparison functionality."""
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .text_processor import TextProcessor, TextExtractionOptions
from .filters import FilterBuilder

@dataclass
class PDFComparisonResult:
    """Result of comparing two PDFs."""
    file1: str
    file2: str
    similarity: float  # 0.0 to 1.0
    text_similarity: float  # 0.0 to 1.0
    size_diff: float  # ratio of sizes
    
class PDFComparator:
    """Handles PDF comparison with text and metadata."""
    
    def __init__(self, text_options: Optional[TextExtractionOptions] = None):
        self.text_processor = TextProcessor(text_options or TextExtractionOptions())
    
    def compare_files(self, file1: str, file2: str) -> PDFComparisonResult:
        """Compare two PDF files."""
        # Get file sizes
        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)
        size_diff = abs(size1 - size2) / max(size1, size2) if max(size1, size2) > 0 else 0
        
        # Compare text content
        text1 = self.text_processor.extract_text(file1)
        text2 = self.text_processor.extract_text(file2)
        text_sim = self.text_processor.compare_texts(text1, text2)
        
        # Combine metrics (simple average for now, could be weighted)
        similarity = (text_sim + (1 - size_diff)) / 2
        
        return PDFComparisonResult(
            file1=file1,
            file2=file2,
            similarity=similarity,
            text_similarity=text_sim,
            size_diff=size_diff
        )
    
    def find_duplicates(self, 
                       files: List[str], 
                       similarity_threshold: float = 0.9,
                       file_filter = None) -> List[Tuple[str, str, float]]:
        """
        Find duplicate PDFs in a list of files.
        
        Args:
            files: List of PDF file paths
            similarity_threshold: Minimum similarity score (0.0-1.0) to consider files duplicates
            file_filter: Optional filter function to pre-filter files
            
        Returns:
            List of tuples (file1, file2, similarity) for duplicate pairs
        """
        # Apply file filter if provided
        if file_filter is not None:
            files = [f for f in files if file_filter(f)]
            
        duplicates = []
        processed = set()
        
        for i, file1 in enumerate(files):
            if file1 in processed:
                continue
                
            group = [file1]
            
            for file2 in files[i+1:]:
                if file2 in processed:
                    continue
                    
                result = self.compare_files(file1, file2)
                if result.similarity >= similarity_threshold:
                    group.append(file2)
                    processed.add(file2)
            
            if len(group) > 1:
                # Add all pairs in the group
                for j in range(len(group)):
                    for k in range(j+1, len(group)):
                        result = self.compare_files(group[j], group[k])
                        duplicates.append((group[j], group[k], result.similarity))
                
                processed.add(file1)
        
        return duplicates
