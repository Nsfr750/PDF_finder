"""
Log Viewer for PDF Duplicate Finder

This module provides a graphical interface to view and filter log messages.
"""

import os
import re
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QComboBox, QPushButton, QLabel, QFileDialog,
                             QMessageBox, QApplication, QLineEdit)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor, QSyntaxHighlighter, QFont

# Import translation utilities
from .language_manager import LanguageManager

class LogHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for log messages."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Format for different log levels
        error_format = QTextCharFormat()
        error_format.setForeground(QColor(200, 0, 0))  # Red
        error_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'ERROR.*'), error_format))
        
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor(255, 165, 0))  # Orange
        warning_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'WARNING.*'), warning_format))
        
        critical_format = QTextCharFormat()
        critical_format.setForeground(QColor(255, 255, 255))  # White
        critical_format.setBackground(QColor(200, 0, 0))  # Red background
        critical_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'CRITICAL.*'), critical_format))
        
        debug_format = QTextCharFormat()
        debug_format.setForeground(QColor(100, 100, 100))  # Gray
        self.highlighting_rules.append((QRegularExpression(r'DEBUG.*'), debug_format))
        
        info_format = QTextCharFormat()
        info_format.setForeground(QColor(0, 0, 200))  # Blue
        info_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'INFO.*'), info_format))
        
        # Format for timestamps
        time_format = QTextCharFormat()
        time_format.setForeground(QColor(0, 128, 0))  # Dark green
        time_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'), time_format))
        
        # Format for tracebacks
        traceback_format = QTextCharFormat()
        traceback_format.setForeground(QColor(200, 0, 0))  # Red
        self.highlighting_rules.append((QRegularExpression(r'Traceback \(most recent call last\):'), traceback_format))
        self.highlighting_rules.append((QRegularExpression(r'File ".*", line \d+.*'), traceback_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class LogViewer(QDialog):
    """Log viewer dialog for displaying and filtering log messages."""
    
    def __init__(self, log_file, language_manager: LanguageManager, parent=None):
        super().__init__(parent)
        self.log_file = log_file
        self.language_manager = language_manager
        self.log_content = []
        self.filtered_content = []
        self.current_level = "ALL"
        
        self.setWindowTitle(self.tr("log_viewer.window_title", "Log Viewer"))
        self.setMinimumSize(900, 600)
        
        self.init_ui()
        self.load_log_file()
    
    def tr(self, key: str, default_text: str = "") -> str:
        """Translate a string using the language manager."""
        return self.language_manager.tr(key, default_text)
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Log level filter
        toolbar.addWidget(QLabel(self.tr("log_viewer.filter_by_level", "Filter by level:")))
        self.level_combo = QComboBox()
        self.level_combo.addItems([
            self.tr("log_viewer.level_all", "ALL"),
            self.tr("log_viewer.level_debug", "DEBUG"),
            self.tr("log_viewer.level_info", "INFO"),
            self.tr("log_viewer.level_warning", "WARNING"),
            self.tr("log_viewer.level_error", "ERROR"),
            self.tr("log_viewer.level_critical", "CRITICAL")
        ])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        toolbar.addWidget(self.level_combo)
        
        # Search box
        toolbar.addWidget(QLabel(self.tr("log_viewer.search", "Search:")))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.tr("log_viewer.search_placeholder", "Search in logs..."))
        self.search_edit.textChanged.connect(self.filter_logs)
        toolbar.addWidget(self.search_edit)
        
        # Buttons
        self.refresh_btn = QPushButton(self.tr("log_viewer.refresh", "Refresh"))
        self.refresh_btn.clicked.connect(self.load_log_file)
        toolbar.addWidget(self.refresh_btn)
        
        self.clear_btn = QPushButton(self.tr("log_viewer.clear_logs", "Clear Logs"))
        self.clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton(self.tr("log_viewer.save_as", "Save As..."))
        self.save_btn.clicked.connect(self.save_logs)
        toolbar.addWidget(self.save_btn)
        
        layout.addLayout(toolbar)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Courier New", 10))
        self.highlighter = LogHighlighter(self.log_document())
        
        layout.addWidget(self.log_display)
        
        # Status bar
        self.status_bar = QLabel()
        layout.addWidget(self.status_bar)
    
    def log_document(self):
        """Return the document associated with the log display."""
        return self.log_display.document()
    
    def load_log_file(self):
        """Load the log file content."""
        try:
            if not os.path.exists(self.log_file):
                self.log_display.setPlainText(
                    self.tr("log_viewer.file_not_found", "Log file not found: {file}").format(file=self.log_file)
                )
                return
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.log_content = f.readlines()
            
            self.filter_logs()
            self.status_bar.setText(
                self.tr("log_viewer.entries_loaded", "Loaded {count} log entries")
                .format(count=len(self.log_content))
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("log_viewer.error", "Error"),
                self.tr("log_viewer.load_error", "Failed to load log file: {error}").format(error=str(e))
            )
    
    def filter_logs(self):
        """Filter logs based on selected level and search text."""
        try:
            level = self.level_combo.currentText()
            search_text = self.search_edit.text().lower()
            
            # Map translated level names back to their original values for filtering
            level_mapping = {
                self.tr("log_viewer.level_all", "ALL"): "ALL",
                self.tr("log_viewer.level_debug", "DEBUG"): "DEBUG",
                self.tr("log_viewer.level_info", "INFO"): "INFO",
                self.tr("log_viewer.level_warning", "WARNING"): "WARNING",
                self.tr("log_viewer.level_error", "ERROR"): "ERROR",
                self.tr("log_viewer.level_critical", "CRITICAL"): "CRITICAL"
            }
            
            level_code = level_mapping.get(level, "ALL")
            
            self.filtered_content = []
            
            for line in self.log_content:
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Extract log level from the line
                log_level = None
                level_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - [^-]+ - (\w+) -', line)
                if level_match:
                    log_level = level_match.group(1)
                
                # Filter by level
                if level_code != "ALL":
                    if not log_level or log_level != level_code:
                        continue
                
                # Filter by search text
                if search_text and search_text not in line.lower():
                    continue
                    
                self.filtered_content.append(line)
            
            # Update display
            self.log_display.clear()
            self.log_display.setPlainText(''.join(self.filtered_content))
            
            # Update status bar
            self.status_bar.setText(
                self.tr("log_viewer.showing_entries", "Showing {filtered} of {total} entries")
                .format(filtered=len(self.filtered_content), total=len(self.log_content))
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("log_viewer.error", "Error"),
                self.tr("log_viewer.filter_error", "Error filtering logs: {error}").format(error=str(e))
            )
    
    def clear_logs(self):
        """Clear the log file after confirmation."""
        reply = QMessageBox.question(
            self,
            self.tr("log_viewer.confirm_clear", "Confirm Clear"),
            self.tr("log_viewer.confirm_clear_message", "Are you sure you want to clear all log entries? This cannot be undone."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                self.log_content = []
                self.filter_logs()
                self.status_bar.setText(self.tr("log_viewer.logs_cleared", "Logs cleared"))
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("log_viewer.error", "Error"),
                    self.tr("log_viewer.clear_error", "Failed to clear log file: {error}").format(error=str(e))
                )
    
    def save_logs(self):
        """Save the filtered logs to a file."""
        if not self.filtered_content:
            QMessageBox.information(
                self,
                self.tr("log_viewer.no_entries", "No Entries"),
                self.tr("log_viewer.no_entries_message", "No log entries to save.")
            )
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("log_viewer.save_logs", "Save Logs"),
            f"pdf_finder_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            self.tr("log_viewer.log_files", "Log Files (*.log);;All Files (*)")
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.writelines(self.filtered_content)
                
                QMessageBox.information(
                    self,
                    self.tr("log_viewer.save_success", "Save Successful"),
                    self.tr("log_viewer.save_success_message", "Logs saved to: {file}").format(file=file_name)
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("log_viewer.error", "Error"),
                    self.tr("log_viewer.save_error", "Failed to save log file: {error}").format(error=str(e))
                )


def show_log_viewer(log_file, language_manager: LanguageManager, parent=None):
    """
    Show the log viewer dialog.
    
    Args:
        log_file (str): Path to the log file
        language_manager (LanguageManager): The application's language manager
        parent: Parent widget
    """
    viewer = LogViewer(log_file, language_manager, parent)
    viewer.exec()


if __name__ == "__main__":
    import sys
    
    # For testing the log viewer
    app = QApplication(sys.argv)
    
    # Create a temporary log file for testing
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as f:
        log_file = f.name
    
    # Create a simple language manager for testing
    class TestLanguageManager:
        def tr(self, key, default_text):
            return default_text
    
    # Show the log viewer
    show_log_viewer(log_file, TestLanguageManager())
    
    # Clean up
    try:
        os.unlink(log_file)
    except:
        pass
    
    sys.exit(app.exec())
