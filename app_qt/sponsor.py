from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTextBrowser, QApplication, QWidget,
                             QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt, QUrl, QSize, QBuffer
from PySide6.QtGui import QPixmap, QDesktopServices, QImage
import webbrowser
import os
import io
import qrcode
from PIL import ImageQt

class SponsorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Support Development")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Support PDF Duplicate Finder")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Message
        message = QLabel(
            "If you find this application useful, please consider supporting its development."
            "\n\nYour support helps cover hosting costs and encourages further development."
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        # Create a grid layout for donation methods
        grid = QGridLayout()
        
        # GitHub Sponsors
        github_label = QLabel('<a href="https://github.com/sponsors/Nsfr750">GitHub Sponsors</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignCenter)
        
        # PayPal
        paypal_label = QLabel('<a href="https://paypal.me/3dmega">PayPal Donation</a>')
        paypal_label.setOpenExternalLinks(True)
        paypal_label.setAlignment(Qt.AlignCenter)
        
        # Monero
        monero_address = "47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF"
        monero_label = QLabel("Monero:")
        monero_address_label = QLabel(f"<code>{monero_address}</code>")
        monero_address_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        monero_address_label.setWordWrap(True)
        
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=4,
        )
        qr.add_data(f'monero:{monero_address}')
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL Image to QPixmap
        qimage = ImageQt.ImageQt(img)
        pixmap = QPixmap.fromImage(qimage).scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        qr_label.setAlignment(Qt.AlignCenter)
        qr_label.setToolTip("Scan to donate XMR")
        
        # Add widgets to grid
        grid.addWidget(QLabel("<h3>Ways to Support:</h3>"), 0, 0, 1, 2)
        grid.addWidget(github_label, 1, 0, 1, 2)
        grid.addWidget(paypal_label, 2, 0, 1, 2)
        grid.addWidget(monero_label, 3, 0, 1, 2)
        grid.addWidget(monero_address_label, 4, 0, 1, 2)
        grid.addWidget(qr_label, 1, 2, 4, 1)  # Span 4 rows
        
        # Add some spacing
        grid.setSpacing(10)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        
        # Add grid to layout
        layout.addLayout(grid)
        
        # Other ways to help
        other_help = QTextBrowser()
        other_help.setOpenExternalLinks(True)
        other_help.setHtml("""
        <h3>Other Ways to Help:</h3>
        <ul>
            <li>Star the project on <a href="https://github.com/Nsfr750/PDF_Finder">GitHub</a></li>
            <li>Report bugs and suggest features</li>
            <li>Share with others who might find it useful</li>
        </ul>
        """)
        other_help.setMaximumHeight(150)
        layout.addWidget(other_help)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        # Donate button
        donate_btn = QPushButton("Donate with PayPal")
        donate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0079C1;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0062A3;
            }
        """)
        donate_btn.clicked.connect(self.open_paypal_link)
        
        # Copy Monero address button
        copy_monero_btn = QPushButton("Copy Monero Address")
        copy_monero_btn.setStyleSheet("""
            QPushButton {
                background-color: #F26822;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #D45B1D;
            }
        """)
        copy_monero_btn.clicked.connect(lambda: self.copy_to_clipboard(monero_address))
        
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        button_layout.addWidget(copy_monero_btn)
        button_layout.addWidget(donate_btn)
        
        layout.addLayout(button_layout)
    
    def open_donation_link(self):
        """Open donation link in default web browser."""
        QDesktopServices.openUrl(QUrl("https://github.com/sponsors/Nsfr750"))

    def open_paypal_link(self):
        """Open PayPal link in default web browser."""
        QDesktopServices.openUrl(QUrl("https://paypal.me/3dmega"))

    def copy_to_clipboard(self, text):
        """Copy text to clipboard and show a tooltip."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Show a temporary tooltip
        button = self.sender()
        if button:
            button.setText("Copied!")
            button.setStyleSheet(button.styleSheet() + "background-color: #4CAF50;")
            
            # Reset button text after 2 seconds
            QTimer.singleShot(2000, lambda: self.reset_button(button, "Copy Monero Address"))
    
    def reset_button(self, button, text):
        """Reset button text and style."""
        button.setText(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #F26822;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #D45B1D;
            }
        """)
