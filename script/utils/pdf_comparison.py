"""
PDF comparison module for PDF Duplicate Finder.

This module provides functionality to compare PDFs using different methods:
- Image-based comparison for scanned PDFs
- Text-based diff for searchable PDFs
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

import fitz  # PyMuPDF
import numpy as np
import cv2
from wand.image import Image as WandImage

# Configure logging
logger = logging.getLogger(__name__)

class PDFType(Enum):
    """Enum representing the type of PDF."""
    UNKNOWN = "unknown"
    SCANNED = "scanned"
    SEARCHABLE = "searchable"
    MIXED = "mixed"

class PDFComparator:
    """Class for comparing PDF documents using different methods."""
    
    def __init__(self, dpi: int = 200, threshold: float = 0.95):
        """Initialize the PDF comparator.
        
        Args:
            dpi: DPI to use for image conversion
            threshold: Similarity threshold (0-1) for considering pages as similar
        """
        self.dpi = dpi
        self.threshold = threshold
    
    def detect_pdf_type(self, file_path: str) -> PDFType:
        """Detect if a PDF is scanned, searchable, or mixed.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            PDFType indicating the type of PDF
        """
        try:
            doc = fitz.open(file_path)
            has_text = False
            has_images = False
            
            for page_num in range(min(5, len(doc))):  # Check first 5 pages or all if fewer
                page = doc.load_page(page_num)
                text = page.get_text("text")
                image_list = page.get_images(full=True)
                
                if text.strip():
                    has_text = True
                if image_list:
                    has_images = True
                
                # Early exit if we've found both
                if has_text and has_images:
                    break
            
            doc.close()
            
            if has_text and has_images:
                return PDFType.MIXED
            elif has_text:
                return PDFType.SEARCHABLE
            elif has_images:
                return PDFType.SCANNED
            else:
                return PDFType.UNKNOWN
                
        except Exception as e:
            logger.error(f"Error detecting PDF type for {file_path}: {e}")
            return PDFType.UNKNOWN
    
    def compare_pdfs(self, file1: str, file2: str) -> Dict[str, Any]:
        """Compare two PDF files using the appropriate method.
        
        Args:
            file1: Path to the first PDF file
            file2: Path to the second PDF file
            
        Returns:
            Dictionary containing comparison results
        """
        # Detect PDF types
        type1 = self.detect_pdf_type(file1)
        type2 = self.detect_pdf_type(file2)
        
        # If either PDF is scanned or mixed, use image comparison
        if type1 in (PDFType.SCANNED, PDFType.MIXED) or type2 in (PDFType.SCANNED, PDFType.MIXED):
            logger.info(f"Using image-based comparison for {file1} and {file2}")
            return self._compare_pdfs_as_images(file1, file2)
        # If both are searchable, use text comparison
        elif type1 == PDFType.SEARCHABLE and type2 == PDFType.SEARCHABLE:
            logger.info(f"Using text-based comparison for {file1} and {file2}")
            return self._compare_pdfs_as_text(file1, file2)
        else:
            # Fall back to image comparison for unknown types
            logger.warning(f"Unknown PDF types, falling back to image comparison for {file1} and {file2}")
            return self._compare_pdfs_as_images(file1, file2)
    
    def _compare_pdfs_as_images(self, file1: str, file2: str) -> Dict[str, Any]:
        """Compare two PDFs by converting them to images and comparing visually.
        
        Args:
            file1: Path to the first PDF file
            file2: Path to the second PDF file
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            # Open both PDFs
            doc1 = fitz.open(file1)
            doc2 = fitz.open(file2)
            
            # Check if page counts match
            if len(doc1) != len(doc2):
                return {
                    "similarity": 0.0,
                    "match": False,
                    "method": "image",
                    "message": "Page counts differ",
                    "details": {"file1_pages": len(doc1), "file2_pages": len(doc2)}
                }
            
            # Compare each page
            similarities = []
            for page_num in range(len(doc1)):
                # Render pages to pixmaps
                pix1 = doc1.load_page(page_num).get_pixmap(dpi=self.dpi)
                pix2 = doc2.load_page(page_num).get_pixmap(dpi=self.dpi)

                # Convert pixmap samples to numpy arrays (H, W, C)
                arr1 = np.frombuffer(pix1.samples, dtype=np.uint8)
                arr1 = arr1.reshape(pix1.height, pix1.width, pix1.n)
                arr2 = np.frombuffer(pix2.samples, dtype=np.uint8)
                arr2 = arr2.reshape(pix2.height, pix2.width, pix2.n)

                # Ensure RGB by taking first 3 channels when available
                if arr1.shape[2] >= 3:
                    arr1 = arr1[..., :3]
                if arr2.shape[2] >= 3:
                    arr2 = arr2[..., :3]

                # Convert to grayscale using luminosity method
                img1_array = np.dot(arr1[..., :3].astype(np.float32), [0.2989, 0.5870, 0.1140])
                img2_array = np.dot(arr2[..., :3].astype(np.float32), [0.2989, 0.5870, 0.1140])

                # Resize to the smaller common shape if different sizes
                if img1_array.shape != img2_array.shape:
                    min_height = min(img1_array.shape[0], img2_array.shape[0])
                    min_width = min(img1_array.shape[1], img2_array.shape[1])
                    img1_array = cv2.resize(img1_array, (min_width, min_height), interpolation=cv2.INTER_AREA)
                    img2_array = cv2.resize(img2_array, (min_width, min_height), interpolation=cv2.INTER_AREA)

                # Convert to uint8 for SSIM with fixed data_range
                img1_array = np.clip(img1_array, 0, 255).astype(np.uint8)
                img2_array = np.clip(img2_array, 0, 255).astype(np.uint8)
                
                # Calculate SSIM via OpenCV/NumPy implementation
                similarity = self._ssim(img1_array, img2_array)
                similarities.append(similarity)
            
            # Calculate average similarity
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
            
            doc1.close()
            doc2.close()
            
            return {
                "similarity": avg_similarity,
                "match": avg_similarity >= self.threshold,
                "method": "image",
                "message": "Comparison completed" if avg_similarity >= self.threshold else "Significant differences found",
                "details": {"page_similarities": similarities}
            }
            
        except Exception as e:
            logger.error(f"Error comparing PDFs as images: {e}", exc_info=True)
            return {
                "similarity": 0.0,
                "match": False,
                "method": "image",
                "message": f"Error during comparison: {str(e)}",
                "details": {}
            }
    
    def _compare_pdfs_as_text(self, file1: str, file2: str) -> Dict[str, Any]:
        """Compare two searchable PDFs by extracting and comparing their text content.
        
        Args:
            file1: Path to the first PDF file
            file2: Path to the second PDF file
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            # Extract text from both PDFs
            text1 = self._extract_text_from_pdf(file1)
            text2 = self._extract_text_from_pdf(file2)
            
            if not text1 or not text2:
                return {
                    "similarity": 0.0,
                    "match": False,
                    "method": "text",
                    "message": "Could not extract text from one or both PDFs",
                    "details": {"file1_text_length": len(text1) if text1 else 0, 
                              "file2_text_length": len(text2) if text2 else 0}
                }
            
            # Simple text similarity (can be replaced with more sophisticated diffing)
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, text1, text2).ratio()
            
            # Generate a simple diff
            from difflib import unified_diff
            diff = list(unified_diff(
                text1.splitlines(keepends=True),
                text2.splitlines(keepends=True),
                fromfile=Path(file1).name,
                tofile=Path(file2).name
            ))
            
            return {
                "similarity": similarity,
                "match": similarity >= self.threshold,
                "method": "text",
                "message": "Text content matches" if similarity >= self.threshold else "Text content differs",
                "details": {
                    "file1_text_length": len(text1),
                    "file2_text_length": len(text2),
                    "diff": ''.join(diff) if diff and len(diff) < 1000 else "Diff too large to display"
                }
            }
            
        except Exception as e:
            logger.error(f"Error comparing PDFs as text: {e}", exc_info=True)
            return {
                "similarity": 0.0,
                "match": False,
                "method": "text",
                "message": f"Error during text comparison: {str(e)}",
                "details": {}
            }
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""

    def _ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Compute SSIM between two uint8 grayscale images using OpenCV/NumPy.
        Args:
            img1: Grayscale image uint8 [H,W]
            img2: Grayscale image uint8 [H,W]
        Returns:
            SSIM value in [0,1]
        """
        try:
            if img1.shape != img2.shape:
                h = min(img1.shape[0], img2.shape[0])
                w = min(img1.shape[1], img2.shape[1])
                img1 = cv2.resize(img1, (w, h), interpolation=cv2.INTER_AREA)
                img2 = cv2.resize(img2, (w, h), interpolation=cv2.INTER_AREA)

            # Convert to float32 and normalize to [0,1]
            img1 = img1.astype(np.float32) / 255.0
            img2 = img2.astype(np.float32) / 255.0

            C1 = (0.01) ** 2
            C2 = (0.03) ** 2

            # Gaussian kernel window
            win_size = 11
            sigma = 1.5
            mu1 = cv2.GaussianBlur(img1, (win_size, win_size), sigma)
            mu2 = cv2.GaussianBlur(img2, (win_size, win_size), sigma)

            mu1_sq = mu1 * mu1
            mu2_sq = mu2 * mu2
            mu1_mu2 = mu1 * mu2

            sigma1_sq = cv2.GaussianBlur(img1 * img1, (win_size, win_size), sigma) - mu1_sq
            sigma2_sq = cv2.GaussianBlur(img2 * img2, (win_size, win_size), sigma) - mu2_sq
            sigma12 = cv2.GaussianBlur(img1 * img2, (win_size, win_size), sigma) - mu1_mu2

            ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2) + 1e-12)
            val = float(ssim_map.mean())

            # Clamp to [0,1]
            if val < 0:
                return 0.0
            if val > 1:
                return 1.0
            return val
        except Exception:
            return 0.0

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python pdf_comparison.py <pdf1> <pdf2>")
        sys.exit(1)
    
    comparator = PDFComparator()
    result = comparator.compare_pdfs(sys.argv[1], sys.argv[2])
    
    print(f"Comparison result: {result['message']}")
    print(f"Similarity: {result['similarity']:.2f}")
    print(f"Match: {result['match']}")
    print(f"Method: {result['method']}")
    
    if 'details' in result and 'diff' in result['details'] and result['details']['diff']:
        print("\nDifferences:")
        print(result['details']['diff'])
    elif 'details' in result and 'page_similarities' in result['details']:
        print("\nPage similarities:")
        for i, sim in enumerate(result['details']['page_similarities']):
            print(f"  Page {i+1}: {sim:.2f}")
