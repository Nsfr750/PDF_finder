"""
UI components for PDF Duplicate Finder.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QLabel, QFrame, QStatusBar
)
from PyQt6.QtCore import Qt

# Import language manager
from lang.language_manager import LanguageManager

class MainUI(QWidget):
    """Main UI components for the application."""
    
    def __init__(self, parent=None):
        """Initialize the UI components.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        # Initialize language manager
        self.language_manager = LanguageManager()
        self.tr = self.language_manager.tr
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create main content area with splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - File list
        self.file_list = QListWidget()
        self.file_list.setMinimumWidth(300)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # Right panel - Preview
        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_widget.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_widget.setText(self.tr("ui.preview_placeholder", "Preview will be shown here"))
        
        # Add widgets to splitter
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(self.preview_widget)
        
        # Set initial sizes
        self.splitter.setSizes([300, 700])
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage(self.tr("ui.status_ready", "Ready"))
    
    def update_preview(self, file_path):
        """Update the preview with the selected file.
        
        Args:
            file_path: Path to the file to preview.
        """
        if not file_path or not hasattr(self, 'preview_widget'):
            return
            
        # Update preview with localized text
        self.preview_widget.setText(
            self.tr("ui.preview_of", "Preview of: {file_path}")
            .format(file_path=file_path)
        )
    
    def clear_preview(self):
        """Clear the preview area."""
        if hasattr(self, 'preview_widget'):
            self.preview_widget.setText(
                self.tr("ui.preview_placeholder", "Preview will be shown here")
            )
    
    def update_status(self, message):
        """Update the status bar with a message.
        
        Args:
            message: The message to display in the status bar.
        """
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message)
