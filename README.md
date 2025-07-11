# PDF Duplicate Finder

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful tool to find and manage duplicate PDF files on your computer. PDF Duplicate Finder helps you identify and remove duplicate PDF documents, saving disk space and organizing your files more efficiently.

## ✨ Features

- 🔍 **Smart PDF Comparison**: Find duplicate PDFs based on content, not just file names or sizes
- 🚀 **Fast Scanning**: Optimized algorithms for quick scanning of large PDF collections
- 🎨 **Intuitive UI**: Clean and user-friendly interface with light/dark theme support
- 🔄 **Batch Processing**: Process multiple files or entire folders at once
- 📊 **Detailed Analysis**: View file details, previews, and comparison results
- 🛠 **Advanced Tools**: Multiple selection modes, filtering, and sorting options
- 🌍 **Multi-language Support**: Available in multiple languages

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

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

## 🚀 Usage

1. Launch the application:
   ```bash
   python main.py
   ```

2. Click "Scan Folder" to select a directory to scan for duplicate PDFs

3. Review the results in the main window

4. Use the tools to manage duplicates:
   - Mark files to keep
   - Delete unwanted duplicates
   - Preview files before taking action

## 🛠 Key Features in Detail

### Smart PDF Comparison
- Compares PDF content using advanced hashing algorithms
- Detects similar documents even with different file names or metadata
- Configurable similarity threshold for fine-tuned results

### Performance Optimizations
- Multi-threaded scanning for faster processing
- Memory-efficient handling of large PDF files
- Progress tracking and cancellation support

### User Experience
- Modern, responsive interface
- Customizable view options
- Comprehensive keyboard shortcuts
- Detailed file information and previews

## 📝 Version History

See [CHANGELOG.md](CHANGELOG.md) for a complete list of changes in each version.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to contribute to this project.

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped improve PDF Duplicate Finder
- Built with ❤️ using Python and PyQt6

---

📅 **Last Updated**: July 2025  
🐍 **Python Version**: 3.8+  
📜 **License**: GPL-3.0
