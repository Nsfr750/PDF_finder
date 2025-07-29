"""
UI Module for PDF Duplicate Finder.

This module contains all the UI-related code for the application,
separated from the main application logic.
"""
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStatusBar, QLabel, QFileDialog, QMessageBox, QToolBar
)

from .main_window import MainWindow
from .menu import MenuManager
from .toolbar import ToolbarManager
from .drag_drop import FileDropHandler
from .preview_widget import PDFPreviewWidget

class PDFDuplicateFinderUI(MainWindow):
    """Main UI class for PDF Duplicate Finder."""
    
    def __init__(self, parent=None, language_manager=None, app_settings=None):
        """Initialize the UI.
        
        Args:
            parent: Parent widget
            language_manager: Instance of LanguageManager
            app_settings: Application settings dictionary
        """
        super().__init__(language_manager, parent)
        
        # Store references
        self.language_manager = language_manager
        self.app_settings = app_settings or {}
        
        # Initialize variables
        self.duplicate_groups = []
        self.current_group_index = -1
        self.current_file_index = -1
        self.scan_directories = []
        self.scan_thread = None
        self.is_scanning = False
        self.preview_window = None
        
        # Initialize UI components
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle(f"{self.tr('PDF Duplicate Finder')}")
        self.setMinimumSize(1000, 700)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # Create menu bar 
        self.menu_manager = MenuManager(self, self.language_manager)
        self.setMenuBar(self.menu_manager.get_menu_bar())
        
        # Create and add toolbar
        self.toolbar_manager = ToolbarManager(self, self.language_manager)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar_manager.get_toolbar())
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel()
        self.status_bar.addWidget(self.status_label)
        
        # Initialize file drop handler
        self._file_drop_handler = FileDropHandler(self)
        
        # Connect menu and toolbar signals
        self.setup_connections()
    
    def create_main_content(self):
        """Create the main content area with split panels."""
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel (search and duplicates list)
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("Search files..."))
        self.search_box.textChanged.connect(self.filter_duplicates)
        self.left_layout.addWidget(self.search_box)
        
        # Duplicates list
        self.duplicates_list = QListWidget()
        self.duplicates_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.duplicates_list.itemDoubleClicked.connect(self.on_duplicate_double_clicked)
        self.duplicates_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.duplicates_list.customContextMenuRequested.connect(self.show_duplicate_context_menu)
        self.left_layout.addWidget(self.duplicates_list)
        
        # Right panel (file details and preview)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # File details
        self.file_details = QTextEdit()
        self.file_details.setReadOnly(True)
        self.right_layout.addWidget(QLabel(self.tr("File Details:")))
        self.right_layout.addWidget(self.file_details)
        
        # Preview area
        self.preview_area = PDFPreviewWidget()
        self.right_layout.addWidget(QLabel(self.tr("Preview:")))
        self.right_layout.addWidget(self.preview_area)
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.right_panel)
        
        # Set initial sizes
        self.main_splitter.setSizes([400, 600])
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.main_splitter)
    
    def setup_connections(self):
        """Connect menu and toolbar signals to slots."""
        # File menu
        self.menu_manager.open_folder_triggered.connect(self.on_scan_folder)
        self.menu_manager.save_results_triggered.connect(self.save_scan_results)
        self.menu_manager.load_results_triggered.connect(self.load_scan_results)
        self.menu_manager.exit_triggered.connect(self.close)
        
        # View menu
        self.menu_manager.view_log_triggered.connect(self.on_view_log)
        self.menu_manager.pdf_viewer_triggered.connect(self.on_pdf_viewer)
        
        # Tools menu
        self.menu_manager.check_updates_triggered.connect(self.on_check_updates)
        
        # Help menu
        self.menu_manager.documentation_triggered.connect(self.on_help)
        self.menu_manager.markdown_docs_triggered.connect(self.on_markdown_docs)
        self.menu_manager.sponsor_triggered.connect(self.on_sponsor)
        self.menu_manager.about_triggered.connect(self.on_about)
        
        # Connect toolbar actions
        self.toolbar_manager.open_folder_triggered.connect(self.on_scan_folder)
        self.toolbar_manager.save_results_triggered.connect(self.save_scan_results)
        self.toolbar_manager.load_results_triggered.connect(self.load_scan_results)
    
    def update_status(self, message, timeout=5000):
        """Update the status bar with a message.
        
        Args:
            message: Message to display
            timeout: Time in milliseconds to show the message (0 = show until next message)
        """
        self.status_label.setText(message)
        if timeout > 0:
            self.status_bar.showMessage(message, timeout)
    
    def show_error(self, title, message):
        """Show an error message dialog.
        
        Args:
            title: Dialog title
            message: Error message to display
        """
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title, message):
        """Show an information message dialog.
        
        Args:
            title: Dialog title
            message: Information message to display
        """
        QMessageBox.information(self, title, message)
    
    def get_open_file_name(self, title, filter_str, initial_dir=None):
        """Show a file open dialog.
        
        Args:
            title: Dialog title
            filter_str: File filter string
            initial_dir: Initial directory (optional)
            
        Returns:
            Selected file path or None if cancelled
        """
        options = QFileDialog.Option(0)
        if initial_dir:
            options |= QFileDialog.Option.DontUseNativeDialog
            
        file_name, _ = QFileDialog.getOpenFileName(
            self, title, initial_dir or "", filter_str, options=options
        )
        return file_name if file_name else None
    
    def get_save_file_name(self, title, filter_str, initial_dir=None):
        """Show a file save dialog.
        
        Args:
            title: Dialog title
            filter_str: File filter string
            initial_dir: Initial directory (optional)
            
        Returns:
            Selected file path or None if cancelled
        """
        options = QFileDialog.Option(0)
        if initial_dir:
            options |= QFileDialog.Option.DontUseNativeDialog
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, title, initial_dir or "", filter_str, options=options
        )
        return file_name if file_name else None
    
    def get_existing_directory(self, title, initial_dir=None):
        """Show a directory selection dialog.
        
        Args:
            title: Dialog title
            initial_dir: Initial directory (optional)
            
        Returns:
            Selected directory path or None if cancelled
        """
        options = QFileDialog.Option(0)
        if initial_dir:
            options |= QFileDialog.Option.DontUseNativeDialog
            
        dir_path = QFileDialog.getExistingDirectory(
            self, title, initial_dir or "", options=options
        )
        return dir_path if dir_path else None
