"""
Main window implementation with internationalization support.
"""
import os
from pathlib import Path
from typing import Callable, Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMenuBar, QMenu, QVBoxLayout, QHBoxLayout,
    QMessageBox, QApplication, QWidget, QSplitter, QListWidget, QLineEdit,
    QLabel, QStatusBar, QToolBar, QDockWidget, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy, QFrame
)
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal as Signal, QObject, Qt, QLocale, QTranslator, QLibraryInfo, QSize

# Import the language manager and menu manager
from .language_manager import LanguageManager
from .menu import MenuManager

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
        
        # Set window properties
        self.setWindowTitle("PDF Duplicate Finder")
        self.setMinimumSize(1000, 700)
        
        # Set up the UI
        self.setup_ui()
        
        # Connect to language change signals
        self.language_manager.language_changed.connect(self.retranslate_ui)
    
    def tr(self, key: str, default_text: str = "") -> str:
        """Translate a string using the language manager."""
        return self.language_manager.tr(key, default_text)
    
    def setup_ui(self):
        """Set up the main window UI with the requested layout."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Search and duplicates list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("search_placeholder", "Search duplicates..."))
        self.search_box.setClearButtonEnabled(True)
        left_layout.addWidget(self.search_box)
        
        # Duplicates list
        self.duplicates_list = QTableWidget()
        self.duplicates_list.setColumnCount(2)
        self.duplicates_list.setHorizontalHeaderLabels([
            self.tr("file_name", "File Name"),
            self.tr("path", "Path")
        ])
        self.duplicates_list.horizontalHeader().setStretchLastSection(True)
        self.duplicates_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.duplicates_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        left_layout.addWidget(self.duplicates_list)
        
        # Right panel - File details and preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        
        # File details
        details_group = QFrame()
        details_group.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)
        details_layout = QVBoxLayout(details_group)
        
        self.file_details = QTextEdit()
        self.file_details.setReadOnly(True)
        details_layout.addWidget(QLabel(self.tr("file_details", "File Details")))
        details_layout.addWidget(self.file_details)
        
        # Preview area
        preview_group = QFrame()
        preview_group.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel(self.tr("preview", "Preview"))
        self.preview_image = QLabel()
        self.preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_image.setStyleSheet("background-color: #f0f0f0;")
        self.preview_image.setMinimumSize(300, 400)
        
        preview_layout.addWidget(self.preview_label)
        preview_layout.addWidget(self.preview_image, 1)
        
        # Add to right panel
        right_layout.addWidget(details_group, 1)
        right_layout.addWidget(preview_group, 2)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])  # Initial sizes
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.tr("ready", "Ready"))
        
        # Set initial window state
        self.update_window_state()
    
    def create_menu_bar(self):
        """Create the main menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(self.tr("file", "&File"))
        
        self.open_folder_action = QAction(self.tr("open_folder", "&Open Folder..."), self)
        self.open_folder_action.triggered.connect(self.on_open_folder)
        file_menu.addAction(self.open_folder_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction(self.tr("exit", "E&xit"), self)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu(self.tr("edit", "&Edit"))
        
        self.settings_action = QAction(self.tr("settings", "&Settings..."), self)
        self.settings_action.triggered.connect(self.on_settings)
        edit_menu.addAction(self.settings_action)
        
        # View menu
        view_menu = menubar.addMenu(self.tr("view", "&View"))
        # Add view options here
        
        # Help menu
        help_menu = menubar.addMenu(self.tr("help", "&Help"))
        
        self.about_action = QAction(self.tr("about", "&About"), self)
        self.about_action.triggered.connect(self.on_about)
        help_menu.addAction(self.about_action)
    
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar(self.tr("main_toolbar", "Main Toolbar"))
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add common actions to toolbar
        self.open_folder_action.setIcon(self.style().standardIcon(
            getattr(QStyle.StandardPixmap, 'SP_DirOpenIcon')))
        toolbar.addAction(self.open_folder_action)
        
        toolbar.addSeparator()
        
        # Add more toolbar actions as needed
    
    def update_window_state(self):
        """Update window state and geometry."""
        self.setWindowState(Qt.WindowState.WindowNoState)
        self.showMaximized()
    
    def retranslate_ui(self):
        """Retranslate all UI elements."""
        self.setWindowTitle(self.tr("app_title", "PDF Duplicate Finder"))
        
        # Update menu bar
        self.menuBar().actions()[0].setText(self.tr("file", "&File"))  # File menu
        self.menuBar().actions()[1].setText(self.tr("edit", "&Edit"))  # Edit menu
        self.menuBar().actions()[2].setText(self.tr("view", "&View"))  # View menu
        self.menuBar().actions()[3].setText(self.tr("help", "&Help"))  # Help menu
        
        # Update actions
        self.open_folder_action.setText(self.tr("open_folder", "&Open Folder..."))
        self.exit_action.setText(self.tr("exit", "E&xit"))
        self.settings_action.setText(self.tr("settings", "&Settings..."))
        self.about_action.setText(self.tr("about", "&About"))
        
        # Update other UI elements
        self.search_box.setPlaceholderText(self.tr("search_placeholder", "Search duplicates..."))
        self.duplicates_list.setHorizontalHeaderLabels([
            self.tr("file_name", "File Name"),
            self.tr("path", "Path")
        ])
        self.file_details.setPlaceholderText(self.tr("select_file_to_view_details", "Select a file to view details"))
        self.preview_label.setText(self.tr("preview", "Preview"))
        self.status_bar.showMessage(self.tr("ready", "Ready"))
        
        # Call registered callbacks
        for callback in self.retranslate_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in retranslate callback: {e}")
    
    # Virtual methods that can be overridden by child classes
    
    def on_open_folder(self):
        """Handle the Open Folder action."""
        pass
    
    def on_settings(self):
        """Handle the Settings action."""
        pass
    
    def on_about(self):
        """Handle the About action."""
        pass
