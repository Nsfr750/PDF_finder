"""
Progress dialog for showing scan progress.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                            QProgressBar, QPushButton, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import logging

logger = logging.getLogger(__name__)

class ScanProgressDialog(QDialog):
    """Dialog for displaying scan progress with a progress bar."""
    
    # Signal to cancel the operation
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None, title="Scan in Progress", message="Scanning files..."):
        """Initialize the progress dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Initial status message
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumWidth(400)
        
        # Set up the layout
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel(message)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate by default
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v/%m files")
        layout.addWidget(self.progress_bar)
        
        # Files info label
        self.files_info_label = QLabel()
        self.files_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.files_info_label)
        
        # Current file label
        self.current_file_label = QLabel()
        self.current_file_label.setWordWrap(True)
        self.current_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.current_file_label)
        
        # Button box with Cancel button
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.button_box.rejected.connect(self.on_cancel)
        layout.addWidget(self.button_box)
        
        # Initialize variables
        self._cancelled = False
        self._last_update = 0
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self.force_update)
        self._update_timer.start(100)  # Update at most every 100ms
    
    def update_progress(self, current: int, total: int, current_file: str = "", files_found: int = 0):
        """Update the progress bar and status.
        
        Args:
            current: Current progress value
            total: Maximum progress value
            current_file: Current file being processed (optional)
            files_found: Number of files found so far (optional)
        """
        if self._cancelled:
            return
            
        # Update progress bar
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
        
        # Update files info
        files_info = f"{self.tr('Files processed:')} {current}/{total}"
        if files_found > 0:
            files_info += f" | {self.tr('Duplicates found:')} {files_found}"
        self.files_info_label.setText(files_info)
        
        # Update current file label
        if current_file:
            self.current_file_label.setText(f"{self.tr('Current file:')} {current_file}")
    
    def update_message(self, message: str):
        """Update the status message.
        
        Args:
            message: New status message
        """
        self.status_label.setText(message)
    
    def on_cancel(self):
        """Handle cancel button click."""
        self._cancelled = True
        self.setEnabled(False)
        self.status_label.setText("Cancelling...")
        self.cancelled.emit()
    
    def force_update(self):
        """Force a UI update."""
        if self.isVisible():
            self.repaint()
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if not self._cancelled:
            self.on_cancel()
        event.accept()
