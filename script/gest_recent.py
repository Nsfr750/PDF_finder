"""
Recent folders management for PDF Duplicate Finder.
"""
import os
from pathlib import Path
from typing import List, Optional, Callable
from PyQt6.QtCore import QSettings, pyqtSignal as Signal, QObject
from script.lang_mgr import LanguageManager

class RecentFoldersManager(QObject):
    """Manages the list of recently used folders."""
    # Signal emitted when the recent folders list changes
    recent_folders_changed = Signal(list)
    
    def __init__(self, max_recent: int = 10, settings_key: str = "recentFolders"):
        """Initialize the recent folders manager.
        
        Args:
            max_recent: Maximum number of recent folders to keep
            settings_key: Key to use in QSettings for storing the recent folders
        """
        super().__init__()
        self.max_recent = max_recent
        self.settings_key = settings_key
        self._recent_folders: List[str] = []
        self.language_manager = LanguageManager()
        self.tr = self.language_manager.tr
        self.load_recent_folders()
    
    def add_recent_folder(self, folder_path: str) -> None:
        """Add a folder to the recent folders list.
        
        Args:
            folder_path: Path to the folder to add
        """
        if not folder_path:
            return
            
        # Convert to absolute path and normalize
        folder_path = str(Path(folder_path).absolute())
        
        # Remove the folder if it already exists in the list
        if folder_path in self._recent_folders:
            self._recent_folders.remove(folder_path)
        
        # Add to the beginning of the list
        self._recent_folders.insert(0, folder_path)
        
        # Trim the list if it's too long
        if len(self._recent_folders) > self.max_recent:
            self._recent_folders = self._recent_folders[:self.max_recent]
        
        # Save the updated list and notify listeners
        self.save_recent_folders()
        self.recent_folders_changed.emit(self._recent_folders)
    
    def get_recent_folders(self) -> List[str]:
        """Get the list of recent folders.
        
        Returns:
            List of recent folder paths
        """
        return self._recent_folders.copy()
    
    def clear_recent_folders(self) -> None:
        """Clear the list of recent folders."""
        self._recent_folders = []
        self.save_recent_folders()
        self.recent_folders_changed.emit(self._recent_folders)
    
    def save_recent_folders(self) -> None:
        """Save the recent folders list to QSettings."""
        settings = QSettings()
        settings.setValue(self.settings_key, self._recent_folders)
    
    def load_recent_folders(self) -> None:
        """Load the recent folders list from QSettings."""
        settings = QSettings()
        recent = settings.value(self.settings_key, [], type=list)
        
        # Filter out non-existent folders
        self._recent_folders = [
            folder for folder in recent 
            if isinstance(folder, str) and os.path.isdir(folder)
        ]
        
        # Ensure we don't exceed max_recent
        if len(self._recent_folders) > self.max_recent:
            self._recent_folders = self._recent_folders[:self.max_recent]
            self.save_recent_folders()
        
        self.recent_folders_changed.emit(self._recent_folders)
    
    def create_recent_menu_actions(
        self, 
        menu, 
        on_triggered: Callable[[str], None],
        clear_action_text: Optional[str] = None
    ) -> None:
        """Create menu actions for recent folders.
        
        Args:
            menu: The QMenu to add the actions to
            on_triggered: Callback function when a recent folder is selected
            clear_action_text: Optional custom text for the clear action
        """
        # Clear existing actions
        menu.clear()
        
        # Get localized strings
        clear_text = clear_action_text or self.tr("recent_folders.clear_recent", "Clear Recent Folders")
        no_recent_text = self.tr("recent_folders.no_recent_folders", "No recent folders")
        
        # Add recent folders
        for i, folder in enumerate(self._recent_folders, 1):
            # Use only the last two parts of the path for display
            display_path = os.path.join("..", *Path(folder).parts[-2:]) if len(Path(folder).parts) > 2 else folder
            action = menu.addAction(f"&{i} {display_path}")
            action.setData(folder)
            action.triggered.connect(lambda checked, f=folder: on_triggered(f))
        
        # Add separator and clear action if there are recent folders
        if self._recent_folders:
            menu.addSeparator()
            clear_action = menu.addAction(clear_text)
            clear_action.triggered.connect(self.clear_recent_folders)
        
        # Add disabled "No recent folders" item if list is empty
        if not self._recent_folders:
            no_recent = menu.addAction(no_recent_text)
            no_recent.setEnabled(False)
