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

# Import the new language manager
from .language_manager import LanguageManager

class MainWindow(QMainWindow):
    """Base main window class with internationalization support."""
    
    # Signal emitted when the language is changed
    language_changed = Signal(str)  # language_code
    
    def __init__(self, language_manager: LanguageManager, parent: Optional[QObject] = None):
        """Initialize the main window.
        
        Args:
            language_manager: The application's language manager
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.language_manager = language_manager
        self.retranslate_callbacks = []
        
        # Set up the UI
        self.setup_ui()
        
        # Connect to language change signals
        self.language_manager.language_changed.connect(self.retranslate_ui)
    
    def tr(self, key: str, default_text: str = "") -> str:
        """Translate a string using the language manager."""
        return self.language_manager.tr(key, default_text)
    
    def setup_ui(self):
        """Set up the main window UI."""
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(self.tr("menu.file", "File"))
        
        # Add actions to File menu
        open_action = QAction(self.tr("menu.file_open", "Open Folder"), self)
        open_action.triggered.connect(self.on_open_folder)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(self.tr("menu.file_exit", "Exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu(self.tr("menu.tools", "Tools"))
        
        # Language submenu
        language_menu = tools_menu.addMenu(self.tr("menu.language", "Language"))
        self.language_group = QActionGroup(self)
        
        # Add available languages to the language menu
        for lang_code, lang_name in self.language_manager.available_languages.items():
            action = QAction(lang_name, self, checkable=True)
            action.setData(lang_code)
            action.triggered.connect(lambda checked, code=lang_code: self.change_language(code))
            language_menu.addAction(action)
            self.language_group.addAction(action)
            
            # Check the current language
            if lang_code == self.language_manager.current_language:
                action.setChecked(True)
        
        # Help menu
        help_menu = menubar.addMenu(self.tr("menu.help", "Help"))
        
        # Add About action
        about_action = QAction(self.tr("menu.help_about", "About"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Set window title
        self.retranslate_ui()
    
    def retranslate_ui(self):
        """Retranslate all UI elements."""
        self.setWindowTitle(self.tr("main_window.title", "PDF Duplicate Finder"))
        
        # Update menu bar
        menubar = self.menuBar()
        
        # Update File menu
        file_menu = menubar.actions()[0].menu()
        file_menu.setTitle(self.tr("menu.file", "File"))
        file_menu.actions()[0].setText(self.tr("menu.file_open", "Open Folder"))
        file_menu.actions()[2].setText(self.tr("menu.file_exit", "Exit"))
        
        # Update Tools menu
        tools_menu = menubar.actions()[1].menu()
        tools_menu.setTitle(self.tr("menu.tools", "Tools"))
        
        # Update Language submenu
        language_action = next((a for a in tools_menu.actions() if a.text() == self.tr("menu.language", "Language")), None)
        if language_action and language_action.menu():
            language_menu = language_action.menu()
            language_menu.setTitle(self.tr("menu.language", "Language"))
            
            # Update language action names
            for action in language_menu.actions():
                lang_code = action.data()
                if lang_code in self.language_manager.available_languages:
                    action.setText(self.language_manager.available_languages[lang_code])
        
        # Update Help menu
        help_menu = menubar.actions()[2].menu()
        help_menu.setTitle(self.tr("menu.help", "Help"))
        help_menu.actions()[0].setText(self.tr("menu.help_about", "About"))
        
        # Call registered callbacks
        for callback in self.retranslate_callbacks:
            try:
                callback()
            except Exception as e:
                print(self.tr("main_window.retranslate_error", "Error in retranslate callback: {error}").format(error=str(e)))
    
    def change_language(self, language_code: str):
        """Change the application language.
        
        Args:
            language_code: Two-letter language code (e.g., 'en', 'it')
        """
        if self.language_manager.set_language(language_code):
            self.language_changed.emit(language_code)
    
    def on_open_folder(self):
        """Handle the 'Open Folder' action."""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr("dialog.select_folder", "Select Folder to Scan"),
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if folder:
            self.scan_folder(folder)
    
    def show_about(self):
        """Show the About dialog."""
        QMessageBox.about(
            self,
            self.tr("dialog.about_title", "About PDF Duplicate Finder"),
            self.tr(
                "dialog.about_text",
                "<h2>PDF Duplicate Finder</h2>"
                "<p>Version: 1.0.0</p>"
                "<p>Find and manage duplicate PDF files on your computer.</p>"
                "<p> 2025 PDF Duplicate Finder</p>"
            )
        )
    
    def scan_folder(self, folder_path: str):
        """Scan a folder for PDF files.
        
        Args:
            folder_path: Path to the folder to scan
        """
        # This method should be overridden by subclasses
        raise NotImplementedError(self.tr("error.not_implemented", "Subclasses must implement scan_folder method"))
    
    def closeEvent(self, event):
        """Handle the window close event."""
        # Save settings or perform cleanup here
        event.accept()
