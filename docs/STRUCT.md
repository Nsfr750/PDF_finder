# PDF Duplicate Finder - Project Structure

This document provides an overview of the PDF Duplicate Finder project structure, explaining the purpose and organization of each directory and key file.

## Root Directory Structure

```
PDF_finder/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── LICENSE                     # GPL-3.0 license file
├── .gitignore                  # Git ignore rules
├── .github/                    # GitHub configuration files
├── .vscode/                    # VS Code configuration
├── assets/                     # Static assets and resources
├── config/                     # Configuration files
├── script/                     # Core application modules
├── tests/                      # Test files
└── logs/                       # Application logs
```

## Core Application Modules (script/)

The `script/` directory contains all the core application logic:

```
script/
├── __init__.py                     # Package initialization
├── UI/                             # User interface components
│   ├── __init__.py                 # UI package initialization
│   ├── about.py                    # About dialog
│   ├── cache_manager.py            # Cache management system
│   ├── filter_dialog.py            # Filter options dialog
│   ├── help.py                     # Help system
│   ├── main_window.py              # Main application window
│   ├── menu.py                     # Menu system
│   ├── PDF_viewer.py               # PDF viewer integration
│   ├── progress_dialog.py          # Progress tracking dialog
│   ├── settings_dialog.py          # Settings dialog
│   ├── sponsor.py                  # Sponsor information
│   ├── toolbar.py                  # Toolbar management
│   ├── ui.py                       # Core UI components
│   └── view_log.py                 # Log viewer
├── utils/                          # Utility modules
│   ├── __init__.py                 # Utils package initialization
│   ├── advanced_scan.py            # Advanced scanning options
│   ├── advanced_scanner.py         # Advanced scanning engine
│   ├── delete.py                   # File deletion operations
│   ├── drag_drop.py                # Drag and drop functionality
│   ├── filter.py                   # Filter logic
│   ├── gest_recent.py              # Recent files gesture handling
│   ├── gest_scan.py                # Scan gesture handling
│   ├── hash_cache.py               # Hash-based caching
│   ├── logger.py                   # Logging system
│   ├── pdf_comparator.py           # PDF comparison logic
│   ├── pdf_comparison.py           # PDF comparison algorithms
│   ├── pdf_utils.py                # PDF utility functions
│   ├── recents.py                  # Recent files management
│   ├── scanner.py                  # PDF scanning engine
│   ├── search_dup.py               # Duplicate search functionality
│   ├── settings.py                 # Application settings
│   ├── text_processor.py           # Text processing utilities
│   ├── updates.py                  # Update checking system
│   ├── urils.py                    # Utility functions
│   └── version.py                  # Version information
└── lang/                           # Language and translation system
    ├── __init__.py                 # Language package initialization
    ├── lang_manager.py             # Language management system
    └── LANG-FILES                  # Translation data (Python module)
```

### Language System (script/lang/)

```
script/lang/
├── __init__.py                     # Language package initialization
├── lang_manager.py                 # Enhanced language management system
├── ar.py                           # Arabic language translations
├── en.py                           # English language translations
├── it.py                           # Italian language translations
├── es.py                           # Spanish language translations
├── fr.py                           # French language translations
├── de.py                           # German language translations
├── pt.py                           # Portuguese language translations
├── ru.py                           # Russian language translations
├── uk.py                           # Ukrainian language translations
├── ja.py                           # Japanese language translations
├── zh.py                           # Chinese language translations
└── he.py                           # Hebrew language translations
    
```

## Static Assets (assets/)

```
assets/
├── icon.ico                        # Application icon (Windows)
├── icon.png                        # Application icon (PNG format)
├── logo.png                        # Application logo
├── screenshot.png                  # Application screenshot
├── main_interface.png              # Application main interface
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
- **script/lang/lang_manager.py**: Enhanced language management system
- **script/lang/translations.py**: Translation data as Python module
- **12 languages supported**: English, Italian, Spanish, French, German, Portuguese, Russian, Ukrainian, Japanese, Chinese, Arabic, Hebrew

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

1. **Application Startup**: `main.py` → Initialize logging (`script/logger.py`) → Load settings (`script/utils/settings.py`) → Create main window (`script/UI/main_window.py`)
2. **User Interaction**: UI events (`script/UI/`) → Menu/Toolbar actions (`script/menu.py`, `script/UI/toolbar.py`) → Business logic (`script/utils/`) → File operations
3. **Scanning Process**: User selects folder → Scanner processes files (`script/utils/scanner.py`) → Cache stores results (`script/utils/cache_manager.py`) → UI displays duplicates (`script/UI/ui.py`)
4. **Language Switching**: User changes language → Language manager loads translations (`script/lang/lang_manager.py`) → UI updates text
5. **Settings Management**: User modifies settings → Settings saved (`script/utils/settings.py`) → Application behavior updated

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

1. **Code Organization**: Follow the modular structure with clear separation:
   - `script/UI/`: All user interface components
   - `script/utils/`: Utility modules and business logic
   - `script/lang/`: Language and translation system
   - Keep related functionality in separate modules
2. **Internationalization**: All user-facing text should use the translation system via `script/lang/lang_manager.py`
3. **Error Handling**: Implement proper error handling and logging using `script/logger.py`
4. **Performance**: Use caching for expensive operations via `script/utils/cache_manager.py`
5. **Testing**: Write tests for new functionality in the `tests/` directory
6. **Documentation**: Update documentation for new features in the `docs/` directory
7. **Import Structure**: Use proper relative imports within packages (e.g., `from .utils.scanner import PDFScanner`)
8. **Version Management**: Update version information in `script/version.py` following Semantic Versioning 2.0.0

This structure ensures maintainability, scalability, and proper separation of concerns for the PDF Duplicate Finder application.
