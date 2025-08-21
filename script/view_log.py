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
from .lang_mgr import LanguageManager

class LogHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for log messages."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Format for different log levels with improved contrast and accessibility
        
        # CRITICAL - High contrast red background with white text
        critical_format = QTextCharFormat()
        critical_format.setForeground(QColor(255, 255, 255))  # White text
        critical_format.setBackground(QColor(178, 34, 34))    # Firebrick red background
        critical_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'CRITICAL.*'), critical_format))
        
        # ERROR - Bright red
        error_format = QTextCharFormat()
        error_format.setForeground(QColor(220, 50, 47))  # Bright red
        error_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'ERROR.*'), error_format))
        
        # WARNING - Orange/brown
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor(203, 75, 22))  # Chocolate orange
        warning_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'WARNING.*'), warning_format))
        
        # INFO - Navy blue
        info_format = QTextCharFormat()
        info_format.setForeground(QColor(42, 101, 153))  # Darker blue
        info_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'INFO.*'), info_format))
        
        # DEBUG - Dark gray
        debug_format = QTextCharFormat()
        debug_format.setForeground(QColor(88, 110, 117))  # Dark gray-blue
        debug_format.setFontItalic(True)  # Italic to distinguish debug messages
        self.highlighting_rules.append((QRegularExpression(r'DEBUG.*'), debug_format))
        
        # Timestamp - Teal
        time_format = QTextCharFormat()
        time_format.setForeground(QColor(7, 102, 120))  # Dark teal
        time_format.setFontWeight(QFont.Weight.Medium)
        self.highlighting_rules.append((QRegularExpression(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'), time_format))
        
        # Tracebacks - Dark red with subtle background
        traceback_format = QTextCharFormat()
        traceback_format.setForeground(QColor(178, 34, 34))  # Firebrick red
        traceback_format.setBackground(QColor(255, 245, 245))  # Very light red background
        self.highlighting_rules.append((QRegularExpression(r'Traceback \(most recent call last\):'), traceback_format))
        self.highlighting_rules.append((QRegularExpression(r'File ".*", line \d+.*'), traceback_format))
        
        # Module/function names - Purple
        module_format = QTextCharFormat()
        module_format.setForeground(QColor(108, 113, 196))  # Soft purple
        module_format.setFontWeight(QFont.Weight.Medium)
        self.highlighting_rules.append((QRegularExpression(r'\b[a-zA-Z_][a-zA-Z0-9_]*\.py:\d+'), module_format))
    
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
        
        # Set window size
        self.resize(600, 400)
        
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
        self.search_edit.setPlaceholderText(self.tr("Search in logs..."))
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
        
        layout.addWidget(self.log_display, 1)  # Add stretch factor to make it expandable
        
        # Status bar and close button
        bottom_layout = QHBoxLayout()
        
        # Status bar
        self.status_bar = QLabel()
        bottom_layout.addWidget(self.status_bar, 1)  # Add stretch to push close button to right
        
        # Close button
        self.close_btn = QPushButton(self.tr("Close"))
        self.close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(self.close_btn)
        
        layout.addLayout(bottom_layout)
    
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
            current_entry = []
            
            for line in self.log_content:
                line = line.rstrip('\n')
                
                # Check if line starts with a timestamp (new log entry)
                is_new_entry = bool(re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line))
                
                if is_new_entry and current_entry:
                    # Process the previous entry
                    entry_text = '\n'.join(current_entry)
                    if self._should_include_entry(entry_text, level, search_text):
                        self.filtered_content.append(entry_text)
                    current_entry = []
                
                if line.strip():  # Only add non-empty lines
                    current_entry.append(line)
            
            # Process the last entry
            if current_entry:
                entry_text = '\n'.join(current_entry)
                if self._should_include_entry(entry_text, level, search_text):
                    self.filtered_content.append(entry_text)
            
            # Update display
            self.log_display.clear()
            if self.filtered_content:
                self.log_display.setPlainText('\n\n'.join(self.filtered_content))
            else:
                no_results = self.tr("No log entries match the current filters.")
                self.log_display.setPlainText(no_results)
            
            # Update status
            total_entries = len([l for l in self.log_content if l.strip() and re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', l)])
            self.status_bar.setText(self.tr("Showing {count} of {total} log entries").format(
                count=len(self.filtered_content) if self.filtered_content else 0,
                total=total_entries
            ))
            
            # Scroll to top after filtering
            self.log_display.verticalScrollBar().setValue(0)
            
        except Exception as e:
            self.log_display.setPlainText(self.tr("Error filtering logs: {}").format(str(e)))
            logger.error(f"Error filtering logs: {e}", exc_info=True)
    
    def _should_include_entry(self, entry_text, level, search_text):
        """Check if a log entry should be included based on filters."""
        # Check level filter
        if level != "ALL":
            # Match the actual log format: "YYYY-MM-DD HH:MM:SS - APPNAME - LEVEL - "
            level_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - [^-]+ - ' + re.escape(level) + r' - '
            level_match = re.search(level_pattern, entry_text)
            if not level_match:
                # For multi-line entries (like tracebacks), check the first line
                first_line = entry_text.split('\n')[0]
                level_match = re.search(level_pattern, first_line)
                if not level_match:
                    return False
        
        # Check search text
        if search_text and search_text.lower() not in entry_text.lower():
            return False
            
        return True
    
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
