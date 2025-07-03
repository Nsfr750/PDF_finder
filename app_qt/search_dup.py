"""
Module for handling duplicate file search functionality with model and view classes.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QSize
from PySide6.QtGui import QIcon, QPainter, QPalette, QColor
from PySide6.QtWidgets import (
    QTreeView, QStyledItemDelegate, QStyleOptionViewItem, QApplication, QStyle
)

class DuplicateFileItem:
    """Represents a duplicate file item in the model."""
    
    def __init__(self, file_path: str, size: int, modified: float, is_original: bool = False):
        self.file_path = file_path
        self.size = size
        self.modified = modified
        self.is_original = is_original
    
    def data(self, role: int = Qt.DisplayRole):
        """Return data for the specified role."""
        if role == Qt.DisplayRole:
            # Return just the file name for display
            return os.path.basename(self.file_path) if self.file_path else ""
        elif role == Qt.UserRole:
            return self
        elif role == Qt.DecorationRole:
            # Return a file icon or other decoration
            return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        elif role == Qt.ToolTipRole:
            # Show full path in tooltip
            if not self.file_path:
                return ""
            file_info = []
            file_info.append(f"File: {self.file_path}")
            file_info.append(f"Size: {self.size:,} bytes" if self.size is not None else "Size: Unknown")
            file_info.append(f"Modified: {self.modified}" if self.modified is not None else "")
            return "\n".join(filter(None, file_info))
        return None

class DuplicateGroup:
    """Represents a group of duplicate files."""
    
    def __init__(self, files: List[DuplicateFileItem]):
        self.files = files
        self.is_expanded = False
    
    def data(self, role: int = Qt.DisplayRole):
        """Return data for the specified role."""
        if role == Qt.DisplayRole:
            count = len(self.files)
            if count == 1:
                return "1 duplicate file"
            return f"{count} duplicate files"
        elif role == Qt.UserRole:
            return self
        elif role == Qt.DecorationRole:
            # Return a folder icon or other decoration
            return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        elif role == Qt.ToolTipRole:
            if not self.files:
                return "No duplicate files in this group"
            return f"Click to expand/collapse - {len(self.files)} duplicate files"
        return None

class DuplicateFilesModel(QAbstractItemModel):
    """Model for displaying duplicate files in a tree structure."""
    
    def __init__(self, duplicate_groups: List[List[Dict[str, Any]]] = None, parent=None):
        super().__init__(parent)
        self.duplicate_groups = []
        self.set_duplicate_groups(duplicate_groups or [])
    
    def set_duplicate_groups(self, duplicate_groups: List[List[Dict[str, Any]]]):
        """Set the duplicate groups for this model."""
        self.beginResetModel()
        self.duplicate_groups = []
        
        for group in duplicate_groups:
            if not group:
                continue
                
            # Convert dict items to DuplicateFileItem objects
            file_items = []
            for file_info in group:
                file_item = DuplicateFileItem(
                    file_path=file_info.get('path', ''),
                    size=file_info.get('size', 0),
                    modified=file_info.get('modified', 0),
                    is_original=file_info.get('is_original', False)
                )
                file_items.append(file_item)
            
            if file_items:
                self.duplicate_groups.append(DuplicateGroup(file_items))
        
        self.endResetModel()
    
    def index(self, row: int, column: int, parent=QModelIndex()):
        """Return the index of the item in the model specified by the given row, column and parent index."""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        if not parent.isValid():
            # Top-level item (group)
            if row < len(self.duplicate_groups):
                return self.createIndex(row, column, self.duplicate_groups[row])
        else:
            # Child item (file)
            group = parent.internalPointer()
            if isinstance(group, DuplicateGroup) and row < len(group.files):
                return self.createIndex(row, column, group.files[row])
        
        return QModelIndex()
    
    def parent(self, index: QModelIndex):
        """Return the parent of the model item with the given index."""
        if not index.isValid():
            return QModelIndex()
        
        item = index.internalPointer()
        
        # If the item is a file, return its parent group
        if isinstance(item, DuplicateFileItem):
            for i, group in enumerate(self.duplicate_groups):
                if item in group.files:
                    return self.createIndex(i, 0, group)
        
        return QModelIndex()
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows under the given parent."""
        if not parent.isValid():
            # Number of top-level items (groups)
            return len(self.duplicate_groups)
        
        item = parent.internalPointer()
        if isinstance(item, DuplicateGroup):
            # Number of files in the group
            return len(item.files)
        
        return 0
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns for the children of the given parent."""
        return 1  # Only one column for the file/group name
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """Return the data stored under the given role for the item referred to by the index."""
        if not index.isValid():
            return None
        
        item = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.DecorationRole or role == Qt.ToolTipRole or role == Qt.UserRole:
            return item.data(role)
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        """Return the data for the given role and section in the header with the specified orientation."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Duplicate Files"
        return None
    
    def flags(self, index: QModelIndex):
        """Return the item flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def mark_as_original(self, file_paths: List[str]):
        """Mark the specified files as originals."""
        for group in self.duplicate_groups:
            for file_item in group.files:
                file_item.is_original = file_item.file_path in file_paths
        
        # Notify views that the data has changed
        self.dataChanged.emit(QModelIndex(), QModelIndex())
    
    def remove_files(self, file_paths: List[str]):
        """Remove the specified files from the model."""
        paths_to_remove = set(file_paths)
        
        for group in self.duplicate_groups[:]:
            # Remove files from the group
            group.files = [f for f in group.files if f.file_path not in paths_to_remove]
            
            # Remove empty groups
            if len(group.files) < 2:
                self.duplicate_groups.remove(group)
        
        # Notify views that the model has been reset
        self.beginResetModel()
        self.endResetModel()

class DuplicateFilesView(QTreeView):
    """View for displaying duplicate files with custom rendering and interactions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setSelectionMode(QTreeView.ExtendedSelection)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setExpandsOnDoubleClick(True)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        
        # Enable custom tooltips
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        
        # Set custom item delegate for custom rendering
        self.setItemDelegate(DuplicateItemDelegate(self))
        
        # Expand all groups by default
        self.expandAll()
    
    def setModel(self, model):
        """Set the model and expand all items by default."""
        super().setModel(model)
        self.expandAll()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events to update tooltips."""
        index = self.indexAt(event.pos())
        if index.isValid():
            item = index.data(Qt.UserRole)
            if item:
                self.setToolTip(item.data(Qt.ToolTipRole) or "")
        else:
            self.setToolTip("")
        
        super().mouseMoveEvent(event)

class DuplicateItemDelegate(QStyledItemDelegate):
    """Custom delegate for rendering duplicate file items with enhanced appearance."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.margin = 4
    
    def paint(self, painter, option, index):
        """Paint the item using the given painter and style options."""
        # Get the item data
        item = index.data(Qt.UserRole)
        if not item:
            return super().paint(painter, option, index)
        
        # Configure the style options
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        
        # Get the widget style
        style = options.widget.style() if options.widget else QApplication.style()
        
        # Save the painter state
        painter.save()
        
        try:
            # Draw the item background
            if options.state & QStyle.State_Selected:
                painter.fillRect(option.rect, options.palette.highlight())
            elif options.state & QStyle.State_MouseOver:
                painter.fillRect(option.rect, options.palette.alternateBase())
            
            # Highlight original files with a different background
            if isinstance(item, DuplicateFileItem) and item.is_original:
                highlight_color = QColor(225, 245, 225)  # Light green
                if options.state & QStyle.State_Selected:
                    highlight_color = highlight_color.darker(110)
                painter.fillRect(option.rect, highlight_color)
            
            # Calculate text rectangle
            text_rect = option.rect.adjusted(self.margin, 0, -self.margin, 0)
            
            # Draw the icon if available
            icon = index.data(Qt.DecorationRole)
            if icon and isinstance(icon, QIcon):
                icon_rect = option.rect.adjusted(4, 2, -2, -2)
                icon_rect.setWidth(16)
                icon_rect.setHeight(16)
                icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                text_rect.adjust(22, 0, 0, 0)  # Make room for the icon
            
            # Draw the text
            text = index.data(Qt.DisplayRole) or ""
            if text:
                # Set text color based on selection state
                if options.state & QStyle.State_Selected:
                    painter.setPen(options.palette.highlightedText().color())
                else:
                    painter.setPen(options.palette.text().color())
                
                # Draw the text with elision if needed
                metrics = painter.fontMetrics()
                elided_text = metrics.elidedText(
                    text, 
                    Qt.TextElideMode.ElideMiddle, 
                    text_rect.width()
                )
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided_text)
                
                # Add a small indicator for original files
                if isinstance(item, DuplicateFileItem) and item.is_original:
                    original_text = " (Original)"
                    original_width = metrics.horizontalAdvance(original_text)
                    original_rect = text_rect.adjusted(metrics.horizontalAdvance(elided_text) + 4, 0, 0, 0)
                    original_rect.setWidth(original_width)
                    painter.setPen(Qt.darkGreen)
                    painter.drawText(original_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, original_text)
        finally:
            # Restore the painter state
            painter.restore()
    
    def sizeHint(self, option, index):
        """Return the size hint for the item."""
        # Adjust the size hint if needed
        size = super().sizeHint(option, index)
        return QSize(size.width(), size.height() + 4)  # Add some padding
