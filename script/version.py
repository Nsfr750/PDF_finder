"""
Version information for PDF Duplicate Finder.
"""

# Version as a tuple (major, minor, patch)
VERSION = (3, 0, 0)

# String version
__version__ = ".".join(map(str, VERSION))

# Detailed version information
__status__ = "stable"
__author__ = "Nsfr750"
__maintainer__ = "Nsfr750"
__email__ = "nsfr750@yandex.com"
__license__ = "GPL-3.0"

# Build information
__build__ = ""
__date__ = "2025-09-21"

# Version description
__description__ = "A tool to find and manage duplicate PDF files on your computer."

# Dependencies
__requires__ = [
    "PyQt6>=6.4.0",
    "PyMuPDF>=1.21.0",
    "wand>=0.6.10",
    "PyPDF2>=3.0.0",
    "pdf2image>=1.17.0",
    "imagehash>=4.3.1",
    "python-dotenv>=0.19.0",
    "tqdm>=4.64.0"
]

# Changelog
__changelog__ = """
## [3.0.0] - 2025-09-21
### Added
- Converted Italian translations from JSON format (it.json) to Python module (it.py)
- Enhanced translation system with improved structure and organization
- Updated build date to September 21, 2025

### Fixed
- Fixed duplicates tree population issue where size, modified, and similarity columns were not being populated
- Fixed critical bug where double-clicking a result file opened 3 PDF viewers instead of 1
- Resolved duplicate signal connections that were triggering multiple handlers
- Improved UI stability and signal handling for better user experience

### Changed
- Improved translation loading performance by using Python modules instead of JSON files
- Enhanced code maintainability with better-structured translation data
- Updated version information and build metadata

## [2.12.0] - 2025-08-23
### Added
- Multi-selection support in file list (Shift+Click, Ctrl+Click)
- Context menu with Select All/Deselect All options
- Expand All/Collapse All buttons in Duplicates tab
- Improved keyboard navigation in file list
- Visual feedback for selection actions

### Fixed
- QAction import issue in PyQt6
- Improved UI responsiveness during file operations

## [2.11.0] - 2025-08-23
### Added
- Integrated PDF viewer for previewing files
- Duplicate file list in the main tab
- Enhanced error handling for PDF operations
- Visual feedback when opening PDF files
- Improved file path handling

### Fixed
- CSV export functionality

## [2.10.0] - 2025-08-21
### Added
- Text-based PDF comparison
- Advanced filtering options
- Performance optimizations
- Keyboard shortcuts

## [2.9.0] - 2025-08-20
### Added
- Export scan results to CSV from Tools menu

### Fixed
- Stabilized PDF rendering to avoid QPainter/QImage invalid paint device errors

## [2.8.0] - 2025-08-17
### Added
- Added tqdm progress bar for better user feedback during file processing
- Enhanced logging with more detailed progress information

### Changed
- Updated dependencies in requirements.txt
- Improved error handling for file operations

### Fixed
- Fixed module import error by adding tqdm to requirements
- Improved error handling for missing dependencies

## [2.7.3] - 2025-07-09
### Added
- Migrated from PySide6 to PyQt6 for better compatibility and performance
- Added utility functions for consistent file path handling
- Improved error handling and logging

### Changed
- Updated all UI components to use PyQt6 APIs
- Refactored file info handling to be more robust
- Updated dependencies to latest stable versions

### Fixed
- Fixed QPainter warnings and rendering issues
- Resolved file path handling inconsistencies
- Fixed log viewer filtering
"""

def get_version():
    """Return the current version as a string."""
    return __version__

def get_version_info():
    """Return the version as a tuple for comparison."""
    return VERSION

def get_version_history():
    """Return the version history."""
    return [
        {
            "version": "3.0.0",
            "date": "2025-09-21",
            "changes": [
                "Converted Italian translations from JSON format (it.json) to Python module (it.py)",
                "Enhanced translation system with improved structure and organization",
                "Updated build date to September 21, 2025",
                "Fixed duplicates tree population issue where size, modified, and similarity columns were not being populated",
                "Fixed critical bug where double-clicking a result file opened 3 PDF viewers instead of 1",
                "Resolved duplicate signal connections that were triggering multiple handlers",
                "Improved UI stability and signal handling for better user experience",
                "Improved translation loading performance by using Python modules instead of JSON files",
                "Enhanced code maintainability with better-structured translation data",
                "Updated version information and build metadata"
            ]
        },
        {
            "version": "2.12.0",
            "date": "2025-08-23",
            "changes": [
                "Added multi-selection support in file list (Shift+Click, Ctrl+Click)",
                "Added context menu with Select All/Deselect All options",
                "Added Expand All/Collapse All buttons in Duplicates tab",
                "Improved keyboard navigation in file list",
                "Added visual feedback for selection actions",
                "Fixed QAction import issue in PyQt6",
                "Improved UI responsiveness during file operations"
            ]
        },
        {
            "version": "2.11.0",
            "date": "2025-08-23",
            "changes": [
                "Integrated PDF viewer for previewing files",
                "Added duplicate file list in the main tab",
                "Enhanced error handling and logging for PDF operations",
                "Added visual feedback when opening PDF files",
                "Improved file path handling for cross-platform compatibility",
                "Fixed CSV export functionality"
            ]
        },
        {
            "version": "2.10.0",
            "date": "2025-08-21",
            "changes": [
                "Added text-based PDF comparison",
                "Added advanced filtering options",
                "Performance optimizations for large PDF collections",
                "Added keyboard shortcuts for common actions"
            ]
        },
        {
            "version": "2.9.0",
            "date": "2025-08-20",
            "changes": [
                "Export scan results to CSV from Tools menu",
                "Stabilized PDF rendering to avoid QPainter/QImage invalid paint device errors"
            ]
        },
        {
            "version": "2.7.3",
            "date": "2025-07-09",
            "changes": [
                "Migrated from PySide6 to PyQt6",
                "Improved file path handling",
                "Enhanced error handling and logging",
                "Updated UI components to PyQt6",
                "Fixed various rendering and performance issues"
            ]
        }
    ]

def get_latest_changes():
    """Get the changes in the latest version."""
    if get_version_history():
        return get_version_history()[0]['changes']
    return []

def is_development():
    """Check if this is a development version."""
    return "dev" in __version__ or "a" in __version__ or "b" in __version__

def get_codename():
    """Get the codename for this version."""
    # Simple codename based on version number
    major, minor, patch = VERSION
    codenames = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]
    return codenames[minor % len(codenames)]
