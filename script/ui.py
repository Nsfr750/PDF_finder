"""
UI components for PDF Duplicate Finder.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QLabel, QFrame, QStatusBar, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize

# Import language manager
from script.lang_mgr import LanguageManager

class MainUI(QWidget):
    """Main UI components for the application."""
    
    def __init__(self, parent=None):
        """Initialize the UI components.
        
        Args:
            parent: Parent widget.
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
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create main content area with vertical splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top panel - Main content (horizontal split)
        self.horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - File list
        self.file_list = QListWidget()
        self.file_list.setMinimumWidth(300)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # Right panel - Preview
        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_widget.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_widget.setText(self.tr("ui.preview_placeholder", "Preview will be shown here"))
        
        # Add widgets to horizontal splitter
        self.horizontal_splitter.addWidget(self.file_list)
        self.horizontal_splitter.addWidget(self.preview_widget)
        self.horizontal_splitter.setSizes([400, 700])
        
        # Bottom panel - Duplicates tree
        self.duplicates_tree = QTreeWidget()
        self.duplicates_tree.setObjectName("duplicatesTree")
        self.duplicates_tree.setHeaderLabels([
            self.tr("File Path"),
            self.tr("Size"),
            self.tr("Modified"),
            self.tr("Similarity")
        ])
        self.duplicates_tree.setAlternatingRowColors(True)
        self.duplicates_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.duplicates_tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.duplicates_tree.setMinimumHeight(200)
        
        # Configure header
        header = self.duplicates_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Add widgets to main vertical splitter
        self.splitter.addWidget(self.horizontal_splitter)
        self.splitter.addWidget(self.duplicates_tree)
        
        # Set initial sizes (2/3 for top, 1/3 for bottom)
        total_height = 800  # Default height, will be adjusted by window
        self.splitter.setSizes([int(total_height * 0.67), int(total_height * 0.33)])
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter)
        
        # Create status bar
        self.status_bar = QStatusBar()
        
        # Add a permanent widget for backend status
        self.backend_status_label = QLabel("")
        self.backend_status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.backend_status_label.setStyleSheet("color: #666666; font-style: italic; padding: 0 8px;")
        self.status_bar.addPermanentWidget(self.backend_status_label)
        
        # Show initial status
        self.status_bar.showMessage(self.tr("ui.status_ready", "Ready"))
    
    def update_preview(self, file_path):
        """Update the preview with the selected file.
        
        Args:
            file_path: Path to the file to preview.
        """
        if not file_path or not hasattr(self, 'preview_widget'):
            return
            
        # Update preview with localized text
        self.preview_widget.setText(
            self.tr("ui.preview_of", "Preview of: {file_path}")
            .format(file_path=file_path)
        )
    
    def clear_preview(self):
        """Clear the preview area."""
        if hasattr(self, 'preview_widget'):
            self.preview_widget.setText(
                self.tr("ui.preview_placeholder", "Preview will be shown here")
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
