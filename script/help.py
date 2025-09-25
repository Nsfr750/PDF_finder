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
from script.simple_lang_manager import SimpleLanguageManager

logger = logging.getLogger('PDFDuplicateFinder')

def _tr(key, default_text):
    """Helper function to translate text using the language manager."""
    return SimpleLanguageManager().tr(key, default_text)

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
        self.language_manager = SimpleLanguageManager()
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
            
            # Language data with flag emojis - same as in menu.py
            languages = [
                ('English', 'en', '🇬🇧'),
                ('Italiano', 'it', '🇮🇹'),
                ('Russian', 'ru', '🇷🇺'),
                ('Ukrainian', 'ua', '🇺🇦'),
                ('German', 'de', '🇩🇪'),
                ('French', 'fr', '🇫🇷'),
                ('Portuguese', 'pt', '🇵🇹'),
                ('Spanish', 'es', '🇪🇸'),
                ('Japanese', 'ja', '🇯🇵'),
                ('Chinese', 'zh', '🇨🇳'),
                ('Arabic', 'ar', '🇦🇪'),
                ('Hebrew', 'he', '🇮🇱'),
            ]
            
            # Create language buttons
            self.lang_buttons = {}
            for name, code, flag in languages:
                button = QPushButton(f"{flag} {name}")
                button.setCheckable(True)
                button.setStyleSheet(button_style)
                button.clicked.connect(lambda checked, c=code: self.on_language_changed(c))
                self.lang_buttons[code] = button
                button_layout.addWidget(button)
            
            # Set current language
            for code, button in self.lang_buttons.items():
                if code == self.current_lang:
                    button.setChecked(True)
                else:
                    button.setChecked(False)
            
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
            # Get help text based on current language
            help_text = self._get_help_text(self.current_lang)
            
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
            try:
                fallback_text = self._get_help_text('en')
                self.text_browser.setHtml(fallback_text)
            except Exception as fallback_error:
                logger.error(f"Fallback to English also failed: {fallback_error}")
                self.text_browser.setHtml("<h1>Error</h1><p>Could not load help content.</p>")
    
    def _get_help_text(self, lang_code):
        """
        Get help text for the specified language.
        
        Args:
            lang_code (str): Language code (e.g., 'en', 'it', 'ru', etc.)
            
        Returns:
            str: HTML help text for the specified language
        """
        help_methods = {
            'en': self._get_english_help,
            'it': self._get_italian_help,
            'ru': self._get_russian_help,
            'ua': self._get_ukrainian_help,
            'de': self._get_german_help,
            'fr': self._get_french_help,
            'pt': self._get_portuguese_help,
            'es': self._get_spanish_help,
            'ja': self._get_japanese_help,
            'zh': self._get_chinese_help,
            'ar': self._get_arabic_help,
            'he': self._get_hebrew_help,
        }
        
        method = help_methods.get(lang_code, self._get_english_help)
        return method()
    
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
            
            <h2>Nuove Funzionalità</h2>
            
            <h3>Confronto Testuale</h3>
            <p>L'applicazione ora confronta i PDF sia per contenuto che per testo. Questo aiuta a identificare i duplicati anche quando i file hanno piccole differenze visive ma contengono lo stesso testo.</p>
            <p>Regola la soglia di somiglianza del testo nelle impostazioni per controllare quanto simili devono essere i file per essere considerati duplicati.</p>
            
            <h3>Filtri Avanzati</h3>
            <p>Utilizza i filtri per restringere la ricerca:</p>
            <ul>
                <li><b>Dimensione File:</b> Filtra per dimensione minima e massima</li>
                <li><b>Data Modifica:</b> Trova file modificati in un intervallo di date specifico</li>
                <li><b>Modello Nome:</b> Cerca file che corrispondono a un modello specifico (supporta caratteri jolly)</li>
            </ul>
            
            <h3>Suggerimenti per le Prestazioni</h3>
            <ul>
                <li>Usa i filtri per ridurre il numero di file da confrontare</li>
                <li>Regola la soglia di somiglianza in base alle tue esigenze</li>
                <li>Per grandi raccolte, considera di eseguire la scansione in lotti più piccoli</li>
            </ul>
            
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
            
            <h2>Introduction</h2>
            <p>PDF Duplicate Finder helps you find and manage duplicate PDF files on your computer.</p>
            
            <h2>How to Use</h2>
            <ol>
                <li>Click <b>Scan Folder</b> to select a directory to analyze</li>
                <li>Review the duplicate groups found</li>
                <li>Use the navigation buttons to move between groups and files</li>
                <li>Select files and use <b>Keep</b> or <b>Delete</b> to manage duplicates</li>
            </ol>
            
            <h2>New Features</h2>
            
            <h3>Text Comparison</h3>
            <p>The application now compares PDFs by both content and text. This helps identify duplicates even when the files have minor visual differences but contain the same text.</p>
            <p>Adjust the text similarity threshold in the settings to control how similar the text needs to be for files to be considered duplicates.</p>
            
            <h3>Advanced Filtering</h3>
            <p>Use filters to narrow down your search:</p>
            <ul>
                <li><b>File Size:</b> Filter by minimum and maximum file size</li>
                <li><b>Date Modified:</b> Find files modified within a specific date range</li>
                <li><b>Name Pattern:</b> Search for files matching a specific name pattern (supports wildcards)</li>
            </ul>
            
            <h3>Performance Tips</h3>
            <ul>
                <li>Use filters to reduce the number of files being compared</li>
                <li>Adjust the similarity threshold based on your needs</li>
                <li>For large collections, consider scanning in smaller batches</li>
            </ul>
            
            <h2>Keyboard Shortcuts</h2>
            <ul>
                <li><b>Ctrl+O</b>: Open folder to scan</li>
                <li><b>Ctrl+Q</b>: Quit application</li>
                <li><b>F1</b>: Show this help</li>
            </ul>
            """
        )
    
    def on_language_changed(self, lang_code):
        """
        Handle language change event.
        
        Args:
            lang_code (str): New language code
        """
        try:
            if lang_code != self.current_lang:
                self.current_lang = lang_code
                self.retranslate_ui()
                self.language_changed.emit(lang_code)
                
                # Update button states
                for code, button in self.lang_buttons.items():
                    if code == lang_code:
                        button.setChecked(True)
                    else:
                        button.setChecked(False)
                    
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
