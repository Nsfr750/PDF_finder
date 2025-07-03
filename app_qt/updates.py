from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTextBrowser, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QUrl
from PySide6.QtGui import QDesktopServices
import requests
import json
import platform
from packaging import version

class UpdateChecker(QObject):
    update_available = Signal(dict)
    no_update = Signal()
    error_occurred = Signal(str)
    
    def check_for_updates(self, current_version):
        """Check for updates on GitHub."""
        try:
            # Replace with your GitHub repository URL
            repo_url = "https://api.github.com/repos/Nsfr750/PDF_Finder/releases/latest"
            response = requests.get(repo_url, timeout=10)
            response.raise_for_status()
            
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            
            if version.parse(latest_version) > version.parse(current_version):
                self.update_available.emit({
                    'version': latest_version,
                    'release_notes': latest_release.get('body', 'No release notes available.'),
                    'url': latest_release.get('html_url', '')
                })
            else:
                self.no_update.emit()
                
        except Exception as e:
            self.error_occurred.emit(str(e))

class UpdateDialog(QDialog):
    def __init__(self, current_version, parent=None):
        super().__init__(parent)
        self.current_version = current_version
        self.latest_version = None
        self.update_url = ""
        
        self.setWindowTitle("Check for Updates")
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Checking for updates...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress)
        
        # Release notes
        self.release_notes = QTextBrowser()
        self.release_notes.setVisible(False)
        layout.addWidget(self.release_notes)
        
        # Buttons
        self.button_box = QHBoxLayout()
        
        self.download_btn = QPushButton("Download Update")
        self.download_btn.clicked.connect(self.download_update)
        self.download_btn.setVisible(False)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        self.button_box.addStretch()
        self.button_box.addWidget(self.download_btn)
        self.button_box.addWidget(self.close_btn)
        
        layout.addLayout(self.button_box)
        
        # Start checking for updates
        self.check_updates()
    
    def check_updates(self):
        """Start the update check in a separate thread."""
        self.thread = QThread()
        self.checker = UpdateChecker()
        self.checker.moveToThread(self.thread)
        
        self.thread.started.connect(
            lambda: self.checker.check_for_updates(self.current_version)
        )
        
        self.checker.update_available.connect(self.show_update_available)
        self.checker.no_update.connect(self.show_no_updates)
        self.checker.error_occurred.connect(self.show_error)
        
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
    
    def show_update_available(self, update_info):
        """Show that an update is available."""
        self.latest_version = update_info['version']
        self.update_url = update_info.get('url', '')
        
        self.status_label.setText(
            f"Version {self.latest_version} is available! (Current: {self.current_version})"
        )
        
        self.release_notes.setHtml(
            f"<h3>What's New in v{self.latest_version}</h3>"
            f"<pre>{update_info['release_notes']}</pre>"
        )
        self.release_notes.setVisible(True)
        
        self.download_btn.setVisible(True)
        self.progress.setVisible(False)
    
    def show_no_updates(self):
        """Show that no updates are available."""
        self.status_label.setText(
            f"You're using the latest version ({self.current_version})."
        )
        self.progress.setVisible(False)
    
    def show_error(self, error_msg):
        """Show an error message."""
        self.status_label.setText(f"Error checking for updates: {error_msg}")
        self.progress.setVisible(False)
    
    def download_update(self):
        """Open the download URL in the default web browser."""
        if self.update_url:
            QDesktopServices.openUrl(QUrl(self.update_url))
        self.accept()
