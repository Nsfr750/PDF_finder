"""
Setup script for PDF Duplicate Finder.
This is kept for backward compatibility and editable installs.
The main configuration is in pyproject.toml.
"""
from pathlib import Path
from setuptools import setup

# Create version_info.txt in the assets folder
def create_version_info():
    """Generate version info file with build information."""
    version = "2.9.1"  # Default version if not found
    try:
        with open("script/version.py", encoding="utf-8") as fp:
            for line in fp:
                if line.startswith("__version__"):
                    version = line.split('=')[1].strip().strip('\"\'')
                    break
    except (FileNotFoundError, Exception) as e:
        print(f"Warning: Could not read version from script/version.py: {e}")
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    from datetime import datetime, timezone
    build_date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    version_info = f"""# PDF Duplicate Finder Version Information
Version: {version}
Build Date: {build_date}
Author: Nsfr750
License: GPL-3.0-or-later
Website: https://github.com/Nsfr750/PDF_finder
Source: https://github.com/Nsfr750/PDF_finder
Issues: https://github.com/Nsfr750/PDF_finder/issues
"""
    with open(assets_dir / "version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info)
    
    return version

def read_requirements():
    """Read requirements from requirements.txt if it exists."""
    requirements = []
    try:
        with open("requirements.txt", encoding="utf-8") as f:
            requirements = [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        print("Warning: requirements.txt not found, using default dependencies")
        requirements = [
            "PyMuPDF>=1.21.0",
            "PyPDF2>=3.0.0",
            "PyQt6>=6.4.0",
            "Wand>=0.6.10",
            "imagehash>=4.3.1",
            "numpy>=1.24.0",
            "pdf2image>=1.16.3",
            "pillow>=9.5.0",
            "python-dotenv>=1.0.0",
            "requests>=2.31.0",
            "scikit-image>=0.21.0",
            "tqdm>=4.66.0"
        ]
    return requirements

if __name__ == "__main__":
    version = create_version_info()
    
    setup(
        name="pdf-finder",
        version=version,
        python_requires=">=3.9",
        install_requires=read_requirements(),
        package_dir={"": "."},
        packages=["script"],
        package_data={
            "": [
                "assets/*",
                "config/*",
                "lang/*",
                "*.md",
                "*.txt"
            ]
        },
        entry_points={
            "gui_scripts": [
                "pdf-finder=main:main"
            ],
            "console_scripts": [
                "pdf-finder-cli=main:main"
            ]
        }
    )
