"""
Logging configuration for PDF Duplicate Finder.
"""
import os
import logging
import time
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication, QTranslator

# Import language manager if available
try:
    from script.language_manager import LanguageManager
    _HAS_LANGUAGE_MANAGER = True
except ImportError:
    _HAS_LANGUAGE_MANAGER = False

# Default translations for logger messages
TRANSLATIONS = {
    'en': {
        'log.app_started': '{app_name} started',
        'log.directory': 'Log directory: {path}',
        'log.level': 'Log level: {level}',
    },
    'it': {
        'log.app_started': '{app_name} avviato',
        'log.directory': 'Directory di log: {path}',
        'log.level': 'Livello di log: {level}',
    },
    # Add more languages as needed
}

def tr(key: str, default: str, language: str = 'en') -> str:
    """
    Translate a string using the available translations.
    
    Args:
        key: Translation key
        default: Default text if translation not found
        language: Language code (e.g., 'en', 'it')
        
    Returns:
        Translated string or default if not found
    """
    if _HAS_LANGUAGE_MANAGER:
        try:
            # Try to use the application's language manager if available
            app = QCoreApplication.instance()
            if hasattr(app, 'language_manager'):
                return app.language_manager.tr(key, default)
        except Exception as e:
            logging.getLogger('PDFDuplicateFinder.Logger').warning(
                f'Error getting translation for {key}: {str(e)}',
                exc_info=True
            )
    
    # Fall back to built-in translations
    return TRANSLATIONS.get(language, {}).get(key, default)

def setup_logging(app_name='PDFDuplicateFinder', log_level=logging.INFO, language='en'):
    """
    Configure the logging system for the application with daily log rotation.
    
    Args:
        app_name (str): Name of the application for log file naming
        log_level (int): Logging level (default: logging.INFO)
        language (str): Language code for log messages (default: 'en')
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate log filename with date
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_base = app_name.lower().replace(" ", "_")
    log_filename = f"{log_base}-{current_date}.log"
    
    # Create a custom formatter
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Configure the root logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    
    # Add file handler with daily rotation
    log_file = log_dir / log_filename
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',  # Rotate at midnight
        interval=1,       # Create new file daily
        backupCount=30,   # Keep logs for 30 days
        encoding='utf-8',
        delay=False
    )
    file_handler.suffix = "%Y-%m-%d"  # Add date to rotated log files
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log the start of the application with translated messages
    logger.info("=" * 80)
    logger.info(tr('log.app_started', '{app_name} started', language).format(app_name=app_name))
    logger.info(tr('log.directory', 'Log directory: {path}', language).format(path=log_dir.absolute()))
    logger.info(tr('log.level', 'Log level: {level}', language).format(level=logging.getLevelName(log_level)))
    
    return logger

# Create a module-level logger instance
logger = logging.getLogger('PDFDuplicateFinder')

# Configure logging when module is imported (optional)
# setup_logging()  # Uncomment if you want logging configured on import
