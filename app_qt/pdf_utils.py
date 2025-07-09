import os
import hashlib
import tempfile
import fitz  # PyMuPDF
from PIL import Image
import imagehash
from typing import List, Dict, Any, Tuple, Optional, Union
import logging
from pathlib import Path

# Import utility functions
from .utils import get_file_path, get_file_info_dict

logger = logging.getLogger('PDFUtils')

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
            logger.warning(f"Could not extract metadata from {file_path}: {e}")
        
        return info
    except Exception as e:
        logger.error(f"Error getting info for {file_path}: {e}")
        return None

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
        return None

def calculate_image_hash(image_path: str, hash_size: int = 8) -> str:
    """
    Calculate the perceptual hash of an image.
    
    Args:
        image_path: Path to the image file
        hash_size: Size of the hash (higher = more accurate but slower)
        
    Returns:
        Perceptual hash of the image
    """
    try:
        with Image.open(image_path) as img:
            # Convert to grayscale and resize for consistency
            img = img.convert('L').resize((hash_size, hash_size), Image.Resampling.LANCZOS)
            # Calculate the average pixel value
            avg = sum(img.getdata()) / (hash_size * hash_size)
            # Create a binary hash based on whether pixels are above or below average
            bits = ''.join(['1' if pixel > avg else '0' for pixel in img.getdata()])
            return bits
    except Exception as e:
        logger.error(f"Error calculating image hash for {image_path}: {e}")
        return None

def compare_hashes(hash1: str, hash2: str) -> float:
    """
    Compare two hashes and return a similarity score.
    
    Args:
        hash1: First hash
        hash2: Second hash
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
    return 1 - (distance / len(hash1))

def extract_first_page_image(pdf_path: str, output_path: str, dpi: int = 100) -> bool:
    """
    Extract the first page of a PDF as an image.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the output image
        dpi: DPI for the output image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return False
        
        # Get the first page
        page = doc[0]
        
        # Calculate the zoom factor based on DPI
        zoom = dpi / 72  # 72 DPI is the default for PDFs
        mat = fitz.Matrix(zoom, zoom)
        
        # Render the page to an image
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Save the image
        pix.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Error extracting first page from {pdf_path}: {e}")
        return False

def find_duplicates(directory: str = '', recursive: bool = True, 
                   min_file_size: int = 0, max_file_size: int = 100 * 1024 * 1024,
                   hash_size: int = 8, threshold: float = 0.9,
                   processed_files: List[Dict[str, Any]] = None) -> List[List[Dict[str, Any]]]:
    """
    Find duplicate PDF files in a directory based on content similarity.
    
    Args:
        directory: Directory to search for PDFs (ignored if processed_files is provided)
        recursive: Whether to search recursively in subdirectories
        min_file_size: Minimum file size in bytes
        max_file_size: Maximum file size in bytes
        hash_size: Size of the perceptual hash
        threshold: Similarity threshold (0.0 to 1.0)
        processed_files: Optional list of pre-processed file info dictionaries
        
    Returns:
        List of duplicate file groups, where each group is a list of file info dictionaries
    """
    logger = logging.getLogger(__name__)
    
    try:
        # If we have pre-processed files, use them
        if processed_files is not None and processed_files:
            logger.info(f"Using {len(processed_files)} pre-processed files")
            file_infos = processed_files
        else:
            # Otherwise, find and process all PDF files in the directory
            file_infos = []
            pdf_files = []
            
            # Find all PDF files
            if recursive:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                if min_file_size <= file_size <= max_file_size:
                                    pdf_files.append((file_path, file_size))
                            except OSError as e:
                                logger.warning(f"Could not get size for {file_path}: {e}")
            else:
                for file in os.listdir(directory):
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(directory, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            if min_file_size <= file_size <= max_file_size:
                                pdf_files.append((file_path, file_size))
                        except OSError as e:
                            logger.warning(f"Could not get size for {file_path}: {e}")
            
            # Get file info for each PDF
            for file_path, file_size in pdf_files:
                try:
                    info = get_pdf_info(file_path)
                    if info:
                        file_infos.append(info)
                except Exception as e:
                    logger.warning(f"Could not get info for {file_path}: {e}")
        
        # Group by size first
        size_groups = {}
        for file_info in file_infos:
            size = file_info.get('size', 0)
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(file_info)
        
        # Only keep groups with more than one file
        potential_duplicates = [group for group in size_groups.values() if len(group) > 1]
        
        if not potential_duplicates:
            return []
        
        # For each group of same-size files, compare content hashes
        duplicate_groups = []
        temp_dir = tempfile.mkdtemp(prefix='pdf_finder_')
        
        try:
            # Calculate perceptual hashes for all files
            file_hashes = {}
            for file_info in file_infos:
                file_path = get_file_path(file_info, 'path')
                if not file_path:
                    continue
                    
                # Create a temporary image for the first page
                image_path = os.path.join(temp_dir, f"{os.path.basename(file_path)}.png")
                if extract_first_page_image(file_path, image_path):
                    try:
                        # Calculate perceptual hash
                        phash = calculate_image_hash(image_path, hash_size=hash_size)
                        file_hashes[file_path] = (phash, file_info)
                    except Exception as e:
                        logger.warning(f"Could not calculate hash for {file_path}: {e}")
            
            # Compare hashes to find duplicates
            processed = set()
            for file1, (hash1, file_info1) in file_hashes.items():
                if file1 in processed:
                    continue
                    
                duplicates = [file_info1]
                
                for file2, (hash2, file_info2) in file_hashes.items():
                    if file1 == file2 or file2 in processed:
                        continue
                        
                    # Compare hashes
                    similarity = compare_hashes(hash1, hash2)
                    if similarity >= threshold:
                        duplicates.append(file_info2)
                        processed.add(file2)
                
                if len(duplicates) > 1:
                    duplicate_groups.append(duplicates)
                
                processed.add(file1)
                
        finally:
            # Clean up temporary files
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Could not delete temporary directory {temp_dir}: {e}")
        
        return duplicate_groups
        
    except Exception as e:
        logger.error(f"Error finding duplicates: {e}", exc_info=True)
        raise

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
            file_path = get_file_path(file_info, 'path')
            size = file_info.get('size', 0)
            print(f"  - {file_path} ({size / 1024:.1f} KB)")
