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
    QLocale, QTranslator, QLibraryInfo, QMetaObject, Q_ARG
)

from datetime import datetime
import csv

# Import our custom modules
from script.main_window import MainWindow
from script.settings import AppSettings
from script.lang_mgr import LanguageManager
from script.logger import get_logger
from script.settings_dialog import SettingsDialog
from script.scanner import PDFScanner
from PyQt6.QtCore import QThread, QObject
from PyQt6.QtWidgets import QProgressBar, QMessageBox

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
        
        # Initialize filter settings
        self.current_filters = {
            'min_size': 0,  # in bytes
            'max_size': 100 * 1024 * 1024,  # 100MB in bytes
            'name_pattern': '',
            'enable_text_compare': True,
            'min_similarity': 0.8
        }
        
        # Storage for last scan results
        self.last_scan_duplicates: List[List[Dict[str, Any]]] = []
        
        # Initialize the scanner
        self._init_scanner()
    
    def _init_scanner(self):
        """Initialize the PDF scanner with default settings and connect signals."""
        logger.info("Initializing scanner...")
        
        # Clean up any existing scanner and thread
        if hasattr(self, '_scanner'):
            try:
                if hasattr(self._scanner, 'deleteLater'):
                    self._scanner.deleteLater()
            except Exception as e:
                logger.warning(f"Error cleaning up scanner: {e}")
        
        if hasattr(self, 'scan_thread'):
            try:
                if self.scan_thread.isRunning():
                    self.scan_thread.quit()
                    self.scan_thread.wait(1000)
            except Exception as e:
                logger.warning(f"Error cleaning up thread: {e}")
        
        try:
            # Create new scanner and thread with proper initialization
            from PyQt6.QtCore import QThread
            self.scan_thread = QThread()
            
            # Get settings for scanner
            comparison_threshold = self.settings.get('comparison_threshold', 0.95)
            dpi = self.settings.get('dpi', 150)
            
            # Create scanner with settings
            self._scanner = PDFScanner(
                threshold=comparison_threshold,
                dpi=dpi
            )
            
            # Move scanner to thread
            self._scanner.moveToThread(self.scan_thread)
            
            # Connect signals
            self._scanner.progress_updated.connect(self._on_scan_progress)
            self._scanner.status_updated.connect(self._on_scan_status)
            self._scanner.duplicates_found.connect(self._on_duplicates_found)
            self._scanner.finished.connect(self._on_scan_finished)
            
            # Set up status callback
            self._scanner.set_status_callback(self._on_scan_status)
            
            # Store the scan method reference
            self._scanner_scan_method = self._scanner.scan_directory
            
            # Connect thread signals
            self._scanner.finished.connect(self.scan_thread.quit)
            self._scanner.finished.connect(self._scanner.deleteLater)
            self.scan_thread.finished.connect(self.scan_thread.deleteLater)
            
            # Make sure the scanner is properly set up in the thread
            self._scanner.moveToThread(self.scan_thread)
            
            # Set up progress bar if needed
            if not hasattr(self, 'progress_bar') and hasattr(self, 'status_bar'):
                self.progress_bar = QProgressBar()
                self.progress_bar.setMinimum(0)
                self.progress_bar.setMaximum(100)
                self.progress_bar.setTextVisible(True)
                self.progress_bar.setVisible(False)
                self.status_bar.addPermanentWidget(self.progress_bar)
                
            logger.info("Scanner initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize scanner: {e}", exc_info=True)
            return False
    
    def _start_scan(self, folder_path: str):
        """Start scanning the given folder with current filter settings.
        
        Args:
            folder_path: Path to the folder to scan
        """
        try:
            if not folder_path or not os.path.isdir(folder_path):
                QMessageBox.warning(
                    self,
                    self.language_manager.tr("dialog.warning", "Warning"),
                    self.language_manager.tr("errors.invalid_folder", "Please select a valid folder to scan.")
                )
                return
                
            # Update status
            self.status_bar.showMessage(
                self.language_manager.tr("status.scanning", "Scanning folder: {folder}").format(
                    folder=os.path.basename(folder_path)
                )
            )
            
            # Initialize the scanner and thread
            if not self._init_scanner():
                error_msg = self.language_manager.tr("errors.scanner_init_failed", "Failed to initialize scanner. Please check the logs for details.")
                logger.error(error_msg)
                QMessageBox.critical(self, self.language_manager.tr("dialog.error", "Error"), error_msg)
                return
            
            try:
                # Configure scan parameters
                self._scanner.scan_directory = folder_path
                self._scanner.recursive = True
                self._scanner.min_file_size = self.current_filters['min_size']
                self._scanner.max_file_size = self.current_filters['max_size']
                self._scanner.min_similarity = self.current_filters['min_similarity']
                self._scanner.enable_text_compare = self.current_filters['enable_text_compare']
                
                # Clear previous results
                self.last_scan_duplicates = []
                if hasattr(self, 'duplicates_tree'):
                    self.duplicates_tree.clear()
                
                # Show progress bar
                if hasattr(self, 'progress_bar'):
                    self.progress_bar.setValue(0)
                    self.progress_bar.setVisible(True)
                
                # Ensure scanner is properly initialized
                if not hasattr(self, '_scanner') or not hasattr(self, 'scan_thread'):
                    logger.error("Scanner or thread not initialized")
                    QMessageBox.critical(self, 
                        self.language_manager.tr("dialog.error", "Error"),
                        self.language_manager.tr("errors.scanner_not_initialized", "Scanner is not properly initialized. Please restart the application.")
                    )
                    return
                
                # Debug thread state
                logger.debug(f"Thread state - isRunning: {self.scan_thread.isRunning()}, isFinished: {self.scan_thread.isFinished()}")
                
                try:
                    # Disconnect any existing connections to avoid multiple calls
                    try:
                        self.scan_thread.started.disconnect()
                    except (TypeError, RuntimeError):
                        pass  # No connections to disconnect
                    
                    # Create a function to start the scan with error handling
                    def start_scan():
                        try:
                            logger.info(f"Starting scan in thread for directory: {folder_path}")
                            # Make sure we're in the right thread
                            if QThread.currentThread() != self.scan_thread:
                                logger.error("Not in scanner thread!")
                                return
                                
                            # Call the scan method with all required parameters
                            self._scanner_scan_method(
                                directory=folder_path,
                                recursive=True,
                                min_file_size=self.current_filters.get('min_size', 1024),
                                max_file_size=self.current_filters.get('max_size', 1024*1024*1024)
                            )
                        except Exception as e:
                            logger.error(f"Error in scan thread: {e}", exc_info=True)
                            self._on_scan_status(f"Error: {str(e)}", 0, 0)
                    
                    # Connect the start_scan function to the thread's started signal
                    self.scan_thread.started.connect(start_scan)
                    
                    # Start the thread
                    logger.info("Starting scan thread...")
                    self.scan_thread.start()
                    
                    # Verify the thread started
                    if not self.scan_thread.isRunning():
                        raise RuntimeError("Thread failed to start")
                        
                    logger.debug(f"Thread started successfully. Thread running: {self.scan_thread.isRunning()}")
                    
                except Exception as e:
                    error_msg = f"Failed to start scan thread: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    QMessageBox.critical(self, 
                                      self.language_manager.tr("dialog.error", "Error"),
                                      self.language_manager.tr("errors.thread_start_failed", "Failed to start scan thread: {error}").format(error=str(e)))
                    
            except Exception as e:
                error_msg = self.language_manager.tr("errors.scan_start_failed", "Failed to start scan: {error}").format(error=str(e))
                logger.error(error_msg, exc_info=True)
                QMessageBox.critical(self, self.language_manager.tr("dialog.error", "Error"), error_msg)
            
            logger.info(f"Started scanning folder: {folder_path}")
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}", exc_info=True)
            
            # Update UI
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(False)
                
            # Show error message
            QMessageBox.critical(
                self,
                self.language_manager.tr("dialog.error", "Error"),
                self.language_manager.tr(
                    "errors.scan_failed", 
                    "Failed to start scan: {error}"
                ).format(error=str(e))
            )
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("status.scan_failed", "Scan failed: {error}").format(error=str(e)),
                    5000  # Show for 5 seconds
                )
    
    def _on_scan_progress(self, current: int, total: int, path: str):
        """Handle scan progress updates."""
        try:
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setMaximum(total)
                self.progress_bar.setValue(current)
                self.progress_bar.setVisible(True)
                
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr(
                        "status.scan_progress", 
                        "Scanning: {current}/{total} - {filename}"
                    ).format(
                        current=current,
                        total=total,
                        filename=os.path.basename(path)
                    )
                )
        except Exception as e:
            logger.error(f"Error updating scan progress: {e}", exc_info=True)
    
    def _on_scan_status(self, message: str, current: int, total: int):
        """Handle scan status updates."""
        try:
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(message)
                
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setMaximum(total if total > 0 else 1)
                self.progress_bar.setValue(current)
                self.progress_bar.setVisible(True)
        except Exception as e:
            logger.error(f"Error updating scan status: {e}", exc_info=True)
    
    def _on_scan_progress(self, current: int, total: int, current_file: str):
        """Handle scan progress updates.
        
        Args:
            current: Current file number being processed
            total: Total number of files to process
            current_file: Path to the current file being processed
        """
        try:
            # Update progress bar if it exists
            if hasattr(self, 'progress_bar'):
                if not self.progress_bar.isVisible():
                    self.progress_bar.setVisible(True)
                self.progress_bar.setMaximum(total)
                self.progress_bar.setValue(current)
            
            # Update status message
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr(
                        "status.scan_progress",
                        "Scanning: {current}/{total} - {file}"
                    ).format(
                        current=current,
                        total=total,
                        file=os.path.basename(current_file)
                    )
                )
                
        except Exception as e:
            logger.error(f"Error updating scan progress: {e}", exc_info=True)
    
    def _on_scan_status(self, message: str, current: int, total: int):
        """Handle scan status updates.
        
        Args:
            message: Status message to display
            current: Current progress value
            total: Maximum progress value
        """
        try:
            # Update progress bar if it exists
            if hasattr(self, 'progress_bar'):
                if not self.progress_bar.isVisible():
                    self.progress_bar.setVisible(True)
                self.progress_bar.setMaximum(total if total > 0 else 1)
                self.progress_bar.setValue(current)
            
            # Update status message
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(message)
                
        except Exception as e:
            logger.error(f"Error updating scan status: {e}", exc_info=True)
    
    def _on_duplicates_found(self, duplicate_groups):
        """Handle when duplicates are found during scanning.
        
        Args:
            duplicate_groups: List of duplicate file groups found
        """
        try:
            logger.info(f"Found {len(duplicate_groups)} duplicate groups")
            self.last_scan_duplicates = duplicate_groups
            
            # Update the UI with the found duplicates
            self._update_scan_results_ui()
            
            # Update status message
            if hasattr(self, 'status_bar'):
                status_msg = self.language_manager.tr(
                    "status.duplicates_found",
                    "Found {count} duplicate groups"
                ).format(count=len(duplicate_groups))
                self.status_bar.showMessage(status_msg, 5000)  # Show for 5 seconds
                
        except Exception as e:
            logger.error(f"Error handling duplicates found: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr(
                        "errors.duplicates_failed",
                        "Error processing duplicates: {error}"
                    ).format(error=str(e)),
                    5000  # Show for 5 seconds
                )
    
    def _on_scan_finished(self, duplicate_groups=None):
        """Handle scan completion.
        
        Args:
            duplicate_groups: List of duplicate file groups found during the scan
        """
        try:
            # Update UI elements
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(False)
                
            # Update status message
            status_msg = self.language_manager.tr(
                "status.scan_complete", 
                "Scan complete! Found {count} duplicate groups"
            )
            
            # Process scan results if provided
            if duplicate_groups is not None:
                self.last_scan_duplicates = duplicate_groups
                status_msg = status_msg.format(count=len(duplicate_groups))
            elif hasattr(self, '_scanner') and hasattr(self._scanner, 'duplicate_groups'):
                self.last_scan_duplicates = self._scanner.duplicate_groups
                status_msg = status_msg.format(count=len(self.last_scan_duplicates))
            else:
                status_msg = self.language_manager.tr(
                    "status.scan_complete_no_duplicates",
                    "Scan complete! No duplicates found."
                )
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(status_msg, 5000)  # Show for 5 seconds
                
            # Update the UI with scan results
            self._update_scan_results_ui()
                
        except Exception as e:
            logger.error(f"Error handling scan completion: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr(
                        "errors.scan_complete_failed",
                        "Error completing scan: {error}"
                    ).format(error=str(e)),
                    5000  # Show for 5 seconds
                )
    
    def _update_scan_results_ui(self):
        """Update the UI with the latest scan results."""
        try:
            # Initialize the duplicates tree if it doesn't exist
            if not hasattr(self, 'duplicates_tree') or self.duplicates_tree is None:
                self._init_duplicates_tree()
            
            # Clear existing items
            self.duplicates_tree.clear()
            
            # Check if we have any duplicate groups to display
            if not hasattr(self, 'last_scan_duplicates') or not self.last_scan_duplicates:
                # No duplicates found, show a message
                no_duplicates_item = QTreeWidgetItem([
                    self.language_manager.tr("ui.no_duplicates", "No duplicate files found."),
                    "", "", ""
                ])
                self.duplicates_tree.addTopLevelItem(no_duplicates_item)
                return
                
            # Add each duplicate group to the tree
            valid_groups = 0
            for group_idx, group in enumerate(self.last_scan_duplicates):
                if group and 'files' in group and len(group['files']) >= 2:
                    self._add_duplicate_group_to_ui(valid_groups, group)
                    valid_groups += 1
            
            # If no valid groups were found, show a message
            if valid_groups == 0:
                no_duplicates_item = QTreeWidgetItem([
                    self.language_manager.tr("ui.no_duplicates", "No duplicate files found."),
                    "", "", ""
                ])
                self.duplicates_tree.addTopLevelItem(no_duplicates_item)
            
            # Resize columns to fit content
            for i in range(self.duplicates_tree.columnCount()):
                self.duplicates_tree.resizeColumnToContents(i)
                
            logger.info(f"Updated UI with {valid_groups} duplicate groups")
            
        except Exception as e:
            logger.error(f"Error updating scan results UI: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("errors.ui_update_failed", "Failed to update UI: {error}").format(error=str(e)),
                    5000  # Show for 5 seconds
                )
    
    def _init_duplicates_tree(self):
        """Initialize the duplicates tree widget."""
        from PyQt6.QtWidgets import QTreeWidget
        from PyQt6.QtCore import Qt
        
        self.duplicates_tree = QTreeWidget()
        self.duplicates_tree.setHeaderLabels([
            self.language_manager.tr("ui.file_name", "File Name"),
            self.language_manager.tr("ui.file_path", "Path"),
            self.language_manager.tr("ui.file_size", "Size"),
            self.language_manager.tr("ui.similarity", "Similarity")
        ])
        self.duplicates_tree.setColumnCount(4)
        self.duplicates_tree.setAlternatingRowColors(True)
        self.duplicates_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.duplicates_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.duplicates_tree.customContextMenuRequested.connect(self._show_duplicate_context_menu)
        
        # Replace the file list with the tree widget
        layout = self.main_ui.file_list.parent().layout()
        layout.replaceWidget(self.main_ui.file_list, self.duplicates_tree)
        self.main_ui.file_list.deleteLater()
        self.main_ui.file_list = self.duplicates_tree
    
    def _add_duplicate_group_to_ui(self, group_idx, group):
        """Add a duplicate group to the UI tree."""
        if not group or 'files' not in group or len(group['files']) < 2:
            return
            
        from PyQt6.QtWidgets import QTreeWidgetItem
        from PyQt6.QtCore import Qt
        
        # Create a group item
        group_item = QTreeWidgetItem([
            self.language_manager.tr("ui.duplicate_group", "Duplicate Group {num}").format(num=group_idx + 1),
            f"({len(group['files'])} {self.language_manager.tr('ui.files', 'files')})",
            "",  # Empty size for group
            f"{group.get('similarity', 0) * 100:.1f}%" if 'similarity' in group else ""
        ])
        group_item.setData(0, Qt.ItemDataRole.UserRole, group)
        group_item.setExpanded(True)
        
        # Add files to the group
        for file_info in group['files']:
            file_path = file_info.get('path', '')
            file_name = os.path.basename(file_path)
            file_size = file_info.get('size', 0)
            
            # Format file size
            size_str = self._format_file_size(file_size)
            
            # Create file item
            file_item = QTreeWidgetItem([
                file_name,
                os.path.dirname(file_path),
                size_str,
                f"{group.get('similarity', 0) * 100:.1f}%" if 'similarity' in group else "100%"
            ])
            file_item.setData(0, Qt.ItemDataRole.UserRole, file_info)
            group_item.addChild(file_item)
        
        self.duplicates_tree.addTopLevelItem(group_item)
    
    def _format_file_size(self, size_bytes):
        """Format file size in a human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    def _show_duplicate_context_menu(self, position):
        """Show context menu for duplicate items."""
        try:
            if not hasattr(self, 'duplicates_tree'):
                return
                
            item = self.duplicates_tree.itemAt(position)
            if not item:
                return
                
            from PyQt6.QtWidgets import QMenu, QMessageBox
            from PyQt6.QtGui import QAction
            from PyQt6.QtCore import Qt
            
            menu = QMenu()
            
            # Add actions based on the selected item type
            if item.parent() is None:
                # Group item selected
                open_group_action = QAction(
                    self.language_manager.tr("actions.open_all", "Open All in Group"),
                    self
                )
                menu.addAction(open_group_action)
                
                action = menu.exec(self.duplicates_tree.viewport().mapToGlobal(position))
                
                if action == open_group_action:
                    self._open_duplicate_group(item)
            else:
                # File item selected
                open_file_action = QAction(
                    self.language_manager.tr("actions.open_file", "Open File"),
                    self
                )
                show_in_folder_action = QAction(
                    self.language_manager.tr("actions.show_in_folder", "Show in Folder"),
                    self
                )
                delete_file_action = QAction(
                    self.language_manager.tr("actions.delete_file", "Delete File"),
                    self
                )
                
                menu.addAction(open_file_action)
                menu.addAction(show_in_folder_action)
                menu.addSeparator()
                menu.addAction(delete_file_action)
                
                action = menu.exec(self.duplicates_tree.viewport().mapToGlobal(position))
                
                if action == open_file_action:
                    self._open_duplicate_file(item)
                elif action == show_in_folder_action:
                    self._show_in_folder(item)
                elif action == delete_file_action:
                    self._delete_duplicate_file(item)
                    
        except Exception as e:
            logger.error(f"Error showing context menu: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("errors.context_menu_failed", "Failed to show context menu: {error}").format(error=str(e)),
                    5000
                )
    
    def _open_duplicate_group(self, group_item):
        """Open all files in a duplicate group."""
        try:
            for i in range(group_item.childCount()):
                file_item = group_item.child(i)
                self._open_duplicate_file(file_item)
        except Exception as e:
            logger.error(f"Error opening duplicate group: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("errors.open_group_failed", "Failed to open group: {error}").format(error=str(e)),
                    5000
                )
    
    def _open_duplicate_file(self, file_item):
        """Open a duplicate file with the default application."""
        try:
            file_info = file_item.data(0, Qt.ItemDataRole.UserRole)
            if not file_info or 'path' not in file_info:
                return
                
            file_path = file_info['path']
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            # Use the system default application to open the file
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS and Linux
                import subprocess
                subprocess.run(['xdg-open', file_path], check=True)
                
        except Exception as e:
            logger.error(f"Error opening file: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("errors.open_file_failed", "Failed to open file: {error}").format(error=str(e)),
                    5000
                )
    
    def _show_in_folder(self, file_item):
        """Show the containing folder of a file in the system file manager."""
        try:
            file_info = file_item.data(0, Qt.ItemDataRole.UserRole)
            if not file_info or 'path' not in file_info:
                return
                
            file_path = os.path.dirname(file_info['path'])
            if not os.path.isdir(file_path):
                raise FileNotFoundError(f"Directory not found: {file_path}")
                
            # Open the folder in the system file manager
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS and Linux
                import subprocess
                subprocess.run(['xdg-open', file_path], check=True)
                
        except Exception as e:
            logger.error(f"Error showing in folder: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("errors.show_folder_failed", "Failed to show in folder: {error}").format(error=str(e)),
                    5000
                )
    
    def _delete_duplicate_file(self, file_item):
        """Delete a duplicate file after confirmation."""
        try:
            file_info = file_item.data(0, Qt.ItemDataRole.UserRole)
            if not file_info or 'path' not in file_info:
                return
                
            file_path = file_info['path']
            file_name = os.path.basename(file_path)
            
            # Ask for confirmation
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                self.language_manager.tr("dialog.confirm_delete", "Confirm Delete"),
                self.language_manager.tr("dialog.confirm_delete_msg", "Are you sure you want to delete '{file}'?").format(file=file_name),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete the file
                os.remove(file_path)
                
                # Remove the item from the tree
                parent = file_item.parent()
                if parent:
                    parent.removeChild(file_item)
                    
                    # If this was the last file in the group, remove the group
                    if parent.childCount() == 0:
                        self.duplicates_tree.takeTopLevelItem(
                            self.duplicates_tree.indexOfTopLevelItem(parent)
                        )
                
                # Show success message
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(
                        self.language_manager.tr("status.file_deleted", "Deleted: {file}").format(file=file_name),
                        5000
                    )
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.language_manager.tr("errors.delete_failed", "Failed to delete file: {error}").format(error=str(e)),
                    5000
                )
    
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
    
    def _update_scan_status(self, message: str, current: int, total: int):
        """Update the UI with scan status.
        
        Args:
            message: Status message
            current: Current file number
            total: Total number of files to process
        """
        try:
            # Ensure we're on the main thread for UI updates
            if not QThread.currentThread() == QApplication.instance().thread():
                QMetaObject.invokeMethod(
                    self,
                    '_update_scan_status',
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(str, message),
                    Q_ARG(int, current),
                    Q_ARG(int, total)
                )
                return
                
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"{message} ({current}/{total})")
            
            # Update progress bar
            if hasattr(self, 'progress_bar'):
                if total > 0:
                    # Ensure progress is within valid range
                    progress = max(0, min(100, int((current / total) * 100)))
                    self.progress_bar.setValue(progress)
                    
                    # Update format with current progress
                    if not self.progress_bar.isVisible():
                        self.progress_bar.setVisible(True)
                        
                    # Update format with current progress
                    self.progress_bar.setFormat(f"{message} - %p% (%v/%m)")
                    
        except Exception as e:
            logger.error(f"Error updating scan status: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"Error updating progress: {str(e)}", 5000)
    
    def _on_scan_finished(self):
        """Handle the scan finished event."""
        try:
            # Ensure we're on the main thread for UI updates
            if not QThread.currentThread() == QApplication.instance().thread():
                QMetaObject.invokeMethod(
                    self,
                    '_on_scan_finished',
                    Qt.ConnectionType.QueuedConnection
                )
                return
                
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.tr("Scan completed successfully"),
                    5000  # Show for 5 seconds
                )
                
            # Update progress bar
            if hasattr(self, 'progress_bar'):
                # Ensure progress is at 100%
                self.progress_bar.setValue(100)
                self.progress_bar.setFormat(self.tr("Scan completed - %p%"))
                
                # Hide progress bar after a short delay
                QTimer.singleShot(3000, lambda: self.progress_bar.setVisible(False))
                
            logger.info("PDF scan completed successfully")
            
            # Clean up thread
            if hasattr(self, 'scan_thread'):
                if self.scan_thread.isRunning():
                    self.scan_thread.quit()
                    self.scan_thread.wait(2000)  # Wait up to 2 seconds
                self.scan_thread = None
            
        except Exception as e:
            logger.error(f"Error in scan finished handler: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    self.tr("Error completing scan: {}").format(str(e)),
                    5000
                )
    
    def _scan_worker(self, folder_path: str):
        """Worker method that runs in a separate thread to perform the scan.
        
        Args:
            folder_path: Path to the folder to scan for PDF files
        """
        try:
            if not hasattr(self, '_scanner') or self._scanner is None:
                self._init_scanner()
            
            # Reset UI state
            if hasattr(self, 'main_ui') and hasattr(self.main_ui, 'file_list'):
                self.main_ui.file_list.clear()
            
            # Connect scanner signals
            if hasattr(self, 'scan_status') and hasattr(self._scanner, 'status_callback'):
                self._scanner.status_callback = self.scan_status.emit
                
            if hasattr(self, 'scan_progress') and hasattr(self._scanner, 'progress_callback'):
                self._scanner.progress_callback = self.scan_progress.emit
            
            # Update status
            if hasattr(self, 'scan_status'):
                self.scan_status.emit(self.tr("Preparing to scan..."), 0, 0)
            
            # Start the scan
            self._scanner.scan_directory(folder_path)
            
            # Update with results if available
            if hasattr(self._scanner, 'duplicate_groups'):
                self.last_scan_duplicates = self._scanner.duplicate_groups
                
                # Update UI with results on the main thread
                if hasattr(self, 'main_ui') and hasattr(self.main_ui, 'update_results'):
                    QMetaObject.invokeMethod(
                        self.main_ui, 
                        'update_results',
                        Qt.ConnectionType.QueuedConnection,
                        Q_ARG(list, self.last_scan_duplicates)
                    )
            
            # Signal that the scan is complete
            if hasattr(self, 'scan_finished'):
                self.scan_finished.emit()
                
        except Exception as e:
            logger.error(f"Error in scan worker: {e}", exc_info=True)
            if hasattr(self, 'scan_status'):
                self.scan_status.emit(
                    self.tr("Error during scan: {}").format(str(e)), 
                    0, 
                    0
                )
            if hasattr(self, 'scan_finished'):
                self.scan_finished.emit()
    
    def _init_scanner(self):
        """Initialize the PDF scanner with current settings."""
        try:
            logger.debug("Initializing PDF scanner...")
            
            # Clean up any existing scanner and thread
            if hasattr(self, '_scanner'):
                logger.debug("Cleaning up existing scanner...")
                try:
                    if hasattr(self, 'scan_thread') and self.scan_thread.isRunning():
                        self.scan_thread.quit()
                        self.scan_thread.wait(1000)
                    if hasattr(self._scanner, 'deleteLater'):
                        self._scanner.deleteLater()
                except Exception as e:
                    logger.warning(f"Error cleaning up existing scanner: {e}")
            
            # Get comparison settings from settings or use defaults
            comparison_threshold = float(self.settings.get('comparison_threshold', 0.95))
            dpi = int(self.settings.get('comparison_dpi', 200))
            logger.debug(f"Scanner settings - threshold: {comparison_threshold}, dpi: {dpi}")
            
            # Create and configure the thread first
            logger.debug("Creating QThread instance...")
            self.scan_thread = QThread()
            logger.debug(f"QThread created: {self.scan_thread}")
            
            # Initialize the scanner with proper parameters
            logger.debug("Creating PDFScanner instance...")
            self._scanner = PDFScanner(
                threshold=comparison_threshold,
                dpi=dpi
            )
            logger.debug("PDFScanner instance created successfully")
            
            # Move scanner to thread
            logger.debug("Moving scanner to thread...")
            self._scanner.moveToThread(self.scan_thread)
            logger.debug("Scanner moved to thread")
            
            # Connect signals
            logger.debug("Connecting signals...")
            self._scanner.progress_updated.connect(self._on_scan_progress)
            self._scanner.status_updated.connect(self._on_scan_status)
            self._scanner.duplicates_found.connect(self._on_duplicates_found)
            self._scanner.finished.connect(self._on_scan_finished)
            self._scanner.finished.connect(self.scan_thread.quit)
            self._scanner.finished.connect(self._scanner.deleteLater)
            self.scan_thread.finished.connect(self.scan_thread.deleteLater)
            logger.debug("All signals connected")
            
            # Connect scanner signals
            logger.debug("Connecting scanner signals...")
            if hasattr(self, 'scan_progress'):
                logger.debug("Connecting progress signal")
                self._scanner.progress_callback = self.scan_progress.emit
            if hasattr(self, 'scan_status'):
                logger.debug("Connecting status signal")
                self._scanner.status_callback = self.scan_status.emit
            if hasattr(self, 'scan_finished'):
                logger.debug("Connecting finished signal")
                self.scan_finished.connect(self._on_scan_finished)
                
            logger.info("PDF scanner initialized successfully")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import required module: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Initialization Error"),
                self.tr("Failed to import required modules. Please make sure all dependencies are installed.\n\nError: {}").format(str(e))
            )
        except Exception as e:
            logger.error(f"Error initializing scanner: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                self.tr("Initialization Error"),
                self.tr("Failed to initialize PDF scanner. Please check the logs for details.\n\nError: {}").format(str(e))
            )
        
        logger.error("Failed to initialize scanner. The application may not function correctly.")
        self._scanner = None
        return False
    
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
        try:
            # Update status bar and show progress bar
            self.status_bar.showMessage(self.tr("Scanning folder: %s") % folder_path)
            
            # Initialize scanner if needed
            if not hasattr(self, '_scanner') or self._scanner is None:
                self._init_scanner()
            
            # Reset UI state
            if hasattr(self, 'main_ui') and hasattr(self.main_ui, 'file_list'):
                self.main_ui.file_list.clear()
                
            # Show and reset progress bar
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                self.progress_bar.setMinimum(0)
                self.progress_bar.setMaximum(100)
                self.progress_bar.setFormat("%p% - %v/%m")
            
            # Start scan in a separate thread
            self.scan_thread = QThread()
            self.scan_worker = lambda: self._scan_worker(folder_path)
            self.scan_thread.started.connect(self.scan_worker)
            
            # Connect signals
            if hasattr(self, 'scan_status'):
                self.scan_status.connect(self._update_scan_status)
            if hasattr(self, 'scan_finished'):
                self.scan_finished.connect(self._on_scan_finished)
            
            # Start the thread
            self.scan_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}", exc_info=True)
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
