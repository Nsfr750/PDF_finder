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
LOG_FILE = os.path.join(APP_ROOT, 'application.log')

def clean_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    # Reset logger configuration
    logger._log_initialized = False
    # Reinitialize logger with test settings
    logger.configure_logging(level='DEBUG', log_to_console=False)

def read_log():
    # Ensure the log file exists and has content
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def test_log_info_and_warning_and_error():
    clean_log()
    logger.log_info('info test')
    logger.log_warning('warn test')
    logger.log_error('error test')
    # Ensure logs are written to disk
    logger._write_log('DEBUG', 'flush')
    contents = read_log()
    assert '[INFO] test_logger.py:test_log_info_and_warning_and_error' in contents
    assert 'info test' in contents
    assert '[WARNING] test_logger.py:test_log_info_and_warning_and_error' in contents
    assert 'warn test' in contents
    assert '[ERROR] test_logger.py:test_log_info_and_warning_and_error' in contents
    assert 'error test' in contents

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
