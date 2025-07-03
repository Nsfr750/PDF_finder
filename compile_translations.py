#!/usr/bin/env python3
"""
Compile translation files (.ts) to binary format (.qm) using PySide6's lrelease.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_lrelease():
    """Find the lrelease executable."""
    # Try to find pyside6-lrelease in the Python scripts directory
    python_dir = os.path.dirname(sys.executable)
    
    # Check for Windows
    if sys.platform == 'win32':
        lrelease = os.path.join(python_dir, 'Scripts', 'pyside6-lrelease.exe')
        if os.path.exists(lrelease):
            return lrelease
    
    # Check for Unix-like systems
    lrelease = os.path.join(python_dir, 'bin', 'pyside6-lrelease')
    if os.path.exists(lrelease):
        return lrelease
    
    # Try to find it in the PATH
    lrelease = shutil.which('pyside6-lrelease')
    if lrelease:
        return lrelease
    
    # Try the direct path on Windows
    if sys.platform == 'win32':
        lrelease = os.path.join(os.path.dirname(python_dir), 'Scripts', 'pyside6-lrelease.exe')
        if os.path.exists(lrelease):
            return lrelease
    
    return None

def compile_translations():
    """Compile all .ts files in the translations directory."""
    # Find lrelease
    lrelease = find_lrelease()
    if not lrelease:
        print("Error: Could not find pyside6-lrelease. Make sure PySide6 is installed.")
        return False
    
    print(f"Using lrelease at: {lrelease}")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    translations_dir = script_dir / 'app_qt' / 'translations'
    
    if not translations_dir.exists():
        print(f"Error: Directory not found: {translations_dir}")
        return False
    
    # Find all .ts files
    ts_files = list(translations_dir.glob('*.ts'))
    
    if not ts_files:
        print(f"No .ts files found in {translations_dir}")
        return False
    
    # Compile each .ts file
    success = True
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix('.qm')
        print(f"Compiling {ts_file} to {qm_file}...")
        
        try:
            # Run pyside6-lrelease
            result = subprocess.run(
                [lrelease, str(ts_file)],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.returncode == 0:
                print(f"Successfully compiled {ts_file}")
            else:
                print(f"Error compiling {ts_file}:")
                print(result.stderr)
                success = False
                
        except subprocess.CalledProcessError as e:
            print(f"Error compiling {ts_file}:")
            print(e.stderr)
            success = False
        except Exception as e:
            print(f"Unexpected error compiling {ts_file}:")
            print(str(e))
            success = False
    
    return success

if __name__ == "__main__":
    if compile_translations():
        print("Translation compilation completed successfully.")
        sys.exit(0)
    else:
        print("Translation compilation failed.")
        sys.exit(1)

