"""
Logging configuration for PDF Duplicate Finder.

This module provides a centralized way to configure and access the application logger.
Logs are saved in the 'logs' directory with filenames in the format 'PDFDuplicateFinder_YYYY-MM-DD.log'.
"""
import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional, Union, Dict, Any

# Log levels mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logger(name: str = 'PDFDuplicateFinder', 
                log_level: Union[str, int] = 'INFO',
                log_dir: str = 'logs',
                max_bytes: int = 10 * 1024 * 1024,  # 10MB per file
                backup_count: int = 7,
                log_to_console: bool = True,
                log_to_file: bool = True) -> logging.Logger:
    """
    Configure and return a logger with the specified settings.
    
    Args:
        name: Name of the logger (default: 'PDFDuplicateFinder')
        log_level: Logging level as string ('DEBUG', 'INFO', etc.) or int (default: 'INFO')
        log_dir: Directory to store log files (default: 'logs')
        max_bytes: Maximum log file size in bytes before rotation (default: 10MB)
        backup_count: Number of backup log files to keep (default: 7)
        log_to_console: Whether to log to console (default: True)
        log_to_file: Whether to log to file (default: True)
        
    Returns:
        Configured logger instance
    """
    # Convert string log level to logging constant if needed
    if isinstance(log_level, str):
        log_level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    # Create formatter with detailed format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_to_file:
        try:
            # Ensure log directory exists
            log_dir_path = Path(log_dir)
            log_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create log file with timestamp
            log_file = log_dir_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file.absolute()}")
            
        except Exception as e:
            logger.error(f"Failed to set up file logging: {e}", exc_info=True)
    
    # Add exception handler for uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Call the default excepthook for keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical("Uncaught exception", 
                       exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception
    
    logger.debug("Logger initialized")
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Name of the logger. If None, returns the root logger.
            
    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger()
    return logging.getLogger(name)

# Create default logger instance
logger = setup_logger()

# Example usage:
if __name__ == "__main__":
    # Test logging at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    try:
        1 / 0  # This will cause a division by zero error
    except Exception as e:
        logger.exception("An error occurred")  # This will include the traceback
