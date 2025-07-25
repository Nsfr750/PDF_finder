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
__build__ = "2.8.0"
__date__ = "2025-07-25"

# Version description
__description__ = "A tool to find and manage duplicate PDF files on your computer."

# Dependencies
__requires__ = [
    "PyQt6>=6.4.0",
    "PyMuPDF>=1.21.0",
    "wand>=0.6.10",
    "python-dotenv>=0.19.0"
]

# Changelog
__changelog__ = """
## [2.8.0] - 2025-07-25
### Added
- Added JSON-based settings storage in config/settings.json
- Implemented daily log rotation with 30-day retention
- Added translations support for log messages (English and Italian)
- New settings manager with improved error handling

### Changed
- Refactored settings management into dedicated SettingsManager class
- Moved logging configuration to script/logger.py
- Updated settings UI to support new configuration options
- Improved error handling and logging throughout the application

### Fixed
- Fixed issues with settings persistence
- Resolved log file permission issues on Windows
- Fixed translation loading for log messages

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
            "version": "2.8.0",
            "date": "2025-07-25",
            "changes": [
                "Added JSON-based settings storage in config/settings.json",
                "Implemented daily log rotation with 30-day retention",
                "Added translations support for log messages (English and Italian)",
                "New settings manager with improved error handling",
                "Refactored settings management into dedicated SettingsManager class",
                "Moved logging configuration to script/logger.py",
                "Updated settings UI to support new configuration options",
                "Improved error handling and logging throughout the application",
                "Fixed issues with settings persistence",
                "Resolved log file permission issues on Windows",
                "Fixed translation loading for log messages"
            ]
        },
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
    history = get_version_history()
    if history:
        return history[0]['changes']
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
