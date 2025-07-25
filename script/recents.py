import os
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from PyQt6.QtCore import QSettings, QObject, pyqtSignal as Signal

logger = logging.getLogger('PDFDuplicateFinder')

class RecentFilesManager(QObject):
    """Manages a list of recently used files with persistence."""
    
    # Signal emitted when recent files list changes
    recents_changed = Signal(list)
    
    def __init__(self, max_files: int = 10, parent: Optional[QObject] = None, language_manager=None):
        """Initialize the recent files manager.
        
        Args:
            max_files: Maximum number of recent files to store
            parent: Parent QObject
            language_manager: Optional language manager for translations
        """
        super().__init__(parent)
        self.max_files = max(1, max_files)
        self._files: List[Dict[str, Any]] = []
        self._settings = QSettings("PDFDuplicateFinder", "RecentFiles")
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
        self._load()
    
    def add_file(self, file_path: str, metadata: Optional[dict] = None):
        """Add a file or directory to the recent files list.
        
        Args:
            file_path: Path to the file or directory to add
            metadata: Optional metadata to store with the path
        """
        if not file_path or not (os.path.exists(file_path) and (os.path.isfile(file_path) or os.path.isdir(file_path))):
            logger.warning(
                self.tr(
                    "recents.cannot_add_nonexistent_path", 
                    "Cannot add non-existent path to recents: {path}"
                ).format(path=file_path)
            )
            return
        
        # Remove any existing entry for this file
        self._files = [f for f in self._files if f['path'].lower() != file_path.lower()]
        
        # Add the new entry
        entry = {
            'path': file_path,
            'last_accessed': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self._files.insert(0, entry)
        
        # Trim the list if needed
        if len(self._files) > self.max_files:
            self._files = self._files[:self.max_files]
        
        # Save and notify
        self._save()
        self.recents_changed.emit(self._files)
    
    def remove_file(self, file_path: str):
        """Remove a file from the recent files list.
        
        Args:
            file_path: Path to the file to remove
        """
        initial_count = len(self._files)
        self._files = [f for f in self._files if f['path'].lower() != file_path.lower()]
        
        if len(self._files) != initial_count:
            self._save()
            self.recents_changed.emit(self._files)
    
    def clear(self):
        """Clear all recent files."""
        if self._files:
            self._files = []
            self._save()
            self.recents_changed.emit(self._files)
    
    def get_recent_files(self) -> List[Dict[str, Any]]:
        """Get the list of recent files.
        
        Returns:
            List of recent file entries, each containing 'path', 'last_accessed', and 'metadata'
        """
        return self._files.copy()
    
    def update_metadata(self, file_path: str, metadata: dict):
        """Update metadata for a file in the recent files list.
        
        Args:
            file_path: Path to the file to update
            metadata: Dictionary of metadata to update (shallow merge with existing)
        """
        updated = False
        
        for entry in self._files:
            if entry['path'].lower() == file_path.lower():
                entry['metadata'].update(metadata)
                entry['last_accessed'] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            self._save()
            self.recents_changed.emit(self._files)
    
    def _load(self):
        """Load recent files from settings."""
        try:
            recents_data = self._settings.value("recentFiles")
            if recents_data:
                self._files = json.loads(recents_data)
                
                # Ensure all files still exist
                self._files = [f for f in self._files if os.path.isfile(f['path'])]
                
                # Sort by last accessed (newest first)
                self._files.sort(key=lambda x: x.get('last_accessed', ''), reverse=True)
                
                # Trim to max files
                if len(self._files) > self.max_files:
                    self._files = self._files[:self.max_files]
                    
        except Exception as e:
            logger.error(
                self.tr(
                    "recents.error_loading", 
                    "Error loading recent files: {error}"
                ).format(error=str(e))
            )
            self._files = []
    
    def _save(self):
        """Save recent files to settings."""
        try:
            self._settings.setValue("recentFiles", json.dumps(self._files))
            self._settings.sync()
        except Exception as e:
            logger.error(
                self.tr(
                    "recents.error_saving", 
                    "Error saving recent files: {error}"
                ).format(error=str(e))
            )
    
    def __len__(self) -> int:
        """Get the number of recent files."""
        return len(self._files)
    
    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Get a recent file by index."""
        return self._files[index]
    
    def __iter__(self):
        """Iterate over recent files."""
        return iter(self._files)
