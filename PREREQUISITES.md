# Prerequisites

This project runs on Python and supports multiple PDF rendering backends. Auto mode will pick the best available one and fall back safely.

## Required

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### System Requirements

- **RAM**: 4GB minimum, 8GB+ recommended for large PDF collections
- **Storage**: SSD highly recommended for faster file access during scanning
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+ or equivalent)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Nsfr750/PDF_finder.git
cd PDF_finder
```

### 2. Set Up Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Development Tools (Optional)

For development and testing:

```bash
pip install black flake8 mypy pytest pytest-cov pre-commit
```

## Optional PDF Rendering Backends

The app supports multiple PDF rendering backends. You can choose your preferred backend in **Settings → PDF Rendering**. Use the **"Test backends"** button to verify availability.

### 1. PyMuPDF (fitz) - **Recommended**

- **Status**: Default and bundled via requirements.txt
- **Performance**: Fast and reliable
- **Installation**: No additional system installation required
- **Features**: Full PDF text extraction, rendering, and metadata support

### 2. Wand / Ghostscript

- **Status**: Optional fallback backend
- **Performance**: Good, but slower than PyMuPDF
- **Installation**: Requires Ghostscript to be installed separately

#### Windows Installation

1. Download Ghostscript from [ghostscript.com](https://ghostscript.com/releases/)
2. Install Ghostscript (typically to `C:\Program Files\gs\`)
3. In **Settings → PDF Rendering**, set the Ghostscript executable path:
   ```
   C:\Program Files\gs\<version>\bin\gswin64c.exe
   ```
4. Click **"Test backends"** to validate the installation

#### Linux Installation

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ghostscript

# Fedora/CentOS
sudo dnf install ghostscript

# Arch Linux
sudo pacman -S ghostscript
```

#### macOS Installation

```bash
# Using Homebrew
brew install ghostscript

# Using MacPorts
sudo port install ghostscript
```

### 3. ImageMagick (Optional)

- **Status**: Optional for advanced image processing
- **Installation**: Download from [imagemagick.org](https://imagemagick.org/script/download.php)

## Text Processing Requirements

For optimal text comparison performance:

### Tesseract OCR (Optional)

For text extraction from scanned PDFs:

#### Windows

1. Download Tesseract from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install Tesseract (typically to `C:\Program Files\Tesseract-OCR\`)
3. Add Tesseract to your system PATH

#### Linux

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Fedora/CentOS
sudo dnf install tesseract

# Arch Linux
sudo pacman -S tesseract
```

#### macOS

```bash
# Using Homebrew
brew install tesseract

# Using MacPorts
sudo port install tesseract
```

### Language Data

For OCR support in specific languages, install additional language packs:

```bash
# Example: Install Italian language pack
# Windows: Download from UB Mannheim and place in tessdata folder
# Linux:
sudo apt-get install tesseract-ocr-ita  # Italian
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-fra  # French
# macOS:
brew install tesseract-lang
```

## Backend Fallback and Error Handling

### Automatic Fallback

- If the selected backend is unavailable or fails, the app automatically falls back to a working backend
- A localized status bar warning indicates when fallback occurs
- The app continues to function with reduced functionality if needed

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Ghostscript not found" | Install Ghostscript and set the correct path in Settings |
| "Backend initialization failed" | Use "Test backends" to diagnose and try a different backend |
| "OCR not available" | Install Tesseract OCR and language packs |
| "Memory error" | Increase system RAM or process smaller batches of files |

## Development Environment Setup

### Pre-commit Hooks (Optional)

For code quality enforcement:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Testing

Run the test suite to verify installation:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=script --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## Performance Optimization

### For Large PDF Collections

- **RAM**: 16GB+ recommended for collections >10,000 files
- **Storage**: Use SSD for PDF storage directory
- **CPU**: Multi-core processor improves parallel processing
- **Network**: Local storage recommended over network drives

### System Configuration

#### Windows

- Disable Windows Defender real-time scanning for PDF directories
- Increase virtual memory if processing large files
- Use high-performance power plan

#### Linux

- Increase file descriptor limits:
  ```bash
  echo "* soft nofile 65536" >> /etc/security/limits.conf
  echo "* hard nofile 65536" >> /etc/security/limits.conf
  ```
- Disable unnecessary background services

#### macOS

- Close unnecessary applications during large scans
- Ensure sufficient disk space for temporary files
- Use Activity Monitor to monitor resource usage

## Troubleshooting

### Diagnostic Steps

1. **Test Backends**: Use **Settings → "Test backends"** to verify all installations
2. **Check Logs**: Review logs in the `logs/` directory for detailed error messages
3. **Verify Paths**: Ensure all executable paths are correct in Settings
4. **Test Permissions**: Ensure the application has read/write access to PDF directories

### Common Error Messages

- **"Translation key not found"**: Check that translation files are properly configured
- **"PDF parsing failed"**: Try a different backend or check file permissions
- **"Out of memory"**: Reduce batch size or increase system RAM
- **"Backend not available"**: Install the required backend software

### Getting Help

- Check the [documentation](docs/) for detailed guides
- Review existing [issues](https://github.com/Nsfr750/PDF_finder/issues)
- Join our [Discord community](https://discord.gg/ryqNeuRYjD)
- Contact the maintainer: [nsfr750@yandex.com](mailto:nsfr750@yandex.com)

## Version Compatibility

| Component | Minimum Version | Recommended Version |
|-----------|-----------------|---------------------|
| Python | 3.8 | 3.10+ |
| PyQt6 | 6.0.0 | 6.6.0+ |
| PyMuPDF | 1.20.0 | 1.23.0+ |
| Ghostscript | 9.50 | 10.0+ |
| Tesseract | 4.0.0 | 5.3.0+ |

*Last Updated: September 2025*