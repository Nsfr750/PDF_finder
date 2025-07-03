from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QApplication
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
import webbrowser
import os

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - PDF Duplicate Finder")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Text browser for help content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.anchorClicked.connect(self.open_link)
        
        # Add help content
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
        <p>Visit our <a href="https://github.com/Nsfr750/PDF_finder">GitHub repository</a> for more information and documentation.</p>
        """
        
        self.text_browser.setHtml(help_text)
        layout.addWidget(self.text_browser)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
    
    def open_link(self, url):
        """Open links in default web browser."""
        QDesktopServices.openUrl(url)
