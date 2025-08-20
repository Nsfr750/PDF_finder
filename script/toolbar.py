"""
Toolbar implementation for PDF Duplicate Finder.
"""
import logging
from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QCoreApplication
from typing import Optional, Dict

# Import language manager
from script.lang_mgr import LanguageManager

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
        # Improve usability by showing text beside icons
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
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
        self._build_toolbar()

    def _build_toolbar(self):
        """Build the toolbar from stored menu actions with improved grouping."""
        if not self.menu_actions:
            return
        
        # Define toolbar groups (separators between groups)
        groups = [
            ['open_folder', 'pdf_viewer'],
            ['select_all', 'deselect_all'],
            ['settings', 'check_updates'],
            ['help', 'documentation', 'about', 'sponsor'],
        ]
        
        first_group_added = False
        for group in groups:
            # Collect existing actions in this group
            existing = [self.menu_actions[k] for k in group if k in self.menu_actions and self.menu_actions[k] is not None]
            if not existing:
                continue
            if first_group_added:
                self.addSeparator()
            for act in existing:
                self.addAction(act)
            first_group_added = True
    
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
        # Rebuild from stored actions to reflect latest translations
        self.clear()
        self._build_toolbar()
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
