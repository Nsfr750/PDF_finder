from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import fitz  # PyMuPDF
import tempfile
import os

class PDFPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_pdf = None
        self.current_page = 0
        self.zoom = 1.0
    
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Label to display the PDF page
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0;")
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("padding: 5px;")
        
        self.layout.addWidget(self.image_label, 1)
        self.layout.addWidget(self.status_label)
    
    def load_pdf(self, file_path):
        if not os.path.exists(file_path):
            self.status_label.setText("File not found")
            return
        
        try:
            self.current_pdf = fitz.open(file_path)
            self.current_page = 0
            self.show_page(0)
            self.status_label.setText(f"Page 1 of {len(self.current_pdf)}")
        except Exception as e:
            self.status_label.setText(f"Error loading PDF: {str(e)}")
    
    def show_page(self, page_num):
        if not self.current_pdf or page_num < 0 or page_num >= len(self.current_pdf):
            return
        
        try:
            # Get the page
            page = self.current_pdf.load_page(page_num)
            
            # Calculate the zoom factor based on the widget size
            zoom = min(
                (self.width() - 20) / page.rect.width,
                (self.height() - 100) / page.rect.height
            )
            zoom = min(max(zoom * 0.9, 0.5), 2.0) * self.zoom  # Limit zoom range
            
            # Render the page to an image
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to QImage
            img = QImage(
                pix.samples, 
                pix.width, 
                pix.height, 
                pix.stride, 
                QImage.Format.Format_RGB888
            )
            
            # Scale the image to fit the label while maintaining aspect ratio
            scaled_img = img.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Display the image
            self.image_label.setPixmap(QPixmap.fromImage(scaled_img))
            self.current_page = page_num
            self.status_label.setText(f"Page {page_num + 1} of {len(self.current_pdf)}")
            
        except Exception as e:
            self.status_label.setText(f"Error displaying page: {str(e)}")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pdf is not None:
            self.show_page(self.current_page)
    
    def zoom_in(self):
        self.zoom *= 1.2
        if self.current_pdf is not None:
            self.show_page(self.current_page)
    
    def zoom_out(self):
        self.zoom /= 1.2
        if self.current_pdf is not None:
            self.show_page(self.current_page)
            
    def clear(self):
        """Clear the preview display."""
        self.current_pdf = None
        self.current_page = 0
        self.zoom = 1.0
        self.image_label.clear()
        self.status_label.clear()
    
    def next_page(self):
        if self.current_pdf is not None and self.current_page < len(self.current_pdf) - 1:
            self.show_page(self.current_page + 1)
    
    def prev_page(self):
        if self.current_pdf is not None and self.current_page > 0:
            self.show_page(self.current_page - 1)


class PreviewWindow(QMainWindow):
    """A separate window for displaying PDF previews."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Preview")
        self.setMinimumSize(800, 600)
        
        # Create the preview widget
        self.preview_widget = PDFPreviewWidget()
        self.setCentralWidget(self.preview_widget)
        
        # Store reference to parent to prevent garbage collection
        self._parent = parent
        
    def load_pdf(self, file_path):
        """Load a PDF file into the preview widget."""
        if hasattr(self.preview_widget, 'load_pdf'):
            self.preview_widget.load_pdf(file_path)
            self.setWindowTitle(f"PDF Preview - {os.path.basename(file_path)}")
            
    def clear(self):
        """Clear the preview."""
        if hasattr(self.preview_widget, 'clear'):
            self.preview_widget.clear()
            self.setWindowTitle("PDF Preview")
            
    def closeEvent(self, event):
        """Handle window close event."""
        # Notify parent that we're closing
        if hasattr(self._parent, 'on_preview_window_closed'):
            self._parent.on_preview_window_closed()
        event.accept()
