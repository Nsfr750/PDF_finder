#!/bin/bash

# Get script directory for proper path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Get version from version.py
# Try python3 first, then fall back to python
PYTHON_CMD=""
if python3 --version >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif python --version >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Neither python3 nor python found in PATH"
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"
VERSION=$(cd "$PROJECT_ROOT" && $PYTHON_CMD -c "import sys; sys.path.insert(0, 'script/utils'); from version import __version__; print(__version__)")
if [ $? -ne 0 ]; then
    echo "Warning: Could not read version from version.py, using default"
    VERSION="3.0.0"
fi

OUTPUT_NAME="PDF-Finder_$VERSION-linux"
OUTPUT_BIN="PDF-Finder_$VERSION"
DIST_DIR="dist-nuitka"
BUILD_DATE=$(date '+%Y-%m-%d')

echo "Building PDF Duplicate Finder $VERSION for Linux..."
echo "Build date: $BUILD_DATE"
echo "Project root: $PROJECT_ROOT"

# Clean previous builds
if [ -d "$PROJECT_ROOT/$DIST_DIR" ]; then
    echo "Cleaning previous build..."
    rm -rf "$PROJECT_ROOT/$DIST_DIR"
fi

# Check if Nuitka is available
if ! $PYTHON_CMD -c "import nuitka" 2>/dev/null; then
    echo "Error: Nuitka is not installed. Please install it using:"
    echo "  $PYTHON_CMD -m pip install nuitka"
    echo "Or visit: https://nuitka.net/doc/installation.html"
    exit 1
fi

# Build with Nuitka
cd "$PROJECT_ROOT" || exit 1
$PYTHON_CMD -m nuitka \
    --standalone \
    --onefile \
    --output-filename="$OUTPUT_BIN" \
    --output-dir="$DIST_DIR" \
    --enable-console \
    --include-package=PyQt6 \
    --include-package=PyQt6.QtCore \
    --include-package=PyQt6.QtGui \
    --include-package=PyQt6.QtWidgets \
    --include-package=PyQt6.QtPrintSupport \
    --include-package=PyQt6.QtSvg \
    --include-package=tqdm \
    --include-package=send2trash \
    --include-package=psutil \
    --include-data-files=assets/icon.ico=assets/icon.ico \
    --include-data-files=assets/logo.png=assets/logo.png \
    --include-data-files=assets/version_info.txt=assets/version_info.txt \
    --include-data-files=config/settings.json=config/settings.json \
    --include-data-files=config/updates.json=config/updates.json \
    --include-data-dir=assets=assets \
    --include-data-dir=config=config \
    --include-data-dir=script/lang=lang \
    --follow-imports \
    --follow-stdlib \
    --nofollow-import-to=*.tests,*.test,*.unittest,*.setuptools,*.distutils,*.pkg_resources \
    --nofollow-import-to=*.pytest,*.setuptools_rust \
    --nofollow-import-to=scipy \
    --nofollow-import-to=skimage \
    --nofollow-import-to=PIL \
    --remove-output \
    --lto=yes \
    --jobs=8 \
    --assume-yes-for-downloads \
    main.py

# Check if build was successful
if [ $? -eq 0 ]; then
    # Create a tar.gz archive of the distribution
    cd "$PROJECT_ROOT/$DIST_DIR" || exit
    if [ -f "$OUTPUT_BIN" ]; then
        mv "$OUTPUT_BIN" "$OUTPUT_NAME"
        tar -czf "$OUTPUT_NAME.tar.gz" "$OUTPUT_NAME"
        echo
        echo "Build completed successfully!"
        echo "Output directory: $(pwd)"
        echo "Archive: $OUTPUT_NAME.tar.gz"
        echo "Size: $(du -h "$OUTPUT_NAME.tar.gz" | cut -f1)"
        echo "Executable: $OUTPUT_NAME"
    else
        echo "Error: Build output file $OUTPUT_BIN not found!"
        exit 1
    fi
else
    echo "Build failed. Check the output for errors."
    exit 1
fi

echo "Build completed on $BUILD_DATE"