# Prerequisites

This project runs on Python and supports multiple PDF rendering backends. Auto mode will pick the best available one and fall back safely.

## Required

- Python 3.8+
- pip
- Tesseract OCR (for text extraction from scanned PDFs)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Text Processing Requirements

For optimal text comparison performance, the following are recommended:

- At least 4GB of free RAM for processing large PDFs
- SSD storage for faster file access during scanning
- Python packages in `requirements.txt` will handle text processing

## Optional PDF Rendering Backends

The app supports two backends. You can choose one in Settings → PDF Rendering. Use the “Test backends” button to verify availability.

### 1) PyMuPDF (fitz)

- Default, fast, and bundled via requirements
- No additional system installation required

### 2) Wand / Ghostscript

- Requires Ghostscript
- Windows:
  - Download and install Ghostscript from <https://ghostscript.com/releases/>
  - In Settings → PDF Rendering, set the Ghostscript executable path (e.g., `C:\Program Files\gs\<version>\bin\gswin64c.exe`)
  - Click “Test backends” to validate

- Linux/Mac: install via your package manager

### 3) ImageMagik

- Download and install ImageMagik from <https://imagemagick.org/script/download.php>

## Backend Fallback and Warnings

- If you select a backend that is unavailable or fails, the app falls back to a working backend
- A localized status-bar warning indicates the fallback

## Troubleshooting

- Use Settings → “Test backends” to diagnose missing paths or installations
- Ensure Ghostscript path points to the executable file
- Check logs in `logs/` for detailed error messages
