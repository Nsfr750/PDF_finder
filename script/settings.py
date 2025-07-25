"""
Settings management for PDF Duplicate Finder.
"""
import os
import json
import logging
from pathlib import Path
from PyQt6.QtCore import QByteArray

logger = logging.getLogger('PDFDuplicateFinder.Settings')

class SettingsManager:
    """Manages application settings and preferences using JSON storage."""
    
    def __init__(self, app_name="PDFDuplicateFinder"):
        """Initialize the settings manager.
        
        Args:
            app_name (str): Application name used for config directory
        """
        # Set up paths
        self.app_name = app_name
        self.config_dir = Path.home() / '.config' / app_name
        self.settings_file = self.config_dir / 'settings.json'
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize settings
        self.window_geometry = QByteArray()
        self.window_state = QByteArray()
        self.app_settings = {}
        self.recent_files = []
        self.recent_folders = []
        
        # Load settings
        self.load_settings()
    
    def _load_json(self, file_path):
        """Load data from a JSON file."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
        return {}
    
    def _save_json(self, file_path, data):
        """Save data to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {file_path}: {e}")
            return False
    
    def load_settings(self):
        """Load application settings from JSON file."""
        try:
            # Load settings from file
            settings_data = self._load_json(self.settings_file)
            
            # Load window geometry and state
            if 'window_geometry' in settings_data:
                self.window_geometry = QByteArray.fromBase64(
                    settings_data['window_geometry'].encode()
                )
            if 'window_state' in settings_data:
                self.window_state = QByteArray.fromBase64(
                    settings_data['window_state'].encode()
                )
            
            # Load application settings with defaults
            self.app_settings = settings_data.get('app_settings', {})
            
            # Set default values for required settings
            defaults = {
                'theme': 'dark',
                'language': 'en',
                'last_scan_directory': os.path.expanduser('~'),
                'check_updates': True,
                'show_hidden': False,
                'min_file_size': 1024,  # 1KB
                'max_file_size': 1024 * 1024 * 1024,  # 1GB
                'compare_method': 'content',
                'thread_count': 4,
                'auto_save_results': True,
                'auto_load_last': True,
                'scan_recursive': True,
                'hash_size': 8,
                'threshold': 5
            }
            
            # Apply defaults for any missing settings
            for key, default_value in defaults.items():
                if key not in self.app_settings:
                    self.app_settings[key] = default_value
            
            # Load recent files and folders
            self.recent_files = settings_data.get('recent_files', [])
            self.recent_folders = settings_data.get('recent_folders', [])
            
            logger.info(f"Settings loaded from {self.settings_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self.reset_to_defaults()
            return False
    
    def save_settings(self):
        """Save application settings to JSON file."""
        try:
            # Prepare data for JSON serialization
            settings_data = {
                'app_name': self.app_name,
                'app_settings': self.app_settings,
                'recent_files': self.recent_files,
                'recent_folders': self.recent_folders,
                'window_geometry': self.window_geometry.toBase64().data().decode(),
                'window_state': self.window_state.toBase64().data().decode()
            }
            
            # Save to file
            if self._save_json(self.settings_file, settings_data):
                logger.info(f"Settings saved to {self.settings_file}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset settings to default values."""
        self.app_settings = {
            'theme': 'dark',
            'language': 'en',
            'last_scan_directory': os.path.expanduser('~'),
            'check_updates': True,
            'show_hidden': False,
            'min_file_size': 1024,  # 1KB
            'max_file_size': 1024 * 1024 * 1024,  # 1GB
            'compare_method': 'content',
            'thread_count': 4,
            'auto_save_results': True,
            'auto_load_last': True,
            'scan_recursive': True,
            'hash_size': 8,
            'threshold': 5
        }
        self.recent_files = []
        self.recent_folders = []
        self.window_geometry = QByteArray()
        self.window_state = QByteArray()
        self.save_settings()
    
    def get(self, key, default=None):
        """Get a setting value by key."""
        return self.app_settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value by key and save to file."""
        self.app_settings[key] = value
        return self.save_settings()
    
    def add_recent_file(self, file_path):
        """Add a file to recent files list."""
        # Convert to string in case a Path object is passed
        file_path = str(file_path)
        
        # Remove if already exists
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        # Add to beginning of list
        self.recent_files.insert(0, file_path)
        
        # Keep only the last 10 files
        self.recent_files = self.recent_files[:10]
        
        return self.save_settings()
    
    def add_recent_folder(self, folder_path):
        """Add a folder to recent folders list."""
        # Convert to string in case a Path object is passed
        folder_path = str(folder_path)
        
        # Remove if already exists
        if folder_path in self.recent_folders:
            self.recent_folders.remove(folder_path)
        
        # Add to beginning of list
        self.recent_folders.insert(0, folder_path)
        
        # Keep only the last 10 folders
        self.recent_folders = self.recent_folders[:10]
        
        return self.save_settings()

# Singleton instance
settings_manager = SettingsManager()
