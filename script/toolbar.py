"""
Toolbar implementation for PDF Duplicate Finder.
"""
import logging
from typing import Optional, Dict

from PyQt6.QtCore import Qt, QCoreApplication, QSize
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar, QWidget
from PyQt6.QtWidgets import QSizePolicy

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
        # Visual tweaks
        self.setIconSize(QSize(20, 20))  # balanced default; scales with DPI
        self.setFloatable(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.setContentsMargins(6, 3, 6, 3)
        self.apply_visual_style()
        
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
        """Build the toolbar from stored menu actions with improved grouping and layout."""
        if not self.menu_actions:
            return

        # Left groups (main actions)
        left_groups = [
            ['open_folder', 'pdf_viewer'],
            ['select_all', 'deselect_all', 'delete_selected'],
            ['settings', 'check_updates'],
        ]
        # Right group (help and about)
        right_group = ['help', 'documentation', 'about', 'sponsor']

        first_group_added = False
        for group in left_groups:
            existing = [self.menu_actions[k] for k in group if k in self.menu_actions and self.menu_actions[k] is not None]
            if not existing:
                continue
            if first_group_added:
                self.addSeparator()
            for act in existing:
                self.addAction(act)
            first_group_added = True

        # Stretch spacer to push help group to the right
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        # Right-aligned help group
        existing_right = [self.menu_actions[k] for k in right_group if k in self.menu_actions and self.menu_actions[k] is not None]
        if existing_right:
            if first_group_added:
                self.addSeparator()
            for act in existing_right:
                self.addAction(act)
    
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
        # Rebuild using existing actions (texts are owned by actions)
        self.update_toolbar_actions()
        # Re-apply style to ensure consistent visuals on theme/language change
        self.apply_visual_style()

    def apply_visual_style(self):
        """Apply a consistent visual style to toolbar buttons."""
        # Subtle padding and spacing; keep neutral for light/dark themes
        self.setStyleSheet(
            """
            QToolBar { spacing: 6px; }
            QToolButton { padding: 4px 8px; margin: 2px; }
            QToolButton:pressed { padding-top: 5px; padding-bottom: 3px; }
            """
        )
    
    def tr(self, text: str) -> str:
        """Translate text using the language manager if available."""
        if hasattr(self, 'language_manager') and self.language_manager:
            return self.language_manager.tr(text, text)
        return QCoreApplication.translate("MainToolBar", text)
