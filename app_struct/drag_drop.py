"""
Drag and drop functionality for PDF Duplicate Finder.

This module provides a DragDropManager class that handles drag and drop operations
for files and folders in the application.
"""
import os
import re
import tkinter as tk
from tkinterdnd2 import DND_FILES
from typing import Callable, Optional

class DragDropManager:
    """
    Manages drag and drop functionality for the application.
    
    This class handles the setup and management of drag and drop operations,
    including visual feedback and file processing.
    """
    
    def __init__(self, root, on_drop_callback: Callable[[str], None], lang: str = 'en'):
        """
        Initialize the DragDropManager.
        
        Args:
            root: The root Tkinter window
            on_drop_callback: Function to call when files/folders are dropped
            lang: Language code for UI text
        """
        self.root = root
        self.on_drop_callback = on_drop_callback
        self.lang = lang
        self.drop_highlight = None
        
        # Set up the drag and drop functionality
        self._setup_drag_drop()
    
    def _setup_drag_drop(self) -> None:
        """Set up drag and drop functionality."""
        try:
            # Remove any existing drop target handlers
            if hasattr(self, '_drop_target_registered'):
                self.root.drop_target_unregister()
            
            # Enable drag and drop for files and folders
            self.root.drop_target_register(DND_FILES)
            
            # Bind drag and drop events
            self.root.dnd_bind('<<DropEnter>>', self._on_drop_enter)
            self.root.dnd_bind('<<DropLeave>>', self._on_drop_leave)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
            
            # Create a drop highlight frame (initially hidden)
            if not hasattr(self, 'drop_highlight'):
                self.drop_highlight = tk.Label(
                    self.root, 
                    text=self._get_translation('drop_folder_here'),
                    background='#e6f3ff',
                    foreground='#0066cc',
                    font=('Arial', 12, 'bold'),
                    relief='solid',
                    borderwidth=2,
                    padding=20
                )
            
            self._drop_target_registered = True
            
        except Exception as e:
            print(f"Warning: Could not set up drag and drop: {e}")
            if hasattr(self, 'drop_highlight'):
                self.drop_highlight.place_forget()
    
    def _on_drop_enter(self, event) -> str:
        """Handle drag enter event."""
        try:
            if hasattr(self, 'drop_highlight'):
                # Position the highlight over the main container
                self.drop_highlight.lift()
                self.drop_highlight.place(relx=0.5, rely=0.5, anchor='center', 
                                        relwidth=0.8, relheight=0.8)
                self.root.update_idletasks()
            return 'copy'  # Show copy cursor
        except Exception as e:
            print(f"Error in drop enter: {e}")
            return 'refuse'
    
    def _on_drop_leave(self, event) -> None:
        """Handle drag leave event."""
        try:
            if hasattr(self, 'drop_highlight'):
                self.drop_highlight.place_forget()
        except Exception as e:
            print(f"Error in drop leave: {e}")
    
    def _on_drop(self, event) -> None:
        """Handle drop event."""
        try:
            # Hide the drop highlight
            if hasattr(self, 'drop_highlight'):
                self.drop_highlight.place_forget()
            
            if not event.data:
                return
            
            # Process the dropped items (can be multiple files/folders)
            items = re.split(r'(?<!\\)\s+', event.data.strip('{}'))
            
            # Clean up paths (remove quotes and escape characters)
            cleaned_paths = []
            for item in items:
                # Remove surrounding quotes if present
                item = item.strip('\"\'')
                # Replace escaped spaces with regular spaces
                item = item.replace('\\ ', ' ')
                if os.path.exists(item):
                    cleaned_paths.append(item)
            
            if not cleaned_paths:
                print("No valid paths found in dropped items")
                return
                
            # Find the first valid directory or PDF file
            target_folder = None
            for path in cleaned_paths:
                if os.path.isdir(path):
                    target_folder = path
                    break
                elif os.path.isfile(path) and path.lower().endswith('.pdf'):
                    target_folder = os.path.dirname(path)
                    break
            
            if target_folder and self.on_drop_callback:
                # Call the callback with the target folder
                self.on_drop_callback(target_folder)
                return 'copy'  # Return copy to show success
                
        except Exception as e:
            error_msg = f"Error processing dropped items: {str(e)}"
            print(error_msg)
            
        return 'refuse'  # If we get here, something went wrong
    
    def _get_translation(self, key: str, default: str = "") -> str:
        """
        Get translation for a given key.
        
        Args:
            key: Translation key
            default: Default text if translation not found
            
        Returns:
            Translated string or default if not found
        """
        # Translations for different languages
        translations = {
            'en': {
                'drop_folder_here': 'Drop folder here',
                'scanning_folder': 'Scanning folder: {}',
            },
            'it': {
                'drop_folder_here': 'Trascina la cartella qui',
                'scanning_folder': 'Analisi cartella: {}',
            },
            # Add more languages as needed
        }
        
        # Get translations for current language or fall back to English
        lang_translations = translations.get(self.lang, translations['en'])
        return lang_translations.get(key, default)
    
    def set_language(self, lang: str) -> None:
        """
        Update the language for UI text.
        
        Args:
            lang: Language code (e.g., 'en', 'it')
        """
        self.lang = lang
        if hasattr(self, 'drop_highlight'):
            self.drop_highlight.config(text=self._get_translation('drop_folder_here'))