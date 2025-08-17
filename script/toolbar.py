"""
Toolbar implementation for PDF Duplicate Finder.
"""
import logging
from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QCoreApplication
from typing import Optional, Dict

# Import language manager
from lang.language_manager import LanguageManager

# Set up logger
logger = logging.getLogger(__name__)

class MainToolBar(QToolBar):
    """Main toolbar for the application."""
    
    def __init__(self, parent=None, language_manager: Optional[LanguageManager] = None):
        """Initialize the toolbar.
        
        Args:
            parent: Parent widget.
            language_manager: Optional LanguageManager instance for translations.
        """
        super().__init__(parent)
        self.setObjectName("mainToolBar")
        self.setMovable(False)
        self.language_manager = language_manager or LanguageManager()
        self.menu_actions = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the toolbar UI components."""
        # Clear existing actions
        self.clear()
        
        # Add standard actions if needed
        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        # Connect to language change signal
        self.language_manager.language_changed.connect(self.on_language_changed)
    
    def add_actions_from_menu(self, menu_actions: Dict[str, QAction]):
        """Add actions from the menu to the toolbar.
        
        Args:
            menu_actions: Dictionary of menu actions to add to the toolbar.
        """
        logger.debug("Adding actions to toolbar")
        logger.debug(f"Available menu actions: {list(menu_actions.keys())}")
        
        # Store the menu actions for later updates
        self.menu_actions = menu_actions
        
        # Clear existing actions
        self.clear()
        
        # Add actions to the toolbar
        action_keys = ['open_folder', 'settings', 'help']  # Add more action keys as needed
        for key in action_keys:
            if key in menu_actions:
                self.addAction(menu_actions[key])
                if key in ['open_folder']:  # Add separators after these actions
                    self.addSeparator()
    
    def retranslate_ui(self):
        """Retranslate all toolbar items when the language changes."""
        if hasattr(self, 'menu_actions') and self.menu_actions:
            # Rebuild the toolbar with the new translations
            self.add_actions_from_menu(self.menu_actions)
    
    def on_language_changed(self):
        """Handle language change event."""
        self.retranslate_ui()
        self.update_toolbar_actions()
    
    def update_toolbar_actions(self):
        """Update the toolbar with the current actions and translations."""
        # Clear existing actions
        self.clear()
        
        # Add Open action
        if 'open_folder' in self.menu_actions and self.menu_actions['open_folder']:
            action = self.menu_actions['open_folder']
            action.setText(self.tr("Open Folder"))
            action.setStatusTip(self.tr("Open a folder to scan for duplicate PDFs"))
            self.addAction(action)
        
        # Add separator
        self.addSeparator()
        
        # Add Select All action
        if 'select_all' in self.menu_actions and self.menu_actions['select_all']:
            action = self.menu_actions['select_all']
            action.setText(self.tr("Select All"))
            action.setStatusTip(self.tr("Select all items"))
            self.addAction(action)
        
        # Add Deselect All action
        if 'deselect_all' in self.menu_actions and self.menu_actions['deselect_all']:
            action = self.menu_actions['deselect_all']
            action.setText(self.tr("Deselect All"))
            action.setStatusTip(self.tr("Deselect all items"))
            self.addAction(action)

        # Delete All action
        if 'delete_all' in self.menu_actions and self.menu_actions['delete_all']:
            action = self.menu_actions['delete_all']
            action.setText(self.tr("Delete All"))
            action.setStatusTip(self.tr("Delete all items"))
            self.addAction(action)            
        
        logger.debug(f"Toolbar actions after update: {[a.text() for a in self.actions()]}")

    def retranslate_ui(self):
        """Retranslate the toolbar UI elements when the language changes."""
        logger.debug("Retranslating toolbar UI")
        self.update_toolbar_actions()
    
    def tr(self, text: str) -> str:
        """Translate text using the language manager if available."""
        if hasattr(self, 'language_manager') and self.language_manager:
            return self.language_manager.tr(text, text)
        return QCoreApplication.translate("MainToolBar", text)
