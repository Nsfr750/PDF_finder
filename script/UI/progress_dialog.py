"""
Progress dialog for showing scan progress.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                            QProgressBar, QPushButton, QDialogButtonBox, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import logging

logger = logging.getLogger(__name__)

class ScanProgressDialog(QDialog):
    """Dialog for displaying scan progress with a progress bar."""
    
    # Signal to cancel the operation
    cancelled = pyqtSignal()
    # Signal to request dialog closure (for proper cleanup)
    close_requested = pyqtSignal()
    
    def __init__(self, parent=None, title="Scan in Progress", message="Scanning files..."):
        """Initialize the progress dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Initial status message
        """
        super().__init__(parent)
        self._language_manager = None
        
        # Try to get language manager from parent if available
        if parent and hasattr(parent, 'language_manager'):
            self._language_manager = parent.language_manager
        
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
        
        # Button box with Cancel and Close buttons
        self.button_box = QDialogButtonBox()
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.close_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Close)
        # Connect to both the detailed method and a simple direct close
        self.close_button.clicked.connect(self.on_close)
        self.close_button.clicked.connect(self.direct_close)
        self.close_button.hide()  # Hide close button initially
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
        # Safety check: don't update if dialog is closed or timer is stopped
        if self._cancelled or not self.isVisible() or not self._update_timer.isActive():
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
        # Safety check: don't update if dialog is closed or timer is stopped
        if self._cancelled or not self.isVisible() or not self._update_timer.isActive():
            return
        self.status_label.setText(message)
    
    def on_cancel(self):
        """Handle cancel button click."""
        self._cancelled = True
        self.setEnabled(False)
        self.status_label.setText("Cancelling...")
        # Stop the update timer to prevent UI updates after dialog is closed
        if self._update_timer.isActive():
            self._update_timer.stop()
        self.cancelled.emit()
    
    def direct_close(self):
        """Direct close method that simply closes the dialog."""
        logger.debug("Direct close method called")
        self.accept()
    
    def on_close(self):
        """Handle close button click."""
        logger.debug("Close button clicked in progress dialog")
        
        # Stop the update timer to prevent UI updates after dialog is closed
        if self._update_timer.isActive():
            self._update_timer.stop()
        
        # Emit a signal to notify that the dialog should be closed
        # This allows the parent to properly clean up the dialog reference
        self.close_requested.emit()
        
        # Close the dialog immediately
        logger.debug("Closing progress dialog")
        self.done(QDialog.DialogCode.Accepted)
    
    def closeEvent(self, event):
        """Handle the dialog close event."""
        logger.debug("Progress dialog close event triggered")
        
        # Stop the update timer
        if self._update_timer.isActive():
            self._update_timer.stop()
        
        # Emit the close requested signal if not already emitted
        self.close_requested.emit()
        
        # Accept the close event
        event.accept()
    
    def set_scan_complete(self):
        """Switch to show close button when scan is complete."""
        logger.debug("Setting scan complete - showing close button")
        
        # Stop the update timer as scan is complete
        if self._update_timer.isActive():
            self._update_timer.stop()
        
        # Hide cancel button and show close button
        self.cancel_button.hide()
        self.close_button.show()
        self.close_button.setDefault(True)
        self.close_button.setFocus()
        
        # Update status message
        self.status_label.setText(self.tr("scan.complete"))
        
        # Force UI update
        self.update()
        
        # Process events to ensure UI is updated
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        logger.debug(f"Close button visible: {self.close_button.isVisible()}")
        logger.debug(f"Close button enabled: {self.close_button.isEnabled()}")
    
    def force_update(self):
        """Force a UI update."""
        # Safety check: don't update if dialog is closed or timer is stopped
        if not self.isVisible() or not self._update_timer.isActive():
            return
            
        try:
            # Force a complete repaint of the dialog and all its children
            self.repaint()
            
            # Also update all child widgets to ensure they are properly rendered
            for child in self.findChildren(QWidget):
                if child.isVisible():
                    child.update()
                    
            # Process events to ensure the UI is responsive
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        except Exception as e:
            # If there's any error during the update, log it but don't crash
            logger.debug(f"Error during force_update: {e}")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Stop the update timer to prevent UI updates after dialog is closed
        if self._update_timer.isActive():
            self._update_timer.stop()
        
        # Cancel the operation if not already cancelled
        if not self._cancelled:
            self.on_cancel()
            
        # Process events to ensure the UI is updated before closing
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        # Accept the close event
        event.accept()
    
    def tr(self, key: str, default: str = None) -> str:
        """Translate a string using the language manager.
        
        Args:
            key: Translation key
            default: Default text if translation not found
            
        Returns:
            Translated string or default/key if not available
        """
        if self._language_manager and hasattr(self._language_manager, 'tr'):
            return self._language_manager.tr(key, default)
        return default or key
