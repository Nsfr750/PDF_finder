import subprocess
import os
import sys

def main():
    print("Building PDF Duplicate Finder with Nuitka...")
    
    # Get the script directory for proper path resolution
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Clean previous builds
    if os.path.exists("../dist-nuitka"):
        print("Cleaning previous build...")
        import shutil
        shutil.rmtree("../dist-nuitka")
    
    # Get version from version.py
    try:
        # Import the version module directly
        import sys
        sys.path.insert(0, os.path.join(project_root, 'script', 'utils'))
        from version import VERSION, __version__
        
        # Create version strings in the required format (X.Y.Z.W)
        version_tuple = list(VERSION)
        while len(version_tuple) < 4:
            version_tuple.append(0)
        version_str = '.'.join(map(str, version_tuple[:4]))
        display_version = __version__
        
    except Exception as e:
        print(f"Warning: Could not read version: {e}")
        # Fallback to default version
        version_str = "3.0.0"
        display_version = "3.0.0"
    
    print(f"Building version: {display_version} (using build version: {version_str})")
    
    # Build command
    cmd = [
        sys.executable,
        "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--output-dir=os.path.join(project_root, 'dist')",
        "--output-filename=PDF-Finder_3.0.0",
        f"--windows-icon-from-ico={os.path.join(project_root, 'assets', 'icon.ico')}",
        "--company-name=Tuxxle",
        "--product-name=PDF Duplicate Finder",
        "--file-description=Find and manage duplicate PDF files.",
        f"--file-version={version_str}",
        f"--product-version={version_str}",
        "--copyright=© 2025 Nsfr750 - All rights reserved",
        "--enable-plugin=pyqt6",
        "--follow-imports",
        "--follow-stdlib",
        "--include-package=tqdm",
        "--include-package=send2trash",
        "--include-package=psutil",
        "--include-package=PyQt6",
        "--include-package=PyQt6.QtPrintSupport",
        "--include-package=PyQt6.QtSvg",
        "--include-package=PyQt6.QtWidgets",
        f"--include-data-files={os.path.join(project_root, 'assets', 'icon.ico')}=assets/icon.ico",
        f"--include-data-files={os.path.join(project_root, 'assets', 'logo.png')}=assets/logo.png",
        f"--include-data-files={os.path.join(project_root, 'assets', 'version_info.txt')}=assets/version_info.txt",
        f"--include-data-files={os.path.join(project_root, 'config', 'settings.json')}=config/settings.json",
        f"--include-data-files={os.path.join(project_root, 'config', 'updates.json')}=config/updates.json",
        f"--include-data-dir={os.path.join(project_root, 'assets')}=assets",
        f"--include-data-dir={os.path.join(project_root, 'config')}=config",
        f"--include-data-dir={os.path.join(project_root, 'script', 'lang')}=script/lang",
        "--nofollow-import-to=*.tests,*.test,*.unittest,*.setuptools,*.distutils,*.pkg_resources",
        "--nofollow-import-to=*.pytest,*.setuptools_rust",
        "--nofollow-import-to=scipy",
        "--nofollow-import-to=skimage",
        "--nofollow-import-to=PIL",
        "--remove-output",
        "--assume-yes-for-downloads",
        "--windows-console-mode=disable",
        os.path.join(project_root, 'main.py')
    ]
    
    # Run the command
    print("Starting build...")
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")
        print(f"Output directory: {os.path.abspath('../dist')}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
