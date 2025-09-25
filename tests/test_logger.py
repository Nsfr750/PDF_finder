#!/usr/bin/env python3
"""
Test script to verify that the logger correctly saves logs to the logs/ directory.
"""

import os
import sys
from pathlib import Path

# Add the script directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'script'))

from utils.logger import setup_logger, get_logs_dir

def test_logger():
    """Test that the logger correctly creates and writes to the logs/ directory."""
    
    print("Testing logger configuration...")
    
    # Get the logs directory
    logs_dir = get_logs_dir()
    print(f"Logs directory: {logs_dir}")
    print(f"Logs directory absolute path: {logs_dir.absolute()}")
    print(f"Logs directory exists: {logs_dir.exists()}")
    
    # Expected logs directory should be at project root
    expected_logs_dir = Path(__file__).parent / 'logs'
    print(f"Expected logs directory: {expected_logs_dir}")
    print(f"Expected logs directory absolute path: {expected_logs_dir.absolute()}")
    
    # Check if the paths match
    if logs_dir.absolute() == expected_logs_dir.absolute():
        print("✓ Logger correctly points to the project root logs/ directory")
    else:
        print("✗ Logger does not point to the expected logs/ directory")
        return False
    
    # Setup a test logger
    test_logger = setup_logger(name='TestLogger', log_level='INFO')
    
    # Log a test message
    test_logger.info("This is a test message to verify logger functionality")
    
    # Check if log files were created
    log_files = list(logs_dir.glob('TestLogger_*.log'))
    if log_files:
        print(f"✓ Log file created: {log_files[0]}")
        
        # Read and display the log file content
        try:
            with open(log_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✓ Log file content preview:")
                print(content[:200] + "..." if len(content) > 200 else content)
        except Exception as e:
            print(f"✗ Error reading log file: {e}")
            return False
    else:
        print("✗ No log files were created")
        return False
    
    print("✓ All logger tests passed!")
    return True

if __name__ == "__main__":
    success = test_logger()
    sys.exit(0 if success else 1)
