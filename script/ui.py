"""
UI components for PDF Duplicate Finder.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QLabel, QFrame, QStatusBar, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QSizePolicy, QMenuBar, QToolBar,
    QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

# Import language manager
from script.lang_mgr import LanguageManager

# Import preview widget
from script.preview_widget import PDFPreviewWidget as PreviewWidget

class MainUI(QWidget):
    """Main UI components for the application."""
    
    def __init__(self, parent=None):
        """Initialize the UI components.
        
        Args:
            parent: Parent widget (main window).
        """
        super().__init__(parent)
        # Initialize language manager
        self.language_manager = LanguageManager()
        self.tr = self.language_manager.tr
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.setSpacing(4)
        
        # Create main horizontal splitter for file list and preview
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - File list with label (30% width)
        file_list_container = QWidget()
        file_list_layout = QVBoxLayout(file_list_container)
        file_list_layout.setContentsMargins(0, 0, 4, 0)
        file_list_layout.setSpacing(4)
        
        file_list_label = QLabel(self.tr("Files"))
        file_list_label.setStyleSheet("font-weight: bold; padding: 4px;")
        file_list_layout.addWidget(file_list_label)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        file_list_layout.addWidget(self.file_list)
        
        # Right panel - Preview with label (70% width)
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(4, 0, 0, 0)
        preview_layout.setSpacing(4)
        
        preview_label = QLabel(self.tr("Preview"))
        preview_label.setStyleSheet("font-weight: bold; padding: 4px;")
        preview_layout.addWidget(preview_label)
        
        self.preview_widget = PreviewWidget()
        preview_layout.addWidget(self.preview_widget)
        
        # Add file list and preview to main splitter
        main_splitter.addWidget(file_list_container)
        main_splitter.addWidget(preview_container)
        
        # Set stretch factors (30% for file list, 70% for preview)
        main_splitter.setStretchFactor(0, 30)
        main_splitter.setStretchFactor(1, 70)
        
        # Add splitter to main layout
        self.main_layout.addWidget(main_splitter, 1)  # Takes all available space
        
        # Initialize the preview widget with placeholder
        self.preview_widget.set_placeholder(self.tr("No preview available"))
    
    def on_file_double_clicked(self, item):
        """Handle double-click on a file in the file list."""
        file_path = item.text()
        if file_path and os.path.exists(file_path):
            self.preview_widget.load_pdf(file_path)
    
    def on_duplicate_double_clicked(self, item, column):
        """Handle double-click on a duplicate file in the tree."""
        if item.parent():  # This is a file item (not a group header)
            file_path = item.text(0)  # Get the file path from the first column
            if file_path and os.path.exists(file_path):
                self.preview_widget.load_pdf(file_path)
    
    def update_preview(self, file_path):
        """Update the preview with the selected file.
        
        Args:
            file_path: Path to the file to preview.
        """
        if not file_path or not hasattr(self, 'preview_widget'):
            return
        
        # Load the PDF in the preview widget
        self.preview_widget.load_pdf(file_path)
    
    def clear_preview(self):
        """Clear the preview area."""
        if hasattr(self, 'preview_widget'):
            self.preview_widget.set_placeholder(
                self.tr("preview.no_preview", "No preview available")
            )
    
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
        if not hasattr(self, 'duplicates_tree'):
            return
            
        self.duplicates_tree.clear()
        
        for group_idx, group in enumerate(duplicates, 1):
            # Skip if group is not iterable
            if not hasattr(group, '__iter__') or isinstance(group, str):
                logger.warning(f"Skipping invalid group {group_idx}: not iterable or is a string")
                continue
                
            # Create a group item
            group_item = QTreeWidgetItem([
                self.tr("Group {}").format(group_idx),
                "", "", ""
            ])
            group_item.setExpanded(True)
            
            # Add files to the group
            for file_info in group:
                if isinstance(file_info, str):
                    # If file_info is a string, treat it as the path
                    file_item = QTreeWidgetItem([file_info, "", "", ""])
                elif isinstance(file_info, dict):
                    # If file_info is a dictionary, extract the values
                    file_item = QTreeWidgetItem([
                        str(file_info.get('path', '')),
                        self._format_file_size(file_info.get('size', 0)),
                        self._format_timestamp(file_info.get('modified', 0)),
                        f"{file_info.get('similarity', 0) * 100:.1f}%" if 'similarity' in file_info else ""
                    ])
                else:
                    # Skip invalid file info
                    logger.warning(f"Skipping invalid file info: {file_info}")
                    continue
                    
                group_item.addChild(file_item)
                
            self.duplicates_tree.addTopLevelItem(group_item)
    
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
