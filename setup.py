from setuptools import setup
from pathlib import Path

# This setup.py is kept for backward compatibility
# The main configuration is now in pyproject.toml

# Create version_info.txt in the assets folder
def create_version_info():
    version = "1.0.0"
    try:
        with open("script/version.py") as fp:
            for line in fp:
                if line.startswith("__version__"):
                    version = line.split('=')[1].strip().strip('"\'')
                    break
    except FileNotFoundError:
        pass
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    with open(assets_dir / "version_info.txt", "w") as f:
        f.write(f"Version: {version}\n")
        f.write(f"Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Author: Nsfr750\n")
        f.write("License: GPL-3.0-or-later\n")
        f.write("Website: https://github.com/Nsfr750/PDF_finder\n")

if __name__ == "__main__":
    create_version_info()
    setup()
