from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTextBrowser, QApplication)
from PyQt6.QtCore import Qt, QSize, QUrl, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
from .version import get_version
from .language_manager import LanguageManager
import os
import sys
import platform
from pathlib import Path

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.setWindowTitle(self.tr("about.title", "About PDF Duplicate Finder"))
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # App logo and title
        header = QHBoxLayout()
        
        # Load application logo
        logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            # Scale logo to a reasonable size while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            # Add some spacing
            logo_label.setContentsMargins(0, 0, 20, 0)
            header.addWidget(logo_label)
        else:
            # Add placeholder if logo not found
            print(f"Logo not found at: {logo_path}")
            logo_label = QLabel(self.tr("about.logo_placeholder", "LOGO"))
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #666;")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setFixedSize(128, 128)
            header.addWidget(logo_label)
        
        # App info
        app_info = QVBoxLayout()
        
        title = QLabel(self.tr("about.app_name", "PDF Duplicate Finder"))
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        version_text = self.tr("about.version", "Version {version}").format(version=get_version())
        version = QLabel(version_text)
        version.setStyleSheet("color: #666;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        app_info.addWidget(title)
        app_info.addWidget(version)
        app_info.addStretch()
        
        header.addLayout(app_info)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Description
        description = QLabel(
            self.tr(
                "about.description",
                "A tool to find and manage duplicate PDF files on your computer.\n\n"
                "PDF Duplicate Finder helps you save disk space by identifying and removing "
                "duplicate PDF documents based on their content."
            )
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # System info
        sys_info = QTextBrowser()
        sys_info.setOpenLinks(True)
        sys_info.setHtml(self.get_system_info())
        sys_info.setMaximumHeight(150)
        
        sys_info_label = QLabel(self.tr("about.system_info", "<b>System Information:</b>"))
        layout.addWidget(sys_info_label)
        layout.addWidget(sys_info)
        
        # Copyright and license
        copyright_text = self.tr(
            "about.copyright",
            " 2025 Nsfr750\n"
            "This software is licensed under the GPL3 License."
        )
        copyright = QLabel(copyright_text)
        copyright.setStyleSheet("color: #666; font-size: 11px;")
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright)
        
        # Buttons
        buttons = QHBoxLayout()
        
        # GitHub button
        github_btn = QPushButton(self.tr("about.github_button", "GitHub"))
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Nsfr750/PDF_Finder")))
        
        # Close button
        close_btn = QPushButton(self.tr("common.close", "Close"))
        close_btn.clicked.connect(self.accept)
        
        buttons.addStretch()
        buttons.addWidget(github_btn)
        buttons.addWidget(close_btn)
        
        layout.addLayout(buttons)
    
    def tr(self, key, default_text):
        """Translate text using the language manager."""
        return self.language_manager.tr(key, default_text)
    
    def get_system_info(self):
        """Get system information for the about dialog."""
        try:
            # Get PyQt version
            python_version = sys.version.split(' ')[0]
            
            # Get operating system information
            os_info = f"{platform.system()} {platform.release()} {platform.version()}"
            
            # Get screen resolution
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            resolution = f"{screen_geometry.width()}x{screen_geometry.height()}"
            
            # Get memory information
            try:
                import psutil
                memory = psutil.virtual_memory()
                total_memory = memory.total / (1024 ** 3)  # Convert to GB
                available_memory = memory.available / (1024 ** 3)
                memory_info = self.tr(
                    "about.memory_info",
                    "{available:.1f} GB available of {total:.1f} GB"
                ).format(available=available_memory, total=total_memory)
            except ImportError:
                memory_info = self.tr("about.psutil_not_available", "psutil not available")
            
            # Format the information as HTML
            info = self.tr(
                "about.system_info_html",
                """
                <html>
                <body>
                <h3>System Information</h3>
                <table>
                <tr><td><b>Operating System:</b></td><td>{os_info}</td></tr>
                <tr><td><b>Python Version:</b></td><td>{python_version}</td></tr>
                <tr><td><b>Qt Version:</b></td><td>{qt_version}</td></tr>
                <tr><td><b>PyQt Version:</b></td><td>{pyqt_version}</td></tr>
                <tr><td><b>Screen Resolution:</b></td><td>{resolution}</td></tr>
                <tr><td><b>Memory:</b></td><td>{memory_info}</td></tr>
                </table>
                </body>
                </html>
                """
            ).format(
                os_info=os_info,
                python_version=python_version,
                qt_version=QT_VERSION_STR,
                pyqt_version=PYQT_VERSION_STR,
                resolution=resolution,
                memory_info=memory_info
            )
            
            return info
            
        except Exception as e:
            error_msg = self.tr(
                "about.system_info_error",
                "Error getting system information: {error}"
            ).format(error=str(e))
            print(error_msg)
            return f"<p>{error_msg}</p>"
