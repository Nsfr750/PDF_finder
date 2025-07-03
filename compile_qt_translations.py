#!/usr/bin/env python3
"""
Compile Qt translation files (.ts) to binary format (.qm).
"""
import os
import sys
import subprocess
from pathlib import Path
from PySide6.QtCore import QLibraryInfo

def find_lrelease():
    """Find the lrelease executable."""
    # Try to find lrelease in the Qt bin directory
    qt_bin_dir = QLibraryInfo.location(QLibraryInfo.BinariesPath)
    if qt_bin_dir:
        lrelease_path = Path(qt_bin_dir) / 'lrelease'
        if os.name == 'nt':
            lrelease_path = lrelease_path.with_suffix('.exe')
        
        if lrelease_path.exists():
            return str(lrelease_path)
    
    # Try to find lrelease in the system PATH
    which_cmd = 'where' if os.name == 'nt' else 'which'
    try:
        result = subprocess.run(
            [which_cmd, 'lrelease'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None

def compile_translations():
    """Compile all .ts files in the translations directory."""
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
    
    # Find lrelease
    lrelease_path = find_lrelease()
    if not lrelease_path:
        print("Error: Could not find lrelease executable. Make sure it's in your PATH.")
        return False
    
    print(f"Using lrelease at: {lrelease_path}")
    
    # Compile each .ts file to .qm
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix('.qm')
        print(f"Compiling {ts_file} to {qm_file}...")
        
        try:
            result = subprocess.run(
                [lrelease_path, str(ts_file), '-qm', str(qm_file)],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print(f"Error compiling {ts_file}:")
                print(result.stderr)
                return False
                
            print(f"Successfully compiled {qm_file}")
                
        except Exception as e:
            print(f"Error compiling {ts_file}: {e}")
            return False
    
    print("All translations compiled successfully.")
    return True

if __name__ == "__main__":
    if compile_translations():
        sys.exit(0)
    else:
        sys.exit(1)
