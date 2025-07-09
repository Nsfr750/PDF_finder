"""
Internationalization support for PDF Duplicate Finder.
"""
import os
from pathlib import Path
from PyQt6.QtCore import QCoreApplication, QLocale, QTranslator, QLibraryInfo, Qt, pyqtSignal as Signal, QObject

class LanguageNotifier(QObject):
    """Simple class to handle language change notifications."""
    language_changed = Signal(str)
    
    def emit_language_changed(self, language_code):
        """Emit the language_changed signal."""
        self.language_changed.emit(language_code)

class Translator:
    def __init__(self, app):
        self.app = app
        self.qt_translator = QTranslator()
        self.app_translator = QTranslator()
        self.current_language = 'en'  # Default language
        self.notifier = LanguageNotifier()
        
        # Load translations
        self.load_language('en')  # Load English by default
        
    def available_languages(self):
        """Return a list of available language codes."""
        return ['en', 'it']
    
    def language_name(self, code):
        """Return the display name of a language given its code."""
        names = {
            'en': 'English',
            'it': 'Italiano'
        }
        return names.get(code, code)
    
    def load_language(self, language_code: str):
        """
        Load translations for the specified language.
        
        Args:
            language_code: Two-letter language code (e.g., 'en', 'it')
        """
        # Remove old translations
        QCoreApplication.removeTranslator(self.qt_translator)
        QCoreApplication.removeTranslator(self.app_translator)
        
        # Load Qt translations
        qt_translations_dir = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        if self.qt_translator.load(f"qtbase_{language_code}", qt_translations_dir):
            QCoreApplication.installTranslator(self.qt_translator)
        
        # Load application translations
        translations_dir = Path(__file__).parent / 'translations'
        if self.app_translator.load(f"pdf_finder_{language_code}", str(translations_dir)):
            QCoreApplication.installTranslator(self.app_translator)
        
        self.current_language = language_code
        
        # Update the application's layout direction
        if language_code in ['ar', 'he', 'fa']:  # RTL languages
            self.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            
        # Notify the application that the language has changed
        self.notifier.emit_language_changed(language_code)
