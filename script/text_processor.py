"""Text processing for PDF comparison."""
import re
import logging
import threading
import signal
from typing import Dict, List, Optional
from dataclasses import dataclass
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

@dataclass
class TextExtractionOptions:
    """Options for text extraction."""
    remove_punctuation: bool = True
    convert_to_lowercase: bool = True
    min_word_length: int = 3

class TextProcessor:
    """Handles text extraction and comparison."""
    
    def __init__(self, options: Optional[TextExtractionOptions] = None):
        self.options = options or TextExtractionOptions()
    
    def extract_text(self, file_path: str) -> str:
        """Extract and process text from PDF with timeout protection."""
        try:
            # Use timeout mechanism to prevent hanging
            result = self._extract_text_with_timeout(file_path, timeout=30.0)  # 30 second timeout
            return self._process_text(result)
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _extract_text_with_timeout(self, file_path: str, timeout: float = 30.0) -> str:
        """Extract text from PDF with timeout protection."""
        result_container = {'text': "", 'error': None}
        
        def extract_worker():
            try:
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text("text") + "\n"
                doc.close()
                result_container['text'] = text
            except Exception as e:
                result_container['error'] = e
        
        # Start extraction thread
        extract_thread = threading.Thread(target=extract_worker)
        extract_thread.daemon = True
        extract_thread.start()
        
        # Wait for completion with timeout
        extract_thread.join(timeout=timeout)
        
        if extract_thread.is_alive():
            # Thread is still running, timeout occurred
            logger.warning(f"Text extraction timed out for {file_path} after {timeout} seconds")
            raise TimeoutError(f"Text extraction timed out for {file_path}")
        
        if result_container['error']:
            raise result_container['error']
        
        return result_container['text']
    
    def _process_text(self, text: str) -> str:
        """Clean and process extracted text."""
        if self.options.convert_to_lowercase:
            text = text.lower()
        if self.options.remove_punctuation:
            text = re.sub(r'[^\w\s]', ' ', text)
        # Keep only words of minimum length
        words = [w for w in text.split() if len(w) >= self.options.min_word_length]
        return " ".join(words)
    
    @staticmethod
    def compare_texts(text1: str, text2: str) -> float:
        """Compare two texts and return similarity score (0.0 to 1.0)."""
        if not text1 or not text2:
            return 0.0
        # Simple Jaccard similarity
        set1 = set(text1.split())
        set2 = set(text2.split())
        if not set1 and not set2:
            return 1.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0
