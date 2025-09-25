# PDF Duplicate Finder - User Guide v3.0.0

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Main Interface](#main-interface)
5. [Scanning for Duplicates](#scanning-for-duplicates)
6. [Managing Results](#managing-results)
7. [Settings Configuration](#settings-configuration)
8. [Language Support](#language-support)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)
11. [FAQ](#faq)

---

## Introduction

PDF Duplicate Finder is a powerful desktop application designed to help you find and manage duplicate PDF files on your computer. With version 3.0.0, the application has been completely rewritten with enhanced performance, improved user interface, and comprehensive multi-language support.

### Key Features in v3.0.0

- **Multi-language Support**: 12 languages available with instant switching
- **Enhanced Performance**: Faster scanning and improved memory management
- **Improved UI**: Modern, responsive interface with better organization
- **Advanced Filtering**: More options to refine duplicate detection
- **Better Error Handling**: Comprehensive error messages and recovery options
- **Help System**: Built-in help dialog with context-sensitive assistance

---

## Installation

### System Requirements

- **Operating System**: Windows 10/11, Linux, or macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space for installation
- **Additional Software**: Ghostscript and Tesseract OCR (optional, for enhanced features)

### Installation Steps

1. **Download the Application**
   - Visit the [GitHub Releases page](https://github.com/Nsfr750/PDF_finder/releases)
   - Download the latest version (3.0.0 or higher)

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Optional Components**
   - **Ghostscript**: For enhanced PDF processing
   - **Tesseract OCR**: For text extraction from scanned PDFs

4. **Run the Application**
   ```bash
   python main.py
   ```

---

## Getting Started

### First Launch

When you first launch PDF Duplicate Finder:

1. **Language Selection**: The application will start in English by default. You can change the language immediately using the language selector in the toolbar.

2. **Initial Setup**: The application will automatically detect available PDF processing backends and configure optimal settings.

3. **Welcome Screen**: A brief introduction to the application's features and capabilities.

### Basic Workflow

1. **Select a Folder**: Choose the directory containing your PDF files
2. **Configure Settings**: Adjust scanning parameters if needed
3. **Start Scanning**: Begin the duplicate detection process
4. **Review Results**: Examine found duplicates and take action
5. **Manage Files**: Delete, move, or keep selected files

---

## Main Interface

### Overview

The main interface is divided into several key sections:

![Main Interface](docs/images/main_interface.png)

### Toolbar

The toolbar provides quick access to main functions:

- **📁 Open Folder**: Select a directory to scan
- **🔄 Rescan**: Rescan the current directory
- **⚙️ Settings**: Open configuration dialog
- **❓ Help**: Access the help system
- **🌐 Language**: Switch between supported languages

### Status Bar

The status bar shows:
- **Current Status**: Ready, scanning, or processing
- **File Count**: Number of PDF files found
- **Progress**: Scanning progress percentage
- **Language**: Currently selected language

### Main Panels

1. **File List Panel** (Left)
   - Shows all PDF files in the selected directory
   - Displays file name, size, and modification date
   - Allows filtering and sorting

2. **Duplicates Panel** (Right)
   - Shows detected duplicate groups
   - Organized by similarity percentage
   - Provides action buttons for each group

---

## Scanning for Duplicates

### Selecting a Folder

1. **Method 1**: Click the "📁 Open Folder" button in the toolbar
2. **Method 2**: Use the menu: `File → Open Folder`
3. **Method 3**: Drag and drop a folder onto the application window

### Scanning Options

Before scanning, you can configure various options in the Settings dialog:

#### Basic Options

- **Scan Subfolders**: Include subdirectories in the scan
- **Minimum File Size**: Ignore files smaller than specified size
- **Maximum File Size**: Ignore files larger than specified size
- **File Extensions**: Specify which file extensions to include

#### Advanced Options

- **Similarity Threshold**: Set the minimum similarity percentage (0-100%)
- **Comparison Method**: Choose between content, metadata, or both
- **Batch Size**: Number of files to process simultaneously
- **Cache Results**: Store results for faster subsequent scans

### Starting the Scan

1. **Click "Start Scan"**: Begin the scanning process
2. **Monitor Progress**: Watch the progress bar and status updates
3. **Pause/Resume**: Use the pause button to temporarily stop scanning
4. **Cancel**: Stop the scanning process completely

### Scan Results

After scanning completes, you'll see:
- **Total Files Scanned**: Number of PDF files processed
- **Duplicates Found**: Number of duplicate groups detected
- **Time Taken**: Duration of the scanning process
- **Storage Saved**: Potential disk space that can be recovered

---

## Managing Results

### Understanding Duplicate Groups

Duplicates are organized into groups based on similarity:

- **100% Similarity**: Exact duplicates
- **90-99% Similarity**: Very similar content
- **70-89% Similarity**: Moderately similar
- **50-69% Similarity**: Somewhat similar

### Viewing Duplicates

Each duplicate group shows:
- **File Path**: Location of each file
- **File Size**: Size in human-readable format
- **Modification Date**: Last modified timestamp
- **Similarity**: Percentage match to other files in the group

### Taking Action

For each duplicate group, you can:

#### Keep/Delete Operations

- **Keep Original**: Keep the first file, delete others
- **Keep Newest**: Keep the most recently modified file
- **Keep Oldest**: Keep the oldest file
- **Keep Largest**: Keep the largest file
- **Keep Smallest**: Keep the smallest file
- **Manual Selection**: Choose which files to keep manually

#### File Operations

- **Delete**: Permanently remove selected files
- **Move to Folder**: Move files to a specified directory
- **Copy to Folder**: Copy files to a specified directory
- **Open in Viewer**: Open file in default PDF viewer
- **Show in Explorer**: Reveal file in file explorer

### Batch Operations

Select multiple duplicate groups and perform batch operations:
- **Delete All Duplicates**: Remove all duplicate files across selected groups
- **Move All Duplicates**: Move all duplicates to a specified folder
- **Export Results**: Save duplicate list to CSV or JSON file

---

## Settings Configuration

### Accessing Settings

- **Method 1**: Click the "⚙️ Settings" button in the toolbar
- **Method 2**: Use the menu: `Tools → Settings`
- **Method 3**: Keyboard shortcut: `Ctrl+S`

### Settings Categories

#### General Settings

- **Default Language**: Choose startup language
- **Auto-update**: Check for updates automatically
- **Start with Windows**: Launch application on system startup
- **Minimize to Tray**: Keep application running in system tray

#### Scanning Settings

- **Default Scan Directory**: Set default folder to scan
- **Include Subfolders**: Scan subdirectories by default
- **File Size Limits**: Set minimum and maximum file sizes
- **File Extensions**: Configure which file types to include

#### Comparison Settings

- **Similarity Threshold**: Default similarity percentage
- **Comparison Method**: Content, metadata, or both
- **Ignore Metadata**: Exclude metadata from comparison
- **Fast Mode**: Use faster but less accurate comparison

#### Performance Settings

- **Batch Size**: Number of files to process simultaneously
- **Memory Limit**: Maximum memory usage
- **Thread Count**: Number of processing threads
- **Cache Results**: Enable result caching

#### Backend Settings

- **PDF Processing Backend**: Choose between PyMuPDF, pdf2image, or Ghostscript
- **OCR Engine**: Select Tesseract or other OCR engine
- **Test Backends**: Verify backend installations

### Saving and Loading Settings

- **Save**: Apply settings immediately
- **Reset to Defaults**: Restore default settings
- **Export Settings**: Save settings to a file
- **Import Settings**: Load settings from a file

---

## Language Support

### Available Languages

Version 3.0.0 supports 12 languages:

- **English** (Default)
- **Italiano** (Italian)
- **Español** (Spanish)
- **Français** (French)
- **Deutsch** (German)
- **Português** (Portuguese)
- **Русский** (Russian)
- **中文** (Chinese)
- **日本語** (Japanese)
- **한국어** (Korean)
- **العربية** (Arabic)
- **हिन्दी** (Hindi)

### Changing Language

1. **Method 1**: Click the language button in the toolbar
2. **Method 2**: Use the menu: `Tools → Language`
3. **Method 3**: Keyboard shortcut: `Ctrl+L`

### Language Features

- **Instant Switching**: Language changes take effect immediately
- **Complete Translation**: All UI elements, menus, and messages are translated
- **Help System**: Help dialog is available in all supported languages
- **RTL Support**: Right-to-left languages properly supported

### Missing Translations

If you notice missing or incorrect translations:
1. **Report Issues**: Use the help system to report translation problems
2. **Contribute**: Help improve translations by contributing to the project
3. **Contact**: Reach out to the maintainer for translation assistance

---

## Advanced Features

### Command Line Interface

The application supports command-line usage:

```bash
# Basic scanning
python main.py --scan "C:\MyPDFs"

# With custom settings
python main.py --scan "C:\MyPDFs" --threshold 85 --subfolders

# Export results
python main.py --scan "C:\MyPDFs" --export results.csv

# Help
python main.py --help
```

### Automation and Scripting

#### Python API

```python
from script.pdf_scanner import PDFScanner

# Create scanner instance
scanner = PDFScanner()

# Configure settings
scanner.set_similarity_threshold(90)
scanner.set_include_subfolders(True)

# Scan directory
results = scanner.scan_directory("C:\MyPDFs")

# Process results
for group in results:
    print(f"Found {len(group.files)} duplicates")
```

#### Batch Processing

Create batch files for automated scanning:

```batch
@echo off
REM Daily PDF duplicate scan
python main.py --scan "C:\Documents" --export "daily_report.csv" --quiet
```

### Integration with Other Tools

#### File Explorer Context Menu

Add PDF Duplicate Finder to Windows context menu:

1. **Create Registry File**:
   ```reg
   Windows Registry Editor Version 5.00
   
   [HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\PDFDuplicateFinder]
   @="Scan for Duplicates"
   
   [HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\PDFDuplicateFinder\command]
   @="\"C:\\path\\to\\python.exe\" \"C:\\path\\to\\main.py\" --scan \"%1\""
   ```

2. **Import Registry**: Double-click the .reg file to import

#### Scheduled Tasks

Set up automatic scanning with Windows Task Scheduler:

1. **Open Task Scheduler**
2. **Create Basic Task**
3. **Set Trigger**: Daily, weekly, or monthly
4. **Set Action**: Run the application with scan parameters
5. **Configure Settings**: Run whether user is logged in or not

### Custom Comparison Methods

For advanced users, you can create custom comparison methods:

```python
from script.comparison_engine import ComparisonEngine

class CustomComparison(ComparisonEngine):
    def compare_files(self, file1, file2):
        # Implement custom comparison logic
        return similarity_score
```

---

## Troubleshooting

### Common Issues

#### Application Won't Start

**Problem**: Application crashes or doesn't launch

**Solutions**:
1. **Check Python Version**: Ensure Python 3.8+ is installed
2. **Install Dependencies**: Run `pip install -r requirements.txt`
3. **Check Permissions**: Run as administrator if needed
4. **View Logs**: Check `logs/` directory for error messages

#### Scanning is Slow

**Problem**: Scanning process takes too long

**Solutions**:
1. **Reduce Batch Size**: Lower the batch size in settings
2. **Exclude Large Files**: Set maximum file size limit
3. **Disable Subfolders**: Uncheck "Include Subfolders"
4. **Use Fast Mode**: Enable fast comparison mode

#### No Duplicates Found

**Problem**: Scanner doesn't find any duplicates

**Solutions**:
1. **Lower Similarity Threshold**: Reduce to 70-80%
2. **Check File Extensions**: Ensure PDF files are included
3. **Verify Directory**: Confirm the directory contains PDF files
4. **Test with Known Duplicates**: Create test duplicates to verify functionality

#### Memory Issues

**Problem**: Application uses too much memory

**Solutions**:
1. **Reduce Batch Size**: Lower the number of files processed simultaneously
2. **Set Memory Limit**: Configure maximum memory usage in settings
3. **Close Other Applications**: Free up system memory
4. **Restart Application**: Clear memory cache

### Error Messages

#### "Translation key not found"

**Cause**: Missing translation for current language

**Solution**:
1. **Switch to English**: Temporarily use English as fallback
2. **Report Issue**: Use help system to report missing translation
3. **Check Updates**: Ensure you have the latest version

#### "PDF parsing failed"

**Cause**: Unable to process PDF file

**Solution**:
1. **Check File Permissions**: Ensure read access to the file
2. **Try Different Backend**: Switch PDF processing backend in settings
3. **Test Backends**: Use "Test Backends" to verify installations
4. **Check File Integrity**: Ensure PDF file is not corrupted

#### "Backend not available"

**Cause**: Required backend software not installed

**Solution**:
1. **Install Missing Software**: Install Ghostscript or Tesseract
2. **Configure Paths**: Set correct executable paths in settings
3. **Test Installation**: Use "Test Backends" to verify
4. **Use Alternative Backend**: Switch to a different backend

### Getting Help

#### Built-in Help System

1. **Press F1**: Open help dialog
2. **Click Help Button**: Access context-sensitive help
3. **Use Menu**: `Help → User Guide` for comprehensive documentation

#### Online Resources

- **Documentation**: [GitHub Wiki](https://github.com/Nsfr750/PDF_finder/wiki)
- **Issues**: [GitHub Issues](https://github.com/Nsfr750/PDF_finder/issues)
- **Discord**: [Community Support](https://discord.gg/ryqNeuRYjD)

#### Contact Support

- **Email**: [nsfr750@yandex.com](mailto:nsfr750@yandex.com)
- **GitHub**: [Create an Issue](https://github.com/Nsfr750/PDF_finder/issues/new)

---

## FAQ

### General Questions

#### Q: Is PDF Duplicate Finder free?
A: Yes, PDF Duplicate Finder is completely free and open-source software licensed under GPL-3.0.

#### Q: What operating systems are supported?
A: Windows 10/11, Linux, and macOS are supported.

#### Q: How accurate is the duplicate detection?
A: The accuracy depends on the similarity threshold and comparison method. At 95%+ similarity, detection is very accurate for exact duplicates.

#### Q: Can I recover deleted files?
A: No, deleted files are permanently removed. Always backup important files before deletion.

### Technical Questions

#### Q: What PDF processing backends are available?
A: PyMuPDF (default), pdf2image, and Ghostscript are supported backends.

#### Q: How much memory does the application need?
A: Minimum 4GB RAM, but 8GB+ is recommended for large collections.

#### Q: Can I scan network drives?
A: Yes, but performance may be slower. Local storage is recommended for best performance.

#### Q: Does the application modify my PDF files?
A: No, the application only reads PDF files for comparison. It never modifies original files.

### Usage Questions

#### Q: How do I exclude certain files from scanning?
A: Use the file size limits and file extension filters in the settings.

#### Q: Can I save my scan results?
A: Yes, use the "Export Results" feature to save results to CSV or JSON files.

#### Q: How do I customize the comparison criteria?
A: Adjust the similarity threshold and comparison method in the settings.

#### Q: Can I scan multiple folders at once?
A: Currently, you can only scan one folder at a time, but you can include subfolders.

### Troubleshooting Questions

#### Q: Why does the application freeze during scanning?
A: This could be due to memory issues or corrupted files. Try reducing the batch size or excluding problematic files.

#### Q: How do I reset all settings to defaults?
A: Use the "Reset to Defaults" button in the settings dialog.

#### Q: What should I do if a translation is missing?
A: Report it through the help system or contribute a translation on GitHub.

#### Q: How do I update the application?
A: Download the latest version from GitHub releases and replace the old files.

---

## Additional Resources

### Documentation

- [API Documentation](docs/api/)
- [Developer Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)

### Community

- [GitHub Repository](https://github.com/Nsfr750/PDF_finder)
- [Discord Community](https://discord.gg/ryqNeuRYjD)
- [Issue Tracker](https://github.com/Nsfr750/PDF_finder/issues)

### Support

- [Email Support](mailto:nsfr750@yandex.com)
- [Bug Reports](https://github.com/Nsfr750/PDF_finder/issues/new)
- [Feature Requests](https://github.com/Nsfr750/PDF_finder/issues/new)

---

*Last Updated: September 2025*  
*Version: 3.0.0*
