#!/bin/bash

# Get version from version.py
VERSION=$(source ../script/version.sh; echo "$VERSION_STR")

OUTPUT_NAME="PDFDuplicateFinder-$VERSION-linux"
OUTPUT_BIN="PDFDuplicateFinder"
DIST_DIR="dist-nuitka"
BUILD_DATE=$(date '+%Y-%m-%d')

echo "Building PDF Duplicate Finder $VERSION for Linux..."
echo "Build date: $BUILD_DATE"

# Clean previous builds
if [ -d "../$DIST_DIR" ]; then
    echo "Cleaning previous build..."
    rm -rf "../$DIST_DIR"
fi

# Build with Nuitka
python -m nuitka \
    --standalone \
    --onefile \
    --output-filename="$OUTPUT_BIN" \
    --output-dir="../$DIST_DIR" \
    --enable-console \
    --include-package=PyQt6 \
    --include-package=PyQt6.QtCore \
    --include-package=PyQt6.QtGui \
    --include-package=PyQt6.QtWidgets \
    --include-package=PyQt6.QtPdf \
    --include-package=PyQt6.QtPdfWidgets \
    --include-package=PyQt6.QtPrintSupport \
    --include-package=PyQt6.QtSvg \
    --include-package=tqdm \
    --include-package=send2trash \
    --include-package=psutil \
    --include-data-files=../assets/icon.ico=assets/icon.ico \
    --include-data-files=../assets/logo.png=assets/logo.png \
    --include-data-files=../assets/version_info.txt=assets/version_info.txt \
    --include-data-files=../config/settings.json=config/settings.json \
    --include-data-files=../config/updates.json=config/updates.json \
    --include-data-dir=../assets=assets \
    --include-data-dir=../config=config \
    --include-data-dir=../lang=lang \
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
    ../../main.py

# Check if build was successful
if [ $? -eq 0 ]; then
    # Create a tar.gz archive of the distribution
    cd "../$DIST_DIR" || exit
    mv "$OUTPUT_BIN" "$OUTPUT_NAME"
    tar -czf "$OUTPUT_NAME.tar.gz" "$OUTPUT_NAME"
    echo
    echo "Build completed successfully!"
    echo "Output directory: $(pwd)"
    echo "Archive: $DIST_DIR/$OUTPUT_NAME.tar.gz"
    echo "Size: $(du -h "$OUTPUT_NAME.tar.gz" | cut -f1)"
else
    echo "Build failed. Check the output for errors."
    exit 1
fi

echo "Build completed on $BUILD_DATE"