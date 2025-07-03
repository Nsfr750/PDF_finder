import os
import sys
import logging
import traceback
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from logging.handlers import RotatingFileHandler

# Qt imports
from PySide6.QtCore import (
    Qt, QSize, QThread, Signal, Slot, QObject, QTimer, QSettings, 
    QPoint, QEvent, QMimeData, QUrl, QByteArray, QBuffer, QIODevice,
    QLocale, QTranslator, QLibraryInfo
)
from PySide6.QtGui import (
    QIcon, QPixmap, QFont, QColor, QPalette, QKeySequence, 
    QDragEnterEvent, QDropEvent, QImage, QImageReader, 
    QAction, QActionGroup
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QFileDialog, QMessageBox, QMenuBar, QMenu, QStyle, QTreeWidget,
    QTreeWidgetItem, QAbstractItemView, QToolBar, QStatusBar, QCheckBox, QSpinBox,
    QDoubleSpinBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QTextEdit, QTabWidget, QGroupBox, QRadioButton, QButtonGroup, QScrollArea,
    QFrame, QSizePolicy, QSpacerItem, QSystemTrayIcon, QStyleFactory, QInputDialog,
    QListWidget, QListWidgetItem, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem,
    QProgressDialog, QToolButton
)

# Application imports
from app_qt.main_window import MainWindow
from app_qt.i18n import Translator
from app_qt.drag_drop import FileDropHandler
from app_qt.gest_scan import ScanManager
from app_qt.recents import RecentFilesManager
from app_qt.gest_recent import RecentFoldersManager
from app_qt.delete import DeleteConfirmationDialog, delete_files
from app_qt.search_dup import DuplicateFilesView, DuplicateFilesModel, DuplicateGroup, DuplicateFileItem

# Import utility functions
from pdf_utils import (
    get_pdf_info, calculate_file_hash, extract_first_page_image,
    calculate_image_hash, find_duplicates
)
from preview_widget import PDFPreviewWidget

# Set up logging before importing Qt
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            log_dir / 'pdf_finder.log',
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('PDFDuplicateFinder')
logger.info('=' * 80)
logger.info('PDF Duplicate Finder started')
logger.info(f'Log file: {log_dir / "pdf_finder.log"}')



# Import application modules
# Import app_qt modules
from app_qt.i18n import Translator
from app_qt.main_window import MainWindow
from app_qt.drag_drop import FileDropHandler
from app_qt.gest_scan import ScanManager
from app_qt.recents import RecentFilesManager
from app_qt.delete import DeleteConfirmationDialog, delete_files
from app_qt.search_dup import DuplicateFilesView, DuplicateFilesModel, DuplicateGroup, DuplicateFileItem

# Import utility functions
from pdf_utils import (
    get_pdf_info, calculate_file_hash, extract_first_page_image,
    calculate_image_hash, find_duplicates
)
from preview_widget import PDFPreviewWidget

# Import app_qt modules
from app_qt.drag_drop import FileDropHandler
from app_qt.gest_scan import ScanManager
from app_qt.recents import RecentFilesManager
from app_qt.delete import DeleteConfirmationDialog, delete_files
from app_qt.search_dup import DuplicateFilesView, DuplicateFilesModel, DuplicateGroup, DuplicateFileItem

def setup_logging():
    """Configure the logging system for the application."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Main log file path
    log_file = os.path.join(log_dir, 'pdf_finder.log')
    
    # Create a custom formatter
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Configure the root logger
    logger = logging.getLogger('PDFDuplicateFinder')
    logger.setLevel(logging.DEBUG)
    
    # Add file handler
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log the start of the application
    logger.info("=" * 80)
    logger.info("PDF Duplicate Finder started")
    logger.info(f"Log file: {log_file}")
    
    return logger

# Set up logging
logger = setup_logging()

# Constants
APP_NAME = "PDF Duplicate Finder"
APP_VERSION = "2.7.0"

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # App name and version
        title = QLabel(f"<h1>{APP_NAME}</h1>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version = QLabel(f"Version: {APP_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        description = QLabel(
            "A tool to find and manage duplicate PDF files on your computer."
        )
        description.setWordWrap(True)
        
        # Copyright
        copyright = QLabel(" 2025 Nsfr750")
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # OK button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(description)
        layout.addStretch()
        layout.addWidget(copyright)
        layout.addWidget(button_box)
        
        self.setLayout(layout)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        
        # Initialize with default settings
        self.settings = {
            'scan_recursive': True,
            'min_file_size': 100,  # KB
            'max_file_size': 10000,  # KB
            'hash_size': 8,
            'threshold': 5,
            'theme': 'system',
            'language': 'en'
        }
        
        # Update with any provided current settings
        if current_settings:
            self.settings.update(current_settings)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create form layout for settings
        form = QFormLayout()
        
        # Scan options
        self.scan_recursive = QCheckBox("Scan subdirectories")
        self.scan_recursive.setChecked(self.settings['scan_recursive'])
        
        # File size range
        size_layout = QHBoxLayout()
        self.min_size = QSpinBox()
        self.min_size.setRange(0, 100000)
        self.min_size.setValue(self.settings['min_file_size'])
        self.max_size = QSpinBox()
        self.max_size.setRange(1, 1000000)
        self.max_size.setValue(self.settings['max_file_size'])
        size_layout.addWidget(QLabel("Min (KB):"))
        size_layout.addWidget(self.min_size)
        size_layout.addWidget(QLabel("Max (KB):"))
        size_layout.addWidget(self.max_size)
        size_layout.addStretch()
        
        # Hash settings
        self.hash_size = QSpinBox()
        self.hash_size.setRange(4, 16)
        self.hash_size.setValue(self.settings['hash_size'])
        
        self.threshold = QSpinBox()
        self.threshold.setRange(0, 100)
        self.threshold.setValue(self.settings['threshold'])
        
        # Theme
        self.theme = QComboBox()
        self.theme.addItems(['system', 'light', 'dark'])
        self.theme.setCurrentText(self.settings['theme'])
        
        # Language
        self.language = QComboBox()
        self.language.addItems(['en', 'it'])
        self.language.setCurrentText(self.settings['language'])
        
        # Add fields to form
        form.addRow("Scan options:", self.scan_recursive)
        form.addRow("File size range:", size_layout)
        form.addRow("Hash size:", self.hash_size)
        form.addRow("Similarity threshold (%):", self.threshold)
        form.addRow("Theme:", self.theme)
        form.addRow("Language:", self.language)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        # Add to main layout
        layout.addLayout(form)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_settings(self):
        return {
            'scan_recursive': self.scan_recursive.isChecked(),
            'min_file_size': self.min_size.value(),
            'max_file_size': self.max_size.value(),
            'hash_size': self.hash_size.value(),
            'threshold': self.threshold.value(),
            'theme': self.theme.currentText(),
            'language': self.language.currentText()
        }
    
    def restore_defaults(self):
        self.scan_recursive.setChecked(True)
        self.min_size.setValue(100)
        self.max_size.setValue(10000)
        self.hash_size.setValue(8)
        self.threshold.setValue(5)
        self.theme.setCurrentText('system')
        self.language.setCurrentText('en')

class PDFDuplicateFinder(MainWindow):
    """Main application window for PDF Duplicate Finder."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("PDFDuplicateFinder", "PDFDuplicateFinder")
        self.app_settings = {}  # Will be populated in load_settings()
        
        # Initialize variables
        self.duplicate_groups = []
        self.current_group_index = -1
        self.current_file_index = -1
        self.scan_directories = []
        self.scan_thread = None
        self.is_scanning = False
        
        # Initialize managers
        self.recent_manager = RecentFilesManager()
        self.recent_folders_manager = RecentFoldersManager()
        self.scan_manager = ScanManager()
        
        # Initialize UI
        self.init_ui()
        
        # Load settings
        self.load_settings()
        
        # Apply theme
        self.apply_theme()
        
        # Load recent files after UI is fully initialized
        self.load_recent_files()
        
        # Connect signals
        self.scan_manager.scan_completed.connect(self.on_scan_completed)
        self.scan_manager.progress.connect(self.update_progress)
        self.scan_manager.file_processed.connect(self.on_file_processed)
    
    def stop_scan(self):
        """Stop the current scan operation."""
        if hasattr(self, 'scan_manager'):
            self.scan_manager.cancel_scan()
            self.is_scanning = False
            if hasattr(self, 'progress_bar'):
                self.progress_bar.hide()
            if hasattr(self, 'status_label'):
                self.status_label.setText(self.tr("Scan stopped by user."))
            self.update_ui_state()
    
    def retranslate_ui(self):
        """Retranslate all UI elements."""
        # Check if the widget is being destroyed
        if not self or not hasattr(self, 'isVisible'):
            return
            
        try:
            # Call parent's retranslate_ui first
            super().retranslate_ui()
            
            # Update main window title
            self.setWindowTitle(self.tr("PDF Duplicate Finder"))
            
            # Update menu items if they exist
            if hasattr(self, 'file_menu') and self.file_menu:
                self.file_menu.setTitle(self.tr("File"))
                
            if hasattr(self, 'open_action') and self.open_action:
                self.open_action.setText(self.tr("Open"))
                self.open_action.setStatusTip(self.tr("Open a folder to scan for duplicate PDFs"))
                
            if hasattr(self, 'exit_action') and self.exit_action:
                self.exit_action.setText(self.tr("Exit"))
                
            # Update Edit menu
            if hasattr(self, 'edit_menu'):
                self.edit_menu.setTitle(self.tr("Edit"))
                
            # Update View menu
            if hasattr(self, 'view_menu'):
                self.view_menu.setTitle(self.tr("View"))
                
            # Update Tools menu and its items
            if hasattr(self, 'tools_menu'):
                self.tools_menu.setTitle(self.tr("Tools"))
                
                if hasattr(self, 'language_menu'):
                    self.language_menu.setTitle(self.tr("Language"))
                    
                    # Update language action texts
                    if hasattr(self, 'language_group'):
                        for action in self.language_group.actions():
                            if hasattr(action, 'data') and action.data():
                                lang_code = action.data()
                                action.setText(self.tr(self.translator.language_name(lang_code)))
                                
            # Update Help menu
            if hasattr(self, 'help_menu'):
                self.help_menu.setTitle(self.tr("Help"))
                
                if hasattr(self, 'about_action'):
                    self.about_action.setText(self.tr("About"))
                    
                if hasattr(self, 'documentation_action'):
                    self.documentation_action.setText(self.tr("Documentation"))
                    
                if hasattr(self, 'sponsor_action'):
                    self.sponsor_action.setText(self.tr("Sponsor"))
                
        except RuntimeError as e:
            # Catch and log any RuntimeError that might occur if Qt objects are deleted
            if 'deleted' in str(e):
                logger.debug("Qt object deleted during retranslate_ui")
                return
            raise
            
    def change_language(self, language_code: str):
        """Change the application language.
        
        Args:
            language_code: Two-letter language code (e.g., 'en', 'it')
        """
        if language_code != self.translator.current_language:
            # Update the translator
            self.translator.load_language(language_code)
            
            # Update the application settings
            self.app_settings['language'] = language_code
            self.save_settings()
            
            # Update the checked state of the language actions
            if hasattr(self, 'language_group'):
                for action in self.language_group.actions():
                    if action.data() == language_code:
                        action.setChecked(True)
                    # Update action text in case it contains translated text
                    if hasattr(action, 'data') and action.data():
                        action.setText(self.tr(self.translator.language_name(action.data())))
            
            # Retranslate the UI
            self.retranslate_ui()
            
            # Update all dynamic text in the UI
            self.update_ui_text()
            
            # Emit signal to notify other components
            self.language_changed.emit()
            
            # Show a message to inform the user that the language has been changed
            QMessageBox.information(
                self,
                self.tr("Language Changed"),
                self.tr("The application language has been changed successfully.")
            )
    
    def update_ui_text(self):
        """Update all UI text elements that need to be retranslated."""
        # Update buttons if they exist
        if hasattr(self, 'scan_button'):
            self.scan_button.setText(self.tr("Scan"))
        
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setText(self.tr("Cancel"))
            
        if hasattr(self, 'settings_button'):
            self.settings_button.setText(self.tr("Settings"))
            
        if hasattr(self, 'select_all_action'):
            self.select_all_action.setText(self.tr("Select All"))
            
        if hasattr(self, 'deselect_all_action'):
            self.deselect_all_action.setText(self.tr("Deselect All"))
        
        # Update labels if they exist
        if hasattr(self, 'status_label'):
            self.status_label.setText(self.tr("Ready"))
            
        if hasattr(self, 'progress_label'):
            self.progress_label.setText(self.tr("Progress:"))
            
        if hasattr(self, 'search_box') and hasattr(self.search_box, 'setPlaceholderText'):
            self.search_box.setPlaceholderText(self.tr("Search duplicates..."))
        
        # Update table headers if the table exists
        if hasattr(self, 'results_table'):
            headers = [
                self.tr("File"),
                self.tr("Size"),
                self.tr("Pages"),
                self.tr("Similarity"),
                self.tr("Path")
            ]
            self.results_table.setHorizontalHeaderLabels(headers)
            
        # Update menu items
        if hasattr(self, 'file_menu'):
            self.file_menu.setTitle(self.tr("File"))
            
        if hasattr(self, 'tools_menu'):
            self.tools_menu.setTitle(self.tr("Tools"))
            
        if hasattr(self, 'help_menu'):
            self.help_menu.setTitle(self.tr("Help"))
            
        # Update window title
        self.setWindowTitle(self.tr("PDF Duplicate Finder"))
    
    def __init__(self):
        # Initialize the translator
        translator = Translator(QApplication.instance())
        super().__init__(translator)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Store the translator instance
        self.translator = translator
        
        # Connect to translator's notifier signal
        self.translator.notifier.language_changed.connect(self.retranslate_ui)
        
        # Set up the rest of the UI
        self.setup_ui()
        
        # Register retranslate callback
        self.retranslate_callbacks.append(self.retranslate_ui)
        
        # Initialize file drop handler
        self._file_drop_handler = FileDropHandler(self)
        
        # Initialize settings
        self.settings = QSettings("PDFDuplicateFinder", "PDFDuplicateFinder")
        self.app_settings = {}  # Will be populated in load_settings()
        
        # Initialize variables
        self.duplicate_groups = []
        self.current_group_index = -1
        self.current_file_index = -1
        self.scan_directories = []
        self.scan_thread = None
        self.is_scanning = False
        
        # Initialize managers
        self.recent_manager = RecentFilesManager()
        self.recent_folders_manager = RecentFoldersManager()
        self.scan_manager = ScanManager()
        
        # Initialize UI
        self.init_ui()
        
        # Load settings
        self.load_settings()
        
        # Apply theme
        self.apply_theme()
        
        # Load recent files after UI is fully initialized
        self.load_recent_files()
        
        # Connect signals
        self.scan_manager.scan_completed.connect(self.on_scan_completed)
        self.scan_manager.progress.connect(self.update_progress)
        self.scan_manager.file_processed.connect(self.on_file_processed)
    
    def save_scan_results(self):
        """Save the current scan results to a CSV file."""
        if not hasattr(self, 'duplicate_groups') or not self.duplicate_groups:
            QMessageBox.information(self, "No Results", "No scan results to save.")
            return
            
        # Get the default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"pdf_duplicate_scan_{timestamp}.csv"
        
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scan Results",
            os.path.join(os.path.expanduser("~"), default_filename),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Group', 'File Path', 'Size (bytes)', 'Pages', 
                    'Creation Date', 'Modification Date', 'MD5 Hash'
                ])
                
                # Write data for each duplicate group
                for i, group in enumerate(self.duplicate_groups, 1):
                    for file_info in group:
                        writer.writerow([
                            i,  # Group number
                            file_info.get('path', ''),
                            file_info.get('size', ''),
                            file_info.get('pages', ''),
                            file_info.get('creation_date', ''),
                            file_info.get('modification_date', ''),
                            file_info.get('md5', '')
                        ])
            
            QMessageBox.information(
                self, 
                "Save Successful", 
                f"Scan results saved to:\n{file_path}"
            )
            
        except Exception as e:
            logger.error(f"Error saving scan results: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save scan results:\n{str(e)}"
            )
    
    def load_scan_results(self):
        """Load scan results from a CSV file."""
        # Open file dialog to select the CSV file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Scan Results",
            os.path.expanduser("~"),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Reset current state
                self.duplicate_groups = []
                current_group = -1
                
                # Read data row by row
                for row in reader:
                    group_num = int(row.get('Group', '0'))
                    
                    # Create a new group if needed
                    if group_num > current_group:
                        self.duplicate_groups.append([])
                        current_group = group_num
                    
                    # Add file info to the current group
                    file_info = {
                        'path': row.get('File Path', ''),
                        'size': int(row.get('Size (bytes)', 0)),
                        'pages': int(row.get('Pages', 0)),
                        'creation_date': row.get('Creation Date', ''),
                        'modification_date': row.get('Modification Date', ''),
                        'md5': row.get('MD5 Hash', '')
                    }
                    self.duplicate_groups[-1].append(file_info)
            
            # Update the UI with the loaded results
            if hasattr(self, 'duplicates_view') and self.duplicate_groups:
                self.current_group_index = 0
                self.current_file_index = 0
                self.update_duplicates_view()
                self.update_ui_state()
                
                QMessageBox.information(
                    self,
                    "Load Successful",
                    f"Successfully loaded {len(self.duplicate_groups)} duplicate groups from:\n{file_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "No Valid Data",
                    "The selected file does not contain valid scan results."
                )
                
        except Exception as e:
            logger.error(f"Error loading scan results: {e}")
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load scan results:\n{str(e)}"
            )
    
    def filter_duplicates(self, search_text):
        """
        Filter the duplicate files based on the search text.
        
        Args:
            search_text (str): The text to search for in file paths
        """
        if not hasattr(self, 'duplicates_view') or not hasattr(self, 'duplicate_groups'):
            return
            
        # If search text is empty, show all duplicates
        if not search_text.strip():
            self.update_duplicates_view()
            return
            
        # Convert search text to lowercase for case-insensitive search
        search_text = search_text.lower()
        
        # Filter duplicate groups where at least one file matches the search
        filtered_groups = []
        for group in self.duplicate_groups:
            # Check if any file in the group matches the search
            matching_files = [
                file_info for file_info in group 
                if search_text in file_info.get('path', '').lower()
            ]
            if matching_files:
                filtered_groups.append(matching_files)
        
        # Update the view with filtered results
        if hasattr(self, 'duplicates_view'):
            self.duplicates_view.clear()
            
            if not filtered_groups:
                item = QListWidgetItem("No matching files found.")
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                self.duplicates_view.addItem(item)
                return
                
            for i, group in enumerate(filtered_groups, 1):
                # Add group header
                group_item = QListWidgetItem(f"Group {i} - {len(group)} duplicate(s)")
                group_item.setBackground(QColor(64, 64, 64))
                group_item.setForeground(QColor(255, 255, 255))
                group_item.setFlags(group_item.flags() & ~Qt.ItemIsSelectable)
                self.duplicates_view.addItem(group_item)
                
                # Add files in the group
                for file_info in group:
                    file_path = file_info.get('path', 'Unknown')
                    file_name = os.path.basename(file_path)
                    item = QListWidgetItem(f"  {file_name}")
                    item.setData(Qt.UserRole, file_info)
                    self.duplicates_view.addItem(item)
    
    def on_files_dropped(self, file_paths):
        """
        Handle files that are dropped onto the application window.
        
        Args:
            file_paths (list): List of file paths that were dropped
        """
        if not file_paths:
            return
            
        # Filter for PDF files only
        pdf_files = [path for path in file_paths if path.lower().endswith('.pdf')]
        
        if not pdf_files:
            QMessageBox.information(
                self,
                "No PDF Files",
                "No PDF files were found in the dropped items."
            )
            return
            
        # If we have exactly one PDF, we can either scan its folder or ask the user
        if len(pdf_files) == 1:
            reply = QMessageBox.question(
                self,
                "Scan Options",
                f"Do you want to scan the folder containing '{os.path.basename(pdf_files[0])}'?\n\n"
                "Click 'Yes' to scan the parent folder, or 'No' to scan just this file.",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Scan the parent folder
                folder_path = os.path.dirname(pdf_files[0])
                self.scan_directories = [folder_path]
                self.start_scan()
                return
            elif reply == QMessageBox.No:
                # Scan just this file
                self.scan_directories = pdf_files
                self.start_scan()
                return
            else:
                # User cancelled
                return
        
        # For multiple PDFs, scan all of them
        self.scan_directories = pdf_files
        self.start_scan()
    
    def load_settings(self):
        """Load application settings from QSettings."""
        try:
            # Load window geometry
            self.restoreGeometry(self.settings.value("geometry", QByteArray()))
            
            # Load window state (toolbars, dock widgets, etc.)
            self.restoreState(self.settings.value("windowState", QByteArray()))
            
            # Load recent files and folders
            if hasattr(self, 'recent_manager') and hasattr(self.recent_manager, 'load'):
                self.recent_manager.load()
            if hasattr(self, 'recent_folders_manager') and hasattr(self.recent_folders_manager, 'load'):
                self.recent_folders_manager.load()
            
            # Load application settings
            self.app_settings = {
                'theme': self.settings.value('theme', 'dark'),
                'language': self.settings.value('language', 'en'),
                'last_directory': self.settings.value('last_directory', os.path.expanduser('~')),
                'check_updates': self.settings.value('check_updates', True, type=bool),
                'show_hidden': self.settings.value('show_hidden', False, type=bool),
                'min_file_size': self.settings.value('min_file_size', 1024, type=int),  # 1KB
                'max_file_size': self.settings.value('max_file_size', 1024 * 1024 * 1024, type=int),  # 1GB
                'compare_method': self.settings.value('compare_method', 'content'),  # 'content' or 'metadata'
                'thread_count': self.settings.value('thread_count', 4, type=int),
                'auto_save_results': self.settings.value('auto_save_results', True, type=bool),
                'auto_load_last': self.settings.value('auto_load_last', False, type=bool)
            }
            
            # Apply theme
            self.apply_theme()
            
            # Apply language if available
            if 'language' in self.app_settings and hasattr(self, 'translator'):
                self.translator.load_language(self.app_settings['language'])
            
            logger.info("Settings loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            # Reset to default settings on error
            self.app_settings = {
                'theme': 'dark',
                'language': 'en',
                'last_directory': os.path.expanduser('~'),
                'check_updates': True,
                'show_hidden': False,
                'min_file_size': 1024,  # 1KB
                'max_file_size': 1024 * 1024 * 1024,  # 1GB
                'compare_method': 'content',
                'thread_count': 4,
                'auto_save_results': True,
                'auto_load_last': True
            }
    
    def apply_theme(self, theme=None):
        """
        Apply the selected theme to the application.
        
        Args:
            theme (str, optional): Theme name to apply. If None, uses the theme from app_settings.
        """
        if theme is None:
            theme = self.app_settings.get('theme', 'dark')
            
        # Save the theme to settings
        self.app_settings['theme'] = theme
        self.settings.setValue('theme', theme)
        
        # Define color palettes for different themes
        if theme == 'dark':
            # Dark theme colors
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            
            # Apply the palette
            QApplication.setPalette(palette)
            
            # Additional style tweaks for dark theme
            self.setStyleSheet("""
                QToolTip { 
                    color: #ffffff; 
                    background-color: #2a82da; 
                    border: 1px solid white; 
                }
                QMenu::item:selected { 
                    background-color: #2a82da; 
                }
                QStatusBar { 
                    background-color: #353535; 
                    color: white; 
                }
            """)
            
        elif theme == 'light':
            # Light theme (system default)
            QApplication.setPalette(QApplication.style().standardPalette())
            self.setStyleSheet("""
                QToolTip { 
                    border: 1px solid #76797C; 
                    background-color: #f0f0f0; 
                    color: #000000; 
                }
                QMenu::item:selected { 
                    background-color: #2a82da; 
                    color: white;
                }
            """)
            
        # Force a style refresh
        self.update()
    
    def load_recent_files(self):
        """Load the list of recently accessed files and update the UI."""
        try:
            # Clear the recent files menu
            if hasattr(self, 'recent_menu'):
                self.recent_menu.clear()
            else:
                # If the menu doesn't exist yet, create it
                menubar = self.menuBar()
                file_menu = menubar.findChild(QMenu, "file_menu")
                if file_menu:
                    self.recent_menu = file_menu.addMenu(self.tr("Recent Files"))
                else:
                    logger.warning("Could not find File menu to add Recent Files submenu")
                    return
            
            # Get recent files from the manager
            recent_files = []
            if hasattr(self, 'recent_manager') and hasattr(self.recent_manager, 'get_recent_files'):
                recent_files = self.recent_manager.get_recent_files()
            
            # Add recent files to the menu
            if not recent_files:
                no_files_action = QAction(self.tr("No recent files"), self)
                no_files_action.setEnabled(False)
                self.recent_menu.addAction(no_files_action)
                return
            
            # Add each recent file to the menu
            for i, file_path in enumerate(recent_files, 1):
                # Show a maximum of 10 recent files
                if i > 10:
                    break
                    
                # Create a user-friendly display name
                display_name = f"&{i} {os.path.basename(file_path)}"
                action = QAction(display_name, self)
                action.setData(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
                self.recent_menu.addAction(action)
            
            # Add a separator and clear action if we have recent files
            if recent_files:
                self.recent_menu.addSeparator()
                clear_action = QAction(self.tr("Clear Recent Files"), self)
                clear_action.triggered.connect(self.clear_recent_files)
                self.recent_menu.addAction(clear_action)
        
        except Exception as e:
            logger.error(f"Error loading recent files: {e}")
    
    def open_recent_file(self, file_path):
        """
        Open a recently accessed file.
        
        Args:
            file_path (str): Path to the file to open
        """
        try:
            if not os.path.exists(file_path):
                QMessageBox.warning(
                    self,
                    "File Not Found",
                    f"The file '{os.path.basename(file_path)}' could not be found."
                )
                # Remove the file from recent files if it doesn't exist
                if hasattr(self, 'recent_manager') and hasattr(self.recent_manager, 'remove_recent_file'):
                    self.recent_manager.remove_recent_file(file_path)
                    self.load_recent_files()  # Refresh the recent files menu
                return
            
            # Check if the file is a directory or a file
            if os.path.isdir(file_path):
                self.scan_directories = [file_path]
            else:
                self.scan_directories = [os.path.dirname(file_path)]
                
            # Start the scan
            self.start_scan()
            
            # Update the recent files list
            if hasattr(self, 'recent_manager') and hasattr(self.recent_manager, 'add_recent_file'):
                self.recent_manager.add_recent_file(file_path)
                self.load_recent_files()  # Refresh the recent files menu
                
        except Exception as e:
            logger.error(f"Error opening recent file '{file_path}': {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Could not open file '{os.path.basename(file_path)}': {str(e)}"
            )
    
    def clear_recent_files(self):
        """Clear the list of recently accessed files."""
        try:
            if hasattr(self, 'recent_manager') and hasattr(self.recent_manager, 'clear_recent_files'):
                self.recent_manager.clear_recent_files()
                self.load_recent_files()  # Refresh the recent files menu
        except Exception as e:
            logger.error(f"Error clearing recent files: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Could not clear recent files: {str(e)}"
            )
    
    def on_scan_completed(self, results):
        """
        Handle the completion of a scan operation.
        
        Args:
            results: The results of the scan operation
        """
        try:
            # Enable UI elements
            self.scan_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # Update status
            self.status_bar.showMessage("Scan completed")
            
            # Process results if any
            if results and hasattr(results, 'duplicate_groups'):
                self.duplicate_groups = results.duplicate_groups
                self.current_group_index = 0
                self.current_file_index = 0
                
                # Update the UI with the first group of duplicates
                if self.duplicate_groups:
                    self.update_duplicates_view()
                    
                    # Show summary
                    total_duplicates = sum(len(group) for group in self.duplicate_groups)
                    total_groups = len(self.duplicate_groups)
                    self.status_bar.showMessage(
                        f"Found {total_duplicates} duplicate files in {total_groups} groups"
                    )
                    
                    # Auto-save results if enabled
                    if self.app_settings.get('auto_save_results', False):
                        self.save_scan_results()
                else:
                    self.status_bar.showMessage("No duplicate files found")
                    QMessageBox.information(self, "No Duplicates", "No duplicate PDF files were found.")
            
            # Re-enable UI elements
            self.update_ui_state()
            
        except Exception as e:
            logger.error(f"Error processing scan completion: {e}")
            self.status_bar.showMessage("Error processing scan results")
            QMessageBox.critical(
                self,
                "Scan Error",
                f"An error occurred while processing the scan results: {str(e)}"
            )
    
    def update_progress(self, current, total, message):
        """
        Update the progress bar and status message during a scan.
        
        Args:
            current (int): Current progress value
            total (int): Total value for completion
            message (str): Status message to display
        """
        try:
            # Update progress bar if it exists
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setMaximum(total)
                self.progress_bar.setValue(current)
                
                # Calculate percentage
                if total > 0:
                    percent = int((current / total) * 100)
                    self.progress_bar.setFormat(f"%p% - {message}")
            
            # Update status bar message
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(message)
                
            # Process events to update the UI
            QApplication.processEvents()
            
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
    
    def on_file_processed(self, file_path, result):
        """
        Handle the signal when a file has been processed during a scan.
        
        Args:
            file_path (str): Path to the processed file
            result (dict): Result of the file processing
        """
        try:
            # Update the log with the processed file
            logger.debug(f"Processed file: {file_path}")
            
            # Update the status bar with the current file being processed
            if hasattr(self, 'status_bar'):
                file_name = os.path.basename(file_path)
                self.status_bar.showMessage(f"Processing: {file_name}")
            
            # Update the file list or log if needed
            if hasattr(self, 'log_view') and self.log_view:
                self.log_view.append(f"Processed: {file_path}")
            
            # Process events to keep the UI responsive
            QApplication.processEvents()
            
        except Exception as e:
            logger.error(f"Error handling processed file {file_path}: {e}")
    
    def init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1400, 900)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu bar
        self.create_menus()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar with progress
        self.status_bar = QStatusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.hide()
        
        self.status_label = QLabel(self.tr("Ready"))
        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status_bar)
        
        # Initialize drag and drop
        self._file_drop_handler.set_file_drop_callback(self.on_files_dropped)
        self._file_drop_handler.set_accepted_extensions(['.pdf'])
        
        # Update UI state
        self.update_ui_state()
    
    def create_menus(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        self.scan_folder_action = QAction("Scan Folder...", self)
        self.scan_folder_action.triggered.connect(self.on_scan_folder)
        file_menu.addAction(self.scan_folder_action)
        
        file_menu.addSeparator()
        
        # Save results action
        self.save_results_action = QAction("Save Results...", self)
        self.save_results_action.triggered.connect(self.save_scan_results)
        self.save_results_action.setShortcut("Ctrl+S")
        file_menu.addAction(self.save_results_action)
        
        # Load results action
        self.load_results_action = QAction("Load Results...", self)
        self.load_results_action.triggered.connect(self.load_scan_results)
        self.load_results_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.load_results_action)
        
        # Add Recent Folders submenu
        file_menu.addSeparator()
        self.recent_menu = file_menu.addMenu(self.tr("Recent Folders"))
        file_menu.addSeparator()
        
        self.exit_action = QAction(self.tr("Exit"))
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu(self.tr("Edit"))
        
        self.settings_action = QAction("Settings...", self)
        self.settings_action.triggered.connect(self.on_settings)
        edit_menu.addAction(self.settings_action)
        
        # Tools menu (moved from MainWindow)
        self.tools_menu = menubar.addMenu(self.tr("Tools"))
        
        # Add Language submenu to Tools
        self.language_menu = self.tools_menu.addMenu(self.tr("Language"))
        
        # Add language actions
        self.language_group = QActionGroup(self)
        for lang_code in self.translator.available_languages():
            action = QAction(self.translator.language_name(lang_code), self)
            action.setCheckable(True)
            action.setData(lang_code)
            action.triggered.connect(lambda checked, code=lang_code: self.change_language(code))
            self.language_menu.addAction(action)
            self.language_group.addAction(action)
        
        # Set current language from settings or system default
        current_lang = self.app_settings.get('language')
        if not current_lang or current_lang not in self.translator.available_languages():
            current_lang = QLocale.system().name()[:2]  # Get 2-letter language code
            if current_lang not in self.translator.available_languages():
                current_lang = 'en'  # Default to English
        
        # Update the checked state and load the language
        for action in self.language_group.actions():
            if action.data() == current_lang:
                action.setChecked(True)
                # Ensure the language is loaded
                self.translator.load_language(current_lang)
                break
                
        # Add separator
        self.tools_menu.addSeparator()
        
        # Check for Updates
        self.update_action = QAction("Check for Updates...", self)
        self.update_action.triggered.connect(self.on_check_updates)
        self.tools_menu.addAction(self.update_action)
        
        # View Log action
        self.view_log_action = QAction("View Log", self)
        self.view_log_action.triggered.connect(self.on_view_log)
        self.tools_menu.addAction(self.view_log_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        self.prev_group_action = QAction("Previous Group", self)
        self.prev_group_action.triggered.connect(self.on_prev_group)
        view_menu.addAction(self.prev_group_action)
        
        self.next_group_action = QAction("Next Group", self)
        self.next_group_action.triggered.connect(self.on_next_group)
        view_menu.addAction(self.next_group_action)
        
        view_menu.addSeparator()
        
        self.prev_file_action = QAction("Previous File", self)
        self.prev_file_action.triggered.connect(self.on_prev_file)
        view_menu.addAction(self.prev_file_action)
        
        self.next_file_action = QAction("Next File", self)
        self.next_file_action.triggered.connect(self.on_next_file)
        view_menu.addAction(self.next_file_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # View Help action
        self.help_action = QAction("Help", self)
        self.help_action.setShortcut("F1")
        self.help_action.triggered.connect(self.on_help)
        help_menu.addAction(self.help_action)

         # About action
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.on_about)
        help_menu.addAction(self.about_action)
        
        help_menu.addSeparator()
        
        # Sponsor action
        self.sponsor_action = QAction("Sponsor", self)
        self.sponsor_action.triggered.connect(self.on_sponsor)
        help_menu.addAction(self.sponsor_action)
        
    def create_toolbar(self):
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setObjectName("mainToolbar")  # Add this line to set objectName
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Import QStyle at the top of the file if not already imported
        from PySide6.QtWidgets import QStyle
        
        # Scan button
        self.scan_button = QAction("Scan Folder", self)
        self.scan_button.triggered.connect(self.on_scan_folder)
        self.scan_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.scan_button.setShortcut("Ctrl+O")
        toolbar.addAction(self.scan_button)
        
        # Stop scan button
        self.stop_scan_button = QAction("Stop Scan", self)
        self.stop_scan_button.triggered.connect(self.stop_scan)
        self.stop_scan_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        self.stop_scan_button.setShortcut("Escape")
        self.stop_scan_button.setEnabled(False)
        toolbar.addAction(self.stop_scan_button)
        
        # Add separator
        toolbar.addSeparator()
        
        # Navigation buttons
        self.prev_group_action = QAction("Previous Group", self)
        self.prev_group_action.triggered.connect(self.on_prev_group)
        self.prev_group_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.prev_group_action.setShortcut("Alt+Up")
        self.prev_group_action.setEnabled(False)
        toolbar.addAction(self.prev_group_action)
        
        self.next_group_action = QAction("Next Group", self)
        self.next_group_action.triggered.connect(self.on_next_group)
        self.next_group_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        self.next_group_action.setShortcut("Alt+Down")
        self.next_group_action.setEnabled(False)
        toolbar.addAction(self.next_group_action)
        
        # Add another separator
        toolbar.addSeparator()
        
        # Select All button
        self.select_all_action = QAction("Select All", self)
        self.select_all_action.triggered.connect(self.select_all)
        self.select_all_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton))
        self.select_all_action.setShortcut("Ctrl+A")
        toolbar.addAction(self.select_all_action)
        
        # Deselect All button
        self.deselect_all_action = QAction("Deselect All", self)
        self.deselect_all_action.triggered.connect(self.deselect_all)
        self.deselect_all_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogNoButton))
        self.deselect_all_action.setShortcut("Ctrl+D")
        toolbar.addAction(self.deselect_all_action)
        
        # Add separator
        toolbar.addSeparator()
        
        # Delete button
        self.delete_action = QAction("Delete Selected", self)
        self.delete_action.triggered.connect(self.on_delete_file)
        self.delete_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.delete_action.setShortcut("Del")
        self.delete_action.setEnabled(False)
        toolbar.addAction(self.delete_action)
        
        toolbar.addSeparator()
        
        self.prev_file_button = QAction("Previous File", self)
        self.prev_file_button.triggered.connect(self.on_prev_file)
        self.prev_file_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        toolbar.addAction(self.prev_file_button)
        
        self.next_file_button = QAction("Next File", self)
        self.next_file_button.triggered.connect(self.on_next_file)
        self.next_file_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        toolbar.addAction(self.next_file_button)
        
        toolbar.addSeparator()
        
        # Action buttons
        self.keep_button = QAction("Keep", self)
        self.keep_button.triggered.connect(self.on_keep_file)
        self.keep_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        toolbar.addAction(self.keep_button)
        
        self.delete_button = QAction("Delete", self)
        self.delete_button.triggered.connect(self.on_delete_file)
        self.delete_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        toolbar.addAction(self.delete_button)
        
        # Settings button
        toolbar.addSeparator()
        self.settings_button = QAction("Settings", self)
        self.settings_button.triggered.connect(self.on_settings)
        self.settings_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        toolbar.addAction(self.settings_button)
    
    def create_main_content(self):
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - duplicate groups
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search duplicates...")
        self.search_box.textChanged.connect(self.filter_duplicates)
        left_layout.addWidget(self.search_box)
        
        # Duplicate groups tree
        self.duplicates_view = DuplicateFilesView()
        self.duplicates_view.setSelectionMode(DuplicateFilesView.SelectionMode.ExtendedSelection)
        self.duplicates_view.doubleClicked.connect(self.on_duplicate_double_clicked)
        self.duplicates_view.customContextMenuRequested.connect(self.show_duplicate_context_menu)
        self.duplicates_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Connect selection changed signal
        selection_model = self.duplicates_view.selectionModel()
        if selection_model:
            selection_model.selectionChanged.connect(self.on_file_selection_changed)
        
        left_layout.addWidget(self.duplicates_view)
        left_panel.setLayout(left_layout)
        
        # Right panel - splitter for file list and preview
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # File details panel
        self.file_details = QTreeWidget()
        self.file_details.setHeaderLabels(["Property", "Value"])
        self.file_details.setColumnCount(2)
        self.file_details.setAlternatingRowColors(True)
        self.file_details.header().setSectionResizeMode(0, self.file_details.header().ResizeMode.ResizeToContents)
        right_layout.addWidget(self.file_details, 1)
        
        # Preview area
        self.preview_widget = PDFPreviewWidget()
        right_layout.addWidget(self.preview_widget, 2)
        
        right_panel.setLayout(right_layout)
        
        # Add widgets to main splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 600])
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        
        # Add to main layout
        self.centralWidget().layout().addWidget(main_splitter)
    
    def on_prev_group(self):
        """Navigate to the previous group of duplicates."""
        if self.current_group_index > 0:
            self.current_group_index -= 1
            self.current_file_index = 0
            self.show_current_group()
            self.update_ui_state()
    
    def on_next_group(self):
        """Navigate to the next group of duplicates."""
        if self.current_group_index < len(self.duplicate_groups) - 1:
            self.current_group_index += 1
            self.current_file_index = 0
            self.show_current_group()
            self.update_ui_state()
    
    def on_prev_file(self):
        """Navigate to the previous file in the current group."""
        if self.current_group_index >= 0 and self.current_file_index > 0:
            self.current_file_index -= 1
            self.show_current_file()
            
            # Update the selection in the view
            model = self.duplicates_view.model()
            if model and hasattr(model, 'setCurrentFile'):
                model.setCurrentFile(self.current_group_index, self.current_file_index)
                
                # Select the item in the view
                index = model.index(self.current_file_index, 0)
                if index.isValid():
                    self.duplicates_view.setCurrentIndex(index)
    
    def select_all(self):
        """Select all files in the current group."""
        if hasattr(self, 'duplicates_view') and self.duplicates_view.model():
            model = self.duplicates_view.model()
            selection_model = self.duplicates_view.selectionModel()
            if selection_model and model.rowCount() > 0:
                # Select all rows
                selection = QItemSelection()
                first_idx = model.index(0, 0)
                last_idx = model.index(model.rowCount() - 1, 0)
                selection.select(first_idx, last_idx)
                selection_model.select(selection, QItemSelectionModel.SelectionFlag.Select)
                
    def deselect_all(self):
        """Deselect all files in the current group."""
        if hasattr(self, 'duplicates_view') and self.duplicates_view.selectionModel():
            self.duplicates_view.selectionModel().clearSelection()
    
    def on_next_file(self):
        """Navigate to the next file in the current group."""
        if (self.current_group_index >= 0 and 
            self.current_file_index < len(self.duplicate_groups[self.current_group_index]) - 1):
            self.current_file_index += 1
            self.show_current_file()
            
            # Update the selection in the view
            model = self.duplicates_view.model()
            if model and hasattr(model, 'setCurrentFile'):
                model.setCurrentFile(self.current_group_index, self.current_file_index)
                
                # Select the item in the view
                index = model.index(self.current_file_index, 0)
                if index.isValid():
                    self.duplicates_view.setCurrentIndex(index)
    
    def on_scan_folder(self):
        """Open a dialog to select a folder to scan for duplicate PDFs."""
        # Get the last used directory from settings or use home directory
        last_dir = self.app_settings.get('last_scan_directory', os.path.expanduser('~'))
        
        folder = QFileDialog.getExistingDirectory(
            self, 
            self.tr("Select Folder to Scan"),
            dir=last_dir,
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if folder:
            # Normalize the folder path
            folder = os.path.normpath(folder)
            # Only add to recent folders if the folder exists
            if os.path.isdir(folder):
                self.recent_folders_manager.add_recent_folder(folder)
                # Update the recent folders menu
                try:
                    self.load_recent_files()
                except Exception as e:
                    logger.warning(f"Failed to update recent folders menu: {str(e)}")
                
                # Save the last used directory
                self.app_settings['last_scan_directory'] = os.path.dirname(folder) if os.path.isfile(folder) else folder
                self.save_settings()
            
            # Start the scan with the selected folder
            self.scan_directories = [folder]
            self.start_scan()
    
    def on_duplicate_double_clicked(self, index):
        """Handle double-clicking on a file in the duplicates view."""
        if not index.isValid():
            return
            
        # Get the item data
        model = self.duplicates_view.model()
        item = model.data(index, Qt.ItemDataRole.UserRole)
        
        # If it's a file item, open it with the default application
        if hasattr(item, 'file_path'):
            try:
                import platform
                import subprocess
                
                if platform.system() == 'Windows':
                    os.startfile(item.file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.Popen(['open', item.file_path])
                else:  # Linux and others
                    subprocess.Popen(['xdg-open', item.file_path])
            except Exception as e:
                logger.error(f"Error opening file: {e}")
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")
    
    def show_duplicate_context_menu(self, position):
        """Show context menu for the duplicates view."""
        # Get the selected indexes
        selected_indexes = self.duplicates_view.selectedIndexes()
        if not selected_indexes:
            return
            
        # Get the first selected item
        index = selected_indexes[0]
        if not index.isValid():
            return
            
        # Get the item data
        model = self.duplicates_view.model()
        item = model.data(index, Qt.ItemDataRole.UserRole)
        
        # Create the context menu
        menu = QMenu()
        
        # Add actions based on the selected item
        if hasattr(item, 'file_path'):
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda: self.on_duplicate_double_clicked(index))
            
            show_in_folder_action = menu.addAction("Show in Folder")
            show_in_folder_action.triggered.connect(lambda: self.show_in_folder(item.file_path))
            
            menu.addSeparator()
            
            keep_action = menu.addAction("Keep This File")
            keep_action.triggered.connect(self.on_keep_file)
            
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self.on_delete_file)
        
        # Show the context menu
        menu.exec_(self.duplicates_view.viewport().mapToGlobal(position))
    
    def show_in_folder(self, file_path):
        """Open the file's containing folder in the system file manager."""
        try:
            import platform
            import subprocess
            import os
            
            file_path = os.path.normpath(file_path)
            
            if platform.system() == 'Windows':
                os.startfile(os.path.dirname(file_path))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', '--', os.path.dirname(file_path)])
            else:  # Linux and others
                subprocess.Popen(['xdg-open', os.path.dirname(file_path)])
        except Exception as e:
            logger.error(f"Error showing file in folder: {e}")
            QMessageBox.critical(self, "Error", f"Could not open folder: {e}")
    
    def on_keep_file(self):
        """Mark selected files as originals to keep."""
        selected_indexes = self.duplicates_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.information(self, "No Selection", "Please select files to keep.")
            return
            
        # Get unique file paths from the selection
        files_to_keep = set()
        model = self.duplicates_view.model()
        
        for index in selected_indexes:
            if index.isValid():
                item = model.data(index, Qt.ItemDataRole.UserRole)
                if hasattr(item, 'file_path'):  # It's a DuplicateFileItem
                    files_to_keep.add(item.file_path)
        
        if not files_to_keep:
            return
        
        # Mark files as originals in the model
        if model:
            model.mark_as_original(list(files_to_keep))
            self.status_label.setText(f"Marked {len(files_to_keep)} file(s) as originals")
    
    def on_delete_file(self):
        """Handle file deletion with confirmation dialog."""
        # Get the current selection from the duplicates view
        selected_indexes = self.duplicates_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.information(self, "No Selection", "Please select files to delete.")
            return
        
        # Get unique file paths from the selection
        files_to_delete = set()
        model = self.duplicates_view.model()
        
        for index in selected_indexes:
            if index.isValid():
                item = model.data(index, Qt.ItemDataRole.UserRole)
                if hasattr(item, 'file_path'):  # It's a DuplicateFileItem
                    files_to_delete.add(item.file_path)
        
        if not files_to_delete:
            return
        
        # Convert to list for the dialog
        files_list = list(files_to_delete)
        
        # Delete the files using the delete_files function which shows its own confirmation
        success_count, failed_count = delete_files(files_list, parent=self)
        
        # Update the model if any files were successfully deleted
        if success_count > 0:
            # Get the list of successfully deleted files
            # Note: The current implementation of delete_files doesn't return which files succeeded/failed
            # So we'll just remove all the files we tried to delete
            # In a more robust implementation, we would track which specific files were deleted
            
            # Remove deleted files from the model
            if hasattr(model, 'remove_files'):
                model.remove_files(files_list)
            
            # Update the duplicate groups
            self.duplicate_groups = [
                [f for f in group if f.file_path not in files_list]
                for group in self.duplicate_groups
            ]
            
            # Remove empty groups
            self.duplicate_groups = [g for g in self.duplicate_groups if len(g) > 1]
            
            # Update the model
            if hasattr(self, 'duplicates_view'):
                model = DuplicateFilesModel(self.duplicate_groups)
                self.duplicates_view.setModel(model)
            
            # Update the UI state
            self.update_ui_state()
    
    def on_file_selection_changed(self):
        """Handle selection changes in the duplicates view."""
        selected_indexes = self.duplicates_view.selectedIndexes()
        if not selected_indexes:
            return
            
        # Get the first selected item
        index = selected_indexes[0]
        if not index.isValid():
            return
            
        # Get the item data
        model = self.duplicates_view.model()
        item = model.data(index, Qt.ItemDataRole.UserRole)
        
        # Update preview if it's a file item and preview_widget exists
        if hasattr(item, 'file_path'):
            # Update preview widget if available
            if hasattr(self, 'preview_widget'):
                try:
                    self.preview_widget.load_pdf(item.file_path)
                except Exception as e:
                    logger.error(f"Error loading PDF preview: {e}")
                    if hasattr(self.preview_widget, 'clear'):
                        self.preview_widget.clear()
            
            # Update file details if available
            if hasattr(self, 'file_details') and hasattr(self.file_details, 'set_file'):
                try:
                    self.file_details.set_file(item.file_path)
                except Exception as e:
                    logger.error(f"Error updating file details: {e}")
        else:
            # Clear preview and details if no file path
            if hasattr(self, 'preview_widget') and hasattr(self.preview_widget, 'clear'):
                self.preview_widget.clear()
            if hasattr(self, 'file_details') and hasattr(self.file_details, 'clear'):
                self.file_details.clear()
    
    def on_keep_file(self):
        """Mark selected files as originals to keep."""
        selected_indexes = self.duplicates_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.information(self, "No Selection", "Please select files to keep.")
            return
            
        # Get unique file paths from the selection
        files_to_keep = set()
        model = self.duplicates_view.model()
        
        for index in selected_indexes:
            if index.isValid():
                item = model.data(index, Qt.ItemDataRole.UserRole)
                if hasattr(item, 'file_path'):  # It's a DuplicateFileItem
                    files_to_keep.add(item.file_path)
        
        if not files_to_keep:
            return
        
        # Mark files as originals in the model
        if model:
            model.mark_as_original(list(files_to_keep))
            self.status_label.setText(f"Marked {len(files_to_keep)} file(s) as originals")
    
    def on_delete_file(self):
        """Handle file deletion with confirmation dialog."""
        # Get the current selection from the duplicates view
        selected_indexes = self.duplicates_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.information(self, "No Selection", "Please select files to delete.")
            return
        
        # Get unique file paths from the selection
        files_to_delete = set()
        model = self.duplicates_view.model()
        
        for index in selected_indexes:
            if index.isValid():
                item = model.data(index, Qt.ItemDataRole.UserRole)
                if hasattr(item, 'file_path'):  # It's a DuplicateFileItem
                    files_to_delete.add(item.file_path)
        
        if not files_to_delete:
            return
        
        # Show confirmation dialog
        dialog = DeleteConfirmationDialog(
            file_paths=list(files_to_delete),
            parent=self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Delete the files using the user's choice (from the dialog's checkbox)
            success, failed = delete_files(
                file_paths=list(files_to_delete),
                parent=self,
                use_recycle_bin=not dialog.permanently
            )
            
            # Update the UI based on deletion results
            if success > 0:
                # Remove deleted files from the model
                if model:
                    model.remove_files(list(files_to_delete))
                
                # Update status
                self.status_label.setText(f"Deleted {success} file(s)")
                
                # Refresh the view
                self.show_current_group()
            
            if failed > 0:
                # Show error message for failed deletions
                QMessageBox.warning(
                    self,
                    "Deletion Incomplete",
                    f"Successfully deleted {success} file(s).\n"
                    f"Failed to delete {failed} file(s).\n\n"
                    "Check the log for details."
                )
    def on_settings(self):
        dialog = SettingsDialog(self, self.app_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save settings
            self.app_settings = dialog.get_settings()
            self.save_settings()
            self.apply_theme()
    
    def on_view_log(self):
        """Open the application log file in the default text editor."""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            log_file = os.path.join(log_dir, 'pdf_finder.log')
            
            if not os.path.exists(log_file):
                QMessageBox.information(
                    self,
                    "Log File Not Found",
                    f"Log file not found at:\n{log_file}",
                    QMessageBox.StandardButton.Ok
                )
                return
                
            # Open the log file with the default application
            if sys.platform == 'win32':
                os.startfile(log_file)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{log_file}"')
            else:  # Linux and other Unix-like
                os.system(f'xdg-open "{log_file}"')
                
            logger.info("Opened log file for viewing")
            
        except Exception as e:
            logger.error(f"Error opening log file: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open log file:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
    
    def on_help(self):
        """Show the help dialog."""
        try:
            from app_qt.help import HelpDialog
            help_dialog = HelpDialog(self)
            help_dialog.exec()
        except ImportError as e:
            logger.error(f"Error showing help: {e}")
            QMessageBox.critical(
                self,
                "Error",
                "Could not load help content. Please check the installation.",
                QMessageBox.StandardButton.Ok
            )
    
    def on_check_updates(self):
        """Check for application updates."""
        try:
            from app_qt.updates import UpdateDialog
            from app_qt.version import get_version
            
            self.update_dialog = UpdateDialog(get_version(), self)
            self.update_dialog.finished.connect(self.on_update_check_finished)
            self.update_dialog.show()
            
        except ImportError as e:
            logger.error(f"Error checking for updates: {e}")
            QMessageBox.critical(
                self,
                "Error",
                "Could not check for updates. Please check your internet connection and try again.",
                QMessageBox.StandardButton.Ok
            )
    
    def on_update_check_finished(self, result):
        """Handle the completion of the update check."""
        # Clean up the dialog
        self.update_dialog.deleteLater()
        self.update_dialog = None
    
    def on_sponsor(self):
        """Show the sponsor dialog."""
        try:
            from app_qt.sponsor import SponsorDialog
            sponsor_dialog = SponsorDialog(self)
            sponsor_dialog.exec()
        except ImportError as e:
            logger.error(f"Error showing sponsor dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                "Could not load sponsor information.",
                QMessageBox.StandardButton.Ok
            )
    
    def on_about(self):
        """Show the about dialog."""
        try:
            from app_qt.about import AboutDialog
            about_dialog = AboutDialog(self)
            about_dialog.exec()
        except ImportError as e:
            logger.error(f"Error showing about dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                "Could not load about information.",
                QMessageBox.StandardButton.Ok
            )
    
    def update_ui_state(self):
        """Update the UI state based on the current selection and scan status."""
        has_selection = self.current_group_index >= 0 and self.current_file_index >= 0
        has_groups = len(self.duplicate_groups) > 0
        
        # Enable/disable navigation buttons
        self.prev_group_action.setEnabled(has_groups and self.current_group_index > 0)
        self.next_group_action.setEnabled(has_groups and self.current_group_index < len(self.duplicate_groups) - 1)
        self.prev_file_action.setEnabled(has_selection and self.current_file_index > 0)
        next_file_enabled = has_selection and self.current_file_index < len(self.duplicate_groups[self.current_group_index]) - 1
        self.next_file_action.setEnabled(next_file_enabled)
        
        # Update toolbar buttons
        if hasattr(self, 'prev_group_button'):
            self.prev_group_button.setEnabled(has_groups and self.current_group_index > 0)
        if hasattr(self, 'next_group_button'):
            self.next_group_button.setEnabled(has_groups and self.current_group_index < len(self.duplicate_groups) - 1)
        if hasattr(self, 'prev_file_button'):
            self.prev_file_button.setEnabled(has_selection and self.current_file_index > 0)
        if hasattr(self, 'next_file_button'):
            self.next_file_button.setEnabled(next_file_enabled)
        
        # Update scan-related UI
        if hasattr(self, 'scan_button'):
            self.scan_button.setEnabled(not self.is_scanning)
        if hasattr(self, 'stop_scan_button'):
            self.stop_scan_button.setEnabled(self.is_scanning)
        if hasattr(self, 'delete_action'):
            self.delete_action.setEnabled(has_selection)
        
        # Update status message
        if self.is_scanning:
            status_text = "Scanning..."
        elif has_groups:
            total_duplicates = sum(len(group) - 1 for group in self.duplicate_groups)
            if has_selection:
                current_group = self.duplicate_groups[self.current_group_index]
                status_text = (
                    f"Group {self.current_group_index + 1} of {len(self.duplicate_groups)} | "
                    f"File {self.current_file_index + 1} of {len(current_group)} | "
                    f"Total duplicates: {total_duplicates}"
                )
            else:
                status_text = f"Found {len(self.duplicate_groups)} groups with {total_duplicates} duplicate files"
        else:
            status_text = "Ready. Drop PDF files or folders to scan."
        
        # Update status bar if it exists
        if hasattr(self, 'status_label'):
            self.status_label.setText(status_text)
    
    def show_current_group(self):
        """Update the view to show the current group of duplicates."""
        if not hasattr(self, 'duplicates_view') or not hasattr(self, 'duplicate_groups'):
            return
            
        if 0 <= self.current_group_index < len(self.duplicate_groups):
            # The DuplicateFilesView handles the display of groups and files
            # Just ensure the correct group is selected in the view
            model = self.duplicates_view.model()
            if model and hasattr(model, 'setCurrentGroup'):
                model.setCurrentGroup(self.current_group_index)
                
                # Select the first file in the group
                if model.rowCount() > 0:
                    first_index = model.index(0, 0)
                    self.duplicates_view.setCurrentIndex(first_index)
                    
                    # Update the current file index
                    item = model.data(first_index, Qt.ItemDataRole.UserRole)
    
def show_current_group(self):
    """Update the view to show the current group of duplicates."""
    if not hasattr(self, 'duplicates_view') or not hasattr(self, 'duplicate_groups'):
        return
            
    if 0 <= self.current_group_index < len(self.duplicate_groups):
        # The DuplicateFilesView handles the display of groups and files
        # Just ensure the correct group is selected in the view
        model = self.duplicates_view.model()
        if model and hasattr(model, 'setCurrentGroup'):
            model.setCurrentGroup(self.current_group_index)
            
            # Select the first file in the group
            if model.rowCount() > 0:
                first_index = model.index(0, 0)
                self.duplicates_view.setCurrentIndex(first_index)
                
                # Update the current file index
                item = model.data(first_index, Qt.ItemDataRole.UserRole)
                if hasattr(item, 'file_index'):
                    self.current_file_index = item.file_index
    
def show_current_file(self):
    """Update the view to show the current file within the current group."""
    if not hasattr(self, 'duplicate_groups') or not self.duplicate_groups:
        return
            
    if 0 <= self.current_group_index < len(self.duplicate_groups):
        group = self.duplicate_groups[self.current_group_index]
        if 0 <= self.current_file_index < len(group):
            file_info = group[self.current_file_index]
            
            # Update the preview if available
            if hasattr(self, 'preview_widget'):
                try:
                    self.preview_widget.load_pdf(file_info.file_path)
                except Exception as e:
                    logger.error(f"Error loading PDF preview: {e}")
                    self.preview_widget.clear()
            
            # Update file details if available and has set_file method
            if hasattr(self, 'file_details') and hasattr(self.file_details, 'set_file'):
                try:
                    if hasattr(file_info, 'file_path'):
                        self.file_details.set_file(file_info.file_path)
                    elif isinstance(file_info, dict) and 'file_path' in file_info:
                        self.file_details.set_file(file_info['file_path'])
                except Exception as e:
                    logger.error(f"Error updating file details: {e}")
            
            # Update the UI state
            self.update_ui_state()
    
def on_files_dropped(self, file_paths):
    """Handle files or folders dropped onto the application."""
    if not file_paths:
        return
            
        # Check if we should scan the dropped items
        reply = QMessageBox.question(
            self, 
            "Scan Files", 
            f"Scan {len(file_paths)} dropped items for duplicates?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scan_directories = []
            for path in file_paths:
                if os.path.isfile(path) and path.lower().endswith('.pdf'):
                    # Add the parent directory for single files
                    self.scan_directories.append(os.path.dirname(path))
                elif os.path.isdir(path):
                    self.scan_directories.append(path)
            
            if self.scan_directories:
                self.start_scan()
    
    def start_scan(self, directories=None):
        """Start scanning the specified directories for duplicate PDFs."""
        if directories:
            self.scan_directories = directories
        
        if not self.scan_directories:
            QMessageBox.warning(self, self.tr("No Directories"), self.tr("No directories to scan."))
            return
        
        # Add directories to recent folders if they don't exist
        for directory in self.scan_directories:
            if os.path.isdir(directory):
                self.recent_folders_manager.add_recent_folder(directory)
        
        # Reset UI state
        self.duplicate_groups = []
        self.current_group_index = -1
        self.current_file_index = -1
        
        # Clear UI components
        if hasattr(self, 'duplicates_view'):
            self.duplicates_view.setModel(None)
        if hasattr(self, 'file_details'):
            self.file_details.clear()
        if hasattr(self, 'preview_widget'):
            self.preview_widget.clear()
        
        # Show progress
        self.is_scanning = True
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.setText(self.tr("Scanning for PDF files..."))
        self.update_ui_state()
        
        # Start scan in background
        # Convert threshold from 0-100 scale to 0.0-1.0 scale if needed
        threshold = self.app_settings['threshold']
        if threshold > 1.0:  # If it's on a 0-100 scale
            threshold = threshold / 100.0
            
        self.scan_manager.start_scan(
            directories=self.scan_directories,
            min_similarity=threshold
        )
    
    def stop_scan(self):
        """Stop the current scan operation."""
        if hasattr(self, 'scan_manager'):
            self.scan_manager.cancel_scan()
            self.is_scanning = False
            self.progress_bar.hide()
            self.status_label.setText(self.tr("Scan stopped by user."))
            self.update_ui_state()
    
    def save_scan_results(self):
        """Save the current scan results to a CSV file."""
        if not self.duplicate_groups:
            QMessageBox.information(self, "No Results", "No scan results to save.")
            return
            
        # Get the default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"pdf_duplicate_scan_{timestamp}.csv"
        
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scan Results",
            os.path.join(os.path.expanduser("~"), default_filename),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Group', 'File Path', 'Size (bytes)', 'Pages', 
                    'Creation Date', 'Modification Date', 'MD5 Hash'
                ])
                
                # Write data for each duplicate group
                for i, group in enumerate(self.duplicate_groups, 1):
                    for file_info in group:
                        writer.writerow([
                            i,  # Group number
                            file_info.get('path', ''),
                            file_info.get('size', ''),
                            file_info.get('pages', ''),
                            file_info.get('creation_date', ''),
                            file_info.get('modification_date', ''),
                            file_info.get('md5', '')
                        ])
            
            QMessageBox.information(
                self, 
                "Save Successful", 
                f"Scan results saved to:\n{file_path}"
            )
            
        except Exception as e:
            logger.error(f"Error saving scan results: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save scan results:\n{str(e)}"
            )
    
    def load_scan_results(self):
        """Load scan results from a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Scan Results",
            os.path.expanduser("~"),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Check if required columns exist
                required_columns = ['Group', 'File Path', 'Size (bytes)']
                if not all(col in reader.fieldnames for col in required_columns):
                    raise ValueError("Invalid CSV format. Required columns not found.")
                
                # Group files by group number
                groups = {}
                for row in reader:
                    group_num = int(row['Group'])
                    if group_num not in groups:
                        groups[group_num] = []
                    
                    # Create file info dictionary
                    file_info = {
                        'path': row['File Path'],
                        'size': int(row.get('Size (bytes)', 0)),
                        'pages': int(row.get('Pages', 0)) if row.get('Pages') else 0,
                        'creation_date': row.get('Creation Date', ''),
                        'modification_date': row.get('Modification Date', ''),
                        'md5': row.get('MD5 Hash', '')
                    }
                    groups[group_num].append(file_info)
                
                # Convert to list of groups
                duplicate_groups = list(groups.values())
                
                # Update the UI with loaded results
                self.duplicate_groups = duplicate_groups
                if hasattr(self, 'duplicates_view'):
                    # Disconnect previous model signals if any
                    try:
                        self.duplicates_view.selectionModel().selectionChanged.disconnect()
                    except (TypeError, RuntimeError):
                        pass
                    
                    # Create a new model with the loaded results
                    model = DuplicateFilesModel(duplicate_groups)
                    self.duplicates_view.setModel(model)
                    
                    # Connect selection change signal
                    selection_model = self.duplicates_view.selectionModel()
                    selection_model.selectionChanged.connect(self.on_file_selection_changed)
                    
                    # Update the view
                    self.duplicates_view.resizeColumnsToContents()
                    
                    # Select first item if available
                    if duplicate_groups:
                        self.current_group_index = 0
                        self.show_current_group()
                    
                    # Update status
                    total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
                    status_text = f"Loaded {len(duplicate_groups)} groups with {total_duplicates} duplicate files"
                    self.status_label.setText(status_text)
                
                self.update_ui_state()
                
                QMessageBox.information(
                    self, 
                    "Load Successful", 
                    f"Successfully loaded {len(duplicate_groups)} groups from:\n{file_path}"
                )
                
        except Exception as e:
            logger.error(f"Error loading scan results: {e}")
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load scan results:\n{str(e)}"
            )
    
    def on_scan_completed(self, duplicate_groups):
        """Handle completion of the scan operation."""
        self.is_scanning = False
        self.progress_bar.hide()
        
        # Update the model with results
        self.duplicate_groups = duplicate_groups
        
        # Reset current indices to -1 to prevent index errors
        self.current_group_index = -1
        self.current_file_index = -1
        
        if hasattr(self, 'duplicates_view'):
            # Disconnect previous model signals if any
            try:
                self.duplicates_view.selectionModel().selectionChanged.disconnect()
            except (TypeError, RuntimeError):
                pass
                
            # Create and set the new model
            model = DuplicateFilesModel(duplicate_groups)
            self.duplicates_view.setModel(model)
            
            # Connect selection changed signal
            selection_model = self.duplicates_view.selectionModel()
            if selection_model:
                selection_model.selectionChanged.connect(self.on_file_selection_changed)
            
            # Connect double click signal
            self.duplicates_view.doubleClicked.disconnect()
            self.duplicates_view.doubleClicked.connect(self.on_duplicate_double_clicked)
            
            # Resize columns to fit content
            for i in range(model.columnCount()):
                self.duplicates_view.resizeColumnToContents(i)
            
            # If we have results, select the first group and file
            if duplicate_groups:
                self.current_group_index = 0
                self.current_file_index = 0
                self.show_current_group()
                self.show_current_file()
            
            # Update status
            total_duplicates = sum(len(group) - 1 for group in duplicate_groups) if duplicate_groups else 0
            if duplicate_groups:
                self.status_label.setText(
                    self.tr("Found {} groups with {} duplicate files").format(
                        len(duplicate_groups), 
                        total_duplicates
                    )
                )
            else:
                self.status_label.setText(self.tr("No duplicate files found."))
        
        # Update UI state to reflect the new scan results
        self.update_ui_state()
        
        # Update status
        if duplicate_groups:
            total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
            status_text = self.tr("Found {} groups with {} duplicate files").format(
                len(duplicate_groups), 
                total_duplicates
            )
            self.status_label.setText(status_text)
        else:
            self.status_label.setText(self.tr("No duplicate files found."))
            
        self.update_ui_state()
        
        # Save to recent files
        for directory in self.scan_directories:
            self.recent_manager.add_file(directory)
        
        self.update_ui_state()
    
    def on_file_processed(self, current, total, filename):
        """Update progress when a file is processed."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"Scanning: {os.path.basename(filename)}")
    
    def update_progress(self, value, maximum=None):
        """Update the progress bar."""
        if maximum is not None:
            self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
    
    def filter_duplicates(self, text):
        """Filter the duplicates list based on search text."""
        if hasattr(self, 'duplicates_view') and hasattr(self.duplicates_view, 'model'):
            self.duplicates_view.model().setFilterFixedString(text)
    
    def load_recent_files(self):
        """Load and display recently scanned folders in the File menu."""
        try:
            # Make sure recent_menu exists and is valid
            if not hasattr(self, 'recent_menu') or not self.recent_menu:
                # Try to find the recent menu in the file menu
                file_menu = self.menuBar().findChild(QMenu, "File")
                if file_menu:
                    for action in file_menu.actions():
                        if action.menu() and action.menu().title() == self.tr("Recent Folders"):
                            self.recent_menu = action.menu()
                            break
                
                if not hasattr(self, 'recent_menu') or not self.recent_menu:
                    return
            
            # Clear existing actions
            self.recent_menu.clear()
            
            # Create menu actions using RecentFoldersManager
            self.recent_folders_manager.create_recent_menu_actions(
                self.recent_menu,
                self.on_recent_folder_selected,
                self.tr("Clear Recent Folders")
            )
        except RuntimeError as e:
            if "deleted" in str(e):
                # Menu was deleted, we'll try again next time
                if hasattr(self, 'recent_menu'):
                    del self.recent_menu
                return
            raise
    
    def on_recent_folder_selected(self, folder_path):
        """Handle selection of a recent folder from the menu."""
        if not folder_path:
            return
            
        # Ensure the path is absolute and normalized
        folder_path = os.path.normpath(os.path.abspath(folder_path))
        
        if os.path.isdir(folder_path):
            # Add to recent folders to update the last accessed time
            self.recent_folders_manager.add_recent_folder(folder_path)
            
            # Start the scan
            self.scan_directories = [folder_path]
            self.start_scan()
        else:
            # Show error message
            reply = QMessageBox.warning(
                self,
                self.tr("Folder Not Found"),
                self.tr("The folder '{}' no longer exists.\n\nWould you like to remove it from the recent folders list?").format(folder_path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            # Remove the non-existent folder from recent list if requested
            if reply == QMessageBox.StandardButton.Yes:
                self.recent_folders_manager.remove_recent_folder(folder_path)
                self.load_recent_files()
    
    def clear_recent_folders(self):
        """Clear the list of recently used folders after confirmation."""
        # Ask for confirmation before clearing
        reply = QMessageBox.question(
            self,
            self.tr("Clear Recent Folders"),
            self.tr("Are you sure you want to clear the list of recent folders?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.recent_folders_manager.clear_recent_folders()
            self.load_recent_files()
    
    def load_settings(self):
        """Load application settings from QSettings."""
        try:
            settings = QSettings("PDFDuplicateFinder", "PDFDuplicateFinder")
            self.app_settings = {
                'scan_recursive': settings.value('scan_recursive', True, type=bool),
                'min_file_size': settings.value('min_file_size', 100, type=int),
                'max_file_size': settings.value('max_file_size', 10000, type=int),
                'hash_size': settings.value('hash_size', 8, type=int),
                'threshold': settings.value('threshold', 5, type=int),
                'theme': settings.value('theme', 'system', type=str),
                'language': settings.value('language', 'en', type=str)
            }
            logger.info("Settings loaded successfully")
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            logger.debug(traceback.format_exc())
            # Set default settings if loading fails
            self.app_settings = {
                'scan_recursive': True,
                'min_file_size': 100,
                'max_file_size': 10000,
                'hash_size': 8,
                'threshold': 5,
                'theme': 'system',
                'language': 'en'
            }
    
    def save_settings(self):
        """Save application settings to QSettings."""
        try:
            settings = QSettings("PDFDuplicateFinder", "PDFDuplicateFinder")
            for key, value in self.app_settings.items():
                settings.setValue(key, value)
            settings.sync()
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            logger.debug(traceback.format_exc())
    
    def save_scan_results(self):
        """Save the current scan results to a CSV file."""
        if not hasattr(self, 'duplicate_groups') or not self.duplicate_groups:
            QMessageBox.information(self, "No Results", "No scan results to save.")
            return
            
        # Get the default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"pdf_duplicate_scan_{timestamp}.csv"
        
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scan Results",
            os.path.join(os.path.expanduser("~"), default_filename),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Group', 'File Path', 'Size (bytes)', 'Pages', 
                    'Creation Date', 'Modification Date', 'MD5 Hash'
                ])
                
                # Write data for each duplicate group
                for i, group in enumerate(self.duplicate_groups, 1):
                    for file_info in group:
                        writer.writerow([
                            i,  # Group number
                            file_info.get('path', ''),
                            file_info.get('size', ''),
                            file_info.get('pages', ''),
                            file_info.get('creation_date', ''),
                            file_info.get('modification_date', ''),
                            file_info.get('md5', '')
                        ])
            
            QMessageBox.information(
                self, 
                "Save Successful", 
                f"Scan results saved to:\n{file_path}"
            )
            
        except Exception as e:
            logger.error(f"Error saving scan results: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save scan results:\n{str(e)}"
            )
    
    def apply_theme(self):
        # Apply the selected theme
        theme = self.app_settings.get('theme', 'system')
        
        if theme == 'dark':
            self.setStyleSheet("""
                /* Main window and dialogs */
                QMainWindow, QDialog, QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    selection-background-color: #3a6ea5;
                    selection-color: #ffffff;
                }
                
                /* Text and labels */
                QLabel, QCheckBox {
                    color: #e0e0e0;
                }
                
                /* Input fields and buttons */
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                    background-color: #3c3f41;
                    color: #e0e0e0;
                    border: 1px solid #555;
                    padding: 3px;
                    border-radius: 3px;
                }
                
                /* Tree and list widgets */
                QTreeView, QTreeWidget, QListView, QListWidget, QTableWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border: 1px solid #3f3f3f;
                    alternate-background-color: #323232;
                }
                
                /* Tree and list items */
                QTreeView::item, QTreeWidget::item, QListWidget::item {
                    padding: 5px;
                    border: 1px solid transparent;
                }
                
                /* Selected items */
                QTreeView::item:selected, QTreeWidget::item:selected, 
                QListWidget::item:selected, QTableView::item:selected {
                    background-color: #3a6ea5;
                    color: #ffffff;
                }
                
                /* Hover effect */
                QTreeView::item:hover, QTreeWidget::item:hover, 
                QListWidget::item:hover, QTableView::item:hover {
                    background-color: #3a3a3a;
                }
                
                /* Headers */
                QHeaderView::section {
                    background-color: #3c3f41;
                    color: #e0e0e0;
                    padding: 5px;
                    border: 1px solid #555;
                }
                
                /* Buttons */
                QPushButton {
                    background-color: #3c3f41;
                    color: #e0e0e0;
                    border: 1px solid #555;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                
                QPushButton:hover {
                    background-color: #4e5153;
                }
                
                QPushButton:pressed {
                    background-color: #2d2f30;
                }
            """)
        elif theme == 'light':
            self.setStyleSheet("""
                /* Main window and dialogs */
                QMainWindow, QDialog, QWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                    selection-background-color: #4a90e2;
                    selection-color: #ffffff;
                }
                
                /* Text and labels */
                QLabel, QCheckBox {
                    color: #333333;
                }
                
                /* Input fields and buttons */
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    padding: 3px;
                    border-radius: 3px;
                }
                
                /* Tree and list widgets */
                QTreeView, QTreeWidget, QListView, QListWidget, QTableWidget {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    alternate-background-color: #f8f8f8;
                }
                
                /* Tree and list items */
                QTreeView::item, QTreeWidget::item, QListWidget::item {
                    padding: 5px;
                    border: 1px solid transparent;
                }
                
                /* Selected items */
                QTreeView::item:selected, QTreeWidget::item:selected, 
                QListWidget::item:selected, QTableView::item:selected {
                    background-color: #4a90e2;
                    color: #ffffff;
                }
                
                /* Hover effect */
                QTreeView::item:hover, QTreeWidget::item:hover, 
                QListWidget::item:hover, QTableView::item:hover {
                    background-color: #f0f0f0;
                }
                
                /* Headers */
                QHeaderView::section {
                    background-color: #e0e0e0;
                    color: #333333;
                    padding: 5px;
                    border: 1px solid #cccccc;
                }
                
                /* Buttons */
                QPushButton {
                    background-color: #f8f8f8;
                    color: #333333;
                    border: 1px solid #cccccc;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
            """)
        else:  # system
            self.setStyleSheet("")  # Reset to system theme
    
    def load_scan_results(self):
        """Load scan results from a CSV file."""
        # Open file dialog to select the CSV file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Scan Results",
            os.path.expanduser("~"),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Reset current state
                self.duplicate_groups = []
                current_group = -1
                
                # Read data row by row
                for row in reader:
                    group_num = int(row.get('Group', '0'))
                    
                    # Create a new group if needed
                    if group_num > current_group:
                        self.duplicate_groups.append([])
                        current_group = group_num
                    
                    # Add file info to the current group
                    file_info = {
                        'path': row.get('File Path', ''),
                        'size': int(row.get('Size (bytes)', 0)),
                        'pages': int(row.get('Pages', 0)),
                        'creation_date': row.get('Creation Date', ''),
                        'modification_date': row.get('Modification Date', ''),
                        'md5': row.get('MD5 Hash', '')
                    }
                    self.duplicate_groups[-1].append(file_info)
            
            # Update the UI with the loaded results
            if hasattr(self, 'duplicates_view') and self.duplicate_groups:
                self.current_group_index = 0
                self.current_file_index = 0
                self.update_duplicates_view()
                self.update_ui_state()
                
                QMessageBox.information(
                    self,
                    "Load Successful",
                    f"Successfully loaded {len(self.duplicate_groups)} duplicate groups from:\n{file_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "No Valid Data",
                    "The selected file does not contain valid scan results."
                )
                
        except Exception as e:
            logger.error(f"Error loading scan results: {e}")
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load scan results:\n{str(e)}"
            )
    
    def save_scan_results(self):
        """Save the current scan results to a CSV file."""
        if not hasattr(self, 'duplicate_groups') or not self.duplicate_groups:
            QMessageBox.information(self, "No Results", "No scan results to save.")
            return
            
        # Get the default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"pdf_duplicate_scan_{timestamp}.csv"
        
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scan Results",
            os.path.join(os.path.expanduser("~"), default_filename),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Group', 'File Path', 'Size (bytes)', 'Pages', 
                    'Creation Date', 'Modification Date', 'MD5 Hash'
                ])
                
                # Write data for each duplicate group
                for i, group in enumerate(self.duplicate_groups, 1):
                    for file_info in group:
                        writer.writerow([
                            i,  # Group number
                            file_info.get('path', ''),
                            file_info.get('size', ''),
                            file_info.get('pages', ''),
                            file_info.get('creation_date', ''),
                            file_info.get('modification_date', ''),
                            file_info.get('md5', '')
                        ])
            
            QMessageBox.information(
                self, 
                "Save Successful", 
                f"Scan results saved to:\n{file_path}"
            )
            
        except Exception as e:
            logger.error(f"Error saving scan results: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save scan results:\n{str(e)}"
            )
    
    def closeEvent(self, event):
        """Handle the window close event."""
        try:
            logger.info("Application is shutting down")
            
            # Save window geometry and state
            settings = QSettings("PDFDuplicateFinder", "PDFDuplicateFinder")
            settings.setValue("geometry", self.saveGeometry())
            settings.setValue("windowState", self.saveState())
            
            # Save current view state
            if hasattr(self, 'current_group_index'):
                settings.setValue("current_group_index", self.current_group_index)
            if hasattr(self, 'current_file_index'):
                settings.setValue("current_file_index", self.current_file_index)
            
            # Save settings
            self.save_settings()
            
            logger.info("Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {str(e)}")
            logger.debug(traceback.format_exc())
        
        event.accept()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default excepthook for keyboard interrupts
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Show error message to the user
    error_msg = f"An unhandled exception occurred:\n\n{str(exc_value)}"
    QMessageBox.critical(
        None,
        "Unexpected Error",
        f"{error_msg}\n\nPlease check the log file for more details.",
        QMessageBox.StandardButton.Ok
    )

def main():
    """Main entry point for the application."""
    try:
        # Set up exception handling
        sys.excepthook = handle_exception
        
        # Create the application
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("PDF Duplicate Finder")
        app.setApplicationVersion("3.0.0")
        app.setOrganizationName("Tuxxle")
        app.setOrganizationDomain("tuxxle.net")
        
        # Set application style
        app.setStyle(QStyleFactory.create("Fusion"))
        
        # Create and show the main window
        window = PDFDuplicateFinder()
        window.show()
        
        logger.info("Application started successfully")
        
        # Start the application
        return app.exec()
        
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"A fatal error occurred: {str(e)}\n\nThe application will now exit.",
            QMessageBox.StandardButton.Ok
        )
        return 1

if __name__ == "__main__":
    main()
