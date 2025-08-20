"""
Language Manager for handling application translations using JSON files.
"""
import json
import os
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class LanguageManager(QObject):
    """Manages application translations loaded from JSON files."""
    
    # Signal emitted when the language is changed
    language_changed = pyqtSignal(str)
    
    def __init__(self, default_lang: str = 'en', parent: Optional[QObject] = None):
        """Initialize the language manager.
        
        Args:
            default_lang: Default language code (e.g., 'en', 'it')
            parent: Optional parent QObject
        """
        super().__init__(parent)
        self.translations: Dict[str, Dict[str, str]] = {}
        self._current_lang = default_lang
        self.default_lang = default_lang
        self.lang_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang')
        
        # Load translations
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load all available translations from JSON files."""
        try:
            # Look for all JSON files in the lang directory
            for file in Path(self.lang_dir).glob('*.json'):
                lang_code = file.stem
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    logger.info(f"Loaded translations for language: {lang_code}")
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error loading {file}: {e}")
            
            if not self.translations:
                logger.warning("No translation files found in the lang directory")
                
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
    
    def set_language(self, lang_code: str) -> bool:
        """Set the current language.
        
        Args:
            lang_code: Language code to set (e.g., 'en', 'it')
            
        Returns:
            bool: True if language was set successfully, False otherwise
        """
        if lang_code in self.translations or lang_code == self.default_lang:
            self.current_lang = lang_code
            logger.info(f"Language set to: {lang_code}")
            return True
        
        logger.warning(f"Language not available: {lang_code}")
        return False
    
    def tr(self, key: str, default: Optional[str] = None) -> str:
        """Get a translated string for the given key.
        
        Args:
            key: Translation key in format 'context.key'
            default: Default value to return if key is not found
            
        Returns:
            str: Translated string or the key if not found
        """
        if not key:
            return default or ''
            
        # Try current language first
        if self.current_lang in self.translations:
            try:
                # Handle nested keys (e.g., 'dialog.error')
                value = self.translations[self.current_lang]
                for k in key.split('.'):
                    value = value[k]
                return value
            except (KeyError, TypeError):
                pass
        
        # Fall back to default language if different from current
        if (self.current_lang != self.default_lang and 
            self.default_lang in self.translations):
            try:
                value = self.translations[self.default_lang]
                for k in key.split('.'):
                    value = value[k]
                return value
            except (KeyError, TypeError):
                pass
        
        # Return the default value or the key itself
        return default or key
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get a dictionary of available language codes and their display names.
        
        Returns:
            Dict[str, str]: Dictionary mapping language codes to display names
        """
        languages = {}
        for lang_code in self.translations:
            try:
                languages[lang_code] = self.translations[lang_code].get('language.name', lang_code)
            except (AttributeError, TypeError):
                languages[lang_code] = lang_code
        return languages
    
    @property
    def current_lang(self) -> str:
        """Get the current language code.
        
        Returns:
            str: Current language code
        """
        return self._current_lang
        
    @current_lang.setter
    def current_lang(self, lang: str) -> None:
        """Set the current language and emit language_changed signal.
        
        Args:
            lang: Language code to set
        """
        if lang != self._current_lang and lang in self.translations:
            self._current_lang = lang
            self.language_changed.emit(lang)
    
    def get_current_language(self) -> str:
        """Get the current language code.
        
        Returns:
            str: Current language code (e.g., 'en', 'it')
        """
        return self._current_lang
