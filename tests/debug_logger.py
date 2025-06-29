import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the logger module
from utils import logger

def test_logger():
    print("=== Starting Logger Test ===")
    
    # Get absolute path for log file
    log_dir = Path(__file__).parent / 'logs'
    log_file = log_dir / 'test_application.log'
    
    print(f"Log file path: {log_file}")
    print(f"Absolute path: {log_file.absolute()}")
    
    # Ensure log directory exists
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Clean up any existing log file
    if log_file.exists():
        print("Removing existing log file...")
        try:
            log_file.unlink()
            print("Existing log file removed.")
        except Exception as e:
            print(f"Error removing log file: {e}")
    
    print("\n=== Configuring Logger ===")
    # Configure logger with absolute path
    logger.configure_logging(
        enabled=True,
        level='DEBUG',
        log_file=str(log_file.absolute()),
        log_to_console=True
    )
    
    print("\n=== Testing Log Levels ===")
    # Test logging at different levels
    print("Logging debug message...")
    logger.log_debug("This is a debug message")
    
    print("Logging info message...")
    logger.log_info("This is an info message")
    
    print("Logging warning message...")
    logger.log_warning("This is a warning message")
    
    print("Logging error message...")
    logger.log_error("This is an error message")
    
    # Force flush
    print("\n=== Flushing Logs ===")
    logger._write_log('DEBUG', 'flush')
    
    print("\n=== Verifying Log File ===")
    # Verify log file was created and has content
    if not log_file.exists():
        print(f"ERROR: Log file {log_file} was not created!")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir(log_dir)}")
        return False
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\n=== LOG FILE CONTENT ===")
            print(content)
            print("=======================")
            
            if not content:
                print("ERROR: Log file is empty!")
                return False
                
            required_messages = [
                'DEBUG', 'INFO', 'WARNING', 'ERROR',
                'debug message', 'info message', 'warning message', 'error message'
            ]
            
            all_found = True
            for msg in required_messages:
                if msg.lower() not in content.lower():
                    print(f"WARNING: Expected message not found in log: {msg}")
                    all_found = False
            
            if all_found:
                print("SUCCESS: All expected log messages found!")
            
    except Exception as e:
        print(f"ERROR reading log file: {e}")
        return False
    
    print("\nLogger test completed!")
    return True

if __name__ == "__main__":
    test_logger()
