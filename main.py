#!/usr/bin/env python3
"""PDF Duplicate Finder - Main Application"""
import os
import sys
import logging
import traceback
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QSplitter, QStatusBar, QLabel, 
                           QLineEdit, QListWidget, QTextEdit, QStyleFactory)

from script.version import get_version
from script.logger import setup_logging
from script.menu import MenuManager
from script.toolbar import ToolbarManager
from script.language_manager import LanguageManager

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QProgressBar, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QFileDialog, QMessageBox, QMenuBar, 
    QMenu, QStyle, QTreeWidget, QTreeWidgetItem, QAbstractItemView, 
    QToolBar, QStatusBar, QCheckBox, QSpinBox, QDoubleSpinBox, 
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, 
    QTextEdit, QTabWidget, QGroupBox, QRadioButton, QButtonGroup, 
    QScrollArea, QFrame, QSizePolicy, QSpacerItem, QSystemTrayIcon, 
    QStyleFactory, QInputDialog, QListWidget, QListWidgetItem, 
    QStyledItemDelegate, QStyleOptionViewItem, QProgressDialog, 
    QToolButton, QSplashScreen, QTreeView, QMessageBox
)
from PyQt6.QtCore import (
    Qt, QSize, QThread, pyqtSignal as Signal, pyqtSlot as Slot, 
    QObject, QTimer, QSettings, QPoint, QEvent, QMimeData, 
    QUrl, QByteArray, QBuffer, QIODevice, QSizeF, QLocale, 
    QTranslator, QLibraryInfo, QRect
)
from PyQt6.QtGui import (
    QAction, QActionGroup, QIcon, QPixmap, QFont, 
    QColor, QPalette, QKeySequence, QDragEnterEvent, 
    QDropEvent, QImage, QImageReader, QPainter, QBrush, 
    QLinearGradient, QGradient, QTextCursor, QTextCharFormat, 
    QTextFormat, QTextLength, QTextBlockFormat, QTextDocument, 
    QTextFrameFormat, QTextImageFormat, QTextTableFormat, QTextTable,
    QScreen
)
from script.version import get_version
from script.view_log import show_log_viewer
from script.language_manager import LanguageManager
from script.settings import settings_manager
from script.logger import setup_logging, logger
from script.UI import PDFDuplicateFinderUI
from script.recents import RecentFilesManager
from script.gest_recent import RecentFoldersManager
from script.gest_scan import ScanManager

# Constants
APP_NAME = "PDF Duplicate Finder"
APP_VERSION = get_version()

def show_error(title: str, message: str):
    """Show an error message dialog.
    
    Args:
        title: The title of the error dialog
        message: The error message to display
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


# Set up logging
logger = setup_logging('PDFDuplicateFinder')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language_manager = LanguageManager()
        self.setWindowTitle(f"PDF Duplicate Finder {get_version()}")
        self.setMinimumSize(1024, 768)
        
        # Create the menu bar first
        self.create_menu_bar()
        
        # Apply the dark gold theme
        self.apply_dark_gold_theme()
        
        # Now set up the rest of the UI
        self.setup_ui()
    
    def create_menu_bar(self):
        """Create and set up the menu bar."""
        # Create menu manager
        self.menu_manager = MenuManager(self, self.language_manager)
        
        # Get the menu bar and set it
        menu_bar = self.menu_manager.get_menu_bar()
        self.setMenuBar(menu_bar)
        
        # Make sure the menu bar is visible
        menu_bar.setVisible(True)
        
        # Connect menu signals
        self.menu_manager.exit_triggered.connect(self.close)
        self.menu_manager.open_folder_triggered.connect(self.on_open_folder)
        self.menu_manager.view_log_triggered.connect(self.on_view_log)
        # Add more signal connections as needed
    
    def on_open_folder(self):
        """Handle open folder action."""
        print("Open folder action triggered")
        # Add your open folder logic here
    
    def on_view_log(self):
        """Handle view log action."""
        print("View log action triggered")
        # Add your view log logic here
    
    def apply_dark_gold_theme(self):
        """Apply the dark gold theme to the application."""
        # Set Fusion style for better dark theme support
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        # Dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(37, 37, 37))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(224, 224, 224))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(139, 117, 0))  # Gold
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(139, 117, 0))  # Gold
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        QApplication.setPalette(dark_palette)
        
        # Apply stylesheet for custom styling
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #252525;
                color: #e0e0e0;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: none;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                color: #e0e0e0;
            }
            QMenuBar::item:selected {
                background-color: #3a3a3a;
            }
            QMenuBar::item:pressed {
                background-color: #4e5254;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #555555;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3c3f41;
            }
            QStatusBar {
                background-color: #2d2d2d;
                border-top: 1px solid #555;
            }
        """)
    
    def setup_ui(self):
        """Set up the main UI components."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create toolbar
        self.toolbar_manager = ToolbarManager(self, self.language_manager)
        toolbar = self.toolbar_manager.get_toolbar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Search and duplicates list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Search:"))
        left_layout.addWidget(QLineEdit(placeholderText="Search duplicates..."))
        left_layout.addWidget(QLabel("Duplicate Files:"))
        left_layout.addWidget(QListWidget())
        
        # Right panel - File details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("File Details:"))
        right_layout.addWidget(QTextEdit())
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([self.width() // 3, 2 * self.width() // 3])
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Make sure the window is properly shown
        self.show()
    
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
