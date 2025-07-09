"""
Main window implementation with internationalization support.
"""
import os
from pathlib import Path
from typing import Callable, Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMenuBar, QMenu,
    QMessageBox, QApplication
)
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtCore import pyqtSignal as Signal, QObject, QLocale, Qt, QTranslator, QLibraryInfo

from .i18n import Translator

class MainWindow(QMainWindow):
    """Base main window class with internationalization support."""
    
    # Signal emitted when the language is changed
    language_changed = Signal()
    
    def __init__(self, translator: Optional[Translator] = None, parent: Optional[QObject] = None):
        """Initialize the main window.
        
        Args:
            translator: Optional Translator instance. If not provided, a new one will be created.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.translator = translator or Translator(QApplication.instance())
        self.retranslate_callbacks = []
        
        # Set up the UI
        self.setup_ui()
        
        # Connect signals
        self.translator.notifier.language_changed.connect(self.retranslate_ui)
    
    def setup_ui(self):
        """Set up the main window UI."""
        # Create menu bar
        menubar = self.menuBar()
        
        # Language menu will be created in the child class
            
    def retranslate_ui(self):
        """Retranslate all UI elements."""
        # This method should be overridden by subclasses to update their UI elements
        self.setWindowTitle(self.tr("PDF Duplicate Finder"))
        
        # Update menu bar
        menubar = self.menuBar()
        
        # Update File menu
        file_menu = menubar.actions()[0].menu()
        file_menu.setTitle(self.tr("File"))
        file_menu.actions()[0].setText(self.tr("Open Folder"))
        file_menu.actions()[2].setText(self.tr("Exit"))
        
        # Update Tools menu
        tools_menu = menubar.actions()[1].menu()
        tools_menu.setTitle(self.tr("Tools"))
        
        # Update Language submenu
        language_action = next((a for a in tools_menu.actions() if a.text() == self.tr("Language")), None)
        if language_action and language_action.menu():
            language_menu = language_action.menu()
            language_menu.setTitle(self.tr("Language"))
        
        # Update Help menu
        help_menu = menubar.actions()[2].menu()
        help_menu.setTitle(self.tr("Help"))
        help_menu.actions()[0].setText(self.tr("About"))
        
        # Call registered callbacks
        for callback in self.retranslate_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in retranslate callback: {e}")
    
    def change_language(self, language_code: str):
        """Change the application language.
        
        Args:
            language_code: Two-letter language code (e.g., 'en', 'it')
        """
        if language_code != self.translator.current_language:
            self.translator.load_language(language_code)
            self.retranslate_ui()
            self.language_changed.emit()
    
    def on_open_folder(self):
        """Handle the 'Open Folder' action."""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Folder to Scan"),
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            self.scan_folder(folder)
    
    def scan_folder(self, folder_path: str):
        """Scan a folder for PDF files.
        
        Args:
            folder_path: Path to the folder to scan
        """
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement scan_folder method")
    
    def closeEvent(self, event):
        """Handle the window close event."""
        # Save settings or perform cleanup here
        event.accept()
