import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import sys
from pathlib import Path

# Aggiungi la cartella principale al path per gli import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

APP_ROOT = Path(__file__).parent.parent
LOG_FILE = os.path.join(APP_ROOT, 'traceback.log')
LOG_LEVELS = ["ALL", "DEBUG","INFO", "WARNING", "ERROR"]

class LogViewer(tk.Toplevel):
    """
    A dialog to view the application log file with filtering by log level.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Log Viewer")
        self.geometry("800x600")
        
        # Make the window modal
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
        self.load_log()
    
    def _setup_ui(self):
        # Frame principale
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame per i controlli
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Etichetta e menu a tendina per il livello di log
        ttk.Label(control_frame, text="Log Level:").pack(side=tk.LEFT, padx=(0, 5))
        self.log_level = tk.StringVar(value="ALL")
        log_menu = ttk.OptionMenu(control_frame, self.log_level, "ALL", *LOG_LEVELS, command=self._on_level_changed)
        log_menu.pack(side=tk.LEFT, padx=(0, 10))
        
        # Pulsante di aggiornamento
        refresh_btn = ttk.Button(control_frame, text="Refresh", command=self.load_log)
        refresh_btn.pack(side=tk.LEFT)
        
        # Area di testo per i log
        self.text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Pulsante di chiusura
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        close_btn = ttk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT)
    
    def load_log(self, event=None):
        """Carica i log dal file."""
        try:
            if not os.path.exists(LOG_FILE):
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, f"Log file not found: {LOG_FILE}")
                return
                
            with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            self.display_lines(lines)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load log file: {str(e)}")
    
    def display_lines(self, lines):
        """Visualizza le righe di log nell'area di testo con formattazione."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        level = self.log_level.get()
        
        for line in lines:
            if level == "ALL" or f"[{level}]" in line:
                # Applica colori diversi in base al livello di log
                if "[ERROR]" in line:
                    self.text_area.tag_config("error", foreground="red")
                    self.text_area.insert(tk.END, line, "error")
                elif "[WARNING]" in line:
                    self.text_area.tag_config("warning", foreground="orange")
                    self.text_area.insert(tk.END, line, "warning")
                elif "[INFO]" in line:
                    self.text_area.tag_config("info", foreground="blue")
                    self.text_area.insert(tk.END, line, "info")
                else:
                    self.text_area.insert(tk.END, line)
        
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)
    
    def _on_level_changed(self, *args):
        """Gestisce il cambio del livello di log."""
        if hasattr(self, 'text_area'):
            self.load_log()

def show_log_viewer(parent):
    """Funzione di utilità per mostrare il visualizzatore di log."""
    try:
        LogViewer(parent)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open log viewer: {str(e)}")

def load_log_lines():
    """Carica le righe del file di log."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
        return f.readlines()

def filter_lines(lines, level):
    """Filtra le righe in base al livello di log."""
    if level == "ALL":
        return lines
    return [line for line in lines if f"[{level}]" in line]
