import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the logger module
from utils import logger

def main():
    print("=== Starting Minimal Logger Test ===")
    
    # Set up log file path
    log_file = 'minimal_test.log'
    print(f"Log file: {os.path.abspath(log_file)}")
    
    # Configure logger
    print("Configuring logger...")
    logger.configure_logging(
        enabled=True,
        level='DEBUG',
        log_file=log_file,
        log_to_console=True
    )
    
    # Test logging
    print("\n=== Testing Log Levels ===")
    print("Logging debug message...")
    logger.log_debug("Debug message from minimal test")
    
    print("Logging info message...")
    logger.log_info("Info message from minimal test")
    
    # Force flush
    print("\nFlushing logs...")
    logger._write_log('DEBUG', 'flush')
    
    # Check if file was created
    if os.path.exists(log_file):
        print(f"\nLog file created at: {os.path.abspath(log_file)}")
        print("\n=== File Content ===")
        with open(log_file, 'r') as f:
            print(f.read())
    else:
        print(f"\nERROR: Log file was not created at {os.path.abspath(log_file)}")
        print("Current directory:", os.getcwd())
        print("Directory contents:", os.listdir('.'))

if __name__ == "__main__":
    main()
