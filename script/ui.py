"""
UI components for PDF Duplicate Finder.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QLabel, QFrame, QStatusBar, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QSizePolicy, QMenuBar, QToolBar,
    QApplication, QTabWidget, QStackedWidget
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
        
        # Create tab widget for file list and duplicates
        self.tab_widget = QTabWidget()
        
        # Tab 1: File List and Preview
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        tab1_layout.setContentsMargins(0, 0, 0, 0)
        tab1_layout.setSpacing(4)
        
        # Left panel - File list (30% width)
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
        
        # Right panel - Preview (70% width)
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(4, 0, 0, 0)
        preview_layout.setSpacing(4)
        
        preview_label = QLabel(self.tr("Preview"))
        preview_label.setStyleSheet("font-weight: bold; padding: 4px;")
        preview_layout.addWidget(preview_label)
        
        self.preview_widget = PreviewWidget()
        preview_layout.addWidget(self.preview_widget)
        
        # Add file list and preview to tab1
        tab1_layout.addWidget(file_list_container, 70)  # 70% width
        tab1_layout.addWidget(preview_container, 30)    # 30% width
        
        # Tab 2: Duplicates Tree
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.setContentsMargins(0, 0, 0, 0)
        tab2_layout.setSpacing(4)
        
        # Duplicates tree widget
        duplicates_label = QLabel(self.tr("Duplicate Files"))
        duplicates_label.setStyleSheet("font-weight: bold; padding: 4px;")
        tab2_layout.addWidget(duplicates_label)
        
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
        
        # Initialize the preview widget with placeholder
        self.preview_widget.set_placeholder(self.tr("No preview available"))
    
    def on_file_double_clicked(self, item):
        """Handle double-click on a file in the file list."""
        file_path = item.text()
        if file_path and os.path.exists(file_path):
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
                self.file_list.addItem(file_path)
                
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
