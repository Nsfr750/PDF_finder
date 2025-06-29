"""
Enhanced Traceback Logger and Viewer

This module provides enhanced error logging and visualization capabilities.
It captures uncaught exceptions and provides a user-friendly interface
for viewing and managing error logs.
"""

import os
import sys
import traceback as _std_traceback
import datetime
import json
import webbrowser
import platform
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
import tkinter as tk
from tkinter import (
    Toplevel, scrolledtext, ttk, messagebox, 
    Menu, filedialog, font as tkfont, StringVar, BooleanVar
)

# Constants
APP_ROOT = Path(__file__).parent.parent
LOG_FILE = os.path.join(APP_ROOT, 'traceback.log')
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3

# Log level colors
LOG_LEVELS = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR"]
LOG_COLORS = {
    "DEBUG": "#666666",
    "INFO": "#007bff",
    "WARNING": "#ffc107",
    "ERROR": "#dc3545",
    "CRITICAL": "#dc3545",
    "TIMESTAMP": "#6c757d",
    "HIGHLIGHT": "#ffff00"
}

class AutoScrollbar(ttk.Scrollbar):
    """A scrollbar that hides itself if it's not needed."""
    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            self.pack_forget()
        else:
            self.pack(fill=tk.Y, side="right", expand=False)
        super().set(low, high)

    def grid(self, **kw):
        raise tk.TclError("Cannot use grid with AutoScrollbar")

    def place(self, **kw):
        raise tk.TclError("Cannot use place with AutoScrollbar")

def setup_logging():
    """Set up logging configuration and ensure log directory exists."""
    log_dir = Path(LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Rotate log file if it's too large
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        rotate_logs()

def rotate_logs():
    """Rotate log files to prevent them from growing too large."""
    try:
        # Remove the oldest backup if it exists
        oldest_backup = f"{LOG_FILE}.{BACKUP_COUNT}"
        if os.path.exists(oldest_backup):
            os.remove(oldest_backup)
        
        # Shift existing backups
        for i in range(BACKUP_COUNT - 1, 0, -1):
            src = f"{LOG_FILE}.{i}" if i == 1 else f"{LOG_FILE}.{i-1}"
            dst = f"{LOG_FILE}.{i}"
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
        
        # Rotate current log
        if os.path.exists(LOG_FILE):
            os.rename(LOG_FILE, f"{LOG_FILE}.1")
    except Exception as e:
        print(f"Error rotating log files: {e}", file=sys.stderr)

def log_exception(exc_type, exc_value, exc_tb):
    """
    Logs uncaught exceptions and their tracebacks to the log file.
    
    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_tb: Exception traceback
    """
    try:
        # Ensure log directory exists
        log_dir = Path(LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Format the timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the exception
        exc_lines = []
        _std_traceback.print_exception(exc_type, exc_value, exc_tb, file=sys.stderr)
        
        # Get the traceback as a string
        exc_lines = _std_traceback.format_exception(exc_type, exc_value, exc_tb)
        
        # Write to log file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n[ERROR] [{timestamp}] Uncaught exception:\n")
            f.writelines(exc_lines)
            f.write("\n" + "-" * 80 + "\n")
    except Exception as e:
        print(f"Error logging exception: {e}", file=sys.stderr)

def log_message(level: str, message: str, **kwargs):
    """
    Log a message with the specified log level.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Message to log
        **kwargs: Additional metadata to include in the log
    """
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message,
            **kwargs
        }
        
        # Convert to JSON for structured logging
        log_line = json.dumps(log_entry) + '\n'
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except Exception as e:
        print(f"Error writing to log: {e}", file=sys.stderr)

def get_traceback_module():
    """
    Returns the standard library traceback module.
    
    Returns:
        The standard library traceback module
    """
    return _std_traceback


class TracebackViewer(Toplevel):
    """Enhanced traceback viewer with filtering and search capabilities."""
    
    def __init__(self, parent, log_file: str = None):
        """Initialize the traceback viewer.
        
        Args:
            parent: Parent window
            log_file: Optional path to a log file to view
        """
        super().__init__(parent)
        self.title("Error Log Viewer")
        self.geometry("1000x700")
        self.minsize(800, 500)
        
        self.log_file = Path(log_file) if log_file else Path(LOG_FILE)
        self.search_text = StringVar()
        self.log_level = StringVar(value="ALL")
        self.auto_refresh = BooleanVar(value=False)
        self.auto_refresh_job = None
        self.highlight_tags = []
        
        # Configure window style
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        
        # Make the window modal
        self.transient(parent)
        self.grab_set()
        
        # Initialize UI
        self._setup_ui()
        
        # Load initial logs
        self.refresh_logs()
        
        # Start auto-refresh if enabled
        if self.auto_refresh.get():
            self.start_auto_refresh()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=5)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Log level filter
        ttk.Label(control_frame, text="Log Level:").pack(side=tk.LEFT, padx=(0, 5))
        log_menu = ttk.OptionMenu(
            control_frame, self.log_level, "ALL", *LOG_LEVELS, 
            command=lambda _: self.refresh_logs()
        )
        log_menu.pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-refresh toggle
        ttk.Checkbutton(
            control_frame, 
            text="Auto-refresh (5s)", 
            variable=self.auto_refresh,
            command=self.toggle_auto_refresh
        ).pack(side=tk.LEFT, padx=10)
        
        # Search entry
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=(10, 0))
        search_entry = ttk.Entry(control_frame, textvariable=self.search_text, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<Return>', lambda e: self.highlight_search())
        
        # Search buttons
        ttk.Button(control_frame, text="Find", command=self.highlight_search).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Clear", command=self.clear_search).pack(
            side=tk.LEFT, padx=(0, 10))
        
        # Right-aligned buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_logs).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📂 Open Folder", command=self.open_log_folder).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📋 Copy", command=self.copy_selected).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Clear", command=self.clear_logs_dialog).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="❌ Close", command=self.destroy).pack(
            side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = StringVar()
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
        
        # Add right-click context menu
        self.setup_context_menu()
        
        # Bind keyboard shortcuts
        self.bind('<Control-f>', lambda e: search_entry.focus())
        self.bind('<Control-F>', lambda e: search_entry.focus())
        self.bind('<F5>', lambda e: self.refresh_logs())
        
        # Set focus to search field by default
        search_entry.focus_set()
    
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
        if hasattr(self, 'auto_refresh_job') and self.auto_refresh_job:
            try:
                self.after_cancel(self.auto_refresh_job)
            except (AttributeError, ValueError):
                pass  # Job doesn't exist or is already canceled
            self.auto_refresh_job = None
    
    def _auto_refresh(self):
        """Internal method to handle auto-refresh."""
        if self.auto_refresh.get():
            self.refresh_logs()
            self.auto_refresh_job = self.after(
                self.auto_refresh_interval, 
                self._auto_refresh
            )
    
    def refresh_logs(self, event=None):
        """Refresh the log display."""
        try:
            if not self.log_file.exists():
                self.update_status(f"Log file not found: {self.log_file}", 'error')
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, f"Log file not found: {self.log_file}")
                return
            
            with open(self.log_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            
            if not content:
                self.text_area.insert(tk.END, "No errors logged.")
                self.update_status("Log file is empty", 'info')
                return
            
            # Process each line
            line_count = 0
            for line in content.splitlines():
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Check log level filter
                level = self.log_level.get()
                if level != "ALL" and f'"level": "{level}"' not in line:
                    continue
                
                # Try to parse as JSON for structured logging
                try:
                    log_entry = json.loads(line)
                    timestamp = log_entry.get('timestamp', '')
                    level = log_entry.get('level', 'INFO')
                    message = log_entry.get('message', '')
                    
                    # Insert timestamp
                    if timestamp:
                        self.text_area.insert(tk.END, f"[{timestamp}] ", 'TIMESTAMP')
                    
                    # Insert log level
                    self.text_area.insert(tk.END, f"[{level}] ", level)
                    
                    # Insert message
                    self.text_area.insert(tk.END, message + '\n')
                    
                    # Add any additional fields
                    for key, value in log_entry.items():
                        if key not in ['timestamp', 'level', 'message']:
                            self.text_area.insert(
                                tk.END, 
                                f"  {key}: {json.dumps(value)}\n",
                                'DEBUG'
                            )
                    
                    line_count += 1
                    
                except json.JSONDecodeError:
                    # Fall back to plain text display
                    self.text_area.insert(tk.END, line + '\n')
                    line_count += 1
            
            # Apply search highlighting if there's search text
            search_text = self.search_text.get().strip()
            if search_text:
                self.highlight_search()
            
            # Auto-scroll to end if not searching
            if not search_text:
                self.text_area.see(tk.END)
            
            self.update_status(f"Loaded {line_count} log entries")
            
        except Exception as e:
            self.update_status(f"Error loading log file: {str(e)}", 'error')
            self.text_area.insert(tk.END, f"Error loading log file: {str(e)}")
        finally:
            self.text_area.config(state=tk.DISABLED)
    
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
        self.text_area.mark_set(tkfont.INSERT, 'search_start')
        self.text_area.see('insert')
        
        while True:
            pos = self.text_area.search(
                search_text, 'search_start',
                stopindex=tkfont.END, 
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
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected)
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear Log", command=self.clear_logs_dialog)
        
        # Bind right-click
        self.text_area.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show the context menu."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_selected(self):
        """Copy selected text to clipboard."""
        try:
            selected = self.text_area.get(tkfont.SEL_FIRST, tkfont.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tkfont.TclError:
            pass  # No selection
    
    def select_all(self):
        """Select all text in the log viewer."""
        self.text_area.tag_add(tkfont.SEL, '1.0', tkfont.END)
        self.text_area.mark_set(tkfont.INSERT, '1.0')
        self.text_area.see(tkfont.INSERT)
        return 'break'  # Prevent default behavior
    
    def clear_logs_dialog(self):
        """Show confirmation dialog before clearing logs."""
        if messagebox.askyesno("Confirm", "Clear the entire log file? This cannot be undone."):
            self.clear_logs()
    
    def clear_logs(self):
        """Clear the log file."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('')
            self.refresh_logs()
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
    
    def destroy(self):
        """Clean up resources before destroying the window."""
        self.stop_auto_refresh()
        super().destroy()

def show_traceback_window(parent, log_file: str = None):
    """Show the traceback viewer window.
    
    Args:
        parent: Parent window (Tk or Toplevel)
        log_file: Optional path to a log file to view
        
    Returns:
        The TracebackViewer instance or None if an error occurred
    """
    try:
        # Ensure logging is set up
        setup_logging()
        
        # Create and return the viewer window
        return TracebackViewer(parent, log_file)
    except Exception as e:
        messagebox.showerror(
            "Error", 
            f"Failed to open traceback viewer: {str(e)}\n"
            f"{_std_traceback.format_exc()}"
        )
        return None
