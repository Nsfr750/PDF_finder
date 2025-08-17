"""
Language management module for PDF_Finder.

This module provides the LanguageManager class which handles application
internationalization and translation management.
"""

from typing import Dict, List, Optional, Any, Union
from PyQt6.QtCore import QObject, pyqtSignal, QSettings, QLocale, QCoreApplication, QTranslator, QLibraryInfo, Qt
from script.logger import get_logger
import logging
from pathlib import Path


# Configure logging
logger = get_logger(__name__)

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
        
        # Initialize translations dictionary first
        self._translations = {}
        self._available_languages = {}
        
        # Store the QApplication instance
        self.app = app
        
        # Initialize settings
        self.settings = QSettings("PDF_Finder", "PDF_Finder")
        
        # Load current language from settings or use default
        self._current_lang = self.settings.value("language", default_lang)
        
        # Initialize Qt translators
        self.qt_translator = QTranslator()
        self.app_translator = QTranslator()
        
        # Load translations
        self._load_translations()
        
        # Set up available languages based on what translations are available
        self._setup_available_languages()
        
        # If current language is not available, fall back to default
        if self._current_lang not in self._available_languages:
            logger.warning(
                "Language '%s' not available, falling back to '%s'",
                self._current_lang, default_lang
            )
            self._current_lang = default_lang
        
        # Load the current language
        self._load_language(self._current_lang)
            
        logger.info("LanguageManager initialized with language: %s", self._current_lang)

    def _setup_available_languages(self):
        """Set up the available languages based on loaded translations."""
        # Define language names (using direct strings to avoid recursion)
        language_names = {
            "en": "English",
            "it": "Italiano",
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
    def available_languages(self) -> dict:
        """
        Get a dictionary of available languages.
        
        Returns:
            dict: Dictionary mapping language codes to language names
        """
        return self._available_languages

    def _load_translations(self):
        """Load translations from the translations module."""
        try:
            from . import translations
            
            # Get the TRANSLATIONS dictionary from the module
            if hasattr(translations, 'TRANSLATIONS') and isinstance(translations.TRANSLATIONS, dict):
                self._translations = translations.TRANSLATIONS
                logger.debug(f"Loaded translations for languages: {list(self._translations.keys())}")
            else:
                logger.warning("No TRANSLATIONS dictionary found in translations module")
                self._translations = {}
            
            # Ensure English is always available as a fallback
            if "en" not in self._translations:
                logger.warning("English translations not found, using fallback")
                self._translations["en"] = {
                    "menu": {
                        "file": "&File",
                        "open": "&Open Folder...",
                        "save_results": "&Save Results",
                        "load_results": "&Load Results...",
                        "settings": "&Settings...",
                        "exit": "E&xit",
                        "view": "&View",
                        "view_log": "View &Log",
                        "pdf_viewer": "PDF Viewer",
                        "language": "&Language",
                        "tools": "&Tools",
                        "check_updates": "Check for &Updates",
                        "help": "&Help",
                        "documentation": "&Documentation",
                        "markdown_docs": "&Markdown Documentation",
                        "sponsor": "&Sponsor...",
                        "about": "&About"
                    },
                    "language": {
                        "english": "English",
                        "italian": "Italiano"
                    }
                }
                
            # Log available translations for debugging
            for lang_code, translations in self._translations.items():
                logger.debug(f"Language {lang_code} has {len(translations)} translation keys")
                
        except ImportError as e:
            logger.error(f"Error importing translations module: {e}")
            # Fallback to English if translations module is not available
            self._translations["en"] = {
                "menu": {
                    "file": "&File",
                    "open": "&Open Folder...",
                    "save_results": "&Save Results",
                    "load_results": "&Load Results...",
                    "settings": "&Settings...",
                    "exit": "E&xit",
                    "view": "&View",
                    "view_log": "View &Log",
                    "pdf_viewer": "PDF Viewer",
                    "language": "&Language",
                    "tools": "&Tools",
                    "check_updates": "Check for &Updates",
                    "help": "&Help",
                    "documentation": "&Documentation",
                    "markdown_docs": "&Markdown Documentation",
                    "sponsor": "&Sponsor...",
                    "about": "&About"
                },
                "language": {
                    "english": "English",
                    "italian": "Italiano"
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error loading translations: {e}")
            # Ensure we at least have English translations
            if "en" not in self._translations:
                self._translations["en"] = {
                    "menu": {
                        "file": "&File",
                        "open": "&Open Folder...",
                        "save_results": "&Save Results",
                        "load_results": "&Load Results...",
                        "settings": "&Settings...",
                        "exit": "E&xit"
                    }
                }

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
        Load translations for the specified language.
        
        Args:
            language_code: Language code to load (e.g., 'en', 'it')
        """
        if not self.app:
            return True  # Return True for headless mode
            
        logger.debug(f"Loading language: {language_code}")
        
        # Remove old translators
        QCoreApplication.removeTranslator(self.qt_translator)
        QCoreApplication.removeTranslator(self.app_translator)
        
        # Load Qt translations if available
        try:
            qt_translations_dir = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
            if self.qt_translator.load(f"qtbase_{language_code}", qt_translations_dir):
                QCoreApplication.installTranslator(self.qt_translator)
                logger.debug(f"Loaded Qt translations for {language_code}")
            else:
                logger.debug(f"No Qt translations found for {language_code} in {qt_translations_dir}")
        except Exception as e:
            logger.warning(f"Could not load Qt translations: {e}")
        
        # Update the application's layout direction for RTL languages
        if language_code in ['ar', 'he', 'fa']:  # RTL languages
            self.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft) 
        else:
            self.app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            
        # Force a UI update to apply translations
        if hasattr(self.app, 'allWidgets'):
            for widget in self.app.allWidgets():
                try:
                    if hasattr(widget, 'changeEvent'):
                        widget.changeEvent(None)
                except Exception as e:
                    logger.debug(f"Error updating widget: {e}")
        
        logger.debug(f"Language loaded: {language_code}")
        return True

    def set_language(self, language_code: str) -> bool:
        """
        Set the application language.
        
        Args:
            language_code: Language code to set (e.g., 'en', 'it')
            
        Returns:
            bool: True if language was changed successfully, False otherwise
        """
        if language_code not in self._available_languages:
            logger.warning(f"Language '{language_code}' is not available")
            return False
            
        if language_code == self._current_lang:
            return True  # Already using this language
            
        logger.debug(f"Attempting to change language to: {language_code}")
            
        # Load the new language
        if self._load_language(language_code):
            self._current_lang = language_code
            self.settings.setValue("language", language_code)
            
            # Emit the language changed signal
            logger.debug(f"Emitting language_changed signal for {language_code}")
            self.language_changed.emit(language_code)
            
            # Force update of all widgets
            self._update_all_widgets()
            
            logger.info(f"Successfully changed language to: {language_code}")
            return True
            
        return False
        
    def _update_all_widgets(self):
        """Force update of all widgets to apply new translations."""
        if not hasattr(self, 'app') or not self.app:
            return
            
        # Update all top-level widgets
        for widget in self.app.topLevelWidgets():
            try:
                # If widget has a retranslate_ui method, call it
                if hasattr(widget, 'retranslate_ui'):
                    widget.retranslate_ui()
                # Otherwise, trigger a change event
                elif hasattr(widget, 'changeEvent'):
                    widget.changeEvent(None)
            except Exception as e:
                logger.debug(f"Error updating widget {widget}: {e}")

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
            # For language manager's own use, don't try to translate if not initialized
            if not hasattr(self, '_current_lang') or not hasattr(self, '_translations'):
                return default_text
                
            # Split the key into parts (e.g., 'menu.file.open' -> ['menu', 'file', 'open'])
            parts = key.split('.')
            
            # Start with the current language's translations
            current = self._translations.get(self._current_lang, {})
            
            # Navigate through the nested dictionaries to find the translation
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    # If any part of the key is not found, return the default text
                    return default_text
            
            # If we found a string, return it; otherwise return the default
            return current if isinstance(current, str) else default_text
            
        except Exception as e:
            logger.error("Error translating key '%s': %s", key, str(e))
            return default_text
