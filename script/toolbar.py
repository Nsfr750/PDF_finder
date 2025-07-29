"""
Toolbar management for PDF Duplicate Finder.
"""
from PyQt6.QtCore import pyqtSignal, QObject, QSize
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtWidgets import QToolBar

class ToolbarManager(QObject):
    """Manages the application's toolbar and actions."""
    
    # Signals
    open_folder_triggered = pyqtSignal()
    save_results_triggered = pyqtSignal()
    load_results_triggered = pyqtSignal()
    prev_group_triggered = pyqtSignal()
    next_group_triggered = pyqtSignal()
    prev_file_triggered = pyqtSignal()
    next_file_triggered = pyqtSignal()
    delete_triggered = pyqtSignal()
    
    def __init__(self, parent, language_manager):
        super().__init__(parent)
        self.parent = parent
        self.language_manager = language_manager
        
        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("MainToolbar")
        self.toolbar.setIconSize(QSize(24, 24))
        
        # Initialize UI
        self.setup_ui()
        
        # Connect language changes
        self.language_manager.language_changed.connect(self.retranslate_ui)
    
    def setup_ui(self):
        """Set up the toolbar UI elements."""
        self.create_actions()
        self.create_toolbar()
    
    def create_actions(self):
        """Create toolbar actions."""
        # File actions
        self.open_action = self._create_action(
            "file.open", "Open Folder", 
            QKeySequence.StandardKey.Open, 
            self.open_folder_triggered.emit
        )
        self.save_results_action = self._create_action(
            "file.save_results", "Save Results",
            QKeySequence.StandardKey.Save,
            self.save_results_triggered.emit
        )
        self.load_results_action = self._create_action(
            "file.load_results", "Load Results",
            QKeySequence("Ctrl+L"),
            self.load_results_triggered.emit
        )
        
        # Navigation actions (can be added later)
        self.prev_group_action = None
        self.next_group_action = None
        self.prev_file_action = None
        self.next_file_action = None
        self.delete_action = None
    
    def _create_action(self, key, default_text, shortcut, slot):
        """Helper method to create an action with translation support."""
        action = QAction(self.parent.tr(key, default_text), self.parent)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        return action
    
    def create_toolbar(self):
        """Create the main toolbar with common actions."""
        # Clear existing actions
        self.toolbar.clear()
        
        # Add actions to toolbar
        self.toolbar.addAction(self.open_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_results_action)
        self.toolbar.addAction(self.load_results_action)
        
        # Add navigation actions if they exist
        if hasattr(self, 'prev_group_action') and self.prev_group_action:
            self.toolbar.addSeparator()
            self.toolbar.addAction(self.prev_group_action)
            self.toolbar.addAction(self.next_group_action)
            
        if hasattr(self, 'prev_file_action') and self.prev_file_action:
            self.toolbar.addSeparator()
            self.toolbar.addAction(self.prev_file_action)
            self.toolbar.addAction(self.next_file_action)
            
        # Add delete action if it exists
        if hasattr(self, 'delete_action') and self.delete_action:
            self.toolbar.addSeparator()
            self.toolbar.addAction(self.delete_action)
        
        return self.toolbar
    
    def get_toolbar(self):
        """Return the toolbar instance."""
        return self.toolbar
    
    def retranslate_ui(self):
        """Retranslate all UI elements when language changes."""
        self.open_action.setText(self.parent.tr("file.open", "Open Folder"))
        self.save_results_action.setText(self.parent.tr("file.save_results", "Save Results"))
        self.load_results_action.setText(self.parent.tr("file.load_results", "Load Results"))
        
        # Update navigation actions if they exist
        if hasattr(self, 'prev_group_action') and self.prev_group_action:
            self.prev_group_action.setText(self.parent.tr("nav.prev_group", "Previous Group"))
            self.next_group_action.setText(self.parent.tr("nav.next_group", "Next Group"))
            
        if hasattr(self, 'prev_file_action') and self.prev_file_action:
            self.prev_file_action.setText(self.parent.tr("nav.prev_file", "Previous File"))
            self.next_file_action.setText(self.parent.tr("nav.next_file", "Next File"))
            
        if hasattr(self, 'delete_action') and self.delete_action:
            self.delete_action.setText(self.parent.tr("edit.delete", "Delete"))
