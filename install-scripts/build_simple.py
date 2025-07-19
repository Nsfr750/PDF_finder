#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF_Finder Build Script

This script handles building and packaging PDF_Finder for Windows.
It creates both an executable and a portable archive with all dependencies.
"""
import os
import sys
import subprocess
import shutil
import time
import logging
import argparse
import platform
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('build.log')
    ]
)
logger = logging.getLogger(__name__)

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.resolve()

def get_version() -> str:
    """Get the current version of PDF_Finder."""
    version_file = get_project_root() / 'script' / 'version.py'
    try:
        version = {}
        with open(version_file, 'r', encoding='utf-8') as f:
            exec(f.read(), version)
        return version.get('__version__', '0.0.0')
    except Exception as e:
        logger.warning(f"Could not read version from {version_file}: {e}")
        return '0.0.0'

def clean_directory(dir_path: Path) -> None:
    """
    Remove directory if it exists and recreate it.
    
    Args:
        dir_path: Path to the directory to clean
    """
    try:
        if dir_path.exists():
            logger.info(f"Cleaning directory: {dir_path}")
            shutil.rmtree(dir_path, ignore_errors=True)
        dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to clean directory {dir_path}: {e}")
        raise

def run_command(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Run a command and return (success, output).
    
    Args:
        cmd: Command to run as a list of strings
        cwd: Working directory for the command
        
    Returns:
        Tuple of (success, output)
    """
    try:
        logger.debug(f"Running command: {' '.join(str(arg) for arg in cmd)}")
        if cwd:
            logger.debug(f"Working directory: {cwd}")
            
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with return code {e.returncode}")
        logger.error(f"Command output: {e.output}")
        return False, e.output
    except Exception as e:
        error_msg = f"Unexpected error running command: {e}"
        logger.error(error_msg)
        return False, error_msg

def create_portable_archive(build_dir: Path, dist_dir: Path) -> bool:
    """
    Create a portable archive of the built application.
    
    Args:
        build_dir: Path to the build directory
        dist_dir: Path to the distribution directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("=" * 80)
    logger.info("📦 Creating portable archive")
    logger.info("=" * 80)
    
    exe_path = dist_dir / "PDF_Finder.exe"
    
    if not exe_path.exists():
        logger.error("Executable not found. Please build the application first.")
        return False
    
    # Get version information
    version_str = get_version()
    archive_name = f"PDF_Finder-Portable-v{version_str}.zip"
    archive_path = dist_dir / archive_name
    
    logger.info(f"Creating archive: {archive_path}")
    
    try:
        # Remove existing archive if it exists
        if archive_path.exists():
            archive_path.unlink()
        
        # Create a new archive
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the executable
            zipf.write(exe_path, arcname=exe_path.name)
            
            # Add additional files and directories
            additional_paths = [
                (build_dir / "assets", "assets"),
                (build_dir / "docs", "docs"),
                (build_dir / "LICENSE", "LICENSE"),
                (build_dir / "README.md", "README.md")
            ]
            
            for src_path, dest_path in additional_paths:
                if src_path.exists():
                    if src_path.is_file():
                        zipf.write(src_path, arcname=dest_path)
                    else:
                        for root, _, files in os.walk(src_path):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = Path(dest_path) / file_path.relative_to(src_path)
                                zipf.write(file_path, arcname=arcname)
            
            # Add a README.txt
            readme_content = f"""PDF_Finder Portable

This is a portable version of PDF_Finder. Simply extract this archive and run PDF_Finder.exe.

Version: {version_str}
Build date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Platform: {platform.system()} {platform.release()}
Python: {platform.python_version()}

For more information, please visit:
https://github.com/Nsfr750/PDF_finder
"""
            zipf.writestr("README.txt", readme_content)
        
        # Verify the archive was created successfully
        if not archive_path.exists():
            raise RuntimeError("Failed to create archive file")
            
        archive_size = archive_path.stat().st_size / (1024 * 1024)  # MB
        logger.info(f"Successfully created portable archive: {archive_path}")
        logger.info(f"Archive size: {archive_size:.2f} MB")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create portable archive: {e}", exc_info=True)
        if archive_path.exists():
            try:
                archive_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up failed archive: {cleanup_error}")
        return False

def build_installer() -> bool:
    """
    Build the Windows installer using PyInstaller.
    
    Returns:
        bool: True if the build was successful, False otherwise
    """
    logger.info("=" * 80)
    logger.info("🚀 Building PDF_Finder")
    logger.info("=" * 80)
    
    # Set up paths
    base_dir = get_project_root()
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    # Clean previous builds
    logger.info("🧹 Cleaning build directories...")
    clean_directory(build_dir)
    
    # Get version information
    version = get_version()
    logger.info(f"Building PDF_Finder version: {version}")
    
    # Define build configuration
    build_config = {
        "name": "PDF_Finder",
        "version": version,
        "description": "A tool for finding and managing PDF files",
        "author": "Nsfr750",
        "entry_point": str(base_dir / "main.py"),
        "icon": str(base_dir / "images" / "icon.ico"),
        "hidden_imports": [
            "script.about",
            "script.help",
            "script.log_viewer",
            "script.sponsor",
            "script.styles",
            "script.translations",
            "script.updates",
            "script.version",
            "script.settings_dialog",
            "script.menu",
            "script.logger",
            "script.language_manager",
            "script.workers",
            "script.image_dialog_preview",
            "script.empty_trash",
            "script.undo_manager",
            "script.update_preview"
        ],
        "data_files": [
            (str(base_dir / "images"), "assets"),
            (str(base_dir / "app_qt"), "script")
        ]
    }
    
    # Build PyInstaller command
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(build_dir),
        "--onefile",
        "--windowed",
        "--noconsole",
        "--name", build_config["name"],
        "--icon", build_config["icon"],
    ]
    
    # Add data files
    for src, dest in build_config["data_files"]:
        pyinstaller_cmd.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
    
    # Add hidden imports
    for hidden_import in build_config["hidden_imports"]:
        pyinstaller_cmd.extend(["--hidden-import", hidden_import])
    
    # Add the entry point
    pyinstaller_cmd.append(build_config["entry_point"])
    
    logger.info("🔨 Running PyInstaller command:")
    logger.info(" ".join(f'"{arg}"' if ' ' in str(arg) else str(arg) 
                        for arg in pyinstaller_cmd))
    
    # Run PyInstaller
    logger.info("📝 Starting PyInstaller build...")
    start_time = time.time()
    
    success, output = run_command(pyinstaller_cmd, cwd=base_dir)
    
    build_time = time.time() - start_time
    logger.info(f"Build completed in {build_time:.2f} seconds")
    
    # Check if build was successful
    exe_path = dist_dir / f"{build_config['name']}.exe"
    if success and exe_path.exists():
        exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        logger.info(f"✅ Successfully built: {exe_path}")
        logger.info(f"Executable size: {exe_size:.2f} MB")
        
        # Create portable archive after successful build
        create_portable_archive(build_dir, dist_dir)
        
        return True
    else:
        logger.error("❌ Build failed")
        if output:
            logger.error("Last 20 lines of output:")
            for line in output.splitlines()[-20:]:
                logger.error(line)
        return False

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Build PDF_Finder')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--clean', action='store_true', help='Clean build directories before building')
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    return parser.parse_args()

def main() -> int:
    """Main entry point for the build script."""
    args = parse_arguments()
    
    # Configure logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    try:
        if args.version:
            print(f"PDF_Finder Build Script - Version {get_version()}")
            return 0
            
        logger.info(f"Starting PDF_Finder build (Python {platform.python_version()})")
        logger.info(f"Platform: {platform.system()} {platform.release()}")
        
        if args.clean:
            logger.info("🧹 Cleaning build directories...")
            clean_directories()
        
        success = build_installer()
        return 0 if success else 1
        
    except Exception as e:
        logger.critical(f"Build failed with error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Build cancelled by user")
        sys.exit(1)
