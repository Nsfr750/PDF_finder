import os
import sys
import logging
import traceback
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

# Import Version
from script.version import get_version

# Import log viewer
from script.view_log import show_log_viewer

# Import language manager
from script.language_manager import LanguageManager

# Import settings manager
from script.settings import settings_manager

# Import logger
from script.logger import setup_logging, logger

# Qt imports - Core
from PyQt6.QtCore import (
    Qt, QSize, QThread, pyqtSignal as Signal, pyqtSlot as Slot, 
    QObject, QTimer, QSettings, QPoint, QEvent, QMimeData, 
    QUrl, QByteArray, QBuffer, QIODevice, QSizeF, QLocale, 
    QTranslator, QLibraryInfo, QRect
)
# Qt imports - Gui
from PyQt6.QtGui import (
    QAction, QActionGroup, QIcon, QPixmap, QFont, 
    QColor, QPalette, QKeySequence, QDragEnterEvent, 
    QDropEvent, QImage, QImageReader, QPainter, QBrush, 
    QLinearGradient, QGradient, QTextCursor, QTextCharFormat, 
    QTextFormat, QTextLength, QTextBlockFormat, QTextDocument, 
    QTextFrameFormat, QTextImageFormat, QTextTableFormat, QTextTable,
    QScreen
)
# Qt imports - Widgets
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QProgressBar, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QFileDialog, QMessageBox, QMenuBar, 
    QMenu, QStyle, QTreeWidget, QTreeWidgetItem, QAbstractItemView, 
    QToolBar, QStatusBar, QCheckBox, QSpinBox, QDoubleSpinBox, 
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, 
    QTextEdit, QTabWidget, QGroupBox, QRadioButton, QButtonGroup, 
    QScrollArea, QFrame, QSizePolicy, QSpacerItem, QSystemTrayIcon, 
    QStyleFactory, QInputDialog, QListWidget, QListWidgetItem, 
    QStyledItemDelegate, QStyleOptionViewItem, QProgressDialog, 
    QToolButton, QSplashScreen
)

# Application imports
from script.main_window import MainWindow
from script.drag_drop import FileDropHandler
from script.gest_scan import ScanManager
from script.recents import RecentFilesManager
from script.gest_recent import RecentFoldersManager
from script.about import AboutDialog
from script.delete import DeleteConfirmationDialog, delete_files
from script.search_dup import DuplicateFilesView, DuplicateFilesModel, DuplicateGroup, DuplicateFileItem

# Import utility functions
from script.pdf_utils import (
    get_pdf_info, calculate_file_hash, extract_first_page_image,
    calculate_image_hash, find_duplicates
)
from script.preview_widget import PDFPreviewWidget, PreviewWindow
from script.utils import get_file_path, get_file_info_dict

# Import menu manager
from script.menu import MenuManager

# Set up logging
logger = setup_logging('PDFDuplicateFinder')

# Constants
APP_NAME = "PDF Duplicate Finder"
APP_VERSION = get_version()
    
class PDFDuplicateFinder(MainWindow):
    """Main application window for PDF Duplicate Finder."""
    
    def __init__(self, parent=None):
        # Initialize the language manager first
        self.language_manager = LanguageManager()
        
        # Now call the parent's __init__ with the language_manager
        super().__init__(self.language_manager, parent)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Initialize settings
        self.app_settings = settings_manager.app_settings  # Use the settings manager
        
        # Initialize variables
        self.duplicate_groups = []
        self.current_group_index = -1
        self.current_file_index = -1
        self.scan_directories = []
        self.scan_thread = None
        self.is_scanning = False
        self.preview_window = None  # Will hold the preview window instance
        
        # Initialize managers
        self.recent_manager = RecentFilesManager()
        self.recent_folders_manager = RecentFoldersManager()
        self.scan_manager = ScanManager()
        
        # Initialize menu manager
        self.menu_manager = MenuManager(self, self.language_manager)
        
        # Initialize file drop handler
        self._file_drop_handler = FileDropHandler(self)
        
        # Initialize UI
        self.init_ui()
        
        # Apply theme
        self.apply_theme()
        
        # Load recent files after UI is fully initialized
        self.load_recent_files()
        
        # Connect signals
        self.scan_manager.scan_completed.connect(self.on_scan_completed)
        self.scan_manager.progress.connect(self.update_progress)
        self.scan_manager.file_processed.connect(self.on_file_processed)

    def setup_menu_connections(self):
        """Set up connections for menu actions."""
        # Connect menu signals to slots
        self.menu_manager.open_folder_triggered.connect(self.on_scan_folder)
        self.menu_manager.save_results_triggered.connect(self.save_scan_results)
        self.menu_manager.load_results_triggered.connect(self.load_scan_results)
        self.menu_manager.settings_triggered.connect(self.on_settings)
        self.menu_manager.exit_triggered.connect(self.close)
        self.menu_manager.view_log_triggered.connect(self.on_view_log)
        self.menu_manager.check_updates_triggered.connect(self.on_check_updates)
        self.menu_manager.about_triggered.connect(self.on_about)
        self.menu_manager.documentation_triggered.connect(self.on_help)
        self.menu_manager.markdown_docs_triggered.connect(self.on_markdown_docs)  # Add this line
        self.menu_manager.sponsor_triggered.connect(self.on_sponsor)
        self.menu_manager.pdf_viewer_triggered.connect(self.on_pdf_viewer)
        self.menu_manager.language_changed.connect(self.change_language)
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle(self.tr("PDF Duplicate Finder"))
        self.setMinimumSize(1024, 768)
        
        # Set up the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Set up the menu bar
        self.menu_manager.set_menu_bar()
        
        # Set up the main layout
        layout = QVBoxLayout(main_widget)
        
        # Add the main content
        self.create_main_content()
        
        # Add the main content to the layout
        layout.addWidget(self.main_widget)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add status label
        self.status_label = QLabel()
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def retranslate_ui(self):
        """Retranslate all UI elements."""
        # Check if the widget is being destroyed or if translation is already in progress
        if not self or not hasattr(self, 'isVisible') or hasattr(self, '_translating') and self._translating:
            return
            
        try:
            # Set flag to prevent recursion
            self._translating = True
            
            # Call parent's retranslate_ui first
            super().retranslate_ui()
            
            # Update main window title
            self.setWindowTitle(self.tr("PDF Duplicate Finder"))
            
            # Update menu items
            self.menu_manager.retranslate_ui()
            
            # Update status bar
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText("")
                
        except RuntimeError as e:
            # Catch and log any RuntimeError that might occur if Qt objects are deleted
            if 'deleted' in str(e):
                logger.debug("Qt object deleted during retranslate_ui")
                return
            raise
            
        finally:
            # Always clear the flag when done
            if hasattr(self, '_translating'):
                del self._translating

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
        # Check if the widget is being destroyed or if translation is already in progress
        if not self or not hasattr(self, 'isVisible') or hasattr(self, '_translating') and self._translating:
            return
            
        try:
            # Set flag to prevent recursion
            self._translating = True
            
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
            
        finally:
            # Always clear the flag when done
            if hasattr(self, '_translating'):
                del self._translating
            
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
            settings_manager.save_settings()
            
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
        """Load application settings."""
        # Settings are now loaded by the SettingsManager
        pass

    def save_settings(self):
        """Save application settings."""
        settings_manager.save_settings()

    def update_duplicates_view(self):
        """Update the duplicates view with the current duplicate groups."""
        try:
            logger.debug("Updating duplicates view...")
            
            if not hasattr(self, 'duplicates_view'):
                logger.error("duplicates_view not found in the UI")
                return
                
            logger.debug(f"Found {len(self.duplicate_groups)} duplicate groups to display")
            
            # Log the structure of the first group for debugging
            if self.duplicate_groups:
                logger.debug(f"First group sample: {self.duplicate_groups[0][0] if self.duplicate_groups[0] else 'Empty group'}")
            
            # Create a model with the current duplicate groups
            from app_qt.search_dup import DuplicateFilesModel
            try:
                model = DuplicateFilesModel(self.duplicate_groups)
                logger.debug("Created DuplicateFilesModel successfully")
                
                # Set the model on the view
                self.duplicates_view.setModel(model)
                logger.debug("Set model on duplicates_view")
                
                # Expand all items by default
                self.duplicates_view.expandAll()
                logger.debug("Expanded all items in the view")
                
                # Resize columns to fit content
                col_count = model.columnCount()
                logger.debug(f"Model has {col_count} columns")
                
                for i in range(col_count):
                    self.duplicates_view.resizeColumnToContents(i)
                
                logger.debug("Finished updating duplicates view")
                
            except Exception as e:
                logger.error(f"Error in model/view setup: {e}", exc_info=True)
                raise
                
        except Exception as e:
            logger.error(f"Error updating duplicates view: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to update the duplicates view: {str(e)}\n\nCheck the log file for more details."
            )
    
    def on_scan_completed(self, duplicate_groups):
        """
        Handle the completion of a scan operation.
        
        Args:
            duplicate_groups: List of duplicate file groups found during the scan
        """
        try:
            # Prevent multiple simultaneous executions
            if hasattr(self, '_scan_completed_running') and self._scan_completed_running:
                logger.debug("on_scan_completed already running, ignoring duplicate call")
                return
                
            self._scan_completed_running = True
            
            # Store the results
            self.duplicate_groups = duplicate_groups
            
            # Reset indices
            self.current_group_index = -1
            self.current_file_index = -1
            
            # Check if view exists and is valid
            if not hasattr(self, 'duplicates_view') or not self.duplicates_view:
                logger.warning("duplicates_view not available, cannot update UI")
                return
            
            # Store reference to the view
            view = self.duplicates_view
            
            # Block all signals during update
            was_blocked = view.blockSignals(True)
            
            try:
                # Safely get current selection model if it exists
                current_selection_model = view.selectionModel()
                
                # Disconnect any existing selection changed signals
                if current_selection_model:
                    try:
                        current_selection_model.selectionChanged.disconnect()
                    except (TypeError, RuntimeError):
                        # Not connected, ignore
                        pass
                
                # Disconnect double click signal
                try:
                    view.doubleClicked.disconnect()
                except (TypeError, RuntimeError):
                    # Not connected, ignore
                    pass
                
                # Create and set the new model
                model = DuplicateFilesModel(duplicate_groups)
                view.setModel(model)  # This will delete the old model and its selection model
                
                # Set up selection behavior
                view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
                
                # Get the new selection model and connect signals
                selection_model = view.selectionModel()
                if selection_model:
                    selection_model.selectionChanged.connect(self.on_file_selection_changed)
                
                # Connect double click signal
                view.doubleClicked.connect(self.on_duplicate_double_clicked)
                
                # Resize columns to fit content
                for i in range(model.columnCount()):
                    view.resizeColumnToContents(i)
                
                # If we have results, select the first group and file
                if duplicate_groups:
                    self.current_group_index = 0
                    self.current_file_index = 0
                    self.show_current_group()
                    self.show_current_file()
                
                # Update status
                total_duplicates = sum(len(group) - 1 for group in duplicate_groups) if duplicate_groups else 0
                if duplicate_groups:
                    status_text = self.tr("Found {} groups with {} duplicate files").format(
                        len(duplicate_groups), 
                        total_duplicates
                    )
                    self.status_label.setText(status_text)
                else:
                    self.status_label.setText(self.tr("No duplicate files found."))
                
                # Show completion message
                QMessageBox.information(
                    self,
                    "Scan Complete",
                    f"Found {len(duplicate_groups)} duplicate groups"
                )
                
            except Exception as e:
                logger.error(f"Error updating UI: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update UI with scan results: {str(e)}\n\nCheck the log file for more details."
                )
                
            finally:
                # Always restore signal blocking state
                view.blockSignals(was_blocked)
                self._scan_completed_running = False
                
        except Exception as e:
            logger.error(f"Error in on_scan_completed: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while processing scan results: {str(e)}"
            )
        finally:
            # Update UI state to reflect the new scan results
            self.update_ui_state()
            
            # Force update the menu bar to ensure it's refreshed
            self.menuBar().update()
            
            # Force a menu bar update to ensure all menu states are refreshed
            self.menuBar().repaint()
    
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
        # Get the menubar
        menubar = self.menuBar()
        
        # Clear existing menus to prevent duplicates
        menubar.clear()
        
        # File menu
        file_menu = menubar.addMenu(self.tr("&File"))
        
        # Scan Folder action
        self.scan_folder_action = QAction(self.tr("&Scan Folder..."), self)
        self.scan_folder_action.triggered.connect(self.on_scan_folder)
        self.scan_folder_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.scan_folder_action)
        
        file_menu.addSeparator()
        
        # Save Results action
        self.save_results_action = QAction(self.tr("&Save Results..."), self)
        self.save_results_action.triggered.connect(self.save_scan_results)
        self.save_results_action.setShortcut("Ctrl+S")
        self.save_results_action.setEnabled(False)  # Disabled by default until we have results
        file_menu.addAction(self.save_results_action)
        
        # Load Results action
        self.load_results_action = QAction(self.tr("Load Results..."), self)
        self.load_results_action.triggered.connect(self.load_scan_results)
        self.load_results_action.setShortcut("Ctrl+L")
        file_menu.addAction(self.load_results_action)
        
        file_menu.addSeparator()
        
        # Recent folders submenu
        self.recent_menu = file_menu.addMenu(self.tr("Recent &Folders"))
        self.load_recent_files()  # This will populate the recent folders
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction(self.tr("E&xit"), self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu(self.tr("&Edit"))
        
        # Settings action
        self.settings_action = QAction(self.tr("&Settings..."), self)
        self.settings_action.triggered.connect(self.on_settings)
        edit_menu.addAction(self.settings_action)
        
        # View menu
        view_menu = menubar.addMenu(self.tr("&View"))
        
        # Navigation actions
        self.prev_group_action = QAction(self.tr("&Previous Group"), self)
        self.prev_group_action.triggered.connect(self.on_prev_group)
        view_menu.addAction(self.prev_group_action)
        
        self.next_group_action = QAction(self.tr("&Next Group"), self)
        self.next_group_action.triggered.connect(self.on_next_group)
        view_menu.addAction(self.next_group_action)
        
        view_menu.addSeparator()
        
        self.prev_file_action = QAction(self.tr("Pre&vious File"), self)
        self.prev_file_action.triggered.connect(self.on_prev_file)
        view_menu.addAction(self.prev_file_action)
        
        self.next_file_action = QAction(self.tr("Ne&xt File"), self)
        self.next_file_action.triggered.connect(self.on_next_file)
        view_menu.addAction(self.next_file_action)
        
        view_menu.addSeparator()
        
        # Toggle preview action
        self.toggle_preview_action = QAction(self.tr("Show &Preview"), self, checkable=True)
        self.toggle_preview_action.setChecked(True)
        self.toggle_preview_action.triggered.connect(self.toggle_preview_window)
        view_menu.addAction(self.toggle_preview_action)
        
        # Tools menu
        tools_menu = menubar.addMenu(self.tr("&Tools"))
        
        # Language submenu
        language_menu = tools_menu.addMenu(self.tr("&Language"))
        
        # Add language actions
        self.language_group = QActionGroup(self)
        self.language_group.setExclusive(True)
        
        # Add available languages
        languages = [
            ("English", "en"),
            ("Italiano", "it"),
            # Add more languages as needed
        ]
        
        for name, code in languages:
            action = QAction(name, self, checkable=True)
            action.setData(code)
            if code == self.app_settings.get('language', 'en'):
                action.setChecked(True)
            action.triggered.connect(lambda checked, code=code: self.change_language(code))
            language_menu.addAction(action)
            self.language_group.addAction(action)
        
        # Add Check for Updates action
        self.update_action = QAction("Check for Updates...", self)
        self.update_action.triggered.connect(self.on_check_updates)
        tools_menu.addAction(self.update_action)
        
        # Add View Log action
        self.view_log_action = QAction("View Log", self)
        self.view_log_action.triggered.connect(self.on_view_log)
        tools_menu.addAction(self.view_log_action)
        
        # Add PDF Viewer action
        self.pdf_viewer_action = QAction("PDF Viewer", self)
        self.pdf_viewer_action.triggered.connect(self.on_pdf_viewer)
        tools_menu.addAction(self.pdf_viewer_action)
        
        # Add Markdown Docs action
        self.markdown_docs_action = QAction("Markdown Documentation", self)
        self.markdown_docs_action.triggered.connect(self.on_markdown_docs)
        tools_menu.addAction(self.markdown_docs_action)
        
        # Help menu
        help_menu = menubar.addMenu(self.tr("&Help"))
        
        # Documentation action
        self.documentation_action = QAction("Documentation", self)
        self.documentation_action.triggered.connect(self.on_help)
        help_menu.addAction(self.documentation_action)
        
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
        
        # Store menu references for later use
        self.file_menu = file_menu
        self.edit_menu = edit_menu
        self.view_menu = view_menu
        self.tools_menu = tools_menu
        self.help_menu = help_menu
    
    def create_toolbar(self):
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setObjectName("mainToolbar")  # Add this line to set objectName
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Import QStyle at the top of the file if not already imported
        from PyQt6.QtWidgets import QStyle
        
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
        
        # Toggle preview button
        self.toggle_preview_action = QAction("Show Preview", self)
        self.toggle_preview_action.setCheckable(True)
        self.toggle_preview_action.setChecked(False)
        self.toggle_preview_action.triggered.connect(self.toggle_preview_window)
        self.toggle_preview_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        toolbar.addAction(self.toggle_preview_action)
        
        # Add stretch to push remaining items to the right
        toolbar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
    
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
            directory=last_dir,
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
                settings_manager.save_settings()
            
            # Start the scan with the selected folder
            self.scan_directories = [folder]
            self.scan_manager.start_scan(self.scan_directories)
    
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
        menu.exec(self.duplicates_view.viewport().mapToGlobal(position))
    
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
            # Update preview window if available
            if hasattr(self, 'preview_window') and self.preview_window:
                try:
                    self.preview_window.load_pdf(item.file_path)
                except Exception as e:
                    logger.error(f"Error loading PDF in preview window: {e}")
            
            # Update file details if available and has set_file method
            if hasattr(self, 'file_details') and hasattr(self.file_details, 'set_file'):
                try:
                    self.file_details.set_file(item.file_path)
                except Exception as e:
                    logger.error(f"Error updating file details: {e}")
        else:
            # Clear preview and details if no file path
            if hasattr(self, 'preview_window') and self.preview_window and hasattr(self.preview_window, 'clear'):
                self.preview_window.clear()
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
    def save_settings(self):
        """Save application settings."""
        settings_manager.save_settings()

    def on_settings(self):
        dialog = SettingsDialog(self, self.app_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save settings
            self.app_settings = dialog.get_settings()
            settings_manager.save_settings()
            self.apply_theme()
    
    def on_view_log(self):
        """Open the application log file in the log viewer dialog."""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            log_file = os.path.join(log_dir, 'pdf_finder.log')
            
            # Show the log viewer dialog
            show_log_viewer(log_file, self)
            logger.info("Opened log viewer")
            
        except Exception as e:
            logger.error(f"Error opening log viewer: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open log viewer:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
    
    def on_help(self):
        """Show the help dialog."""
        try:
            from app_qt.help import HelpDialog
            # Get current language from settings or use 'en' as default
            current_lang = getattr(self, 'current_language', 'en')
            help_dialog = HelpDialog(self, current_lang=current_lang)
            # Connect language change signal
            help_dialog.language_changed.connect(self.on_help_language_changed)
            help_dialog.exec()
        except ImportError as e:
            logger.error(f"Error showing help: {e}")
            QMessageBox.critical(
                self,
                "Error",
                "Could not load help content. Please check the installation.",
                QMessageBox.StandardButton.Ok
            )
    
    def on_help_language_changed(self, language_code):
        """Handle language change from help dialog."""
        # Update the current language in the main application
        self.current_language = language_code
        # You can add additional logic here to update other parts of the UI
        # if needed when the language changes from the help dialog
    
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
        self.next_file_action.setEnabled(has_selection and self.current_file_index < len(self.duplicate_groups[self.current_group_index]) - 1)
        
        # Enable/disable action buttons
        if hasattr(self, 'save_results_action'):
            self.save_results_action.setEnabled(has_groups)
            
        if hasattr(self, 'delete_action'):
            self.delete_action.setEnabled(has_selection)
        
        # Update status message
        if self.is_scanning:
            status_text = "Scanning..."
        elif has_groups:
            total_duplicates = sum(len(group) - 1 for group in self.duplicate_groups) if self.duplicate_groups else 0
            status_text = f"Found {total_duplicates} duplicate files in {len(self.duplicate_groups)} groups"
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
    
    def show_current_file(self):
        """Update the view to show the current file within the current group."""
        if not hasattr(self, 'duplicate_groups') or not self.duplicate_groups:
            return
            
        if 0 <= self.current_group_index < len(self.duplicate_groups):
            group = self.duplicate_groups[self.current_group_index]
            if 0 <= self.current_file_index < len(group):
                file_info = group[self.current_file_index]
                
                # Get the file path using the utility function
                file_path = get_file_path(file_info)
                
                if not file_path:
                    logger.warning("No valid file path found in file_info")
                    return
                
                # Update the preview if available
                if hasattr(self, 'preview_widget'):
                    try:
                        self.preview_widget.load_pdf(file_path)
                    except Exception as e:
                        logger.error(f"Error loading PDF preview: {e}", exc_info=True)
                        if hasattr(self.preview_widget, 'clear'):
                            self.preview_widget.clear()
                
                # Update file details if available and has set_file method
                if hasattr(self, 'file_details') and hasattr(self.file_details, 'set_file'):
                    try:
                        self.file_details.set_file(file_path)
                    except Exception as e:
                        logger.error(f"Error updating file details: {e}", exc_info=True)
                
                # Update the UI state
                self.update_ui_state()
    
    def toggle_preview_window(self):
        """Toggle the preview window visibility."""
        if self.toggle_preview_action.isChecked():
            self.show_preview_window()
        else:
            self.hide_preview_window()
    
    def show_preview_window(self):
        """Show the preview window."""
        if not hasattr(self, 'preview_window') or not self.preview_window:
            self.preview_window = PreviewWindow(self)
            # Load current PDF if available
            selected_indexes = self.duplicates_view.selectedIndexes()
            if selected_indexes:
                index = selected_indexes[0]
                if index.isValid():
                    model = self.duplicates_view.model()
                    item = model.data(index, Qt.ItemDataRole.UserRole)
                    if hasattr(item, 'file_path'):
                        self.preview_window.load_pdf(item.file_path)
        
        self.preview_window.show()
        self.preview_window.raise_()
        self.preview_window.activateWindow()
    
    def hide_preview_window(self):
        """Hide the preview window."""
        if hasattr(self, 'preview_window') and self.preview_window:
            self.preview_window.hide()
    
    def on_preview_window_closed(self):
        """Handle the preview window being closed."""
        if hasattr(self, 'toggle_preview_action'):
            self.toggle_preview_action.setChecked(False)
        self.preview_window = None
    
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
                self.recent_folders_manager.add_recent(directory)
        
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
            # Disconnect any existing selection model signals
            current_selection_model = self.duplicates_view.selectionModel()
            if current_selection_model:
                try:
                    current_selection_model.selectionChanged.disconnect()
                except (TypeError, RuntimeError):
                    # Ignore if not connected
                    pass
            
            # Create and set the new model
            model = DuplicateFilesModel(duplicate_groups)
            self.duplicates_view.setModel(model)
            
            # Set up selection behavior
            self.duplicates_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) 
            self.duplicates_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            
            # Connect selection changed signal
            selection_model = self.duplicates_view.selectionModel()
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
        if duplicate_groups:
            total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
            status_text = self.tr("Found {} groups with {} duplicate files").format(
                len(duplicate_groups), 
                total_duplicates
            )
            # Force update the menu bar to ensure it's refreshed
            self.menuBar().update()
        else:
            status_text = self.tr("No duplicate files found.")
            
        self.status_label.setText(status_text)
        
        # Update UI state to reflect the new scan results
        self.update_ui_state()
        
        # Force a menu bar update to ensure all menu states are refreshed
        self.menuBar().repaint()
    
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
                file_menu = self.menuBar().findChild(QMenu, "file_menu")
                if file_menu:
                    self.recent_menu = file_menu.addMenu(self.tr("Recent Folders"))
                else:
                    logger.warning("Could not find File menu to add Recent Folders submenu")
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
    
    def closeEvent(self, event):
        """Handle the window close event."""
        try:
            logger.info("Application is shutting down")
            
            # Save window geometry and state
            settings_manager.window_geometry = self.saveGeometry()
            settings_manager.window_state = self.saveState()
            
            # Save current view state
            if hasattr(self, 'current_group_index'):
                settings_manager.set('current_group_index', self.current_group_index)
            if hasattr(self, 'current_file_index'):
                settings_manager.set('current_file_index', self.current_file_index)
            
            # Save settings
            settings_manager.save_settings()
            
            logger.info("Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {str(e)}")
            logger.debug(traceback.format_exc())
        
        event.accept()

    def on_pdf_viewer(self):
        """Open the PDF viewer dialog."""
        from script.PDF_viewer import show_pdf_viewer
        
        # Get the current file if available
        current_file = None
        if hasattr(self, 'current_file') and self.current_file:
            current_file = self.current_file
        
        # Show the PDF viewer
        viewer = show_pdf_viewer(current_file, self, self.language_manager)
        viewer.show()

    def on_markdown_docs(self):
        """Open the markdown documentation viewer."""
        from script.markdown_viewer import MarkdownViewer
        import os
        
        # Path to the documentation file
        docs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'documentation.md')
        
        # Check if file exists
        if not os.path.exists(docs_path):
            QMessageBox.warning(
                self,
                self.tr("Documentation Not Found"),
                self.tr("Could not find the documentation file at: {}").format(docs_path)
            )
            return
        
        # Create and show the markdown viewer
        self.markdown_viewer = MarkdownViewer(docs_path, self.language_manager, self)
        self.markdown_viewer.setWindowTitle(self.tr("Documentation"))
        self.markdown_viewer.show()

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
        f"{error_msg}\n\nPlease check the log file for more details."
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
