#!/usr/bin/env python3
"""
Test script to reproduce the scanning crash issue.
"""

import sys
import os
import tempfile
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'script'))

from script.scanner import PDFScanner
from script.simple_translations import SimpleLanguageManager

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scan_crash():
    """Test scanning to reproduce the crash."""
    print("Testing scan crash reproduction...")
    
    # Create a temporary directory with some test files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory: {temp_dir}")
        
        # Create some test PDF files (empty files for testing)
        test_files = []
        for i in range(3):
            test_file = os.path.join(temp_dir, f"test_{i}.pdf")
            with open(test_file, 'w') as f:
                f.write("")  # Empty file
            test_files.append(test_file)
        
        print(f"Created {len(test_files)} test PDF files")
        
        try:
            # Create language manager
            language_manager = SimpleLanguageManager()
            
            # Create scanner with hash cache enabled
            print("Creating PDFScanner...")
            scanner = PDFScanner(
                threshold=0.95,
                dpi=150,
                enable_hash_cache=True,
                cache_dir="X:/GitHub/PDF_finder/.data",
                language_manager=language_manager
            )
            
            print(f"PDFScanner created successfully")
            print(f"Hash cache available: {scanner.hash_cache.is_available() if scanner.hash_cache else False}")
            
            # Test scanning the directory
            print(f"Starting scan of directory: {temp_dir}")
            
            # Set up scan parameters
            scanner.scan_parameters = {
                'directory': temp_dir,
                'recursive': True,
                'min_file_size': 0,
                'max_file_size': 1024*1024*1024,
                'min_similarity': 0.8,
                'enable_text_compare': True
            }
            
            # Try to run the scan
            print("Calling scan_directory...")
            scanner.scan_directory(
                directory=temp_dir,
                recursive=True,
                min_file_size=0,
                max_file_size=1024*1024*1024,
                min_similarity=0.8,
                enable_text_compare=True
            )
            
            print("Scan completed successfully")
            
        except Exception as e:
            print(f"❌ Error during scan: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("✅ Test completed successfully")
    return True

if __name__ == "__main__":
    test_scan_crash()
