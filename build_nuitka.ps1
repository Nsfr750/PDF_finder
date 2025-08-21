# Requires: Python with Nuitka installed (pip install -U nuitka), MSVC Build Tools, and ImageMagick (for Wand)
# Usage:  ./build_nuitka.ps1 [-Clean]
param(
  [switch]$Clean
)

$ErrorActionPreference = 'Stop'

# Resolve project root as script location
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ProjectRoot

try {
  if ($Clean) {
    Write-Host 'Cleaning previous Nuitka outputs...' -ForegroundColor Yellow
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue 'build' ,'dist','dist-nuitka','*.onefile.exe','*.build','*.dist'
  }

  # Read version from script/version.py
  $versionPy = Join-Path $ProjectRoot 'script/version.py'
  if (-not (Test-Path $versionPy)) { throw 'script/version.py not found' }
  $verContent = Get-Content $versionPy -Raw
  $m = [regex]::Match($verContent, '__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"')
  if (-not $m.Success) {
    # fallback to VERSION tuple
    $m2 = [regex]::Match($verContent, 'VERSION\s*=\s*\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\)')
    if (-not $m2.Success) { throw 'Could not parse version from script/version.py' }
    $Version = "$($m2.Groups[1].Value).$($m2.Groups[2].Value).$($m2.Groups[3].Value)"
  } else {
    $Version = $m.Groups[1].Value
  }

  Write-Host "Building PDF Duplicate Finder v$Version with Nuitka..." -ForegroundColor Cyan

  # Ensure Nuitka is available
  $python = 'python'
  # $nuitkaVersion = & $python -m nuitka --version 2>$null
  if ($LASTEXITCODE -ne 0) {
    throw 'Nuitka is not installed. Run: python -m pip install -U nuitka'
  }

  # Run Nuitka with inline options (avoid --config-file for broader compatibility)
  & $python -m nuitka `
    --onefile `
    --remove-output `
    --assume-yes-for-downloads `
    --windows-console-mode=disable `
    --windows-icon-from-ico=assets/icon.ico `
    --enable-plugin=pyqt6 `
    --include-qt-plugins=printsupport,svg,widgets `
    --include-package=PyQt6 `
    --include-package=fitz `
    --include-package=PyMuPDF `
    --include-package=wand `
    --include-package=numpy `
    --include-package=cv2 `
    --include-package=tqdm `
    --include-package=send2trash `
    --include-package=psutil `
    --include-data-files=assets/icon.ico=assets/icon.ico `
    --include-data-files=assets/version_info.txt=assets/version_info.txt `
    --include-data-files=config/settings.json=config/settings.json `
    --include-data-files=config/updates.json=config/updates.json `
    --include-data-files=docs/GUIDA_UTENTE.md=docs/GUIDA_UTENTE.md `
    --include-data-files=docs/USER_GUIDE.md=docs/USER_GUIDE.md `
    --include-data-dir=lang=lang `
    --include-data-dir=docs=docs `
    --nofollow-import-to=scipy `
    --nofollow-import-to=skimage `
    --nofollow-import-to=PIL `
    --company-name="Tuxxle" `
    --product-name="PDF Duplicate Finder" `
    --file-description="A tool to find and manage duplicate PDF files." `
    --file-version="$Version" `
    --product-version="$Version" `
    --copyright="© 2025 Nsfr750" `
    --output-dir=dist `
    --output-filename=PDF-Finder `
    main.py

  if ($LASTEXITCODE -ne 0) { throw "Nuitka build failed with exit code $LASTEXITCODE" }

  Write-Host 'Build completed.' -ForegroundColor Green
  Write-Host 'Output directory: dist-nuitka' -ForegroundColor Green
}
finally {
  Pop-Location
}
