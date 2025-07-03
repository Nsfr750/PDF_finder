#!/usr/bin/env python3
"""
Compile translation files (.ts) to binary format (.qm) using PySide6's lrelease.
"""
import os
import sys
import subprocess
from pathlib import Path

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
    
    # Get the path to lrelease
    try:
        from PySide6.utilities.lrelease import run_lrelease
        use_module = True
    except ImportError:
        use_module = False
    
    # Compile each .ts file to .qm
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix('.qm')
        print(f"Compiling {ts_file} to {qm_file}...")
        
        try:
            if use_module:
                # Use the Python module if available
                args = [str(ts_file), '-qm', str(qm_file)]
                if not run_lrelease(args):
                    print(f"Error compiling {ts_file}")
                    return False
            else:
                # Fall back to subprocess
                cmd = [
                    sys.executable, 
                    '-m', 'PySide6.utilities.lrelease',
                    str(ts_file),
                    '-qm', str(qm_file)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
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
