import os
import re
import sys
import datetime
import pytest
import traceback
from tkinter import messagebox
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the logger module directly
from utils import logger

APP_ROOT = Path(__file__).parent.parent
LOG_FILE = os.path.join(APP_ROOT, 'logs/application.log')

def clean_log():
    """Clean up log file and reset logger configuration."""
    try:
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
    except Exception as e:
        print(f"Warning: Could not remove log file: {e}")
    
    # Reset logger configuration
    logger._log_initialized = False
    # Reinitialize logger with test settings
    logger.configure_logging(
        enabled=True,
        level='DEBUG',
        log_file=LOG_FILE,
        log_to_console=False
    )
    
    # Verify log file can be written to
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write("=== LOGGER TEST SESSION STARTED ===\n")
    except Exception as e:
        print(f"ERROR: Cannot write to log file {LOG_FILE}: {e}")
        raise

def read_log():
    """Read and return the contents of the log file."""
    try:
        if not os.path.exists(LOG_FILE):
            print(f"Log file {LOG_FILE} does not exist")
            return ""
            
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                print(f"Log file {LOG_FILE} is empty")
            return content
    except Exception as e:
        print(f"Error reading log file: {e}")
        return ""

def test_log_info_and_warning_and_error():
    """Test logging at different levels."""
    clean_log()
    
    # Log test messages
    test_messages = [
        ('INFO', 'info test'),
        ('WARNING', 'warn test'),
        ('ERROR', 'error test')
    ]
    
    for level, msg in test_messages:
        if level == 'INFO':
            logger.log_info(msg)
        elif level == 'WARNING':
            logger.log_warning(msg)
        elif level == 'ERROR':
            logger.log_error(msg)
    
    # Force flush logs to disk
    logger._write_log('DEBUG', 'flush')
    
    # Verify log file exists and has content
    assert os.path.exists(LOG_FILE), f"Log file {LOG_FILE} was not created"
    
    # Read log contents
    contents = read_log()
    assert contents, "Log file is empty"
    
    # Verify each log level was recorded
    for level, msg in test_messages:
        assert f'[{level}]' in contents, f"Missing {level} level in log"
        assert msg in contents, f"Missing message '{msg}' in log"
        assert 'test_logger.py:test_log_info_and_warning_and_error' in contents, \
               f"Missing caller info for {level} message"

def test_log_exception():
    clean_log()
    try:
        raise ValueError('test exception')
    except Exception as e:
        logger.log_exception(type(e), e, e.__traceback__)
    # Ensure logs are written to disk
    logger._write_log('DEBUG', 'flush')
    contents = read_log()
    assert 'Uncaught exception:' in contents
    assert 'ValueError: test exception' in contents
    assert 'Traceback' in contents

def test_setup_global_exception_logging(monkeypatch):
    clean_log()
    def mock_sys_excepthook(type, value, tb):
        pass
    monkeypatch.setattr(sys, 'excepthook', mock_sys_excepthook)
    logger.setup_global_exception_logging()
    try:
        raise ValueError('test global exception')
    except ValueError:
        sys.excepthook(*sys.exc_info())
    # Ensure logs are written to disk
    logger._write_log('DEBUG', 'flush')
    contents = read_log()
    assert 'Traceback' in contents
    assert 'ValueError: test global exception' in contents


def run_tests():
    """
    Esegue i test del logger e mostra i risultati in una finestra di dialogo.
    Restituisce True se tutti i test sono passati, False altrimenti.
    """
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    # Cattura l'output dei test
    f = io.StringIO()
    
    try:
        # Esegui i test e cattura l'output
        with redirect_stdout(f), redirect_stderr(f):
            # Esegui pytest sui test in questo modulo
            result = pytest.main(
                [__file__, '-v'],
                plugins=[]
            )
            
        output = f.getvalue()
        
        # Verifica se i test sono passati (pytest restituisce 0 se tutti i test passano)
        if result == 0:
            messagebox.showinfo("Test Logger", "Tutti i test del logger sono passati con successo!\n\n" + output)
            return True
        else:
            messagebox.showerror("Test Logger Falliti", 
                               f"Alcuni test del logger sono falliti. Codice di uscita: {result}\n\n{output}")
            return False
            
    except Exception as e:
        error_msg = f"Errore durante l'esecuzione dei test: {str(e)}\n\n{traceback.format_exc()}"
        messagebox.showerror("Errore nei Test del Logger", error_msg)
        return False
    finally:
        f.close()


if __name__ == "__main__":
    # Se eseguito direttamente, esegui i test
    run_tests()
