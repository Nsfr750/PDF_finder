"""
Module for handling duplicate file search functionality with model and view classes.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from PyQt6.QtCore import Qt, QAbstractItemModel, QModelIndex, QSize
from PyQt6.QtGui import QIcon, QPainter, QPalette, QColor
from PyQt6.QtWidgets import (
    QTreeView, QStyledItemDelegate, QStyleOptionViewItem, QApplication, QStyle,
    QAbstractItemView, QHeaderView
)

class DuplicateFileItem:
    """Represents a duplicate file item in the model."""
    
    def __init__(self, file_path: str, size: int, modified: float, is_original: bool = False, language_manager=None):
        self.file_path = file_path
        self.size = size
        self.modified = modified
        self.is_original = is_original
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
    
    def data(self, role: int = Qt.ItemDataRole.DisplayRole):
        """Return data for the specified role."""
        if role == Qt.ItemDataRole.DisplayRole:
            # Return just the file name for display
            return os.path.basename(self.file_path) if self.file_path else ""
        elif role == Qt.ItemDataRole.UserRole:
            return self
        elif role == Qt.ItemDataRole.DecorationRole:
            # Return a file icon or other decoration
            return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        elif role == Qt.ItemDataRole.ToolTipRole:
            # Show full path in tooltip
            if not self.file_path:
                return ""
            file_info = []
            file_info.append(self.tr("search_dup.tooltip.file", "File: {path}").format(path=self.file_path))
            if self.size is not None:
                file_info.append(self.tr("search_dup.tooltip.size", "Size: {size:,} bytes").format(size=self.size))
            if self.modified is not None:
                file_info.append(self.tr("search_dup.tooltip.modified", "Modified: {date}").format(date=self.modified))
            return "\n".join(filter(None, file_info))
        return None

class DuplicateGroup:
    """Represents a group of duplicate files."""
    
    def __init__(self, files: List[DuplicateFileItem], language_manager=None):
        self.files = files
        self.is_expanded = False
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
    
    def data(self, role: int = Qt.ItemDataRole.DisplayRole):
        """Return data for the specified role."""
        if role == Qt.ItemDataRole.DisplayRole:
            count = len(self.files)
            if count == 1:
                return self.tr("search_dup.group.singular", "1 duplicate file")
            return self.tr("search_dup.group.plural", "{count} duplicate files").format(count=count)
        elif role == Qt.ItemDataRole.UserRole:
            return self
        elif role == Qt.ItemDataRole.DecorationRole:
            # Return a folder icon or other decoration
            return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        elif role == Qt.ItemDataRole.ToolTipRole:
            if not self.files:
                return self.tr("search_dup.tooltip.empty_group", "No duplicate files in this group")
            return self.tr(
                "search_dup.tooltip.group", 
                "Click to expand/collapse - {count} duplicate files"
            ).format(count=len(self.files))
        return None

class DuplicateFilesModel(QAbstractItemModel):
    """Model for displaying duplicate files in a tree structure."""
    
    def __init__(self, duplicate_groups: List[List[Dict[str, Any]]] = None, parent=None, language_manager=None):
        super().__init__(parent)
        self.duplicate_groups = []
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
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
                    is_original=file_info.get('is_original', False),
                    language_manager=self.language_manager
                )
                file_items.append(file_item)
            
            if file_items:
                self.duplicate_groups.append(DuplicateGroup(file_items, self.language_manager))
        
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
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """Return the data stored under the given role for the item referred to by the index."""
        if not index.isValid():
            return None
        
        item = index.internalPointer()
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.DecorationRole, 
                   Qt.ItemDataRole.ToolTipRole, Qt.ItemDataRole.UserRole):
            return item.data(role)
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        """Return the data for the given role and section in the header with the specified orientation."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.tr("search_dup.header", "Duplicate Files")
        return None
    
    def flags(self, index: QModelIndex):
        """Return the item flags for the given index."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    
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
            
            # Remove empty groups or groups with only one file
            if len(group.files) < 2:
                self.duplicate_groups.remove(group)
        
        # Notify views that the model has been reset
        self.beginResetModel()
        self.endResetModel()

class DuplicateFilesView(QTreeView):
    """View for displaying duplicate files with custom rendering and interactions."""
    
    def __init__(self, parent=None, language_manager=None):
        super().__init__(parent)
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
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
        self.setItemDelegate(DuplicateItemDelegate(self, self.language_manager))
        
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
            item = index.data(Qt.ItemDataRole.UserRole)
            if item:
                self.setToolTip(item.data(Qt.ItemDataRole.ToolTipRole) or "")
        else:
            self.setToolTip("")
        
        super().mouseMoveEvent(event)

class DuplicateItemDelegate(QStyledItemDelegate):
    """Custom delegate for rendering duplicate file items with enhanced appearance."""
    
    def __init__(self, parent=None, language_manager=None):
        super().__init__(parent)
        self.margin = 4
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
    
    def paint(self, painter, option, index):
        """Paint the item using the given painter and style options."""
        if not index.isValid():
            return
            
        # Get the item data
        item = index.data(Qt.ItemDataRole.UserRole)
        if not item:
            return
            
        # Set up painter
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        option.state &= ~QStyle.StateFlag.State_HasFocus
        if option.state & QStyle.StateFlag.State_Selected:
            bg_color = option.palette.highlight().color()
            painter.fillRect(option.rect, bg_color)
            
            # Adjust text color for better contrast on selection
            text_color = option.palette.highlightedText().color()
            painter.setPen(text_color)
        else:
            # Use alternate background for better readability
            if index.row() % 2 == 1:
                bg_color = option.palette.alternateBase().color()
                painter.fillRect(option.rect, bg_color)
            
            # Use default text color
            text_color = option.palette.text().color()
            painter.setPen(text_color)
        
        # Draw icon
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon and isinstance(icon, QIcon):
            icon_rect = option.rect.adjusted(self.margin, self.margin, -self.margin, -self.margin)
            icon_rect.setWidth(16)  # Fixed width for icon
            icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Draw text
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        if text:
            text_rect = option.rect.adjusted(24 + self.margin * 2, 0, -self.margin, 0)  # Leave space for icon
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        
        # Draw a small indicator for original files
        if hasattr(item, 'is_original') and item.is_original:
            original_text = self.tr("search_dup.original_indicator", "(Original)")
            text_rect = option.rect.adjusted(24 + self.margin * 2, 0, -self.margin, 0)  # Align with text
            text_rect.setLeft(text_rect.left() + painter.fontMetrics().horizontalAdvance(text) + 5)
            
            # Use a different color for the "(Original)" text
            original_color = QColor(0, 128, 0)  # Dark green
            if option.state & QStyle.StateFlag.State_Selected:
                original_color = option.palette.highlightedText().color().lighter(150)
            
            painter.save()
            painter.setPen(original_color)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, original_text)
            painter.restore()
        
        painter.restore()
    
    def sizeHint(self, option, index):
        """Return the size hint for the item."""
        size = super().sizeHint(option, index)
        if size.isValid():
            size.setHeight(max(size.height(), 24))  # Ensure minimum height
        return size
