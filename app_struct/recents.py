import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Callable, Dict, Any

class RecentFolders:
    """
    Manages the recent folders functionality for the application.
    Handles storing, loading, and displaying recent folders in the menu.
    """
    
    def __init__(self, app, max_recent: int = 10):
        """
        Initialize the RecentFolders manager.
        
        Args:
            app: Reference to the main application instance
            max_recent: Maximum number of recent folders to remember
        """
        self.app = app
        self.max_recent = max_recent
        self.recent_folders: List[str] = []
        self.on_folder_selected: Optional[Callable[[str], None]] = None
        self.menu: Optional[tk.Menu] = None
        self._keyboard_shortcuts: Dict[int, str] = {}
        
        # Load recent folders from settings
        self._load_recent_folders()
        
        # Clean up any invalid paths on initialization
        self.remove_invalid_paths()
    
    def _load_recent_folders(self):
        """Load recent folders from application settings."""
        if hasattr(self.app, 'settings'):
            self.recent_folders = self.app.settings.get('recent_folders', [])
    
    def save_to_settings(self):
        """Save recent folders to application settings."""
        if hasattr(self.app, 'settings'):
            self.app.settings['recent_folders'] = self.recent_folders
            if hasattr(self.app, 'save_settings'):
                self.app.save_settings()
    
    def add_folder(self, folder_path: str):
        """
        Add a folder to the recent folders list.
        
        Args:
            folder_path: Path to the folder to add
        """
        if not folder_path or not os.path.isdir(folder_path):
            return
            
        # Remove if already in list
        if folder_path in self.recent_folders:
            self.recent_folders.remove(folder_path)
        
        # Add to beginning of list
        self.recent_folders.insert(0, folder_path)
        
        # Trim to max length
        if len(self.recent_folders) > self.max_recent:
            self.recent_folders = self.recent_folders[:self.max_recent]
        
        # Save to settings
        self.save_to_settings()
        
        # Update the menu if available
        if hasattr(self, 'menu') and self.menu:
            self.update_menu()
    
    def clear(self):
        """Clear all recent folders."""
        if self.recent_folders:
            if messagebox.askyesno(
                "Clear Recent Folders",
                "Are you sure you want to clear the recent folders list?",
                parent=self.app.root if hasattr(self.app, 'root') else None
            ):
                self.recent_folders = []
                self.save_to_settings()
                if hasattr(self, 'menu') and self.menu:
                    self.update_menu()
                return True
        return False
    
    def create_menu(self, parent_menu) -> tk.Menu:
        """
        Create the recent folders menu.
        
        Args:
            parent_menu: The parent menu to attach to
            
        Returns:
            The created menu
        """
        self.menu = tk.Menu(parent_menu, tearoff=0)
        self.update_menu()
        return self.menu
    
    def update_menu(self):
        """
        Update the recent folders menu with current list.
        
        This method will clear the current menu and rebuild it with the current
        list of recent folders, including keyboard shortcuts.
        """
        if not hasattr(self, 'menu') or not self.menu:
            return
            
        # Clear current items
        self.menu.delete(0, 'end')
        
        # Clear any existing keyboard shortcuts
        self._clear_keyboard_shortcuts()
        
        if not self.recent_folders:
            self.menu.add_command(
                label="No recent folders",
                state=tk.DISABLED
            )
        else:
            for i, folder in enumerate(self.recent_folders, 1):
                # Show only the last 2 parts of the path for brevity
                display_path = os.path.join(*Path(folder).parts[-2:]) if len(Path(folder).parts) > 1 else folder
                
                self.menu.add_command(
                    label=f"{i}. {display_path}",
                    command=lambda f=folder: self._on_folder_selected(f),
                    accelerator=f"Ctrl+{i}" if i <= 9 else ""
                )
                
                # Add keyboard shortcuts (Ctrl+1 to Ctrl+9)
                if i <= 9 and hasattr(self.app, 'root'):
                    self._keyboard_shortcuts[i] = self.app.root.bind(
                        f'<Control-Key-{i}>',
                        lambda e, f=folder: self._on_folder_selected(f)
                    )
            
            # Add separator and clear option
            self.menu.add_separator()
            self.menu.add_command(
                label="Clear Recent Folders",
                command=self.clear
            )
    
    def _on_folder_selected(self, folder_path: str):
        """
        Handle selection of a recent folder.
        
        Args:
            folder_path: Path to the selected folder
        """
        if not os.path.isdir(folder_path):
            messagebox.showerror(
                "Error",
                f"Folder not found: {folder_path}",
                parent=self.app.root if hasattr(self.app, 'root') else None
            )
            # Remove non-existent folder from recent list
            self.recent_folders = [f for f in self.recent_folders if f != folder_path]
            self.save_to_settings()
            self.update_menu()
            return
            
        # Move the selected folder to the top of the list
        if folder_path in self.recent_folders:
            self.recent_folders.remove(folder_path)
        self.recent_folders.insert(0, folder_path)
        self.save_to_settings()
        
        # Call the callback if provided
        if callable(self.on_folder_selected):
            self.on_folder_selected(folder_path)
            
    def _clear_keyboard_shortcuts(self):
        """Remove all keyboard shortcuts for recent folders."""
        if not hasattr(self.app, 'root') or not self._keyboard_shortcuts:
            return
            
        for i, binding_id in self._keyboard_shortcuts.items():
            try:
                self.app.root.unbind(f'<Control-Key-{i}>', binding_id)
            except tk.TclError:
                pass
        self._keyboard_shortcuts.clear()
        
    def remove_invalid_paths(self):
        """Remove any paths that no longer exist from the recent folders list."""
        if not self.recent_folders:
            return
            
        original_count = len(self.recent_folders)
        self.recent_folders = [f for f in self.recent_folders if os.path.isdir(f)]
        
        if len(self.recent_folders) != original_count:
            self.save_to_settings()
            if hasattr(self, 'menu') and self.menu:
                self.update_menu()
                
    def get_recent_folders(self) -> List[str]:
        """
        Get the current list of recent folders.
        
        Returns:
            List of folder paths
        """
        return self.recent_folders.copy()
        
    def set_recent_folders(self, folders: List[str]):
        """
        Set the list of recent folders.
        
        Args:
            folders: List of folder paths to set
        """
        self.recent_folders = [str(f) for f in folders if os.path.isdir(str(f))][:self.max_recent]
        self.save_to_settings()
        if hasattr(self, 'menu') and self.menu:
            self.update_menu()