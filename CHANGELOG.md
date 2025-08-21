# Changelog

All notable changes to PDF Duplicate Finder will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.10.0] - 2025-08-21

### Added in 2.10.0

- Text-based PDF comparison for identifying duplicates with minor visual differences
- Advanced filtering options for file size, modification date, and name patterns
- Performance optimizations for scanning large PDF collections
- Updated help documentation with new features and usage instructions
- Added keyboard shortcuts for common actions
- Improved error handling and user feedback

### Changed in 2.10.0

- Enhanced duplicate detection algorithm for better accuracy
- Updated dependencies to their latest stable versions
- Improved memory management for large PDF files
- Optimized UI responsiveness during scanning operations

### Fixed in 2.10.0

- Fixed issue with certain PDF files not being properly compared
- Resolved memory leaks in the scanning process
- Fixed UI glitches in the file comparison view

## [2.9.0] - 2025-08-20

### Added in 2.9.0

- Settings dialog: Pre-flight backend checks with inline status labels
- Settings dialog: "Test backends" button to validate PyMuPDF and Ghostscript
- UI: File list automatically populates with scanned PDFs on scan completion
- Internationalization: Localized status-bar warning when selected backend fails and app falls back
- Implemented image-based comparison for scanned PDFs
- Implemented text diff for text-based PDFs
- Implemented backend status display in the status bar
- Export scan results to CSV from Tools menu
- Added settings to toggle permanent delete
- Added settings to toggle recycle bin
- Added settings to toggle language
- Added settings to toggle dark mode
- Added settings to toggle file info

### Changed

- Toolbar visual improvements: spacing, padding, right-aligned help actions, consistent stylesheet
- Scanner.py: Added Callable to typing imports

### Fixed

- Propagated backend fallback messages from PDF processing to the UI status bar
- Stabilized PDF rendering to avoid QPainter/QImage invalid paint device errors
- Fixed language manager
  - Fixed en.json
  - Fixed it.json
- Fixed delete selected files
- Fixed toggle permanent delete
- Fixed progress bar appearance

## [2.8.0] - 2025-08-17

### Added in 2.8.0

- Added tqdm progress bar for better user feedback during file processing
- Enhanced logging with more detailed progress information

### Changed in 2.8.0

- Updated dependencies in requirements.txt
- Improved error handling for file operations

### Fixed in 2.8.0

- Fixed module import error by adding tqdm to requirements
- Improved error handling for missing dependencies

## [2.7.3] - 2025-07-09

### Added in 2.7.3

- Migrated from PySide6 to PyQt6 for better compatibility and performance
- Added utility functions for consistent file path handling
- Improved error handling and logging
- Added more detailed error messages for file operations
- Added better handling of files in use by other applications

### Changed in 2.7.3

- Updated all UI components to use PyQt6 APIs
- Refactored file info handling to be more robust
- Updated dependencies to latest stable versions
- Improved file deletion with better error handling
- Enhanced recycle bin fallback mechanism

### Fixed in 2.7.3

- Fixed QPainter warnings and rendering issues
- Resolved file path handling inconsistencies
- Fixed log viewer filtering
- Fixed signal disconnection errors in scan completion
- Fixed handling of file previews with invalid PDFs

## [2.7.2] - 2025-07-09

### Added in v2.7.2

- Enhanced error handling for file operations
- Improved logging for better debugging
- Added more detailed progress feedback during scans

### Fixed in v2.7.2

- Fixed memory leaks in PDF processing
- Resolved issues with special characters in file paths
- Improved stability during large file processing
- Enhanced file deletion with improved error handling
- Added better handling of files in use by other applications
- Improved recycle bin fallback mechanism
- Added more detailed error messages for file operations

### Changed in 2.7.2

- Updated dependencies to latest stable versions
- Optimized memory usage for better performance

## [2.7.1] - 2025-07-08

### Added in 2.7.1

- Added blue buttons with white text for language selection in help dialog
- Improved help dialog layout and styling
- Added proper error handling for settings management
- Enhanced settings persistence

### Fixed in 2.7.1

- Fixed settings save/load functionality
- Resolved Qt object deletion warnings
- Fixed help dialog layout issues
- Improved error messages for better user feedback
- Fixed signal disconnection errors in scan completion
- Improved handling of file previews with invalid PDFs
- Updated deprecated PySide6 method calls

### Changed in 2.7.1

## [2.7.0] - 2025-07-03

### Added in 2.7.0

- Added application icon support
- Improved UI with better menu organization
- Added Tools menu with language selection
- Moved "Check for Updates" and "View Log" to Tools menu
- Added support for multiple language translations
- Enhanced error handling and logging
- New release of PDF Duplicate Finder

### Fixed in 2.7.0

- Fixed menu handling during language changes
- Resolved issues with Qt object deletion during UI updates
- Improved application stability during shutdown
- Fixed memory leaks in UI components

### Changed in 2.7.0

- Updated dependencies to latest stable versions
- Improved application startup time
- Enhanced dark theme support

## [2.6.3] - 2025-06-20

### Fixed in 2.6.3

- Fixed issue with file scanning on Windows
- Resolved problems with special characters in file paths

### Changed in 2.6.3

- Updated PDF processing library for better performance

## [2.6.0] - 2025-05-15

### Added in 2.6.0

- Initial public release
- Basic PDF duplicate detection
- Simple preview functionality
- Light/dark theme support

[2.8.0]: https://github.com/Nsfr750/PDF_finder/compare/v2.9.0...HEAD
[2.7.2]: https://github.com/Nsfr750/PDF_finder/compare/v2.7.1...v2.7.2
[2.7.1]: https://github.com/Nsfr750/PDF_finder/compare/v2.7.0...v2.7.1
[2.7.0]: https://github.com/Nsfr750/PDF_finder/releases/tag/v2.7.0
