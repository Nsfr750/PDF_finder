from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTextBrowser, QApplication)
from PyQt6.QtCore import Qt, QSize, QUrl, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
from .version import get_version
# Import language manager
from script.simple_lang_manager import SimpleLanguageManager
import os
import sys
import platform
from pathlib import Path
from wand.image import Image as WandImage
import psutil
import subprocess
import logging

logger = logging.getLogger(__name__)

class AboutDialog(QDialog):
    def __init__(self, parent=None, language_manager=None):
        super().__init__(parent)
        self.language_manager = language_manager if language_manager else SimpleLanguageManager()
        self.setWindowTitle(self.language_manager.tr("about.title", "About PDF Duplicate Finder"))
        self.setMinimumSize(600, 600)
        
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
            logo_label = QLabel("LOGO")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #666;")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setFixedSize(128, 128)
            header.addWidget(logo_label)
        
        # App info
        app_info = QVBoxLayout()
        
        title = QLabel(self.language_manager.tr("about.title", "PDF Duplicate Finder"))
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        version_text = self.language_manager.tr("about.version", "Version {version}").format(version=get_version())
        version = QLabel(version_text)
        version.setStyleSheet("color: white;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        app_info.addWidget(title)
        app_info.addWidget(version)
        app_info.addStretch()
        
        header.addLayout(app_info)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Description
        description = QLabel(
            self.language_manager.tr(
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
        sys_info.setMaximumHeight(300) # Height of Info Block
        layout.addWidget(QLabel(self.language_manager.tr("about.system_info", "<b>System Information:</b>")))
        layout.addWidget(sys_info)
        
        # Copyright and license
        copyright = QLabel(
            self.language_manager.tr(
                "about.copyright",
                " {year} Nsfr750\n"
                "This software is licensed under the GPL3 License."
            ).format(year="2025")
        )
        copyright.setStyleSheet("color: white; font-size: 11px;")
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright)
        
        # Buttons
        buttons = QHBoxLayout()
        
        # GitHub button
        github_btn = QPushButton("GitHub")
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Nsfr750/PDF_Finder")))
        # Style GitHub button with blue background and white text
        github_btn.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
        """)
        
        # Close button
        close_btn = QPushButton(self.language_manager.tr("about.close", "Close"))
        close_btn.clicked.connect(self.accept)
        # Style Close button with red background and white text
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        
        buttons.addStretch()
        buttons.addWidget(github_btn)
        buttons.addWidget(close_btn)
        
        layout.addLayout(buttons)
        
        # Connect language change signal
        self.language_manager.language_changed.connect(self.retranslate_ui)
    
    def retranslate_ui(self):
        """Update the UI when the language changes."""
        self.setWindowTitle(self.language_manager.tr("about.title", "About PDF Duplicate Finder"))
        
        # Update version text
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and "Version" in widget.text():
                widget.setText(self.language_manager.tr("about.version", "Version {version}").format(version=get_version()))
                break
        
        # Update description and other translatable text
        for widget in self.findChildren(QLabel):
            if widget.text() == "System Information:":
                widget.setText(self.language_manager.tr("about.system_info", "<b>System Information:</b>"))
            elif "This software is licensed" in widget.text():
                widget.setText(
                    self.language_manager.tr(
                        "about.copyright",
                        " {year} Nsfr750\n"
                        "This software is licensed under the GPL3 License."
                    ).format(year="2025")
                )
        
        # Update button text
        for button in self.findChildren(QPushButton):
            if button.text() == "Close":
                button.setText(self.language_manager.tr("about.close", "Close"))
    
    def get_imagemagick_version(self):
        """Get ImageMagick version information."""
        try:
            # Try to get version from Wand first
            from wand.version import MAGICK_VERSION, MAGICK_VERSION_NUMBER
            return f"{MAGICK_VERSION} ({MAGICK_VERSION_NUMBER})"
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Could not get ImageMagick version from Wand: {e}")
        
        # Fallback: try to run magick/convert command
        try:
            # Try different possible command names
            commands = ['magick', 'convert', 'identify']
            for cmd in commands:
                try:
                    result = subprocess.run([cmd, '-version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        # Extract version from first line
                        first_line = result.stdout.split('\n')[0]
                        if 'Version:' in first_line:
                            version = first_line.split('Version:')[1].split(',')[0].strip()
                            return version
                        return first_line.strip()
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    continue
        except Exception as e:
            logger.warning(f"Could not get ImageMagick version from command: {e}")
        
        return 'Not found'
    
    def get_ghostscript_version(self):
        """Get Ghostscript version information."""
        try:
            # Try different possible command names
            commands = ['gs', 'gswin64c', 'gswin32c', 'ghostscript']
            for cmd in commands:
                try:
                    result = subprocess.run([cmd, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return result.stdout.strip()
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    continue
        except Exception as e:
            logger.warning(f"Could not get Ghostscript version: {e}")
        
        return 'Not found'

    def get_system_info(self):
        import psutil

        system = platform.system()
        release = platform.release()
        machine = platform.machine()
        python_version = platform.python_version()

        # Get CPU information
        cpu_info = platform.processor()
        if not cpu_info and system == "Windows":
            cpu_info = platform.processor() or "Unknown"
        elif not cpu_info and system == "Darwin":
            cpu_info = (
                subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.brand_string"]
                )
                .strip()
                .decode()
            )
        elif not cpu_info and system == "Linux":
            cpu_info = ""
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        cpu_info = line.split(":", 1)[1].strip()
                        break

        # Get core count
        core_count = psutil.cpu_count(logical=True)
        physical_cores = psutil.cpu_count(logical=False) or core_count

        # Get RAM information
        ram = psutil.virtual_memory()
        total_ram = ram.total / (1024**3)  # Convert to GB
        available_ram = ram.available / (1024**3)  # Convert to GB

        # Get Wand version
        try:
            wand_version = getattr(WandImage, 'VERSION', 'Unknown')
            # If VERSION is a callable (like in newer versions), call it
            if callable(wand_version):
                wand_version = wand_version()
        except Exception as e:
            logger.warning(f"Could not get Wand version: {e}")
            wand_version = 'Unknown'
            
        imagemagick_version = self.get_imagemagick_version()
        ghostscript_version = self.get_ghostscript_version()
            
        info = [
            f"<b>OS:</b> {platform.system()} {platform.release()} ({platform.version()})<br>",
            f"<b>System:</b> ({machine})<br>",
            f"<b>Processor:</b> {cpu_info}<br>",
            f"<b>Core Count:</b> {core_count} ({physical_cores} physical cores)<br>",
            f"<b>RAM:</b> {total_ram:.2f} GB ({available_ram:.2f} GB available)<br>",
            f"<b>Python:</b> {platform.python_version()}<br>",
            f"<b>Qt:</b> {QT_VERSION_STR}<br>",
            f"<b>PyQt:</b> {PYQT_VERSION_STR}<br>",
            f"<b>Wand:</b> {wand_version}<br>",
            f"<b>ImageMagick:</b> {imagemagick_version}<br>",
            f"<b>Ghostscript:</b> {ghostscript_version}<br>"
        ]
        return ''.join(info)
