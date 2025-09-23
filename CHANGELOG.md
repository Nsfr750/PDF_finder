# Changelog

All notable changes to PDF Duplicate Finder will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-09-21

### Added in 3.0.0

- **Complete Translation System Rewrite**
  - Converted translations from JSON format (en.json/it.json) to Python module (simple_translations.py) for better performance and maintainability
  - Created simple_lang_manager.py with enhanced SimpleLanguageManager class
  - Improved translation loading performance and error handling
  - Added backward compatibility method get_current_language() as alias to get_language()
  - Enhanced translation system with better structure and organization

- **Enhanced Error Handling**
  - Added comprehensive error handling for QPainter errors in icon rendering
  - Improved error handling around Qt style operations to gracefully handle system-level issues
  - Added fallback mechanisms for translation key lookups with proper error logging

### Fixed in 3.0.0

- **Critical Bug Fixes**
  - Fixed duplicates tree population issue where size, modified, and similarity columns were not being populated
    - Resolved problem where _update_duplicates_list method was trying to populate non-existent 'duplicates_list' (QListWidget)
    - Fixed by properly using 'duplicates_tree' (QTreeWidget) defined in ui.py
    - Removed duplicate standalone _update_duplicates_list function outside MainWindow class
    - Added proper initialization of self.duplicate_groups = [] in MainWindow __init__ method
    - Updated method to call self.main_ui.update_duplicates_tree(self.duplicate_groups) correctly

  - Fixed critical bug where double-clicking a result file opened 3 PDF viewers instead of 1
    - Resolved duplicate signal connections that were triggering multiple handlers
    - Removed duplicate itemDoubleClicked and itemActivated connections in main_window.py
    - UI layer now properly handles double-click events without conflicts
    - Fixed signal connections at lines 61 (ui.py) and 149 (ui.py) vs 398-399 (main_window.py)

  - Fixed toolbar shifting issue when changing languages
    - Resolved problem where _build_toolbar() method added new spacer widgets without removing previous ones
    - Added self.spacer_widget = None to track spacer widget in __init__ method
    - Modified _build_toolbar() to properly remove existing spacer widget before creating new one
    - Used removeWidget() and deleteLater() to properly clean up old spacer widgets

- **Translation System Fixes**
  - Fixed all "Translation key not found" errors by updating translation keys to match actual calls in code
    - Removed "ui." prefix from translation keys to match direct calls in menu.py
    - Added missing translation keys for all menu items, dialog messages, and status messages
    - Added comprehensive translations for both English and Italian languages
    - Fixed translation system to work without any "Translation key not found" warnings

  - Fixed language translation issue where menu and UI elements were not being translated when language changed
    - Added translation_keys dictionary to store original translation keys for all UI elements
    - Modified UI setup to store translation keys for labels, buttons, tabs, and actions
    - Updated on_language_changed method to use stored translation keys instead of retranslating existing text
    - Added call to UI's on_language_changed method in main window's on_language_changed method

  - Fixed AttributeError for 'get_current_language' method in SimpleLanguageManager
    - Added get_current_language() as alias to get_language() for backward compatibility
    - Ensured translation system works correctly with existing components expecting get_current_language() method

  - Fixed ModuleNotFoundError for 'script.simple_lang_manager'
    - Created missing simple_lang_manager.py file with complete SimpleLanguageManager functionality
    - Added language initialization, validation, switching with signal emission
    - Implemented translation lookup with fallback logic (current language -> default language -> English)
    - Added available languages retrieval functionality

  - Removed language selection from settings dialog as per requirements
    - Removed language_changed signal from SettingsDialog class
    - Removed language_combo from setup_general_tab method
    - Removed language loading/saving code from load_settings and save_settings methods
    - Removed initial_language variable and related initialization code
    - Removed restart message when language was changed
    - Simplified on_show_settings method by removing language change handling logic

### Changed in 3.0.0

- **Major Architecture Changes**
  - Improved translation loading performance by using Python modules instead of JSON files
  - Enhanced code maintainability with better-structured translation data
  - Updated version information and build metadata to September 21, 2025
  - Improved overall application stability and error handling

- **Code Quality Improvements**
  - Enhanced error handling throughout the application
  - Improved signal connection management to prevent duplicate handlers
  - Better resource management with proper widget cleanup
  - Enhanced logging and debugging capabilities

- **User Experience Improvements**
  - More stable UI behavior during language changes
  - Better error messages and user feedback
  - Improved application responsiveness
  - Enhanced stability for PDF viewer operations

## [2.12.0] - 2025-08-23

### Added in 2.12.0

- Added Recent Files panel in the right sidebar for quick access to recently opened files
- Implemented context menu for recent files with Open, Remove, and Show in Explorer options
- Added Clear All button to clear recent files history
- Files are automatically added to recent list when opened
- Limited to 10 most recent files for better performance
- Added multi-selection support in file list (Shift+Click, Ctrl+Click)
- Added context menu with Select All/Deselect All options
- Added Expand All/Collapse All buttons in Duplicates tab
- Improved keyboard navigation in file list
- Added visual feedback for selection actions
- Improved update dialog with collapsible release notes

### Fixed

- Improved UI layout with proper splitter between file list and recent files
- Fixed tooltips to show full file paths in recent files list
- Better handling of file paths with special characters
- Fixed QAction import issue in PyQt6
- Improved UI responsiveness during file operations
- Fixed update dialog layout and spacing issues
- Removed progress bar from update dialog for cleaner UI

## [2.11.0] - 2025-08-23

### Added in 2.11.0

- Integrated PDF viewer for previewing files directly in the application
- Added duplicate file list in the main tab for better accessibility
- Enhanced error handling and logging for PDF operations
- Added visual feedback when opening PDF files
- Improved file path handling for cross-platform compatibility

### Fixed in 2.11.0

- Fixed CSV export

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

### Fixed in 2.9.0

- Propagated backend fallback messages from PDF processing to the UI status bar
- Stabilized PDF rendering to avoid QPainter/QImage invalid paint device errors
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
