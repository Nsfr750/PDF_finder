"""File list widget for displaying duplicate PDF groups."""
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAbstractItemView,
    QStyledItemDelegate, QStyleOptionViewItem, QApplication, QStyle
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QModelIndex, QRect
from PyQt6.QtGui import QColor, QBrush, QFont, QIcon, QPixmap, QPainter, QFontMetrics
import logging
from .language_manager import LanguageManager

logger = logging.getLogger(__name__)

def _tr(key, default_text):
    """Helper function to translate text using the language manager."""
    return LanguageManager().tr(key, default_text)

class FileListWidget(QTreeWidget):
    """Widget for displaying duplicate PDF groups in a tree structure."""
    
    # Signals
    group_selected = pyqtSignal(list)  # List of PDFDocument objects
    open_file = pyqtSignal(str)        # File path to open
    open_containing_folder = pyqtSignal(str)  # File path to show in explorer
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        
        self.setColumnCount(3)
        self.setHeaderLabels([
            _tr("file_list.column_name", "Name"),
            _tr("file_list.column_size", "Size"),
            _tr("file_list.column_pages", "Pages")
        ])
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
    
    def tr(self, key, default_text):
        """Translate text using the language manager."""
        return self.language_manager.tr(key, default_text)
    
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
            
            # Set group item text with translations
            group_item.setText(0, self.tr(
                "file_list.group_title",
                "Duplicate Group {group_num} ({file_count} files)"
            ).format(group_num=i + 1, file_count=len(group)))
            
            group_item.setText(1, self.format_file_size(group_size))
            
            page_count = group[0].page_count if hasattr(group[0], 'page_count') else '?'
            group_item.setText(2, self.tr(
                "file_list.page_count",
                "{count} pages"
            ).format(count=page_count))
            
            # Add tooltip with more info
            tooltip = self.tr(
                "file_list.group_tooltip",
                "<b>Group {group_num}: {file_count} duplicate files</b>"
                "<br>Size: {size}"
            ).format(
                group_num=i + 1,
                file_count=len(group),
                size=self.format_file_size(group_size)
            )
            
            if len(group) > 1:
                tooltip += self.tr(
                    "file_list.group_tooltip_savings",
                    "<br>Space savings: {savings}"
                ).format(savings=self.format_file_size(space_savings))
                
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
                
                doc_page_count = doc.page_count if hasattr(doc, 'page_count') else '?'
                doc_item.setText(2, self.tr(
                    "file_list.page_count",
                    "{count} pages"
                ).format(count=doc_page_count))
                
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
            expand_all = menu.addAction(self.tr("file_list.action_expand_all", "Expand All"))
            collapse_all = menu.addAction(self.tr("file_list.action_collapse_all", "Collapse All"))
            menu.addSeparator()
            open_all = menu.addAction(self.tr("file_list.action_open_all", "Open All in Group"))
            show_all = menu.addAction(self.tr("file_list.action_show_all", "Show All in Explorer"))
            
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
            open_file = menu.addAction(self.tr("file_list.action_open_file", "Open File"))
            show_in_explorer = menu.addAction(self.tr("file_list.action_show_in_explorer", "Show in Explorer"))
            
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
        # Check if painter is valid
        if not painter.isActive():
            logger.warning("Painter is not active, skipping paint operation")
            return
            
        # Save the painter state at the start
        painter.save()
        
        try:
            # Set up the style options
            options = QStyleOptionViewItem(option)
            self.initStyleOption(options, index)
            
            # Configure the painter with rendering hints
            painter.setRenderHints(
                QPainter.RenderHint.Antialiasing | 
                QPainter.RenderHint.TextAntialiasing |
                QPainter.RenderHint.SmoothPixmapTransform
            )
            
            # Get the item
            model = index.model()
            if not model:
                return
                
            item = model.itemFromIndex(index)
            if not item:
                return
            
            # Get the style
            style = option.widget.style() if option.widget else QApplication.style()
            
            # Draw the item background
            style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)
            
            # Highlight the first item in each group (the one to keep)
            if item.parent() is not None and item.parent().indexOfChild(item) == 0:
                # Draw highlight background
                highlight_rect = option.rect
                highlight_brush = QBrush(QColor(220, 240, 255))
                painter.fillRect(highlight_rect, highlight_brush)
            
            # Get the text to display
            text = index.data(Qt.ItemDataRole.DisplayRole)
            
            if text:
                # Calculate text rectangle with some padding
                text_rect = options.rect.adjusted(2, 0, -2, 0)
                
                # Draw text with elision if needed
                metrics = painter.fontMetrics()
                elided_text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, text_rect.width())
                
                # Set text color based on state
                text_color = QColor(Qt.GlobalColor.black)
                if not (option.state & QStyle.StateFlag.State_Enabled):
                    text_color = QColor(Qt.GlobalColor.gray)
                
                painter.setPen(text_color)
                
                # Draw the text
                text_flags = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                if option.state & QStyle.StateFlag.State_Selected:
                    text_flags |= Qt.AlignmentFlag.AlignHCenter
                
                painter.drawText(text_rect, int(text_flags), elided_text)
                
        except Exception as e:
            logger.error(f"Error painting item: {e}", exc_info=True)
            # If there's an error, fall back to default painting
            try:
                super().paint(painter, option, index)
            except Exception as inner_e:
                logger.error(f"Error in fallback paint: {inner_e}")
                
        finally:
            # Always restore the painter state
            if painter.isActive():
                try:
                    painter.restore()
                except Exception as e:
                    logger.error(f"Error restoring painter state: {e}")
    
    def sizeHint(self, option, index):
        """Return the size hint for the item."""
        size = super().sizeHint(option, index)
        if size.height() < 24:  # Minimum height
            size.setHeight(24)
        return size
