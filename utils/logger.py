import datetime
import inspect
import os
import sys
import threading
from pathlib import Path
from typing import Optional, Dict, Any

# Ottieni il percorso della directory principale dell'applicazione
APP_ROOT = Path(__file__).parent.parent
LOG_FILE = os.path.join(APP_ROOT, 'application.log')
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Configurazione di default
_log_config = {
    'enabled': True,
    'level': LOG_LEVEL,
    'max_size_mb': 10,  # Dimensione massima del file di log in MB
    'backup_count': 5,  # Numero di file di backup da mantenere
    'log_to_console': True
}

_log_lock = threading.Lock()
_log_initialized = False

def configure_logging(enabled: bool = True, level: str = "INFO", 
                     log_file: Optional[str] = None,
                     max_size_mb: int = 10,
                     backup_count: int = 5,
                     log_to_console: bool = True) -> None:
    """Configura il sistema di logging.
    
    Args:
        enabled: Se True, abilita il logging
        level: Livello di log (DEBUG, INFO, WARNING, ERROR)
        log_file: Percorso del file di log
        max_size_mb: Dimensione massima del file di log in MB
        backup_count: Numero di file di backup da mantenere
        log_to_console: Se True, scrive anche sulla console
    """
    global _log_config, LOG_FILE
    
    _log_config.update({
        'enabled': enabled,
        'level': level.upper(),
        'max_size_mb': max_size_mb,
        'backup_count': backup_count,
        'log_to_console': log_to_console
    })
    
    if log_file:
        LOG_FILE = log_file
    
    # Crea la directory se non esiste
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    global _log_initialized
    _log_initialized = True

def _should_log(level: str) -> bool:
    """Determina se un messaggio con il dato livello dovrebbe essere registrato."""
    if not _log_config['enabled']:
        return False
        
    try:
        return LOG_LEVELS.index(level) >= LOG_LEVELS.index(_log_config['level'])
    except ValueError:
        return False

def _rotate_logs() -> None:
    """Esegue la rotazione dei file di log."""
    if not os.path.exists(LOG_FILE):
        return
        
    max_size = _log_config['max_size_mb'] * 1024 * 1024  # Converti in bytes
    
    if os.path.getsize(LOG_FILE) < max_size:
        return
    
    # Elimina il file di backup più vecchio se necessario
    backup_count = _log_config['backup_count']
    oldest_backup = f"{LOG_FILE}.{backup_count}"
    if os.path.exists(oldest_backup):
        try:
            os.remove(oldest_backup)
        except OSError:
            pass
    
    # Rinomina i file di log esistenti
    for i in range(backup_count - 1, 0, -1):
        src = f"{LOG_FILE}.{i}" if i > 0 else LOG_FILE
        dst = f"{LOG_FILE}.{i + 1}"
        
        if os.path.exists(src):
            try:
                os.rename(src, dst)
            except OSError:
                pass
    
    # Svuota il file di log principale
    try:
        with open(LOG_FILE, 'w'):
            pass
    except OSError:
        pass

def _get_caller_info() -> Dict[str, Any]:
    """Ottiene le informazioni sul chiamante della funzione di log."""
    try:
        frame = inspect.currentframe()
        # Salta i frame interni al modulo di logging
        while frame:
            if frame.f_code.co_filename != __file__:
                break
            frame = frame.f_back
        
        if frame:
            return {
                'filename': os.path.basename(frame.f_code.co_filename),
                'function': frame.f_code.co_name,
                'lineno': frame.f_lineno
            }
    except Exception:
        pass
    return {'filename': 'unknown', 'function': 'unknown', 'lineno': 0}

def _format_message(level: str, message: str) -> str:
    """Formatta il messaggio di log con timestamp e informazioni aggiuntive."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    caller = _get_caller_info()
    
    return (
        f"[{timestamp}] [{level}] "
        f"{caller['filename']}:{caller['function']}:{caller['lineno']} - {message}"
    )

def _write_log(level: str, message: str) -> None:
    """Scrive un messaggio di log nel file e/o sulla console."""
    if not _log_initialized:
        configure_logging()
        
    if not _should_log(level):
        return
    
    try:
        formatted_msg = _format_message(level, message)
        
        # Scrive sulla console se richiesto
        if _log_config['log_to_console']:
            print(formatted_msg, file=sys.stderr if level == "ERROR" else sys.stdout)
        
        with _log_lock:
            # Esegue la rotazione dei log se necessario
            _rotate_logs()
            
            # Scrive sul file
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{formatted_msg}\n")
                
    except Exception as e:
        print(f"[ERROR] Failed to write to log: {str(e)}", file=sys.stderr)

def log_debug(message: str) -> None:
    """Scrive un messaggio di debug."""
    _write_log("DEBUG", message)

def log_info(message: str) -> None:
    """Scrive un messaggio informativo."""
    _write_log("INFO", message)

def log_warning(message: str) -> None:
    """Scrive un messaggio di avviso."""
    _write_log("WARNING", message)

def log_error(message: str) -> None:
    """Scrive un messaggio di errore."""
    _write_log("ERROR", message)

def log_exception(exc_type, exc_value, exc_tb, context: str = None) -> None:
    """Registra un'eccezione nel file di log.
    
    Args:
        exc_type: Tipo dell'eccezione
        exc_value: Valore dell'eccezione
        exc_tb: Traceback
        context: Messaggio contestuale opzionale
    """
    if not _log_initialized:
        configure_logging()
        
    if not _log_config['enabled']:
        return
        
    try:
        import traceback
        from io import StringIO
        
        # Crea un buffer per il traceback
        tb_buffer = StringIO()
        traceback.print_exception(exc_type, exc_value, exc_tb, file=tb_buffer)
        tb_str = tb_buffer.getvalue().strip()
        
        # Prepara il messaggio di contesto se fornito
        context_msg = f"\nContext: {context}" if context else ""
        
        # Formatta il messaggio completo
        message = f"Uncaught exception:{context_msg}\n{tb_str}"
        
        # Usa _write_log per la formattazione coerente
        _write_log("ERROR", message)
        
    except Exception as e:
        print(f"[ERROR] Failed to log exception: {str(e)}", file=sys.stderr)

def setup_global_exception_logging() -> None:
    """Configura il logging delle eccezioni non gestite."""
    if not _log_initialized:
        configure_logging()
    sys.excepthook = log_exception
    
    # Configura anche il logging per i thread
    import threading
    threading.excepthook = lambda args: log_exception(
        args.exc_type, 
        args.exc_value, 
        args.exc_traceback,
        f"Unhandled exception in thread {args.thread.name if hasattr(args, 'thread') else 'unknown'}"
    )

def get_log_file_path() -> str:
    """Restituisce il percorso completo del file di log."""
    if not _log_initialized:
        configure_logging()
    return os.path.abspath(LOG_FILE)

def clear_log() -> bool:
    """Cancella il contenuto del file di log."""
    if not _log_initialized:
        configure_logging()
        
    try:
        with _log_lock:
            with open(LOG_FILE, 'w'):
                pass
        return True
    except Exception as e:
        log_error(f"Failed to clear log file: {str(e)}")
        return False
