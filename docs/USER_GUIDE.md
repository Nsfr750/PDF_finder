# PDF Duplicate Finder - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [User Interface Overview](#user-interface-overview)
4. [Finding Duplicates](#finding-duplicates)
5. [Managing Results](#managing-results)
6. [Using the PDF Viewer](#using-the-pdf-viewer)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#frequently-asked-questions)

## Introduction
Welcome to PDF Duplicate Finder! This guide will help you make the most of the application's features to find and manage duplicate PDF files on your system.

## Installation
### System Requirements
- Windows 10/11, macOS 10.15+, or Linux
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 100MB free disk space

### Step-by-Step Installation
1. Download the latest release from GitHub
2. Extract the archive to your preferred location
3. Open a terminal/command prompt in the extracted directory
4. Run: `pip install -r requirements.txt`
5. Launch the application: `python main.py`

## User Interface Overview

### Main Window
- **Menu Bar**: Access to all application functions
- **Toolbar**: Quick access to common actions
- **Directory List**: Shows folders being scanned
- **Results Panel**: Displays found duplicates
- **Preview Panel**: Shows preview of selected files
- **Status Bar**: Shows current status and progress

### Navigation
- Use the View menu to toggle panels
- Right-click context menus provide additional options
- Drag and drop PDF files directly into the window

## Finding Duplicates

### Basic Scan
1. Click "Add Directory" and select a folder to scan
2. Adjust scan settings if needed
3. Click "Start Scan"
4. View results in the main window

### Advanced Scanning Options
- **Content Comparison**: Compare actual PDF content
- **Metadata Comparison**: Check document properties
- **File Size Filtering**: Ignore files outside size ranges
- **Date Range Filtering**: Focus on files modified within specific dates

## Managing Results

### Working with Duplicates
- Select files to view detailed comparison
- Use checkboxes to mark files for actions
- Right-click for context menu options

### Available Actions
- **Delete**: Remove selected files
- **Move**: Relocate files to a new location
- **Open**: View files in default application
- **Exclude**: Add files/folders to exclusion list

## Using the PDF Viewer

### Navigation
- Use arrow keys or on-screen buttons to navigate pages
- Enter page number to jump to specific page
- Use zoom controls to adjust view

### Features
- **Search**: Find text within the document
- **Thumbnail View**: Navigate using page thumbnails
- **Rotate**: Rotate pages for better viewing
- **Bookmarks**: Save and manage bookmarks

## Advanced Features

### Batch Processing
- Process multiple files at once
- Create custom action sequences
- Save and load processing profiles

### Automation
- Schedule regular scans
- Set up automatic cleanup rules
- Export scan results to various formats

## Troubleshooting

### Common Issues
- **Slow Performance**: Try scanning smaller directories or adjust comparison settings
- **Files Not Found**: Check file permissions and exclusions
- **Crashes**: Update to the latest version and check system requirements

### Log Files
- Application logs are stored in `logs/`
- Enable debug mode for detailed logging
- Include logs when reporting issues

## Frequently Asked Questions

### General
**Q: Is my data sent to any servers?**
A: No, all processing happens locally on your computer.

**Q: What file types are supported?**
A: Currently, only PDF files are supported.

### Technical
**Q: How does the duplicate detection work?**
A: We use a combination of file hashing and content analysis to identify duplicates.

**Q: Can I recover deleted files?**
A: Files deleted through the application are moved to the system recycle bin/trash and can be restored from there.

### Support
**Q: How do I report a bug?**
A: Please open an issue on our GitHub repository with detailed steps to reproduce.

**Q: Where can I request a new feature?**
A: Feature requests can be submitted through GitHub issues or our community forum.

---
*Last updated: August 20, 2025*
