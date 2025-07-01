"""
Module for handling duplicate file search functionality.
"""
import os
import threading
from typing import List, Dict, Set, Tuple, Optional, Any
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import time

class DuplicateFinder:
    """Handles finding duplicate files in a directory."""
    
    def __init__(self, app):
        """
        Initialize the DuplicateFinder.
        
        Args:
            app: Reference to the main application instance
        """
        self.app = app
        self.stop_event = threading.Event()
        self.is_searching = False
    
    def _compare_files(self, file1: str, file2: str) -> bool:
        """
        Compare two files for equality based on current mode.
        
        Args:
            file1: Path to the first file
            file2: Path to the second file
            
        Returns:
            bool: True if files are identical, False otherwise
        """
        if not os.path.exists(file1) or not os.path.exists(file2):
            return False
            
        # Quick compare mode (faster but less accurate)
        if hasattr(self.app, 'quick_compare') and self.app.quick_compare.get():
            return os.path.getsize(file1) == os.path.getsize(file2)
        
        # Full compare mode (slower but more accurate)
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                # Compare file sizes first (quick check)
                if os.path.getsize(file1) != os.path.getsize(file2):
                    return False
                # If sizes match, compare content
                return f1.read() == f2.read()
        except Exception as e:
            if hasattr(self.app, 'show_status'):
                self.app.show_status(f"Error comparing files {file1} and {file2}: {str(e)}", "error")
            return False
    
    def find_duplicates(self, folder_path: str) -> None:
        """
        Find duplicate files in the specified folder.
        
        Args:
            folder_path: Path to the folder to search for duplicates
        """
        if not folder_path or not os.path.isdir(folder_path):
            if hasattr(self.app, 'show_status'):
                self.app.show_status("Please select a valid folder first.", "error")
            if hasattr(self.app, 'root'):
                self.app.root.after(0, lambda: messagebox.showerror("Error", "Please select a valid folder first."))
            return
            
        # Reset UI
        if hasattr(self.app, 'tree'):
            self.app.root.after(0, self._reset_ui)
        
        # Update UI for scanning
        self._update_ui_state(searching=True)
        
        # Start search in a separate thread
        self.stop_event.clear()
        search_thread = threading.Thread(
            target=self._find_duplicates_thread,
            args=(folder_path,),
            daemon=True
        )
        search_thread.start()
    
    def _reset_ui(self) -> None:
        """Reset the UI elements."""
        if hasattr(self.app, 'tree'):
            for item in self.app.tree.get_children():
                self.app.tree.delete(item)
    
    def _update_ui_state(self, searching: bool) -> None:
        """
        Update the UI state based on search status.
        
        Args:
            searching: Whether a search is in progress
        """
        if not hasattr(self.app, 'root'):
            return
            
        def update():
            if hasattr(self.app, 'find_btn'):
                self.app.find_btn.config(state=tk.DISABLED if searching else tk.NORMAL)
            if hasattr(self.app, 'stop_btn'):
                self.app.stop_btn.config(state=tk.NORMAL if searching else tk.DISABLED)
            if hasattr(self.app, 'progress_var'):
                self.app.progress_var.set(0)
                
        self.app.root.after(0, update)
    
    def _find_duplicates_thread(self, folder_path: str) -> None:
        """
        Worker thread for finding duplicates.
        
        Args:
            folder_path: Path to the folder to search for duplicates
        """
        try:
            self.is_searching = True
            self.stop_event.clear()
            
            # Implementation of duplicate finding logic
            # This is a placeholder - you'll need to implement the actual search logic here
            # based on your existing code
            
            # Example of how to update progress
            if hasattr(self.app, 'update_status'):
                self.app.root.after(0, lambda: self.app.update_status("Searching for duplicates...", "info"))
            
            # Simulate work (replace with actual search)
            import time
            for i in range(1, 101):
                if self.stop_event.is_set():
                    break
                if hasattr(self.app, 'progress_var'):
                    self.app.root.after(0, lambda v=i: setattr(self.app.progress_var, 'set', v))
                time.sleep(0.1)
            
            # Update status when done
            if hasattr(self.app, 'show_status'):
                self.app.root.after(0, lambda: self.app.show_status("Search completed", "success"))
                
        except Exception as e:
            if hasattr(self.app, 'show_status'):
                self.app.root.after(0, lambda: self.app.show_status(f"Error during search: {str(e)}", "error"))
        finally:
            self.is_searching = False
            self._update_ui_state(searching=False)
    
    def stop_search(self) -> None:
        """Stop the current search operation."""
        self.stop_event.set()
