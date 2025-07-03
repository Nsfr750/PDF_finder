"""
Module for handling duplicate file search functionality with model and view classes.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QTreeView, QStyledItemDelegate, QStyleOptionViewItem, QApplication
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
            return os.path.basename(self.file_path)
        elif role == Qt.UserRole:
            return self
        elif role == Qt.DecorationRole:
            # Return a file icon or other decoration
            return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        elif role == Qt.ToolTipRole:
            return f"{self.file_path}\nSize: {self.size:,} bytes\nModified: {self.modified}"
        return None

class DuplicateGroup:
    """Represents a group of duplicate files."""
    
    def __init__(self, files: List[DuplicateFileItem]):
        self.files = files
        self.is_expanded = False
    
    def data(self, role: int = Qt.DisplayRole):
        """Return data for the specified role."""
        if role == Qt.DisplayRole:
            return f"{len(self.files)} duplicate files"
        elif role == Qt.UserRole:
            return self
        elif role == Qt.DecorationRole:
            # Return a folder icon or other decoration
            return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
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
        
        # Set custom item delegate for custom rendering
        self.setItemDelegate(DuplicateItemDelegate(self))

class DuplicateItemDelegate(QStyledItemDelegate):
    """Custom delegate for rendering duplicate file items."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        """Paint the item with custom rendering."""
        # Let the base class handle the basic painting
        super().paint(painter, option, index)
        
        # Add custom rendering here if needed
        item = index.data(Qt.UserRole)
        if isinstance(item, DuplicateFileItem) and item.is_original:
            # Highlight original files
            painter.save()
            painter.setPen(Qt.green)
            rect = option.rect.adjusted(2, 2, -2, -2)
            painter.drawRect(rect)
            painter.restore()
    
    def sizeHint(self, option, index):
        """Return the size hint for the item."""
        # Adjust the size hint if needed
        size = super().sizeHint(option, index)
        return QSize(size.width(), size.height() + 4)  # Add some padding
