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
from PyQt6.QtCore import Qt, QRegularExpression, pyqtSlot
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor, QSyntaxHighlighter, QFont

# Import language manager
from lang.language_manager import LanguageManager

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
    
    def __init__(self, log_file, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.log_file = log_file
        self.log_content = []
        self.filtered_content = []
        self.current_level = "ALL"
        
        self.init_ui()
        self.retranslate_ui()
        self.load_log_file()
        
        # Connect language change signal
        self.language_manager.language_changed.connect(self.retranslate_ui)
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Log level filter
        self.level_label = QLabel()
        toolbar.addWidget(self.level_label)
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        toolbar.addWidget(self.level_combo)
        
        # Search box
        self.search_label = QLabel()
        toolbar.addWidget(self.search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_logs)
        toolbar.addWidget(self.search_edit)
        
        # Buttons
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.load_log_file)
        toolbar.addWidget(self.refresh_btn)
        
        self.clear_btn = QPushButton()
        self.clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton()
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
    
    def retranslate_ui(self):
        """Update the UI when the language changes."""
        self.setWindowTitle(self.tr("Log Viewer"))
        self.level_label.setText(self.tr("Filter by level:"))
        self.search_label.setText(self.tr("Search:"))
        self.search_edit.setPlaceholderText(self.tr("Search in logs..."))
        self.refresh_btn.setText(self.tr("Refresh"))
        self.clear_btn.setText(self.tr("Clear Logs"))
        self.save_btn.setText(self.tr("Save As..."))
        
        # Update status bar if we have content
        if hasattr(self, 'log_content'):
            self.status_bar.setText(self.tr("Loaded {count} log entries").format(count=len(self.log_content)))
    
    def log_document(self):
        """Return the document associated with the log display."""
        return self.log_display.document()
    
    def load_log_file(self):
        """Load the log file content."""
        try:
            if not os.path.exists(self.log_file):
                self.log_display.setPlainText(self.tr("Log file not found: {path}").format(path=self.log_file))
                return
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.log_content = f.readlines()
            
            self.filter_logs()
            self.status_bar.setText(self.tr("Loaded {count} log entries").format(count=len(self.log_content)))
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to load log file: {error}").format(error=str(e)))
    
    def filter_logs(self):
        """Filter logs based on selected level and search text."""
        try:
            level = self.level_combo.currentText()
            search_text = self.search_edit.text().lower()
            
            self.filtered_content = []
            
            for i, line in enumerate(self.log_content):
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Extract log level from format: YYYY-MM-DD HH:MM:SS,SSS - PDFDuplicateFinder - LEVEL - message
                log_level = None
                level_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - [^-]+ - (\w+) -', line)
                if level_match:
                    log_level = level_match.group(1)
                
                # If we can't determine the level, include the line only if level is "ALL"
                if level != "ALL":
                    if not log_level or log_level != level:
                        continue
                    
                # Check search text
                if search_text and search_text not in line.lower():
                    continue
                    
                self.filtered_content.append(line)
            
            # Update display
            self.log_display.clear()
            self.log_display.setPlainText(''.join(self.filtered_content))
            
            # Scroll to bottom
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_display.setTextCursor(cursor)
            
            # Update status
            self.status_bar.setText(
                self.tr("Showing {filtered} of {total} log entries").format(
                    filtered=len(self.filtered_content),
                    total=len(self.log_content)
                )
            )
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to filter logs: {error}").format(error=str(e)))
    
    def clear_logs(self):
        """Clear the log file after confirmation."""
        try:
            reply = QMessageBox.question(
                self,
                self.tr("Confirm Clear"),
                self.tr("Are you sure you want to clear all logs? This cannot be undone."),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                self.load_log_file()
                
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to clear logs: {error}").format(error=str(e)))
    
    def save_logs(self):
        """Save the filtered logs to a file."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                self.tr("Save Log File"),
                "",
                self.tr("Log Files (*.log);;All Files (*)")
            )
            
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.writelines(self.filtered_content)
                
                QMessageBox.information(
                    self,
                    self.tr("Save Successful"),
                    self.tr("Logs saved successfully to: {path}").format(path=file_name)
                )
                
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr("Failed to save logs: {error}").format(error=str(e)))


def show_log_viewer(log_file, parent=None):
    """
    Show the log viewer dialog.
    
    Args:
        log_file (str): Path to the log file
        parent: Parent widget
    """
    if not os.path.exists(log_file):
        QMessageBox.warning(
            parent,
            parent.tr("Log File Not Found"),
            parent.tr("Log file not found: {path}").format(path=log_file)
        )
        return
    
    viewer = LogViewer(log_file, parent)
    viewer.exec()


if __name__ == "__main__":
    import sys
    
    # For testing
    app = QApplication(sys.argv)
    
    # Create a test log file if it doesn't exist
    log_file = "test.log"
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write("2023-01-01 12:00:00,000 - Test - INFO - This is an info message\n")
            f.write("2023-01-01 12:00:01,000 - Test - WARNING - This is a warning\n")
            f.write("2023-01-01 12:00:02,000 - Test - ERROR - This is an error\n")
    
    # Show the log viewer
    viewer = LogViewer(log_file)
    viewer.show()
    
    sys.exit(app.exec())
