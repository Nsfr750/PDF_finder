"""
Help Dialog Module

This module provides a help dialog for the PDF Duplicate Finder application.
It includes support for multiple languages and a clean, modern interface.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
                             QPushButton, QWidget, QFrame)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal as Signal, QSize
from PyQt6.QtGui import QDesktopServices
import os

# Import application logger
import logging

# Import language manager
from script.lang_mgr import LanguageManager

logger = logging.getLogger('PDFDuplicateFinder')

def _tr(key, default_text):
    """Helper function to translate text using the language manager."""
    return LanguageManager().tr(key, default_text)

class HelpDialog(QDialog):
    # Signal to notify language change
    language_changed = Signal(str)
    
    def __init__(self, parent=None, current_lang='en'):
        """
        Initialize the help dialog.
        
        Args:
            parent: Parent widget
            current_lang (str): Current language code (default: 'en')
        """
        super().__init__(parent)
        self.current_lang = current_lang
        self.language_manager = LanguageManager()
        self.setMinimumSize(800, 600)
        self.setWindowTitle(self.tr("help.window_title", "Help"))
        
        try:
            # Set up UI
            self.init_ui()
            self.retranslate_ui()
            logger.debug(self.tr(
                "help.init_success",
                "Help dialog initialized successfully"
            ))
        except Exception as e:
            logger.error(self.tr(
                "help.init_error",
                "Error initializing help dialog: {error}"
            ).format(error=str(e)))
            raise
    
    def tr(self, key, default_text):
        """Translate text using the language manager."""
        return self.language_manager.tr(key, default_text)
    
    def init_ui(self):
        """Initialize the user interface components."""
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(10)
        
            # Language selection with styled buttons
            lang_widget = QWidget()
            lang_layout = QHBoxLayout(lang_widget)
            lang_layout.setContentsMargins(0, 0, 0, 10)
        
            # Create a frame to contain the buttons
            button_frame = QFrame()
            button_frame.setFrameShape(QFrame.Shape.StyledPanel)
            button_frame.setStyleSheet("""
                QFrame {
                    border-radius: 4px;
                    padding: 20px;
                }
            """)
            button_layout = QHBoxLayout(button_frame)
            button_layout.setContentsMargins(10, 2, 10, 2)
            button_layout.setSpacing(10)
        
            # Style for language buttons
            button_style = """
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 3px;
                    min-width: 80px;
                }
                QPushButton:checked {
                    background-color: #005a9e;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """
            
            # English button
            self.en_button = QPushButton(self.tr("help.language.en", "English"))
            self.en_button.setCheckable(True)
            self.en_button.setStyleSheet(button_style)
            self.en_button.clicked.connect(lambda: self.on_language_changed('en'))
            
            # Italian button
            self.it_button = QPushButton(self.tr("help.language.it", "Italiano"))
            self.it_button.setCheckable(True)
            self.it_button.setStyleSheet(button_style)
            self.it_button.clicked.connect(lambda: self.on_language_changed('it'))
            
            # Set current language
            if self.current_lang == 'it':
                self.it_button.setChecked(True)
                self.en_button.setChecked(False)
            else:
                self.en_button.setChecked(True)
                self.it_button.setChecked(False)
            
            # Add buttons to layout
            button_layout.addWidget(self.en_button)
            button_layout.addWidget(self.it_button)
            
            # Add to main layout
            lang_layout.addStretch()
            lang_layout.addWidget(button_frame)
            
            # Text browser for help content
            self.text_browser = QTextBrowser()
            self.text_browser.setOpenExternalLinks(True)
            self.text_browser.anchorClicked.connect(self.open_link)
            
            # Close button
            self.close_btn = QPushButton(self.tr("common.close", "Close"))
            self.close_btn.clicked.connect(self.accept)
            
            # Add widgets to layout
            layout.addWidget(lang_widget)
            layout.addWidget(self.text_browser, 1)
            layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)
            
        except Exception as e:
            logger.error(self.tr(
                "help.ui_init_error",
                "Error initializing UI: {error}"
            ).format(error=str(e)))
            raise
    
    def retranslate_ui(self):
        """
        Update the UI with the current language.
        
        This method loads the appropriate help text based on the current language
        and updates all UI elements accordingly.
        """
        try:
            if self.current_lang == 'it':
                help_text = self._get_italian_help()
            else:
                help_text = self._get_english_help()
                
            self.text_browser.setHtml(help_text)
            logger.debug(self.tr(
                "help.language_changed",
                "UI retranslated to {language}"
            ).format(language=self.current_lang))
            
        except Exception as e:
            logger.error(self.tr(
                "help.translation_error",
                "Error retranslating UI: {error}"
            ).format(error=str(e)))
            # Fallback to English if translation fails
            help_text = self._get_english_help()
            self.text_browser.setHtml(help_text)
    
    def _get_italian_help(self):
        """Return Italian help text."""
        return self.tr(
            "help.content.it",
            """
            <h1>PDF Duplicate Finder - Aiuto</h1>
            
            <h2>Introduzione</h2>
            <p>PDF Duplicate Finder ti aiuta a trovare e gestire i file PDF duplicati sul tuo computer.</p>
            
            <h2>Come Usare il programma</h2>
            <ol>
                <li>Clicca su <b>Scansiona Cartella</b> per selezionare una directory da analizzare</li>
                <li>Esamina i gruppi di duplicati trovati</li>
                <li>Usa i pulsanti di navigazione per spostarti tra i gruppi e i file</li>
                <li>Seleziona i file e usa <b>Mantieni</b> o <b>Elimina</b> per gestire i duplicati</li>
            </ol>
            
            <h2>Scorciatoie da Tastiera</h2>
            <ul>
                <li><b>Ctrl+O</b>: Apri cartella da scansionare</li>
                <li><b>Ctrl+Q</b>: Esci dall'applicazione</li>
                <li><b>F1</b>: Mostra questo aiuto</li>
            </ul>
            """
        )
    
    def _get_english_help(self):
        """Return English help text."""
        return self.tr(
            "help.content.en",
            """
            <h1>PDF Duplicate Finder - Help</h1>
            
            <h2>Getting Started</h2>
            <p>PDF Duplicate Finder helps you find and manage duplicate PDF files on your computer.</p>
            
            <h2>How to Use</h2>
            <ol>
                <li>Click <b>Scan Folder</b> to select a directory to scan for duplicate PDFs</li>
                <li>Review the duplicate groups found</li>
                <li>Use the navigation buttons to move between groups and files</li>
                <li>Select files and use <b>Keep</b> or <b>Delete</b> to manage duplicates</li>
            </ol>
            
            <h2>Keyboard Shortcuts</h2>
            <ul>
                <li><b>Ctrl+O</b>: Open folder to scan</li>
                <li><b>Ctrl+Q</b>: Quit the application</li>
                <li><b>F1</b>: Show this help</li>
            </ul>
            """
        )
    
    def on_language_changed(self, lang_code):
        """
        Handle language change event.
        
        Args:
            lang_code (str): New language code ('en' or 'it')
        """
        try:
            if lang_code != self.current_lang:
                self.current_lang = lang_code
                self.retranslate_ui()
                self.language_changed.emit(lang_code)
                
                # Update button states
                if lang_code == 'it':
                    self.it_button.setChecked(True)
                    self.en_button.setChecked(False)
                else:
                    self.en_button.setChecked(True)
                    self.it_button.setChecked(False)
                    
                logger.debug(self.tr(
                    "help.language_switched",
                    "Language switched to {language}"
                ).format(language=lang_code))
                
        except Exception as e:
            logger.error(self.tr(
                "help.language_switch_error",
                "Error switching language: {error}"
            ).format(error=str(e)))
    
    def open_link(self, url):
        """
        Open a link in the default web browser.
        
        Args:
            url: QUrl of the link to open
        """
        try:
            QDesktopServices.openUrl(url)
        except Exception as e:
            logger.error(self.tr(
                "help.link_open_error",
                "Error opening link {url}: {error}"
            ).format(url=url.toString(), error=str(e)))
