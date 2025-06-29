import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the logger module
from utils import logger

def main():
    print("=== Starting Logger Test ===", file=sys.stderr)
    
    # Use a temporary directory for the log file
    temp_dir = tempfile.mkdtemp(prefix="pdf_finder_test_")
    log_file = os.path.join(temp_dir, "test_application.log")
    
    print(f"Using temporary directory: {temp_dir}", file=sys.stderr)
    print(f"Log file: {log_file}", file=sys.stderr)
    
    try:
        # Configure logger with absolute path
        print("\nConfiguring logger...", file=sys.stderr)
        logger.configure_logging(
            enabled=True,
            level='DEBUG',
            log_file=log_file,
            log_to_console=True
        )
        
        # Test logging
        print("\n=== Testing Log Levels ===", file=sys.stderr)
        print("Logging debug message...", file=sys.stderr)
        logger.log_debug("This is a debug message")
        
        print("Logging info message...", file=sys.stderr)
        logger.log_info("This is an info message")
        
        print("Logging warning message...", file=sys.stderr)
        logger.log_warning("This is a warning message")
        
        print("Logging error message...", file=sys.stderr)
        logger.log_error("This is an error message")
        
        # Force flush
        print("\nFlushing logs...", file=sys.stderr)
        logger._write_log('DEBUG', 'flush')
        
        # Verify log file was created
        if os.path.exists(log_file):
            print(f"\nLog file created at: {log_file}", file=sys.stderr)
            print("\n=== File Content ===", file=sys.stderr)
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content, file=sys.stderr)
                print("\n=== Test Successful ===", file=sys.stderr)
                print(f"Log file location: {log_file}", file=sys.stderr)
                return True
        else:
            print(f"\nERROR: Log file was not created at {log_file}", file=sys.stderr)
            print(f"Current directory: {os.getcwd()}", file=sys.stderr)
            print(f"Directory contents: {os.listdir(temp_dir)}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False
    finally:
        # Clean up the temporary directory
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temporary directory: {e}", file=sys.stderr)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
