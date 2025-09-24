"""
Test script for PDF Hash Cache functionality

This script provides comprehensive testing of the hash cache system including:
- Basic cache operations
- Performance testing with large PDF collections
- Cache persistence across restarts
- Cache invalidation when files are modified
- Memory usage optimization
"""

import os
import sys
import tempfile
import shutil
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from script.hash_cache import HashCache, CacheEntry
from script.text_processor import TextProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestHashCache(unittest.TestCase):
    """Test cases for HashCache functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, 'cache')
        self.test_dir = os.path.join(self.temp_dir, 'test_pdfs')
        
        # Create test directories
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Initialize hash cache
        self.hash_cache = HashCache(
            cache_dir=self.cache_dir,
            max_cache_size=1000,
            cache_ttl_days=1,
            memory_cache_size=100
        )
        
        # Create sample PDF files for testing
        self.sample_pdfs = self._create_sample_pdfs()
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_sample_pdfs(self) -> List[str]:
        """Create sample PDF files for testing."""
        pdf_files = []
        
        # Create simple PDF-like files (for testing purposes)
        # In a real scenario, you would use actual PDF files
        sample_contents = [
            b"Sample PDF content 1 - This is a test PDF file",
            b"Sample PDF content 2 - This is another test PDF file",
            b"Sample PDF content 3 - This is a third test PDF file",
            b"Sample PDF content 1 - This is a test PDF file",  # Duplicate of first
            b"Sample PDF content 4 - This is a fourth test PDF file"
        ]
        
        for i, content in enumerate(sample_contents):
            file_path = os.path.join(self.test_dir, f'test_{i+1}.pdf')
            with open(file_path, 'wb') as f:
                f.write(content)
            pdf_files.append(file_path)
        
        return pdf_files
    
    def test_cache_initialization(self):
        """Test hash cache initialization."""
        self.assertTrue(os.path.exists(self.cache_dir))
        self.assertTrue(os.path.exists(os.path.join(self.cache_dir, 'pdf_cache.db')))
        
        # Test cache stats
        stats = self.hash_cache.get_cache_stats()
        self.assertIn('persistent_entries', stats)
        self.assertIn('memory_entries', stats)
        self.assertIn('cache_dir', stats)
        self.assertEqual(stats['cache_dir'], self.cache_dir)
    
    def test_file_caching(self):
        """Test basic file caching functionality."""
        # Cache a file
        file_path = self.sample_pdfs[0]
        entry = self.hash_cache.cache_file(file_path)
        
        # Verify entry structure
        self.assertIsInstance(entry, CacheEntry)
        self.assertEqual(entry.file_path, file_path)
        self.assertTrue(entry.file_hash)
        self.assertTrue(entry.text_hash)
        self.assertGreater(entry.file_size, 0)
        self.assertGreater(entry.modified_time, 0)
        self.assertEqual(entry.access_count, 1)
        
        # Test retrieving cached entry
        cached_entry = self.hash_cache.get_cached_entry(file_path)
        self.assertIsNotNone(cached_entry)
        self.assertEqual(cached_entry.file_path, file_path)
        self.assertEqual(cached_entry.file_hash, entry.file_hash)
    
    def test_cache_persistence(self):
        """Test cache persistence across restarts."""
        # Cache some files
        for file_path in self.sample_pdfs[:3]:
            self.hash_cache.cache_file(file_path)
        
        # Get cache stats before restart
        stats_before = self.hash_cache.get_cache_stats()
        entries_before = stats_before['persistent_entries']
        
        # Create new cache instance (simulating restart)
        new_cache = HashCache(cache_dir=self.cache_dir)
        
        # Get cache stats after restart
        stats_after = new_cache.get_cache_stats()
        entries_after = stats_after['persistent_entries']
        
        # Verify persistence
        self.assertEqual(entries_before, entries_after)
        
        # Verify cached entries are still accessible
        for file_path in self.sample_pdfs[:3]:
            entry = new_cache.get_cached_entry(file_path)
            self.assertIsNotNone(entry)
            self.assertEqual(entry.file_path, file_path)
    
    def test_duplicate_detection_by_hash(self):
        """Test duplicate detection using file hashes."""
        # Find duplicates by hash
        duplicates = self.hash_cache.find_duplicates_by_hash(self.sample_pdfs)
        
        # Should find one duplicate group (files 1 and 4 have same content)
        self.assertEqual(len(duplicates), 1)
        
        # Verify the duplicate group contains the expected files
        duplicate_group = list(duplicates.values())[0]
        self.assertEqual(len(duplicate_group), 2)
        
        # Verify the files are actually duplicates
        file1, file2 = duplicate_group
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            content1 = f1.read()
            content2 = f2.read()
            self.assertEqual(content1, content2)
    
    def test_duplicate_detection_by_content(self):
        """Test duplicate detection using content similarity."""
        # Find duplicates by content
        duplicates = self.hash_cache.find_duplicates_by_content(
            self.sample_pdfs, 
            similarity_threshold=0.9
        )
        
        # Should find one duplicate group (files 1 and 4 have same content)
        self.assertEqual(len(duplicates), 1)
        
        # Verify the duplicate group contains the expected files
        duplicate_group = list(duplicates.values())[0]
        self.assertEqual(len(duplicate_group), 2)
    
    def test_cache_invalidation(self):
        """Test cache invalidation when files are modified."""
        file_path = self.sample_pdfs[0]
        
        # Cache the file
        entry1 = self.hash_cache.cache_file(file_path)
        original_hash = entry1.file_hash
        
        # Modify the file
        time.sleep(0.1)  # Ensure different timestamp
        with open(file_path, 'a') as f:
            f.write(b" - modified")
        
        # Try to get cached entry (should be invalidated)
        cached_entry = self.hash_cache.get_cached_entry(file_path)
        self.assertIsNone(cached_entry)
        
        # Cache the modified file
        entry2 = self.hash_cache.cache_file(file_path)
        modified_hash = entry2.file_hash
        
        # Verify hash changed
        self.assertNotEqual(original_hash, modified_hash)
    
    def test_cache_cleanup(self):
        """Test cache cleanup functionality."""
        # Cache many files to exceed size limit
        for i in range(1500):  # Exceeds max_cache_size of 1000
            file_path = os.path.join(self.test_dir, f'extra_{i}.pdf')
            with open(file_path, 'w') as f:
                f.write(f"Extra content {i}")
            self.hash_cache.cache_file(file_path)
        
        # Check that cache was cleaned up
        stats = self.hash_cache.get_cache_stats()
        self.assertLessEqual(stats['persistent_entries'], self.hash_cache.max_cache_size)
    
    def test_memory_cache_lru(self):
        """Test memory cache LRU eviction."""
        # Cache files to exceed memory cache size
        for i in range(150):  # Exceeds memory_cache_size of 100
            file_path = os.path.join(self.test_dir, f'memory_test_{i}.pdf')
            with open(file_path, 'w') as f:
                f.write(f"Memory test content {i}")
            self.hash_cache.cache_file(file_path)
        
        # Check memory cache size
        stats = self.hash_cache.get_cache_stats()
        self.assertLessEqual(stats['memory_entries'], self.hash_cache.memory_cache_size)
    
    def test_cache_clear(self):
        """Test cache clear functionality."""
        # Cache some files
        for file_path in self.sample_pdfs:
            self.hash_cache.cache_file(file_path)
        
        # Verify cache has entries
        stats_before = self.hash_cache.get_cache_stats()
        self.assertGreater(stats_before['persistent_entries'], 0)
        
        # Clear cache
        self.hash_cache.clear_cache()
        
        # Verify cache is empty
        stats_after = self.hash_cache.get_cache_stats()
        self.assertEqual(stats_after['persistent_entries'], 0)
        self.assertEqual(stats_after['memory_entries'], 0)
    
    def test_performance_comparison(self):
        """Test performance comparison between cached and non-cached operations."""
        import time
        
        # Test without cache (first run)
        start_time = time.time()
        for file_path in self.sample_pdfs:
            self.hash_cache.cache_file(file_path, force_reprocess=True)
        first_run_time = time.time() - start_time
        
        # Test with cache (second run)
        start_time = time.time()
        for file_path in self.sample_pdfs:
            entry = self.hash_cache.get_cached_entry(file_path)
            self.assertIsNotNone(entry)
        second_run_time = time.time() - start_time
        
        # Verify cached run is faster
        logger.info(f"First run (no cache): {first_run_time:.3f}s")
        logger.info(f"Second run (cached): {second_run_time:.3f}s")
        logger.info(f"Speed improvement: {first_run_time/second_run_time:.2f}x")
        
        # Cached run should be significantly faster
        self.assertLess(second_run_time, first_run_time)
    
    def test_error_handling(self):
        """Test error handling for various scenarios."""
        # Test with non-existent file
        non_existent_file = os.path.join(self.test_dir, 'non_existent.pdf')
        with self.assertRaises(ValueError):
            self.hash_cache.cache_file(non_existent_file)
        
        # Test with invalid file path
        with self.assertRaises(ValueError):
            self.hash_cache.cache_file('')
        
        # Test get_cached_entry with non-existent file
        entry = self.hash_cache.get_cached_entry(non_existent_file)
        self.assertIsNone(entry)
    
    def test_cache_entry_serialization(self):
        """Test CacheEntry serialization and deserialization."""
        file_path = self.sample_pdfs[0]
        entry = self.hash_cache.cache_file(file_path)
        
        # Convert to dictionary
        entry_dict = entry.to_dict()
        
        # Convert back from dictionary
        restored_entry = CacheEntry.from_dict(entry_dict)
        
        # Verify all fields are preserved
        self.assertEqual(entry.file_path, restored_entry.file_path)
        self.assertEqual(entry.file_hash, restored_entry.file_hash)
        self.assertEqual(entry.file_size, restored_entry.file_size)
        self.assertEqual(entry.modified_time, restored_entry.modified_time)
        self.assertEqual(entry.text_hash, restored_entry.text_hash)
        self.assertEqual(entry.text_content, restored_entry.text_content)
        self.assertEqual(entry.page_count, restored_entry.page_count)
        self.assertEqual(entry.cache_time, restored_entry.cache_time)
        self.assertEqual(entry.access_count, restored_entry.access_count)
        self.assertEqual(entry.last_access, restored_entry.last_access)

def run_performance_test():
    """Run performance test with large number of files."""
    print("\n" + "="*50)
    print("PERFORMANCE TEST")
    print("="*50)
    
    # Create temporary directory for performance test
    temp_dir = tempfile.mkdtemp()
    test_dir = os.path.join(temp_dir, 'perf_test')
    cache_dir = os.path.join(temp_dir, 'cache')
    
    try:
        os.makedirs(test_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create many test files
        num_files = 100
        file_paths = []
        
        print(f"Creating {num_files} test files...")
        for i in range(num_files):
            file_path = os.path.join(test_dir, f'perf_test_{i}.pdf')
            with open(file_path, 'w') as f:
                # Create files with varying content
                content = f"Performance test file {i}\n"
                content += "This is a test file for performance testing.\n" * (10 + (i % 5))
                f.write(content)
            file_paths.append(file_path)
        
        # Initialize cache
        cache = HashCache(cache_dir=cache_dir, max_cache_size=10000)
        
        # Test first run (no cache)
        print("Running first scan (no cache)...")
        start_time = time.time()
        
        for file_path in file_paths:
            cache.cache_file(file_path, force_reprocess=True)
        
        first_run_time = time.time() - start_time
        print(f"First run completed in {first_run_time:.3f}s")
        
        # Test second run (with cache)
        print("Running second scan (with cache)...")
        start_time = time.time()
        
        for file_path in file_paths:
            entry = cache.get_cached_entry(file_path)
            assert entry is not None
        
        second_run_time = time.time() - start_time
        print(f"Second run completed in {second_run_time:.3f}s")
        
        # Test duplicate detection
        print("Testing duplicate detection...")
        start_time = time.time()
        
        duplicates = cache.find_duplicates_by_hash(file_paths)
        
        duplicate_time = time.time() - start_time
        print(f"Duplicate detection completed in {duplicate_time:.3f}s")
        print(f"Found {len(duplicates)} duplicate groups")
        
        # Performance summary
        print("\nPerformance Summary:")
        print(f"  First run: {first_run_time:.3f}s")
        print(f"  Second run: {second_run_time:.3f}s")
        print(f"  Speed improvement: {first_run_time/second_run_time:.2f}x")
        print(f"  Duplicate detection: {duplicate_time:.3f}s")
        
        # Cache statistics
        stats = cache.get_cache_stats()
        print(f"\nCache Statistics:")
        print(f"  Persistent entries: {stats['persistent_entries']}")
        print(f"  Memory entries: {stats['memory_entries']}")
        print(f"  Cache size: {stats['cache_size_bytes']} bytes")
        
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    """Main test runner."""
    print("PDF Hash Cache Test Suite")
    print("="*50)
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance test
    run_performance_test()
    
    print("\n" + "="*50)
    print("All tests completed!")

if __name__ == '__main__':
    main()
