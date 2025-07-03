"""Preview widget for displaying PDF thumbnails and navigation controls."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QRectF, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QFont, QImage

class PDFPreviewWidget(QWidget):
    """Widget for displaying PDF previews with navigation controls."""
    
    # Signals
    next_requested = pyqtSignal()
    prev_requested = pyqtSignal()
    keep_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_doc = None
        self.current_page = 0
        self.pages = []
        self.thumbnails = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setMinimumSize(600, 800)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Preview area
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view.setFrameStyle(QFrame.Shape.NoFrame)
        self.view.setBackgroundBrush(QColor(240, 240, 240))
        
        # Navigation controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(5)
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_requested)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_requested)
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.keep_btn = QPushButton("Keep This File")
        self.keep_btn.clicked.connect(self.keep_requested)
        self.keep_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_requested)
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        
        # Add stretch to push buttons to the sides
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addWidget(self.page_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.keep_btn)
        controls_layout.addWidget(self.delete_btn)
        
        # Document info
        self.doc_info = QLabel()
        self.doc_info.setWordWrap(True)
        self.doc_info.setStyleSheet("background-color: #f8f9fa; padding: 5px; border: 1px solid #dee2e6; border-radius: 4px;")
        
        # Add widgets to main layout
        main_layout.addWidget(self.view, 1)
        main_layout.addWidget(self.doc_info)
        main_layout.addLayout(controls_layout)
        
        # Set initial state
        self.set_document(None)
    
    def set_document(self, doc, page_index=0):
        """Set the current PDF document to display."""
        self.current_doc = doc
        self.current_page = page_index
        self.pages = []
        self.thumbnails = {}
        
        self.scene.clear()
        
        if not doc or not hasattr(doc, 'file_path'):
            self.page_label.setText("No document")
            self.doc_info.setText("No document selected")
            self.update_navigation_buttons()
            return
        
        try:
            # Display document info
            info_text = f"<b>{doc.file_name}</b>"
            if hasattr(doc, 'file_size'):
                info_text += f"<br>Size: {self.format_file_size(doc.file_size)}"
            if hasattr(doc, 'page_count'):
                info_text += f"<br>Pages: {doc.page_count}"
            if hasattr(doc, 'metadata') and doc.metadata:
                if 'title' in doc.metadata and doc.metadata['title']:
                    info_text += f"<br>Title: {doc.metadata['title']}"
                if 'author' in doc.metadata and doc.metadata['author']:
                    info_text += f"<br>Author: {doc.metadata['author']}"
            
            self.doc_info.setText(info_text)
            
            # Load the first page
            self.load_page(page_index)
            
        except Exception as e:
            self.page_label.setText(f"Error loading document")
            self.doc_info.setText(f"Error: {str(e)}")
    
    def load_page(self, page_index):
        """Load and display a specific page of the current document."""
        if not self.current_doc:
            return
            
        try:
            # Clear the scene
            self.scene.clear()
            
            # Check if we have a cached thumbnail
            if page_index in self.thumbnails and self.thumbnails[page_index]:
                pixmap = self.thumbnails[page_index]
            else:
                # Generate thumbnail
                from pdf2image import convert_from_path
                from PIL.ImageQt import ImageQt
                
                # Convert PDF page to image
                images = convert_from_path(
                    self.current_doc.file_path,
                    first_page=page_index + 1,
                    last_page=page_index + 1,
                    fmt='jpeg',
                    thread_count=1,
                    size=(800, None)  # Width of 800, height calculated to maintain aspect ratio
                )
                
                if not images:
                    raise ValueError("Failed to convert PDF page to image")
                
                # Convert to QPixmap
                qim = ImageQt(images[0])
                pixmap = QPixmap.fromImage(qim)
                
                # Cache the thumbnail
                self.thumbnails[page_index] = pixmap
            
            # Add the pixmap to the scene
            pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(pixmap_item)
            
            # Fit the view to the scene
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
            # Update page label
            page_count = getattr(self.current_doc, 'page_count', 1)
            self.page_label.setText(f"Page {page_index + 1} of {page_count}")
            
            # Update navigation buttons
            self.update_navigation_buttons()
            
        except Exception as e:
            self.page_label.setText(f"Error loading page {page_index + 1}")
            self.doc_info.setText(f"Error: {str(e)}")
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons based on current page."""
        if not hasattr(self.current_doc, 'page_count') or self.current_doc.page_count <= 1:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
        else:
            self.prev_btn.setEnabled(self.current_page > 0)
            self.next_btn.setEnabled(self.current_page < self.current_doc.page_count - 1)
    
    def resizeEvent(self, event):
        """Handle window resize events to maintain aspect ratio."""
        super().resizeEvent(event)
        if self.scene and self.scene.items():
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in a human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
