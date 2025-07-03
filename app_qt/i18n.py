"""
Internationalization support for PDF Duplicate Finder.
"""
import os
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QLocale, QTranslator, QLibraryInfo, Qt, Signal, QObject

class LanguageNotifier(QObject):
    """Simple class to handle language change notifications."""
    language_changed = Signal()
    
    def emit_language_changed(self):
        """Emit the language_changed signal."""
        self.language_changed.emit()

class Translator:
    def __init__(self, app):
        self.app = app
        self.translator_qt = QTranslator()
        self.translator_app = QTranslator()
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
    
    def load_language(self, language_code):
        """Load the specified language."""
        # Remove old translations
        QCoreApplication.removeTranslator(self.translator_qt)
        QCoreApplication.removeTranslator(self.translator_app)
        
        # Load Qt base translations
        qt_translations_dir = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
        if self.translator_qt.load(f'qtbase_{language_code}', qt_translations_dir):
            QCoreApplication.installTranslator(self.translator_qt)
        
        # Load application translations
        translations_dir = Path(__file__).parent / 'translations'
        if self.translator_app.load(f'pdf_finder_{language_code}', str(translations_dir)):
            QCoreApplication.installTranslator(self.translator_app)
        
        self.current_language = language_code
        
        # Update the application's layout direction
        if language_code in ['ar', 'he', 'fa']:  # RTL languages
            self.app.setLayoutDirection(Qt.RightToLeft)
        else:
            self.app.setLayoutDirection(Qt.LeftToRight)
            
        # Notify the application that the language has changed
        self.notifier.emit_language_changed()
