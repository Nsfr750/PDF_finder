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
logger = logging.getLogger('PDFDuplicateFinder')

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
        self.setMinimumSize(800, 600)
        self.setWindowTitle(self.tr("Help"))
        
        try:
            # Set up UI
            self.init_ui()
            self.retranslate_ui()
            logger.debug("Help dialog initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing help dialog: {e}")
            raise
    
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
            self.en_button = QPushButton("English")
            self.en_button.setCheckable(True)
            self.en_button.setStyleSheet(button_style)
            self.en_button.clicked.connect(lambda: self.on_language_changed('en'))
            
            # Italian button
            self.it_button = QPushButton("Italiano")
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
            self.close_btn = QPushButton(self.tr("Close"))
            self.close_btn.clicked.connect(self.accept)
            
            # Add widgets to layout
            layout.addWidget(lang_widget)
            layout.addWidget(self.text_browser, 1)
            layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)
            
        except Exception as e:
            logger.error(f"Error initializing UI: {e}")
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
            logger.debug(f"UI retranslated to {self.current_lang}")
            
        except Exception as e:
            logger.error(f"Error retranslating UI: {e}")
            # Fallback to English if translation fails
            help_text = self._get_english_help()
            self.text_browser.setHtml(help_text)
    
    def _get_italian_help(self):
        """Return Italian help text."""
        return """
            <h1>PDF Duplicate Finder - Aiuto</h1>
            
            <h2>Introduzione</h2>
            <p>PDF Duplicate Finder ti aiuta a trovare e gestire i file PDF duplicati sul tuo computer.</p>
            
            <h2>Come Usare</h2>
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
            
            <h2>Serve altro aiuto?</h2>
            <p>Visita la nostra <a href="https://github.com/Nsfr750/PDF_Finder">repository GitHub</a> per maggiori informazioni e documentazione.</p>
            """
    
    def _get_english_help(self):
        """Return English help text."""
        return """
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
                <li><b>Ctrl+Q</b>: Quit application</li>
                <li><b>F1</b>: Show this help</li>
            </ul>
            
            <h2>Need More Help?</h2>
            <p>Visit our <a href="https://github.com/Nsfr750/PDF_Finder">GitHub repository</a> for more information and documentation.</p>
            """
    
    def on_language_changed(self, lang):
        """
        Handle language change.
        
        Args:
            lang (str): New language code ('en' or 'it')
        """
        try:
            if lang not in ['en', 'it']:
                logger.warning(f"Unsupported language: {lang}")
                return
                
            if lang != self.current_lang:
                logger.debug(f"Language changed from {self.current_lang} to {lang}")
                self.current_lang = lang
                
                # Update button states
                self.en_button.setChecked(lang == 'en')
                self.it_button.setChecked(lang == 'it')
                
                # Update UI and emit signal
                self.retranslate_ui()
                self.language_changed.emit(lang)
                
        except Exception as e:
            logger.error(f"Error changing language: {e}")
    
    def open_link(self, url):
        """Open links in default web browser."""
        QDesktopServices.openUrl(url)
