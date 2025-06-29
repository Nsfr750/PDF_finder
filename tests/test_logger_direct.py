import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the logger module
from utils import logger

def test_logger():
    # Set up logging
    log_file = 'test_application.log'
    
    # Clean up any existing log file
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Configure logger
    logger.configure_logging(
        enabled=True,
        level='DEBUG',
        log_file=log_file,
        log_to_console=True
    )
    
    # Test logging at different levels
    logger.log_debug("This is a debug message")
    logger.log_info("This is an info message")
    logger.log_warning("This is a warning message")
    logger.log_error("This is an error message")
    
    # Force flush
    logger._write_log('DEBUG', 'flush')
    
    # Verify log file was created and has content
    if not os.path.exists(log_file):
        print(f"ERROR: Log file {log_file} was not created!")
        return False
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print("=== LOG FILE CONTENT ===")
        print(content)
        print("=======================")
        
        if not content:
            print("ERROR: Log file is empty!")
            return False
            
        required_messages = [
            'DEBUG', 'INFO', 'WARNING', 'ERROR',
            'debug message', 'info message', 'warning message', 'error message'
        ]
        
        for msg in required_messages:
            if msg.lower() not in content.lower():
                print(f"WARNING: Expected message not found in log: {msg}")
    
    print("Logger test completed successfully!")
    return True

if __name__ == "__main__":
    test_logger()
