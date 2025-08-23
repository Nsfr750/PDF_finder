"""
PDF Duplicate Finder - Script Package

This package contains the main application modules for the PDF Duplicate Finder.
"""

# This file makes Python treat the directory as a package
# All the application modules are imported here for easier access

# Import main components
from .main_window import MainWindow
from .menu import MenuBar
from .toolbar import MainToolBar
from .settings_dialog import SettingsDialog
from .help import HelpDialog

# Version information
__version__ = '2.10.0'
__author__ = 'Nsfr750'
__email__ = 'nsfr750@yandex.com'

# Define what gets imported with 'from script import *'
__all__ = [
    'MainWindow',
    'MenuBar',
    'ToolBar',
    'SettingsDialog',
    'HelpDialog'
]
