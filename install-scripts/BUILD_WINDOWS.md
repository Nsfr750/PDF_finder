# Building Images-Deduplicator for Windows

This guide explains how to build a standalone Windows executable for Images-Deduplicator using PyInstaller.

## Prerequisites

1. Python 3.8 or higher (tested with Python 3.13.5)
2. pip (Python package manager)
3. Git (optional, for cloning the repository)

## Installation

1. Clone the repository (or download the source code):
   ```bash
   git clone https://github.com/Nsfr750/Images-Deduplicator.git
   cd Images-Deduplicator
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

## Building the Executable

1. Run the build script:
   ```bash
   python build_simple.py
   ```

2. The build process will:
   - Clean previous build artifacts
   - Create a standalone executable using PyInstaller
   - Generate a portable ZIP archive containing the executable and required assets

3. The output files will be created in the `dist` directory:
   - `Images-Deduplicator.exe`: The main executable
   - `Images-Deduplicator-Portable-vX.Y.Z.zip`: Portable archive containing the executable and assets

## Building Manually

If you need to customize the build, you can run PyInstaller directly:

```bash
python -m PyInstaller \
    --clean \
    --onefile \
    --windowed \
    --noconsole \
    --name Images-Deduplicator \
    --icon assets/icon.ico \
    --add-data "assets;assets" \
    --add-data "script;script" \
    --hidden-import script.about \
    --hidden-import script.help \
    --hidden-import script.log_viewer \
    --hidden-import script.sponsor \
    --hidden-import script.styles \
    --hidden-import script.translations \
    --hidden-import script.updates \
    --hidden-import script.version \
    --hidden-import script.settings_dialog \
    --hidden-import script.menu \
    --hidden-import script.logger \
    --hidden-import script.language_manager \
    --hidden-import script.workers \
    --hidden-import script.image_dialog_preview \
    --hidden-import script.empty_trash \
    --hidden-import script.undo_manager \
    --hidden-import script.update_preview \
    main.py
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Ensure all required Python packages are installed
   - Run `pip install -r requirements.txt`

2. **Build Failures**
   - Clean the build directory: `rmdir /s /q build`
   - Try running the build script again

3. **Executable Not Found**
   - Check the `dist` directory for the output files
   - Verify that the build completed successfully

4. **Runtime Errors**
   - Run the executable from a command prompt to see error messages
   - Check the application logs in the `logs` directory

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the [GitHub repository](https://github.com/Nsfr750/Images-Deduplicator).
