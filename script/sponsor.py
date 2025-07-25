from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTextBrowser, QApplication, QWidget,
                             QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QUrl, QSize, QBuffer, QTimer
from PyQt6.QtGui import QPixmap, QDesktopServices, QImage, QIcon
import webbrowser
import os
import io
import qrcode
import wand.image
import logging

logger = logging.getLogger(__name__)

class SponsorDialog(QDialog):
    def __init__(self, parent=None, language_manager=None):
        super().__init__(parent)
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
        
        self.setWindowTitle(self.tr("sponsor.window_title", "Support Development"))
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.tr("sponsor.title", "Support PDF Duplicate Finder"))
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Message
        message = QLabel(self.tr(
            "sponsor.message",
            "If you find this application useful, please consider supporting its development.\n\n"
            "Your support helps cover hosting costs and encourages further development."
        ))
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)
        
        # Create a grid layout for donation methods
        grid = QGridLayout()
        
        # GitHub Sponsors
        github_label = QLabel(f'<a href="https://github.com/sponsors/Nsfr750">{self.tr("sponsor.links.github_sponsors", "GitHub Sponsors")}</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # PayPal
        paypal_label = QLabel(f'<a href="https://paypal.me/3dmega">{self.tr("sponsor.links.paypal", "PayPal Donation")}</a>')
        paypal_label.setOpenExternalLinks(True)
        paypal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Monero
        monero_address = "47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF"
        monero_label = QLabel(self.tr("sponsor.monero.label", "Monero:"))
        monero_address_label = QLabel(monero_address)
        monero_address_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        monero_address_label.setStyleSheet("""
            QLabel {
                font-family: monospace;
                background-color: #f0f0f0;
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #ddd;
            }
        """)
        
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f'monero:{monero_address}')
        qr.make(fit=True)
        
        # Generate QR code as a Wand image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to bytes using Wand
        with wand.image.Image(blob=qr_img.tobytes()) as img:
            # Convert to RGBA if needed
            if img.alpha_channel:
                img.background_color = wand.color.Color('white')
                img.alpha_channel = 'background'
            
            # Save to bytes buffer
            img.format = 'png'
            img_data = img.make_blob()
        
        # Load image data into QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        
        # Scale the pixmap
        pixmap = pixmap.scaled(200, 200, 
                             Qt.AspectRatioMode.KeepAspectRatio, 
                             Qt.TransformationMode.SmoothTransformation)
        
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_label.setToolTip(self.tr("sponsor.qr_tooltip", "Scan to donate XMR"))
        
        # Add widgets to grid
        grid.addWidget(QLabel(f"<h3>{self.tr('sponsor.ways_to_support', 'Ways to Support:')}</h3>"), 0, 0, 1, 2)
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
        other_help.setHtml(f"""
        <h3>{self.tr('sponsor.other_ways.title', 'Other Ways to Help:')}</h3>
        <ul>
            <li>{self.tr('sponsor.other_ways.star', 'Star the project on')} <a href="https://github.com/Nsfr750/PDF_Finder">GitHub</a></li>
            <li>{self.tr('sponsor.other_ways.report', 'Report bugs and suggest features')}</li>
            <li>{self.tr('sponsor.other_ways.share', 'Share with others who might find it useful')}</li>
        </ul>
        """)
        other_help.setMaximumHeight(150)
        layout.addWidget(other_help)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Close button
        close_btn = QPushButton(self.tr("common.close", "Close"))
        close_btn.clicked.connect(self.accept)
        
        # Donate button
        donate_btn = QPushButton(self.tr("sponsor.buttons.donate_paypal", "Donate with PayPal"))
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
        self.copy_monero_btn = QPushButton(self.tr("sponsor.buttons.copy_monero", "Copy Monero Address"))
        self.copy_monero_btn.setStyleSheet("""
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
        self.copy_monero_btn.clicked.connect(lambda: self.copy_to_clipboard(monero_address))
        
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_monero_btn)
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
        
        # Change button text temporarily
        original_text = self.copy_monero_btn.text()
        self.copy_monero_btn.setText(self.tr("sponsor.buttons.copied", "Copied!"))
        
        # Reset button text after 2 seconds
        QTimer.singleShot(2000, self.reset_monero_button)
    
    def reset_monero_button(self):
        """Reset the Monero button text and style."""
        self.copy_monero_btn.setText(self.tr("sponsor.buttons.copy_monero", "Copy Monero Address"))
