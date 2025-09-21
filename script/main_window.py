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
from script.lang_mgr import LanguageManager
from script.settings import AppSettings

# Set up logger
logger = logging.getLogger(__name__)

from .menu import MenuBar
from .toolbar import MainToolBar as ToolBar
from .ui import MainUI
from .settings_dialog import SettingsDialog
from .PDF_viewer import show_pdf_viewer
from .scanner import PDFScanner
from .updates import UpdateDataManager

class MainWindow(QMainWindow):
    """Base main window class with internationalization support."""
    
    # Signal emitted when the language is changed
    language_changed = Signal(str)  # Emits the new language code
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
        
        # Connect the language_changed signal to the on_language_changed slot
        self.language_changed.connect(self.on_language_changed)
            
        # Initialize update manager and check for updates on startup
        self.update_manager = UpdateDataManager("config")
        self.check_for_updates()
    
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
                
            # Update the window title
            logger.debug("Updating window title")
            self.setWindowTitle(self.language_manager.tr("main_window.title", "PDF Duplicate Finder"))
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                logger.debug("Updating status bar")
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_ready", "Ready")
                )
                
            # Update toolbar
            if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'retranslate_ui'):
                logger.debug("Calling toolbar.retranslate_ui()")
                self.toolbar.retranslate_ui()
                
            # Update main UI
            if hasattr(self, 'main_ui') and hasattr(self.main_ui, 'on_language_changed'):
                logger.debug("Calling main_ui.on_language_changed()")
                self.main_ui.on_language_changed()
                
            logger.info(f"Language changed to: {self.language_manager.current_lang}")
            
        except Exception as e:
            logger.error(f"Error updating UI for language change: {e}")
            import traceback
            traceback.print_exc()
    
    def check_for_updates(self):
        """Check for application updates."""
        try:
            # Get current version (you'll need to import your version)
            from script.version import __version__ as current_version
            
            # Check if we already have a recent update check
            last_check = self.update_manager.get_last_check()
            if last_check and (datetime.now() - last_check).days < 1:  # Check once per day
                logger.debug("Skipping update check - already checked today")
                return
                
            # In a real app, you would fetch this from your update server
            # For now, we'll just demonstrate the data structure
            update_data = {
                "version": "1.1.0",  # Example new version
                "release_notes": "New features and improvements",
                "download_url": "https://github.com/yourusername/yourrepo/releases/latest",
                "release_date": "2025-08-22"
            }
            
            # Save the update check
            self.update_manager.save_update_check(
                version=current_version,
                update_available=True,  # In a real app, compare versions
                update_data=update_data
            )
            
            # Notify user if update is available
            if self.update_manager.is_update_available():
                update_info = self.update_manager.get_update_data()
                QMessageBox.information(
                    self,
                    self.tr("Update Available"),
                    self.tr("Version {0} is now available!\n\n{1}").format(
                        update_info.get('version', '1.0.0'),
                        update_info.get('release_notes', '')
                    )
                )
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            # Don't show error to user for failed update checks
    
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
        
        # Create the main UI with the central widget as parent and shared language manager
        self.main_ui = MainUI(central_widget, self.language_manager)
        
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

    def on_delete_selected(self):
        """Handle deletion of selected files."""
        try:
            selected_items = self.main_ui.file_list.selectedItems()
            if not selected_items:
                return

            file_paths = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items if item.data(Qt.ItemDataRole.UserRole)]
            if not file_paths:
                return

            # Import delete function
            from script.delete import delete_files

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
                # A more robust way to remove items from the list
                for item in list(selected_items): # Make a copy for safe iteration
                    row = self.main_ui.file_list.row(item)
                    if row >= 0:
                        self.main_ui.file_list.takeItem(row)

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
        """Show the settings dialog and handle language changes."""
        print("DEBUG: MainWindow.on_show_settings() called")
        logger.debug("MainWindow.on_show_settings() called")
        try:
            # Store current language to detect changes
            current_lang = self.language_manager.current_lang
            print(f"DEBUG: Current language before opening settings: {current_lang}")
            logger.debug(f"Current language before opening settings: {current_lang}")
            language_changed = False
            
            # Create and show the settings dialog
            print("DEBUG: Creating SettingsDialog")
            logger.debug("Creating SettingsDialog")
            dialog = SettingsDialog(self, self.language_manager)
            print("DEBUG: SettingsDialog created")
            logger.debug("SettingsDialog created")
            
            # Connect to the language_changed signal
            def on_language_changed(lang_code):
                nonlocal language_changed
                if lang_code and lang_code != self.language_manager.current_lang:
                    logger.debug(f"Language changed to: {lang_code}")
                    if self.change_language(lang_code):
                        language_changed = True
                        # Update the UI immediately
                        self.on_language_changed(lang_code)
            
            # Connect signals
            dialog.language_changed.connect(on_language_changed)
            
            # Show the dialog
            result = dialog.exec()
            
            # If settings were saved and language changed, ensure UI is updated
            if result == QDialog.DialogCode.Accepted and language_changed:
                logger.debug("Settings saved with language change")
                # The UI is already updated via the signal handler
                # Just show a message to the user
                QMessageBox.information(
                    self,
                    self.language_manager.tr("settings_dialog.language_changed", "Language Changed"),
                    self.language_manager.tr(
                        "settings_dialog.restart_for_full_effect",
                        "The application language has been changed. Some changes may require a restart to take full effect."
                    )
                )
            
        except Exception as e:
            logger.error(f"Error showing settings dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("errors.settings_open_failed", "Could not open settings: %s") % str(e)
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
        

def on_language_changed(self):
    """Handle language change events.
    
    This method is called when the application language is changed.
    It updates all UI elements to reflect the new language.
    """
    try:
        # Retranslate the UI
        if hasattr(self, 'menu_bar') and hasattr(self.menu_bar, 'retranslate_ui'):
            self.menu_bar.retranslate_ui()
            
        # Update the window title
        self.setWindowTitle(self.language_manager.tr("main_window.title", "PDF Duplicate Finder"))
        
        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(
                self.language_manager.tr("ui.status_ready", "Ready")
            )
            
        # Update any other UI elements that need to be retranslated
        if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'retranslate_ui'):
            self.toolbar.retranslate_ui()
            
        logger.info(f"Language changed to: {self.language_manager.current_lang}")
        
    except Exception as e:
        logger.error(f"Error updating UI for language change: {e}")
        import traceback
        traceback.print_exc()
