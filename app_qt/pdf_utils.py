"""PDF utility functions for PDF Duplicate Finder."""
import os
import hashlib
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any
import logging
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError
from pdf2image import convert_from_path
from PIL import Image
import imagehash

logger = logging.getLogger('PDFDuplicateFinder')

class PDFUtils:
    """Utility class for PDF operations."""
    
    @staticmethod
    def get_pdf_metadata(file_path: str) -> dict:
        """Extract metadata from a PDF file."""
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                metadata = reader.metadata
                return {
                    'title': metadata.title or '',
                    'author': metadata.author or '',
                    'creator': metadata.creator or '',
                    'producer': metadata.producer or '',
                    'subject': metadata.subject or '',
                    'creation_date': str(metadata.creation_date) if hasattr(metadata, 'creation_date') else '',
                    'modification_date': str(metadata.modification_date) if hasattr(metadata, 'modification_date') else '',
                    'pages': len(reader.pages)
                }
        except Exception as e:
            logger.error(f"Error reading PDF metadata for {file_path}: {e}")
            return {}
    
    @staticmethod
    def generate_thumbnail(pdf_path: str, page_number: int = 0, size: tuple = (200, 200)) -> Optional[Image.Image]:
        """Generate a thumbnail for a PDF page."""
        try:
            # Convert the PDF page to an image
            images = convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)
            if not images:
                return None
                
            # Resize the image
            img = images[0]
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            logger.error(f"Error generating thumbnail for {pdf_path}: {e}")
            return None
    
    @staticmethod
    def calculate_file_hash(file_path: str, chunk_size: int = 8192) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    @staticmethod
    def calculate_content_hash(file_path: str) -> str:
        """Calculate a hash based on PDF content (text and structure)."""
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                content = []
                
                # Extract text from each page
                for page in reader.pages:
                    try:
                        content.append(page.extract_text() or "")
                    except Exception as e:
                        logger.warning(f"Error extracting text from page in {file_path}: {e}")
                
                # Add metadata to content
                if hasattr(reader, 'metadata') and reader.metadata:
                    content.append(str(reader.metadata))
                
                # Calculate hash of the combined content
                return hashlib.sha256("".join(content).encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating content hash for {file_path}: {e}")
            return ""
    
    @staticmethod
    def calculate_image_hash(file_path: str, page_number: int = 0) -> str:
        """Calculate a perceptual hash of a PDF page's image."""
        try:
            # Convert PDF page to image
            images = convert_from_path(file_path, first_page=page_number + 1, last_page=page_number + 1)
            if not images:
                return ""
                
            # Calculate perceptual hash
            img_hash = imagehash.average_hash(images[0])
            return str(img_hash)
        except Exception as e:
            logger.error(f"Error calculating image hash for {file_path}: {e}")
            return ""
    
    @staticmethod
    def are_similar_pdfs(file1: str, file2: str, similarity_threshold: float = 0.95) -> bool:
        """Check if two PDFs are similar based on content and structure."""
        try:
            # First, compare file hashes (exact match)
            if PDFUtils.calculate_file_hash(file1) == PDFUtils.calculate_file_hash(file2):
                return True
                
            # If not exact match, compare content hashes
            hash1 = PDFUtils.calculate_content_hash(file1)
            hash2 = PDFUtils.calculate_content_hash(file2)
            
            if not hash1 or not hash2:
                return False
                
            # Calculate similarity between hashes
            similarity = sum(1 for a, b in zip(hash1, hash2) if a == b) / max(len(hash1), len(hash2))
            return similarity >= similarity_threshold
            
        except Exception as e:
            logger.error(f"Error comparing PDFs {file1} and {file2}: {e}")
            return False
    
    @staticmethod
    def get_pdf_size(file_path: str) -> int:
        """Get the size of a PDF file in bytes."""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Error getting size of {file_path}: {e}")
            return 0
    
    @staticmethod
    def is_pdf(file_path: str) -> bool:
        """Check if a file is a valid PDF."""
        try:
            with open(file_path, 'rb') as f:
                # Check PDF header
                header = f.read(4)
                if header != b'%PDF':
                    return False
                    
                # Try to read the PDF to verify it's not corrupted
                f.seek(0)
                PdfReader(f)
                return True
        except:
            return False

class PDFDocument:
    """Class representing a PDF document with its metadata and hashes."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        self.metadata = {}
        self.content_hash = ""
        self.image_hash = ""
        self.thumbnail = None
        self.page_count = 0
        self.last_modified = os.path.getmtime(file_path)
        self._load()
    
    def _load(self):
        """Load PDF metadata and calculate hashes."""
        self.metadata = PDFUtils.get_pdf_metadata(self.file_path)
        self.content_hash = PDFUtils.calculate_content_hash(self.file_path)
        self.image_hash = PDFUtils.calculate_image_hash(self.file_path)
        self.thumbnail = PDFUtils.generate_thumbnail(self.file_path)
        self.page_count = self.metadata.get('pages', 0) if self.metadata else 0
    
    def __str__(self):
        return f"PDFDocument({self.file_name}, pages={self.page_count}, size={self.file_size} bytes)"
