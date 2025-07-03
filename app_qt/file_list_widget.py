"""File list widget for displaying duplicate PDF groups."""
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAbstractItemView,
    QStyledItemDelegate, QStyleOptionViewItem, QApplication, QStyle
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QModelIndex, QRect
from PyQt6.QtGui import QColor, QBrush, QFont, QIcon, QPixmap, QPainter

class FileListWidget(QTreeWidget):
    """Widget for displaying duplicate PDF groups in a tree structure."""
    
    # Signals
    group_selected = pyqtSignal(list)  # List of PDFDocument objects
    open_file = pyqtSignal(str)        # File path to open
    open_containing_folder = pyqtSignal(str)  # File path to show in explorer
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHeaderLabels(["Name", "Size", "Pages"])
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setIndentation(15)
        self.setAnimated(True)
        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        
        # Set header properties
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Connect signals
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Initialize data
        self.duplicate_groups = []
        self.current_group_index = -1
    
    def set_duplicate_groups(self, groups):
        """Set the duplicate groups to display."""
        self.clear()
        self.duplicate_groups = groups or []
        self.current_group_index = -1
        
        for i, group in enumerate(self.duplicate_groups):
            if not group:
                continue
                
            # Create group item
            group_item = QTreeWidgetItem()
            group_item.setData(0, Qt.ItemDataRole.UserRole, i)
            
            # Calculate group info
            group_size = group[0].file_size if group else 0
            total_size = sum(doc.file_size for doc in group[1:]) if len(group) > 1 else 0
            space_savings = group_size * (len(group) - 1) if len(group) > 1 else 0
            
            # Set group item text
            group_item.setText(0, f"Duplicate Group {i + 1} ({len(group)} files)")
            group_item.setText(1, self.format_file_size(group_size))
            group_item.setText(2, f"{group[0].page_count if hasattr(group[0], 'page_count') else '?'} pages")
            
            # Add tooltip with more info
            tooltip = f"<b>Group {i + 1}: {len(group)} duplicate files</b>"
            tooltip += f"<br>Size: {self.format_file_size(group_size)}"
            if len(group) > 1:
                tooltip += f"<br>Space savings: {self.format_file_size(space_savings)}"
            group_item.setToolTip(0, tooltip)
            
            # Set group item appearance
            font = group_item.font(0)
            font.setBold(True)
            group_item.setFont(0, font)
            group_item.setBackground(0, QColor(240, 240, 240))
            group_item.setBackground(1, QColor(240, 240, 240))
            group_item.setBackground(2, QColor(240, 240, 240))
            
            # Add group item to tree
            self.addTopLevelItem(group_item)
            
            # Add document items
            for doc in group:
                doc_item = QTreeWidgetItem()
                doc_item.setData(0, Qt.ItemDataRole.UserRole, doc.file_path)
                
                # Set document item text
                doc_item.setText(0, doc.file_name)
                doc_item.setText(1, self.format_file_size(doc.file_size))
                doc_item.setText(2, f"{doc.page_count if hasattr(doc, 'page_count') else '?'} pages")
                
                # Add tooltip with file path
                doc_item.setToolTip(0, doc.file_path)
                
                # Add to group
                group_item.addChild(doc_item)
            
            # Expand the group by default
            group_item.setExpanded(True)
        
        # Select the first group if available
        if self.topLevelItemCount() > 0:
            self.setCurrentItem(self.topLevelItem(0))
    
    def on_selection_changed(self):
        """Handle selection changes in the tree."""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        parent = item.parent()
        
        if parent is None:  # Group item selected
            group_index = item.data(0, Qt.ItemDataRole.UserRole)
            if 0 <= group_index < len(self.duplicate_groups):
                self.current_group_index = group_index
                self.group_selected.emit(self.duplicate_groups[group_index])
        else:  # Document item selected
            group_index = parent.data(0, Qt.ItemDataRole.UserRole)
            if 0 <= group_index < len(self.duplicate_groups):
                self.current_group_index = group_index
                self.group_selected.emit(self.duplicate_groups[group_index])
    
    def on_item_double_clicked(self, item, column):
        """Handle double-click on an item."""
        if item.parent() is not None:  # Document item
            file_path = item.data(0, Qt.ItemDataRole.UserRole)
            if file_path:
                self.open_file.emit(file_path)
    
    def show_context_menu(self, position):
        """Show context menu for the selected item."""
        item = self.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        if item.parent() is None:  # Group item
            expand_all = menu.addAction("Expand All")
            collapse_all = menu.addAction("Collapse All")
            menu.addSeparator()
            open_all = menu.addAction("Open All in Group")
            show_all = menu.addAction("Show All in Explorer")
            
            action = menu.exec(self.viewport().mapToGlobal(position))
            
            if action == expand_all:
                self.expandAll()
            elif action == collapse_all:
                self.collapseAll()
            elif action == open_all:
                self.open_all_in_group(item)
            elif action == show_all:
                self.show_all_in_explorer(item)
                
        else:  # Document item
            open_file = menu.addAction("Open File")
            show_in_explorer = menu.addAction("Show in Explorer")
            
            action = menu.exec(self.viewport().mapToGlobal(position))
            
            if action == open_file:
                file_path = item.data(0, Qt.ItemDataRole.UserRole)
                if file_path:
                    self.open_file.emit(file_path)
            elif action == show_in_explorer:
                file_path = item.data(0, Qt.ItemDataRole.UserRole)
                if file_path:
                    self.open_containing_folder.emit(file_path)
    
    def open_all_in_group(self, group_item):
        """Open all files in the selected group."""
        for i in range(group_item.childCount()):
            child = group_item.child(i)
            file_path = child.data(0, Qt.ItemDataRole.UserRole)
            if file_path:
                self.open_file.emit(file_path)
    
    def show_all_in_explorer(self, group_item):
        """Show all files in the selected group in file explorer."""
        paths = []
        for i in range(group_item.childCount()):
            child = group_item.child(i)
            file_path = child.data(0, Qt.ItemDataRole.UserRole)
            if file_path:
                paths.append(file_path)
        
        if paths:
            self.open_containing_folder.emit(paths[0])
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in a human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

class FileItemDelegate(QStyledItemDelegate):
    """Custom delegate for styling file items in the tree."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_color = QColor(225, 240, 255)
    
    def paint(self, painter, option, index):
        """Custom paint method for items."""
        # Save the painter state
        painter.save()
        
        # Set up the style options
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        
        # Get the item
        model = index.model()
        item = model.itemFromIndex(index)
        
        # Highlight the first item in each group (the one to keep)
        if item and item.parent() is not None and item.parent().indexOfChild(item) == 0:
            # Draw highlight background
            highlight_rect = option.rect
            painter.fillRect(highlight_rect, self.highlight_color)
            
            # Draw border
            pen = QPen(QColor(180, 210, 255), 1)
            painter.setPen(pen)
            painter.drawRect(highlight_rect.adjusted(0, 0, -1, -1))
        
        # Draw the item text
        text = options.text
        if text:
            # Calculate text rectangle
            text_rect = options.rect.adjusted(2, 0, -2, 0)
            
            # Draw text with elision if needed
            metrics = QApplication.fontMetrics()
            elided_text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, text_rect.width())
            
            # Set text color
            painter.setPen(Qt.GlobalColor.black if option.state & QStyle.StateFlag.State_Enabled else Qt.GlobalColor.gray)
            
            # Draw text
            painter.drawText(text_rect, int(option.displayAlignment()), elided_text)
        
        # Restore the painter state
        painter.restore()
    
    def sizeHint(self, option, index):
        """Return the size hint for the item."""
        size = super().sizeHint(option, index)
        if size.height() < 24:  # Minimum height
            size.setHeight(24)
        return size
