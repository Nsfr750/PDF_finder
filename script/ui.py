"""
UI components for PDF Duplicate Finder.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QLabel, QFrame, QStatusBar, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QSizePolicy, QMenuBar, QToolBar,
    QApplication, QTabWidget, QStackedWidget, QMenu, QPushButton, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

# Import language manager
from script.lang_mgr import LanguageManager

class MainUI(QWidget):
    """Main UI components for the application."""
    
    def __init__(self, parent=None, language_manager=None):
        """Initialize the UI components.
        
        Args:
            parent: Parent widget (main window).
            language_manager: Shared LanguageManager instance for translations.
        """
        super().__init__(parent)
        # Use shared language manager or create default one
        self.language_manager = language_manager or LanguageManager()
        self.tr = self.language_manager.tr
        
        # Connect to language change signal
        if hasattr(self.language_manager, 'language_changed'):
            self.language_manager.language_changed.connect(self.on_language_changed)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.setSpacing(4)
        
        # Create tab widget for file list and duplicates
        self.tab_widget = QTabWidget()
        
        # Tab 1: File List and Preview
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        tab1_layout.setContentsMargins(0, 0, 0, 0)
        tab1_layout.setSpacing(4)
        
        # Left panel - File list (70% width)
        file_list_container = QWidget()
        file_list_layout = QVBoxLayout(file_list_container)
        file_list_layout.setContentsMargins(0, 0, 4, 0)
        file_list_layout.setSpacing(4)
        
        file_list_label = QLabel(self.tr("Files"))
        file_list_label.setStyleSheet("font-weight: bold; padding: 4px;")
        file_list_layout.addWidget(file_list_label)
        
        # Create file list with extended selection mode
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # Enable multi-selection with Shift/Ctrl
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        
        # Enable keyboard navigation
        self.file_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.file_list.setDragEnabled(True)
        self.file_list.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.file_list.setSelectionBehavior(QListWidget.SelectionBehavior.SelectItems)
        
        # Add select/deselect all context menu
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        
        file_list_layout.addWidget(self.file_list)
        
        # Right panel - Recent Files (30% width)
        recent_files_container = QWidget()
        recent_files_layout = QVBoxLayout(recent_files_container)
        recent_files_layout.setContentsMargins(4, 0, 0, 0)
        recent_files_layout.setSpacing(4)
        
        # Recent files label
        recent_label = QLabel(self.tr("Recent Files"))
        recent_label.setStyleSheet("font-weight: bold; padding: 4px;")
        recent_files_layout.addWidget(recent_label)
        
        # Recent files list
        self.recent_files_list = QListWidget()
        self.recent_files_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.recent_files_list.itemDoubleClicked.connect(self.on_recent_file_double_clicked)
        self.recent_files_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.recent_files_list.customContextMenuRequested.connect(self.show_recent_files_context_menu)
        recent_files_layout.addWidget(self.recent_files_list)
        
        # Add a clear button
        clear_button = QPushButton(self.tr("Clear Recent Files"))
        clear_button.clicked.connect(self.clear_recent_files)
        recent_files_layout.addWidget(clear_button)

        # Add file list and recent files to tab1
        tab1_layout.addWidget(file_list_container, 70)  # 70% width
        tab1_layout.addWidget(recent_files_container, 30)  # 30% width
        
        # Tab 2: Duplicates Tree
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.setContentsMargins(0, 0, 0, 0)
        tab2_layout.setSpacing(4)
        
        # Duplicates header with buttons
        duplicates_header = QWidget()
        duplicates_header_layout = QHBoxLayout(duplicates_header)
        duplicates_header_layout.setContentsMargins(0, 0, 0, 0)
        
        duplicates_label = QLabel(self.tr("Duplicate Files"))
        duplicates_label.setStyleSheet("font-weight: bold; padding: 4px;")
        
        # Add expand/collapse buttons
        btn_expand = QPushButton(self.tr("Expand All"))
        btn_expand.clicked.connect(lambda: self.duplicates_tree.expandAll())
        btn_expand.setMaximumWidth(100)
        
        btn_collapse = QPushButton(self.tr("Collapse All"))
        btn_collapse.clicked.connect(lambda: self.duplicates_tree.collapseAll())
        btn_collapse.setMaximumWidth(100)
        
        # Add stretch to push buttons to the right
        duplicates_header_layout.addWidget(duplicates_label)
        duplicates_header_layout.addStretch()
        duplicates_header_layout.addWidget(btn_expand)
        duplicates_header_layout.addWidget(btn_collapse)
        
        tab2_layout.addWidget(duplicates_header)
        
        # Create the tree widget for duplicates
        self.duplicates_tree = QTreeWidget()
        self.duplicates_tree.setHeaderLabels([
            self.tr("File"), 
            self.tr("Size"), 
            self.tr("Modified"), 
            self.tr("Similarity")
        ])
        self.duplicates_tree.setColumnCount(4)
        self.duplicates_tree.setSortingEnabled(True)
        self.duplicates_tree.setAlternatingRowColors(True)
        self.duplicates_tree.setAnimated(True)
        self.duplicates_tree.setIndentation(20)
        self.duplicates_tree.setWordWrap(True)
        self.duplicates_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.duplicates_tree.itemDoubleClicked.connect(self.on_duplicate_double_clicked)
        
        # Set header properties
        header = self.duplicates_tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # File path
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Modified
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Similarity
        
        tab2_layout.addWidget(self.duplicates_tree)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(tab1, self.tr("Files"))
        self.tab_widget.addTab(tab2, self.tr("Duplicates"))
        
        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)
    
    def show_context_menu(self, position):
        """Show context menu for file list with select/deselect/delete options."""
        menu = QMenu()
        
        # Add select/deselect actions
        select_all_action = QAction(self.tr("Select All"), self)
        select_all_action.triggered.connect(self.select_all_files)
        menu.addAction(select_all_action)
        
        deselect_all_action = QAction(self.tr("Deselect All"), self)
        deselect_all_action.triggered.connect(self.deselect_all_files)
        menu.addAction(deselect_all_action)
        
        # Add separator
        menu.addSeparator()
        
        # Add delete action if items are selected
        if self.file_list.selectedItems():
            delete_action = QAction(self.tr("Delete Selected"), self)
            delete_action.triggered.connect(self._on_delete_selected)
            delete_action.setIcon(QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_TrashIcon
            ))
            menu.addAction(delete_action)
        
        menu.exec(self.file_list.viewport().mapToGlobal(position))
    
    def on_recent_file_double_clicked(self, item):
        """Handle double-click on a recent file."""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            # Move the clicked item to the top
            self.add_to_recent_files(file_path)
            # Open the file
            if hasattr(self.parent(), 'open_file'):
                self.parent().open_file(file_path)
    
    def show_recent_files_context_menu(self, position):
        """Show context menu for recent files list."""
        item = self.recent_files_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        # Open file action
        open_action = QAction(self.tr("Open"), self)
        open_action.triggered.connect(lambda: self.on_recent_file_double_clicked(item))
        menu.addAction(open_action)
        
        # Remove from list action
        remove_action = QAction(self.tr("Remove from list"), self)
        remove_action.triggered.connect(lambda: self.recent_files_list.takeItem(self.recent_files_list.row(item)))
        menu.addAction(remove_action)
        
        # Show in file explorer
        show_in_explorer = QAction(self.tr("Show in Explorer"), self)
        show_in_explorer.triggered.connect(lambda: self.show_in_explorer(item.data(Qt.ItemDataRole.UserRole)))
        menu.addAction(show_in_explorer)
        
        menu.exec(self.recent_files_list.viewport().mapToGlobal(position))
    
    def show_in_explorer(self, file_path):
        """Show the file in system file explorer."""
        if os.path.exists(file_path):
            import subprocess
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(os.path.dirname(file_path))
                else:  # macOS and Linux
                    subprocess.Popen(['xdg-open', os.path.dirname(file_path)])
            except Exception as e:
                print(f"Error opening file explorer: {e}")
    
    def clear_recent_files(self):
        """Clear the recent files list."""
        self.recent_files_list.clear()
    
    def _on_delete_selected(self):
        """Handle delete selected action from context menu."""
        if hasattr(self.parent(), 'on_delete_selected'):
            self.parent().on_delete_selected()
    
    def select_all_files(self):
        """Select all files in the file list."""
        self.file_list.selectAll()
    
    def deselect_all_files(self):
        """Deselect all files in the file list."""
        self.file_list.clearSelection()
    
    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list."""
        if not file_path or not os.path.exists(file_path):
            return
            
        # Remove if already exists
        for i in range(self.recent_files_list.count()):
            if self.recent_files_list.item(i).data(Qt.ItemDataRole.UserRole) == file_path:
                self.recent_files_list.takeItem(i)
                break
                
        # Add to top of the list
        item = QListWidgetItem(os.path.basename(file_path))
        item.setData(Qt.ItemDataRole.ToolTipRole, file_path)  # Full path in tooltip
        item.setData(Qt.ItemDataRole.UserRole, file_path)  # Store full path in user data
        self.recent_files_list.insertItem(0, item)
        
        # Limit to 10 recent files
        if self.recent_files_list.count() > 10:
            self.recent_files_list.takeItem(self.recent_files_list.count() - 1)
    
    def on_file_double_clicked(self, item):
        """Handle double-click on a file in the file list."""
        file_path = item.text()
        if file_path and os.path.exists(file_path):
            self.add_to_recent_files(file_path)
            try:
                # First try to open with the PDF viewer
                from script.PDF_viewer import PDFViewer, show_pdf_viewer
                
                # Usa la funzione show_pdf_viewer invece di creare direttamente l'istanza
                show_pdf_viewer(file_path=file_path, parent=self, language_manager=self.language_manager)
            except Exception as e:
                # Fall back to preview widget if viewer fails
                import logging
                logging.error(f"Failed to open PDF viewer: {e}", exc_info=True)
                if hasattr(self, 'preview_widget'):
                    self.preview_widget.load_pdf(file_path)
    
    def on_duplicate_double_clicked(self, item, column):
        """Handle double-click on a duplicate file in the tree."""
        if item.parent():  # This is a file item (not a group header)
            file_path = item.text(0)  # Get the file path from the first column
            if file_path and os.path.exists(file_path):
                try:
                    # Use the show_pdf_viewer function instead of creating the instance directly
                    from script.PDF_viewer import show_pdf_viewer
                    show_pdf_viewer(file_path=file_path, parent=self, language_manager=self.language_manager)
                except Exception as e:
                    # Fall back to preview widget if viewer fails
                    import logging
                    logging.error(f"Failed to open PDF viewer: {e}", exc_info=True)
                    if hasattr(self, 'preview_widget'):
                        self.preview_widget.load_pdf(file_path)
    
    def update_status(self, message):
        """Update the status bar with a message.
        
        Args:
            message: The message to display in the status bar.
        """
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message)
    
    def update_duplicates_tree(self, duplicates):
        """Update the duplicates tree with the provided duplicate groups.
        
        Args:
            duplicates: List of duplicate file groups, where each group is a list of file info dicts or strings
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if not hasattr(self, 'duplicates_tree'):
                logger.error("duplicates_tree widget not found in UI")
                return
                
            logger.info(f"Updating duplicates tree with {len(duplicates)} groups")
            self.duplicates_tree.clear()
            self.file_list.clear()  # Clear the file list in tab1
            
            if not duplicates:
                no_duplicates = QTreeWidgetItem([self.tr("No duplicate files found."), "", "", ""])
                self.duplicates_tree.addTopLevelItem(no_duplicates)
                self.file_list.addItem(self.tr("No duplicate files found."))
                return
            
            # Set to store all unique file paths to avoid duplicates in the file list
            all_files = set()
            
            for group_idx, group in enumerate(duplicates, 1):
                if not group:
                    continue
                
                # Create a group header
                group_item = QTreeWidgetItem([f"Group {group_idx} - {len(group)} files"])
                group_item.setData(0, Qt.ItemDataRole.UserRole, group_idx)
                group_item.setExpanded(True)
                
                valid_files = 0
                
                # Add files to the group
                for file_info in group:
                    try:
                        if isinstance(file_info, str):
                            # If file_info is a string, treat it as the path
                            file_path = file_info
                            file_item = QTreeWidgetItem([file_path, "", "", ""])
                            valid_files += 1
                        elif isinstance(file_info, dict):
                            # If file_info is a dictionary, extract the values
                            file_path = str(file_info.get('path', ''))
                            file_item = QTreeWidgetItem([
                                file_path,
                                self._format_file_size(file_info.get('size', 0)),
                                self._format_timestamp(file_info.get('modified', 0)),
                                f"{file_info.get('similarity', 0) * 100:.1f}%" if 'similarity' in file_info else ""
                            ])
                            valid_files += 1
                        else:
                            logger.warning(f"Skipping invalid file info type: {type(file_info).__name__}")
                            continue
                        
                        # Add to the tree
                        group_item.addChild(file_item)
                        
                        # Add to the set of all files (if not already present)
                        if file_path and file_path not in all_files:
                            all_files.add(file_path)
                            
                    except Exception as e:
                        logger.error(f"Error processing file info: {e}", exc_info=True)
                        continue
                
                # Only add the group if it contains valid files
                if valid_files > 0:
                    self.duplicates_tree.addTopLevelItem(group_item)
                    logger.debug(f"Added group {group_idx} with {valid_files} files")
            
            # Add all unique files to the file list in tab1
            self.file_list.clear()
            for file_path in sorted(all_files):
                item = QListWidgetItem(file_path)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.file_list.addItem(item)
                
            # If no files were added, show a message
            if self.file_list.count() == 0:
                self.file_list.addItem(self.tr("No files to display"))
                
            # Expand all groups by default
            self.duplicates_tree.expandAll()
            
            # Resize columns to fit content
            for i in range(self.duplicates_tree.columnCount()):
                self.duplicates_tree.resizeColumnToContents(i)
                
            logger.info(f"Duplicates tree updated with {self.duplicates_tree.topLevelItemCount()} groups and {len(all_files)} unique files in the list")
            
            # Switch to the duplicates tab to show results
            if hasattr(self, 'tab_widget') and self.duplicates_tree.topLevelItemCount() > 0:
                self.tab_widget.setCurrentIndex(1)  # Switch to Duplicates tab
            
        except Exception as e:
            logger.error(f"Error updating duplicates tree: {e}", exc_info=True)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(self.tr("Error updating file list"), 5000)
    
    def _format_file_size(self, size_bytes):
        """Format file size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0 or unit == 'GB':
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} B"
    
    def _format_timestamp(self, timestamp):
        """Format timestamp to human-readable date."""
        if not timestamp:
            return ""
        from datetime import datetime
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError, OverflowError):
            return ""
    
    def on_language_changed(self):
        """Update UI translations when language changes."""
        # Update tab titles
        self.tab_widget.setTabText(0, self.tr("Files"))
        self.tab_widget.setTabText(1, self.tr("Duplicates"))
        
        # Update labels and buttons
        for widget in self.findChildren((QLabel, QPushButton)):
            if hasattr(widget, 'text'):
                widget.setText(self.tr(widget.text()))
        
        # Update file list and recent files list
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setText(self.tr(item.text()))
        
        for i in range(self.recent_files_list.count()):
            item = self.recent_files_list.item(i)
            item.setText(self.tr(item.text()))
        
        # Update duplicates tree
        for i in range(self.duplicates_tree.topLevelItemCount()):
            item = self.duplicates_tree.topLevelItem(i)
            item.setText(0, self.tr(item.text(0)))
            
            for j in range(item.childCount()):
                child_item = item.child(j)
                child_item.setText(0, self.tr(child_item.text(0)))
