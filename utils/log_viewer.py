import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, font as tkfont
import os
import sys
import re
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import platform

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

APP_ROOT = Path(__file__).parent.parent
LOG_FILE = os.path.join(APP_ROOT, 'logs/application.log')
LOG_LEVELS = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR"]
LOG_COLORS = {
    "DEBUG": "#666666",
    "INFO": "#007bff",
    "WARNING": "#ffc107",
    "ERROR": "#dc3545",
    "TIMESTAMP": "#6c757d",
    "HIGHLIGHT": "#ffff00"
}

class AutoScrollbar(ttk.Scrollbar):
    """A scrollbar that hides itself if it's not needed."""
    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            self.pack_forget()
        else:
            self.pack(fill=tk.Y, side=tk.RIGHT, expand=False)
        ttk.Scrollbar.set(self, low, high)

    def grid(self, **kw):
        raise tk.TclError("Cannot use grid with AutoScrollbar")

    def place(self, **kw):
        raise tk.TclError("Cannot use place with AutoScrollbar")

class LogViewer(tk.Toplevel):
    """
    An enhanced log viewer with filtering, search, and auto-refresh capabilities.
    """
    def __init__(self, parent, log_file: str = None):
        super().__init__(parent)
        self.title("Log Viewer")
        self.geometry("1000x700")
        self.minsize(800, 500)
        
        self.log_file = Path(log_file) if log_file else Path(LOG_FILE)
        self.last_load_time = 0
        self.auto_refresh = tk.BooleanVar(value=False)
        self.search_text = tk.StringVar()
        self.highlight_tags = []
        
        # Configure window style
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        
        # Make the window modal
        self.transient(parent)
        self.grab_set()
        
        # Bind Ctrl+F for search
        self.bind('<Control-f>', lambda e: self.show_search())
        self.bind('<Control-F>', lambda e: self.show_search())
        
        self._setup_ui()
        self.load_log()
    
    def _setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=5)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Log level filter
        ttk.Label(control_frame, text="Log Level:").pack(side=tk.LEFT, padx=(0, 5))
        self.log_level = tk.StringVar(value="ALL")
        log_menu = ttk.OptionMenu(control_frame, self.log_level, "ALL", *LOG_LEVELS, command=self._on_level_changed)
        log_menu.pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-refresh toggle
        self.auto_refresh_btn = ttk.Checkbutton(
            control_frame, 
            text="Auto-refresh (5s)", 
            variable=self.auto_refresh,
            command=self.toggle_auto_refresh
        )
        self.auto_refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # Search entry
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=(10, 0))
        search_entry = ttk.Entry(control_frame, textvariable=self.search_text, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<Return>', lambda e: self.highlight_search())
        
        # Search buttons
        search_btn = ttk.Button(control_frame, text="Find", command=self.highlight_search)
        search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_search_btn = ttk.Button(control_frame, text="Clear", command=self.clear_search)
        clear_search_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Right-aligned buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        refresh_btn = ttk.Button(btn_frame, text="🔄 Refresh", command=self.load_log)
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        open_btn = ttk.Button(btn_frame, text="📂 Open Folder", command=self.open_log_folder)
        open_btn.pack(side=tk.LEFT, padx=2)
        
        close_btn = ttk.Button(btn_frame, text="❌ Close", command=self.destroy)
        close_btn.pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=(5, 2, 5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Text area with custom scrollbars
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        v_scrollbar = AutoScrollbar(text_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scrollbar = AutoScrollbar(text_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Text widget
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=('Consolas', 10),
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            bg='#f8f9fa',
            insertbackground='black',
            selectbackground='#0078d7',
            selectforeground='white',
            padx=5,
            pady=5
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.text_area.yview)
        h_scrollbar.config(command=self.text_area.xview)
        
        # Configure tags for log levels
        for level, color in LOG_COLORS.items():
            self.text_area.tag_configure(level, foreground=color)
        
        # Configure highlight tag
        self.text_area.tag_configure('highlight', background=LOG_COLORS['HIGHLIGHT'])
        
        # Configure timestamp tag
        self.text_area.tag_configure('timestamp', foreground=LOG_COLORS['TIMESTAMP'])
        
        # Add right-click context menu
        self.setup_context_menu()
        
        # Start auto-refresh if enabled
        self.auto_refresh_job = None
        if self.auto_refresh.get():
            self.start_auto_refresh()
    
    def load_log(self, event=None):
        """Load logs from file with error handling and performance optimizations."""
        try:
            if not self.log_file.exists():
                self.update_status(f"Log file not found: {self.log_file}", 'error')
                return
                
            # Check if file has been modified since last load
            mtime = self.log_file.stat().st_mtime
            if mtime <= self.last_load_time and not getattr(self, '_force_refresh', False):
                return
                
            self.last_load_time = mtime
            self._force_refresh = False
            
            with open(self.log_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            self.display_lines(lines)
            self.update_status(f"Loaded {len(lines)} lines from {self.log_file.name}")
            
        except PermissionError:
            self.update_status(f"Permission denied: {self.log_file}", 'error')
        except Exception as e:
            self.update_status(f"Error loading log file: {str(e)}", 'error')
    
    def display_lines(self, lines: List[str]):
        """Display log lines with syntax highlighting and filtering."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        level = self.log_level.get()
        search_text = self.search_text.get().lower()
        
        # Configure tags for log levels
        for level_name, color in LOG_COLORS.items():
            if level_name not in ['HIGHLIGHT', 'TIMESTAMP']:
                self.text_area.tag_configure(level_name, foreground=color)
        
        line_count = 0
        for line in lines:
            line = line.rstrip('\n')
            
            # Skip empty lines
            if not line.strip():
                continue
                
            # Apply level filter
            if level != "ALL" and f"[{level}]" not in line:
                continue
                
            # Apply search filter
            if search_text and search_text not in line.lower():
                continue
                
            # Parse log line
            timestamp = ''
            log_level = 'INFO'  # Default log level
            
            # Extract timestamp if present
            timestamp_match = re.match(r'^(\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?\])', line)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                line = line[len(timestamp):].lstrip()
            
            # Extract log level if present
            level_match = re.match(r'^\[(DEBUG|INFO|WARNING|ERROR)\]', line)
            if level_match:
                log_level = level_match.group(1)
            
            # Insert timestamp if present
            if timestamp:
                self.text_area.insert(tk.END, timestamp + ' ', 'timestamp')
            
            # Insert the rest of the line with appropriate formatting
            self.text_area.insert(tk.END, line + '\n', log_level)
            line_count += 1
        
        # Apply search highlighting if needed
        if search_text:
            self.highlight_search()
        
        self.text_area.config(state=tk.DISABLED)
        
        # Auto-scroll to end if not searching
        if not search_text:
            self.text_area.see(tk.END)
        
        return line_count
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh of log file."""
        if self.auto_refresh.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        if not self.auto_refresh_job:
            self.auto_refresh_interval = 5000  # 5 seconds
            self._auto_refresh()
    
    def stop_auto_refresh(self):
        """Stop auto-refresh timer."""
        if self.auto_refresh_job:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None
    
    def _auto_refresh(self):
        """Internal method to handle auto-refresh."""
        if self.auto_refresh.get():
            self.load_log()
            self.auto_refresh_job = self.after(self.auto_refresh_interval, self._auto_refresh)
    
    def show_search(self):
        """Show search dialog."""
        self.focus_set()
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
    
    def highlight_search(self, event=None):
        """Highlight search results in the log viewer."""
        search_text = self.search_text.get().strip()
        
        # Remove previous highlights
        for tag in self.highlight_tags:
            self.text_area.tag_remove(tag, '1.0', tk.END)
        self.highlight_tags = []
        
        if not search_text:
            return
        
        # Configure highlight tag
        tag_name = f'highlight_{len(self.highlight_tags)}'
        self.text_area.tag_configure(tag_name, background=LOG_COLORS['HIGHLIGHT'])
        
        # Search and highlight
        start_pos = '1.0'
        count = 0
        self.text_area.mark_set('search_start', start_pos)
        self.text_area.mark_set(tk.INSERT, 'search_start')
        self.text_area.see('insert')
        
        while True:
            pos = self.text_area.search(
                search_text, 'search_start',
                stopindex=tk.END, 
                nocase=True
            )
            
            if not pos:
                break
                
            # Calculate end position
            end_pos = f"{pos}+{len(search_text)}c"
            
            # Add the tag
            self.text_area.tag_add(tag_name, pos, end_pos)
            self.highlight_tags.append(tag_name)
            
            # Move to the next position
            self.text_area.mark_set('search_start', end_pos)
            count += 1
        
        if count > 0:
            self.text_area.see(pos)
            self.update_status(f"Found {count} occurrences of '{search_text}'", 'info')
        else:
            self.update_status(f"Text '{search_text}' not found", 'warning')
    
    def clear_search(self):
        """Clear search highlights and reset search."""
        self.search_text.set('')
        self.highlight_search()
        self.text_area.tag_remove(tk.SEL, '1.0', tk.END)
    
    def open_log_folder(self):
        """Open the folder containing the log file."""
        try:
            if platform.system() == 'Windows':
                os.startfile(self.log_file.parent)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{self.log_file.parent}"')
            else:  # Linux and others
                os.system(f'xdg-open "{self.log_file.parent}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")
    
    def setup_context_menu(self):
        """Set up the right-click context menu."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selection)
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear Log", command=self.clear_log)
        
        # Bind right-click
        self.text_area.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show the context menu."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_selection(self):
        """Copy selected text to clipboard."""
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tk.TclError:
            pass  # No selection
    
    def select_all(self):
        """Select all text in the log viewer."""
        self.text_area.tag_add(tk.SEL, '1.0', tk.END)
        self.text_area.mark_set(tk.INSERT, '1.0')
        self.text_area.see(tk.INSERT)
        return 'break'  # Prevent default behavior
    
    def clear_log(self):
        """Clear the log file."""
        if messagebox.askyesno("Confirm", "Clear the entire log file? This cannot be undone."):
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                self.load_log()
                self.update_status("Log file cleared", 'info')
            except Exception as e:
                messagebox.showerror("Error", f"Could not clear log file: {str(e)}")
    
    def update_status(self, message: str, level: str = 'info'):
        """Update the status bar with a message."""
        self.status_var.set(message)
        
        # Change status bar color based on level
        if level == 'error':
            self.status_bar.config(background='#f8d7da', foreground='#721c24')
        elif level == 'warning':
            self.status_bar.config(background='#fff3cd', foreground='#856404')
        elif level == 'success':
            self.status_bar.config(background='#d4edda', foreground='#155724')
        else:
            self.status_bar.config(background='#e2e3e5', foreground='#383d41')
    
    def _on_level_changed(self, *args):
        """Handle log level filter change."""
        if hasattr(self, 'text_area'):
            self.load_log()
    
    def destroy(self):
        """Clean up resources before destroying the window."""
        self.stop_auto_refresh()
        super().destroy()

def show_log_viewer(parent, log_file: str = None):
    """Show the log viewer window.
    
    Args:
        parent: Parent window (Tk or Toplevel)
        log_file: Optional path to a log file to view
    """
    try:
        LogViewer(parent, log_file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open log viewer: {str(e)}")

def load_log_lines(log_file: str = None) -> List[str]:
    """Load lines from a log file.
    
    Args:
        log_file: Path to the log file (default: main log file)
        
    Returns:
        List of log lines
    """
    file_path = Path(log_file) if log_file else Path(LOG_FILE)
    if not file_path.exists():
        return []
        
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.readlines()
    except Exception:
        return []

def filter_lines(lines: List[str], level: str = "ALL") -> List[str]:
    """Filter log lines by log level.
    
    Args:
        lines: List of log lines
        level: Log level to filter by (DEBUG, INFO, WARNING, ERROR, ALL)
        
    Returns:
        Filtered list of log lines
    """
    if not lines or level == "ALL":
        return lines
    return [line for line in lines if f"[{level}]" in line]
