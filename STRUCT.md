# PDF Duplicate Finder - Project Structure

This document provides an overview of the PDF Duplicate Finder project structure, explaining the purpose and organization of each directory and key file.

## Root Directory Structure

```
PDF_finder/
├── main.py                 # Application entry point
├── pyproject.toml          # Modern Python project configuration
├── setup.py                # Traditional Python setup configuration
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── LICENSE                 # GPL-3.0 license file
├── CHANGELOG.md            # Version history and changes
├── CONTRIBUTING.md         # Contribution guidelines
├── SECURITY.md             # Security policy
├── USER_GUIDE.md           # User documentation
├── PREREQUISITES.md        # System requirements
├── TO_DO.md                # Development roadmap and tasks
├── Setup.txt               # Setup instructions
├── installer.nsi           # NSIS installer script for Windows
├── nuitka_build_win.py     # Nuitka build script for Windows
├── nuitka_config.toml      # Nuitka configuration file
├── publish_to_pypi.py      # PyPI publishing automation script
├── .gitignore              # Git ignore rules
├── .github/                # GitHub configuration files
├── .vscode/                # VS Code configuration
├── assets/                 # Static assets and resources
├── config/                 # Configuration files
├── script/                 # Core application modules
├── tests/                  # Test files
├── build/                  # Build artifacts
├── dist/                   # Distribution files
├── dist-nuitka/            # Nuitka build output
├── logs/                   # Application logs
├── venv/                   # Virtual environment
└── PDF/                    # PDF-related resources
```

## Core Application Modules (script/)

The `script/` directory contains all the core application logic:

```
script/
├── __init__.py                     # Package initialization
├── main_window.py                  # Main application window
├── ui.py                           # User interface components
├── menu.py                         # Menu system
├── toolbar.py                      # Toolbar management
├── scanner.py                      # PDF scanning engine
├── pdf_utils.py                    # PDF utility functions
├── pdf_comparator.py               # PDF comparison logic
├── pdf_comparison.py               # PDF comparison algorithms
├── cache_manager.py                # Cache management system
├── hash_cache.py                   # Hash-based caching
├── simple_lang_manager.py          # Language management system
├── lang/                           # Language translation files
├── settings.py                     # Application settings
├── settings_dialog.py              # Settings dialog
├── progress_dialog.py              # Progress tracking dialog
├── filter_dialog.py                # Filter options dialog
├── filters.py                      # Filter logic
├── delete.py                       # File deletion operations
├── recents.py                      # Recent files management
├── gest_recent.py                  # Recent files gesture handling
├── gest_scan.py                    # Scan gesture handling
├── search_dup.py                   # Duplicate search functionality
├── advanced_scan.py                # Advanced scanning options
├── advanced_scanner.py             # Advanced scanning engine
├── text_processor.py               # Text processing utilities
├── utils.py                        # General utility functions
├── drag_drop.py                    # Drag and drop functionality
├── PDF_viewer.py                   # PDF viewer integration
├── about.py                        # About dialog
├── help.py                         # Help system
├── sponsor.py                      # Sponsor information
├── updates.py                      # Update checking system
├── logger.py                       # Logging system
├── view_log.py                     # Log viewer
└── version.py                      # Version information
```

### Language System (script/lang/)

```
script/lang/
├── __init__.py                     # Language package initialization
├── en.py                           # English translations
├── it.py                           # Italian translations
├── es.py                           # Spanish translations
├── fr.py                           # French translations
├── de.py                           # German translations
├── ru.py                           # Russian translations
├── ua.py                           # Ukrainian translations
├── pt.py                           # Portuguese translations
├── ja.py                           # Japanese translations
├── zh.py                           # Chinese translations
├── ar.py                           # Arabic translations
└── he.py                           # Hebrew translations
```

## Static Assets (assets/)

```
assets/
├── icon.ico                        # Application icon (Windows)
├── icon.png                        # Application icon (PNG format)
├── logo.png                        # Application logo
├── screenshot.png                  # Application screenshot
└── version_info.txt                # Version information file
```

## Configuration Files (config/)

```
config/
├── settings.json                   # Application settings
└── updates.json                    # Update configuration
```

## Build and Distribution

### Nuitka Build Configuration

- **nuitka_build_win.py**: Windows build script that compiles Python to standalone executable
- **nuitka_config.toml**: Nuitka configuration with package includes, data files, and build settings

### PyPI Publishing

- **publish_to_pypi.py**: Automated script for building and publishing to PyPI
- **pyproject.toml**: Modern Python project configuration with build system and metadata
- **setup.py**: Traditional Python setup script for backward compatibility

### Windows Installer

- **installer.nsi**: NSIS script for creating Windows installer with proper file placement and shortcuts

## Testing

```
tests/
├── test_import.py                  # Import validation tests
├── test_cache_manager_fix.py       # Cache manager tests
├── test_hash_cache.py              # Hash cache functionality tests
└── ...                             # Additional test files
```

## Key Architectural Components

### 1. Application Core
- **main.py**: Entry point that initializes the application, sets up logging, and starts the main window
- **main_window.py**: Main application window that coordinates all UI components and business logic

### 2. User Interface
- **ui.py**: Core UI components including file lists, duplicate trees, and status displays
- **menu.py**: Menu system with actions and shortcuts
- **toolbar.py**: Toolbar with quick access buttons
- **progress_dialog.py**: Progress tracking for long operations

### 3. PDF Processing
- **scanner.py**: Main scanning engine for finding duplicates
- **pdf_utils.py**: PDF file manipulation utilities
- **pdf_comparator.py**: PDF comparison algorithms
- **pdf_comparison.py**: Advanced comparison logic

### 4. Performance Optimization
- **cache_manager.py**: Manages scanning cache for performance
- **hash_cache.py**: Hash-based caching system
- **advanced_scanner.py**: Optimized scanning algorithms

### 5. Internationalization
- **simple_lang_manager.py**: Language management system
- **lang/**: Translation files for multiple languages
- **script/simple_translations.py**: Simple translation system (if exists)

### 6. Configuration and Settings
- **settings.py**: Settings management
- **settings_dialog.py**: Settings UI
- **config/**: Configuration files

### 7. File Operations
- **delete.py**: Safe file deletion with recycle bin integration
- **recents.py**: Recent files management
- **drag_drop.py**: Drag and drop functionality

### 8. Help and Support
- **help.py**: Help system and documentation
- **about.py**: About dialog with version and author information
- **sponsor.py**: Sponsor information

## Data Flow

1. **Application Startup**: `main.py` → Initialize logging → Load settings → Create main window
2. **User Interaction**: UI events → Menu/Toolbar actions → Business logic → File operations
3. **Scanning Process**: User selects folder → Scanner processes files → Cache stores results → UI displays duplicates
4. **Language Switching**: User changes language → Language manager loads translations → UI updates text
5. **Settings Management**: User modifies settings → Settings saved → Application behavior updated

## Build Process

### Nuitka Build
1. Clean previous builds (`dist-nuitka/`)
2. Read version information from `script/version.py`
3. Compile Python code to standalone executable
4. Include data files (assets, config, lang)
5. Package with Windows icon and metadata
6. Output to `dist/PDF-Finder_3.0.0.exe`

### PyPI Publishing
1. Validate project structure and requirements
2. Clean build artifacts
3. Build package using `python -m build`
4. Validate package with `twine check`
5. Upload to PyPI (test or production)

### Windows Installer
1. Check for built executable
2. Copy executable and resources
3. Create start menu shortcuts
4. Set up uninstaller
5. Handle file associations

## Dependencies

Key Python packages used:
- **PyQt6**: GUI framework
- **PyMuPDF**: PDF processing
- **tqdm**: Progress bars
- **send2trash**: Safe file deletion
- **psutil**: System utilities
- **PyQt6-QtPdf**: PDF viewing support

## Development Guidelines

1. **Code Organization**: Keep related functionality in separate modules
2. **Internationalization**: All user-facing text should use the translation system
3. **Error Handling**: Implement proper error handling and logging
4. **Performance**: Use caching for expensive operations
5. **Testing**: Write tests for new functionality
6. **Documentation**: Update documentation for new features

This structure ensures maintainability, scalability, and proper separation of concerns for the PDF Duplicate Finder application.
