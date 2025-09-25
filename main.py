"""
PDF Duplicate Finder - Main Module
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QMenu,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStatusBar, QSplitter,
    QWidget, QListWidget, QListWidgetItem, QProgressBar, QTreeWidget, QTreeWidgetItem,
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
    QLocale, QTranslator, QLibraryInfo, QMetaObject, Q_ARG,
    QMutex, QMutexLocker, QCoreApplication
)

from datetime import datetime
import csv
import shutil
try:
    import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False

# Import our custom modules
from script.UI.main_window import MainWindow
from script.utils.settings import AppSettings
from script.utils.logger import get_logger
from script.UI.settings_dialog import SettingsDialog
from script.utils.scanner import PDFScanner
from PyQt6.QtCore import QThread, QObject, QTimer, QMetaObject
from PyQt6.QtWidgets import QProgressBar, QMessageBox, QDialog
from script.UI.progress_dialog import ScanProgressDialog

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
        from script.lang.lang_manager import SimpleLanguageManager
        self.language_manager = SimpleLanguageManager(
            default_lang=language
        )
        
        # Initialize the main window with the language manager
        super().__init__(parent, self.language_manager)
        logger.debug("MainWindow initialization complete")
        
        # Load window state and geometry from settings
        self.apply_settings()
        
        # Initialize hash cache if enabled in settings
        self._initialize_hash_cache()
        
        # Initialize filter settings
        self.current_filters = {
            'min_size': 0,  # in bytes
            'max_size': 100 * 1024 * 1024,  # 100MB in bytes
            'name_pattern': '',
            'enable_text_compare': True,
            'min_similarity': 0.8
        }
        
        # Show the window
        self.show()
        
        # Note: Removed automatic folder selection dialog to prevent freezing
        # QTimer.singleShot(100, self.on_open_folder)
        
        # Storage for last scan results
        self.last_scan_duplicates: List[List[Dict[str, Any]]] = []
        
        # Initialize progress dialog
        self.progress_dialog = None
    
    def _initialize_hash_cache(self):
        """Initialize the hash cache if enabled in settings."""
        try:
            # Get cache settings from settings
            enable_hash_cache = self.settings.get('enable_hash_cache', True)
            cache_dir = self.settings.get('cache_dir', None)
            
            if enable_hash_cache:
                logger.info("Initializing hash cache...")
                
                # Create scanner with hash cache enabled
                self._scanner = PDFScanner(
                    threshold=0.8,  # Default threshold
                    dpi=150,        # Default DPI
                    enable_hash_cache=True,
                    cache_dir=cache_dir,
                    language_manager=self.language_manager
                )
                
                logger.info("Hash cache initialized successfully")
            else:
                logger.info("Hash cache is disabled in settings")
                self._scanner = None
                
        except Exception as e:
            logger.error(f"Error initializing hash cache: {e}", exc_info=True)
            self._scanner = None
    
    def on_show_about(self):
        """Show the about dialog."""
        from script.UI.about import AboutDialog
        about_dialog = AboutDialog(self, self.language_manager)
        about_dialog.exec()
        
    def on_view_logs(self):
        """Show the log viewer dialog."""
        from script.UI.view_log import show_log_viewer
        log_file = os.path.join('logs', 'PDFDuplicateFinder.log')
        show_log_viewer(log_file, self)
        
    def _init_scanner(self):
        """Initialize the scanner with default settings and connect signals."""
        logger.info("Initializing scanner...")
        
        # Make sure we're in the main thread for UI updates
        if QThread.currentThread() != self.thread():
            logger.debug("Dispatching _init_scanner to main thread")
            QMetaObject.invokeMethod(
                self,
                "_init_scanner",
                Qt.ConnectionType.BlockingQueuedConnection
            )
            return
        
        # Clean up any existing scanner and thread
        if hasattr(self, '_scanner'):
            try:
                # Disconnect all signals first
                try:
                    if hasattr(self._scanner, 'progress_updated'):
                        self._scanner.progress_updated.disconnect()
                    if hasattr(self._scanner, 'status_updated'):
                        self._scanner.status_updated.disconnect()
                    if hasattr(self._scanner, 'duplicates_found'):
                        self._scanner.duplicates_found.disconnect()
                    if hasattr(self._scanner, 'finished'):
                        self._scanner.finished.disconnect()
                    if hasattr(self._scanner, 'deleteLater'):
                        self._scanner.deleteLater()
                except Exception as e:
                    logger.warning(f"Error disconnecting scanner signals: {e}")
                self._scanner = None
            except Exception as e:
                logger.error(f"Error cleaning up scanner: {e}", exc_info=True)
        
        # Clean up thread
        if hasattr(self, 'scan_thread'):
            try:
                if self.scan_thread.isRunning():
                    logger.debug("Stopping existing scan thread...")
                    self.scan_thread.quit()
                    if not self.scan_thread.wait(2000):  # Wait up to 2 seconds
                        logger.warning("Thread did not stop cleanly, terminating...")
                        self.scan_thread.terminate()
                        self.scan_thread.wait()
                self.scan_thread = None
            except Exception as e:
                logger.error(f"Error cleaning up thread: {e}", exc_info=True)
        
        try:
            # Create new scanner and thread with proper initialization
            self.scan_thread = QThread()
            self.scan_thread.setObjectName("PDFScannerThread")
            
            # Get settings for scanner with reasonable defaults
            comparison_threshold = float(self.settings.get('comparison_threshold', 0.8))
            dpi = int(self.settings.get('dpi', 150))
            enable_hash_cache = bool(self.settings.get('enable_hash_cache', True))
            cache_dir = self.settings.get('cache_dir', None)
            
            logger.debug(f"Creating scanner with threshold={comparison_threshold}, dpi={dpi}, "
                        f"hash_cache={'enabled' if enable_hash_cache else 'disabled'}")
            
            # Create scanner with settings including hash cache
            self._scanner = PDFScanner(
                threshold=comparison_threshold,
                dpi=dpi,
                enable_hash_cache=enable_hash_cache,
                cache_dir=cache_dir,
                language_manager=self.language_manager
            )
            
            # Move scanner to thread
            self._scanner.moveToThread(self.scan_thread)
            
            # Connect signals with proper connection type
            self._scanner.progress_updated.connect(
                self._on_scan_progress,
                Qt.ConnectionType.QueuedConnection
            )
            self._scanner.status_updated.connect(
                self._on_scan_status,
                Qt.ConnectionType.QueuedConnection
            )
            self._scanner.duplicates_found.connect(
                self._on_duplicates_found,
                Qt.ConnectionType.QueuedConnection
            )
            self._scanner.finished.connect(
                self._on_scan_finished,
                Qt.ConnectionType.QueuedConnection
            )
            
            # Connect thread signals
            self.scan_thread.started.connect(self._scanner.start_scan)
            self.scan_thread.finished.connect(self.scan_thread.deleteLater)
            
            # Set up status callback
            if hasattr(self._scanner, 'set_status_callback'):
                self._scanner.set_status_callback(self._on_scan_status)
            
            # Connect cleanup signals
            self._scanner.finished.connect(self._scanner.deleteLater)
            
            logger.info("Scanner initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scanner: {e}", exc_info=True)
            return False
    
    def _init_scanner_without_thread(self):
        """Initialize the PDF scanner without creating a thread."""
        logger.debug("Initializing PDF scanner without thread")
        
        try:
            # Get settings for scanner with reasonable defaults
            comparison_threshold = float(self.settings.get('comparison_threshold', 0.8))
            dpi = int(self.settings.get('dpi', 150))
            enable_hash_cache = bool(self.settings.get('enable_hash_cache', True))
            cache_dir = self.settings.get('cache_dir', None)
            
            logger.debug(f"Creating scanner with threshold={comparison_threshold}, dpi={dpi}, "
                        f"hash_cache={'enabled' if enable_hash_cache else 'disabled'}")
            
            # Create scanner with settings including hash cache
            self._scanner = PDFScanner(
                threshold=comparison_threshold,
                dpi=dpi,
                enable_hash_cache=enable_hash_cache,
                cache_dir=cache_dir,
                language_manager=self.language_manager
            )
            
            logger.debug("PDF scanner initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing scanner: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to initialize scanner: {}").format(str(e))
            )
    
    def _reset_scan_ui(self):
        """Reset the UI for a new scan."""
        # Clear previous results
        if hasattr(self, 'duplicates_tree'):
            self.duplicates_tree.clear()
        
        # Reset status
        self.status_bar.clearMessage()
    
    def cancel_scan(self):
        """Cancel the current scan operation."""
        if hasattr(self, '_scanner') and self._scanner:
            self._scanner.stop_scan()
        
        if hasattr(self, 'scan_thread') and self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait()
        
        if self.progress_dialog:
            # Stop any pending updates and close the dialog
            if hasattr(self.progress_dialog, '_update_timer') and self.progress_dialog._update_timer.isActive():
                self.progress_dialog._update_timer.stop()
            
            # Process events to ensure the dialog is properly updated before closing
            QCoreApplication.processEvents()
            
            self.progress_dialog.accept()
            self.progress_dialog = None
            
            # Process events again to ensure the dialog is fully closed
            QCoreApplication.processEvents()
        
        self.status_bar.showMessage(self.tr("Scan cancelled"), 3000)
    
    def _auto_close_progress_dialog(self):
        """Automatically close the progress dialog after scan completion."""
        logger.debug("Auto-closing progress dialog")
        if self.progress_dialog:
            # Stop any pending updates
            if hasattr(self.progress_dialog, '_update_timer') and self.progress_dialog._update_timer.isActive():
                self.progress_dialog._update_timer.stop()
            
            # Close the dialog
            if self.progress_dialog.isVisible():
                logger.debug("Closing progress dialog automatically")
                self.progress_dialog.close()
            
            # Clear the reference
            self.progress_dialog = None
            
            # Process events to ensure everything is cleaned up
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            logger.debug("Progress dialog auto-close completed")
    
    def _cleanup_progress_dialog(self):
        """Clean up the progress dialog reference when it's closed."""
        logger.debug("Cleaning up progress dialog reference")
        if self.progress_dialog:
            # Stop any pending updates
            if hasattr(self.progress_dialog, '_update_timer') and self.progress_dialog._update_timer.isActive():
                self.progress_dialog._update_timer.stop()
            
            # Process events to ensure the dialog is properly updated
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            
            # Close the dialog if it's still visible
            if self.progress_dialog.isVisible():
                logger.debug("Closing visible progress dialog")
                self.progress_dialog.close()
            
            # Clear the reference
            self.progress_dialog = None
            
            # Process events again to ensure everything is cleaned up
            QCoreApplication.processEvents()
            logger.debug("Progress dialog cleanup completed")
    
    def _cleanup_scan(self):
        """Clean up resources after scan is complete or cancelled."""
        if hasattr(self, 'scan_thread') and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait()
        
        # Note: Don't automatically close the progress dialog here
        # The dialog should be closed either by user clicking Close button
        # or when scan is cancelled (handled in cancel_scan method)
    
    def _on_scan_finished(self, duplicate_groups=None):
        """Handle scan completion."""
        logger.info("Scan finished")
        self.scan_in_progress = False
        self.last_scan_duplicates = duplicate_groups or []
        
        # Clean up the scan thread properly
        if hasattr(self, 'scan_thread') and self.scan_thread:
            logger.debug("Cleaning up scan thread")
            self.scan_thread.quit()
            self.scan_thread.wait()  # Wait for thread to finish
            self.scan_thread = None
        
        # Update status
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(
                self.tr("Found {} duplicate groups").format(len(self.last_scan_duplicates)),
                5000
            )
        
        # Update progress dialog to show completion status
        if self.progress_dialog:
            logger.debug("Setting progress dialog to complete state")
            self.progress_dialog.set_scan_complete()
            
            # Auto-close the dialog after 2 seconds since close button doesn't work
            logger.debug("Scheduling auto-close of progress dialog in 2 seconds")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, self._auto_close_progress_dialog)
        
        # Update the UI directly since we're already on the main thread
        self._update_scan_results_ui()
    
    def _update_scan_results_ui(self):
        """Update the UI with the latest scan results.
        
        This method is called on the main thread after a scan completes.
        """
        try:
            if not hasattr(self, 'main_ui') or not hasattr(self.main_ui, 'update_duplicates_tree'):
                logger.warning("MainUI or update_duplicates_tree method not found")
                return
                
            # Update the duplicates tree in the main UI
            self.main_ui.update_duplicates_tree(self.last_scan_duplicates)
            logger.info(f"Updated UI with {len(self.last_scan_duplicates)} duplicate groups")
                
            logger.info(f"UI updated with {len(self.last_scan_duplicates)} duplicate groups")
            
        except Exception as e:
            logger.error(f"Error updating scan results UI: {e}", exc_info=True)
            
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in a human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0 or unit == 'GB':
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} B"
        
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp in a human-readable format."""
        if not timestamp:
            return ""
        return QDateTime.fromSecsSinceEpoch(int(timestamp)).toString(Qt.DateFormat.SystemLocaleShortDate)
    
    def _on_duplicates_found(self, duplicates: List[List[Dict[str, Any]]]):
        """Handle the event when duplicates are found during a scan.
        
        Args:
            duplicates: List of duplicate file groups, where each group is a list of file info dicts
        """
        try:
            logger.info(f"Found {len(duplicates)} groups of duplicate files")
            self.last_scan_duplicates = duplicates
            
            # Update the UI with the found duplicates
            if hasattr(self, 'main_ui') and hasattr(self.main_ui, 'update_duplicates_tree'):
                self.main_ui.update_duplicates_tree(duplicates)
            elif hasattr(self, 'update_duplicates_list'):
                # Fallback to old method if exists
                self.update_duplicates_list(duplicates)
                
            # Enable relevant UI elements
            if hasattr(self, 'action_export_csv') and hasattr(self.action_export_csv, 'setEnabled'):
                self.action_export_csv.setEnabled(True)
                
        except Exception as e:
            logger.error(f"Error processing found duplicates: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("An error occurred while processing duplicate files.")
            )
    
    def _on_scan_status(self, message: str, current: int, total: int):
        """Handle scan status updates."""
        if hasattr(self, 'status_bar') and hasattr(self.status_bar, 'showMessage'):
            self.status_bar.showMessage(message)
        
        # Update progress dialog if it exists
        if self.progress_dialog and not self.progress_dialog._cancelled:
            self.progress_dialog.update_progress(current, total)
        
        # Update status bar less frequently to improve performance
        if current % 10 == 0 or current == total:
            self.status_bar.showMessage(f"{message} ({current}/{total})")
    
    def _on_scan_progress(self, current: int, total: int, current_file: str):
        """Handle scan progress updates.
        
        Args:
            current: Current file number being processed
            total: Total number of files to process
            current_file: Path to the current file being processed
        """
        if self.progress_dialog and not self.progress_dialog._cancelled:
            # Calculate number of duplicates found so far
            duplicates_found = sum(len(group) for group in self.last_scan_duplicates)
            
            # Update progress dialog
            self.progress_dialog.update_progress(
                current, 
                total, 
                os.path.basename(current_file),
                duplicates_found
            )
            
            # Update status less frequently to improve performance
            if current % 10 == 0 or current == total:
                self.status_bar.showMessage(
                    self.tr("Scanning: {}/{} files | Duplicates found: {}")
                    .format(current, total, duplicates_found)
                )
    
    def _start_scan(self, folder_path: str):
        """Start scanning the given folder with current filter settings.
        
        Args:
            folder_path: Path to the folder to scan
        """
        try:
            # Create and show progress dialog
            if self.progress_dialog is None:
                self.progress_dialog = ScanProgressDialog(
                    self,
                    self.tr("Scanning for Duplicates"),
                    self.tr("Preparing to scan: {}").format(folder_path)
                )
                self.progress_dialog.cancelled.connect(self.cancel_scan)
                self.progress_dialog.close_requested.connect(self._cleanup_progress_dialog)
                
                # Configure dialog properties
                self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
                self.progress_dialog.setWindowFlags(
                    self.progress_dialog.windowFlags() & 
                    ~Qt.WindowType.WindowContextHelpButtonHint |
                    Qt.WindowType.WindowStaysOnTopHint
                )
                
                # Show the dialog
                self.progress_dialog.show()
                self.progress_dialog.raise_()
                self.progress_dialog.activateWindow()
                
                # Force update to ensure the dialog is visible
                QCoreApplication.processEvents()
            
            # Initialize scanner with proper threading
            if not hasattr(self, '_scanner') or self._scanner is None:
                self._init_scanner_without_thread()
            elif not hasattr(self, 'scan_thread') or self.scan_thread is None:
                # Scanner exists but no thread, create thread and move scanner
                self.scan_thread = QThread()
                self.scan_thread.setObjectName("PDFScanThread")
                self._scanner.moveToThread(self.scan_thread)
                
                # Connect signals with proper connection type
                self._scanner.progress_updated.connect(
                    self._on_scan_progress,
                    Qt.ConnectionType.QueuedConnection
                )
                self._scanner.status_updated.connect(
                    self._on_scan_status,
                    Qt.ConnectionType.QueuedConnection
                )
                self._scanner.duplicates_found.connect(
                    self._on_duplicates_found,
                    Qt.ConnectionType.QueuedConnection
                )
                self._scanner.finished.connect(
                    self._on_scan_finished,
                    Qt.ConnectionType.QueuedConnection
                )
                
                # Connect thread signals
                self.scan_thread.started.connect(self._scanner.start_scan)
                self.scan_thread.finished.connect(self.scan_thread.deleteLater)
            
            # Reset UI
            self._reset_scan_ui()
            
            # Update status bar
            self.status_bar.showMessage(self.tr("Scanning: {}").format(folder_path))
            
            # Connect thread signals (only if not already connected)
            if not self.scan_thread.receivers(self.scan_thread.started):
                self.scan_thread.started.connect(self._scanner.start_scan)
            if not self.scan_thread.receivers(self.scan_thread.finished):
                self.scan_thread.finished.connect(self.scan_thread.deleteLater)
            
            # Set scan parameters
            self._scanner.scan_parameters = {
                'directory': folder_path,
                'recursive': True,
                'min_file_size': 1024,  # 1KB
                'max_file_size': 1024 * 1024 * 1024,  # 1GB
                'min_similarity': self.settings.get('comparison_threshold', 0.8),
                'enable_text_compare': self.settings.get('enable_text_compare', True)
            }
            
            # Start the thread
            self.scan_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}", exc_info=True)
            self._cleanup_scan()
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to start scan: {}".format(str(e)))
            )
    
    
    def scan_folder(self, folder_path: str):
        """Scan a folder for duplicate PDF files.
        
        Args:
            folder_path: Path to the folder to scan
        """
        try:
            # Create and show progress dialog
            if self.progress_dialog is None:
                self.progress_dialog = ScanProgressDialog(
                    self,
                    self.tr("Scanning for Duplicates"),
                    self.tr("Preparing to scan: {}").format(folder_path)
                )
                self.progress_dialog.cancelled.connect(self.cancel_scan)
                self.progress_dialog.close_requested.connect(self._cleanup_progress_dialog)
            
            # Show the dialog
            self.progress_dialog.show()
            self.progress_dialog.raise_()
            self.progress_dialog.activateWindow()
            
            # Start the scan
            self._start_scan(folder_path)
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}", exc_info=True)
            self._cleanup_scan()
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to start scan: {}").format(str(e))
            )
            
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
            # Get the duplicates from last scan
            if not hasattr(self, 'last_scan_duplicates') or not self.last_scan_duplicates:
                QMessageBox.information(
                    self,
                    self.tr("Export CSV"),
                    self.tr("No results to export. Please run a scan first.")
                )
                return
                
            duplicate_groups = self.last_scan_duplicates
            if not duplicate_groups:
                QMessageBox.information(
                    self,
                    self.tr("Export CSV"),
                    self.tr("No results to export. Please run a scan first.")
                )
                return
            
            # Function to extract files from a group
            def get_files_from_group(group):
                if isinstance(group, dict):
                    if 'files' in group and hasattr(group['files'], '__iter__'):
                        return group['files']
                    return group  # Assume the dict itself contains file info
                elif hasattr(group, 'files') and hasattr(group.files, '__iter__'):
                    return group.files
                elif hasattr(group, '__iter__') and not isinstance(group, (str, bytes)):
                    return group  # Assume it's already a list of files
                return [group]  # Single file
            
            # Collect all files from all groups
            all_files = []
            for group in duplicate_groups:
                try:
                    files = get_files_from_group(group)
                    if files:
                        all_files.extend(files)
                except Exception as e:
                    logger.error(f"Error processing group: {e}", exc_info=True)
            
            if not all_files:
                QMessageBox.warning(
                    self,
                    self.tr("Export CSV"),
                    self.tr("No files found in scan results to export.")
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
                return  # User cancelled
                
            # Ensure the file has .csv extension
            if not dest_path.lower().endswith('.csv'):
                dest_path += '.csv'
                
            # Function to get file info
            def get_file_info(file_obj):
                if isinstance(file_obj, dict):
                    return {
                        'path': str(file_obj.get('path', '')),
                        'size': str(file_obj.get('size', '')),
                        'modified': str(file_obj.get('modified', ''))
                    }
                elif hasattr(file_obj, 'path') and hasattr(file_obj, 'size'):
                    return {
                        'path': str(file_obj.path),
                        'size': str(file_obj.size),
                        'modified': str(getattr(file_obj, 'modified', ''))
                    }
                return {'path': str(file_obj), 'size': '', 'modified': ''}
                
            # Prepare data for CSV
            csv_data = []
            for file_obj in all_files:
                try:
                    file_info = get_file_info(file_obj)
                    csv_data.append([
                        file_info['path'],
                        file_info['size'],
                        file_info['modified']
                    ])
                except Exception as e:
                    logger.error(f"Error processing file {file_obj}: {e}")
                    continue
                    
            if not csv_data:
                QMessageBox.warning(
                    self,
                    self.tr("Export CSV"),
                    self.tr("No valid file data found to export.")
                )
                return
                
            # Write to CSV
            try:
                with open(dest_path, 'w', encoding='utf-8') as f:
                    # Write header
                    f.write('File Path,Size (bytes),Last Modified\n')
                    # Write data
                    for row in csv_data:
                        # Escape commas and quotes in the data
                        escaped_row = ['"' + str(field).replace('"', '""') + '"' for field in row]
                        f.write(','.join(escaped_row) + '\n')
                        
                QMessageBox.information(
                    self,
                    self.tr("Export Successful"),
                    self.tr(f"Successfully exported {len(csv_data)} files to:\n{dest_path}")
                )
                
            except Exception as e:
                logger.error(f"Error writing to CSV: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    self.tr("Export Failed"),
                    self.tr(f"Failed to export to CSV: {str(e)}")
                )
            
        except Exception as e:
            logger.error(f"Unexpected error in export: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Export Error"),
                self.tr(f"An unexpected error occurred: {str(e)}")
            )
    
    def on_delete_selected(self):
        """Delete selected files from the duplicates tree.
        
        Moves selected files to the Recycle Bin if send2trash is available,
        otherwise permanently deletes them.
        """
        try:
            logger.info("DEBUG: on_delete_selected method started")
            # Check if duplicates_tree exists in main_ui
            logger.info(f"DEBUG: hasattr(self, 'main_ui'): {hasattr(self, 'main_ui')}")
            if hasattr(self, 'main_ui'):
                logger.info(f"DEBUG: hasattr(self.main_ui, 'duplicates_tree'): {hasattr(self.main_ui, 'duplicates_tree')}")
                if hasattr(self.main_ui, 'duplicates_tree'):
                    logger.info(f"DEBUG: self.main_ui.duplicates_tree: {self.main_ui.duplicates_tree}")
            
            if (not hasattr(self, 'main_ui') or 
                not hasattr(self.main_ui, 'duplicates_tree') or 
                not self.main_ui.duplicates_tree):
                logger.warning("Duplicates tree not available for deletion")
                QMessageBox.information(
                    self,
                    self.tr("No Scan Results"),
                    self.tr("Please run a scan first to find duplicate PDF files before attempting to delete them.")
                )
                return
            
            # Get selected items
            selected_items = self.main_ui.duplicates_tree.selectedItems()
            logger.info(f"DEBUG: Found {len(selected_items)} selected items")
            
            if not selected_items:
                QMessageBox.information(
                    self,
                    self.tr("No Selection"),
                    self.tr("Please select files to delete.")
                )
                return
            
            # Debug: Log details of selected items
            for i, item in enumerate(selected_items):
                file_path = item.data(0, Qt.ItemDataRole.UserRole)
                logger.info(f"DEBUG: Selected item {i}: text='{item.text(0)}', path='{file_path}'")
            
            # Collect files to delete
            files_to_delete = []
            for item in selected_items:
                # Get file path from item data (stored in Qt.UserRole)
                file_path = item.data(0, Qt.ItemDataRole.UserRole)
                if file_path and os.path.exists(file_path):
                    files_to_delete.append(file_path)
            
            if not files_to_delete:
                QMessageBox.information(
                    self,
                    self.tr("No Valid Files"),
                    self.tr("No valid files found for deletion.")
                )
                return
            
            # Confirm deletion
            if len(files_to_delete) == 1:
                confirm_msg = self.tr("Are you sure you want to delete this file?\n\n{}").format(files_to_delete[0])
            else:
                confirm_msg = self.tr("Are you sure you want to delete {} files?").format(len(files_to_delete))
                confirm_msg += "\n\n" + "\n".join(files_to_delete[:5])  # Show first 5 files
                if len(files_to_delete) > 5:
                    confirm_msg += f"\n... and {len(files_to_delete) - 5} more"
            
            reply = QMessageBox.question(
                self,
                self.tr("Confirm Deletion"),
                confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Delete files
            deleted_files = []
            failed_files = []
            
            for file_path in files_to_delete:
                try:
                    if SEND2TRASH_AVAILABLE:
                        send2trash.send2trash(file_path)
                        logger.info(f"Moved file to Recycle Bin: {file_path}")
                    else:
                        os.remove(file_path)
                        logger.info(f"Permanently deleted file: {file_path}")
                    deleted_files.append(file_path)
                except Exception as e:
                    logger.error(f"Failed to delete file {file_path}: {e}")
                    failed_files.append((file_path, str(e)))
            
            # Show results
            if deleted_files:
                # Remove deleted items from the tree
                for item in selected_items:
                    file_path = item.data(0, Qt.ItemDataRole.UserRole)
                    if file_path in deleted_files:
                        parent = item.parent()
                        if parent:
                            parent.removeChild(item)
                            # If parent has no more children, remove it too
                            if parent.childCount() == 0:
                                grandparent = parent.parent()
                                if grandparent:
                                    grandparent.removeChild(parent)
                                else:
                                    # Parent is a top-level item
                                    root = self.main_ui.duplicates_tree.invisibleRootItem()
                                    root.removeChild(parent)
                        else:
                            # Item is top-level
                            root = self.main_ui.duplicates_tree.invisibleRootItem()
                            root.removeChild(item)
            
            # Show success message
            if deleted_files:
                if SEND2TRASH_AVAILABLE:
                    msg = self.tr("Successfully moved {} file(s) to Recycle Bin.").format(len(deleted_files))
                else:
                    msg = self.tr("Successfully deleted {} file(s).").format(len(deleted_files))
                
                if failed_files:
                    msg += "\n\n" + self.tr("Some files could not be deleted:")
                    for file_path, error in failed_files[:3]:  # Show first 3 errors
                        msg += f"\n- {os.path.basename(file_path)}: {error}"
                    if len(failed_files) > 3:
                        msg += f"\n... and {len(failed_files) - 3} more"
                
                QMessageBox.information(self, self.tr("Deletion Complete"), msg)
            elif failed_files:
                # All files failed to delete
                error_msg = self.tr("Failed to delete any files. Errors:")
                for file_path, error in failed_files:
                    error_msg += f"\n- {os.path.basename(file_path)}: {error}"
                QMessageBox.critical(self, self.tr("Deletion Failed"), error_msg)
            
            # Update status bar
            if deleted_files:
                self.status_bar.showMessage(
                    self.tr("Deleted {} file(s)").format(len(deleted_files)), 
                    3000
                )
        except Exception as e:
            logger.error(f"DEBUG: Error in on_delete_selected: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Delete Error"),
                self.tr(f"An error occurred while trying to delete files: {str(e)}")
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
