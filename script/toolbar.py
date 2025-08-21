"""
Toolbar implementation for PDF Duplicate Finder.
"""
import logging
from typing import Optional, Dict

from PyQt6.QtCore import Qt, QCoreApplication, QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QToolBar, QWidget, QStyle, QApplication
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
    
    def _get_icon(self, name):
        """Get icon from theme or fallback to style standard icons."""
        # Map action names to standard icons
        icon_map = {
            'open_folder': 'folder-open',
            'pdf_viewer': 'document-preview',
            'export_csv': 'document-save',
            'exit': 'application-exit',
            'select_all': 'edit-select-all',
            'deselect_all': 'edit-select-none',
            'delete_selected': 'edit-delete',
            'log_viewer':'document-preview',
            'about': 'help-about',
            'help': 'help-contents',
            'documentation': 'docs-contents',
            'sponsor': 'emblem-favorite',
            'settings': 'preferences-system',
            'language': 'language' ,
            'check_updates': 'system-software-update',
        }
        
        icon_name = icon_map.get(name, '')
        if icon_name:
            # Try to get icon from theme first, fallback to standard icons
            icon = QIcon.fromTheme(icon_name)
            if not icon.isNull():
                return icon
                
            # Fallback to standard icons
            std_icon_map = {
                'folder-open': QStyle.StandardPixmap.SP_DirOpenIcon,
                'document-preview': QStyle.StandardPixmap.SP_FileDialogDetailedView,
                'edit-select-all': QStyle.StandardPixmap.SP_ArrowRight,
                'edit-select-none': QStyle.StandardPixmap.SP_ArrowLeft,
                'edit-delete': QStyle.StandardPixmap.SP_TrashIcon,
                'help-about': QStyle.StandardPixmap.SP_MessageBoxInformation,
                'help-contents': QStyle.StandardPixmap.SP_DialogHelpButton,
                'emblem-favorite': QStyle.StandardPixmap.SP_DialogYesButton,
                'preferences-system': QStyle.StandardPixmap.SP_ComputerIcon,
                'system-software-update': QStyle.StandardPixmap.SP_BrowserReload
            }
            
            std_icon = std_icon_map.get(icon_name, QStyle.StandardPixmap.SP_ComputerIcon)
            return self.style().standardIcon(std_icon)
            
        return QIcon()

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
            ['select_all', 'deselect_all'], 
            ['delete_selected'],            
        ]

        self.addSeparator()
         
        # Right group (help and about)
        right_group = [
            ['help', 'documentation'], 
        ]

        first_group_added = False
        for group in left_groups:
            existing = []
            for k in group:
                if k in self.menu_actions and self.menu_actions[k] is not None:
                    action = self.menu_actions[k]
                    # Set icon for the action
                    icon = self._get_icon(k)
                    if not icon.isNull():
                        action.setIcon(icon)
                    existing.append(action)
                    
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
        
        # Add a visual separator before the right-aligned group
        self.addSeparator()

        # Right-aligned help group
        for group in right_group:
            # Handle both single actions and lists of actions
            action_keys = group if isinstance(group, list) else [group]
            existing_actions = []
            
            # Collect all valid actions
            for key in action_keys:
                if key in self.menu_actions and self.menu_actions[key] is not None:
                    existing_actions.append(self.menu_actions[key])
            
            # Add separator if needed and add the actions with icons
            if existing_actions:
                if first_group_added:
                    self.addSeparator()
                for action in existing_actions:
                    # Set icon for the action
                    action_name = None
                    for name, act in self.menu_actions.items():
                        if act == action:
                            action_name = name
                            break
                    if action_name:
                        icon = self._get_icon(action_name)
                        if not icon.isNull():
                            action.setIcon(icon)
                    self.addAction(action)
                first_group_added = True
    
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
