"""
PDF Hash Cache Module

This module provides a comprehensive caching system for PDF file hashes and text content
to speed up rescans and optimize memory usage for large PDF collections.
"""
import os
import json
import hashlib
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import threading
from contextlib import contextmanager

from .text_processor import TextProcessor, TextExtractionOptions

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached PDF file entry."""
    file_path: str
    file_hash: str
    file_size: int
    modified_time: float
    text_hash: str
    text_content: str
    page_count: int
    cache_time: float
    access_count: int
    last_access: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary."""
        return cls(**data)

class HashCache:
    """
    A comprehensive cache system for PDF file hashes and text content.
    
    Features:
    - Persistent storage using SQLite
    - File hash caching using SHA-256
    - Text content caching to avoid re-extraction
    - Automatic cache expiration and cleanup
    - Memory optimization with LRU eviction
    - Thread-safe operations
    """
    
    def __init__(self, 
                 cache_dir: Optional[str] = None,
                 max_cache_size: int = 10000,
                 cache_ttl_days: int = 30,
                 memory_cache_size: int = 1000):
        """
        Initialize the hash cache.
        
        Args:
            cache_dir: Directory to store cache database (defaults to ~/.pdf_finder_cache)
            max_cache_size: Maximum number of entries in persistent cache
            cache_ttl_days: Time-to-live for cache entries in days
            memory_cache_size: Maximum number of entries in memory cache
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / '.pdf_finder_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / 'pdf_cache.db'
        self.max_cache_size = max_cache_size
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.memory_cache_size = memory_cache_size
        
        # Memory cache for frequently accessed entries
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_cache_order: List[str] = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Text processor for content extraction
        self.text_processor = TextProcessor()
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Hash cache initialized with directory: {self.cache_dir}")
    
    def _init_database(self) -> None:
        """Initialize the SQLite database with required tables."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pdf_cache (
                    file_path TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    modified_time REAL NOT NULL,
                    text_hash TEXT NOT NULL,
                    text_content TEXT,
                    page_count INTEGER,
                    cache_time REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_access REAL NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_hash ON pdf_cache(file_hash)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_text_hash ON pdf_cache(text_hash)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_cache_time ON pdf_cache(cache_time)
            ''')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _calculate_text_hash(self, text: str) -> str:
        """Calculate hash of text content."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _is_file_changed(self, file_path: str, entry: Optional[CacheEntry]) -> bool:
        """Check if file has been modified since caching."""
        if not entry:
            return True
        
        try:
            stat = os.stat(file_path)
            return (stat.st_size != entry.file_size or 
                   stat.st_mtime != entry.modified_time)
        except OSError:
            return True
    
    def _update_memory_cache(self, entry: CacheEntry) -> None:
        """Update the memory cache with LRU eviction."""
        with self.lock:
            # Remove from existing position if present
            if entry.file_path in self.memory_cache_order:
                self.memory_cache_order.remove(entry.file_path)
            
            # Add to end (most recently used)
            self.memory_cache_order.append(entry.file_path)
            self.memory_cache[entry.file_path] = entry
            
            # Evict least recently used if over size limit
            while len(self.memory_cache_order) > self.memory_cache_size:
                lru_path = self.memory_cache_order.pop(0)
                del self.memory_cache[lru_path]
    
    def get_cached_entry(self, file_path: str) -> Optional[CacheEntry]:
        """
        Get cached entry for a file if it exists and is valid.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            CacheEntry if valid, None otherwise
        """
        # Check memory cache first
        with self.lock:
            if file_path in self.memory_cache:
                entry = self.memory_cache[file_path]
                if not self._is_file_changed(file_path, entry):
                    # Update access stats
                    entry.access_count += 1
                    entry.last_access = datetime.now().timestamp()
                    self._update_memory_cache(entry)
                    return entry
                else:
                    # File changed, remove from memory cache
                    del self.memory_cache[file_path]
                    self.memory_cache_order.remove(file_path)
        
        # Check persistent cache
        with self._get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM pdf_cache WHERE file_path = ?',
                (file_path,)
            ).fetchone()
            
            if row:
                entry = CacheEntry(
                    file_path=row['file_path'],
                    file_hash=row['file_hash'],
                    file_size=row['file_size'],
                    modified_time=row['modified_time'],
                    text_hash=row['text_hash'],
                    text_content=row['text_content'] or '',
                    page_count=row['page_count'] or 0,
                    cache_time=row['cache_time'],
                    access_count=row['access_count'] or 0,
                    last_access=row['last_access']
                )
                
                # Check if file has changed
                if self._is_file_changed(file_path, entry):
                    self.remove_entry(file_path)
                    return None
                
                # Check if cache entry is expired
                if datetime.now().timestamp() - entry.cache_time > self.cache_ttl.total_seconds():
                    self.remove_entry(file_path)
                    return None
                
                # Update access stats and move to memory cache
                entry.access_count += 1
                entry.last_access = datetime.now().timestamp()
                
                with self._get_connection() as conn_update:
                    conn_update.execute(
                        '''UPDATE pdf_cache 
                           SET access_count = ?, last_access = ? 
                           WHERE file_path = ?''',
                        (entry.access_count, entry.last_access, file_path)
                    )
                    conn_update.commit()
                
                self._update_memory_cache(entry)
                return entry
        
        return None
    
    def cache_file(self, file_path: str, force_reprocess: bool = False) -> CacheEntry:
        """
        Cache a PDF file's hash and text content.
        
        Args:
            file_path: Path to the PDF file
            force_reprocess: Force reprocessing even if cached
            
        Returns:
            CacheEntry with file information
        """
        # Check if we have a valid cached entry
        if not force_reprocess:
            cached_entry = self.get_cached_entry(file_path)
            if cached_entry:
                logger.debug(f"Using cached entry for {file_path}")
                return cached_entry
        
        logger.debug(f"Processing and caching {file_path}")
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)
        if not file_hash:
            raise ValueError(f"Could not calculate file hash for {file_path}")
        
        # Get file stats
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            modified_time = stat.st_mtime
        except OSError as e:
            raise ValueError(f"Could not access file {file_path}: {e}")
        
        # Extract text content
        try:
            text_content = self.text_processor.extract_text(file_path)
            text_hash = self._calculate_text_hash(text_content)
            
            # Get page count
            import fitz
            with fitz.open(file_path) as doc:
                page_count = len(doc)
                
        except Exception as e:
            logger.error(f"Error processing PDF content for {file_path}: {e}")
            text_content = ""
            text_hash = ""
            page_count = 0
        
        # Create cache entry
        current_time = datetime.now().timestamp()
        entry = CacheEntry(
            file_path=file_path,
            file_hash=file_hash,
            file_size=file_size,
            modified_time=modified_time,
            text_hash=text_hash,
            text_content=text_content,
            page_count=page_count,
            cache_time=current_time,
            access_count=1,
            last_access=current_time
        )
        
        # Store in persistent cache
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO pdf_cache 
                (file_path, file_hash, file_size, modified_time, text_hash, 
                 text_content, page_count, cache_time, access_count, last_access)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.file_path, entry.file_hash, entry.file_size, entry.modified_time,
                entry.text_hash, entry.text_content, entry.page_count, entry.cache_time,
                entry.access_count, entry.last_access
            ))
            conn.commit()
        
        # Update memory cache
        self._update_memory_cache(entry)
        
        # Perform cache cleanup if needed
        self._cleanup_cache()
        
        logger.debug(f"Cached entry for {file_path}")
        return entry
    
    def remove_entry(self, file_path: str) -> bool:
        """
        Remove a cache entry.
        
        Args:
            file_path: Path to the file to remove from cache
            
        Returns:
            True if entry was removed, False if not found
        """
        removed = False
        
        # Remove from memory cache
        with self.lock:
            if file_path in self.memory_cache:
                del self.memory_cache[file_path]
                if file_path in self.memory_cache_order:
                    self.memory_cache_order.remove(file_path)
                removed = True
        
        # Remove from persistent cache
        with self._get_connection() as conn:
            cursor = conn.execute(
                'DELETE FROM pdf_cache WHERE file_path = ?',
                (file_path,)
            )
            conn.commit()
            if cursor.rowcount > 0:
                removed = True
        
        return removed
    
    def _cleanup_cache(self) -> None:
        """Clean up expired and excess cache entries."""
        with self._get_connection() as conn:
            # Remove expired entries
            cutoff_time = datetime.now().timestamp() - self.cache_ttl.total_seconds()
            conn.execute(
                'DELETE FROM pdf_cache WHERE cache_time < ?',
                (cutoff_time,)
            )
            
            # Remove excess entries if over size limit
            result = conn.execute('SELECT COUNT(*) FROM pdf_cache').fetchone()
            total_count = result[0]
            
            if total_count > self.max_cache_size:
                # Remove least recently used entries
                excess = total_count - self.max_cache_size
                conn.execute('''
                    DELETE FROM pdf_cache 
                    WHERE file_path IN (
                        SELECT file_path FROM pdf_cache 
                        ORDER BY last_access ASC 
                        LIMIT ?
                    )
                ''', (excess,))
            
            conn.commit()
        
        logger.debug("Cache cleanup completed")
    
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.memory_cache.clear()
            self.memory_cache_order.clear()
        
        with self._get_connection() as conn:
            conn.execute('DELETE FROM pdf_cache')
            conn.commit()
        
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._get_connection() as conn:
            result = conn.execute('SELECT COUNT(*) FROM pdf_cache').fetchone()
            persistent_count = result[0]
            
            result = conn.execute('SELECT COUNT(*) FROM pdf_cache WHERE cache_time >= ?', 
                                (datetime.now().timestamp() - self.cache_ttl.total_seconds(),)).fetchone()
            valid_count = result[0]
            
            result = conn.execute('SELECT SUM(access_count) FROM pdf_cache').fetchone()
            total_accesses = result[0] or 0
            
            # Get cache size on disk
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        with self.lock:
            memory_count = len(self.memory_cache)
        
        return {
            'persistent_entries': persistent_count,
            'valid_entries': valid_count,
            'memory_entries': memory_count,
            'total_accesses': total_accesses,
            'cache_size_bytes': db_size,
            'cache_dir': str(self.cache_dir),
            'max_cache_size': self.max_cache_size,
            'cache_ttl_days': self.cache_ttl.days
        }
    
    def find_duplicates_by_hash(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Find duplicate files by their hash values.
        
        Args:
            file_paths: List of file paths to check
            
        Returns:
            Dictionary mapping hash to list of file paths with that hash
        """
        hash_groups = {}
        
        for file_path in file_paths:
            try:
                entry = self.cache_file(file_path)
                if entry.file_hash:
                    if entry.file_hash not in hash_groups:
                        hash_groups[entry.file_hash] = []
                    hash_groups[entry.file_hash].append(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
        
        # Filter out groups with only one file
        return {hash_val: files for hash_val, files in hash_groups.items() if len(files) > 1}
    
    def find_duplicates_by_content(self, file_paths: List[str], 
                                 similarity_threshold: float = 0.9) -> Dict[str, List[str]]:
        """
        Find duplicate files by text content similarity.
        
        Args:
            file_paths: List of file paths to check
            similarity_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            Dictionary mapping representative file to list of similar files
        """
        content_groups = {}
        processed = set()
        
        for i, file_path in enumerate(file_paths):
            if file_path in processed:
                continue
                
            try:
                entry = self.cache_file(file_path)
                if not entry.text_hash:
                    continue
                
                group = [file_path]
                
                for other_path in file_paths[i+1:]:
                    if other_path in processed:
                        continue
                        
                    try:
                        other_entry = self.cache_file(other_path)
                        if not other_entry.text_hash:
                            continue
                        
                        # Compare text content
                        similarity = self.text_processor.compare_texts(
                            entry.text_content, 
                            other_entry.text_content
                        )
                        
                        if similarity >= similarity_threshold:
                            group.append(other_path)
                            processed.add(other_path)
                            
                    except Exception as e:
                        logger.error(f"Error comparing {file_path} with {other_path}: {e}")
                        continue
                
                if len(group) > 1:
                    # Use first file as representative
                    content_groups[file_path] = group
                    processed.add(file_path)
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
        
        return content_groups
