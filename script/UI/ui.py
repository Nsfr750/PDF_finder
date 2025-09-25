"""
UI components for PDF Duplicate Finder.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QLabel, QFrame, QStatusBar, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QSizePolicy, QMenuBar, QToolBar,
    QApplication, QTabWidget, QStackedWidget, QMenu, QPushButton, QListWidgetItem,
    QStyle
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

# Import language manager
from script.lang.lang_manager import SimpleLanguageManager

class MainUI(QWidget):
    """Main UI components for the application."""
    
    # Signal emitted when delete selected is requested
    delete_selected = pyqtSignal()
    
    def __init__(self, parent=None, language_manager=None):
        """Initialize the UI components.
        
        Args:
            parent: Parent widget (main window).
            language_manager: Shared SimpleLanguageManager instance for translations.
        """
        super().__init__(parent)
        # Use shared language manager or create default one
        self.language_manager = language_manager or SimpleLanguageManager()
        self.tr = self.language_manager.tr
        
        # Store translation keys for UI elements
        self.translation_keys = {}
        
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
        self.translation_keys['file_list_label'] = "Files"
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
        self.translation_keys['recent_label'] = "Recent Files"
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
        self.translation_keys['clear_button'] = "Clear Recent Files"
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
        self.translation_keys['duplicates_label'] = "Duplicate Files"
        
        # Add expand/collapse buttons
        btn_expand = QPushButton(self.tr("Expand All"))
        btn_expand.clicked.connect(lambda: self.duplicates_tree.expandAll())
        btn_expand.setMaximumWidth(100)
        self.translation_keys['btn_expand'] = "Expand All"
        
        btn_collapse = QPushButton(self.tr("Collapse All"))
        btn_collapse.clicked.connect(lambda: self.duplicates_tree.collapseAll())
        btn_collapse.setMaximumWidth(100)
        self.translation_keys['btn_collapse'] = "Collapse All"
        
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
        self.duplicates_tree.customContextMenuRequested.connect(self.show_context_menu)
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
        self.translation_keys['tab_widget_files'] = "Files"
        self.tab_widget.addTab(tab2, self.tr("Duplicates"))
        self.translation_keys['tab_widget_duplicates'] = "Duplicates"
        
        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)
    
    def show_context_menu(self, position):
        """Show context menu for file list or duplicates tree with select/deselect/delete options."""
        import logging
        logger = logging.getLogger(__name__)
        
        menu = QMenu()
        
        # Determine which widget called this context menu
        sender = self.sender()
        if sender == self.file_list:
            widget = self.file_list
            logger.info("Context menu for file_list")
        elif sender == self.duplicates_tree:
            widget = self.duplicates_tree
            logger.info("Context menu for duplicates_tree")
        else:
            widget = self.file_list  # Default fallback
            logger.warning(f"Unknown sender for context menu: {sender}")
        
        # Check if items are selected in the current widget
        selected_items = widget.selectedItems()
        logger.info(f"Selected items in {widget.objectName()}: {len(selected_items)}")
        
        # Add select/deselect actions
        select_all_action = QAction(self.tr("Select All"), self)
        select_all_action.triggered.connect(self.select_all_files)
        self.translation_keys['select_all_action'] = "Select All"
        menu.addAction(select_all_action)
        
        deselect_all_action = QAction(self.tr("Deselect All"), self)
        deselect_all_action.triggered.connect(self.deselect_all_files)
        self.translation_keys['deselect_all_action'] = "Deselect All"
        menu.addAction(deselect_all_action)
        
        # Add separator
        menu.addSeparator()
        
        # Add delete action if items are selected
        if selected_items:
            delete_action = QAction(self.tr("Delete Selected"), self)
            delete_action.triggered.connect(self.delete_selected.emit)
            delete_action.setIcon(QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_TrashIcon
            ))
            self.translation_keys['delete_action'] = "Delete Selected"
            menu.addAction(delete_action)
            logger.info("Delete action added to context menu")
        else:
            logger.info("No items selected, delete action not added")
        
        menu.exec(widget.viewport().mapToGlobal(position))
    
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
        self.translation_keys['open_action'] = "Open"
        menu.addAction(open_action)
        
        # Remove from list action
        remove_action = QAction(self.tr("Remove from list"), self)
        remove_action.triggered.connect(lambda: self.recent_files_list.takeItem(self.recent_files_list.row(item)))
        self.translation_keys['remove_action'] = "Remove from list"
        menu.addAction(remove_action)
        
        # Show in file explorer
        show_in_explorer = QAction(self.tr("Show in Explorer"), self)
        show_in_explorer.triggered.connect(lambda: self.show_in_explorer(item.data(Qt.ItemDataRole.UserRole)))
        self.translation_keys['show_in_explorer'] = "Show in Explorer"
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
        print(f"DEBUG: Context menu delete action triggered")
        print(f"DEBUG: Parent: {self.parent()}")
        if hasattr(self.parent(), 'on_delete_selected'):
            print(f"DEBUG: on_delete_selected method found on parent")
            self.parent().on_delete_selected()
        else:
            print(f"DEBUG: on_delete_selected method NOT found on parent")
            print(f"DEBUG: Parent attributes: {[attr for attr in dir(self.parent()) if 'delete' in attr.lower()]}")
    
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
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            self.add_to_recent_files(file_path)
            try:
                # First try to open with the PDF viewer
                from script.UI.PDF_viewer import PDFViewer, show_pdf_viewer
                
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
            file_path = item.data(0, Qt.ItemDataRole.UserRole)  # Get the file path from UserRole
            if file_path and os.path.exists(file_path):
                try:
                    # Use the show_pdf_viewer function instead of creating the instance directly
                    from script.UI.PDF_viewer import show_pdf_viewer
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
                # Add a message item to the file list
                no_files_item = QListWidgetItem(self.tr("No duplicate files found."))
                no_files_item.setData(Qt.ItemDataRole.ToolTipRole, self.tr("No duplicate files found."))
                self.file_list.addItem(no_files_item)
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
                            file_path = os.path.normpath(file_info)
                            file_item = QTreeWidgetItem([file_path, "", "", ""])
                            # Store file path in UserRole for delete function
                            file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                            valid_files += 1
                        elif isinstance(file_info, dict):
                            # If file_info is a dictionary, extract the values
                            file_path = os.path.normpath(str(file_info.get('path', '')))
                            file_item = QTreeWidgetItem([
                                file_path,
                                self._format_file_size(file_info.get('size', 0)),
                                self._format_timestamp(file_info.get('modified', 0)),
                                f"{file_info.get('similarity', 0) * 100:.1f}%" if 'similarity' in file_info else ""
                            ])
                            # Store file path in UserRole for delete function
                            file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                            valid_files += 1
                        else:
                            logger.warning(f"Unknown file_info type: {type(file_info)}")
                            continue
                        
                        # Add the file to the group
                        group_item.addChild(file_item)
                        
                        # Add to file list (avoid duplicates)
                        if file_path and file_path not in all_files:
                            all_files.add(file_path)
                            # Create QListWidgetItem with file path stored in UserRole
                            file_item = QListWidgetItem(os.path.basename(file_path))
                            file_item.setData(Qt.ItemDataRole.UserRole, file_path)
                            file_item.setData(Qt.ItemDataRole.ToolTipRole, file_path)
                            self.file_list.addItem(file_item)
                        
                    except Exception as e:
                        logger.error(f"Error processing file info: {e}", exc_info=True)
                        continue
                
                if valid_files > 0:
                    self.duplicates_tree.addTopLevelItem(group_item)
                else:
                    logger.warning(f"Group {group_idx} has no valid files")
            
            logger.info(f"Added {len(all_files)} unique files to file list")
            
        except Exception as e:
            logger.error(f"Error updating duplicates tree: {e}", exc_info=True)
            # Show error in UI
            error_item = QTreeWidgetItem([f"Error: {str(e)}", "", "", ""])
            self.duplicates_tree.addTopLevelItem(error_item)
    
    def remove_files_from_list(self, file_paths):
        """Remove files from the file list after deletion.
        
        Args:
            file_paths: List of file paths to remove
        """
        try:
            if not hasattr(self, 'file_list'):
                return
                
            # Create a set of file paths for faster lookup
            paths_to_remove = set(file_paths)
            
            # Iterate through all items and remove those that match
            items_to_remove = []
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                item_path = item.data(Qt.ItemDataRole.UserRole)
                if item_path in paths_to_remove:
                    items_to_remove.append(item)
            
            # Remove the items
            for item in items_to_remove:
                row = self.file_list.row(item)
                if row >= 0:
                    self.file_list.takeItem(row)
                    
            logger.info(f"Removed {len(items_to_remove)} files from file list")
            
        except Exception as e:
            logger.error(f"Error removing files from list: {e}", exc_info=True)
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _format_timestamp(self, timestamp):
        """Format timestamp in human readable format.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted timestamp string
        """
        if timestamp == 0:
            return ""
        
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(timestamp)
    
    def on_language_changed(self):
        """Handle language change event."""
        # Rebuild UI with new language
        self.rebuild_ui()
    
    def rebuild_ui(self):
        """Rebuild UI elements with current language."""
        # Update labels using stored translation keys
        if 'file_list_label' in self.translation_keys:
            file_list_label = self.findChild(QLabel, "file_list_label")
            if file_list_label:
                file_list_label.setText(self.tr(self.translation_keys['file_list_label']))
        
        # Update tab labels
        if hasattr(self, 'tab_widget') and self.tab_widget:
            self.tab_widget.setTabText(0, self.tr(self.translation_keys.get('tab_widget_files', 'Files')))
            self.tab_widget.setTabText(1, self.tr(self.translation_keys.get('tab_widget_duplicates', 'Duplicates')))
        
        # Update tree headers
        if hasattr(self, 'duplicates_tree') and self.duplicates_tree:
            self.duplicates_tree.setHeaderLabels([
                self.tr("File"), 
                self.tr("Size"), 
                self.tr("Modified"), 
                self.tr("Similarity")
            ])
        
        # Update button texts
        if hasattr(self, 'btn_expand') and self.btn_expand:
            self.btn_expand.setText(self.tr(self.translation_keys.get('btn_expand', 'Expand All')))
        
        if hasattr(self, 'btn_collapse') and self.btn_collapse:
            self.btn_collapse.setText(self.tr(self.translation_keys.get('btn_collapse', 'Collapse All')))
        
        if hasattr(self, 'clear_button') and self.clear_button:
            self.clear_button.setText(self.tr(self.translation_keys.get('clear_button', 'Clear Recent Files')))
