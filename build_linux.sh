#!/bin/bash

VERSION=$(python -c "from script.version import __version__; print(__version__)")
OUTPUT_NAME="PDFDuplicateFinder-$VERSION-linux"
OUTPUT_BIN="PDFDuplicateFinder"
DIST_DIR="dist"

echo "Building PDF Duplicate Finder $VERSION for Linux..."

# Create output directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Build with Nuitka
python -m nuitka \
    --standalone \
    --onefile \
    --output-filename="$OUTPUT_BIN" \
    --output-dir="$DIST_DIR" \
    --enable-console \
    --include-package=PyQt6 \
    --include-package=PyQt6.QtCore \
    --include-package=PyQt6.QtGui \
    --include-package=PyQt6.QtWidgets \
    --include-package=PyQt6.QtPdf \
    --include-package=PyQt6.QtPdfWidgets \
    --follow-imports \
    --nofollow-import-to=*.tests,*.test,*.unittest,*.setuptools,*.distutils,*.pkg_resources \
    --nofollow-import-to=*.pytest,*.setuptools_rust \
    --remove-output \
    main.py

# Check if build was successful
if [ $? -eq 0 ]; then
    # Create a zip file of the distribution
    cd "$DIST_DIR" || exit
    mv "$OUTPUT_BIN" "$OUTPUT_NAME"
    zip -r "$OUTPUT_NAME.zip" "$OUTPUT_NAME"
    echo "Build successful! Output: $DIST_DIR/$OUTPUT_NAME"
else
    echo "Build failed. Check the output for errors."
    exit 1
fi