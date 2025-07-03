from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTextBrowser, QApplication)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QDesktopServices
import sys
import platform
from pathlib import Path

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PDF Duplicate Finder")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # App logo and title
        header = QHBoxLayout()
        
        # Load application logo
        logo_path = Path(__file__).parent.parent / "images" / "logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            # Scale logo to a reasonable size while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            # Add some spacing
            logo_label.setContentsMargins(0, 0, 20, 0)
            header.addWidget(logo_label)
        else:
            # Add placeholder if logo not found
            print(f"Logo not found at: {logo_path}")
            logo_label = QLabel("LOGO")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #666;")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setFixedSize(128, 128)
            header.addWidget(logo_label)
        
        # App info
        app_info = QVBoxLayout()
        
        title = QLabel("PDF Duplicate Finder")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        version = QLabel("Version 1.0.0")
        version.setStyleSheet("color: #666;")
        
        app_info.addWidget(title)
        app_info.addWidget(version)
        app_info.addStretch()
        
        header.addLayout(app_info)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Description
        description = QLabel(
            "A tool to find and manage duplicate PDF files on your computer.\n\n"
            "PDF Duplicate Finder helps you save disk space by identifying and removing "
            "duplicate PDF documents based on their content."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # System info
        sys_info = QTextBrowser()
        sys_info.setOpenLinks(True)
        sys_info.setHtml(self.get_system_info())
        sys_info.setMaximumHeight(150)
        layout.addWidget(QLabel("<b>System Information:</b>"))
        layout.addWidget(sys_info)
        
        # Copyright and license
        copyright = QLabel(
            "© 2025 Nsfr750\n"
            "This software is licensed under the GPL3 License."
        )
        copyright.setStyleSheet("color: #666; font-size: 11px;")
        copyright.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright)
        
        # Buttons
        buttons = QHBoxLayout()
        
        # GitHub button
        github_btn = QPushButton("GitHub")
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Nsfr750/PDF_finder")))
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        buttons.addStretch()
        buttons.addWidget(github_btn)
        buttons.addWidget(close_btn)
        
        layout.addLayout(buttons)
    
    def get_system_info(self):
        """Get system information for the about dialog."""
        try:
            import PySide6
            pyside_version = PySide6.__version__
        except ImportError:
            pyside_version = "Not available"
            
        return f"""
        <table>
            <tr><td><b>OS:</b></td><td>{platform.system()} {platform.release()}</td></tr>
            <tr><td><b>Python:</b></td><td>{platform.python_version()}</td></tr>
            <tr><td><b>PySide6:</b></td><td>{pyside_version}</td></tr>
            <tr><td><b>Processor:</b></td><td>{platform.processor() or 'Unknown'}</td></tr>
        </table>
        """
