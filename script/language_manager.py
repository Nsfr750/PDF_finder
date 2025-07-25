"""
Language management module for PDF_Finder.

This module provides the LanguageManager class which handles application
internationalization and translation management.
"""

from typing import Dict, List, Optional, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal, QSettings, QLocale, QCoreApplication, QTranslator, QLibraryInfo, Qt
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class LanguageManager(QObject):
    """
    Manages application language settings and translations.
    
    This class handles loading translations, changing languages at runtime,
    and providing translated strings to the application.
    """

    # Signal emitted when language changes
    language_changed = pyqtSignal(str)  # language_code

    def __init__(self, app=None, default_lang: str = "en"):
        """
        Initialize the language manager.

        Args:
            app: The QApplication instance (optional)
            default_lang: Default language code (e.g., 'en', 'it')
        """
        super().__init__()
        logger.debug(self.tr(
            "language_manager.initializing", 
            "Initializing LanguageManager..."
        ))
        
        # Store the QApplication instance
        self.app = app
        
        # Initialize settings
        self.settings = QSettings("PDF_Finder", "PDF_Finder")
        logger.debug(self.tr(
            "language_manager.settings_file", 
            "Settings file: {file}"
        ).format(file=self.settings.fileName()))
        
        # Load current language from settings or use default
        self._current_lang = self.settings.value("language", default_lang)
        logger.debug(self.tr(
            "language_manager.current_language", 
            "Current language from settings: {lang}"
        ).format(lang=self._current_lang))
        
        # Initialize Qt translators
        self.qt_translator = QTranslator()
        self.app_translator = QTranslator()
        
        # Initialize translations dictionary
        self._translations = {}
        self._available_languages = {}
        
        # Load translations
        self._load_translations()
        
        # Set up available languages based on what translations are available
        self._setup_available_languages()
        
        # If current language is not available, fall back to default
        if self._current_lang not in self._available_languages:
            logger.warning(
                self.tr(
                    "language_manager.language_not_available", 
                    "Language '{lang}' not available, falling back to '{default_lang}'"
                ).format(lang=self._current_lang, default_lang=default_lang)
            )
            self._current_lang = default_lang
        
        # Load the current language
        self._load_language(self._current_lang)
            
        logger.info(self.tr(
            "language_manager.initialized", 
            "LanguageManager initialized with language: {lang}"
        ).format(lang=self._current_lang))

    def _setup_available_languages(self):
        """Set up the available languages based on loaded translations."""
        # Define language names
        language_names = {
            "en": self.tr("language.english", "English"),
            "it": self.tr("language.italian", "Italiano"),
            # Add more languages here as they become available
        }
        
        # Only include languages that have translations loaded
        available_codes = set(self._translations.keys())
        self._available_languages = {
            code: name 
            for code, name in language_names.items()
            if code in available_codes
        }

    @property
    def current_language(self) -> str:
        """
        Get the current language code.
        
        Returns:
            str: Current language code (e.g., 'en', 'it')
        """
        return self._current_lang

    @property
    def available_languages(self) -> Dict[str, str]:
        """
        Get a dictionary of available language codes and their display names.
        
        Returns:
            Dict[str, str]: Dictionary mapping language codes to display names
        """
        return self._available_languages.copy()

    def _load_translations(self):
        """Load translations from the translations module."""
        try:
            from .translation import TRANSLATIONS, HELP_TRANSLATIONS
            
            # Load main translations
            self._translations = TRANSLATIONS
            logger.debug(self.tr(
                "language_manager.loaded_translations", 
                "Loaded main translations for languages: {languages}"
            ).format(languages=", ".join(TRANSLATIONS.keys()) if TRANSLATIONS else self.tr("common.none", "none")))
            
            # Merge help translations
            for lang, translations in HELP_TRANSLATIONS.items():
                if lang not in self._translations:
                    self._translations[lang] = {}
                self._update_dict_recursive(self._translations[lang], translations)
                
            logger.debug(self.tr(
                "language_manager.merged_help_translations", 
                "Merged help translations for languages: {languages}"
            ).format(languages=", ".join(HELP_TRANSLATIONS.keys()) if HELP_TRANSLATIONS else self.tr("common.none", "none")))
            
        except ImportError as e:
            logger.error(self.tr(
                "language_manager.load_translations_error", 
                "Failed to load translations: {error}"
            ).format(error=str(e)))
            self._translations = {"en": {}}  # Fallback to empty English translations

    def _update_dict_recursive(self, d: Dict, u: Dict) -> Dict:
        """Recursively update a dictionary."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_dict_recursive(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def _load_language(self, language_code: str):
        """
        Load Qt translations for the specified language.
        
        Args:
            language_code: Language code to load (e.g., 'en', 'it')
        """
        if not self.app:
            return
            
        # Remove old translators
        QCoreApplication.removeTranslator(self.qt_translator)
        QCoreApplication.removeTranslator(self.app_translator)
        
        # Load Qt translations
        qt_translations_dir = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        if self.qt_translator.load(f"qtbase_{language_code}", qt_translations_dir):
            QCoreApplication.installTranslator(self.qt_translator)
        
        # Load application translations from .qm files if available
        translations_dir = Path(__file__).parent / 'translations'
        if self.app_translator.load(f"pdf_finder_{language_code}", str(translations_dir)):
            QCoreApplication.installTranslator(self.app_translator)
        
        # Update the application's layout direction for RTL languages
        if language_code in ['ar', 'he', 'fa']:  # RTL languages
            self.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def set_language(self, lang_code: str) -> bool:
        """
        Set the application language.

        Args:
            lang_code: Language code to set (e.g., 'en', 'it')

        Returns:
            bool: True if language was changed, False otherwise
        """
        if lang_code not in self._available_languages:
            logger.warning(self.tr(
                "language_manager.unsupported_language", 
                "Attempted to set unsupported language: {lang}"
            ).format(lang=lang_code))
            return False

        if lang_code != self._current_lang:
            logger.info(self.tr(
                "language_manager.language_changing", 
                "Changing language from {old_lang} to {new_lang}"
            ).format(old_lang=self._current_lang, new_lang=lang_code))
            
            self._current_lang = lang_code
            self.settings.setValue("language", lang_code)
            
            # Load Qt translations
            self._load_language(lang_code)
            
            # Notify the application that the language has changed
            self.language_changed.emit(lang_code)
            
            return True
            
        return False

    def tr(self, key: str, default_text: str = "") -> str:
        """
        Translate a string using the current language.
        
        Args:
            key: The translation key (e.g., 'menu.file.open')
            default_text: Default text to return if translation is not found
            
        Returns:
            str: The translated string, or the default text if not found
        """
        if not key:
            return default_text
            
        try:
            # Split the key into parts (e.g., 'menu.file.open' -> ['menu', 'file', 'open'])
            parts = key.split('.')
            
            # Start with the current language's translations
            current = self._translations.get(self._current_lang, {})
            
            # Navigate through the nested dictionaries to find the translation
            for part in parts:
                if part in current:
                    current = current[part]
                else:
                    # If any part of the key is not found, return the default text
                    return default_text
            
            # If we found a string, return it; otherwise return the default
            return current if isinstance(current, str) else default_text
            
        except Exception as e:
            logger.error(self.tr(
                "language_manager.translation_error", 
                "Error translating key '{key}': {error}"
            ).format(key=key, error=str(e)))
            return default_text
