from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTextBrowser)
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
        
        self.setWindowTitle(self.tr("updates.window_title", "Software Update"))
        self.setMinimumSize(600, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Version info section
        version_layout = QVBoxLayout()
        
        # Current version
        current_layout = QHBoxLayout()
        current_label = QLabel(self.tr("updates.current_version", "Current Version:"))
        current_label.setStyleSheet("font-weight: bold;")
        self.current_version_label = QLabel(current_version)
        current_layout.addWidget(current_label, 0, Qt.AlignmentFlag.AlignLeft)
        current_layout.addWidget(self.current_version_label, 0, Qt.AlignmentFlag.AlignLeft)
        current_layout.addStretch()
        version_layout.addLayout(current_layout)
        
        # Latest version
        self.latest_layout = QHBoxLayout()
        latest_label = QLabel(self.tr("updates.latest_version", "Latest Version:"))
        latest_label.setStyleSheet("font-weight: bold;")
        self.latest_version_label = QLabel(self.tr("updates.checking", "Checking..."))
        self.latest_layout.addWidget(latest_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.latest_layout.addWidget(self.latest_version_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.latest_layout.addStretch()
        version_layout.addLayout(self.latest_layout)
        
        # Status message
        self.status_label = QLabel(self.tr("updates.checking", "Checking for updates..."))
        self.status_label.setWordWrap(True)
        version_layout.addWidget(self.status_label)
        
        layout.addLayout(version_layout)
        
        # Release notes section
        notes_group = QVBoxLayout()
        notes_label = QLabel(self.tr("updates.release_notes", "<b>Release Notes:</b>"))
        notes_label.setTextFormat(Qt.TextFormat.RichText)
        notes_group.addWidget(notes_label)
        
        # Release notes section (initially hidden)
        self.release_notes = QTextBrowser()
        self.release_notes.setOpenExternalLinks(True)
        self.release_notes.setReadOnly(True)
        self.release_notes.setVisible(False)
        self.release_notes.setMaximumHeight(150)  # Limit the height
        notes_group.addWidget(self.release_notes)
        self.notes_group = notes_group  # Store reference to show/hide later
        
        layout.addLayout(notes_group, 1)  # Add stretch factor to make this section expandable
        
        # Buttons
        self.button_box = QHBoxLayout()
        self.button_box.setSpacing(10)
        
        # Ignore button (only shown when update is available)
        self.ignore_btn = QPushButton(self.tr("updates.buttons.ignore", "Ignore This Version"))
        self.ignore_btn.clicked.connect(self.ignore_update)
        self.ignore_btn.setVisible(False)
        
        # Download button (shown when update is available)
        self.download_btn = QPushButton(self.tr("updates.buttons.download", "Download Update"))
        self.download_btn.clicked.connect(self.download_update)
        self.download_btn.setVisible(False)
        self.download_btn.setDefault(True)
        
        # Close button
        self.close_btn = QPushButton(self.tr("common.close", "Close"))
        self.close_btn.clicked.connect(self.accept)
        
        # Add buttons to layout (right-aligned)
        self.button_box.addStretch()
        self.button_box.addWidget(self.ignore_btn)
        self.button_box.addWidget(self.download_btn)
        self.button_box.addWidget(self.close_btn)
        
        layout.addLayout(self.button_box)
        
        # Initialize the data manager with the config directory
        self.data_manager = UpdateDataManager(self.config_dir)
        
        # Check for updates
        self.check_updates()
    
    def check_updates(self):
        """Start the update check in a separate thread."""
        self.thread = QThread()
        self.checker = UpdateChecker(self.language_manager, self.config_dir)
        self.checker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(
            lambda: self.checker.check_for_updates(self.current_version)
        )
        self.checker.update_available.connect(self.show_update_available)
        self.checker.no_update.connect(self.show_no_updates)
        self.checker.error_occurred.connect(self.show_error)
        
        # Clean up thread when done
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.checker.deleteLater)
        
        # Start the thread
        self.thread.start()
        
        # Show checking status
        self.status_label.setText(self.tr("updates.checking", "Checking for updates..."))
    
    def show_update_available(self, update_data):
        """Show that an update is available.
        
        Args:
            update_data: Dictionary containing update information
        """
        self.latest_version = update_data.get('version')
        self.update_url = update_data.get('html_url', '')
        
        # Update UI
        self.latest_version_label.setText(f"{self.latest_version} (Update available!)")
        self.latest_version_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        
        # Show release notes if available
        if 'body' in update_data and update_data['body']:
            # Format markdown for better display
            notes = update_data['body']
            # Convert markdown links to HTML
            import re
            notes = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', notes)
            self.release_notes.setMarkdown(notes)
            self.release_notes.setVisible(True)
            self.notes_group.setVisible(True)  # Show the notes group
        
        # Update status with formatted message
        status_text = self.tr(
            "updates.update_available", 
            f"A new version {self.latest_version} is available!"
        )
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet("color: #2e7d32;")
        
        # Show appropriate buttons
        self.download_btn.setVisible(True)
        self.ignore_btn.setVisible(True)
        self.close_btn.setText(self.tr("common.later", "Later"))
        
        # Bring window to front
        self.raise_()
        self.activateWindow()
    
    def show_no_updates(self):
        """Show that no updates are available."""
        self.latest_version_label.setText(self.current_version)
        self.latest_version_label.setStyleSheet("color: #2e7d32;")
        
        status_text = self.tr(
            "updates.up_to_date", 
            "You're using the latest version of PDF Duplicate Finder!"
        )
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet("color: #2e7d32;")
        
        # Hide release notes section when no update is available
        if hasattr(self, 'notes_group'):
            self.notes_group.setVisible(False)
        
        # Show last check time
        last_check = self.data_manager.get_last_check()
        if last_check:
            last_check_str = last_check.strftime("%Y-%m-%d %H:%M")
            self.status_label.setText(
                f"{status_text}\n" +
                self.tr("updates.last_checked", "Last checked: {0}").format(last_check_str)
            )
        
        self.close_btn.setVisible(True)
        self.close_btn.setDefault(True)
    
    def show_error(self, error_msg):
        """Show an error message."""
        self.latest_version_label.setText("-")
        self.status_label.setText(
            self.tr("updates.error", "Error checking for updates: {0}").format(error_msg)
        )
        self.status_label.setStyleSheet("color: #d32f2f;")
        self.close_btn.setVisible(True)
        self.close_btn.setDefault(True)
    
    def download_update(self):
        """Open the download URL in the default web browser."""
        if self.update_url:
            QDesktopServices.openUrl(QUrl(self.update_url))
        self.accept()
    
    def ignore_update(self):
        """Ignore this version and close the dialog."""
        if self.latest_version:
            # Save the ignored version to avoid showing the update again
            self.data_manager.save_update_check(
                version=self.current_version,
                update_available=False,  # We're ignoring this update
                update_data={
                    'ignored_version': self.latest_version,
                    'ignored_at': datetime.now().isoformat(),
                    'last_check': datetime.now().isoformat()
                }
            )
            # Show feedback
            self.status_label.setText(
                self.tr("updates.ignored", "Version {0} will be ignored.").format(self.latest_version)
            )
            self.status_label.setStyleSheet("color: #ff8f00;")
            
            # Update UI
            self.download_btn.setVisible(False)
            self.ignore_btn.setVisible(False)
            self.close_btn.setText(self.tr("common.close", "Close"))
            
            # Close after a short delay
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, self.accept)
        else:
            self.accept()
