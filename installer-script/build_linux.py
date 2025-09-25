#!/usr/bin/env python3
"""
Linux build script for PDF Duplicate Finder.
Python equivalent of build_linux.sh for better cross-platform compatibility.
"""

import os
import sys
import subprocess
import shutil
import tarfile
from datetime import datetime

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def get_python_command():
    """Find the available Python command."""
    # Check if we're running from a virtual environment
    venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        print(f"Using virtual environment Python: {venv_python}")
        return venv_python
    
    # Try python3 first, then python
    for cmd in ["python3", "python"]:
        try:
            result = subprocess.run([cmd, "--version"], 
                                  capture_output=True, text=True, check=True)
            if result.returncode == 0:
                print(f"Using Python command: {cmd}")
                return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    print("Error: Neither python3 nor python found in PATH")
    sys.exit(1)

def get_version(project_root, python_cmd):
    """Get version from version.py file."""
    try:
        cmd = f'import sys; sys.path.insert(0, "script/utils"); from version import __version__; print(__version__)'
        result = subprocess.run(
            [python_cmd, "-c", cmd],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Warning: Could not read version from version.py, using default")
        return "3.0.0"

def check_nuitka(python_cmd):
    """Check if Nuitka is available."""
    try:
        subprocess.run(
            [python_cmd, "-c", "import nuitka"],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        print("Error: Nuitka is not installed. Please install it using:")
        print(f"  {python_cmd} -m pip install nuitka")
        print("Or visit: https://nuitka.net/doc/installation.html")
        return False

def clean_previous_builds(project_root, dist_dir):
    """Clean previous build artifacts."""
    dist_path = os.path.join(project_root, dist_dir)
    if os.path.exists(dist_path):
        print("Cleaning previous build...")
        try:
            shutil.rmtree(dist_path)
        except OSError as e:
            print(f"Warning: Could not remove {dist_path}: {e}")
            print("Attempting to remove contents manually...")
            try:
                for item in os.listdir(dist_path):
                    item_path = os.path.join(dist_path, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                # Try to remove the directory again
                try:
                    os.rmdir(dist_path)
                except OSError:
                    print(f"Warning: Could not remove directory {dist_path}, continuing anyway...")
            except Exception as e2:
                print(f"Warning: Failed to clean directory contents: {e2}")

def build_with_nuitka(project_root, python_cmd, output_bin, dist_dir):
    """Build the executable with Nuitka."""
    print(f"Building with Nuitka...")
    
    # Change to project root
    os.chdir(project_root)
    
    # Nuitka command arguments - updated for newer Nuitka version with fixes
    nuitka_cmd = [
        python_cmd, "-m", "nuitka",
        "--standalone",
        "--onefile",
        f"--output-filename={output_bin}",
        f"--output-dir={dist_dir}",
        "--windows-console-mode=force",  # Updated from --enable-console
        "--enable-plugin=pyqt6",  # Enable PyQt6 plugin for better Qt support
        "--include-package=PyQt6",
        "--include-package=PyQt6.QtCore",
        "--include-package=PyQt6.QtGui",
        "--include-package=PyQt6.QtWidgets",
        "--include-package=PyQt6.QtPrintSupport",
        "--include-package=PyQt6.QtSvg",
        "--include-package=tqdm",
        "--include-package=send2trash",
        "--include-package=psutil",
        "--include-data-files=assets/icon.ico=assets/icon.ico",
        "--include-data-files=assets/logo.png=assets/logo.png",
        "--include-data-files=assets/version_info.txt=assets/version_info.txt",
        "--include-data-files=config/settings.json=config/settings.json",
        "--include-data-files=config/updates.json=config/updates.json",
        "--include-data-dir=assets=assets",
        "--include-data-dir=config=config",
        # Note: script/lang contains Python modules, not data files, so we don't include it as data-dir
        "--follow-imports",
        "--nofollow-import-to=*.tests,*.test,*.unittest,*.setuptools,*.distutils,*.pkg_resources",
        "--nofollow-import-to=*.pytest,*.setuptools_rust",
        "--nofollow-import-to=scipy",
        "--nofollow-import-to=skimage",
        "--nofollow-import-to=PIL",
        "--remove-output",
        "--lto=no",  # Disable LTO to avoid compilation issues
        "--jobs=4",  # Reduce jobs to avoid memory issues
        "--assume-yes-for-downloads",
        "main.py"
    ]
    
    # Run Nuitka
    result = subprocess.run(nuitka_cmd, capture_output=True, text=True)
    
    # Print Nuitka output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0

def create_archive(project_root, dist_dir, output_bin, output_name):
    """Create a tar.gz archive of the built executable."""
    dist_path = os.path.join(project_root, dist_dir)
    bin_path = os.path.join(dist_path, output_bin)
    output_path = os.path.join(dist_path, output_name)
    archive_path = os.path.join(dist_path, f"{output_name}.tar.gz")
    
    if not os.path.exists(bin_path):
        print(f"Error: Build output file {output_bin} not found!")
        return False
    
    # Rename the binary
    os.rename(bin_path, output_path)
    
    # Create tar.gz archive
    print(f"Creating archive: {archive_path}")
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(output_path, arcname=output_name)
    
    # Get file size
    size_bytes = os.path.getsize(archive_path)
    size_mb = size_bytes / (1024 * 1024)
    
    print()
    print("Build completed successfully!")
    print(f"Output directory: {dist_path}")
    print(f"Archive: {output_name}.tar.gz")
    print(f"Size: {size_mb:.2f} MB")
    print(f"Executable: {output_name}")
    
    return True

def main():
    """Main build function."""
    # Get script directory for proper path resolution
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Get Python command
    python_cmd = get_python_command()
    
    # Get version from version.py
    version = get_version(project_root, python_cmd)
    
    # Build configuration
    output_name = f"PDF-Finder_{version}-linux"
    output_bin = f"PDF-Finder_{version}"
    dist_dir = "dist-nuitka"
    build_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Building PDF Duplicate Finder {version} for Linux...")
    print(f"Build date: {build_date}")
    print(f"Project root: {project_root}")
    
    # Clean previous builds
    clean_previous_builds(project_root, dist_dir)
    
    # Check if Nuitka is available
    if not check_nuitka(python_cmd):
        sys.exit(1)
    
    # Build with Nuitka
    build_success = build_with_nuitka(project_root, python_cmd, output_bin, dist_dir)
    
    if build_success:
        # Create archive
        archive_success = create_archive(project_root, dist_dir, output_bin, output_name)
        if not archive_success:
            sys.exit(1)
    else:
        print("Build failed. Check the output for errors.")
        sys.exit(1)
    
    print(f"Build completed on {build_date}")

if __name__ == "__main__":
    main()
