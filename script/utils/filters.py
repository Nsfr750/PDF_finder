"""File filtering system for PDF comparison."""
import os
import re
from datetime import datetime
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union

@dataclass
class FileFilter:
    """Represents a file filter with various conditions."""
    min_size: Optional[int] = None  # in bytes
    max_size: Optional[int] = None
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    name_pattern: Optional[str] = None
    
    def matches(self, filepath: str) -> bool:
        """Check if file matches all filter conditions."""
        try:
            stat = os.stat(filepath)
            
            if self.min_size is not None and stat.st_size < self.min_size:
                return False
                
            if self.max_size is not None and stat.st_size > self.max_size:
                return False
                
            mtime = datetime.fromtimestamp(stat.st_mtime)
            
            if self.modified_after is not None and mtime < self.modified_after:
                return False
                
            if self.modified_before is not None and mtime > self.modified_before:
                return False
                
            if self.name_pattern is not None:
                filename = os.path.basename(filepath)
                if not re.search(self.name_pattern, filename, re.IGNORECASE):
                    return False
                    
            return True
            
        except (OSError, re.error):
            return False

class FilterBuilder:
    """Builder for creating file filters."""
    
    def __init__(self):
        self._filters: List[FileFilter] = []
    
    def with_size(self, min_size: Optional[int] = None, max_size: Optional[int] = None) -> 'FilterBuilder':
        """Add size-based filtering."""
        self._filters.append(FileFilter(min_size=min_size, max_size=max_size))
        return self
    
    def with_modified_date(self, 
                         after: Optional[datetime] = None, 
                         before: Optional[datetime] = None) -> 'FilterBuilder':
        """Add modification date filtering."""
        self._filters.append(FileFilter(modified_after=after, modified_before=before))
        return self
    
    def with_name_pattern(self, pattern: str) -> 'FilterBuilder':
        """Add filename pattern filtering using regex."""
        self._filters.append(FileFilter(name_pattern=pattern))
        return self
    
    def build(self) -> Callable[[str], bool]:
        """Build the filter function."""
        def filter_func(filepath: str) -> bool:
            return all(f.matches(filepath) for f in self._filters)
        return filter_func
