# PDF Duplicate Finder

[![GitHub release](https://img.shields.io/badge/release-v2.6.2-green.svg?style=for-the-badge)](https://github.com/Nsfr750/PDF_finder/releases/latest)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/Nsfr750/PDF_finder/graphs/commit-activity)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-green?style=for-the-badge)](https://github.com/Nsfr750/PDF_finder/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen?style=for-the-badge)](https://codecov.io/gh/Nsfr750/PDF_finder)

![PDF Finder Screenshot](images/screenshot.png)

A Python application that helps you find and remove duplicate PDF files based on their content. Features an advanced preview system that allows you to verify duplicates before deletion, with a customizable interface that includes light and dark themes.

## What's New in v2.6.2

### Bug Fixes in v2.6.2

- Fixed file saving and loading functionality
- Improved error handling for JSON operations
- Resolved issues with file path handling on Windows
- Fixed PDF preview updating when selecting files

### Improvements in v2.6.2

- Enhanced error messages for better user feedback
- Improved file handling reliability
- Better Windows compatibility

## Previous Version (v2.6.1)

### Bug Fixes in v2.6.1

- Resolved module import conflicts with Python's standard library
- Fixed package structure for better maintainability

### Improvements in v2.6.1

- Improved code organization and module structure
- Updated dependencies to their latest stable versions

## Features

### Smart Duplicate Detection

- Content-based comparison for accurate results
- Support for both text and image-based comparison
- Fast scanning with progress tracking
- Batch processing for large collections
- Configurable comparison sensitivity

### Modern User Interface

- Light and dark theme support with automatic switching
- Responsive layout that adapts to window size
- Horizontal scrolling for long file paths
- Comprehensive keyboard shortcuts
- Multi-language support (6+ languages)
- Recent folders with quick access

### Advanced PDF Preview

- Image preview with page navigation
- Text content extraction view
- High-quality rendering with LANCZOS resampling
- Automatic image scaling

### User Experience

- Theme preferences saved between sessions
- Intuitive menu organization
- Comprehensive help system
- About dialog with version information
- Support and sponsorship options

### Performance & Reliability

- Efficient memory management for large PDF collections
- Background processing to keep UI responsive
- Cancel long-running operations at any time
- Automatic recovery from errors
- Optimized for both SSD and HDD storage

## What's New in v2.6.0

### Improved Update System

- Fixed automatic update checking
- Better error handling and user feedback
- Smoother update experience

### Enhanced Stability

- Fixed various crash issues
- Improved error recovery
- Better handling of corrupted PDFs

### Dependency Updates

- Updated to latest library versions
- Added Windows-specific optimizations
- Better compatibility with Python 3.10+

## Previous Versions

### v2.5.0

#### Multi-language Support

- Added support for English, Italian, Spanish, Portuguese, Russian, and Arabic
- Language selection from the View menu
- Automatic saving of language preference
- Right-to-Left (RTL) support for Arabic

#### Improved Menu System

- Refactored menu code for better maintainability
- Added Recent Folders menu with keyboard shortcuts
- Undo functionality for file deletions
- Better organization of menu items

### Previous Updates

#### v2.4.0
- Automatic update checks on startup
- Manual update check via Help menu
- User notifications for available updates
- Direct download of new versions from GitHub

#### v2.3.0
- Added light and dark theme support
- Theme preferences are now saved between sessions
- New View menu for theme selection
- Improved horizontal scrolling for file lists
- Added keyboard shortcuts for better productivity
- Configuration file for user preferences

## Requirements

### Software Requirements

- Python 3.x
- Operating System: Windows, macOS, or Linux

### Python Packages

- PyPDF2 >= 3.0.0 (PDF processing and text extraction)
- pdf2image >= 1.16.3 (PDF to image conversion)
- Pillow >= 10.0.0 (Image processing and display)
- imagehash >= 4.3.1 (Content comparison)
- requests >= 2.31.0 (HTTP requests for update checks)
- tkinter (GUI framework, comes with Python)

### System Dependencies

- Poppler (required by pdf2image for PDF rendering)
- Internet connection (for update checks)
  - Windows: Included in the pdf2image package
  - macOS: Install via `brew install poppler`
  - Linux: Install via `sudo apt-get install poppler-utils`

## Installation

### Prerequisites

- Python 3.8 or higher
- Poppler (required for PDF rendering)
  - Windows: Included in the pdf2image package
  - macOS: `brew install poppler`
  - Linux: `sudo apt-get install poppler-utils`

### Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/PDF_finder.git
   cd PDF_finder
   ```

2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python main.py
   ```

## Usage

1. Run the application:

   ```bash
   python main.py
   ```

2. Click "Browse" to select a folder to scan

3. Click "Find Duplicates" to start scanning
   - Progress and status will be shown
   - Click again to cancel the scan

4. Review the results:
   - Select a PDF to preview its contents
   - Switch between image and text preview modes

5. Manage duplicates:
   - Review the original and duplicate file pairs
   - Select unwanted duplicates
   - Click "Delete Selected" to remove them

## Support & Community

If you find this tool useful, consider supporting the development:

- [GitHub Sponsors](https://github.com/sponsors/Nsfr750)
- [Patreon](https://www.patreon.com/Nsfr750)
- [PayPal](https://paypal.me/3dmega)

Join our community:

- [Discord](https://discord.gg/BvvkUEP9)

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
