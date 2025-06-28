import os
import re
import sys
import datetime
import pytest
import traceback
from tkinter import messagebox
from pathlib import Path

# Aggiungi la cartella principale al path per gli import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from struttura import logger
except ImportError:
    # Se non si riesce a importare da struttura, prova a importare direttamente
    try:
        from . import logger
    except ImportError:
        import logger

APP_ROOT = Path(__file__).parent.parent
LOG_FILE = os.path.join(APP_ROOT, 'traceback.log')

def clean_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

def read_log():
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def test_log_info_and_warning_and_error():
    clean_log()
    logger.log_info('info test')
    logger.log_warning('warn test')
    logger.log_error('error test')
    contents = read_log()
    assert '[INFO] info test' in contents
    assert '[WARNING] warn test' in contents
    assert '[ERROR] error test' in contents

def test_log_exception():
    clean_log()
    try:
        raise ValueError('test exception')
    except Exception as e:
        logger.log_exception(type(e), e, e.__traceback__)
    contents = read_log()
    assert 'Uncaught exception:' in contents
    assert 'ValueError: test exception' in contents

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
