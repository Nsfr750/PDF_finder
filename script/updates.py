from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTextBrowser, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal as Signal, QObject, QUrl
from PyQt6.QtGui import QDesktopServices
import requests
import json
import platform
from packaging import version
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Import language manager
from script.lang_mgr import LanguageManager

logger = logging.getLogger(__name__)

class UpdateDataManager:
    """Handles saving and loading update data to/from JSON file."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize with the configuration directory.
        
        Args:
            config_dir: Directory where updates.json will be stored
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.updates_file = self.config_dir / "updates.json"
        
        # Initialize with default values if file doesn't exist
        if not self.updates_file.exists():
            self._save_data({
                'last_check': None,
                'last_version': None,
                'update_available': False,
                'update_data': {}
            })
    
    def _load_data(self) -> Dict[str, Any]:
        """Load update data from JSON file."""
        try:
            if self.updates_file.exists():
                with open(self.updates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading update data: {e}")
        
        # Return default data if loading fails
        return {
            'last_check': None,
            'last_version': None,
            'update_available': False,
            'update_data': {}
        }
    
    def _save_data(self, data: Dict[str, Any]) -> bool:
        """Save update data to JSON file."""
        try:
            with open(self.updates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving update data: {e}")
            return False
    
    def get_last_check(self) -> Optional[datetime]:
        """Get the timestamp of the last update check."""
        data = self._load_data()
        last_check = data.get('last_check')
        return datetime.fromisoformat(last_check) if last_check else None
    
    def get_last_version(self) -> Optional[str]:
        """Get the last known version from the update data."""
        data = self._load_data()
        return data.get('last_version')
    
    def is_update_available(self) -> bool:
        """Check if an update is available based on stored data."""
        data = self._load_data()
        return data.get('update_available', False)
    
    def get_update_data(self) -> Dict[str, Any]:
        """Get the stored update data."""
        data = self._load_data()
        return data.get('update_data', {})
    
    def save_update_check(self, version: str, update_available: bool, update_data: Dict[str, Any] = None) -> bool:
        """Save the results of an update check.
        
        Args:
            version: The current version of the application
            update_available: Whether an update is available
            update_data: Additional data about the update
            
        Returns:
            bool: True if the data was saved successfully
        """
        data = {
            'last_check': datetime.now().isoformat(),
            'last_version': version,
            'update_available': update_available,
            'update_data': update_data or {}
        }
        return self._save_data(data)


class UpdateChecker(QObject):
    """Handles checking for application updates."""
    
    update_available = Signal(dict)
    no_update = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, language_manager: Optional[LanguageManager] = None, config_dir: str = "config"):
        """Initialize the update checker.
        
        Args:
            language_manager: Optional language manager for translations
            config_dir: Directory where update data will be stored
        """
        super().__init__()
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
        self.data_manager = UpdateDataManager(config_dir)
    
    def should_check_for_updates(self, current_version: str, check_interval_days: int = 1) -> bool:
        """Check if we should check for updates based on the last check time.
        
        Args:
            current_version: Current version of the application
            check_interval_days: Minimum days between update checks
            
        Returns:
            bool: True if we should check for updates
        """
        last_check = self.data_manager.get_last_check()
        if not last_check:
            return True
            
        # Check if enough time has passed since the last check
        time_since_last_check = datetime.now() - last_check
        return time_since_last_check >= timedelta(days=check_interval_days)
    
    def check_for_updates(self, current_version: str, force: bool = False) -> bool:
        """Check for updates on GitHub.
        
        Args:
            current_version: Current version of the application
            force: If True, check for updates even if recently checked
            
        Returns:
            bool: True if the check was performed (not skipped)
        """
        if not force and not self.should_check_for_updates(current_version):
            logger.debug("Skipping update check - recently checked")
            return False
            
        try:
            # Replace with your GitHub repository URL
            repo_url = "https://api.github.com/repos/Nsfr750/PDF_Finder/releases/latest"
            response = requests.get(repo_url, timeout=10)
            response.raise_for_status()
            
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            
            update_data = {
                'version': latest_version,
                'release_notes': latest_release.get('body', self.tr("updates.no_release_notes", "No release notes available.")),
                'url': latest_release.get('html_url', ''),
                'published_at': latest_release.get('published_at', '')
            }
            
            is_update_available = version.parse(latest_version) > version.parse(current_version)
            
            # Save the update check results
            self.data_manager.save_update_check(
                version=current_version,
                update_available=is_update_available,
                update_data=update_data if is_update_available else {}
            )
            
            if is_update_available:
                self.update_available.emit(update_data)
            else:
                self.no_update.emit()
                
            return True
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error checking for updates: {error_msg}")
            self.error_occurred.emit(error_msg)
            return False


class UpdateDialog(QDialog):
    def __init__(self, current_version, language_manager=None, config_dir: str = "config", parent=None):
        super().__init__(parent)
        self.current_version = current_version
        self.latest_version = None
        self.update_url = ""
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
        self.config_dir = config_dir
        
        self.setWindowTitle(self.tr("updates.window_title", "Check for Updates"))
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel(self.tr("updates.checking", "Checking for updates..."))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        
        self.download_btn = QPushButton(self.tr("updates.buttons.download", "Download Update"))
        self.download_btn.clicked.connect(self.download_update)
        self.download_btn.setVisible(False)
        
        self.close_btn = QPushButton(self.tr("common.close", "Close"))
        self.close_btn.clicked.connect(self.accept)
        
        self.button_box.addStretch()
        self.button_box.addWidget(self.download_btn)
        self.button_box.addWidget(self.close_btn)
        
        layout.addLayout(self.button_box)
        
        # Initialize the data manager with the config directory
        self.data_manager = UpdateDataManager(self.config_dir)
        
        # Check if we already know about an available update
        if self.data_manager.is_update_available():
            update_data = self.data_manager.get_update_data()
            self.show_update_available(update_data)
        else:
            # Check for updates in the background
            self.check_updates()
    
    def check_updates(self):
        """Start the update check in a separate thread."""
        self.thread = QThread()
        self.checker = UpdateChecker(self.language_manager)
        self.checker.moveToThread(self.thread)
        
        self.thread.started.connect(
            lambda: self.checker.check_for_updates(self.current_version)
        )
        
        self.checker.update_available.connect(self.show_update_available)
        self.checker.no_update.connect(self.show_no_updates)
        self.checker.error_occurred.connect(self.show_error)
        
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
    
    def show_update_available(self, update_data):
        """Show that an update is available."""
        self.latest_version = update_data['version']
        self.update_url = update_data.get('url', '')
        
        self.status_label.setText(
            self.tr(
                "updates.update_available", 
                "Version {latest_version} is available! (Current: {current_version})"
            ).format(
                latest_version=self.latest_version,
                current_version=self.current_version
            )
        )
        
        # Use raw string for HTML content to avoid issues with backslashes
        whats_new = self.tr('updates.whats_new', 'What\'s New in v')
        html_content = (
            f'<h3>{whats_new}{self.latest_version}</h3>'
            f'<pre>{update_data["release_notes"]}</pre>'
        )
        self.release_notes.setHtml(html_content)
        self.release_notes.setVisible(True)
        
        self.download_btn.setVisible(True)
        self.progress.setVisible(False)
    
    def show_no_updates(self):
        """Show that no updates are available."""
        self.status_label.setText(
            self.tr(
                "updates.no_updates", 
                "You're using the latest version ({current_version})."
            ).format(current_version=self.current_version)
        )
        self.progress.setVisible(False)
    
    def show_error(self, error_msg):
        """Show an error message."""
        self.status_label.setText(
            self.tr(
                "updates.error_checking", 
                "Error checking for updates: {error_msg}"
            ).format(error_msg=error_msg)
        )
        self.progress.setVisible(False)
    
    def download_update(self):
        """Open the download URL in the default web browser."""
        if self.update_url:
            QDesktopServices.openUrl(QUrl(self.update_url))
        self.accept()
