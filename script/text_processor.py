"""Text processing for PDF comparison."""
import re
import logging
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
        """Extract and process text from PDF."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            return self._process_text(text)
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
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
