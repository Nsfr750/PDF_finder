"""
Main window implementation with internationalization support.
"""
import os
import logging
from pathlib import Path
from typing import Callable, Optional, Dict, Any
import threading
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMenu, QWidget, QVBoxLayout, 
    QHBoxLayout, QSplitter, QListWidget, QLabel, QToolBar,
    QStatusBar, QApplication, QMenuBar, QFrame, QMessageBox, QDialog,
    QProgressBar, QListWidgetItem
)
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal as Signal, QObject, QTimer, Qt

# Import language manager
from ..lang.lang_manager import SimpleLanguageManager
from ..utils.settings import AppSettings

# Set up logger
logger = logging.getLogger(__name__)

from .menu import MenuBar
from .toolbar import MainToolBar as ToolBar
from .ui import MainUI
from .settings_dialog import SettingsDialog
from .PDF_viewer import show_pdf_viewer
from ..utils.scanner import PDFScanner

class MainWindow(QMainWindow):
    """Base main window class with internationalization support."""
    
    # Signal emitted when the language is changed
    language_changed = Signal(str)  # Emits the new language code
    # Scan-related signals (thread-safe updates)
    scan_progress = Signal(int, int, str)  # current, total, path
    scan_status = Signal(str, int, int)    # message, current, total
    scan_finished = Signal()
    
    def __init__(self, parent: Optional[QObject] = None, language_manager: Optional[SimpleLanguageManager] = None):
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
        self.language_manager = language_manager or SimpleLanguageManager(
            default_lang=self.settings.get_language() or 'en'
        )
        
        # Store a reference to the QApplication instance
        self.app = QApplication.instance()
        
        # Set up the UI
        self.setup_ui()
        
        # Connect to language change signals
        if hasattr(self.language_manager, 'language_changed'):
            self.language_manager.language_changed.connect(self.on_language_changed)
        
        # Connect to our own language changed signal
        self.language_changed.connect(self.on_language_changed)
    
    def change_language(self, lang_code: str) -> bool:
        """Change the application language.
        
        Args:
            lang_code: The language code to change to (e.g., 'en', 'it')
            
        Returns:
            bool: True if the language was changed successfully, False otherwise
        """
        logger.debug(f"MainWindow.change_language called with: {lang_code}")
        logger.debug(f"Current language_manager language: {self.language_manager.current_lang}")
        
        if self.language_manager.set_language(lang_code):
            logger.debug(f"LanguageManager.set_language succeeded for: {lang_code}")
            # Save the language preference
            self.settings.set('app.language', lang_code)
            # Emit the language changed signal with the language code
            logger.debug(f"Emitting MainWindow.language_changed signal with: {lang_code}")
            self.language_changed.emit(lang_code)
            return True
        else:
            logger.debug(f"LanguageManager.set_language failed for: {lang_code}")
            return False
    
    def on_language_changed(self, language_code: str = None):
        """Handle language change events.
        
        This method is called when the application language is changed.
        It updates all UI elements to reflect the new language.
        
        Args:
            language_code: The language code that was changed to (e.g., 'en', 'it')
        """
        try:
            logger.debug(f"MainWindow.on_language_changed called with: {language_code}")
            logger.debug(f"Current language_manager language: {self.language_manager.current_lang}")
            
            # Update the language in the language manager if a new code is provided
            if language_code and language_code != self.language_manager.current_lang:
                logger.debug(f"Updating language_manager from {self.language_manager.current_lang} to {language_code}")
                self.language_manager.current_lang = language_code
                
            # Retranslate the UI
            if hasattr(self, 'menu_bar') and hasattr(self.menu_bar, 'retranslate_ui'):
                logger.debug("Calling menu_bar.retranslate_ui()")
                self.menu_bar.retranslate_ui()
            else:
                logger.debug("menu_bar or retranslate_ui not found")
                
            # Update the window title
            logger.debug("Updating window title")
            self.setWindowTitle(self.language_manager.tr("main_window.title"))
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                logger.debug("Updating status bar")
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_ready")
                )
            else:
                logger.debug("status_bar not found")
                
            # Update toolbar
            if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'retranslate_ui'):
                logger.debug("Calling toolbar.retranslate_ui()")
                self.toolbar.retranslate_ui()
            else:
                logger.debug("toolbar or retranslate_ui not found")
                
            # Update the main UI components
            if hasattr(self, 'main_ui') and hasattr(self.main_ui, 'on_language_changed'):
                self.main_ui.on_language_changed()
            else:
                logger.debug("main_ui or on_language_changed not found")
                
            logger.info(f"Language changed to: {self.language_manager.current_lang}")
            
        except Exception as e:
            logger.error(f"Error updating UI for language change: {e}")
            import traceback
            traceback.print_exc()   
    
    def on_open_folder(self):
        """Handle the 'Open Folder' action from the menu."""
        try:
            logger.debug("on_open_folder: Starting folder selection process")
            
            # Open a directory dialog to select a folder
            logger.debug("on_open_folder: Opening directory dialog")
            folder_path = QFileDialog.getExistingDirectory(
                self,
                self.language_manager.tr("dialog.select_folder", "Select Folder"),
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            
            logger.debug(f"on_open_folder: Selected folder path: {folder_path}")
            
            if folder_path:
                logger.debug(f"on_open_folder: Processing selected folder: {folder_path}")
                
                # Update the status bar
                logger.debug("on_open_folder: Updating status bar")
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_scanning", "Scanning folder: %s") % folder_path
                )
                
                # Start scanning in background thread
                logger.debug("on_open_folder: Starting scan process")
                self._start_scan(folder_path)
                
                # Reset status bar after a delay
                logger.debug("on_open_folder: Setting status bar reset timer")
                QTimer.singleShot(3000, lambda: self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_ready")
                ))
                
                # Show folder selected message
                logger.debug("on_open_folder: Showing folder selected message")
                QMessageBox.information(
                    self,
                    self.language_manager.tr("dialog.folder_selected", "Folder Selected"),
                    self.language_manager.tr("dialog.selected_folder", "Selected folder: %s") % folder_path
                )
                
                logger.debug("on_open_folder: Folder selection process completed successfully")
            else:
                logger.debug("on_open_folder: No folder selected, process cancelled")
                
        except Exception as e:
            logger.error(f"Error in on_open_folder: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("errors.folder_open_failed", "Failed to open folder: %s") % str(e)
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
                self.language_manager.tr("ui.status_ready")
            ))
            
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
                    self.language_manager.tr("ui.status_ready")
                ))
            
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
        self.setWindowTitle(self.language_manager.tr("main_window.title"))
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
        
        # Create the main UI with the central widget as parent and shared language manager
        self.main_ui = MainUI(central_widget, self.language_manager)
        
        # Connect UI signals to main window methods
        self.main_ui.delete_selected.connect(self.on_delete_selected)
        
        # Add the main UI to the main layout
        main_layout.addWidget(self.main_ui)
        
        # Set up status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.language_manager.tr("ui.status_ready"))
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
    
    def apply_settings(self):
        """Apply initial settings to the main window."""
        logger.debug("MainWindow.apply_settings() called")
        try:
            # Apply window settings
            if hasattr(self.settings, 'get_window_geometry'):
                geometry = self.settings.get_window_geometry()
                if geometry:
                    self.restoreGeometry(geometry)
            
            if hasattr(self.settings, 'get_window_state'):
                state = self.settings.get_window_state()
                if state:
                    self.restoreState(state)
            
            # Apply theme settings if available
            if hasattr(self.settings, 'get_theme'):
                theme = self.settings.get_theme()
                if theme:
                    self.app.setStyle(theme)
            
            logger.debug("Settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}", exc_info=True)
    
    def setup_connections(self):
        """Set up signal connections."""
        # Connect file list selection change if the UI has a file list
        if hasattr(self.main_ui, 'file_list'):
            self.main_ui.file_list.itemSelectionChanged.connect(self.on_file_selection_changed)
        
        # Connect scan status signals
        self.scan_status.connect(self.on_scan_status)
        self.scan_progress.connect(self.on_scan_progress)
        
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
    
    def on_scan_status(self, message: str, current: int, total: int):
        """Handle scan status updates.
        
        Args:
            message: Status message to display
            current: Current progress value
            total: Total progress value
        """
        try:
            # Update status bar with the message
            self.status_bar.showMessage(message)
            
            # Update progress bar if we have valid progress values
            if total > 0:
                self.progress_bar.setVisible(True)
                self.progress_bar.setMaximum(total)
                self.progress_bar.setValue(current)
                
                # Calculate percentage for progress bar text
                if total > 0:
                    percentage = int((current / total) * 100)
                    self.progress_bar.setFormat(f"{percentage}% ({current}/{total})")
                else:
                    self.progress_bar.setFormat(f"{current}/{total}")
            else:
                # Hide progress bar if no valid progress
                self.progress_bar.setVisible(False)
                
            logger.debug(f"Scan status: {message} ({current}/{total})")
            
        except Exception as e:
            logger.error(f"Error updating scan status: {e}", exc_info=True)
    
    def on_scan_progress(self, current: int, total: int, current_file: str):
        """Handle scan progress updates.
        
        Args:
            current: Current progress value
            total: Total progress value
            current_file: Path to the current file being processed
        """
        try:
            # Update progress bar
            if total > 0:
                self.progress_bar.setVisible(True)
                self.progress_bar.setMaximum(total)
                self.progress_bar.setValue(current)
                
                # Calculate percentage for progress bar text
                percentage = int((current / total) * 100)
                filename = os.path.basename(current_file) if current_file else ""
                self.progress_bar.setFormat(f"{percentage}% ({current}/{total}) - {filename}")
                
                # Update status bar with current file info
                self.status_bar.showMessage(
                    self.language_manager.tr("main.processing_file", "Processing: {file}").format(file=filename)
                )
            else:
                self.progress_bar.setVisible(False)
                
            logger.debug(f"Scan progress: {current}/{total} - {current_file}")
            
        except Exception as e:
            logger.error(f"Error updating scan progress: {e}", exc_info=True)

    def on_delete_selected(self):
        """Handle deletion of selected files."""
        logger.info("on_delete_selected method called")
        try:
            # Check for selected items in both file_list and duplicates_tree
            selected_items = self.main_ui.file_list.selectedItems()
            selected_tree_items = self.main_ui.duplicates_tree.selectedItems()
            
            logger.info(f"Selected items in file_list: {len(selected_items)}")
            logger.info(f"Selected items in duplicates_tree: {len(selected_tree_items)}")
            
            if not selected_items and not selected_tree_items:
                logger.info("No files selected for deletion")
                return

            # Get file paths from file_list
            file_paths = []
            for item in selected_items:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path:
                    file_paths.append(file_path)
            
            # Get file paths from duplicates_tree
            logger.info(f"Extracting file paths from {len(selected_tree_items)} tree items...")
            for i, item in enumerate(selected_tree_items):
                file_path = item.data(Qt.ItemDataRole.UserRole)
                logger.info(f"Tree item {i}: file_path = {file_path}")
                if file_path:
                    file_paths.append(file_path)
                else:
                    logger.warning(f"Tree item {i} has no file path in UserRole")
            
            logger.info(f"Total file paths extracted: {len(file_paths)}")
            if not file_paths:
                logger.info("No valid file paths found in selected items")
                return

            # Import delete function
            from script.utils.delete import delete_files

            # Let delete_files handle the confirmation dialog
            success, failed = delete_files(
                file_paths,
                parent=self,
                use_recycle_bin=self.settings.get('deletion.use_recycle_bin', True)
            )

            # Update UI based on results
            if success > 0:
                self.status_bar.showMessage(
                    self.language_manager.tr(
                        "status.deleted_success",
                        "Successfully moved {count} file(s) to Recycle Bin"
                    ).format(count=success)
                )
                
                # Remove only items corresponding to files that were actually deleted
                # Check which files no longer exist and remove their corresponding items
                
                # Remove from file_list
                for item in list(selected_items): # Make a copy for safe iteration
                    file_path = item.data(Qt.ItemDataRole.UserRole)
                    if file_path and not os.path.exists(file_path):
                        row = self.main_ui.file_list.row(item)
                        if row >= 0:
                            self.main_ui.file_list.takeItem(row)
                            logger.info(f"Removed deleted file from file_list: {file_path}")
                
                # Remove from duplicates_tree
                for item in list(selected_tree_items): # Make a copy for safe iteration
                    file_path = item.data(Qt.ItemDataRole.UserRole)
                    if file_path and not os.path.exists(file_path):
                        parent = item.parent()
                        if parent:
                            # Remove from parent (group)
                            parent.removeChild(item)
                            logger.info(f"Removed deleted file from duplicates_tree: {file_path}")
                            # If parent has no more children, remove the parent too
                            if parent.childCount() == 0:
                                root = self.main_ui.duplicates_tree.invisibleRootItem()
                                root.removeChild(parent)
                                logger.info(f"Removed empty parent group from duplicates_tree")
                        else:
                            # Remove top-level item
                            root = self.main_ui.duplicates_tree.invisibleRootItem()
                            root.removeChild(item)
                            logger.info(f"Removed deleted top-level item from duplicates_tree: {file_path}")

            if failed > 0:
                QMessageBox.warning(
                    self,
                    self.language_manager.tr("dialog.delete_error_title", "Deletion Incomplete"),
                    self.language_manager.tr(
                        "dialog.delete_error_msg",
                        "Failed to delete {failed} of {total} file(s)."
                    ).format(failed=failed, total=len(file_paths))
                )

        except Exception as e:
            logger.error(f"Error during file deletion: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("errors.delete_failed", "An unexpected error occurred: %s") % str(e)
            )
    
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
            from .filter_dialog import FilterDialog
            
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
                self.language_manager.tr("error.filter_dialog").format(error=str(e))
            )
    
    def on_show_settings(self):
        """Show the settings dialog and handle language changes."""
        logger.debug("MainWindow.on_show_settings() called")
        try:
            # Create and show the settings dialog
            logger.debug("Creating SettingsDialog")
            dialog = SettingsDialog(self, self.language_manager)
            logger.debug("SettingsDialog created")
            
            # The on_language_changed will be called automatically by the signal
            logger.debug(f"Language change signal processed")
            
            # Connect to language change signal from settings dialog
            dialog.language_changed.connect(self._handle_settings_language_change)
            
            # Show the dialog
            result = dialog.exec()
            
        except Exception as e:
            logger.error(f"Error showing settings dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error"),
                self.language_manager.tr("errors.settings_open_failed") % str(e)
            )
    
    def _handle_settings_language_change(self, language_code: str):
        """Handle language change from settings dialog.
        
        Args:
            language_code: The new language code
        """
        logger.debug(f"Handling language change from settings dialog: {language_code}")
        try:
            # Update the language manager
            if self.language_manager:
                self.language_manager.set_language(language_code)
                
            # Save the language setting
            self.settings.set_language(language_code)
                
            # Emit our own language changed signal
            self.language_changed.emit(language_code)
                
            logger.debug(f"Language changed to: {language_code}")
            
        except Exception as e:
            logger.error(f"Error handling language change: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error"),
                self.language_manager.tr("errors.language_change_failed") % str(e)
            )

    def on_show_cache_manager(self):
        """Show the cache manager dialog."""
        logger.debug("MainWindow.on_show_cache_manager() called")
        try:
            # Initialize scanner if it doesn't exist
            if not hasattr(self, '_scanner') or self._scanner is None:
                logger.debug("Scanner not initialized, creating new one for cache manager")
                enable_hash_cache = self.settings.get('enable_hash_cache', True)
                cache_dir = self.settings.get('cache_dir', None)
                threshold = self.settings.get('scan_threshold', 0.95)
                dpi = self.settings.get('scan_dpi', 150)
                
                # Create scanner with settings
                self._scanner = PDFScanner(
                    threshold=threshold,
                    dpi=dpi,
                    enable_hash_cache=enable_hash_cache,
                    cache_dir=cache_dir,
                    language_manager=self.language_manager
                )
            
            # Check if scanner has hash cache
            if not self._scanner.hash_cache:
                QMessageBox.information(
                    self,
                    self.language_manager.tr("cache_manager.title"),
                    self.language_manager.tr("cache_manager.not_available")
                )
                return
            
            # Get current settings
            current_settings = {
                'enable_hash_cache': self.settings.get('enable_hash_cache', True),
                'cache_dir': self.settings.get('cache_dir', None),
                'max_cache_size': self.settings.get('max_cache_size', 10000),
                'cache_ttl_days': self.settings.get('cache_ttl_days', 30),
                'memory_cache_size': self.settings.get('memory_cache_size', 1000)
            }
            
            # Create and show the cache manager dialog
            from .cache_manager import CacheManagerDialog
            dialog = CacheManagerDialog(
                hash_cache=self._scanner.hash_cache,
                current_settings=current_settings,
                parent=self
            )
            
            # Connect signals
            dialog.settings_changed.connect(self.on_cache_settings_changed)
            dialog.cache_cleared.connect(self.on_cache_cleared)
            
            # Show the dialog
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error showing cache manager dialog: {e}", exc_info=True)
            error_msg = self.language_manager.tr("errors.cache_manager_open_failed")
            if "{error}" in error_msg:
                error_msg = error_msg.format(error=str(e))
            else:
                error_msg = f"{error_msg}: {str(e)}"
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error"),
                error_msg
            )
    
    def on_cache_settings_changed(self, settings: Dict[str, Any]):
        """Handle cache settings changes."""
        logger.debug(f"Cache settings changed: {settings}")
        try:
            # Update settings
            for key, value in settings.items():
                self.settings.set(key, value)
            
            # Show info message
            QMessageBox.information(
                self,
                self.language_manager.tr("cache_manager.settings_changed"),
                self.language_manager.tr("cache_manager.settings_changed_message")
            )
            
        except Exception as e:
            logger.error(f"Error updating cache settings: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error"),
                self.language_manager.tr("errors.cache_settings_update_failed") % str(e)
            )
    
    def on_cache_cleared(self):
        """Handle cache cleared event."""
        logger.debug("Cache cleared")
        try:
            # Show info message
            QMessageBox.information(
                self,
                self.language_manager.tr("cache_manager.cache_cleared"),
                self.language_manager.tr("cache_manager.cache_cleared_message")
            )
            
        except Exception as e:
            logger.error(f"Error handling cache cleared event: {e}", exc_info=True)
    
    def _start_scan(self, folder_path: str):
        """Start the PDF scanning process.
        
        Args:
            folder_path: Path to the folder to scan
        """
        try:
            logger.debug(f"_start_scan: Starting scan process for folder: {folder_path}")
            
            # Get scanner settings from settings
            logger.debug("_start_scan: Getting scanner settings")
            threshold = self.settings.get('similarity_threshold', 0.95)
            dpi = self.settings.get('scan_dpi', 150)
            logger.debug(f"_start_scan: Settings - threshold: {threshold}, dpi: {dpi}")
            
            # Check if scanner is already initialized
            logger.debug("_start_scan: Checking scanner initialization")
            if not hasattr(self, '_scanner') or self._scanner is None:
                logger.debug("_start_scan: Scanner not initialized, creating new one")
                enable_hash_cache = self.settings.get('enable_hash_cache', True)
                cache_dir = self.settings.get('cache_dir', None)
                logger.debug(f"_start_scan: Cache settings - enabled: {enable_hash_cache}, dir: {cache_dir}")
                
                # Create scanner with settings
                logger.debug("_start_scan: Creating new PDFScanner instance")
                self._scanner = PDFScanner(
                    threshold=threshold,
                    dpi=dpi,
                    enable_hash_cache=enable_hash_cache,
                    cache_dir=cache_dir,
                    language_manager=self.language_manager
                )
                logger.debug("_start_scan: PDFScanner instance created successfully")
            else:
                logger.debug("_start_scan: Using existing scanner")
                # Update scanner settings if needed
                self._scanner.threshold = threshold
                self._scanner.dpi = dpi
            
            # Set up scan parameters
            logger.debug("_start_scan: Setting up scan parameters")
            self._scanner.scan_parameters = {
                'directory': folder_path,
                'recursive': True,
                'min_file_size': 1024,  # 1KB
                'max_file_size': 1024 * 1024 * 1024,  # 1GB
                'min_similarity': 0.8,
                'enable_text_compare': True
            }
            logger.debug("_start_scan: Scan parameters set up successfully")
            
            # Connect scanner signals to main window signals
            logger.debug("_start_scan: Connecting scanner signals")
            self._scanner.status_updated.connect(self.scan_status)
            self._scanner.progress_updated.connect(self.scan_progress)
            self._scanner.duplicates_found.connect(self._on_duplicates_found)
            self._scanner.finished.connect(self._on_scan_finished)
            logger.debug("_start_scan: Scanner signals connected successfully")
            
            # Create and start scan thread
            logger.debug("_start_scan: Creating scan thread")
            from PyQt6.QtCore import QThread
            self._scan_thread = QThread()
            self._scanner.moveToThread(self._scan_thread)
            logger.debug("_start_scan: Scanner moved to thread")
            
            # Connect thread signals
            logger.debug("_start_scan: Connecting thread signals")
            self._scan_thread.started.connect(self._scanner.start_scan)
            self._scanner.finished.connect(self._scan_thread.quit)
            self._scanner.finished.connect(self._scanner.deleteLater)
            self._scan_thread.finished.connect(self._scan_thread.deleteLater)
            logger.debug("_start_scan: Thread signals connected successfully")
            
            # Start the thread
            logger.debug("_start_scan: Starting scan thread")
            self._scan_thread.start()
            logger.debug("_start_scan: Scan thread started successfully")
            
            logger.info(f"Scan started for folder: {folder_path}")
            
        except Exception as e:
            logger.error(f"Error in _start_scan: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("errors.scan_start_failed", "Failed to start scan: %s") % str(e)
            )
    
    def _on_duplicates_found(self, duplicates):
        """Handle when duplicates are found during scanning.
        
        Args:
            duplicates: List of duplicate groups
        """
        logger.debug(f"Duplicates found: {len(duplicates)} groups")
        # This method should be implemented to handle displaying duplicates
        # For now, just log the finding
        
    def _on_scan_finished(self, duplicates):
        """Handle when scan is finished.
        
        Args:
            duplicates: List of duplicate groups
        """
        logger.debug(f"Scan finished with {len(duplicates)} duplicate groups")
        
        try:
            # Store the duplicates for later use
            self.duplicate_groups = duplicates
            
            # Hide progress bar and reset status bar
            self.progress_bar.setVisible(False)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage(self.language_manager.tr("ui.status_ready"))
            
            # Update the duplicates list and file list
            self._update_duplicates_list()
            
            # Update the UI with the duplicates
            if hasattr(self.main_ui, 'update_duplicates_tree'):
                self.main_ui.update_duplicates_tree(duplicates)
            
            # Emit scan finished signal
            self.scan_finished.emit()
            
            logger.info("Scan completed successfully")
            
        except Exception as e:
            logger.error(f"Error finishing scan: {e}", exc_info=True)
