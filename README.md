# PDF Duplicate Finder

A Python application that helps you find and remove duplicate PDF files based on their content. Features an advanced preview system that allows you to verify duplicates before deletion, with a customizable interface that includes light and dark themes.

## Features

- **Smart Duplicate Detection**
  - Content-based comparison for accurate results
  - Support for both text and image-based comparison
  - Fast scanning with progress tracking

- **Modern User Interface**
  - Light and dark theme support
  - Responsive layout that adapts to window size
  - Horizontal scrolling for long file paths
  - Keyboard shortcuts for common actions

- **Advanced PDF Preview**
  - Image preview with page navigation
  - Text content extraction view
  - High-quality rendering with LANCZOS resampling
  - Automatic image scaling

- **User Experience**
  - Theme preferences saved between sessions
  - Intuitive menu organization
  - Comprehensive help system
  - About dialog with version information
  - Support and sponsorship options

- **Performance**
  - Efficient memory management
  - Background processing for large collections
  - Cancel long-running operations

## What's New in v2.4.0

- **Automatic Update Checks**
  - Automatic check for updates on startup
  - Manual update check via Help menu
  - User notifications for available updates
  - Direct download of new versions from GitHub

### Previous Updates

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
   ```
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

- GitHub Sponsors: https://github.com/sponsors/Nsfr750
- Patreon: https://www.patreon.com/Nsfr750
- PayPal: https://paypal.me/3dmega

Join our community:
- Discord: https://discord.gg/BvvkUEP9

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
