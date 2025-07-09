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
        return VERSION_HISTORY[0]["changes"]
    return []

def is_development():
    """Check if this is a development version."""
    return "dev" in __version__ or "a" in __version__ or "b" in __version__

def get_codename():
    """Get the codename for this version."""
    # Add version codenames here if desired
    version_codenames = {
        "2.7.1": "Butterfly"
    }
    return version_codenames.get(__version__, "")
