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
        self.log_file = log_file
        self.log_content = []
        self.filtered_content = []
        self.current_level = "ALL"
        
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(900, 600)
        
        self.init_ui()
        self.load_log_file()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Log level filter
        toolbar.addWidget(QLabel("Filter by level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        toolbar.addWidget(self.level_combo)
        
        # Search box
        toolbar.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search in logs...")
        self.search_edit.textChanged.connect(self.filter_logs)
        toolbar.addWidget(self.search_edit)
        
        # Buttons
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_log_file)
        toolbar.addWidget(self.refresh_btn)
        
        self.clear_btn = QPushButton("Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton("Save As...")
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
                self.log_display.setPlainText(f"Log file not found: {self.log_file}")
                return
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.log_content = f.readlines()
            
            self.filter_logs()
            self.status_bar.setText(f"Loaded {len(self.log_content)} log entries")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load log file: {str(e)}")
    
    def filter_logs(self):
        """Filter logs based on selected level and search text."""
        try:
            level = self.level_combo.currentText()
            search_text = self.search_edit.text().lower()
            
            print(f"Filtering logs - Level: {level}, Search text: {search_text}")  # Debug
            
            self.filtered_content = []
            
            for i, line in enumerate(self.log_content):
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Debug: stampa le prime 5 righe per vedere il formato
                if i < 5:
                    print(f"Log line {i}: {line.strip()}")
                
                # Estrai il livello di log dal formato: YYYY-MM-DD HH:MM:SS,SSS - PDFDuplicateFinder - LEVEL - message
                log_level = None
                import re
                
                # Pattern per il formato: 2025-07-09 14:12:29,742 - PDFDuplicateFinder - INFO - message
                level_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - [^-]+ - (\w+) -', line)
                if level_match:
                    log_level = level_match.group(1)
                
                print(f"Line {i}: Extracted log level: {log_level}")  # Debug
                
                # Se non riusciamo a determinare il livello, includiamo la riga solo se il livello è "ALL"
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
            
            self.status_bar.setText(f"Showing {len(self.filtered_content)} of {len(self.log_content)} log entries")
            
        except Exception as e:
            print(f"Error in filter_logs: {str(e)}")  # Debug
            QMessageBox.critical(self, "Error", f"Failed to filter logs: {str(e)}")
    
    def clear_logs(self):
        """Clear the log file after confirmation."""
        try:
            if not os.path.exists(self.log_file):
                return
                
            reply = QMessageBox.question(
                self,
                'Clear Logs',
                'Are you sure you want to clear all log files?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                self.load_log_file()
                self.status_bar.setText("Logs cleared")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear logs: {str(e)}")
    
    def save_logs(self):
        """Save the currently displayed logs to a file."""
        try:
            if not self.filtered_content:
                QMessageBox.information(self, "No Content", "No logs to save.")
                return
                
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Logs As",
                f"pdf_finder_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
            )
            
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.writelines(self.filtered_content)
                self.status_bar.setText(f"Logs saved to {os.path.basename(file_name)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save logs: {str(e)}")


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
            "Log File Not Found",
            f"Log file not found: {log_file}"
        )
        return
    
    viewer = LogViewer(log_file, parent)
    viewer.exec()
    

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = "pdf_finder.log"
    
    viewer = LogViewer(log_file)
    viewer.show()
    sys.exit(app.exec())
