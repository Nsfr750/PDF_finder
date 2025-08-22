from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMainWindow
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QPixmap, QImage
from wand.image import Image as WandImage
import tempfile
import os

# Import language manager
from script.lang_mgr import LanguageManager

__all__ = ['PDFPreviewWidget', 'PreviewWindow']

class PDFPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.tr = self.language_manager.tr
        self.setup_ui()
        self.current_pdf = None
        self.current_page = 0
        self.zoom = 1.0
        self.pages = []
    
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
        
        # Set initial placeholder
        self.set_placeholder(self.tr("preview.no_preview", "No preview available"))
    
    def set_placeholder(self, text):
        """Set placeholder text to be displayed in the preview area.
        
        Args:
            text: The text to display as placeholder
        """
        if hasattr(self, 'image_label'):
            self.image_label.setText(text)
    
    def load_pdf(self, file_path):
        if not os.path.exists(file_path):
            self.status_label.setText(self.tr("preview.file_not_found", "File not found"))
            return
        
        try:
            # Clear any existing PDF data
            self.pages = []
            
            # Read PDF with Wand
            with WandImage(filename=file_path, resolution=150) as img:
                # Convert PDF to a sequence of images
                img_sequence = img.sequence
                for page in img_sequence:
                    with WandImage(page) as pg:
                        self.pages.append(pg.clone())
            
            if not self.pages:
                raise ValueError(self.tr("preview.no_pages_found", "No pages found in PDF"))
                
            self.current_page = 0
            self.show_page(0)
            self.status_label.setText(self.tr(
                "preview.page_status", 
                "Page {current} of {total}"
            ).format(current=1, total=len(self.pages)))
            
        except Exception as e:
            self.status_label.setText(self.tr(
                "preview.error_loading_pdf", 
                "Error loading PDF: {error}"
            ).format(error=str(e)))
            self.pages = []
    
    def show_page(self, page_num):
        if not self.pages or page_num < 0 or page_num >= len(self.pages):
            return
        
        try:
            # Get the page image
            page = self.pages[page_num]
            
            # Convert Wand image to QImage
            img_data = page.make_blob('RGB')
            qimg = QImage(
                img_data, 
                page.width, 
                page.height, 
                QImage.Format.Format_RGB888
            )
            
            # Scale the image to fit the label while maintaining aspect ratio
            scaled_img = qimg.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Display the image
            self.image_label.setPixmap(QPixmap.fromImage(scaled_img))
            self.current_page = page_num
            self.status_label.setText(self.tr(
                "preview.page_status", 
                "Page {current} of {total}"
            ).format(current=page_num + 1, total=len(self.pages)))
            
        except Exception as e:
            self.status_label.setText(self.tr(
                "preview.error_displaying_page", 
                "Error displaying page: {error}"
            ).format(error=str(e)))
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pages:
            self.show_page(self.current_page)
    
    def zoom_in(self):
        self.zoom *= 1.2
        if self.pages:
            self.show_page(self.current_page)
    
    def zoom_out(self):
        self.zoom /= 1.2
        if self.pages:
            self.show_page(self.current_page)
            
    def clear(self):
        """Clear the preview display."""
        self.pages = []
        self.current_page = 0
        self.zoom = 1.0
        self.image_label.clear()
        self.status_label.clear()
    
    def next_page(self):
        if self.pages and self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)
    
    def prev_page(self):
        if self.pages and self.current_page > 0:
            self.show_page(self.current_page - 1)


class PreviewWindow(QMainWindow):
    """A separate window for displaying PDF previews."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.tr = self.language_manager.tr
        self.setWindowTitle(self.tr("preview.window_title", "PDF Preview"))
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
            self.setWindowTitle(self.tr(
                "preview.window_title_with_file", 
                "PDF Preview - {filename}"
            ).format(filename=os.path.basename(file_path)))
            
    def clear(self):
        """Clear the preview."""
        if hasattr(self.preview_widget, 'clear'):
            self.preview_widget.clear()
            self.setWindowTitle(self.tr("preview.window_title", "PDF Preview"))
            
    def closeEvent(self, event):
        """Handle window close event."""
        # Notify parent that we're closing
        if hasattr(self._parent, 'on_preview_window_closed'):
            self._parent.on_preview_window_closed()
        event.accept()
