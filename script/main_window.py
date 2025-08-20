"""
Main window implementation with internationalization support.
"""
import os
import logging
from pathlib import Path
from typing import Callable, Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMenu, QWidget, QVBoxLayout, 
    QHBoxLayout, QSplitter, QListWidget, QLabel, QToolBar,
    QStatusBar, QApplication, QMenuBar, QFrame, QMessageBox, QDialog
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

class MainWindow(QMainWindow):
    """Base main window class with internationalization support."""
    
    # Signal emitted when the language is changed
    language_changed = Signal()
    
    def __init__(self, parent: Optional[QObject] = None, language_manager: Optional[LanguageManager] = None):
        """Initialize the main window.
        
        Args:
            parent: Optional parent widget.
            language_manager: Optional LanguageManager instance. If not provided, a new one will be created.
        """
        super().__init__(parent)
        
        # Initialize settings
        self.settings = AppSettings()
        
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
                
                # Here you would typically scan the folder for PDFs
                # For now, we'll just show a message
                QMessageBox.information(
                    self,
                    self.language_manager.tr("dialog.folder_selected", "Folder Selected"),
                    self.language_manager.tr("dialog.selected_folder", "Selected folder: %s") % folder_path
                )
                
                # Reset status bar after a delay
                QTimer.singleShot(3000, lambda: self.status_bar.showMessage(
                    self.language_manager.tr("ui.status_ready", "Ready"))
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
            # Get menu actions that should be in the toolbar
            toolbar_actions = {
                'open_folder': self.menu_bar.actions.get('open_folder'),
                'select_all': self.menu_bar.actions.get('select_all'),
                'deselect_all': self.menu_bar.actions.get('deselect_all')
            }
            # Add actions to toolbar
            self.toolbar.add_actions_from_menu(toolbar_actions)
            
        # Connect other signals
        if hasattr(self, 'language_changed'):
            self.language_changed.connect(self.retranslate_ui)
    
    def on_file_selection_changed(self):
        """Handle file selection changes."""
        if not hasattr(self.main_ui, 'file_list'):
            return
            
        selected_items = self.main_ui.file_list.selectedItems()
        if selected_items:
            # Update preview based on selected item
            self.main_ui.update_preview(selected_items[0].data(Qt.ItemDataRole.UserRole))
    
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
                'deselect_all': self.menu_bar.actions.get('deselect_all')
            }
            # Re-add actions to toolbar to refresh their text
            self.toolbar.add_actions_from_menu(toolbar_actions)
        
        # Update status bar
        if hasattr(self, 'status_bar'):
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
            # Update window title
            self.setWindowTitle(lm.tr("app.name", "PDF Duplicate Finder"))
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(lm.tr("status.ready", "Ready"))
                
            # Update menu bar
            if hasattr(self, 'menu_bar') and hasattr(self.menu_bar, 'retranslate_ui'):
                self.menu_bar.retranslate_ui()
                
            # Update toolbar
            if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'retranslate_ui'):
                self.toolbar.retranslate_ui()
                
            # Update main UI
            if hasattr(self, 'main_ui') and hasattr(self.main_ui, 'retranslate_ui'):
                self.main_ui.retranslate_ui()
                
            # Save the new language to settings
            if hasattr(self, 'settings') and hasattr(self.settings, 'set_language'):
                self.settings.set_language(language_code)
                
            logger.info("Language change completed successfully")
            
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
