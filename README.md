# PDF Duplicate Finder

A Python application that helps you find and remove duplicate PDF files based on their content. Features an advanced preview system that allows you to verify duplicates before deletion.

## Features

- Smart duplicate detection based on PDF content analysis
- Interactive graphical interface with modern design
- Advanced PDF preview capabilities:
  - Image preview of PDF pages with page count indicator
  - Automatic image scaling to fit the preview window
  - High-quality image rendering using LANCZOS resampling
  - Text content extraction view for searchable PDFs
- Real-time progress tracking with status updates
- Ability to cancel ongoing scans
- Selective duplicate management
- Horizontal and vertical scrolling for long paths
- Cross-platform compatibility
- Organized help system with user guide
- About dialog with version information
- Support and sponsorship options

## Requirements

### Software Requirements
- Python 3.x
- Operating System: Windows, macOS, or Linux

### Python Packages
- PyPDF2 >= 3.0.0 (PDF processing and text extraction)
- pdf2image >= 1.16.3 (PDF to image conversion)
- Pillow >= 10.0.0 (Image processing and display)
- imagehash >= 4.3.1 (Content comparison)
- tkinter (GUI framework, comes with Python)

### System Dependencies
- Poppler (required by pdf2image for PDF rendering)
  - Windows: Included in the pdf2image package
  - macOS: Install via `brew install poppler`
  - Linux: Install via `sudo apt-get install poppler-utils`

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
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
