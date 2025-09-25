"""
Application settings management for PDF Duplicate Finder using JSON storage.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from script.lang.lang_manager import SimpleLanguageManager
logger = logging.getLogger('settings')

class AppSettings:
    """Manage application settings with JSON file storage."""
    
    def __init__(self, config_dir: str = "config", config_file: str = "settings.json"):
        # Get the project root directory (go up from script/utils to project root)
        project_root = Path(__file__).parent.parent.parent
        self._config_path = project_root / config_dir / config_file
        self._data: Dict[str, Any] = {}
        self._load_settings()
    
    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_settings(self) -> None:
        """Load settings from JSON file."""
        try:
            if self._config_path.exists():
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self._data = {}
    
    def _save_settings(self) -> None:
        """Save settings to JSON file."""
        try:
            self._ensure_config_dir()
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by dot notation key."""
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
        
    def get_language(self) -> str:
        """Get the current language setting."""
        return self.get('language', 'en')
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value by dot notation key."""
        keys = key.split('.')
        current = self._data
        
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self._save_settings()
    
    # Convenience methods
    def get_window_geometry(self) -> Optional[bytes]:
        """Get saved window geometry."""
        geometry = self.get('window.geometry')
        return bytes.fromhex(geometry) if isinstance(geometry, str) else None
    
    def set_window_geometry(self, geometry: Union[bytes, str, None]) -> None:
        """Save window geometry.
        
        Args:
            geometry: Either a bytes object or a hex string
        """
        if geometry is None:
            return
            
        if isinstance(geometry, bytes):
            self.set('window.geometry', geometry.hex())
        elif isinstance(geometry, str):
            # If it's already a hex string, store it directly
            self.set('window.geometry', geometry)
    
    def get_window_state(self) -> Optional[bytes]:
        """Get saved window state."""
        state = self.get('window.state')
        return bytes.fromhex(state) if isinstance(state, str) else None
    
    def set_window_state(self, state: Union[bytes, str, None]) -> None:
        """Save window state.
        
        Args:
            state: Either a bytes object or a hex string
        """
        if state is None:
            return
            
        if isinstance(state, bytes):
            self.set('window.state', state.hex())
        elif isinstance(state, str):
            # If it's already a hex string, store it directly
            self.set('window.state', state)
    
    def get_language(self) -> str:
        """Get saved language setting."""
        return self.get('application.language', 'en')
    
    def set_language(self, language_code: str) -> None:
        """Save language setting."""
        self.set('application.language', language_code)

# Global settings instance
settings = AppSettings()
