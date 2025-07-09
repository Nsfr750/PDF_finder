"""
Version information for PDF Duplicate Finder.
"""

# Version information
__version__ = "2.7.2"
__version_info__ = tuple(int(num) if num.isdigit() else num 
                        for num in __version__.replace("-", ".", 1).split("."))

# Version history
VERSION_HISTORY = [
    {
        "version": "2.7.2",
        "date": "2025-07-09",
        "changes": [
            "Enhanced file deletion with improved error handling",
            "Added better handling of files in use by other applications",
            "Improved recycle bin fallback mechanism",
            "Added more detailed error messages for file operations"
        ]
    },
    {
        "version": "2.7.1",
        "date": "2025-07-08",
        "changes": [
            "Fixed signal disconnection errors in scan completion",
            "Improved handling of file previews with invalid PDFs",
            "Updated deprecated PySide6 method calls"
        ]
    },
    {
        "version": "2.7.0",
        "date": "2025-07-03",
        "changes": [
            "New release of PDF Duplicate Finder"
        ]
    }
]

def get_version():
    """Return the current version as a string."""
    return __version__

def get_version_info():
    """Return the version as a tuple for comparison."""
    return __version_info__

def get_version_history():
    """Return the version history."""
    return VERSION_HISTORY

def get_latest_changes():
    """Get the changes in the latest version."""
    if VERSION_HISTORY:
        return VERSION_HISTORY[0]['changes']
    return []

def is_development():
    """Check if this is a development version."""
    return "dev" in __version__ or "a" in __version__ or "b" in __version__

def get_codename():
    """Get the codename for this version."""
    # Simple codename based on version number
    major, minor, patch = map(int, __version__.split('.')[:3])
    codenames = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]
    return codenames[minor % len(codenames)]
