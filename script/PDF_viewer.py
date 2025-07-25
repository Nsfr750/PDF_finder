"""
PDF Viewer Module for PDF Duplicate Finder.

This module provides an enhanced PDF viewer with navigation, zoom, and search capabilities.
"""
import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFileDialog, QMessageBox, QSlider, QLineEdit, QToolBar, 
                            QSizePolicy, QMainWindow, QApplication, QSplitter, QScrollArea)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QUrl, QPoint
from PyQt6.QtGui import QPixmap, QImage, QAction, QPainter, QIcon, QKeySequence, QDesktopServices

class PDFViewer(QMainWindow):
    """Enhanced PDF viewer with navigation and zoom capabilities."""
    
    def __init__(self, parent=None, language_manager=None):
        """Initialize the PDF viewer.
        
        Args:
            parent: Parent widget
            language_manager: Language manager for translations
        """
        super().__init__(parent)
        self.language_manager = language_manager
        self.tr = language_manager.tr if language_manager else lambda key, default: default
        
        # PDF document and page tracking
        self.doc = None
        self.current_page = 0
        self.zoom = 1.0
        self.file_path = None
        
        # Setup UI
        self.setup_ui()
        
        # Set window properties
        self.setWindowTitle(self.tr("pdf_viewer.window_title", "PDF Viewer"))
        self.setMinimumSize(800, 600)
        
        # Connect signals
        self.connect_signals()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # Create status bar
        self.status_bar = self.statusBar()
        
        # Create scroll area for the page
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create page widget
        self.page_widget = QLabel()
        self.page_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_widget.setMinimumSize(1, 1)  # Ensure it can be made very small
        
        # Set the page widget in the scroll area
        self.scroll_area.setWidget(self.page_widget)
        main_layout.addWidget(self.scroll_area, 1)
        
        # Add page navigation controls
        self.create_page_controls()
        main_layout.addLayout(self.page_controls)
        
        # Set initial state
        self.update_ui()
    
    def create_toolbar(self):
        """Create the toolbar with actions."""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(24, 24))
        
        # Open action
        self.open_action = QAction(
            self.tr("pdf_viewer.actions.open", "Open"),
            self,
            shortcut=QKeySequence.StandardKey.Open,
            triggered=self.open_file
        )
        
        # Zoom actions
        self.zoom_in_action = QAction(
            self.tr("pdf_viewer.actions.zoom_in", "Zoom In"),
            self,
            shortcut=QKeySequence.StandardKey.ZoomIn,
            triggered=self.zoom_in
        )
        
        self.zoom_out_action = QAction(
            self.tr("pdf_viewer.actions.zoom_out", "Zoom Out"),
            self,
            shortcut=QKeySequence.StandardKey.ZoomOut,
            triggered=self.zoom_out
        )
        
        self.fit_width_action = QAction(
            self.tr("pdf_viewer.actions.fit_width", "Fit Width"),
            self,
            triggered=self.fit_width
        )
        
        self.fit_page_action = QAction(
            self.tr("pdf_viewer.actions.fit_page", "Fit Page"),
            self,
            triggered=self.fit_page
        )
        
        # Add actions to toolbar
        self.toolbar.addAction(self.open_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.zoom_in_action)
        self.toolbar.addAction(self.zoom_out_action)
        self.toolbar.addAction(self.fit_width_action)
        self.toolbar.addAction(self.fit_page_action)
    
    def create_page_controls(self):
        """Create the page navigation controls."""
        self.page_controls = QHBoxLayout()
        self.page_controls.setContentsMargins(5, 5, 5, 5)
        
        # Previous page button
        self.prev_page_btn = QPushButton(self.tr("pdf_viewer.actions.prev_page", "Previous"))
        self.prev_page_btn.clicked.connect(self.prev_page)
        
        # Page number display
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Next page button
        self.next_page_btn = QPushButton(self.tr("pdf_viewer.actions.next_page", "Next"))
        self.next_page_btn.clicked.connect(self.next_page)
        
        # Add widgets to layout
        self.page_controls.addWidget(self.prev_page_btn)
        self.page_controls.addWidget(self.page_label, 1)
        self.page_controls.addWidget(self.next_page_btn)
    
    def connect_signals(self):
        """Connect signals to slots."""
        # Connect keyboard shortcuts
        self.installEventFilter(self)
    
    def open_file(self, file_path=None):
        """Open a PDF file.
        
        Args:
            file_path: Path to the PDF file. If None, a file dialog will be shown.
        """
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                self.tr("pdf_viewer.dialogs.open_file", "Open PDF"),
                "",
                self.tr("pdf_viewer.file_filter", "PDF Files (*.pdf)")
            )
            
            if not file_path:
                return
        
        try:
            # Close any existing document
            if self.doc:
                self.doc.close()
            
            # Open the new document
            self.doc = fitz.open(file_path)
            self.file_path = file_path
            self.current_page = 0
            self.zoom = 1.0
            
            # Update the UI
            self.update_ui()
            
            # Update window title
            self.setWindowTitle(
                self.tr("pdf_viewer.window_title_with_file", "{filename} - PDF Viewer").format(
                    filename=os.path.basename(file_path)
                )
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("pdf_viewer.errors.open_error", "Error Opening PDF"),
                self.tr("pdf_viewer.errors.could_not_open", "Could not open {file}: {error}").format(
                    file=os.path.basename(file_path) if file_path else "",
                    error=str(e)
                )
            )
    
    def render_page(self):
        """Render the current page with the current zoom level."""
        if not self.doc:
            return
        
        try:
            # Get the page
            page = self.doc.load_page(self.current_page)
            
            # Calculate the zoom factor (72 DPI * zoom)
            zoom_matrix = fitz.Matrix(self.zoom, self.zoom)
            
            # Render the page to a pixmap
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Convert to QImage
            img = QImage(
                pix.samples, 
                pix.width, 
                pix.height, 
                pix.stride, 
                QImage.Format.Format_RGB888
            )
            
            # Convert to QPixmap and set it
            self.page_widget.setPixmap(QPixmap.fromImage(img))
            
            # Update status bar
            self.status_bar.showMessage(
                self.tr(
                    "pdf_viewer.status.page_of", 
                    "Page {current} of {total} | {width} x {height} | {zoom:.0%}"
                ).format(
                    current=self.current_page + 1,
                    total=len(self.doc),
                    width=pix.width,
                    height=pix.height,
                    zoom=self.zoom
                )
            )
            
        except Exception as e:
            self.status_bar.showMessage(
                self.tr("pdf_viewer.errors.render_error", "Error rendering page: {error}").format(
                    error=str(e)
                )
            )
    
    def update_ui(self):
        """Update the UI based on the current state."""
        # Update page controls
        has_doc = self.doc is not None
        num_pages = len(self.doc) if has_doc else 0
        
        self.prev_page_btn.setEnabled(has_doc and self.current_page > 0)
        self.next_page_btn.setEnabled(has_doc and self.current_page < num_pages - 1)
        
        if has_doc:
            self.page_label.setText(
                self.tr("pdf_viewer.page_number", "Page {current} of {total}").format(
                    current=self.current_page + 1,
                    total=num_pages
                )
            )
        else:
            self.page_label.setText("")
        
        # Update zoom actions
        self.zoom_in_action.setEnabled(has_doc and self.zoom < 5.0)
        self.zoom_out_action.setEnabled(has_doc and self.zoom > 0.2)
        self.fit_width_action.setEnabled(has_doc)
        self.fit_page_action.setEnabled(has_doc)
        
        # Render the current page
        if has_doc:
            self.render_page()
        else:
            self.page_widget.clear()
            self.status_bar.clearMessage()
    
    # Navigation methods
    def next_page(self):
        """Go to the next page."""
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.update_ui()
    
    def prev_page(self):
        """Go to the previous page."""
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.update_ui()
    
    # Zoom methods
    def zoom_in(self):
        """Zoom in on the document."""
        if self.doc:
            self.zoom = min(5.0, self.zoom + 0.1)
            self.update_ui()
    
    def zoom_out(self):
        """Zoom out from the document."""
        if self.doc:
            self.zoom = max(0.1, self.zoom - 0.1)
            self.update_ui()
    
    def fit_width(self):
        """Fit the page width to the viewport."""
        if self.doc and self.scroll_area.width() > 0:
            page = self.doc.load_page(self.current_page)
            page_width = page.rect.width
            viewport_width = self.scroll_area.viewport().width() - 40  # Account for margins
            self.zoom = viewport_width / page_width
            self.update_ui()
    
    def fit_page(self):
        """Fit the entire page in the viewport."""
        if self.doc and self.scroll_area.height() > 0:
            page = self.doc.load_page(self.current_page)
            page_rect = page.rect
            viewport_size = self.scroll_area.viewport().size() - QSize(40, 100)  # Account for margins and controls
            
            # Calculate zoom to fit both width and height
            zoom_width = viewport_size.width() / page_rect.width
            zoom_height = viewport_size.height() / page_rect.height
            self.zoom = min(zoom_width, zoom_height)
            self.update_ui()
    
    # Event handlers
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # You could add auto-fitting here if desired
    
    def closeEvent(self, event):
        """Handle window close events."""
        # Close the document when the viewer is closed
        if hasattr(self, 'doc') and self.doc:
            self.doc.close()
        super().closeEvent(event)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events."""
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_Space:
                self.next_page()
                return True
            elif event.key() == Qt.Key.Key_Left or event.key() == Qt.Key.Key_Backspace:
                self.prev_page()
                return True
            elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                self.zoom_in()
                return True
            elif event.key() == Qt.Key.Key_Minus:
                self.zoom_out()
                return True
            elif event.key() == Qt.Key.Key_0:  # Reset zoom
                self.zoom = 1.0
                self.update_ui()
                return True
        
        return super().eventFilter(obj, event)

def show_pdf_viewer(file_path=None, parent=None, language_manager=None):
    """
    Show the PDF viewer with the specified file.
    
    Args:
        file_path: Path to the PDF file to open (optional)
        parent: Parent widget (optional)
        language_manager: Language manager for translations
    """
    viewer = PDFViewer(parent, language_manager)
    if file_path and os.path.isfile(file_path):
        viewer.open_file(file_path)
    viewer.show()
    return viewer

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # For testing
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = None
    
    viewer = show_pdf_viewer(file_path)
    sys.exit(app.exec())
