#!/usr/bin/env python3
"""
Test script to verify that the hash_cache.py correctly saves and reads cache files 
in the .data/ directory at the project root.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the script directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'script'))

from utils.hash_cache import HashCache

def test_hash_cache_config():
    """Test that the hash_cache module correctly uses the .data/ directory."""
    
    print("Testing hash_cache configuration...")
    
    # Create a HashCache instance
    cache = HashCache()
    
    # Check the cache directory path
    print(f"Cache directory: {cache.cache_dir}")
    print(f"Cache directory absolute path: {cache.cache_dir.absolute()}")
    print(f"Cache directory exists: {cache.cache_dir.exists()}")
    
    # Expected cache directory should be at project root
    expected_cache_dir = Path(__file__).parent / '.data'
    print(f"Expected cache directory: {expected_cache_dir}")
    print(f"Expected cache directory absolute path: {expected_cache_dir.absolute()}")
    
    # Check if the paths match
    if cache.cache_dir.absolute() == expected_cache_dir.absolute():
        print("✓ HashCache correctly points to the project root .data/ directory")
    else:
        print("✗ HashCache does not point to the expected .data/ directory")
        return False
    
    # Check the database path
    print(f"Database path: {cache.db_path}")
    print(f"Database path absolute: {cache.db_path.absolute()}")
    
    expected_db_path = expected_cache_dir / 'pdf_cache.db'
    print(f"Expected database path: {expected_db_path}")
    print(f"Expected database path absolute: {expected_db_path.absolute()}")
    
    # Check if the database paths match
    if cache.db_path.absolute() == expected_db_path.absolute():
        print("✓ Database file correctly points to the project root .data/pdf_cache.db")
    else:
        print("✗ Database file does not point to the expected .data/pdf_cache.db")
        return False
    
    # Check if the database file was created
    if cache.db_path and cache.db_path.exists():
        print("✓ Database file was created successfully")
    else:
        print("✗ Database file was not created")
        return False
    
    # Test basic cache functionality
    print("\nTesting cache functionality...")
    
    # Create a test file for caching (we'll create a dummy file)
    test_file = "test_dummy.pdf"
    try:
        # Create a dummy PDF file for testing
        with open(test_file, 'w') as f:
            f.write("dummy content for testing")
        
        # Cache the test file
        entry = cache.cache_file(test_file)
        print("✓ Test entry cached successfully")
        
        # Check that the entry has the expected properties
        if entry.file_path == test_file and entry.file_hash:
            print("✓ Cache entry has correct properties")
        else:
            print("✗ Cache entry has incorrect properties")
            return False
        
        # Retrieve the cached entry
        retrieved_entry = cache.get_cached_entry(test_file)
        if retrieved_entry and retrieved_entry.file_path == test_file:
            print("✓ Test entry retrieved successfully")
        else:
            print("✗ Test entry retrieval failed")
            return False
            
    except Exception as e:
        print(f"✗ Error during cache functionality test: {e}")
        return False
    finally:
        # Clean up the test file
        try:
            if os.path.exists(test_file):
                os.remove(test_file)
        except:
            pass
    
    # Check if the database contains the entry
    if cache.db_path:
        try:
            conn = sqlite3.connect(cache.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pdf_cache WHERE file_path = ?", (test_file,))
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                print("✓ Test entry found in database")
            else:
                print("✗ Test entry not found in database")
                return False
        except Exception as e:
            print(f"✗ Error checking database: {e}")
            return False
    
    print("✓ All hash_cache configuration tests passed!")
    return True

if __name__ == "__main__":
    success = test_hash_cache_config()
    sys.exit(0 if success else 1)
