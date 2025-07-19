"""
Build configuration for PDF_Finder installers.

This module contains all the build configurations for creating platform-specific
installers and packages for PDF_Finder.
"""
from pathlib import Path
import sys
import os
from typing import Dict, Any, List, Optional

# Project information
PROJECT_NAME = "PDF_Finder"
AUTHOR = "Nsfr750"
EMAIL = "nsfr750@yandex.com"
DESCRIPTION = "A powerful tool for finding, managing, and organizing PDF files"
LONG_DESCRIPTION = """PDF_Finder is a comprehensive PDF management tool that helps you:
- Find and remove duplicate PDF files
- Search and organize your PDF collection
- Extract text and metadata from PDFs
- Convert between different PDF formats
- And much more!
"""
COPYRIGHT = f"© 2023-2025 {AUTHOR}"
LICENSE = "GPLv3"
HOMEPAGE = "https://github.com/Nsfr750/PDF_finder"
SUPPORT_URL = f"{HOMEPAGE}/issues"
DOCS_URL = f"{HOMEPAGE}/wiki"

# Try to get version from script/version.py
try:
    version = {}
    version_file = Path(__file__).parent / "script" / "version.py"
    with open(version_file, 'r', encoding='utf-8') as f:
        exec(f.read(), version)
    VERSION = version.get('__version__', '0.0.0')
except Exception as e:
    VERSION = '0.0.0'

# Paths
ROOT_DIR = Path(__file__).parent.absolute()
ASSETS_DIR = ROOT_DIR / "images"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
SCRIPT_DIR = ROOT_DIR / "script"
DOCS_DIR = ROOT_DIR / "docs"
LOCALE_DIR = ROOT_DIR / "locales"
CONFIG_DIR = ROOT_DIR / "config"
NSISDIR = "C:\Program Files\NSIS"
# Ensure required directories exist
for directory in [DIST_DIR, BUILD_DIR, ASSETS_DIR, SCRIPT_DIR, DOCS_DIR, LOCALE_DIR, CONFIG_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Platform-specific configurations
PLATFORMS = {
    "Windows": {
        "name": "Windows",
        "executable": f"{PROJECT_NAME}.exe",
        "installer": {
            "type": "nsis",
            "extension": "exe",
            "extra_args": [
                "--windowed",
                "--onefile",
                "--noconsole",
                "--name", f"{PROJECT_NAME}-{VERSION}-Windows",
                "--icon", str(ASSETS_DIR / "icon.ico"),
                "--version-file", str(ASSETS_DIR / "version_info.txt"),
            ],
            "nsis": {
                "install_icon": str(NSISDIR / "Contrib/Graphics/Icons/box-install.ico"),
                "uninstall_icon": str(NSISDIR / "Contrib/Graphics/Icons/box-uninstall.ico"),
                "header_image": str(NSISDIR / "Contrib/Graphics/Header/orange.bmp"),
                "wizard_image": str(NSISDIR / "Contrib/Graphics/Header/orange-uninstall.bmp"),
                "sidebar_image": str(NSISDIR / "Contrib/Graphics/Wizard/orange.bmp"),
                "installer_name": f"{PROJECT_NAME}-{VERSION}-Setup"
            }
        },
        "archive": {
            "formats": ["zip", "7z"],
            "include": ["*.exe", "*.dll", "*.pyd", "LICENSE", "README.md"]
        }
    },
    "Darwin": {
        "name": "macOS",
        "executable": f"{PROJECT_NAME}.app",
        "installer": {
            "type": "dmg",
            "extension": "dmg",
            "extra_args": [
                "--windowed",
                "--osx-bundle-identifier", f"com.{AUTHOR.lower()}.{PROJECT_NAME.lower()}",
                "--icon", str(ASSETS_DIR / "icon.icns"),
                "--name", f"{PROJECT_NAME}-{VERSION}-macOS",
                "--osx-entitlements-file", str(ASSETS_DIR / "entitlements.plist"),
            ],
            "dmg": {
                "volume_name": f"{PROJECT_NAME} {VERSION}",
                "background": str(ASSETS_DIR / "dmg-background.png"),
                "icon_size": 80,
                "text_size": 12,
                "window_rect": {"x": 100, "y": 100, "width": 500, "height": 300}
            }
        },
        "archive": {
            "formats": ["tar.gz", "zip"],
            "include": ["*.app", "LICENSE", "README.md"]
        }
    },
    "Linux": {
        "name": "Linux",
        "executable": PROJECT_NAME,
        "installer": {
            "type": "appimage",
            "extension": "AppImage",
            "extra_args": [
                "--windowed",
                "--name", f"{PROJECT_NAME}-{VERSION}-Linux",
                "--icon", str(ASSETS_DIR / "icon.png"),
                "--runtime-tmpdir", "/tmp"
            ],
            "appimage": {
                "update-information": None,
                "sign": True,
                "sign-args": ["--sign"],
                "runtime-file": "appruntime"
            }
        },
        "archive": {
            "formats": ["tar.gz", "zip"],
            "include": ["*.AppImage", "*.desktop", "LICENSE", "README.md"]
        },
        "deb": {
            "enabled": True,
            "dependencies": ["python3", "python3-pip"],
            "maintainer": f"{AUTHOR} <nsfr750@yandex.com>",
            "section": "utils",
            "architecture": "amd64",
            "description": DESCRIPTION,
            "pre_install_script": "preinst",
            "post_install_script": "postinst",
            "pre_uninstall_script": "prerm",
            "post_uninstall_script": "postrm"
        }
    }
}

# Common PyInstaller configurations
PYINSTALLER_CONFIG = {
    # Core build settings
    "name": PROJECT_NAME,
    "version": VERSION,
    "description": DESCRIPTION,
    "author": AUTHOR,
    "copyright": COPYRIGHT,
    "license": LICENSE,
    
    # Build behavior
    "console": False,  # Set to True for console applications
    "debug": False,
    "strip": True,
    "upx": True,
    "upx_exclude": [],
    "no_compress": False,
    "optimize": 2,  # -O2 optimization level
    "clean_build": True,
    "noconfirm": True,  # Overwrite output directory without confirmation
    "noupx": False,  # Set to True to disable UPX compression
    "ascii": False,  # Do not include encodings and codecs for other charsets
    "bootloader_ignore_signals": False,
    "bootloader_no_sandbox": False,
    "codesign_identity": None,  # macOS code signing identity
    "codesign_entitlements": None,  # Path to entitlements file for macOS
    "codesign_deep": True,  # Sign all binaries in the bundle
    "codesign_timestamp": True,  # Add timestamp to code signature
    "codesign_verify": True,  # Verify the code signature after building
    "entitlements_file": None,  # Path to entitlements file for code signing
    "icon": str(ASSETS_DIR / "icon.ico"),  # Default icon
    "version_file": str(ASSETS_DIR / "version_info.txt"),  # Windows version info
    "manifest": None,  # Path to manifest file for Windows
    "no_embed_manifest": False,  # Do not embed the manifest in the executable
    "uac_admin": False,  # Request UAC elevation on Windows
    "uac_uiaccess": False,  # Allow UI automation on Windows
    "windowed": True,  # Run without a console window
    "disable_windowed_traceback": False,  # Disable traceback in windowed mode
    "target_arch": None,  # Target architecture (None = auto-detect)
    "codesign_identity": None,  # Code signing identity for macOS
    "osx_bundle_identifier": f"com.{AUTHOR.lower()}.{PROJECT_NAME.lower()}",
    "osx_min_system_version": "10.15",  # Minimum macOS version
    "osx_signing_identity_name": None,  # Name of the signing identity
    "osx_signing_cert_name": None,  # Name of the certificate in the keychain
    "osx_signing_keychain": None,  # Path to the keychain file
    "osx_notarization_identity": None,  # Apple ID for notarization
    "osx_notarization_password": None,  # App-specific password for notarization
    "osx_notarization_entitlements": None,  # Path to entitlements file for notarization
    "osx_notarization_bundle_id": None,  # Bundle ID for notarization
    "osx_notarization_asc_provider": None,  # Team ID for notarization
    "osx_notarization_tool": "altool",  # Tool for notarization (altool or notarytool)
    "osx_notarization_timeout": 600,  # Timeout for notarization in seconds
    "osx_notarization_verify": True,  # Verify notarization after completion
    "osx_notarization_staple": True,  # Staple the notarization ticket
    "osx_notarization_staple_timeout": 300,  # Timeout for stapling in seconds
    "osx_notarization_staple_verify": True,  # Verify stapling after completion
    "osx_notarization_staple_retries": 3,  # Number of retries for stapling
    "osx_notarization_staple_retry_delay": 10,  # Delay between retries in seconds
    
    # Hidden imports - Python modules to include in the executable
    "hidden_imports": [
        # Core Python modules
        'os', 'sys', 'json', 'logging', 'pathlib', 'typing', 'datetime',
        'subprocess', 'shutil', 'glob', 're', 'io', 'base64', 'hashlib',
        'functools', 'collections', 'itertools', 'threading', 'queue',
        'concurrent.futures', 'urllib', 'urllib.parse', 'urllib.request',
        'urllib.error',
        
        # Third-party packages
        'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
        'PyQt6.QtNetwork', 'PyQt6.QtPrintSupport', 'PyQt6.QtSvg',
        'PyQt6.QtSvgWidgets', 'wand', 'wand.image', 'wand.version',
        'send2trash', 'python_magic', 'dateutil', 'dateutil.parser',
        'dateutil.tz', 'packaging', 'packaging.version',
        'packaging.specifiers', 'packaging.requirements',
        
        # Platform-specific
        *(['win32timezone', 'pywin32'] if sys.platform == 'win32' else []),
        *(['appdirs'] if sys.platform != 'win32' else [])
    ],
    
    # Data files to include in the distribution
    "datas": [
        (str(ASSETS_DIR), "assets"),
        (str(LOCALE_DIR), "locales"),
        (str(DOCS_DIR), "docs"),
        (str(SCRIPT_DIR), "script"),
        (str(CONFIG_DIR), "config"),
        (str(ROOT_DIR / "README.md"), "."),
        (str(ROOT_DIR / "LICENSE"), "."),
        (str(ROOT_DIR / "CHANGELOG.md"), ".")
    ],
    
    # Binary files to include
    "binaries": [],
    
    # Python modules to exclude
    "excludes": [
        'tkinter', 'tcl', 'tk', '_tkinter', 'tcl8*', 'tcl9*', 'tcl1*',
        'tcl2*', 'tcl3*', 'tcl4*', 'tcl5*', 'tcl6*', 'tcl7*',
        'PIL', 'pillow', 'numpy', 'matplotlib', 'pandas', 'scipy',
        'pytest', 'unittest', 'test', 'tests', 'setuptools', 'pip',
        'wheel', 'pkg_resources', 'distutils', 'email', 'http', 'xml',
        'pydoc', 'doctest', 'pdb', 'pdb.py', 'pdb.doc', 'pdb.doc.*',
        'pdb.doc.*.*', 'pdb.doc.*.*.*', 'pdb.doc.*.*.*.*',
        'pdb.doc.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
        'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*', 'pdb.doc.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*.*',
    ]
}
