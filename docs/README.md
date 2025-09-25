# PDF Duplicate Finder

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Version: 3.0.0](https://img.shields.io/badge/version-3.0.0-brightgreen.svg)](https://github.com/Nsfr750/PDF_finder/releases)

A powerful tool to find and manage duplicate PDF files on your computer. PDF Duplicate Finder helps you identify and remove duplicate PDF documents, saving disk space and organizing your files more efficiently.

![screenshot](assets/screenshot.png)

## ✨ Features

- 🔍 **Smart PDF Comparison**: Find duplicate PDFs based on content, not just file names or sizes
- 📝 **Text-based Comparison**: Identify duplicates even with minor visual differences using advanced text analysis
- 👁 **Built-in PDF Viewer**: Preview PDFs directly within the application
- 📋 **Dual-View Interface**: View both file list and duplicates groups in separate tabs
- 🎯 **Advanced Filtering**: Filter by file size, modification date, and name patterns
- 🚀 **Fast Scanning**: Optimized algorithms for quick scanning of large PDF collections
- 🎨 **Intuitive UI**: Clean and user-friendly interface with light/dark theme support
- 🔄 **Batch Processing**: Process multiple files or entire folders at once
- 📊 **Detailed Analysis**: View file details, previews, and comparison results
- 🛠 **Advanced Tools**: Multiple selection modes, filtering, and sorting options
- 🌍 **Enhanced Multi-language Support**: Completely rewritten translation system using Python modules for better performance and maintainability with 12 supported languages
- 📊 **Progress Tracking**: Real-time progress bar for file processing operations
- ⏱ **Recent Files**: Quick access to recently opened files with context menu options
- 🐛 **Enhanced Stability**: Major bug fixes including duplicate tree population, PDF viewer issues, signal handling improvements, and file deletion functionality
- 🗂️ **Improved Code Organization**: Restructured codebase with better separation of concerns (UI, utils, lang modules)
- 🛡️ **Better Error Handling**: Comprehensive error handling and graceful degradation
- 🧹 **Maintenance Tools**: Built-in script for cleaning Python cache files (__pycache__ directories and .pyc files)

## 🆕 What's New in Version 3.0.0

### Major Improvements

- **Complete Codebase Refactoring**: Restructured the entire application with improved organization:
  - Moved all UI components to `script/UI/` subdirectory
  - Consolidated utility scripts in `script/utils/`
  - Organized language management in `script/lang/`
  - Updated all import statements for better maintainability

- **Completely Rewritten Translation System**: Migrated from JSON files to Python modules for better performance, maintainability, and error handling
  - Fixed path resolution issues in language manager
  - Enhanced translation loading with proper error handling
  - Support for 12 languages: English, Italian, German, French, Spanish, Portuguese, Russian, Ukrainian, Hebrew, Arabic, Japanese, Chinese

- **Critical Bug Fixes**: Resolved major issues that were affecting user experience and application stability
- **Enhanced UI Stability**: Fixed toolbar shifting, duplicate signal connections, and tree population issues
- **Improved Error Handling**: Better handling of QPainter errors and system-level Qt issues

### Key Bug Fixes

- **Fixed Duplicates Tree Population**: Resolved issue where size, modified, and similarity columns were not being populated correctly
- **Fixed PDF Viewer Double-Click Bug**: Eliminated problem where double-clicking opened 3 PDF viewers instead of 1
- **Fixed Toolbar Shifting**: Resolved UI layout issues during language changes
- **Fixed Translation System**: Eliminated "Translation key not found" errors and improved language switching
- **Fixed Signal Handling**: Resolved duplicate signal connections that were causing multiple handler executions
- **Fixed Import Structure**: Resolved all ModuleNotFoundError issues after code reorganization
- **Fixed File Deletion**: Resolved critical issue where file deletion functionality was not working correctly due to method overriding conflicts
  - Removed duplicate on_delete_selected method from main.py that was overriding the correct implementation
  - Fixed UI update logic to properly remove only files that were actually deleted
  - Added detailed logging for deletion operations and UI updates
- **Added Maintenance Script**: Created clean_pycache.py script for easy cleanup of Python cache files (__pycache__ directories and .pyc files)
  - Script supports dry-run mode, verbose output, and selective cleaning
  - Helps maintain clean project structure and reduce disk usage

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Optional backends for PDF rendering (Auto falls back safely):
  - PyMuPDF (fitz) — default and bundled via requirements
  - Ghostscript (for Wand) — install Ghostscript and set its executable path in Settings

See [PREREQUISITES.md](PREREQUISITES.md) for platform-specific setup.

### Install from source

1. Clone the repository:

   ```bash
   git clone https://github.com/Nsfr750/PDF_finder.git
   cd PDF_finder
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Launch the application:

   ```bash
   python main.py
   ```

2. Click "Scan Folder" to select a directory to scan for duplicate PDFs.

3. Review the results in the main window. After a scan completes, the file list is automatically populated with the scanned PDFs and duplicate groups.

4. Use the tools to manage duplicates:
   - Mark files to keep
   - Delete unwanted duplicates
   - Preview files before taking action

## Key Features in Detail

### Smart PDF Comparison

The application uses advanced text extraction and comparison algorithms to identify duplicate PDFs based on their content rather than just metadata. This means it can find duplicates even if:

- Files have different names
- Files have different creation/modification dates
- Files have slightly different visual formatting but identical text content

### Multi-language Support

Version 3.0.0 introduces comprehensive multi-language support with:

- **12 Supported Languages**: English, Italian, German, French, Spanish, Portuguese, Russian, Ukrainian, Hebrew, Arabic, Japanese, Chinese
- **Instant Language Switching**: Change languages without restarting the application
- **Professional Translations**: High-quality translations by native speakers
- **Automatic Detection**: Detects system language and defaults to it when available

### Enhanced User Interface

The completely redesigned interface offers:

- **Dual-View Layout**: Separate tabs for file list and duplicate groups
- **Advanced Filtering**: Filter by size, date, name patterns, and similarity thresholds
- **Context Menus**: Right-click actions for quick file operations
- **Progress Indicators**: Real-time feedback during scanning and processing
- **Theme Support**: Light and dark themes with system integration

### Performance Optimizations

Significant performance improvements in version 3.0.0:

- **Faster Scanning**: Optimized algorithms for quicker duplicate detection
- **Memory Efficiency**: Better memory management for large PDF collections
- **Caching**: Intelligent caching to speed up repeated operations
- **Background Processing**: Non-blocking operations for better responsiveness

## 📚 Documentation

- [User Guide](USER_GUIDE.md) - Comprehensive user documentation
- [Changelog](CHANGELOG.md) - Version history and changes
- [Contributing](CONTRIBUTING.md) - How to contribute to the project
- [Security Policy](SECURITY.md) - Security guidelines and vulnerability reporting
- [Project Structure](STRUCT.md) - Detailed project structure explanation
- [Prerequisites](PREREQUISITES.md) - System requirements and setup
- [To Do List](TO_DO.md) - Development roadmap and planned features

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 🐛 Reporting Issues

Found a bug? Please report it on our [GitHub Issues](https://github.com/Nsfr750/PDF_finder/issues) page.

## 📄 License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all the contributors who have helped improve this project
- The open-source libraries that make this project possible: PyQt6, PyMuPDF, Wand, and many others
- Our users for their valuable feedback and bug reports

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Nsfr750/PDF_finder/issues)
- **Discussions**: [Join our community discussions](https://github.com/Nsfr750/PDF_finder/discussions)
- **Email**: [nsfr750@yandex.com](mailto:nsfr750@yandex.com)
- **Discord**: [Join our Discord server](https://discord.gg/ryqNeuRYjD)

---

© Copyright 2025 Nsfr750 - All rights reserved
