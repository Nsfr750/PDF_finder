"""
Menu management for PDF Duplicate Finder.
"""
from PyQt6.QtCore import pyqtSignal, QObject, QSize, QTranslator, QLocale
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtWidgets import QMenuBar, QMenu, QActionGroup

class MenuManager(QObject):
    """Manages the application's menu bar and actions."""
    
    # Signals
    open_folder_triggered = pyqtSignal()
    save_results_triggered = pyqtSignal()
    load_results_triggered = pyqtSignal()
    settings_triggered = pyqtSignal()
    exit_triggered = pyqtSignal()
    view_log_triggered = pyqtSignal()
    check_updates_triggered = pyqtSignal()
    about_triggered = pyqtSignal()
    documentation_triggered = pyqtSignal()
    markdown_docs_triggered = pyqtSignal()
    sponsor_triggered = pyqtSignal()
    pdf_viewer_triggered = pyqtSignal()
    language_changed = pyqtSignal(str)  # language_code
    
    def __init__(self, parent, language_manager):
        super().__init__(parent)
        self.parent = parent
        self.language_manager = language_manager
        
        # Create menu bar
        self.menu_bar = QMenuBar()
        self.menu_bar.setObjectName("MainMenuBar")
        
        # Initialize UI
        self.setup_ui()
        
        # Connect language changes
        self.language_manager.language_changed.connect(self.retranslate_ui)
    
    def setup_ui(self):
        """Set up the menu UI elements."""
        self.create_actions()
        self.create_menus()
        self.retranslate_ui()
    
    def create_actions(self):
        """Create menu actions."""
        # File actions
        self.open_action = self._create_action(
            "menu.open", "&Open Folder...", 
            QKeySequence.StandardKey.Open, 
            self.open_folder_triggered.emit
        )
        self.save_results_action = self._create_action(
            "menu.save_results", "&Save Results...",
            QKeySequence.StandardKey.Save,
            self.save_results_triggered.emit
        )
        self.load_results_action = self._create_action(
            "menu.load_results", "&Load Results...",
            QKeySequence("Ctrl+L"),
            self.load_results_triggered.emit
        )
        self.settings_action = self._create_action(
            "menu.settings", "&Settings...",
            QKeySequence("Ctrl+,"),
            self.settings_triggered.emit
        )
        self.exit_action = self._create_action(
            "menu.exit", "E&xit",
            QKeySequence.StandardKey.Quit,
            self.exit_triggered.emit
        )
        
        # View actions
        self.view_log_action = self._create_action(
            "menu.view_log", "View &Log",
            QKeySequence("Ctrl+Shift+L"),
            self.view_log_triggered.emit
        )
        self.view_pdf_viewer_action = self._create_action(
            "menu.pdf_viewer", "PDF &Viewer",
            QKeySequence("Ctrl+P"),
            self.pdf_viewer_triggered.emit
        )
        
        # Language actions
        self.language_group = QActionGroup(self)
        self.language_group.setExclusive(True)
        self.language_actions = {}
        
        for lang_code, lang_name in self.language_manager.available_languages.items():
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setData(lang_code)
            action.triggered.connect(self.on_language_changed)
            self.language_group.addAction(action)
            self.language_actions[lang_code] = action
        
        # Tools actions
        self.check_updates_action = self._create_action(
            "menu.check_updates", "Check for &Updates",
            None,
            self.check_updates_triggered.emit
        )
        
        # Help actions
        self.documentation_action = self._create_action(
            "menu.documentation", "&Documentation",
            QKeySequence("F1"),
            self.documentation_triggered.emit
        )
        self.markdown_docs_action = self._create_action(
            "menu.markdown_docs", "&Markdown Documentation",
            QKeySequence("Shift+F1"),
            self.markdown_docs_triggered.emit
        )
        self.sponsor_action = self._create_action(
            "menu.sponsor", "&Sponsor...",
            None,
            self.sponsor_triggered.emit
        )
        self.about_action = self._create_action(
            "menu.about", "&About",
            QKeySequence("F12"),
            self.about_triggered.emit
        )
    
    def _create_action(self, key, default_text, shortcut, slot):
        """Helper method to create an action with translation support."""
        action = QAction(self.parent.tr(key, default_text), self.parent)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        return action
    
    def create_menus(self):
        """Create the application menus."""
        # File menu
        self.file_menu = self.menu_bar.addMenu("")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_results_action)
        self.file_menu.addAction(self.load_results_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.settings_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # View menu
        self.view_menu = self.menu_bar.addMenu("")
        self.view_menu.addAction(self.view_log_action)
        self.view_menu.addAction(self.view_pdf_viewer_action)
        
        # Language submenu
        self.language_menu = self.view_menu.addMenu("")
        for action in self.language_actions.values():
            self.language_menu.addAction(action)
        
        # Tools menu
        self.tools_menu = self.menu_bar.addMenu("")
        self.tools_menu.addAction(self.check_updates_action)
        
        # Help menu
        self.help_menu = self.menu_bar.addMenu("")
        self.help_menu.addAction(self.documentation_action)
        self.help_menu.addAction(self.markdown_docs_action)
        self.help_menu.addAction(self.sponsor_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)
    
    def on_language_changed(self):
        """Handle language change from the menu."""
        action = self.sender()
        if action and action.isChecked():
            language_code = action.data()
            self.language_changed.emit(language_code)
    
    def retranslate_ui(self):
        """Retranslate all UI elements when language changes."""
        # File menu
        self.file_menu.setTitle(self.parent.tr("menu.file", "&File"))
        self.open_action.setText(self.parent.tr("menu.open", "&Open Folder..."))
        self.save_results_action.setText(self.parent.tr("menu.save_results", "&Save Results..."))
        self.load_results_action.setText(self.parent.tr("menu.load_results", "&Load Results..."))
        self.settings_action.setText(self.parent.tr("menu.settings", "&Settings..."))
        self.exit_action.setText(self.parent.tr("menu.exit", "E&xit"))
        
        # View menu
        self.view_menu.setTitle(self.parent.tr("menu.view", "&View"))
        self.view_log_action.setText(self.parent.tr("menu.view_log", "View &Log"))
        self.view_pdf_viewer_action.setText(self.parent.tr("menu.pdf_viewer", "PDF &Viewer"))
        
        # Language menu
        self.language_menu.setTitle(self.parent.tr("menu.language", "&Language"))
        for lang_code, action in self.language_actions.items():
            action.setChecked(lang_code == self.language_manager.current_language)
            action.setText(self.parent.tr(f"language.{lang_code}", 
                                        self.language_manager.available_languages.get(lang_code, lang_code)))
        
        # Tools menu
        self.tools_menu.setTitle(self.parent.tr("menu.tools", "&Tools"))
        self.check_updates_action.setText(self.parent.tr("menu.check_updates", "Check for &Updates"))
        
        # Help menu
        self.help_menu.setTitle(self.parent.tr("menu.help", "&Help"))
        self.documentation_action.setText(self.parent.tr("menu.documentation", "&Documentation"))
        self.markdown_docs_action.setText(self.parent.tr("menu.markdown_docs", "&Markdown Documentation"))
        self.sponsor_action.setText(self.parent.tr("menu.sponsor", "&Sponsor..."))
        self.about_action.setText(self.parent.tr("menu.about", "&About"))
    
    def get_menu_bar(self):
        """Return the menu bar instance."""
        return self.menu_bar
