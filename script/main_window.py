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
from PyQt6.QtCore import pyqtSignal as Signal, QObject, QLocale, Qt, QTranslator, QLibraryInfo

# Import language manager
from lang.language_manager import LanguageManager
from script.settings import AppSettings

# Set up logger
logger = logging.getLogger(__name__)

from .menu import MenuBar
from .toolbar import MainToolBar
from .ui import MainUI

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
        self.language_manager = language_manager or LanguageManager()
        
        # Store a reference to the QApplication instance
        self.app = QApplication.instance()
        
        # Set up the UI
        self.setup_ui()
        
        # Connect to language change signals
        self.language_manager.language_changed.connect(self.on_language_changed)
        
        # Apply initial language if not already set
        initial_language = self.settings.get_language()
        if initial_language:
            self.language_manager.set_language(initial_language)
    
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
        """Handle language change signal from the language manager.
        
        Args:
            language_code: The new language code (e.g., 'en', 'it'). If None, uses current language from manager.
        """
        print("\n" + "="*50)
        print(f"DEBUG: on_language_changed called with language_code={language_code}")
        print(f"DEBUG: hasattr(self, 'language_manager') = {hasattr(self, 'language_manager')}")
        
        try:
            if language_code is None:
                print("DEBUG: No language_code provided, getting from language_manager")
                if hasattr(self, 'language_manager') and self.language_manager:
                    language_code = self.language_manager.current_language
                    print(f"DEBUG: Got language_code from language_manager: {language_code}")
                else:
                    print("WARNING: No language_manager available, using default 'en'")
                    language_code = 'en'
            
            print(f"DEBUG: Language will be set to: {language_code}")
            logger.debug(f"Language changed to {language_code}, retranslating UI")
            
        except Exception as e:
            print(f"ERROR in on_language_changed (initial setup): {e}")
            import traceback
            traceback.print_exc()
            language_code = 'en'  # Fallback to English on error
            logger.error(f"Error in on_language_changed (initial setup): {e}")
            logger.error(traceback.format_exc())
        
        try:
            print("DEBUG: Starting UI update process...")
            # Use a try-finally to ensure we always log completion
            try:
                # Update the application's language
                if not hasattr(self, 'app') or not self.app:
                    logger.warning("No QApplication instance found")
                    return
                
                # Process any pending events before starting
                self.app.processEvents()
                
                # Update the main window title
                self.setWindowTitle(self.language_manager.tr("main_window.title", "PDF Duplicate Finder"))
                
                # Update the status bar if it exists
                if hasattr(self, 'status_bar') and self.status_bar and hasattr(self.status_bar, 'showMessage'):
                    try:
                        self.status_bar.showMessage(
                            self.language_manager.tr("ui.status_ready", "Ready")
                        )
                    except Exception as e:
                        logger.error(f"Error updating status bar: {e}")
                
                # Update menu bar if it exists
                if hasattr(self, 'menu_bar') and self.menu_bar and hasattr(self.menu_bar, 'retranslate_ui'):
                    try:
                        self.menu_bar.retranslate_ui()
                    except Exception as e:
                        logger.error(f"Error updating menu bar: {e}")
                
                # Update toolbar if it exists
                if hasattr(self, 'toolbar') and self.toolbar and hasattr(self.toolbar, 'retranslate_ui'):
                    try:
                        self.toolbar.retranslate_ui()
                    except Exception as e:
                        logger.error(f"Error updating toolbar: {e}")
                
                # Safely update all child widgets
                try:
                    self.retranslate_ui()
                except Exception as e:
                    logger.error(f"Error in retranslate_ui: {e}")
                
                # Process any pending events after updates
                self.app.processEvents()
                
                logger.debug("UI retranslation completed successfully")
                
            except Exception as e:
                logger.error(f"Error in on_language_changed: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Try to show an error message to the user if possible
                try:
                    QMessageBox.critical(
                        self,
                        self.tr("Error"),
                        self.tr("An error occurred while changing the language. Please check the log for details.")
                    )
                except:
                    pass  # If we can't show the error dialog, at least we logged it
                    
        except Exception as e:
            # This is a last resort error handler
            logger.critical(f"Critical error in language change handler: {e}")
            logger.critical(f"Traceback: {traceback.format_exc()}")
    
    def on_show_about(self):
        """Show the about dialog."""
        from .about import AboutDialog
        about_dialog = AboutDialog(self, self.language_manager)
        about_dialog.exec()
    
    def on_show_settings(self):
        """Show the settings dialog."""
        print("\n" + "="*50)
        print("DEBUG: MainWindow.on_show_settings called")
        print(f"DEBUG: self = {self}")
        print(f"DEBUG: self.language_manager = {self.language_manager}")
        
        try:
            print("\nDEBUG: Attempting to import SettingsDialog")
            from .settings_dialog import SettingsDialog
            print("DEBUG: Successfully imported SettingsDialog")
            
            print("\nDEBUG: Creating SettingsDialog instance")
            # Create the settings dialog with the main window as parent
            settings_dialog = SettingsDialog(parent=self, language_manager=self.language_manager)
            print(f"DEBUG: SettingsDialog created: {settings_dialog}")
            print(f"DEBUG: settings_dialog.isVisible() = {settings_dialog.isVisible()}")
            
            # Store the current language to detect changes
            current_language = self.language_manager.current_language
            
            # Connect the settings_changed signal to handle any necessary updates
            print("\nDEBUG: Connecting signals")
            settings_dialog.settings_changed.connect(self.on_settings_changed)
            settings_dialog.language_changed.connect(self.on_language_changed)
            settings_dialog.requires_restart.connect(self.on_requires_restart)
            
            # Show the dialog as a modal dialog
            print("\nDEBUG: About to show settings dialog")
            print(f"DEBUG: Before exec(), isActiveWindow = {self.isActiveWindow()}")
            print(f"DEBUG: Before exec(), isVisible = {self.isVisible()}")
            
            # Use exec() for modal dialog
            result = settings_dialog.exec()
            print(f"DEBUG: exec() returned with result: {result}")
            
            print("\nDEBUG: After showing dialog")
            
        except ImportError as e:
            print(f"\nERROR: Failed to import SettingsDialog: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr(f"Failed to load settings dialog: {e}")
            )
        except Exception as e:
            print(f"\nERROR in on_show_settings: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr(f"Could not open settings: {e}")
            )
        
        print("="*50 + "\n")
    
    def on_settings_changed(self):
        """Handle settings changes."""
        # Update the UI
        self.retranslate_ui()
        
        # Apply new settings
        self.apply_settings()
    
    def on_requires_restart(self):
        """Handle application restart required."""
        print("\nDEBUG: Application restart required")
        reply = QMessageBox.information(
            self,
            self.language_manager.tr("settings_dialog.restart_required", "Restart Required"),
            self.language_manager.tr("settings_dialog.restart_message", 
                                   "The application needs to be restarted for all changes to take effect.\n"
                                   "Do you want to restart now?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Restart the application
            QApplication.quit()
            QProcess.startDetached(sys.executable, sys.argv)
    
    def retranslate_ui(self):
        """Retranslate the UI after language change."""
        # Update window title
        self.setWindowTitle(self.language_manager.tr("main_window.title", "PDF Duplicate Finder"))
        
        # Update menu bar
        if hasattr(self, 'menu_bar'):
            self.menu_bar.retranslate_ui()
        
        # Update toolbar
        if hasattr(self, 'toolbar'):
            self.toolbar.retranslate_ui()
        
        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(self.language_manager.tr("ui.status_ready", "Ready"))
        
        # Notify any registered callbacks
        for callback in getattr(self, 'retranslate_callbacks', []):
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in retranslate callback: {e}")
    
    def apply_settings(self):
        """Apply settings to the application."""
        # Apply theme if needed
        self.apply_theme()
        
        # Apply any other settings...
    
    def apply_theme(self):
        """Apply the selected theme to the application."""
        theme = self.settings.get('app.theme', 'system')
        # Implement theme application logic here
        # This is a placeholder - you'll need to implement the actual theming
        print(f"Applying theme: {theme}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Save window geometry and state
            geometry = self.saveGeometry()
            state = self.saveState()
            
            # Convert QByteArray to hex string for storage
            self.settings.set('window.geometry', bytes(geometry).hex() if not geometry.isEmpty() else '')
            self.settings.set('window.state', bytes(state).hex() if not state.isEmpty() else '')
            
            # Save any other settings
            if hasattr(self, 'language_manager'):
                self.settings.set_language(self.language_manager.current_language)
            
            # Save settings to disk
            self.settings._save_settings()
            
        except Exception as e:
            logger.error(f"Error saving settings on close: {e}", exc_info=True)
        
        # Accept the close event
        event.accept()
