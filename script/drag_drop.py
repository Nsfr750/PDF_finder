import os
import logging
from PyQt6.QtCore import QMimeData, Qt, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from typing import List, Optional, Union, Callable
from lang.language_manager import LanguageManager

logger = logging.getLogger('PDFDuplicateFinder')

class FileDropHandler:
    """Class to add file drop functionality to widgets."""
    
    def __init__(self, widget):
        self.widget = widget
        self.widget.setAcceptDrops(True)
        self._file_drop_callback = None
        self._accepted_extensions = ['.pdf']  # Default to PDF files
    
    def set_accepted_extensions(self, extensions: List[str]):
        """Set the list of accepted file extensions."""
        self._accepted_extensions = [ext.lower() for ext in extensions]
    
    def set_file_drop_callback(self, callback: Callable[[List[str]], None]):
        """Set the callback function to handle dropped files."""
        self._file_drop_callback = callback
    
    def _has_accepted_extension(self, file_path: str) -> bool:
        """Check if the file has an accepted extension."""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self._accepted_extensions
    
    def _get_dropped_files(self, mime_data: QMimeData) -> List[str]:
        """Extract file paths from MIME data."""
        file_paths = []
        
        # Check for URLs (files from file manager)
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if os.path.isfile(file_path) and self._has_accepted_extension(file_path):
                        file_paths.append(file_path)
                    elif os.path.isdir(file_path):
                        # Recursively search for PDFs in the directory
                        for root, _, files in os.walk(file_path):
                            for file in files:
                                if self._has_accepted_extension(file):
                                    file_paths.append(os.path.join(root, file))
        
        return file_paths
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(self._has_accepted_extension(url.toLocalFile()) for url in urls if url.isLocalFile()):
                event.acceptProposedAction()
                return
        event.ignore()
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(self._has_accepted_extension(url.toLocalFile()) for url in urls if url.isLocalFile()):
                event.acceptProposedAction()
                return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                if url.isLocalFile() and self._has_accepted_extension(url.toLocalFile()):
                    file_paths.append(url.toLocalFile())
            
            if file_paths and self._file_drop_callback:
                self._file_drop_callback(file_paths)
                event.acceptProposedAction()
                return
        
        event.ignore()

class FileDropHandlerWrapper:
    """Class to add file drop functionality to widgets."""
    
    def __init__(self, widget):
        self._file_drop_handler = FileDropHandler(widget)
        
    def set_accepted_extensions(self, extensions):
        """Set the list of accepted file extensions."""
        self._file_drop_handler.set_accepted_extensions(extensions)
        
    def set_file_drop_callback(self, callback):
        """Set the callback function to handle dropped files."""
        self._file_drop_handler.set_file_drop_callback(callback)
        
    def dragEnterEvent(self, event):
        """Delegate drag enter event to the handler."""
        self._file_drop_handler.dragEnterEvent(event)
        
    def dragMoveEvent(self, event):
        """Delegate drag move event to the handler."""
        self._file_drop_handler.dragMoveEvent(event)
        
    def dropEvent(self, event):
        """Delegate drop event to the handler."""
        self._file_drop_handler.dropEvent(event)
