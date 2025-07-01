# Changelog

All notable changes to the PDF Duplicate Finder project will be documented in this file.

## [2.6.3] - 2025-07-01

### Bug Fixes in 2.6.3

- **File Handling**
  - Fixed CSV file saving functionality
  - Resolved path handling issues in ScanManager
  - Improved error handling for file operations

- **User Interface**
  - Enhanced error messages for file operations
  - Improved status feedback during file operations

## [2.6.2] - 2025-06-29

### Bug Fixes in 2.6.2

- **File Handling**
  - Fixed file saving and loading functionality
  - Improved error handling for JSON operations
  - Resolved issues with file path handling on Windows

- **User Interface**
  - Fixed PDF preview updating when selecting files
  - Improved error messages for better user feedback

## [2.6.1] - 2025-06-29

### Bug Fixes in 2.6.1

- **Import System**
  - Fixed module import conflicts with Python's built-in `struct` module
  - Renamed `struct` package to `app_struct` to prevent naming conflicts
  - Updated all internal imports to use the new package name

### Dependencies

- **Updated Dependencies**
  - Moved pymupdf to main dependencies as it's required for core functionality
  - Added pytest-cov for test coverage reporting
  - Updated development dependencies to their latest stable versions

### Development Tools

## [2.6.0] - 2025-06-28

### New Features

- **Update System Improvements**
  - Fixed automatic update checking functionality
  - Enhanced error handling and user feedback
  - Improved version comparison logic
  - Added automatic update check on startup

### Dependency Management

- **Updated Dependencies**
  - Added python-dotenv for better configuration management
  - Included Windows-specific dependencies for improved compatibility
  - Updated minimum required versions for security patches

### Documentation Updates

- **Content Updates**
  - Updated help documentation with new features
  - Enhanced README with better feature descriptions
  - Added comprehensive installation instructions
  - Improved code documentation

## [2.5.0] - 2025-06-27

### Language Support

- Added multi-language support with 6 languages:
  - English
  - Italian
  - Spanish
  - Portuguese
  - Russian
  - Arabic (with RTL support)
- Language selection from View > Language menu
- Automatic saving of language preference

### Menu System

- Refactored menu system for better maintainability
- Added Recent Folders menu with keyboard shortcuts (Ctrl+1 to Ctrl+9)
- Added Undo functionality for file deletions (Ctrl+Z)
- Improved menu organization and accessibility

## [2.4.0] - 2025-06-23

### Update System

- Automatic update check on application startup
- Manual update check via Help menu
- Support for downloading new versions directly from GitHub
- User notifications for available updates

## [2.3.0] - 2025-05-20

### Theme and UI Improvements

- Added theme support with light and dark modes
- Implemented theme preferences persistence between sessions
- Added new View menu for theme selection
- Improved horizontal scrolling support for the file list
- Added keyboard shortcuts for common actions
- Added configuration file for user preferences

## [2.2.0] - 2025-05-20

### Documentation

- Comprehensive help system with user guide
- About dialog showing version information
- Support and sponsorship options
- CHANGELOG.md to track project changes

### Code Organization

- Renamed main application file from `PDF_Finder.py` to `main.py`
- Reorganized menu structure to group related items under "Help"
- Improved code organization with separate modules for different components

### Bug Fixes in 2.2.0

- Fixed potential memory leaks in PDF preview handling
- Improved error handling during PDF processing

## [2.1.0] - 2025-05-15

### Initial Release

- Basic duplicate detection functionality
- Image and text preview capabilities
- File management features
