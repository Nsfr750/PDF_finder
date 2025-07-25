"""
Menu management for PDF Duplicate Finder.

This module provides the MenuManager class which handles the creation and management
of the application's menu bar, menus, and actions.
"""
from typing import Dict, Any, Callable, Optional

from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QIcon, QKeySequence, QAction, QActionGroup, QDesktopServices
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QFileDialog, QMessageBox
)
from .language_manager import LanguageManager
from .translation import TRANSLATIONS

# Get available languages from TRANSLATIONS
LANGUAGES = list(TRANSLATIONS.keys())

class MenuManager(QObject):
    """Manages the application's menu bar and actions."""
    
    # Signals
    open_folder_triggered = pyqtSignal()
    save_results_triggered = pyqtSignal()
    load_results_triggered = pyqtSignal()
    settings_triggered = pyqtSignal()
    exit_triggered = pyqtSignal()
    view_log_triggered = pyqtSignal()
    check_updates_triggered = pyqtSignal()
    about_triggered = pyqtSignal()
    documentation_triggered = pyqtSignal()
    markdown_docs_triggered = pyqtSignal()  # New signal for markdown documentation
    sponsor_triggered = pyqtSignal()
    pdf_viewer_triggered = pyqtSignal()
    language_changed = pyqtSignal(str)  # language_code
    
    def __init__(self, parent, language_manager: LanguageManager):
        """Initialize the menu manager.
        
        Args:
            parent: The parent widget (usually the main window)
            language_manager: The application's language manager
        """
        super().__init__(parent)
        self.parent = parent
        self.language_manager = language_manager
        
        # Create the menu bar
        self.menu_bar = QMenuBar(parent)
        
        # Create menus
        self.file_menu = None
        self.edit_menu = None
        self.view_menu = None
        self.tools_menu = None
        self.help_menu = None
        
        # Action groups
        self.language_group = None
        
        # Initialize the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the menu bar and its actions."""
        self.create_actions()
        self.create_menus()
    
    def create_actions(self):
        """Create all the actions for the menus."""
        # File menu actions
        self.open_action = QAction(
            self.parent.tr("file.open"),
            self.parent,
            shortcut=QKeySequence.StandardKey.Open,
            statusTip=self.parent.tr("tooltips.open_folder"),
            triggered=self.on_open_folder
        )
        
        self.save_results_action = QAction(
            self.parent.tr("file.save_results"),
            self.parent,
            shortcut=QKeySequence.StandardKey.Save,
            statusTip=self.parent.tr("tooltips.save_results"),
            triggered=self.save_results_triggered.emit
        )
        
        self.load_results_action = QAction(
            self.parent.tr("file.load_results"),
            self.parent,
            shortcut=QKeySequence("Ctrl+L"),
            statusTip=self.parent.tr("tooltips.load_results"),
            triggered=self.load_results_triggered.emit
        )
        
        self.settings_action = QAction(
            self.parent.tr("file.settings"),
            self.parent,
            shortcut=QKeySequence("Ctrl+,"),  # Common shortcut for preferences
            statusTip=self.parent.tr("tooltips.settings"),
            triggered=self.settings_triggered.emit
        )
        
        self.exit_action = QAction(
            self.parent.tr("file.exit"),
            self.parent,
            shortcut=QKeySequence.StandardKey.Quit,
            statusTip=self.parent.tr("tooltips.exit"),
            triggered=self.exit_triggered.emit
        )
        
        # View menu actions
        self.view_log_action = QAction(
            self.parent.tr("view.view_log"),
            self.parent,
            statusTip=self.parent.tr("tooltips.view_log"),
            triggered=self.view_log_triggered.emit
        )
        
        self.pdf_viewer_action = QAction(
            self.parent.tr("view.pdf_viewer"),
            self.parent,
            shortcut=QKeySequence("Ctrl+P"),
            statusTip=self.parent.tr("tooltips.pdf_viewer"),
            triggered=self.pdf_viewer_triggered.emit
        )
        
        # Tools menu actions
        self.check_updates_action = QAction(
            self.parent.tr("tools.check_updates"),
            self.parent,
            statusTip=self.parent.tr("tooltips.check_updates"),
            triggered=self.check_updates_triggered.emit
        )
        
        # Help menu actions
        self.documentation_action = QAction(
            self.parent.tr("help.documentation"),
            self.parent,
            shortcut=QKeySequence("F1"),  # Standard help key
            statusTip=self.parent.tr("tooltips.documentation"),
            triggered=self.documentation_triggered.emit
        )
        
        self.markdown_docs_action = QAction(
            self.parent.tr("help.markdown_docs"),
            self.parent,
            shortcut=QKeySequence("Shift+F1"),  # Alternative help key for markdown docs
            statusTip=self.parent.tr("tooltips.markdown_docs"),
            triggered=self.markdown_docs_triggered.emit
        )
        
        self.sponsor_action = QAction(
            self.parent.tr("help.sponsor"),
            self.parent,
            statusTip=self.parent.tr("tooltips.sponsor"),
            triggered=self.sponsor_triggered.emit
        )
        
        self.about_action = QAction(
            self.parent.tr("help.about"),
            self.parent,
            statusTip=self.parent.tr("tooltips.about"),
            triggered=self.about_triggered.emit
        )
    
    def create_menus(self):
        """Create the menu bar and its menus."""
        # File menu
        self.file_menu = self.menu_bar.addMenu(self.parent.tr("menu.file"))
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_results_action)
        self.file_menu.addAction(self.load_results_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.settings_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menu_bar.addMenu(self.parent.tr("menu.edit"))
        
        # View menu
        self.view_menu = self.menu_bar.addMenu(self.parent.tr("menu.view"))
        self.view_menu.addAction(self.view_log_action)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.pdf_viewer_action)
        
        # Tools menu
        self.tools_menu = self.menu_bar.addMenu(self.parent.tr("menu.tools"))
        self.tools_menu.addAction(self.check_updates_action)
        
        # Add language submenu to Tools menu
        self.create_language_menu()
        
        # Help menu
        self.help_menu = self.menu_bar.addMenu(self.parent.tr("menu.help"))
        self.help_menu.addAction(self.documentation_action)
        self.help_menu.addAction(self.markdown_docs_action)  # Add markdown docs action
        self.help_menu.addAction(self.sponsor_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)
    
    def create_language_menu(self):
        """Create the language selection submenu."""
        if not hasattr(self, 'language_menu'):
            self.language_menu = QMenu(self.parent.tr("menu.language"), self.parent)
            self.language_group = QActionGroup(self.parent)
            self.language_group.setExclusive(True)
            
            # Add available languages from language manager
            for code, name in self.language_manager.available_languages.items():
                action = QAction(name, self.parent, checkable=True)
                action.setData(code)
                action.triggered.connect(lambda checked, code=code: self.on_language_changed(code))
                self.language_group.addAction(action)
                self.language_menu.addAction(action)
                
                # Check the current language
                if code == self.language_manager.current_language:
                    action.setChecked(True)
            
            # Add language menu to Tools menu
            self.tools_menu.addMenu(self.language_menu)
    
    def on_open_folder(self):
        """Handle the 'Open Folder' action."""
        folder = QFileDialog.getExistingDirectory(
            self.parent,
            self.parent.tr("dialog.open_folder"),
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if folder:
            self.open_folder_triggered.emit(folder)
    
    def on_language_changed(self, language_code):
        """Handle language change from the language menu."""
        if language_code != self.language_manager.current_language:
            self.language_changed.emit(language_code)
    
    def retranslate_ui(self):
        """Retranslate all menu items."""
        # Update menu titles
        self.file_menu.setTitle(self.parent.tr("menu.file"))
        self.edit_menu.setTitle(self.parent.tr("menu.edit"))
        self.view_menu.setTitle(self.parent.tr("menu.view"))
        self.tools_menu.setTitle(self.parent.tr("menu.tools"))
        self.help_menu.setTitle(self.parent.tr("menu.help"))
        
        # Update action texts
        self.open_action.setText(self.parent.tr("file.open"))
        self.save_results_action.setText(self.parent.tr("file.save_results"))
        self.load_results_action.setText(self.parent.tr("file.load_results"))
        self.settings_action.setText(self.parent.tr("file.settings"))
        self.exit_action.setText(self.parent.tr("file.exit"))
        
        self.view_log_action.setText(self.parent.tr("view.view_log"))
        self.pdf_viewer_action.setText(self.parent.tr("view.pdf_viewer"))
        
        self.check_updates_action.setText(self.parent.tr("tools.check_updates"))
        
        self.documentation_action.setText(self.parent.tr("help.documentation"))
        self.markdown_docs_action.setText(self.parent.tr("help.markdown_docs"))
        self.sponsor_action.setText(self.parent.tr("help.sponsor"))
        self.about_action.setText(self.parent.tr("help.about"))
        
        # Update language menu
        if hasattr(self, 'language_menu'):
            self.language_menu.setTitle(self.parent.tr("menu.language"))
            for action in self.language_group.actions():
                if action.data() in self.language_manager.available_languages:
                    action.setText(self.language_manager.available_languages[action.data()])
    
    def set_menu_bar(self):
        """Set the menu bar for the main window."""
        self.parent.setMenuBar(self.menu_bar)
    
    def set_actions_enabled(self, enabled: bool):
        """Enable or disable menu actions.
        
        Args:
            enabled: Whether to enable or disable the actions
        """
        self.save_results_action.setEnabled(enabled)
        self.load_results_action.setEnabled(enabled)
        self.settings_action.setEnabled(enabled)
        self.view_log_action.setEnabled(enabled)
        self.pdf_viewer_action.setEnabled(enabled)
        self.check_updates_action.setEnabled(enabled)
