"""
Traceback Logger 
"""

import os
import sys
import traceback as _std_traceback
import datetime
from tkinter import Toplevel, scrolledtext, ttk, messagebox
from pathlib import Path

APP_ROOT = Path(__file__).parent.parent
LOG_FILE = os.path.join(APP_ROOT, 'traceback.log')

def log_exception(exc_type, exc_value, exc_tb):
    """
    Logs uncaught exceptions and their tracebacks to Traceback.log.
    """
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Uncaught exception:\n")
        _std_traceback.print_exception(exc_type, exc_value, exc_tb, file=f)

def get_traceback_module():
    """
    Returns the standard library traceback module (for use in main.py if needed).
    """
    return _std_traceback

# To enable global exception logging, add this to main.py:
# import traceback as tb_logger
# sys.excepthook = tb_logger.log_exception
# traceback = tb_logger.get_traceback_module()  # if you need the standard library traceback


def show_traceback_window(parent):
    """
    Mostra una finestra con il contenuto del file di log delle tracce di errore.
    
    Args:
        parent: La finestra genitrice (Tk o Toplevel)
    """
    try:
        # Crea una nuova finestra
        window = Toplevel(parent)
        window.title("Visualizzatore Traceback")
        window.geometry("800x600")
        
        # Frame principale
        main_frame = ttk.Frame(window)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Etichetta del titolo
        title_label = ttk.Label(
            main_frame, 
            text="Ultimi errori registrati:",
            font=('Helvetica', 10, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Area di testo per i log
        text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap="word",
            width=100,
            height=30,
            font=('Consolas', 9)
        )
        text_area.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pulsante per cancellare i log
        def clear_logs():
            try:
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, 'w', encoding='utf-8') as f:
                        f.write('')
                    text_area.delete(1.0, "end")
                    messagebox.showinfo("Successo", "Log degli errori cancellato con successo.")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile cancellare i log: {str(e)}")
        
        # Pulsante per aggiornare i log
        def refresh_logs():
            try:
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, 'r', encoding='utf-8') as f:
                        content = f.read()
                    text_area.delete(1.0, "end")
                    text_area.insert("end", content if content else "Nessun errore registrato.")
                    text_area.see("end")
                else:
                    text_area.delete(1.0, "end")
                    text_area.insert("end", "Nessun file di log trovato.")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile leggere il file di log: {str(e)}")
        
        # Frame per i pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(5, 0))
        
        # Pulsanti
        refresh_btn = ttk.Button(button_frame, text="Aggiorna", command=refresh_logs)
        refresh_btn.pack(side="left", padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Cancella Log", command=clear_logs)
        clear_btn.pack(side="left", padx=5)
        
        close_btn = ttk.Button(button_frame, text="Chiudi", command=window.destroy)
        close_btn.pack(side="right", padx=5)
        
        # Carica i log all'apertura
        refresh_logs()
        
        # Rendi la finestra modale
        window.transient(parent)
        window.grab_set()
        
        return window
        
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile aprire il visualizzatore di traceback: {str(e)}")
        return None
