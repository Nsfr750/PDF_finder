import os
import hashlib
import logging
import tempfile
import time
import io
from typing import List, Dict, Any, Tuple, Optional, TYPE_CHECKING
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from wand.image import Image as WandImage
import fitz  # PyMuPDF
from tqdm import tqdm

# Set up logger
logger = logging.getLogger(__name__)

# For type hints
if TYPE_CHECKING:
    from wand.image import Image as WandImageType

# Global flag to track if Ghostscript is available
GHOSTSCRIPT_AVAILABLE = False
try:
    from pdf2image import convert_from_path
    GHOSTSCRIPT_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.warning("Ghostscript not available. Using fallback PDF processing. Some features may be limited.")
    logger.debug(f"Error: {e}")

class ProgressTracker:
    """Helper class to track and report progress."""
    def __init__(self, total_steps: int = 100):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.last_update = self.start_time
        self.pbar = None
        
    def update(self, step: int = 1, description: str = None):
        """Update progress and return current status."""
        self.current_step = min(self.current_step + step, self.total_steps)
        now = time.time()
        
        # Only update at most 10 times per second
        if now - self.last_update < 0.1 and self.current_step < self.total_steps:
            return
            
        self.last_update = now
        elapsed = now - self.start_time
        progress = self.current_step / self.total_steps
        
        if self.pbar:
            self.pbar.update(step)
            if description:
                self.pbar.set_description(description)
                
        return {
            'progress': progress,
            'elapsed': elapsed,
            'remaining': (elapsed / self.current_step * (self.total_steps - self.current_step)) if self.current_step > 0 else 0,
            'current': self.current_step,
            'total': self.total_steps
        }

def extract_first_page_pdf(pdf_path: str, progress_callback: callable = None) -> Optional['WandImageType']:
    """Extract the first page of a PDF as an image using Wand with optimizations."""
    try:
        # Try PyMuPDF first as it's generally faster
        try:
            with fitz.open(pdf_path) as doc:
                if doc.page_count == 0:
                    return None
                
                if progress_callback:
                    progress_callback("Extracting page with PyMuPDF...")
                
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=72, alpha=False)
                
                with WandImage(
                    width=pix.width,
                    height=pix.height,
                    depth=8,
                    colorspace='rgb',
                    background='white'
                ) as img:
                    img.import_pixels(0, 0, pix.width, pix.height, 'RGB', pix.samples)
                    return img.clone()
        except Exception as e:
            logger.debug(f"PyMuPDF extraction failed, trying Ghostscript: {e}")
            
        # Fall back to Ghostscript if PyMuPDF fails
        if GHOSTSCRIPT_AVAILABLE:
            try:
                if progress_callback:
                    progress_callback("Extracting page with Ghostscript...")
                
                images = convert_from_path(
                    pdf_path,
                    first_page=1,
                    last_page=1,
                    dpi=72,
                    fmt='jpeg',
                    thread_safe=True
                )
                
                if images:
                    with io.BytesIO() as output:
                        images[0].save(output, format='JPEG', quality=85, optimize=True)
                        output.seek(0)
                        with WandImage(blob=output.read()) as img:
                            return img.clone()
            except Exception as e:
                logger.debug(f"Ghostscript extraction failed: {e}")
        
        return None
    except Exception as e:
        logger.error(f"Error extracting first page: {e}")
        return None

def calculate_hash(image: 'WandImageType', hash_size: int = 8) -> np.ndarray:
    """Calculate perceptual hash of an image using Wand."""
    try:
        with image.clone() as img:
            img.transform_colorspace('gray')
            img.resize(hash_size + 1, hash_size, 'lanczos')
            
            # Get pixel data as numpy array
            img_data = np.array(img)
            
            # Calculate differences between adjacent pixels
            diff = img_data[:, 1:] > img_data[:, :-1]
            return diff.flatten()
    except Exception as e:
        logger.error(f"Error calculating hash: {e}")
        return np.zeros(hash_size * hash_size, dtype=bool)

def process_pdf_file(file_path: str, min_size: int, max_size: int, hash_size: int, 
                    progress_callback: callable = None) -> Optional[Tuple[str, np.ndarray, Dict[str, Any]]]:
    """Process a single PDF file with progress callbacks."""
    try:
        file_path = Path(file_path)
        file_size = file_path.stat().st_size
        
        if not (min_size <= file_size <= max_size):
            return None
            
        if progress_callback:
            progress_callback(f"Processing {file_path.name}...")
            
        image = extract_first_page_pdf(str(file_path), progress_callback)
        if image is None:
            return None
            
        phash = calculate_hash(image, hash_size)
        
        return (str(file_path), (phash, {
            'path': str(file_path),
            'filename': file_path.name,
            'size': file_size,
            'modified': file_path.stat().st_mtime
        }))
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None

def find_duplicates(
    directory: str = '',
    recursive: bool = True,
    min_file_size: int = 1024,
    max_file_size: int = 100 * 1024 * 1024,
    hash_size: int = 8,
    threshold: float = 0.9,
    processed_files: List[Dict[str, Any]] = None,
    progress_callback: Optional[callable] = None
) -> List[List[Dict[str, Any]]]:
    """Find duplicate PDF files with progress tracking.
    
    Args:
        directory: Directory to search for PDFs
        recursive: Whether to search subdirectories
        min_file_size: Minimum file size in bytes
        max_file_size: Maximum file size in bytes
        hash_size: Size of the perceptual hash (higher = more accurate but slower)
        threshold: Similarity threshold (0-1) to consider files as duplicates
        processed_files: Optional list of pre-processed files with 'path' and 'size' keys
        progress_callback: Callback function for progress updates (receives status message)
        
    Returns:
        List of duplicate groups, where each group is a list of file info dicts
    """
    start_time = time.time()
    
    def update_progress(message: str, current: int = None, total: int = None) -> bool:
        """Helper to format and send progress updates."""
        if progress_callback is not None:
            if current is not None and total is not None and total > 0:
                message = f"{message} ({current}/{total})"
            return progress_callback(message)
        return True
    
    # Find all PDF files if not provided
    if processed_files is None:
        if not directory:
            return []
            
        if not update_progress("Scanning for PDF files..."):
            return []
            
        path = Path(directory)
        pattern = '**/*.pdf' if recursive else '*.pdf'
        
        try:
            pdf_files = list(path.glob(pattern))
            if not pdf_files:
                update_progress("No PDF files found")
                return []
                
            if not update_progress(f"Found {len(pdf_files)} PDF files to process"):
                return []
                
        except Exception as e:
            update_progress(f"Error scanning for PDF files: {str(e)}")
            logger.error(f"Error scanning for PDF files: {e}", exc_info=True)
            return []
    else:
        pdf_files = [Path(f['path']) for f in processed_files]
    
    # Process files in parallel with better progress tracking
    file_hashes = {}
    total_files = len(pdf_files)
    processed_count = 0
    
    def process_file_wrapper(file_path, min_size, max_size, h_size):
        """Wrapper to process a single file and track progress."""
        nonlocal processed_count
        result = process_pdf_file(file_path, min_size, max_size, h_size)
        processed_count += 1
        
        # Update progress every 5 files or for the last file
        if processed_count % 5 == 0 or processed_count == total_files:
            if not update_progress(
                "Processing PDFs", 
                current=processed_count, 
                total=total_files
            ):
                return None
                
        return result
    
    try:
        with ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 2)) as executor:
            # Submit all processing tasks
            futures = {
                executor.submit(
                    process_file_wrapper,
                    str(pdf_file),
                    min_file_size,
                    max_file_size,
                    hash_size
                ): pdf_file for pdf_file in pdf_files
            }
            
            # Process completed tasks
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        file_path, (phash, file_info) = result
                        file_hashes[file_path] = (phash, file_info)
                except Exception as e:
                    logger.error(f"Error processing file: {e}", exc_info=True)
                
                # Check if we should cancel
                if progress_callback and not progress_callback(""):
                    logger.info("Processing cancelled by user")
                    return []
        
        # Update progress for duplicate detection phase
        if not update_progress("Analyzing file similarities..."):
            return []
        
        # Find duplicates by comparing hashes
        duplicates = []
        processed = set()
        total_files = len(file_hashes)
        
        if total_files == 0:
            update_progress("No valid PDF files found to compare")
            return []
        
        # Sort files by size (largest first) for better progress estimation
        sorted_files = sorted(
            file_hashes.items(),
            key=lambda x: x[1][1]['size'],
            reverse=True
        )
        
        # Compare files to find duplicates
        for i, (file1, (hash1, file_info1)) in enumerate(sorted_files):
            if file1 in processed:
                continue
                
            # Update progress every 5 files or for the last file
            if i % 5 == 0 or i == len(sorted_files) - 1:
                if not update_progress(
                    f"Analyzing {i+1}/{total_files} files",
                    current=i,
                    total=total_files
                ):
                    return []
            
            duplicate_group = [file_info1]
            
            # Compare with other files
            for file2, (hash2, file_info2) in sorted_files[i+1:]:
                if file2 in processed:
                    continue
                    
                # Calculate similarity
                similarity = np.mean(hash1 == hash2)
                if similarity >= threshold:
                    duplicate_group.append(file_info2)
                    processed.add(file2)
            
            if len(duplicate_group) > 1:
                duplicates.append(duplicate_group)
            
            processed.add(file1)
        
        # Final update
        update_progress(
            f"Found {len(duplicates)} duplicate groups in {time.time() - start_time:.1f} seconds"
        )
        
        return duplicates
        
    except Exception as e:
        error_msg = f"Error during duplicate detection: {str(e)}"
        update_progress(error_msg)
        logger.error(error_msg, exc_info=True)
        return []

def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing file information
    """
    try:
        file_stat = os.stat(file_path)
        
        # Get basic file info
        info = {
            'path': file_path,
            'size': file_stat.st_size,
            'modified': file_stat.st_mtime,
            'pages': 0,
            'title': '',
            'author': '',
            'subject': '',
            'keywords': '',
            'creator': '',
            'producer': ''
        }
        
        # Try to extract PDF metadata
        try:
            with fitz.open(file_path) as doc:
                info['pages'] = len(doc)
                
                # Get document metadata
                meta = doc.metadata
                if meta:
                    info.update({
                        'title': meta.get('title', ''),
                        'author': meta.get('author', ''),
                        'subject': meta.get('subject', ''),
                        'keywords': meta.get('keywords', ''),
                        'creator': meta.get('creator', ''),
                        'producer': meta.get('producer', '')
                    })
        except Exception as e:
            logger.warning(f"Could not extract PDF metadata for {file_path}: {e}")
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting info for {file_path}: {e}")
        return {}

def calculate_file_hash(file_path: str, block_size: int = 65536) -> str:
    """
    Calculate the MD5 hash of a file.
    
    Args:
        file_path: Path to the file
        block_size: Size of blocks to read at a time
        
    Returns:
        MD5 hash of the file
    """
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(block_size)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return ""

def calculate_image_hash(image_path: str, hash_size: int = 8) -> str:
    """
    Calculate the perceptual hash of an image using Wand.
    
    Args:
        image_path: Path to the image file
        hash_size: Size of the hash (higher = more accurate but slower)
        
    Returns:
        Perceptual hash of the image
    """
    try:
        with WandImage(filename=image_path) as img:
            # Convert to grayscale and resize for consistent hashing
            img.transform_colorspace('gray')
            img.resize(hash_size, hash_size, 'lanczos')
            
            # Get pixel data as numpy array
            img_data = np.array(img)
            
            # Calculate average pixel value
            avg = np.mean(img_data)
            
            # Create hash string (1 if pixel > avg, 0 otherwise)
            hash_str = ''.join(['1' if p > avg else '0' for p in img_data.flatten()])
            return hash_str
    except Exception as e:
        logger.error(f"Error calculating image hash for {image_path}: {e}")
        return ""

def compare_hashes(hash1: str, hash2: str) -> float:
    """
    Compare two hashes and return a similarity score.
    
    Args:
        hash1: First hash
        hash2: Second hash
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    if not hash1 or not hash2 or len(hash1) != len(hash2):
        return 0.0
    
    # Calculate Hamming distance
    distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
    return 1.0 - (distance / len(hash1))

def extract_first_page_image(pdf_path: str, output_path: str, dpi: int = 100) -> bool:
    """
    Extract the first page of a PDF as an image using Wand.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the output image
        dpi: DPI for the output image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with WandImage(filename=f"{pdf_path}[0]", resolution=dpi) as img:
            # Convert to RGB and save as PNG
            img.format = 'png'
            img.save(filename=output_path)
            return True
    except Exception as e:
        logger.error(f"Error extracting first page from {pdf_path}: {e}")
        return False

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_utils.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    duplicates = find_duplicates(directory)
    
    print(f"\nFound {len(duplicates)} groups of duplicate PDFs:")
    for i, group in enumerate(duplicates, 1):
        print(f"\nGroup {i}:")
        for file_info in group:
            file_path = file_info.get('path', '')
            size = file_info.get('size', 0)
            print(f"  - {file_path} ({size / 1024:.1f} KB)")
