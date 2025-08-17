"""
Version information for PDF Duplicate Finder.
"""

# Version as a tuple (major, minor, patch)
VERSION = (2, 8, 0)

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
__date__ = "2025-08-17"

# Version description
__description__ = "A tool to find and manage duplicate PDF files on your computer."

# Dependencies
__requires__ = [
    "PyQt6>=6.4.0",
    "PyMuPDF>=1.21.0",
    "Pillow>=9.0.0",
    "python-dotenv>=0.19.0",
    "tqdm>=4.64.0"
]

# Changelog
__changelog__ = """
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
            "version": "2.7.3",
            "date": "2025-07-09",
            "changes": [
                "Migrated from PySide6 to PyQt6 for better compatibility and performance",
                "Added utility functions for consistent file path handling",
                "Improved error handling and logging",
                "Updated all UI components to use PyQt6 APIs",
                "Refactored file info handling to be more robust",
                "Updated dependencies to latest stable versions",
                "Fixed QPainter warnings and rendering issues",
                "Resolved file path handling inconsistencies",
                "Fixed log viewer filtering"
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
