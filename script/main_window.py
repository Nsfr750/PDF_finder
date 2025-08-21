"""
Main window implementation with internationalization support.
"""
import os
import logging
from pathlib import Path
from typing import Callable, Optional, Dict, Any
import threading

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMenu, QWidget, QVBoxLayout, 
    QHBoxLayout, QSplitter, QListWidget, QLabel, QToolBar,
    QStatusBar, QApplication, QMenuBar, QFrame, QMessageBox, QDialog,
    QProgressBar, QListWidgetItem
)
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal as Signal, QObject, QTimer, Qt

# Import language manager
from script.lang_mgr import LanguageManager
from script.settings import AppSettings

# Set up logger
logger = logging.getLogger(__name__)

from .menu import MenuBar
from .toolbar import ToolBar
from .ui import MainUI
from .settings_dialog import SettingsDialog
from .PDF_viewer import show_pdf_viewer
from .scanner import PDFScanner

class MainWindow(QMainWindow):
    """Base main window class with internationalization support."""
    
    # Signal emitted when the language is changed
    language_changed = Signal()
    # Scan-related signals (thread-safe updates)
    scan_progress = Signal(int, int, str)  # current, total, path
    scan_status = Signal(str, int, int)    # message, current, total
    scan_finished = Signal()
    
    def __init__(self, parent: Optional[QObject] = None, language_manager: Optional[LanguageManager] = None):
        """Initialize the main window.
        
        Args:
            parent: Optional parent widget.
            language_manager: Optional LanguageManager instance. If not provided, a new one will be created.
        """
        super().__init__(parent)
        
        # PDF comparison settings
        self.comparison_threshold = 0.95  # Default similarity threshold (95%)
        self.comparison_dpi = 200  # Default DPI for image comparison
        
        # Initialize filter settings
        self.current_filters = {
            'min_size': 0,  # in bytes
            'max_size': 100 * 1024 * 1024,  # 100MB in bytes
            'date_from': None,
            'date_to': None,
            'name_pattern': '',
            'enable_text_compare': True,
            'min_similarity': 0.8
        }
        
        # Initialize settings
        self.settings = AppSettings()
        # Keep references to open viewers
        self._open_viewers = []
        # Scanner/thread refs
        self._scanner = None
        self._scan_thread = None
        
        # Initialize language manager
        self.language_manager = language_manager or LanguageManager(
            default_lang=self.settings.get_language() or 'en'
        )
        
        # Store a reference to the QApplication instance
        self.app = QApplication.instance()
        
        # Set up the UI
        self.setup_ui()
        
        # Connect to language change signals
        if hasattr(self.language_manager, 'language_changed'):
            self.language_manager.language_changed.connect(self.on_language_changed)
    
    def on_open_folder(self):
        """Handle the 'Open Folder' action from the menu."""
        try:
            # Open a directory dialog to select a folder
            folder_path = QFileDialog.getExistingDirectory(
                self,
                self.language_manager.tr("dialog.select_folder", "Select Folder"),
                "",
                QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontUseNativeDialog
            )
            
            if folder_path:
                # Update the status bar
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_scanning", "Scanning folder: %s") % folder_path
                )
                
                # Start scanning in background thread
                self._start_scan(folder_path)
                
                # Reset status bar after a delay
                QTimer.singleShot(3000, lambda: self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_ready", "Ready"))
                )
                
                QMessageBox.information(
                    self,
                    self.language_manager.tr("dialog.folder_selected", "Folder Selected"),
                    self.language_manager.tr("dialog.selected_folder", "Selected folder: %s") % folder_path
                )
                
        except Exception as e:
            logger.error(f"Error opening folder: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("dialog.error_opening_folder", "Error opening folder: %s") % str(e)
            )
    
    def on_select_all(self):
        """Handle the 'Select All' action from the menu."""
        try:
            # Get the main list widget from the UI
            if hasattr(self.main_ui, 'file_list'):
                self.main_ui.file_list.selectAll()
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_selected_all", "Selected all items")
                )
        except Exception as e:
            logger.error(f"Error selecting all items: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("dialog.error_selecting_all", "Error selecting all items: %s") % str(e)
            )
    
    def on_deselect_all(self):
        """Handle the 'Deselect All' action from the menu."""
        try:
            # Get the main list widget from the UI
            if hasattr(self.main_ui, 'file_list'):
                self.main_ui.file_list.clearSelection()
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_deselected_all", "Deselected all items")
                )
        except Exception as e:
            logger.error(f"Error deselecting all items: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("dialog.error_deselecting_all", "Error deselecting all items: %s") % str(e)
            )
    
    def on_toggle_toolbar(self):
        """Handle the 'Toggle Toolbar' action from the view menu."""
        try:
            # Toggle the visibility of the toolbar
            is_visible = not self.toolbar.isVisible()
            self.toolbar.setVisible(is_visible)
            
            # Update the action's checked state
            if hasattr(self, 'menu_bar') and 'toggle_toolbar' in self.menu_bar.actions:
                self.menu_bar.actions['toggle_toolbar'].setChecked(is_visible)
            
            # Save the toolbar visibility state to settings
            self.settings.set('ui.toolbar_visible', is_visible)
            
            # Update status bar
            status_message = (
                self.language_manager.tr("ui.toolbar_shown", "Toolbar shown") if is_visible else
                self.language_manager.tr("ui.toolbar_hidden", "Toolbar hidden")
            )
            self.status_bar.showMessage(status_message)
            
            # Reset status bar after a delay
            QTimer.singleShot(3000, lambda: self.status_bar.showMessage(
                self.language_manager.tr("ui.status_ready", "Ready"))
            )
            
        except Exception as e:
            logger.error(f"Error toggling toolbar: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("dialog.error_toggling_toolbar", "Error toggling toolbar: %s") % str(e)
            )
    
    def on_toggle_statusbar(self):
        """Handle the 'Toggle Status Bar' action from the view menu."""
        try:
            # Toggle the visibility of the status bar
            is_visible = not self.status_bar.isVisible()
            self.status_bar.setVisible(is_visible)
            
            # Update the action's checked state
            if hasattr(self, 'menu_bar') and 'toggle_statusbar' in self.menu_bar.actions:
                self.menu_bar.actions['toggle_statusbar'].setChecked(is_visible)
            
            # Save the status bar visibility state to settings
            self.settings.set('ui.statusbar_visible', is_visible)
            
            # Update status bar if it's visible
            if is_visible:
                status_message = self.language_manager.tr(
                    "ui.statusbar_shown", 
                    "Status bar shown"
                )
                self.status_bar.showMessage(status_message)
                
                # Reset status bar after a delay
                QTimer.singleShot(3000, lambda: self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_ready", "Ready"))
                )
            
        except Exception as e:
            logger.error(f"Error toggling status bar: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("dialog.error_toggling_statusbar", "Error toggling status bar: %s") % str(e)
            )
    
    def setup_ui(self):
        """Set up the main window UI."""
        # Set window properties
        self.setWindowTitle(self.language_manager.tr("main_window.title", "PDF Duplicate Finder"))
        self.setMinimumSize(1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create and set up the menu bar
        self.menu_bar = MenuBar(parent=self, language_manager=self.language_manager)
        self.menubar = self.menu_bar.menubar  # Store the QMenuBar instance
        self.setMenuBar(self.menubar)
        
        # Create and set up the toolbar
        self.toolbar = ToolBar(self, self.language_manager)
        self.toolbar.setObjectName("mainToolBar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Create the main UI
        self.main_ui = MainUI()
        
        # Add the main UI to the main layout
        main_layout.addWidget(self.main_ui)
        
        # Set up status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.language_manager.tr("ui.status_ready", "Ready"))
        # Progress bar in status bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.status_bar.addPermanentWidget(self.progress_bar, 1)
        
        # Connect signals
        self.setup_connections()
        
        # Apply initial settings
        self.apply_settings()
    
    def setup_connections(self):
        """Set up signal connections."""
        # Connect file list selection change if the UI has a file list
        if hasattr(self.main_ui, 'file_list'):
            self.main_ui.file_list.itemSelectionChanged.connect(self.on_file_selection_changed)
            # Open in viewer on double-click or Enter/Activation
            self.main_ui.file_list.itemDoubleClicked.connect(self.on_open_selected_in_viewer)
            self.main_ui.file_list.itemActivated.connect(self.on_open_selected_in_viewer)
        
        # Connect menu actions to toolbar
        if hasattr(self, 'menu_bar') and hasattr(self, 'toolbar'):
            # Get all available menu actions
            all_actions = {}
            for key, action in self.menu_bar.actions.items():
                if action is not None:
                    all_actions[key] = action
            
            # Add the actions to the toolbar
            self.toolbar.add_actions_from_menu(all_actions)
            
            # Connect toolbar toggle action
            if hasattr(self, 'on_toggle_toolbar'):
                self.menu_bar.actions.get('toggle_toolbar').toggled.connect(self.on_toggle_toolbar)

    def on_file_selection_changed(self):
        """Update preview and status when file selection changes."""
        try:
            if not hasattr(self, 'main_ui') or not hasattr(self.main_ui, 'file_list'):
                return
            lw = self.main_ui.file_list
            selected = lw.selectedItems()
            count = len(selected)
            if count == 0:
                if hasattr(self.main_ui, 'clear_preview'):
                    self.main_ui.clear_preview()
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(
                        self.language_manager.tr("ui.no_selection", "No item selected")
                    )
                return
            if count == 1:
                item = selected[0]
                path = item.data(Qt.ItemDataRole.UserRole)
                if path and hasattr(self.main_ui, 'update_preview'):
                    self.main_ui.update_preview(path)
                if hasattr(self, 'status_bar'):
                    name = os.path.basename(path) if path else item.text()
                    self.status_bar.showMessage(
                        self.language_manager.tr("ui.selected_one", "Selected: %s") % name
                    )
            else:
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(
                        self.language_manager.tr("ui.selected_many", "%d items selected") % count
                    )
        except Exception as e:
            logger.error(f"Error handling selection change: {e}", exc_info=True)

    def on_open_selected_in_viewer(self, item):
        """Open the currently selected PDF in the built-in viewer."""
        try:
            path = None
            if item is not None:
                path = item.data(Qt.ItemDataRole.UserRole)
            if not path and hasattr(self.main_ui, 'file_list'):
                current = self.main_ui.file_list.currentItem()
                if current is not None:
                    path = current.data(Qt.ItemDataRole.UserRole)
            if not path:
                return
                
            show_pdf_viewer(path, parent=self)
                
        except Exception as e:
            logger.error(f"Error opening viewer: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("errors.viewer_open_failed", "Could not open viewer: %s") % str(e)
            )
            
    def _update_duplicates_list(self):
        """Update the duplicates list widget with the current duplicate groups."""
        if not hasattr(self, 'duplicates_list'):
            return
            
        self.duplicates_list.clear()
        
        for i, group in enumerate(self.duplicate_groups, 1):
            # Create a group item
            group_item = QListWidgetItem()
            group_item.setData(Qt.ItemDataRole.UserRole, group)
            
            # Format the group header with enhanced information
            group_type = group.get('type', 'unknown')
            files_count = len(group['files'])
            
            # Create a more informative header
            header_parts = [f"Group {i}: {files_count} "]
            
            # Add type-specific information
            if group_type == 'content':
                header_parts.append(self.tr("main.duplicate_content", "duplicate files (exact content match)"))
            elif group_type == 'image':
                header_parts.append(self.tr("main.duplicate_images", "similar files (image comparison)"))
            elif group_type == 'searchable':
                header_parts.append(self.tr("main.duplicate_text", "similar text documents"))
            else:
                header_parts.append(self.tr("main.duplicate_files", "similar files"))
            
            # Add comparison method if available
            method = group.get('method', '')
            if method:
                method_display = {
                    'content_hash': self.tr("main.method_content_hash", "content hash"),
                    'image_hash': self.tr("main.method_image_hash", "image hash"),
                    'direct_comparison': self.tr("main.method_direct", "direct comparison")
                }.get(method, method)
                header_parts.append(f" ({method_display})")
            
            # Add similarity if available
            if 'similarity' in group:
                similarity = group['similarity']
                similarity_text = f" - {similarity*100:.1f}% {self.tr('main.similarity', 'similar')}"
                
                # Color code based on similarity
                if similarity > 0.9:
                    similarity_text = f"<span style='color: #2ecc71;'>{similarity_text}</span>"
                elif similarity > 0.7:
                    similarity_text = f"<span style='color: #f39c12;'>{similarity_text}</span>"
                else:
                    similarity_text = f"<span style='color: #e74c3c;'>{similarity_text}</span>"
                
                header_parts.append(similarity_text)
            
            # Set the formatted text
            group_item.setText("".join(header_parts))
            
            # Add tooltip with more details
            tooltip_parts = [
                f"<b>{self.tr('main.group', 'Group')} {i}: {files_count} {self.tr('main.files', 'files')}</b>",
                f"<b>{self.tr('main.type', 'Type')}:</b> {group_type}",
                f"<b>{self.tr('main.method', 'Method')}:</b> {method}"
            ]
            
            if 'similarity' in group:
                tooltip_parts.append(f"<b>{self.tr('main.similarity', 'Similarity')}:</b> {group['similarity']*100:.1f}%")
            
            if 'details' in group and 'message' in group['details']:
                tooltip_parts.append(f"<b>{self.tr('main.notes', 'Notes')}:</b> {group['details']['message']}")
            
            group_item.setToolTip("<br>".join(tooltip_parts))
            
            # Add the item to the list
            self.duplicates_list.addItem(group_item)
            # Save all settings to disk
            self.settings._save_settings()
            

    def on_show_filter_dialog(self):
        """Show the filter dialog and apply selected filters."""
        try:
            from script.filter_dialog import FilterDialog
            
            dialog = FilterDialog(self)
            dialog.set_filters(self.current_filters)
            
            def on_filters_changed():
                # Update current filters when they change
                self.current_filters.update(dialog.get_filters())
                
            dialog.filters_changed.connect(on_filters_changed)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Update current filters with the final values
                self.current_filters.update(dialog.get_filters())
                self.status_bar.showMessage(
                    self.language_manager.tr("filters.applied", "Filters applied"), 
                    3000
                )
                
        except Exception as e:
            logger.error(f"Error showing filter dialog: {e}")
            QMessageBox.critical(
                self,
                self.language_manager.tr("error.title", "Error"),
                self.language_manager.tr("error.filter_dialog", "Failed to open filter dialog: {error}").format(error=str(e))
            )
    
    def on_show_settings(self):
        """Open the settings dialog and wire its signals."""
        try:
            dialog = SettingsDialog(self)  # Pass parent directly
            
            # Connect settings changed signal
            callback = getattr(self, 'on_settings_changed', self.apply_settings)
            dialog.settings_changed.connect(callback)
            
            # Connect language changed signal
            def lang_changed():
                if hasattr(dialog, 'language_combo'):
                    self.change_language(dialog.language_combo.currentData())
            
            dialog.language_changed.connect(lang_changed)
            dialog.requires_restart.connect(lambda: None)
            
            dialog.exec()
            
        except Exception as e:
            logger.error("Error in settings dialog: %s", e, exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Error"),
                f"Could not open settings: {e}"
            )
