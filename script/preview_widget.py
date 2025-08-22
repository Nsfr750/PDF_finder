"""
Preview widget for displaying PDF files.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt

class PDFPreviewWidget(QWidget):
    """Widget for displaying PDF previews."""
    
    def __init__(self, parent=None):
        """Initialize the preview widget."""
        super().__init__(parent)
        self.setup_ui()
        self.set_placeholder("No preview available")
    
    def setup_ui(self):
        """Set up the UI components."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Label for displaying the preview or placeholder
        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.layout.addWidget(self.preview_label)
    
    def set_placeholder(self, text):
        """Set placeholder text when no preview is available.
        
        Args:
            text: The text to display as placeholder
        """
        self.preview_label.setText(text)
    
    def load_pdf(self, file_path):
        """Load and display a PDF file.
        
        Args:
            file_path: Path to the PDF file
        """
        if not os.path.exists(file_path):
            self.set_placeholder("File not found")
            return
            
        try:
            # In a real implementation, you would render the PDF here
            # For now, we'll just show the file path
            self.set_placeholder(f"Preview for: {os.path.basename(file_path)}")
        except Exception as e:
            self.set_placeholder(f"Error loading preview: {str(e)}")
            import traceback
            traceback.print_exc()
