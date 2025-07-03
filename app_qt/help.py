from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
                             QPushButton, QApplication, QWidget, QButtonGroup, 
                             QFrame)
from PySide6.QtCore import Qt, QUrl, Signal, QSize
from PySide6.QtGui import QDesktopServices, QPalette, QColor
import webbrowser
import os

class HelpDialog(QDialog):
    # Signal to notify language change
    language_changed = Signal(str)
    
    def __init__(self, parent=None, current_lang='en'):
        super().__init__(parent)
        self.current_lang = current_lang
        self.setMinimumSize(800, 600)
        
        # Set up UI
        self.init_ui()
        self.retranslate_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Language selection with styled buttons
        lang_widget = QWidget()
        lang_layout = QHBoxLayout(lang_widget)
        lang_layout.setContentsMargins(0, 0, 0, 10)
        
        # Create a frame to contain the buttons
        button_frame = QFrame()
        button_frame.setFrameShape(QFrame.StyledPanel)
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
        self.close_btn = QPushButton()
        self.close_btn.clicked.connect(self.accept)
        
        # Add widgets to main layout
        layout.addWidget(lang_widget)
        layout.addWidget(self.text_browser)
        layout.addWidget(self.close_btn, alignment=Qt.AlignRight)
    
    def retranslate_ui(self):
        """Update UI text based on current language"""
        if self.current_lang == 'it':
            self.setWindowTitle("Aiuto - PDF Duplicate Finder")
            help_text = """
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
            self.close_btn.setText("Chiudi")
        else:
            self.setWindowTitle("Help - PDF Duplicate Finder")
            help_text = """
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
            self.close_btn.setText("Close")
        
        self.text_browser.setHtml(help_text)
    
    def on_language_changed(self, lang):
        """Handle language change"""
        if lang != self.current_lang:
            self.current_lang = lang
            
            # Update button states
            self.en_button.setChecked(lang == 'en')
            self.it_button.setChecked(lang == 'it')
            
            # Update UI and emit signal
            self.retranslate_ui()
            self.language_changed.emit(lang)
    
    def open_link(self, url):
        """Open links in default web browser."""
        QDesktopServices.openUrl(url)
