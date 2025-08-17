"""
Menu implementation for the PDF Duplicate Finder application.
"""
from PyQt6.QtWidgets import (
    QMenu, QMenuBar, QFileDialog, QMessageBox, QApplication
)
from PyQt6.QtGui import QAction, QActionGroup, QIcon
from PyQt6.QtCore import Qt, QObject, QCoreApplication

import os
import webbrowser
import logging
from typing import Optional, Dict, Any, List, Callable

# Import language manager
from lang.language_manager import LanguageManager

# Set up logger
logger = logging.getLogger(__name__)

class MenuBar(QObject):
    """Menu bar for the PDF Duplicate Finder application."""
    
    def __init__(self, parent=None, language_manager: Optional[LanguageManager] = None):
        """Initialize the menu bar.
        
        Args:
            parent: Parent widget.
            language_manager: Optional LanguageManager instance for translations.
        """
        super().__init__(parent)
        self.parent = parent
        self.language_manager = language_manager or LanguageManager()
        self.menubar = QMenuBar()
        self.actions = {}
        self.menus = {}
        
        # Connect to language change signal
        self.language_manager.language_changed.connect(self.on_language_changed)
        
        # Set up the menu bar
        self.setup_menus()
    
    def setup_menus(self):
        """Set up the menu bar with all menus and actions."""
        # Clear existing menus
        self.menubar.clear()
        self.menus.clear()
        
        # File menu
        self.menus['file'] = self.create_file_menu()
        self.menubar.addMenu(self.menus['file'])
        
        # Edit menu
        self.menus['edit'] = self.create_edit_menu()
        self.menubar.addMenu(self.menus['edit'])
        
        # View menu
        self.menus['view'] = self.create_view_menu()
        self.menubar.addMenu(self.menus['view'])
        
        # Tools menu
        self.menus['tools'] = self.create_tools_menu()
        self.menubar.addMenu(self.menus['tools'])
        
        # Help menu
        self.menus['help'] = self.create_help_menu()
        self.menubar.addMenu(self.menus['help'])
    
    def retranslate_ui(self):
        """Retranslate all menu items when the language changes."""
        # Rebuild all menus with the new language
        self.setup_menus()
        
        # Notify parent that the language has changed
        if hasattr(self.parent, 'on_language_changed'):
            self.parent.on_language_changed()
    
    def on_language_changed(self):
        """Handle language change event."""
        self.retranslate_ui()
    
    def create_file_menu(self) -> QMenu:
        """Create the File menu.
        
        Returns:
            QMenu: The configured File menu.
        """
        menu = QMenu(self.tr("File"), self.parent)
        
        # Open Folder action
        self.actions['open_folder'] = QAction(self.tr("Open Folder"), self.parent)
        self.actions['open_folder'].setShortcut("Ctrl+O")
        self.actions['open_folder'].setStatusTip(self.tr("Open a folder to scan for duplicate PDFs"))
        self.actions['open_folder'].triggered.connect(self.parent.on_open_folder)
        menu.addAction(self.actions['open_folder'])
        
        # Add separator
        menu.addSeparator()

        # PDF Viewer action
        self.actions['pdf_viewer'] = QAction(self.tr("PDF Viewer"), self.parent)
        self.actions['pdf_viewer'].setStatusTip(self.tr("Open PDF Viewer"))
        self.actions['pdf_viewer'].triggered.connect(self.on_show_pdf_viewer)
        menu.addAction(self.actions['pdf_viewer'])
        
        # Add separator
        menu.addSeparator()
        
        # Exit action
        self.actions['exit'] = QAction(self.tr("Exit"), self.parent)
        self.actions['exit'].setShortcut("Ctrl+Q")
        self.actions['exit'].setStatusTip(self.tr("Exit the application"))
        self.actions['exit'].triggered.connect(QApplication.quit)
        menu.addAction(self.actions['exit'])
        
        return menu
    
    def create_edit_menu(self) -> QMenu:
        """Create the Edit menu.
        
        Returns:
            QMenu: The configured Edit menu.
        """
        menu = QMenu(self.tr("Edit"), self.parent)
        
        # Select All action
        self.actions['select_all'] = QAction(self.tr("Select All"), self.parent)
        self.actions['select_all'].setShortcut("Ctrl+A")
        self.actions['select_all'].setStatusTip(self.tr("Select all items"))
        self.actions['select_all'].triggered.connect(self.parent.on_select_all)
        menu.addAction(self.actions['select_all'])
        
        # Deselect All action
        self.actions['deselect_all'] = QAction(self.tr("Deselect All"), self.parent)
        self.actions['deselect_all'].setStatusTip(self.tr("Deselect all items"))
        self.actions['deselect_all'].triggered.connect(self.parent.on_deselect_all)
        menu.addAction(self.actions['deselect_all'])
        
        return menu
    
    def create_view_menu(self) -> QMenu:
        """Create the View menu.
        
        Returns:
            QMenu: The configured View menu.
        """
        menu = QMenu(self.tr("View"), self.parent)
        
        # Toolbar toggle action
        self.actions['toggle_toolbar'] = QAction(self.tr("Show Toolbar"), self.parent)
        self.actions['toggle_toolbar'].setCheckable(True)
        self.actions['toggle_toolbar'].setChecked(True)
        self.actions['toggle_toolbar'].setStatusTip(self.tr("Show or hide the toolbar"))
        self.actions['toggle_toolbar'].triggered.connect(self.parent.on_toggle_toolbar)
        menu.addAction(self.actions['toggle_toolbar'])
        
        # Status bar toggle action
        self.actions['toggle_statusbar'] = QAction(self.tr("Show Status Bar"), self.parent)
        self.actions['toggle_statusbar'].setCheckable(True)
        self.actions['toggle_statusbar'].setChecked(True)
        self.actions['toggle_statusbar'].setStatusTip(self.tr("Show or hide the status bar"))
        self.actions['toggle_statusbar'].triggered.connect(self.parent.on_toggle_statusbar)
        menu.addAction(self.actions['toggle_statusbar'])
        
        return menu
    
    def create_tools_menu(self) -> QMenu:
        """Create the Tools menu.
        
        Returns:
            QMenu: The configured Tools menu.
        """
        menu = QMenu(self.tr("Tools"), self.parent)
        
        # Settings action
        self.actions['settings'] = QAction(self.tr("Settings"), self.parent)
        self.actions['settings'].setStatusTip(self.tr("Configure application settings"))
        
        def on_settings_triggered():
            print("DEBUG: Settings menu action triggered")
            try:
                print("DEBUG: Accessing parent.on_show_settings")
                print(f"DEBUG: Parent type: {type(self.parent)}")
                print(f"DEBUG: Parent has on_show_settings: {hasattr(self.parent, 'on_show_settings')}")
                
                # Try to call the method directly with error handling
                if hasattr(self.parent, 'on_show_settings'):
                    print("DEBUG: Calling parent.on_show_settings()")
                    try:
                        self.parent.on_show_settings()
                        print("DEBUG: Returned from on_show_settings()")
                    except Exception as e:
                        print(f"ERROR in on_show_settings call: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # Try to show an error message if possible
                        try:
                            QMessageBox.critical(
                                self.parent,
                                "Error",
                                f"Failed to open settings: {e}"
                            )
                        except:
                            print("Could not show error message dialog")
                else:
                    print("ERROR: Parent does not have on_show_settings method")
                    print(f"DEBUG: Parent methods: {[m for m in dir(self.parent) if not m.startswith('_')]}")
                    
            except Exception as e:
                print(f"ERROR in settings menu handler: {e}")
                import traceback
                traceback.print_exc()
        
        self.actions['settings'].triggered.connect(on_settings_triggered)
        menu.addAction(self.actions['settings'])
        
        # Add separator
        menu.addSeparator()
        
        # Check for Updates action
        self.actions['check_updates'] = QAction(self.tr("Check for Updates"), self.parent)
        self.actions['check_updates'].setStatusTip(self.tr("Check for application updates"))
        if hasattr(self.parent, 'check_for_updates'):
            self.actions['check_updates'].triggered.connect(self.parent.check_for_updates)
        menu.addAction(self.actions['check_updates'])
        
        # Add separator
        menu.addSeparator()
        
        # Language submenu
        self.menus['language'] = QMenu(self.tr("Language"), self.parent)
        self.setup_language_menu()
        menu.addMenu(self.menus['language'])
        
        return menu
    
    def create_help_menu(self) -> QMenu:
        """Create the Help menu.
        
        Returns:
            QMenu: The configured Help menu.
        """
        menu = QMenu(self.tr("Help"), self.parent)
        
        # Help action
        self.actions['help'] = QAction(self.tr("Help"), self.parent)
        self.actions['help'].setShortcut("F1")
        self.actions['help'].setStatusTip(self.tr("Open help documentation"))
        self.actions['help'].triggered.connect(self.on_show_help)
        menu.addAction(self.actions['help'])
        
        # Add separator
        menu.addSeparator()
        
        # Documentation action
        self.actions['documentation'] = QAction(self.tr("Documentation"), self.parent) 
        self.actions['documentation'].setStatusTip(self.tr("Open the documentation"))
        self.actions['documentation'].triggered.connect(self.on_show_documentation)
        menu.addAction(self.actions['documentation'])
        
        # Add separator
        menu.addSeparator()
        
        # About action
        self.actions['about'] = QAction(self.tr("About"), self.parent)
        self.actions['about'].setStatusTip(self.tr("Show information about the application"))
        self.actions['about'].triggered.connect(self.parent.on_show_about)
        menu.addAction(self.actions['about'])
        
        # Add separator
        menu.addSeparator()
        
        # Sponsor action
        self.actions['sponsor'] = QAction(self.tr("Sponsor"), self.parent) 
        self.actions['sponsor'].setStatusTip(self.tr("Support the development of this application"))
        self.actions['sponsor'].triggered.connect(self.on_show_sponsor)
        menu.addAction(self.actions['sponsor'])
        
        return menu
    
    def setup_language_menu(self):
        """Set up the language selection menu."""
        if not hasattr(self, 'language_group'):
            self.language_group = QActionGroup(self)
            self.language_group.setExclusive(True)
            
            # Add available languages
            languages = [
                ('English', 'en'),
                ('Italiano', 'it'),
                # Add more languages as needed
            ]
            
            for name, code in languages:
                action = QAction(self.tr(name), self.parent, checkable=True)
                action.setData(code)
                action.triggered.connect(lambda checked, c=code: self.parent.change_language(c))
                self.language_group.addAction(action)
                self.menus['language'].addAction(action)
                
                # Check the current language
                if hasattr(self, 'language_manager') and code == self.language_manager.current_language:
                    action.setChecked(True)
                
            # Connect to language changed signal to update the menu
            if hasattr(self, 'language_manager'):
                self.language_manager.language_changed.connect(self.update_language_menu)
    
    def update_language_menu(self, language_code: str):
        """Update the language menu to reflect the current language.
        
        Args:
            language_code: The code of the currently selected language.
        """
        if hasattr(self, 'language_group'):
            for action in self.language_group.actions():
                if action.data() == language_code:
                    action.setChecked(True)
                    break
    
    def on_language_changed(self, language_code: str):
        """Handle language change event."""
        logger.debug(f"Language changed to {language_code}, retranslating menu bar")
        self.retranslate_ui()
    
    def retranslate_ui(self):
        """Retranslate all menu items and actions with the current language."""
        try:
            logger.debug("Retranslating menu bar UI")
            
            # Update menu titles
            self.menus['file'].setTitle(self.tr("File"))
            self.menus['edit'].setTitle(self.tr("Edit"))
            self.menus['view'].setTitle(self.tr("View"))
            self.menus['tools'].setTitle(self.tr("Tools"))
            self.menus['help'].setTitle(self.tr("Help"))
            
            # Update file menu actions
            self.actions['open_folder'].setText(self.tr("Open Folder"))
            self.actions['open_folder'].setStatusTip(self.tr("Open a folder to scan for duplicate PDFs"))
            self.actions['pdf_viewer'].setText(self.tr("PDF Viewer"))
            self.actions['pdf_viewer'].setStatusTip(self.tr("Open PDF Viewer"))
            self.actions['exit'].setText(self.tr("Exit"))
            self.actions['exit'].setStatusTip(self.tr("Exit the application"))
            
            # Update edit menu actions
            self.actions['select_all'].setText(self.tr("Select All"))
            self.actions['select_all'].setStatusTip(self.tr("Select all items"))
            self.actions['deselect_all'].setText(self.tr("Deselect All"))
            self.actions['deselect_all'].setStatusTip(self.tr("Deselect all items"))
            
            # Update view menu actions
            self.actions['toggle_toolbar'].setText(self.tr("Show Toolbar"))
            self.actions['toggle_toolbar'].setStatusTip(self.tr("Show or hide the toolbar"))
            self.actions['toggle_statusbar'].setText(self.tr("Show Status Bar"))
            self.actions['toggle_statusbar'].setStatusTip(self.tr("Show or hide the status bar"))
            
            # Update tools menu actions
            self.actions['settings'].setText(self.tr("Settings"))
            self.actions['settings'].setStatusTip(self.tr("Configure application settings"))
            self.actions['check_updates'].setText(self.tr("Check for Updates"))
            self.actions['check_updates'].setStatusTip(self.tr("Check for application updates"))
            
            # Update help menu actions
            self.actions['help'].setText(self.tr("Help"))
            self.actions['help'].setStatusTip(self.tr("Open help documentation"))
            self.actions['documentation'].setText(self.tr("Documentation"))
            self.actions['documentation'].setStatusTip(self.tr("Open the documentation"))
            self.actions['about'].setText(self.tr("About"))
            self.actions['about'].setStatusTip(self.tr("Show information about the application"))
            self.actions['sponsor'].setText(self.tr("Sponsor"))
            self.actions['sponsor'].setStatusTip(self.tr("Support the development of this application"))
            
            # Update language menu
            if 'language' in self.menus:
                self.menus['language'].setTitle(self.tr("Language"))
                
            logger.debug("Menu bar retranslation completed")
            
        except Exception as e:
            logger.error(f"Error retranslating menu bar: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    def on_show_documentation(self):
        """Open the documentation in the markdown viewer."""
        try:
            from .markdown_viewer import MarkdownViewer
            # Pass None as file_path to let the viewer load the default documentation
            viewer = MarkdownViewer(
                file_path=None,
                language_manager=self.language_manager,
                parent=self.parent
            )
            viewer.exec()
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                self.tr("Error"),
                self.tr(f"Could not open documentation: {e}")
            )
    
    def on_show_sponsor(self):
        """Open the sponsor dialog."""
        try:
            from .sponsor import SponsorDialog
            dialog = SponsorDialog(self.parent, language_manager=self.language_manager)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                self.tr("Error"),
                self.tr(f"Could not open sponsor dialog: {e}")
            )
    
    def on_show_pdf_viewer(self):
        """Open the PDF Viewer."""
        try:
            from .PDF_viewer import PDFViewer
            viewer = PDFViewer(parent=self.parent, language_manager=self.language_manager)
            viewer.show()
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                self.tr("Error"),
                self.tr(f"Could not open PDF Viewer: {e}")
            )
    
    def on_show_help(self):
        """Open the help dialog."""
        try:
            from .help import HelpDialog
            
            # Create and show the help dialog
            help_dialog = HelpDialog(
                parent=self.parent,
                current_lang=self.language_manager.current_language
            )
            help_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                self.tr("Error"),
                self.tr(f"Could not open help dialog: {e}")
            )
    
    def tr(self, text: str) -> str:
        """Translate text using the parent's translator.
        
        Args:
            text: Text to translate.
            
        Returns:
            str: Translated text.
        """
        if hasattr(self.parent, 'tr'):
            return self.parent.tr(text)
        return QCoreApplication.translate('MenuBar', text)
