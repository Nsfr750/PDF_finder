"""
PDF Duplicate Finder - Main Application Module
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QProgressBar,
    QSplitter, QMenu, QMenuBar, QStatusBar, QToolBar, 
    QCheckBox, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QSpinBox, QComboBox, QGroupBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QStyle, QStyleFactory, QSystemTrayIcon,
    QToolButton, QSizePolicy, QSpacerItem, QFrame,
    QProgressDialog
)
from PyQt6.QtGui import (
    QAction, QActionGroup, QIcon, QPixmap, QPainter, QColor, 
    QFont, QFontMetrics, QTextDocument, QTextCursor, 
    QTextCharFormat, QTextFormat, QTextOption, QSyntaxHighlighter, 
    QKeySequence, QGuiApplication, QDesktopServices, QValidator, 
    QIntValidator, QDoubleValidator, QRegularExpressionValidator,
    QKeyEvent, QMouseEvent, QWheelEvent, QResizeEvent, 
    QCloseEvent, QContextMenuEvent, QDragEnterEvent, QDropEvent,
    QShowEvent, QHideEvent, QFocusEvent, QWindowStateChangeEvent,
    QPaintEvent
)
from PyQt6.QtCore import (
    Qt, QSize, QTimer, QThread, pyqtSignal, pyqtSlot,
    QObject, QEvent, QPoint, QRect, QRectF, QUrl,
    QLocale, QTranslator, QLibraryInfo
)

from datetime import datetime
import csv

# Import our custom modules
from script.main_window import MainWindow
from script.settings import AppSettings
from script.lang_mgr import LanguageManager
from script.logger import get_logger
from script.settings_dialog import SettingsDialog

# Set up logger
logger = get_logger('main')

class PDFDuplicateFinder(MainWindow):
    """Main application window for PDF Duplicate Finder."""
    
    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the application window."""
        logger.info("Initializing PDF Duplicate Finder")
        
        # Initialize settings
        self.settings = AppSettings()
        
        # Initialize language manager with saved language
        language = self.settings.get_language()
        self.language_manager = LanguageManager(
            default_lang=language
        )
        
        # Initialize the main window with the language manager
        super().__init__(parent, self.language_manager)
        logger.debug("MainWindow initialization complete")
        
        # Load window state and geometry from settings
        self.load_window_state()
        
        # Show the window
        self.show()
        # Storage for last scan results
        self.last_scan_duplicates: List[List[Dict[str, Any]]] = []
    
    def on_show_settings(self):
        """Override to ensure the settings dialog is shown correctly."""
        print("DEBUG: PDFDuplicateFinder.on_show_settings called")
        try:
            dialog = SettingsDialog(parent=self, language_manager=self.language_manager)
            dialog.settings_changed.connect(self.on_settings_changed)
            
            # Connect language changed signal
            def handle_language_changed():
                if hasattr(dialog, 'language_combo'):
                    lang_code = dialog.language_combo.currentData()
                    self.on_language_change(lang_code)
            
            dialog.language_changed.connect(handle_language_changed)
            dialog.exec()
        except Exception as e:
            print(f"ERROR in PDFDuplicateFinder.on_show_settings: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr(f"Could not open settings: {e}")
            )
            
    def on_language_change(self, language_code: str):
        """Handle language change from the settings dialog.
        
        Args:
            language_code: The new language code to change to (e.g., 'en', 'it')
        """
        try:
            logger.info(f"Changing language to: {language_code}")
            
            # Save the new language setting
            self.settings.set_language(language_code)
            
            # Update the language manager
            self.language_manager.set_language(language_code)
            
            # Retranslate the UI
            self.retranslate_ui()
            
            # Show a message to the user
            self.main_ui.status_bar.showMessage(
                self.tr("Language changed. Restart the application for all changes to take effect."), 
                5000  # 5 seconds
            )
            
        except Exception as e:
            logger.error(f"Error changing language: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr(f"Failed to change language: {e}")
            )
    
    def on_language_changed(self, language_code: str):
        """Handle language change from the language manager.
        
        This is called when the language is changed through other means
        (e.g., from a menu or keyboard shortcut).
        
        Args:
            language_code: The new language code (e.g., 'en', 'it')
        """
        # Just forward to on_language_change since the logic is the same
        self.on_language_change(language_code)
    
    def change_language(self, language_code: str):
        """Change the application language.
        
        This is called when the language is changed from the menu.
        
        Args:
            language_code: The new language code (e.g., 'en', 'it')
        """
        try:
            # Update the language manager
            self.language_manager.set_language(language_code)
            
            # Save the language setting
            self.settings.set_language(language_code)
            
            # Refresh the UI
            self.retranslate_ui()
            
            # Show a status message
            self.main_ui.status_bar.showMessage(
                self.tr("Language changed to {}").format(language_code),
                3000  # 3 seconds
            )
            
        except Exception as e:
            logger.error(f"Error changing language: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr(f"Failed to change language: {e}")
            )
    
    def check_for_updates(self):
        """Check for application updates."""
        try:
            # Get current version
            from script.version import __version__ as current_version
            
            # Show checking message
            self.status_bar.showMessage(self.tr("Checking for updates..."), 5000)
            
            # In a real application, you would check for updates from a server
            # For now, we'll just show a message that no updates are available
            QMessageBox.information(
                self,
                self.tr("Check for Updates"),
                self.tr("You are using the latest version: v{}").format(current_version)
            )
            
            # Example of how to check for updates (commented out for reference):
            """
            import requests
            try:
                response = requests.get("https://api.github.com/repos/Nsfr750/PDF_Finder/releases/latest", timeout=10)
                if response.status_code == 200:
                    latest_release = response.json()
                    latest_version = latest_release['tag_name'].lstrip('v')
                    
                    if latest_version > current_version:
                        # New version available
                        reply = QMessageBox.information(
                            self,
                            self.tr("Update Available"),
                            self.tr("A new version (v{}) is available. Would you like to download it now?").format(latest_version),
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        
                        if reply == QMessageBox.StandardButton.Yes:
                            # Open download URL in default browser
                            download_url = latest_release.get('html_url', '')
                            if download_url:
                                import webbrowser
                                webbrowser.open(download_url)
                    else:
                        QMessageBox.information(
                            self,
                            self.tr("No Updates"),
                            self.tr("You are using the latest version: v{}").format(current_version)
                        )
                else:
                    QMessageBox.warning(
                        self,
                        self.tr("Update Check Failed"),
                        self.tr("Failed to check for updates. Please try again later.")
                    )
            except Exception as e:
                logger.error(f"Error checking for updates: {e}", exc_info=True)
                QMessageBox.warning(
                    self,
                    self.tr("Update Error"),
                    self.tr("An error occurred while checking for updates: {}").format(str(e))
                )
            """
            
        except Exception as e:
            logger.error(f"Error in check_for_updates: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to check for updates: {}").format(str(e))
            )
    
    def retranslate_ui(self):
        """Retranslate all UI elements when the language changes."""
        try:
            logger.info("Retranslating UI...")
            
            # Update window title
            self.setWindowTitle(self.tr("PDF Duplicate Finder"))
            
            # Update menu bar
            if hasattr(self, 'menu_bar'):
                self.menu_bar.retranslate_ui()
            
            # Update toolbar
            if hasattr(self, 'toolbar'):
                self.toolbar.retranslate_ui()
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(self.tr("Ready"))
            
            # Update any other UI elements that need translation
            if hasattr(self, 'main_ui') and hasattr(self.main_ui, 'retranslate_ui'):
                self.main_ui.retranslate_ui()
                
            logger.info("UI retranslation complete")
                
        except Exception as e:
            logger.error(f"Error retranslating UI: {e}", exc_info=True)
            
    def apply_settings(self):
        """Apply settings that need to be updated immediately."""
        try:
            # Apply language setting if changed
            current_lang = self.language_manager.get_current_language()
            saved_lang = self.settings.get_language()
            
            if current_lang != saved_lang:
                self.language_manager.set_language(saved_lang)
                self.retranslate_ui()
            
            # Apply UI settings
            if hasattr(self, 'toolbar') and hasattr(self.settings, 'get_show_toolbar'):
                self.toolbar.setVisible(self.settings.get_show_toolbar())
                
            if hasattr(self.main_ui, 'status_bar') and hasattr(self.settings, 'get_show_statusbar'):
                self.main_ui.status_bar.setVisible(self.settings.get_show_statusbar())
                
            logger.info("Settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}", exc_info=True)
            raise
    
    def on_settings_changed(self):
        """Handle settings changes from the settings dialog."""
        print("DEBUG: PDFDuplicateFinder.on_settings_changed called")
        try:
            # Apply any settings that need to be updated immediately
            self.apply_settings()
            
            # Update the UI to reflect the new settings
            self.retranslate_ui()
            
            # Show a message to the user
            self.main_ui.status_bar.showMessage(self.tr("Settings have been updated"), 3000)  # 3 seconds
            
        except Exception as e:
            print(f"ERROR in on_settings_changed: {e}")
            import traceback
            traceback.print_exc()
    
    def load_window_state(self):
        """Load window state and geometry from settings."""
        try:
            # Load window geometry
            geometry = self.settings.get_window_geometry()
            if geometry:
                self.restoreGeometry(geometry)
            
            # Load window state
            state = self.settings.get_window_state()
            if state:
                self.restoreState(state)
                
        except Exception as e:
            logger.error(f"Error loading window state: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Save window geometry and state
            geometry = self.saveGeometry()
            state = self.saveState()
            
            # Only save non-empty geometry/state
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
            logger.error(f"Error saving settings: {e}")
        
        # Proceed with the default close behavior
        super().closeEvent(event)

    def on_open_folder(self):
        """Use MainWindow's scanning flow (status-bar progress bar)."""
        # Delegate to base class which starts PDFScanner and updates the status-bar QProgressBar
        return super().on_open_folder()
    
    def on_toggle_toolbar(self, checked: bool):
        """Show or hide the toolbar.
        
        Args:
            checked: Whether the toolbar should be visible
        """
        if hasattr(self, 'toolbar'):
            self.toolbar.setVisible(checked)
    
    def on_toggle_statusbar(self, checked: bool):
        """Show or hide the status bar.
        
        Args:
            checked: Whether the status bar should be visible
        """
        if hasattr(self.main_ui, 'status_bar'):
            self.main_ui.status_bar.setVisible(checked)
    
    def on_select_all(self):
        """Select all items in the current view."""
        if hasattr(self.main_ui, 'file_list'):
            self.main_ui.file_list.selectAll()
    
    def on_deselect_all(self):
        """Deselect all items in the current view."""
        if hasattr(self.main_ui, 'file_list'):
            self.main_ui.file_list.clearSelection()
    
    def on_show_about(self):
        """Show the about dialog."""
        from script.about import AboutDialog
        
        about_dialog = AboutDialog(self)
        about_dialog.exec()
    
    def on_show_log_viewer(self):
        """Open the log viewer dialog for today's log file."""
        try:
            from script.view_log import show_log_viewer
            # Build expected log file path (same pattern as logger.setup_logger)
            logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            today = datetime.now().strftime('%Y%m%d')
            log_file = os.path.join(logs_dir, f"PDFDuplicateFinder_{today}.log")
            show_log_viewer(log_file, parent=self)
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Could not open log viewer: %s") % str(e)
            )
    
    def scan_folder(self, folder_path: str):
        """Scan a folder for duplicate PDF files.
        
        Args:
            folder_path: Path to the folder to scan
        """
        from script.pdf_utils import find_duplicates
        
        # Update status bar
        self.main_ui.status_bar.showMessage(self.tr("Scanning folder: %s") % folder_path)
        
        # Create and configure progress dialog
        progress = QProgressDialog(
            self.tr("Preparing to scan..."),
            self.tr("Cancel"),
            0, 100,
            self
        )
        progress.setWindowTitle(self.tr("Scanning for Duplicates"))
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.setAutoReset(False)
        progress.setAutoClose(False)
        
        # Force the progress dialog to appear immediately
        QApplication.processEvents()
        
        # Flag to track if the user cancelled the operation
        cancelled = [False]
        
        def progress_callback(message: str):
            """Handle progress updates from the scanning process."""
            if cancelled[0]:
                return False  # Stop processing if cancelled
                
            if "Processed" in message:
                # Extract progress percentage from message if available
                try:
                    parts = message.split()
                    current = int(parts[1].split('/')[0])
                    total = int(parts[1].split('/')[1])
                    percent = int((current / total) * 100) if total > 0 else 0
                    progress.setValue(percent)
                    progress.setLabelText(f"{message} - {percent}%")
                except (IndexError, ValueError):
                    progress.setLabelText(message)
            else:
                progress.setLabelText(message)
                
            # Process events to update the UI
            QApplication.processEvents()
            
            # Check if the user clicked cancel
            if progress.wasCanceled():
                cancelled[0] = True
                return False
                
            return True
        
        try:
            # Find duplicate PDFs with progress updates
            progress.setLabelText(self.tr("Searching for PDF files..."))
            QApplication.processEvents()
            
            duplicates = find_duplicates(
                directory=folder_path,
                recursive=True,
                min_file_size=1024,  # 1KB minimum file size
                max_file_size=100 * 1024 * 1024,  # 100MB maximum file size
                hash_size=8,
                threshold=0.80,
                progress_callback=progress_callback
            )
            # Save for export
            self.last_scan_duplicates = duplicates or []
            
            # Check if operation was cancelled
            if cancelled[0]:
                self.main_ui.status_bar.showMessage(self.tr("Scan cancelled by user"))
                progress.close()
                return
            
            # Update progress
            progress.setValue(100)
            progress.setLabelText(self.tr("Processing results..."))
            QApplication.processEvents()
            
            # Clear the file list
            if hasattr(self.main_ui, 'file_list'):
                self.main_ui.file_list.clear()
            else:
                # If file_list doesn't exist, log an error and return
                logger.error("file_list widget not found in main_ui")
                return
            
            # Add duplicates to the file list
            if duplicates and len(duplicates) > 0:
                for group_index, duplicate_group in enumerate(duplicates, 1):
                    if not duplicate_group:  # Skip empty groups
                        continue
                        
                    # Create a group header item
                    group_item = QListWidgetItem()
                    group_item.setText(f"{self.tr('Group')} {group_index} - {len(duplicate_group)} {self.tr('duplicates')}")
                    group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # Make header non-selectable
                    group_item.setBackground(QColor(240, 240, 240))  # Light gray background for headers
                    group_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))  # Make header text bold
                    self.main_ui.file_list.addItem(group_item)
                    
                    # Add each file in the duplicate group
                    for file_info in duplicate_group:
                        if isinstance(file_info, dict) and 'path' in file_info:
                            file_item = QListWidgetItem()
                            file_name = file_info.get('filename', os.path.basename(file_info['path']))
                            file_size = file_info.get('size', 0)
                            size_kb = file_size / 1024.0
                            file_item.setText(f"  • {file_name} ({size_kb:.1f} KB)")
                            # Store path for activation/double-click handlers
                            file_item.setData(Qt.ItemDataRole.UserRole, file_info.get('path'))
                            # Store full info in another role for future features
                            try:
                                file_item.setData(Qt.ItemDataRole.UserRole + 1, file_info)
                            except Exception:
                                pass
                            self.main_ui.file_list.addItem(file_item)
                    
                    # Add a small space between groups
                    spacer = QListWidgetItem()
                    spacer.setFlags(Qt.ItemFlag.NoItemFlags)
                    spacer.setSizeHint(QSize(0, 5))  # 5 pixels height for spacing
                    self.main_ui.file_list.addItem(spacer)
                
                # Show completion message
                msg = self.tr("Found %d groups of duplicate files") % len(duplicates)
                self.main_ui.status_bar.showMessage(msg)
                progress.setLabelText(msg)
            else:
                # No duplicates found
                msg = self.tr("No duplicate files found")
                self.main_ui.status_bar.showMessage(msg)
                progress.setLabelText(msg)
                # Save empty results for export clarity
                self.last_scan_duplicates = []
                
                # Add a message to the file list
                no_duplicates_item = QListWidgetItem(self.tr("No duplicate files found in the selected folder."))
                no_duplicates_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.main_ui.file_list.addItem(no_duplicates_item)
            
            # Show completion for a moment before closing
            progress.setValue(100)
            QTimer.singleShot(1000, progress.close)
            
        except Exception as e:
            # Show error message
            error_msg = self.tr("Failed to scan folder: %s") % str(e)
            QMessageBox.critical(
                self,
                self.tr("Error"),
                error_msg
            )
            
            # Update status bar
            self.main_ui.status_bar.showMessage(error_msg)
            logger.error(f"Error scanning folder: {e}", exc_info=True)
            
        finally:
            # Make sure to close the progress dialog if it's still open
            if progress.isVisible():
                progress.close()

    def on_export_csv(self):
        """Export the latest scan results to a CSV file."""
        try:
            results = getattr(self, 'last_scan_duplicates', [])
            if not results:
                QMessageBox.information(
                    self,
                    self.tr("Export CSV"),
                    self.tr("No results to export. Please run a scan first.")
                )
                return
            # Ask for destination file
            dest_path, _ = QFileDialog.getSaveFileName(
                self,
                self.tr("Save Scan Results as CSV"),
                "duplicates.csv",
                self.tr("CSV Files (*.csv)")
            )
            if not dest_path:
                return
            # Write CSV
            with open(dest_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["group", "path", "filename", "size_bytes", "size_kb", "modified_epoch", "md5"]) 
                for group_idx, group in enumerate(results, start=1):
                    for info in group or []:
                        if not isinstance(info, dict):
                            continue
                        path = info.get('path', '')
                        filename = info.get('filename', os.path.basename(path))
                        size = int(info.get('size', 0) or 0)
                        size_kb = f"{size/1024:.1f}"
                        modified = info.get('modified', 0)
                        md5 = info.get('md5', '')
                        writer.writerow([group_idx, path, filename, size, size_kb, modified, md5])
            QMessageBox.information(
                self,
                self.tr("Export CSV"),
                self.tr("Export completed: %s") % dest_path
            )
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to export CSV: %s") % str(e)
            )
    
def main():
    """Main entry point for the application."""
    # Create the application first
    app = QApplication(sys.argv)
    
    try:
        # Set application metadata
        app.setApplicationName("PDF Duplicate Finder")
        app.setOrganizationName("PDFDuplicateFinder")
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            app.setWindowIcon(app_icon)
        else:
            logger.warning(f"Icon file not found at: {icon_path}")
        
        # Apply Fusion style first
        app.setStyle("Fusion")
        
        # Only set the dark palette if the style was applied successfully
        if app.style().objectName().lower() == "fusion":
            # Create a dark palette
            dark_palette = app.palette()
            dark_palette.setColor(dark_palette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(dark_palette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(dark_palette.ColorRole.Base, QColor(42, 42, 42))
            dark_palette.setColor(dark_palette.ColorRole.AlternateBase, QColor(66, 66, 66))
            dark_palette.setColor(dark_palette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            dark_palette.setColor(dark_palette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(dark_palette.ColorRole.Text, Qt.GlobalColor.white)
            dark_palette.setColor(dark_palette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(dark_palette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(dark_palette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(dark_palette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(dark_palette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(dark_palette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            
            # Apply the dark palette
            app.setPalette(dark_palette)
        
        # Set style sheet for tooltips
        app.setStyleSheet("""
            QToolTip { 
                color: #ffffff; 
                background-color: #2a82da; 
                border: 1px solid white; 
            }
        """)
        
        # Create and show the main window
        window = PDFDuplicateFinder()
        window.show()
        
        # Run the application
        return app.exec()
        
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"A critical error occurred and the application must close.\n\n{str(e)}"
        )
        return 1
    finally:
        # Ensure proper cleanup
        app.quit()
        
if __name__ == "__main__":
    main()
