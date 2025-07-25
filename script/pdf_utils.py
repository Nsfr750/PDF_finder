import os
import hashlib
import tempfile
import fitz  # PyMuPDF
import wand.image
import wand.color
import numpy as np
import imagehash
from typing import List, Dict, Any, Tuple, Optional, Union
import logging
from pathlib import Path

# Import utility functions
from .utils import get_file_path, get_file_info_dict

logger = logging.getLogger('PDFUtils')

def get_pdf_info(file_path: str, language_manager=None) -> Dict[str, Any]:
    """
    Get information about a PDF file.
    
    Args:
        file_path: Path to the PDF file
        language_manager: Optional language manager for translations
        
    Returns:
        Dictionary containing file information
    """
    tr = language_manager.tr if language_manager else lambda key, default: default
    
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
                
                if doc.metadata:
                    info.update({
                        'title': doc.metadata.get('title', ''),
                        'author': doc.metadata.get('author', ''),
                        'subject': doc.metadata.get('subject', ''),
                        'keywords': doc.metadata.get('keywords', ''),
                        'creator': doc.metadata.get('creator', ''),
                        'producer': doc.metadata.get('producer', '')
                    })
                    
        except Exception as e:
            logger.warning(tr('pdf_utils.error.extract_metadata', 
                           'Could not extract metadata from {file}: {error}').format(
                               file=file_path, error=str(e)))
            
        return info
        
    except Exception as e:
        logger.error(tr('pdf_utils.error.file_info', 
                       'Error getting info for {file}: {error}').format(
                           file=file_path, error=str(e)))
        return {}

def calculate_file_hash(file_path: str, block_size: int = 65536, language_manager=None) -> str:
    """
    Calculate the MD5 hash of a file.
    
    Args:
        file_path: Path to the file
        block_size: Size of blocks to read at a time
        language_manager: Optional language manager for translations
        
    Returns:
        MD5 hash of the file
    """
    tr = language_manager.tr if language_manager else lambda key, default: default
    
    try:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(block_size)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(tr('pdf_utils.error.hash_calculation', 
                       'Error calculating hash for {file}: {error}').format(
                           file=file_path, error=str(e)))
        return ''

def calculate_image_hash(image_path: str, hash_size: int = 8, language_manager=None) -> str:
    """
    Calculate the perceptual hash of an image using Wand.
    
    Args:
        image_path: Path to the image file
        hash_size: Size of the hash (higher = more accurate but slower)
        language_manager: Optional language manager for translations
        
    Returns:
        Perceptual hash of the image
    """
    tr = language_manager.tr if language_manager else lambda key, default: default
    
    try:
        with wand.image.Image(filename=image_path) as img:
            # Convert to grayscale and resize for hashing
            img.transform(resize=f"{hash_size}x{hash_size}!")
            img.type = 'grayscale'
            
            # Get pixel data as numpy array
            pixels = np.array(img)
            
            # Calculate average pixel value
            avg = pixels.mean()
            
            # Create hash by comparing each pixel to the average
            diff = pixels > avg
            
            # Convert boolean array to hash string
            return ''.join(['1' if p else '0' for p in diff.flatten()])
            
    except Exception as e:
        logger.error(tr('pdf_utils.error.image_hash', 
                       'Error calculating image hash for {file}: {error}').format(
                           file=image_path, error=str(e)))
        return ''

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

def extract_first_page_image(pdf_path: str, output_path: str, dpi: int = 100, language_manager=None) -> bool:
    """
    Extract the first page of a PDF as an image using Wand.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the output image
        dpi: DPI for the output image
        language_manager: Optional language manager for translations
        
    Returns:
        True if successful, False otherwise
    """
    tr = language_manager.tr if language_manager else lambda key, default: default
    
    try:
        # Use Wand to convert first page to image
        with wand.image.Image(filename=f"{pdf_path}[0]", resolution=dpi) as img:
            # Convert to RGB and save as PNG
            img.format = 'png'
            img.save(filename=output_path)
        return True
        
    except Exception as e:
        logger.error(tr('pdf_utils.error.extract_image', 
                       'Error extracting image from {file}: {error}').format(
                           file=pdf_path, error=str(e)))
        return False

def find_duplicates(directory: str = '', recursive: bool = True, 
                   min_file_size: int = 0, max_file_size: int = 100 * 1024 * 1024,
                   hash_size: int = 8, threshold: float = 0.9,
                   processed_files: List[Dict[str, Any]] = None,
                   language_manager = None) -> List[List[Dict[str, Any]]]:
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
        language_manager: Optional language manager for translations
        
    Returns:
        List of duplicate file groups, where each group is a list of file info dictionaries
    """
    tr = language_manager.tr if language_manager else lambda key, default: default
    logger = logging.getLogger(__name__)
    
    try:
        # If we have pre-processed files, use them
        if processed_files is not None and processed_files:
            logger.info(tr("pdf_utils.using_preprocessed_files", 
                          "Using {count} pre-processed files").format(
                              count=len(processed_files)))
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
                            except (OSError, Exception) as e:
                                logger.warning(tr("pdf_utils.file_access_warning",
                                                "Could not access file {file}: {error}").format(
                                                    file=file_path, error=str(e)))
            else:
                # Non-recursive search
                try:
                    for file in os.listdir(directory):
                        if file.lower().endswith('.pdf'):
                            file_path = os.path.join(directory, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                if min_file_size <= file_size <= max_file_size:
                                    pdf_files.append((file_path, file_size))
                            except (OSError, Exception) as e:
                                logger.warning(tr("pdf_utils.file_access_warning",
                                                "Could not access file {file}: {error}").format(
                                                    file=file_path, error=str(e)))
                except (OSError, Exception) as e:
                    logger.error(tr("pdf_utils.directory_access_error",
                                  "Error accessing directory {dir}: {error}").format(
                                      dir=directory, error=str(e)))
                    return []
            
            logger.info(tr("pdf_utils.found_pdf_files", 
                          "Found {count} PDF files to process").format(
                              count=len(pdf_files)))
            
            # Process each PDF file
            for i, (file_path, file_size) in enumerate(pdf_files):
                try:
                    # Get file info
                    file_info = get_file_info_dict(file_path)
                    if not file_info:
                        continue
                    
                    # Add size and modification time
                    file_info['size'] = file_size
                    file_info['modified'] = os.path.getmtime(file_path)
                    
                    # Create a temporary file for the first page image
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    try:
                        # Extract first page as image
                        if extract_first_page_image(file_path, temp_path, language_manager=language_manager):
                            # Calculate perceptual hash of the first page
                            image_hash = calculate_image_hash(
                                temp_path, 
                                hash_size=hash_size,
                                language_manager=language_manager
                            )
                            if image_hash:
                                file_info['image_hash'] = image_hash
                    finally:
                        # Clean up the temporary file
                        try:
                            os.unlink(temp_path)
                        except (OSError, Exception) as e:
                            logger.warning(tr("pdf_utils.temp_file_cleanup_warning",
                                            "Could not delete temporary file {file}: {error}").format(
                                                file=temp_path, error=str(e)))
                    
                    file_infos.append(file_info)
                    
                    # Log progress every 10 files
                    if (i + 1) % 10 == 0:
                        logger.info(tr("pdf_utils.processing_progress",
                                     "Processed {current}/{total} files").format(
                                         current=i+1, total=len(pdf_files)))
                except Exception as e:
                    logger.error(tr("pdf_utils.file_processing_error",
                                  "Error processing file {file}: {error}").format(
                                      file=file_path, error=str(e)))
        
        # Group files by size and hash
        size_groups = {}
        for file_info in file_infos:
            size = file_info.get('size', 0)
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(file_info)
        
        # Find potential duplicates (files with the same size)
        potential_duplicates = [group for group in size_groups.values() if len(group) > 1]
        
        logger.info(tr("pdf_utils.potential_duplicates_found",
                      "Found {count} potential duplicate groups based on size").format(
                          count=len(potential_duplicates)))
        
        # Compare files in each potential duplicate group
        duplicate_groups = []
        for group in potential_duplicates:
            # If there are only 2 files, compare them directly
            if len(group) == 2:
                file1 = group[0]
                file2 = group[1]
                
                # If both have image hashes, compare them
                if 'image_hash' in file1 and 'image_hash' in file2:
                    similarity = compare_hashes(file1['image_hash'], file2['image_hash'])
                    if similarity >= threshold:
                        duplicate_groups.append([file1, file2])
            else:
                # For groups with more than 2 files, compare each pair
                current_group = []
                for i in range(len(group)):
                    file1 = group[i]
                    if 'image_hash' not in file1:
                        continue
                        
                    for j in range(i + 1, len(group)):
                        file2 = group[j]
                        if 'image_hash' not in file2:
                            continue
                            
                        similarity = compare_hashes(file1['image_hash'], file2['image_hash'])
                        if similarity >= threshold:
                            # Add both files to the current group if not already there
                            if file1 not in current_group:
                                current_group.append(file1)
                            if file2 not in current_group:
                                current_group.append(file2)
                
                if current_group:
                    duplicate_groups.append(current_group)
        
        logger.info(tr("pdf_utils.duplicate_groups_found",
                      "Found {count} duplicate groups").format(
                          count=len(duplicate_groups)))
        
        return duplicate_groups
    
    except Exception as e:
        logger.error(tr("pdf_utils.duplicate_finding_error",
                       "Error finding duplicates: {error}").format(error=str(e)))
        return []

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.getcwd()
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print(f"Searching for duplicate PDFs in: {directory}")
    duplicates = find_duplicates(directory)
    
    if duplicates:
        print(f"\nFound {len(duplicates)} groups of duplicate files:")
        for i, group in enumerate(duplicates, 1):
            print(f"\nGroup {i}:")
            for file_info in group:
                print(f"  {file_info['path']} ({file_info.get('size', 0) / 1024:.1f} KB)")
    else:
        print("No duplicate PDFs found.")
