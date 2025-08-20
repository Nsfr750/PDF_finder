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
from .toolbar import MainToolBar
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
        self.setMenuBar(self.menu_bar.menubar)
        
        # Create and set up the toolbar
        self.toolbar = MainToolBar(self, self.language_manager)
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
            # Get menu actions that should be in the toolbar
            toolbar_actions = {
                'open_folder': self.menu_bar.actions.get('open_folder'),
                'select_all': self.menu_bar.actions.get('select_all'),
                'deselect_all': self.menu_bar.actions.get('deselect_all'),
                'delete_selected': self.menu_bar.actions.get('delete_selected')
            }
            # Add actions to toolbar
            self.toolbar.add_actions_from_menu(toolbar_actions)
            
        # Connect other signals
        if hasattr(self, 'language_changed'):
            self.language_changed.connect(self.retranslate_ui)
        # Scan signals
        self.scan_progress.connect(self._on_scan_progress)
        self.scan_status.connect(self._on_scan_status)
        self.scan_finished.connect(self._on_scan_finished)

    def _start_scan(self, folder_path: str):
        """Start scanning the given folder in a background thread."""
        try:
            # If a scan is already running, ignore
            if self._scan_thread and self._scan_thread.is_alive():
                return
            # Create scanner and wire callbacks
            self._scanner = PDFScanner()
            self._scanner.progress_callback = lambda current, total, path: self.scan_progress.emit(current, total, path or "")
            self._scanner.status_callback = lambda message, current, total: self.scan_status.emit(str(message or ""), int(current or 0), int(total or 0))
            # Optional: capture found duplicates as they appear (no UI hookup yet)
            self._scanner.found_callback = lambda group: None
            
            # Prepare progress bar UI
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(True)
                self.progress_bar.setMinimum(0)
                self.progress_bar.setMaximum(0)  # Indeterminate until we know total
                self.progress_bar.setFormat(self.language_manager.tr("ui.progress_scanning", "Scanning..."))
            
            # Run scan in a background thread
            self._scan_thread = threading.Thread(target=self._scan_worker, args=(folder_path,), daemon=True)
            self._scan_thread.start()
        except Exception as e:
            logger.error(f"Failed to start scan: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("errors.scan_start_failed", "Failed to start scan: %s") % str(e)
            )

    def _scan_worker(self, folder_path: str):
        """Worker function executed in a background thread."""
        try:
            self._scanner.scan_directory(folder_path, recursive=True)
        except Exception as e:
            logger.error(f"Scan errored: {e}", exc_info=True)
        finally:
            # Notify UI that scanning finished
            self.scan_finished.emit()

    def _on_scan_progress(self, current: int, total: int, path: str):
        """UI thread: update progress bar based on progress callback."""
        try:
            if not hasattr(self, 'progress_bar'):
                return
            # Switch to determinate once total known
            if total and self.progress_bar.maximum() != total:
                self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(max(0, int(current)))
            base = os.path.basename(path) if path else ""
            fmt = self.language_manager.tr("ui.progress_format", "%d/%d %s")
            self.progress_bar.setFormat(fmt % (current, total, base))
            # Keep status message informative
            if base:
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_processing", "Processing: %s") % base
                )
        except Exception as e:
            logger.debug(f"Progress update failed: {e}")

    def _on_scan_status(self, message: str, current: int, total: int):
        """UI thread: update status text and optionally bar range/value."""
        try:
            if hasattr(self, 'status_bar') and message:
                self.status_bar.showMessage(str(message))
            if hasattr(self, 'progress_bar') and total:
                if self.progress_bar.maximum() != total:
                    self.progress_bar.setMaximum(int(total))
                self.progress_bar.setValue(int(current))
        except Exception as e:
            logger.debug(f"Status update failed: {e}")

    def _on_scan_finished(self):
        """UI thread: finalize progress UI when scan completes."""
        try:
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(self.progress_bar.maximum())
                # Hide after short delay to let user see completion
                QTimer.singleShot(800, lambda: self.progress_bar.setVisible(False))
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_scan_complete", "Scan complete")
                )
            # Populate file list with results
            self._populate_file_list_from_scanner()
        except Exception as e:
            logger.debug(f"Finalize scan UI failed: {e}")

    def _populate_file_list_from_scanner(self):
        """Populate the UI file list with scanned PDF results."""
        try:
            if not hasattr(self, '_scanner') or self._scanner is None:
                return
            if not hasattr(self, 'main_ui') or not hasattr(self.main_ui, 'file_list'):
                return
            lw = self.main_ui.file_list
            lw.clear()

            # Flatten results preserving insertion order by scan
            items = []
            seen_paths = set()
            for docs in self._scanner.scan_results.values():
                for doc in docs:
                    path = getattr(doc, 'path', None) or getattr(doc, 'file_path', None)
                    if not path or path in seen_paths:
                        continue
                    seen_paths.add(path)
                    name = os.path.basename(path)
                    item = QListWidgetItem(name)
                    item.setData(Qt.ItemDataRole.UserRole, path)
                    items.append(item)

            # Sort alphabetically for user friendliness
            items.sort(key=lambda it: it.text().lower())
            for it in items:
                lw.addItem(it)

            # Update status message with count
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("ui.files_loaded", "{count} files loaded").format(count=len(items))
                )

            # Reset preview placeholder
            if hasattr(self.main_ui, 'clear_preview'):
                self.main_ui.clear_preview()
        except Exception as e:
            logger.debug(f"Populate file list failed: {e}")

    def on_open_selected_in_viewer(self, item=None):
        """Open the selected file(s) in the built-in PDF viewer."""
        try:
            if not hasattr(self.main_ui, 'file_list'):
                return
            selected = self.main_ui.file_list.selectedItems()
            if not selected and item is not None:
                selected = [item]
            if not selected:
                return
            import os
            from PyQt6.QtCore import Qt as _Qt
            for it in selected:
                # Prefer file path stored in UserRole; fallback to text
                path = it.data(_Qt.ItemDataRole.UserRole) or it.text()
                if not path:
                    continue
                path = os.fspath(path)
                if not os.path.isfile(path):
                    logger.warning(f"Selected item is not a file: {path}")
                    continue
                if not path.lower().endswith('.pdf'):
                    logger.warning(f"Selected item is not a PDF: {path}")
                    continue
                viewer = show_pdf_viewer(path, parent=self, language_manager=self.language_manager)
                self._open_viewers.append(viewer)
        except Exception as e:
            logger.error(f"Error opening selected files in viewer: {e}", exc_info=True)
    
    def on_file_selection_changed(self):
        """Handle file selection changes."""
        if not hasattr(self.main_ui, 'file_list'):
            return
            
        selected_items = self.main_ui.file_list.selectedItems()
        if selected_items:
            # Update preview based on selected item
            self.main_ui.update_preview(selected_items[0].data(Qt.ItemDataRole.UserRole))
        # Enable/disable delete action based on selection
        try:
            if hasattr(self, 'menu_bar') and 'delete_selected' in self.menu_bar.actions:
                self.menu_bar.actions['delete_selected'].setEnabled(bool(selected_items))
            if hasattr(self, 'toolbar'):
                # Toolbar uses same QAction instance; nothing else needed
                pass
        except Exception as e:
            logger.debug(f"Could not update delete action enabled state: {e}")
    
    def retranslate_ui(self):
        """Retranslate all UI elements."""
        # Update window title
        self.setWindowTitle(self.language_manager.tr("main_window.title", "PDF Duplicate Finder"))
        
        # Update menu bar
        if hasattr(self, 'menu_bar'):
            self.menu_bar.retranslate_ui()
        
        # Update toolbar by re-adding the menu actions
        if hasattr(self, 'menu_bar') and hasattr(self, 'toolbar'):
            # Get menu actions that should be in the toolbar
            toolbar_actions = {
                'open_folder': self.menu_bar.actions.get('open_folder'),
                'select_all': self.menu_bar.actions.get('select_all'),
                'deselect_all': self.menu_bar.actions.get('deselect_all'),
                'delete_selected': self.menu_bar.actions.get('delete_selected')
            }
            # Re-add actions to toolbar to refresh their text
            self.toolbar.add_actions_from_menu(toolbar_actions)
        
        # Update status bar
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.showMessage(
                self.language_manager.tr("ui.status_ready", "Ready")
            )
        
        # Update preview message if preview_widget exists and is valid
        if hasattr(self.main_ui, 'preview_widget') and self.main_ui.preview_widget is not None:
            if self.main_ui.preview_widget.text() == self.language_manager.tr("ui.preview_placeholder", "Preview will be shown here"):
                self.main_ui.preview_widget.setText(
                    self.language_manager.tr("ui.preview_placeholder", "Preview will be shown here")
                )
    
    def change_language(self, language_code: str):
        """Change the application language.
        
        Args:
            language_code: The language code to change to (e.g., 'en', 'it')
        """
        logger.debug(f"Changing language to: {language_code}")
        
        try:
            # Save the new language setting
            self.settings.set('app.language', language_code)
            
            # Change the language in the language manager
            if hasattr(self, 'language_manager') and self.language_manager:
                # This will trigger the on_language_changed signal
                success = self.language_manager.set_language(language_code)
                
                if success:
                    # Show a message to the user
                    if hasattr(self, 'status_bar') and self.status_bar:
                        self.status_bar.showMessage(
                            self.language_manager.tr("settings_dialog.language_changed", 
                                                  "Language changed successfully"),
                            3000  # 3 seconds
                        )
                    logger.info(f"Language changed to: {language_code}")
                else:
                    logger.error(f"Failed to change language to: {language_code}")
                    if hasattr(self, 'status_bar') and self.status_bar:
                        self.status_bar.showMessage(
                            self.language_manager.tr("settings_dialog.language_change_failed",
                                                  "Failed to change language"),
                            3000
                        )
            else:
                logger.warning("No language manager found")
                
        except Exception as e:
            logger.error(f"Error changing language: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            
            # Show error message to user
            if hasattr(self, 'status_bar') and self.status_bar:
                self.status_bar.showMessage(
                    self.tr(f"Error changing language: {e}"),
                    5000  # 5 seconds for error messages
                )
            
            # Show error message to the user
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr(f"Failed to change language: {e}")
            )

    def on_delete_selected(self):
        """Delete selected files by moving them to the Recycle Bin (send2trash)."""
        try:
            if not hasattr(self.main_ui, 'file_list'):
                return
            selected_items = self.main_ui.file_list.selectedItems()
            if not selected_items:
                QMessageBox.information(
                    self,
                    self.language_manager.tr("dialog.no_selection", "No Selection"),
                    self.language_manager.tr("dialog.select_items_to_delete", "Please select one or more files to delete.")
                )
                return
            # Collect file paths
            paths = []
            for it in selected_items:
                path = it.data(Qt.ItemDataRole.UserRole)
                if path and isinstance(path, (str, bytes)):
                    paths.append(str(path))
            if not paths:
                return
            # Perform deletion with confirmation using helper
            from script.delete import delete_files
            success, failed = delete_files(paths, parent=self, use_recycle_bin=True)
            # Remove items from list for files that no longer exist
            removed = 0
            import os as _os
            for it in list(selected_items):
                path = it.data(Qt.ItemDataRole.UserRole)
                path_str = str(path) if isinstance(path, (str, bytes)) else None
                if path_str and not _os.path.exists(path_str):
                    row = self.main_ui.file_list.row(it)
                    self.main_ui.file_list.takeItem(row)
                    removed += 1
            # Optionally clean up extra spacers without flags around removed items (best-effort)
            self.status_bar.showMessage(
                self.language_manager.tr(
                    "ui.status_deleted_summary",
                    "Deleted: %d, Failed: %d"
                ) % (success, failed),
                4000
            )
        except Exception as e:
            logger.error(f"Error deleting selected files: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("errors.delete_failed", "Failed to delete selected files: %s") % str(e)
            )
    
    def on_language_changed(self, language_code: str = None):
        """Handle language change signal from the language manager."""
        logger.info("=== Language Change Started ===")
        
        # Get the language manager instance
        lm = getattr(self, 'language_manager', None)
        if not lm:
            logger.error("No language manager found")
            return
            
        # If no language code provided, use current language
        if language_code is None:
            language_code = lm.get_current_language()
            
        logger.info(f"Changing language to: {language_code}")
        
        # Block signals to prevent recursion
        was_blocked = self.signalsBlocked()
        self.blockSignals(True)
        
        try:
            # Save the new language to settings first
            if hasattr(self, 'settings'):
                self.settings.set('app.language', language_code)
                self.settings._save_settings()
            
            # Update window title
            self.setWindowTitle(lm.tr("app.name", "PDF Duplicate Finder"))
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(lm.tr("status.ready", "Ready"), 3000)
            
            # Force update the application's style to ensure all text is refreshed
            QApplication.processEvents()
                
            # Recreate the menu bar to ensure all items are retranslated
            if hasattr(self, 'menu_bar') and hasattr(self, 'menubar'):
                # Store the current menu bar state
                menu_bar_geometry = self.menubar.geometry()
                
                # Remove the old menu bar
                self.menu_bar = None
                
                # Create a new menu bar
                from script.menu import MenuBar
                self.menu_bar = MenuBar(parent=self, language_manager=lm)
                
                # Add the new menu bar to the window
                self.menubar = self.menu_bar.menubar
                self.setMenuBar(self.menubar)
                
                # Restore geometry if we had a previous geometry
                if menu_bar_geometry.isValid():
                    self.menubar.setGeometry(menu_bar_geometry)
                
                # Force update
                self.menubar.update()
                
            # Update toolbar
            if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'retranslate_ui'):
                self.toolbar.retranslate_ui()
                self.toolbar.update()
                
            # Update main UI
            if hasattr(self, 'main_ui'):
                if hasattr(self.main_ui, 'retranslate_ui'):
                    self.main_ui.retranslate_ui()
                # Force update the UI
                self.main_ui.update()
            
            # Update any open dialogs
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'retranslate_ui'):
                    widget.retranslate_ui()
            
            # Force a style refresh
            self.style().unpolish(self)
            self.style().polish(self)
            
            # Update the application's style to ensure all text is refreshed
            QApplication.setStyle(QApplication.style().objectName())
            
            logger.info("Language change completed successfully")
            
            # Show a message to the user
            if hasattr(self, 'status_bar') and self.status_bar:
                self.status_bar.showMessage(
                    lm.tr("settings_dialog.language_changed", "Language changed successfully"),
                    3000  # 3 seconds
                )
            
        except Exception as e:
            logger.error(f"Error changing language: {e}", exc_info=True)
            
            # Show error message to the user
            if hasattr(self, 'status_bar') and self.status_bar:
                self.status_bar.showMessage(
                    lm.tr("errors.language_change_failed", "Failed to change language"),
                    5000  # 5 seconds
                )
            
            QMessageBox.critical(
                self,
                lm.tr("dialog.error", "Error"),
                lm.tr("errors.language_change_failed_details", "Failed to change language: {error}").format(error=str(e))
            )
            
        finally:
            # Restore signal blocking state
            self.blockSignals(was_blocked)
            
            # Force a UI update
            self.update()
            QApplication.processEvents()
    
    def apply_settings(self):
        """Apply application settings from the settings file."""
        try:
            logger.info("Applying application settings...")
            
            # Apply theme
            self.apply_theme()
            
            # Apply window state if available
            geometry = self.settings.get_window_geometry()
            state = self.settings.get_window_state()
            
            if geometry:
                try:
                    self.restoreGeometry(geometry)
                except Exception as e:
                    logger.error(f"Error restoring window geometry: {e}")
            
            if state:
                try:
                    self.restoreState(state)
                except Exception as e:
                    logger.error(f"Error restoring window state: {e}")
            
            # Apply toolbar visibility
            toolbar_visible = self.settings.get('ui.toolbar_visible', True)
            if hasattr(self, 'toolbar'):
                self.toolbar.setVisible(toolbar_visible)
                # Update the menu action if it exists
                if hasattr(self, 'menu_bar') and 'toggle_toolbar' in self.menu_bar.actions:
                    self.menu_bar.actions['toggle_toolbar'].setChecked(toolbar_visible)
            
            # Apply status bar visibility
            statusbar_visible = self.settings.get('ui.statusbar_visible', True)
            if hasattr(self, 'status_bar'):
                self.status_bar.setVisible(statusbar_visible)
                # Update the menu action if it exists
                if hasattr(self, 'menu_bar') and 'toggle_statusbar' in self.menu_bar.actions:
                    self.menu_bar.actions['toggle_statusbar'].setChecked(statusbar_visible)
            
            logger.info("Application settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}", exc_info=True)
    
    def apply_theme(self):
        """Apply the selected theme to the application."""
        try:
            theme = self.settings.get('app.theme', 'system')
            logger.debug(f"Applying theme: {theme}")
            
            # Default style sheet (can be overridden by theme)
            style_sheet = """
                QMainWindow, QDialog, QWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QStatusBar {
                    background-color: #e0e0e0;
                    color: #333333;
                }
            """
            
            # Apply theme-specific styles
            if theme == 'dark':
                style_sheet = """
                    QMainWindow, QDialog, QWidget {
                        background-color: #2d2d2d;
                        color: #f0f0f0;
                    }
                    QStatusBar {
                        background-color: #1e1e1e;
                        color: #f0f0f0;
                    }
                """
            
            self.setStyleSheet(style_sheet)
            
        except Exception as e:
            logger.error(f"Error applying theme: {e}", exc_info=True)
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Save window geometry and state
            geometry = self.saveGeometry()
            state = self.saveState()
            
            # Save using helper methods (convert QByteArray to bytes)
            if not geometry.isEmpty():
                self.settings.set_window_geometry(bytes(geometry))
            if not state.isEmpty():
                self.settings.set_window_state(bytes(state))
            
            # Save any other settings
            if hasattr(self, 'language_manager'):
                self.settings.set_language(self.language_manager.get_current_language())
            
            # Save settings to disk
            self.settings._save_settings()
            
        except Exception as e:
            logger.error(f"Error saving settings on close: {e}", exc_info=True)
        
        # Accept the close event
        event.accept()

    def on_show_settings(self):
        """Open the settings dialog and wire its signals."""
        try:
            dialog = SettingsDialog(parent=self, language_manager=self.language_manager)
            dialog.settings_changed.connect(getattr(self, 'on_settings_changed', self.apply_settings))
            dialog.language_changed.connect(lambda: self.change_language(dialog.language_combo.currentData()))
            dialog.requires_restart.connect(lambda: None)  # Placeholder: can implement restart flow
            dialog.exec()
        except Exception as e:
            logger.error(f"Error showing settings dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr("errors.open_settings_failed", "Could not open settings: %s") % str(e)
            )
