#!/usr/bin/env python3
"""
PyPI Publishing Script for PDF Duplicate Finder

This script automates the process of building and publishing the PDF Duplicate Finder
package to PyPI. It handles both test and production PyPI repositories.

Usage:
    python publish_to_pypi.py --test          # Publish to test PyPI
    python publish_to_pypi.py --prod          # Publish to production PyPI
    python publish_to_pypi.py --build-only    # Only build, don't upload
    python publish_to_pypi.py --check         # Only check, don't build or upload

Requirements:
    - twine must be installed: pip install twine
    - PyPI API token configured in ~/.pypirc or as environment variable
"""

import argparse
import subprocess
import sys
import os
import shutil
import glob
from pathlib import Path
import tempfile
import zipfile
import tarfile


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_requirements():
    """Check if all required tools are available."""
    print("Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check required packages
    required_packages = ['build', 'twine', 'setuptools', 'wheel']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + ' '.join(missing_packages))
        sys.exit(1)
    
    print("✓ All requirements satisfied")


def check_project_structure():
    """Check if the project structure is correct for publishing."""
    print("Checking project structure...")
    
    required_files = [
        '../pyproject.toml',
        '../README.md',
        '../LICENSE',
        '../script/version.py',
        '../main.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing required files: {', '.join(missing_files)}")
        sys.exit(1)
    
    # Check if version.py can be imported
    try:
        sys.path.insert(0, str(Path('../script')))
        from version import __version__
        print(f"✓ Version found: {__version__}")
    except ImportError as e:
        print(f"Error importing version: {e}")
        sys.exit(1)
    
    print("✓ Project structure is valid")


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    directories_to_clean = [
        '../build',
        '../dist',
        '../pdf_finder.egg-info'
    ]
    
    for directory in directories_to_clean:
        if Path(directory).exists():
            print(f"Removing {directory}...")
            shutil.rmtree(directory)
    
    # Clean Python cache
    for pattern in ['**/__pycache__', '**/*.pyc', '**/*.pyo']:
        for path in glob.glob(pattern, recursive=True):
            if Path(path).is_dir():
                shutil.rmtree(path)
            else:
                Path(path).unlink()
    
    print("✓ Build artifacts cleaned")


def build_package():
    """Build the package using python -m build."""
    print("Building package...")
    
    # Clean first
    clean_build_artifacts()
    
    # Build the package
    result = run_command([sys.executable, '-m', 'build'], cwd='..')
    
    # Check if build artifacts were created
    dist_files = list(Path('../dist').glob('*'))
    if not dist_files:
        print("Error: No build artifacts found in dist/ directory")
        sys.exit(1)
    
    print("✓ Package built successfully:")
    for file in dist_files:
        print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    return dist_files


def check_package():
    """Check the built package for common issues."""
    print("Checking package...")
    
    dist_files = list(Path('../dist').glob('*'))
    if not dist_files:
        print("Error: No files to check in dist/ directory")
        return False
    
    # Check with twine check
    print("Running twine check...")
    result = run_command([sys.executable, '-m', 'twine', 'check', '../dist/*'])
    
    if result.returncode != 0:
        print("Error: Package check failed")
        return False
    
    # Check file sizes
    for file in dist_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  - {file.name}: {size_mb:.2f} MB")
        
        # Warn if files are too large
        if size_mb > 100:
            print(f"Warning: {file.name} is very large ({size_mb:.2f} MB)")
    
    print("✓ Package check passed")
    return True


def upload_to_pypi(repository='testpypi'):
    """Upload the package to PyPI."""
    print(f"Uploading to {repository}...")
    
    # Check if twine is configured
    try:
        result = run_command([sys.executable, '-m', 'twine', 'upload', '--help'], check=False)
        if result.returncode != 0:
            print("Error: twine is not properly configured")
            return False
    except Exception as e:
        print(f"Error checking twine configuration: {e}")
        return False
    
    # Upload the package
    cmd = [sys.executable, '-m', 'twine', 'upload']
    
    if repository == 'testpypi':
        cmd.extend(['--repository', 'testpypi'])
    
    cmd.extend(['../dist/*'])
    
    print(f"Uploading with command: {' '.join(cmd)}")
    print("Note: You may be prompted for PyPI credentials")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✓ Upload completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error uploading to PyPI: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Publish PDF Duplicate Finder to PyPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python publish_to_pypi.py --test          # Publish to test PyPI
  python publish_to_pypi.py --prod          # Publish to production PyPI
  python publish_to_pypi.py --build-only    # Only build, don't upload
  python publish_to_pypi.py --check         # Only check, don't build or upload
        """
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Publish to test PyPI (default action if no other flag specified)'
    )
    
    parser.add_argument(
        '--prod',
        action='store_true',
        help='Publish to production PyPI'
    )
    
    parser.add_argument(
        '--build-only',
        action='store_true',
        help='Only build the package, do not upload'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check the package, do not build or upload'
    )
    
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip requirement and project structure checks'
    )
    
    args = parser.parse_args()
    
    print("PDF Duplicate Finder PyPI Publishing Script")
    print("=" * 50)
    
    # Determine action
    if args.prod:
        action = 'prod'
    elif args.build_only:
        action = 'build-only'
    elif args.check_only:
        action = 'check-only'
    else:
        action = 'test'  # Default to test PyPI
    
    print(f"Action: {action}")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"Working directory: {project_dir}")
    
    # Run checks
    if not args.skip_checks:
        check_requirements()
        check_project_structure()
    
    # Build package
    if action in ['test', 'prod', 'build-only']:
        dist_files = build_package()
        
        # Check package
        if not check_package():
            print("Package check failed. Aborting.")
            sys.exit(1)
    
    # Upload package
    if action == 'test':
        success = upload_to_pypi('testpypi')
        if success:
            print("\n🎉 Package published to test PyPI successfully!")
            print("You can install it with:")
            print("pip install --index-url https://test.pypi.org/simple/ pdf-finder")
        else:
            print("\n❌ Failed to publish to test PyPI")
            sys.exit(1)
    
    elif action == 'prod':
        # Confirm production upload
        print("\n⚠️  WARNING: You are about to publish to PRODUCTION PyPI!")
        print("This will make the package publicly available.")
        print("Please confirm that you have:")
        print("  - Tested the package thoroughly")
        print("  - Updated the version number")
        print("  - Updated the changelog")
        print("  - Verified all dependencies")
        
        response = input("\nType 'PRODUCTION' to continue: ")
        if response != 'PRODUCTION':
            print("Upload cancelled.")
            sys.exit(0)
        
        success = upload_to_pypi('pypi')
        if success:
            print("\n🎉 Package published to production PyPI successfully!")
            print("You can install it with:")
            print("pip install pdf-finder")
        else:
            print("\n❌ Failed to publish to production PyPI")
            sys.exit(1)
    
    elif action == 'build-only':
        print("\n📦 Package built successfully!")
        print("Files are available in the dist/ directory")
    
    elif action == 'check-only':
        print("\n✅ Package check completed successfully!")
    
    print("\nDone!")


if __name__ == '__main__':
    main()
