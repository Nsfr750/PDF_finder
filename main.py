import os
import hashlib
import tempfile
import json
import time
from tkinter import messagebox
from app_struct.drag_drop import DragDropManager
from app_struct.gest_scan import ScanManager
from app_struct.delete import FileDeleter
import math
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event
import logging
from typing import List, Dict, Optional, Set

# Configure PyPDF2 logger to suppress warnings
logging.getLogger('PyPDF2').setLevel(logging.ERROR)

# Custom logger for our application
logger = logging.getLogger('PDFDuplicateFinder')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
import traceback
import concurrent.futures
import shutil
from pathlib import Path
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError
from pdf2image import convert_from_path
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox, ttk, Button, Tk, Label,  simpledialog, font as tkfont, colorchooser, Toplevel, Frame, IntVar, Scale, HORIZONTAL
from tkinterdnd2 import TkinterDnD, DND_FILES, DND_ALL
import imagehash
from app_struct.help import HelpWindow
from app_struct.about import About
from app_struct.sponsor import Sponsor
from app_struct.theme import ThemeManager
from lang.translations import TRANSLATIONS, t
from app_struct.updates import check_for_updates
import threading
import time
import os
from datetime import datetime
import queue
import webbrowser
from PIL import ImageOps, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import win32ui
import win32gui
import win32con
import win32api
import pythoncom
from win32com.shell import shell, shellcon

# Try to import send2trash for safe file deletion
try:
    from send2trash import send2trash
except ImportError:
    send2trash = None
    print("Note: send2trash module not found. Using standard file deletion.")
    print("Install with: pip install send2trash")


class PDFDuplicateApp:
    def __init__(self, root):
        self.root = root
        
        # Initialize settings and config file
        self.settings = {}
        self.config_file = Path(os.path.join(os.path.expanduser('~'), '.pdf_duplicate_finder', 'settings.json'))
        
        # Initialize cache directory
        self.cache_dir = os.path.join(os.path.expanduser('~'), '.pdf_duplicate_finder')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load saved settings if they exist
        self.load_settings()
        
        # Add cache settings
        self.use_cache = tk.BooleanVar(value=True)
        self.low_priority = tk.BooleanVar(value=False)
        
        # Set window title with version
        self.root.title("PDF Duplicate Finder")
        self.root.geometry('1024x768+576+132')
        # Initialize color theme variables
        self.primary_color = "#007bff"
        self.secondary_color = "#0056b3"
        self.text_color = "#000000"
        self.bg_color = "#f8f9fa"
        
        # Set window icon if available
        try:
            self.root.iconbitmap('images/icon.ico')
        except Exception:
            pass
            
        # Enable drag and drop
        try:
            from ctypes import windll
            windll.shell32.SetCurrentProcessExplicitAppUserModelID("PDFDuplicateFinder")
        except Exception:
            pass  # Not on Windows or failed to set AppUserModelID
            
        # Initialize basic attributes
        self.is_searching = False
        
        # Initialize treeview visibility
        self.tree_visible = self.settings.get('tree_visible', True)
        
        # Initialize preview visibility
        self.preview_visible = self.settings.get('preview_visible', True)
        
        # Initialize Quick Compare mode (faster but less accurate)
        self.quick_compare = tk.BooleanVar(value=self.settings.get('quick_compare', False))
        
        # Initialize filter variables
        self.filters_active = tk.BooleanVar(value=False)
        self.filter_size_min = tk.StringVar()
        self.filter_size_max = tk.StringVar()
        self.filter_date_from = tk.StringVar()
        self.filter_date_to = tk.StringVar()
        self.filter_pages_min = tk.StringVar()
        self.filter_pages_max = tk.StringVar()
        self.duplicates = []
        self.all_pdf_files = []
        self.problematic_files = []  # Track files with issues
        self.last_scan_folder = ""
        self.current_preview_image = None
        self.scan_start_time = 0
        self.suppress_warnings = True  # Default to suppressing PyPDF2 warnings
        
        # Initialize sponsor attribute for the sponsor menu
        from app_struct.sponsor import Sponsor
        self.sponsor = Sponsor(root)
        
        # Initialize config file path
        self.config_dir = Path.home() / '.pdfduplicatefinder'
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / 'settings.json'
        
        # Load settings
        self.settings = self.load_settings()
        self.lang = self.settings.get('lang', 'en')
        
        # Initialize theme manager first since it's needed early
        self.theme_manager = ThemeManager(self.root)
        
        # Initialize processing parameters
        self.batch_size = 10  # Default batch size for processing files
        self.max_workers = min(4, (os.cpu_count() or 1))  # Default to 4 workers or number of CPUs, whichever is smaller
        
        # Initialize recent folders
        from app_struct.recents import RecentFolders
        self.recents = RecentFolders(self)
        self.recents.on_folder_selected = self.load_recent_folder
        
        # Initialize filters visibility state
        self.filters_visible = self.settings.get('filters_visible', True)  # Default to visible
        
        # Initialize Tkinter variables after root is set up
        self._initialize_tk_variables()
        
        # Apply theme before setting up UI
        self.theme_manager.apply_theme(self.settings.get('theme', 'light'))
        
        # Configure styles for custom buttons
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        style.configure('Danger.TButton', font=('Arial', 10, 'bold'), foreground='white', background='#dc3545')
        style.map('Danger.TButton', 
                 background=[('active', '#c82333'), ('disabled', '#f5c6cb')],
                 foreground=[('disabled', '#721c24')])
        
        # Initialize FileDeleter for handling file deletion
        self.file_deleter = FileDeleter(self)
        
        # Set up the UI without menu first
        self._setup_ui()
        
        # Set up drag and drop
        self._setup_drag_drop()
        
        # Initialize ScanManager for handling scan results
        self.scan_manager = ScanManager(self.root, self)
        
        # Create menu bar after everything else is initialized
        from app_struct.menu import MenuManager
        self.menu_manager = MenuManager(self.root, self)
        self.menu_manager.create_menu_bar()
    
    def _initialize_tk_variables(self):
        """Initialize Tkinter variables after root window is created."""
        # Theme and settings
        self.theme_var = tk.StringVar(self.root, value=self.settings.get('theme', 'light'))
        self.lang_var = tk.StringVar(self.root, value=self.lang)
        
        # Search and filter variables
        self.folder_path = tk.StringVar(self.root)
        self.search_text = tk.StringVar(self.root)
        
        # Progress variables
        self.progress_var = tk.IntVar(self.root, value=0)
        self.overall_progress_var = tk.IntVar(self.root, value=0)
        self.status_text = tk.StringVar(self.root, value="Ready")
        self.compare_mode = tk.StringVar(self.root, value='quick')  # 'quick' or 'full'
        self.preview_type = tk.StringVar(self.root, value='text')  # 'text' or 'image'
        
        # Status variables
        self.status_text = tk.StringVar(self.root)
        self.file_progress = tk.IntVar(self.root)
        self.overall_progress_value = tk.IntVar(self.root)
        
        # Warning suppression
        self.suppress_warnings = self.settings.get('suppress_warnings', False)
        self.suppress_warnings_var = tk.BooleanVar(self.root, value=self.suppress_warnings)
        
        # Filter variables with defaults
        self.filters_active = tk.BooleanVar(self.root, value=False)
        
        # Size filter (in KB)
        self.filter_size_min = tk.StringVar(self.root, value='')
        self.filter_size_max = tk.StringVar(self.root, value='')
        
        # Date filter (YYYY-MM-DD format)
        self.filter_date_from = tk.StringVar(self.root, value='')
        self.filter_date_to = tk.StringVar(self.root, value='')
        
        # Page count filter
        self.filter_pages_min = tk.StringVar(self.root, value='')
        self.filter_pages_max = tk.StringVar(self.root, value='')
        
        # Load saved filter settings
        self._load_filter_settings()
        
    def clear_cache_if_needed(self):
        """Clear the cache if the user is disabling it."""
        if not self.use_cache.get():
            # Clear the cache directory
            import shutil
            try:
                if os.path.exists(self.cache_dir):
                    shutil.rmtree(self.cache_dir)
                    os.makedirs(self.cache_dir, exist_ok=True)
                    self.show_status("Cache cleared", "info")
            except Exception as e:
                self.show_status(f"Error clearing cache: {str(e)}", "error")
    
    def toggle_filters(self):
        """Toggle the enabled/disabled state of filter controls."""
        state = 'normal' if self.filters_active.get() else 'disabled'
        
        # Toggle all filter entry widgets
        for widget in self.filter_frame.winfo_children():
            if widget.winfo_class() in ('TEntry', 'TButton'):
                widget.configure(state=state)
        
        # Save the filter state
        self.save_settings()
    
    def _load_filter_settings(self):
        """Load filter settings from the configuration file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    filters = settings.get('filters', {})
                    
                    # Load filter values
                    self.filter_size_min.set(filters.get('size_min', ''))
                    self.filter_size_max.set(filters.get('size_max', ''))
                    self.filter_date_from.set(filters.get('date_from', ''))
                    self.filter_date_to.set(filters.get('date_to', ''))
                    self.filter_pages_min.set(filters.get('pages_min', ''))
                    self.filter_pages_max.set(filters.get('pages_max', ''))
                    self.filters_active.set(filters.get('active', False))
        except Exception as e:
            print(f"Error loading filter settings: {e}")
            
    def _save_filter_settings(self):
        """Save current filter settings to the configuration file."""
        try:
            # Create the config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Load existing settings or create a new dict
            settings = {}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r') as f:
                        settings = json.load(f)
                except json.JSONDecodeError:
                    settings = {}
            
            # Update filter settings
            filters = {
                'size_min': self.filter_size_min.get(),
                'size_max': self.filter_size_max.get(),
                'date_from': self.filter_date_from.get(),
                'date_to': self.filter_date_to.get(),
                'pages_min': self.filter_pages_min.get(),
                'pages_max': self.filter_pages_max.get(),
                'active': self.filters_active.get()
            }
            
            settings['filters'] = filters
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
                
        except Exception as e:
            print(f"Error saving filter settings: {e}")
    
        self.max_undo_steps = 10
        self.batch_size = 10  # Default batch size
        self.max_workers = 4  # Default number of worker threads
        self.quick_compare = False  # Quick compare mode flag
        
        # Set window title and size
        self.root.title(t('app_title', self.lang))
        print("Setting window title...")
        self.root.geometry("1024x768")
        print("Setting window geometry...")
        
    def show_about(self):
        """Show the about dialog."""
        About.show_about(self.root)
        
    def show_sponsor(self):
        """Show the sponsor dialog."""
        if not hasattr(self, 'sponsor'):
            self.sponsor = Sponsor(self.root)
        self.sponsor.show_sponsor()
        
    def show_help(self):
        """Show the help dialog."""
        HelpWindow(self.root, self.lang)
        
    def on_select(self, event):
        """Handle treeview selection event."""
        selected_items = self.tree.selection()
        if hasattr(self, 'delete_btn'):
            self.delete_btn['state'] = tk.NORMAL if selected_items else tk.DISABLED
        
        # Update preview
        self.update_preview()

    def _add_to_notification_history(self):
        """Add a message to the notification history."""
        if not hasattr(self, 'notification_history'):
            self.notification_history = []
            
        # Add new message to beginning of list
        timestamp = datetime.now()
        self.notification_history.insert(0, {
            'message': message,
            'type': message_type,
            'timestamp': timestamp
        })
        
        # Trim history if needed
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[:self.max_history]
    
    def show_notification_history(self):
        """Show a window with notification history."""
        if not hasattr(self, 'notification_history') or not self.notification_history:
            messagebox.showinfo("Notification History", "No notifications in history.")
            return
            
        history_win = tk.Toplevel(self.root)
        history_win.title("Notification History")
        history_win.geometry("600x400")
        
        # Create a text widget with scrollbar
        frame = ttk.Frame(history_win)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text = tk.Text(
            frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add notifications to text widget
        text.config(state=tk.NORMAL)
        for idx, note in enumerate(self.notification_history):
            # Add separator between entries (except first one)
            if idx > 0:
                text.insert(tk.END, "\n" + "-" * 80 + "\n\n")
                
            # Format timestamp
            timestamp = note['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            
            # Get style for message type
            style = self.message_styles.get(note['type'], self.message_styles['info'])
            
            # Insert message with timestamp
            text.insert(tk.END, f"[{timestamp}]\n", 'timestamp')
            text.insert(tk.END, f"{note['message']}\n")
            
            # Configure tags for styling
            text.tag_configure('timestamp', font=('Segoe UI', 8, 'italic'), foreground='#666666')
            text.tag_configure(note['type'], 
                             foreground=style['fg'], 
                             background=style['bg'],
                             font=('Segoe UI', 10, 'bold'))
            
            # Apply style to the message
            text.tag_add(note['type'], f"{idx*3+2}.0", f"{idx*3+2}.end")
        
        # Add clear button
        btn_frame = ttk.Frame(history_win)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        clear_btn = ttk.Button(
            btn_frame,
            text="Clear History",
            command=lambda: self._clear_notification_history(history_win)
        )
        clear_btn.pack(side=tk.RIGHT)
        
        close_btn = ttk.Button(
            btn_frame,
            text="Close",
            command=history_win.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        text.config(state=tk.DISABLED)
        text.see(tk.END)
    
    def _clear_notification_history(self, window):
        """Clear the notification history."""
        if hasattr(self, 'notification_history'):
            self.notification_history = []
            window.destroy()
            self.show_status("Notification history cleared", "info")
    
    def _play_notification_sound(self, message_type):
        """Play a sound for the notification if enabled."""
        if not self.settings.get('enable_sounds', True):
            return
            
        try:
            import winsound
            # Define default sound constants if they don't exist
            MB_ICONHAND = getattr(winsound, 'MB_ICONHAND', 0x00000010)  # Critical stop/hand/error
            MB_ICONWARNING = getattr(winsound, 'MB_ICONWARNING', 0x00000030)  # Warning
            MB_ICONASTERISK = getattr(winsound, 'MB_ICONASTERISK', 0x00000040)  # Information/asterisk
            
            if message_type == 'error':
                winsound.MessageBeep(MB_ICONHAND)
            elif message_type == 'warning':
                winsound.MessageBeep(MB_ICONWARNING)
            elif message_type == 'success':
                winsound.MessageBeep(MB_ICONASTERISK)
        except Exception:
            # Silently fail if sound can't be played
            pass
    
    def _create_filter_ui(self, parent):
        """Create the filter controls UI."""
        # Filters frame
        filter_frame = ttk.LabelFrame(parent, text=t('filters', self.lang))
        filter_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Size filter frame
        size_frame = ttk.LabelFrame(filter_frame, text=t('file_size_kb', self.lang))
        size_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Min size
        ttk.Label(size_frame, text=t('min', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(size_frame, textvariable=self.filter_size_min, width=8, 
                 validate='key', 
                 validatecommand=(self.root.register(self._validate_number), '%P'))\
            .pack(side=tk.LEFT, padx=2)
        
        # Max size
        ttk.Label(size_frame, text=t('max', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(size_frame, textvariable=self.filter_size_max, width=8,
                 validate='key',
                 validatecommand=(self.root.register(self._validate_number), '%P'))\
            .pack(side=tk.LEFT, padx=2)
        
        # Date filter frame
        date_frame = ttk.LabelFrame(filter_frame, text=t('modified_date', self.lang))
        date_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # From date
        ttk.Label(date_frame, text=t('from', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        from_entry = ttk.Entry(date_frame, textvariable=self.filter_date_from, width=10,
                             validate='key',
                             validatecommand=(self.root.register(self._validate_date), '%P'))
        from_entry.pack(side=tk.LEFT, padx=2)
        
        # To date
        ttk.Label(date_frame, text=t('to', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        to_entry = ttk.Entry(date_frame, textvariable=self.filter_date_to, width=10,
                           validate='key',
                           validatecommand=(self.root.register(self._validate_date), '%P'))
        to_entry.pack(side=tk.LEFT, padx=2)
        
        # Add date picker buttons
        ttk.Button(date_frame, text="📅", width=3,
                  command=lambda: self._show_calendar(from_entry, self.filter_date_from))\
            .pack(side=tk.LEFT, padx=2)
        ttk.Button(date_frame, text="📅", width=3,
                  command=lambda: self._show_calendar(to_entry, self.filter_date_to))\
            .pack(side=tk.LEFT, padx=2)
        
        # Page count filter frame
        page_frame = ttk.LabelFrame(filter_frame, text=t('page_count', self.lang))
        page_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Min pages
        ttk.Label(page_frame, text=t('min', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(page_frame, textvariable=self.filter_pages_min, width=5,
                 validate='key',
                 validatecommand=(self.root.register(self._validate_number), '%P'))\
            .pack(side=tk.LEFT, padx=2)
        
        # Max pages
        ttk.Label(page_frame, text=t('max', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(page_frame, textvariable=self.filter_pages_max, width=5,
                 validate='key',
                 validatecommand=(self.root.register(self._validate_number), '%P'))\
            .pack(side=tk.LEFT, padx=2)
        
        # Filter toggle button with save on change
        def on_filter_toggle():
            self.filters_active.set(not self.filters_active.get())
            self._save_filter_settings()
            self.toggle_filters()
        
        ttk.Checkbutton(
            filter_frame, 
            text=t('enable_filters', self.lang), 
            variable=self.filters_active,
            command=on_filter_toggle
        ).pack(pady=5)
        

    
    def _validate_number(self, value):
        """Validate that the input is a valid number or empty."""
        if value == '':
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _validate_date(self, value):
        """Validate that the input is a valid date (YYYY-MM-DD) or empty."""
        if value == '':
            return True
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return len(value) <= 10 and all(c.isdigit() or c == '-' for c in value)
    
    def _show_calendar(self, entry_widget, date_var):
        """Show a calendar dialog for date selection."""
        try:
            from tkcalendar import Calendar
            
            def set_date():
                date_var.set(cal.selection_get().strftime('%Y-%m-%d'))
                top.destroy()
            
            top = tk.Toplevel(self.root)
            top.title("Select Date")
            
            # Try to parse current date or use today
            try:
                current_date = datetime.strptime(date_var.get(), '%Y-%m-%d')
            except (ValueError, AttributeError):
                current_date = datetime.now()
            
            cal = Calendar(top, selectmode='day', year=current_date.year, 
                          month=current_date.month, day=current_date.day)
            cal.pack(padx=10, pady=10)
            
            ttk.Button(top, text="OK", command=set_date).pack(pady=5)
            
        except ImportError:
            # Fallback to simple date entry if tkcalendar is not available
            entry_widget.focus()
    
    def clear_filters(self):
        """Clear all filter values."""
        self.filter_size_min.set('')
        self.filter_size_max.set('')
        self.filter_date_from.set('')
        self.filter_date_to.set('')
        self.filter_pages_min.set('')
        self.filter_pages_max.set('')
        self._save_filter_settings()
        self.show_status("All filters cleared", "info")
    
    def _on_quick_compare_toggle(self):
        """Handle Quick Compare mode toggle."""
        if self.quick_compare.get():
            self.show_status("Quick Compare enabled - Faster but less accurate scanning", "info")
        else:
            self.show_status("Full comparison mode enabled - More accurate but slower", "info")
        self.save_settings()
    
    def _compare_files(self, file1, file2):
        """Compare two files for equality based on current mode."""
        if self.quick_compare.get():
            # Quick compare: Only check file size
            try:
                return os.path.getsize(file1) == os.path.getsize(file2)
            except:
                return False
        else:
            # Full compare: Compare file contents
            try:
                with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                    # Compare file sizes first (quick check)
                    if os.path.getsize(file1) != os.path.getsize(file2):
                        return False
                    # If sizes match, compare content
                    return f1.read() == f2.read()
            except:
                return False
    
    def find_duplicates(self):
        """Find duplicate PDF files in the selected folder."""
        from app_struct.search_dup import DuplicateFinder
        
        if not hasattr(self, 'duplicate_finder'):
            self.duplicate_finder = DuplicateFinder(self)
            
        folder_path = self.folder_path.get()
        self.duplicate_finder.find_duplicates(folder_path)
        self.overall_progress_var.set(0)
        self.status_text.set("Scanning for PDF files...")
        self.root.update_idletasks()
        
        try:
            # Find all PDF files
            pdf_files = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
            
            total_files = len(pdf_files)
            self.status_text.set(f"Found {total_files} PDF files. Analyzing...")
            self.progress_var.set(0)
            self.progress['maximum'] = total_files
            self.root.update_idletasks()
            
            if self.quick_compare.get():
                # Quick compare mode: group by file size only
                self.show_status("Quick Compare: Grouping files by size...", "info")
                size_map = {}
                for i, file_path in enumerate(pdf_files, 1):
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size in size_map:
                            size_map[file_size].append(file_path)
                        else:
                            size_map[file_size] = [file_path]
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                    
                    # Update progress
                    self.progress_var.set(i)
                    if i % 10 == 0:  # Update UI every 10 files
                        self.root.update_idletasks()
                
                # Only keep groups with more than one file
                self.duplicates = [files for files in size_map.values() if len(files) > 1]
                
            else:
                # Full compare mode: compare file contents
                self.show_status("Full comparison: Analyzing file contents...", "info")
                self.duplicates = []
                processed = set()
                
                for i in range(total_files):
                    if i in processed:
                        continue
                        
                    current_file = pdf_files[i]
                    current_duplicates = [current_file]
                    
                    for j in range(i + 1, total_files):
                        if j in processed:
                            continue
                            
                        if self._compare_files(current_file, pdf_files[j]):
                            current_duplicates.append(pdf_files[j])
                            processed.add(j)
                    
                    if len(current_duplicates) > 1:
                        self.duplicates.append(current_duplicates)
                    
                    # Update progress
                    self.progress_var.set(i + 1)
                    if (i + 1) % 5 == 0:  # Update UI more frequently for full compare
                        self.root.update_idletasks()
            
            # Update UI with results
            self._update_results_ui()
            
            # Update status
            if self.duplicates:
                dup_count = len(self.duplicates)
                file_count = sum(len(group) for group in self.duplicates)
                self.show_status(
                    f"Found {dup_count} groups with {file_count} duplicate files" +
                    (" (Quick Compare)" if self.quick_compare.get() else ""), 
                    "info"
                )
                self.save_btn.config(state=tk.NORMAL)
            else:
                self.show_status("No duplicate files found" + 
                               (" (Quick Compare)" if self.quick_compare.get() else ""), 
                               "info")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Reset UI
            self.find_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def _update_results_ui(self):
        """Update the results in the UI."""
        if not hasattr(self, 'tree') or not hasattr(self, 'duplicates'):
            return
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new items
        group_id = 1
        for group in self.duplicates:
            if not group:  # Skip empty groups
                continue
                
            # Sort files by path for consistent ordering
            group = sorted(group)
            
            # The first file is considered the "original" for comparison
            original_path = group[0]
            try:
                original_size = os.path.getsize(original_path)
                original_date = datetime.fromtimestamp(os.path.getmtime(original_path)).strftime('%Y-%m-%d %H:%M')
                
                # Add the original file
                self.tree.insert("", "end", 
                               values=(
                                   os.path.basename(original_path),
                                   f"{original_size/1024:,.1f} KB",
                                   original_date,
                                   "",  # size_diff (empty for original)
                                   "",  # date_diff (empty for original)
                                   "",  # orig_path (empty for original)
                                   "",  # orig_size (empty for original)
                                   "",  # orig_date (empty for original)
                                   original_path  # full_path
                               ),
                               tags=('original',))
                
                # Add duplicates with comparison to original
                for dup_path in group[1:]:
                    try:
                        dup_size = os.path.getsize(dup_path)
                        dup_date = datetime.fromtimestamp(os.path.getmtime(dup_path)).strftime('%Y-%m-%d %H:%M')
                        
                        # Calculate differences
                        size_diff = dup_size - original_size
                        size_diff_str = f"{size_diff/1024:+,.1f} KB" if size_diff != 0 else "0 KB"
                        
                        # Calculate date difference
                        date_diff = (datetime.strptime(dup_date, '%Y-%m-%d %H:%M') - 
                                   datetime.strptime(original_date, '%Y-%m-%d %H:%M'))
                        date_diff_str = str(date_diff)
                        
                        self.tree.insert("", "end",
                                       values=(
                                           os.path.basename(dup_path),
                                           f"{dup_size/1024:,.1f} KB",
                                           dup_date,
                                           size_diff_str,
                                           date_diff_str,
                                           os.path.basename(original_path),
                                           f"{original_size/1024:,.1f} KB",
                                           original_date,
                                           dup_path  # full_path
                                       ),
                                       tags=('duplicate',))
                    except Exception as e:
                        print(f"Error adding duplicate {dup_path}: {e}")
                        
                # Add a separator between groups
                self.tree.insert("", "end", values=("-"*20, "", "", "", "", "", "", "", ""), tags=('separator',))
                group_id += 1
                
            except Exception as e:
                print(f"Error processing group {group_id}: {e}")
                    
        # Update status bar
        if hasattr(self, 'status_text'):
            self.status_text.set(f"Found {len(self.duplicates)} groups of duplicates")
    
    def on_filter_toggle(self):
        """Handle filter activation/deactivation."""
        if self.filters_active.get():
            # Apply filters
            self._apply_filters()
        else:
            # Reset to show all results when filters are disabled
            if hasattr(self, 'duplicates'):
                self._update_results_ui()
    
    def _apply_filters(self):
        """Apply filters to the current results."""
        if not hasattr(self, 'duplicates') or not self.duplicates:
            return
            
        # If filters are not active, show all results
        if not self.filters_active.get():
            self._update_results_ui()
            return
            
        # Get filter values
        size_min = self.filter_size_min.get()
        size_max = self.filter_size_max.get()
        date_from = self.filter_date_from.get()
        date_to = self.filter_date_to.get()
        pages_min = self.filter_pages_min.get()
        pages_max = self.filter_pages_max.get()
        
        # Filter duplicates based on criteria
        filtered_duplicates = []
        
        for group in self.duplicates:
            filtered_group = []
            for file_path in group:
                try:
                    # Get file info
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    mod_time = os.path.getmtime(file_path)
                    mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                    
                    # Page count is not implemented yet, using 0 as placeholder
                    page_count = 0
                    
                    # Apply filters
                    size_ok = (not size_min or file_size >= float(size_min)) and \
                             (not size_max or file_size <= float(size_max))
                    
                    date_ok = (not date_from or mod_date >= date_from) and \
                             (not date_to or mod_date <= date_to)
                    
                    pages_ok = (not pages_min or page_count >= int(pages_min)) and \
                              (not pages_max or page_count <= int(pages_max))
                    
                    if size_ok and date_ok and pages_ok:
                        filtered_group.append(file_path)
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
            
            if filtered_group:
                filtered_duplicates.append(filtered_group)
        
        # Update UI with filtered results
        self._update_results_ui(filtered_duplicates)

    
    def toggle_filters_visibility(self):
        """Toggle the visibility of the filters section."""
        self.filters_visible = not self.filters_visible
        
        if self.filters_visible:
            self.filters_container.pack(fill=tk.X, padx=5, pady=5)
            self.toggle_filters_btn.config(text="-")
        else:
            self.filters_container.pack_forget()
            self.toggle_filters_btn.config(text="+")
            
        # Save the filters visibility state
        self.settings['filters_visible'] = self.filters_visible
        self.save_settings()
        
    def toggle_tree_visibility(self):
        """Toggle the visibility of the treeview."""
        self.tree_visible = not self.tree_visible
        
        if self.tree_visible:
            self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.toggle_tree_btn.config(text="◀")
        else:
            self.left_frame.pack_forget()
            self.toggle_tree_btn.config(text="▶")
            
        # Save the treeview visibility state
        self.settings['tree_visible'] = self.tree_visible
        self.save_settings()
        
    def toggle_preview_visibility(self):
        """Toggle the visibility of the preview panel."""
        self.preview_visible = not self.preview_visible
        
        if self.preview_visible:
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
            self.toggle_preview_btn.config(text="▶")
        else:
            self.right_frame.pack_forget()
            self.toggle_preview_btn.config(text="◀")
            
        # Save the preview visibility state
        self.settings['preview_visible'] = self.preview_visible
        self.save_settings()
    
    def _set_process_priority(self):
        """Set the process priority to below normal to improve system responsiveness."""
        try:
            if os.name == 'nt':  # Windows
                import win32api, win32process, win32con
                pid = win32api.GetCurrentProcessId()
                handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
                win32process.SetPriorityClass(handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
        except Exception as e:
            print(f"Warning: Could not set process priority: {e}")
    
    def _setup_ui(self):
        """Set up the user interface components."""
        print("Setting up UI...")
        
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Initialize suppress_warnings_var for the menu
        self.suppress_warnings_var = tk.BooleanVar(value=self.suppress_warnings)
        
        # Apply theme if theme manager exists
        if hasattr(self, 'theme_manager') and hasattr(self, 'theme_var'):
            self.theme_manager.apply_theme(self.theme_var.get())
        
        # Bind F5 to refresh
        self.root.bind('<F5>', lambda e: self.find_duplicates() if self.folder_path.get() else None)
        self.root.bind('<Control-z>', lambda e: self.undo_last_delete() if hasattr(self, 'menu_manager') and hasattr(self.menu_manager, 'undo_menu_item') and self.menu_manager.undo_menu_item['state'] == tk.NORMAL else None)
        
        # Drag and drop is now handled by DragDropManager
        
        # Create left and right frames for the main layout
        self.left_frame = ttk.Frame(self.main_container)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create right frame for preview
        self.right_frame = ttk.Frame(self.main_container, width=300)
        # Don't pack it yet, it will be packed when preview is shown
        
        # Treeview visibility toggle button
        self.toggle_tree_btn = ttk.Button(
            self.main_container,
            text="◀" if self.tree_visible else "▶",
            width=2,
            command=self.toggle_tree_visibility
        )
        self.toggle_tree_btn.pack(side=tk.LEFT, fill=tk.Y, padx=2)
        
        # Add drop target highlight (initially hidden)
        self.drop_highlight = ttk.Label(
            self.main_container, 
            text=t('drop_folder_here', self.lang), 
            background='#e6f3ff', 
            foreground='#0066cc',
            relief='solid',
            borderwidth=2
        )
        self.drop_highlight.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.8, relheight=0.8)
        self.drop_highlight.place_forget()  # Hide by default
        
        # Apply saved theme
        self.change_theme(self.settings.get('theme', 'light'))

        # Search controls at the top of left frame
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill=tk.X, pady=5)

        # Move search controls to search frame
        tk.Label(search_frame, text=t('select_folder', self.lang), font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.folder_path, width=50, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text=t('browse', self.lang), command=self.browse_folder, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Create buttons frame
        self.button_frame = ttk.Frame(self.left_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        # Add delete button first
        self.delete_btn = ttk.Button(
            self.button_frame,
            text="Elimina Selezionati",
            command=self.file_deleter.delete_selected,
            style='Danger.TButton',
            state=tk.DISABLED  # Initially disabled
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add other buttons frame for find/stop
        action_frame = ttk.Frame(self.button_frame)
        action_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Find duplicates button
        self.find_btn = tk.Button(action_frame, text=t('find_duplicates', self.lang), 
                                command=self.find_duplicates, 
                                font=("Arial", 10))
        self.find_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Stop scan button
        self.stop_btn = tk.Button(action_frame, text=t('stop_scan', self.lang) if hasattr(t, 'stop_scan') else 'Stop Scan',
                                command=self.cancel_scan,
                                font=("Arial", 10), 
                                state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
                 
        # Save and load buttons
        self.save_btn = tk.Button(self.button_frame, text=t('save_results', self.lang), command=self.save_scan_results,
                               font=("Arial", 10), state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Load results button
        tk.Button(self.button_frame, text=t('load_results', self.lang), command=self.load_scan_results,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Quick Compare checkbox
        self.quick_compare_var = tk.BooleanVar()
        self.quick_compare = ttk.Checkbutton(
            self.button_frame,
            text=t('quick_compare', self.lang) if hasattr(t, 'quick_compare') else 'Quick Compare',
            variable=self.quick_compare_var,
            command=self._on_quick_compare_toggle
        )
        self.quick_compare.pack(side=tk.RIGHT, padx=5, pady=2)

        # Progress bar and status
        self.progress_frame = ttk.Frame(self.left_frame)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        # Overall progress bar
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 2))
        
        # Individual file progress bar
        self.file_progress_frame = ttk.Frame(self.progress_frame)
        self.file_progress_frame.pack(fill=tk.X, pady=(0, 2))
        
        self.file_progress_label = ttk.Label(self.file_progress_frame, text=t('current_file', self.lang) + ":")
        self.file_progress_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_progress_bar = ttk.Progressbar(self.file_progress_frame, mode='determinate')
        self.file_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Filters section with toggle
        self.filter_frame = ttk.LabelFrame(self.left_frame, text=t('filters', self.lang))
        self.filter_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Add toggle button in the title bar of the filter frame
        self.toggle_filters_btn = ttk.Button(
            self.filter_frame, 
            text="-" if self.filters_visible else "+", 
            width=2,
            command=self.toggle_filters_visibility
        )
        self.toggle_filters_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Container for all filter controls
        self.filters_container = ttk.Frame(self.filter_frame)
        if self.filters_visible:
            self.filters_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Size filter
        size_frame = ttk.LabelFrame(self.filters_container, text=t('file_size_kb', self.lang))
        size_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(size_frame, text=t('min', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(size_frame, textvariable=self.filter_size_min, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(size_frame, text="-").pack(side=tk.LEFT, padx=2)
        ttk.Entry(size_frame, textvariable=self.filter_size_max, width=8).pack(side=tk.LEFT, padx=2)
        
        # Date filter
        date_frame = ttk.LabelFrame(self.filters_container, text=t('modified_date', self.lang))
        date_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(date_frame, text=t('from', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(date_frame, textvariable=self.filter_date_from, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Label(date_frame, text=t('to', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(date_frame, textvariable=self.filter_date_to, width=10).pack(side=tk.LEFT, padx=2)
        
        # Page count filter
        page_frame = ttk.LabelFrame(self.filters_container, text=t('page_count', self.lang))
        page_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(page_frame, text=t('min', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(page_frame, textvariable=self.filter_pages_min, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(page_frame, text="-").pack(side=tk.LEFT, padx=2)
        ttk.Entry(page_frame, textvariable=self.filter_pages_max, width=5).pack(side=tk.LEFT, padx=2)
        
        # Filter toggle button
        filter_controls_frame = ttk.Frame(self.filters_container)
        filter_controls_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(
            filter_controls_frame, 
            text=t('enable_filters', self.lang), 
            variable=self.filters_active,
            command=self.on_filter_toggle
        ).pack(side=tk.LEFT, padx=5)
        
        # Clear filters button
        ttk.Button(
            filter_controls_frame,
            text=t('clear_filters', self.lang),
            command=self.clear_filters
        ).pack(side=tk.RIGHT, padx=5)
        
        # Treeview frame
        self.tree_frame = ttk.Frame(self.left_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Add scrollbars to treeview
        tree_scroll_y = ttk.Scrollbar(self.tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create treeview with all necessary columns
        self.tree = ttk.Treeview(
            self.tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode='extended',
            columns=('filename', 'size', 'modified', 'size_diff', 'date_diff', 'original_name', 'original_size', 'original_date', 'full_path'),
            show='headings'  # Nasconde la colonna #0 vuota
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Configure treeview columns
        self.tree.heading('filename', text=t('filename', self.lang), anchor=tk.W)
        self.tree.heading('size', text=t('size', self.lang), anchor=tk.E)
        self.tree.heading('modified', text=t('modified', self.lang), anchor=tk.W)
        self.tree.heading('size_diff', text=t('size_diff', self.lang), anchor=tk.E)
        self.tree.heading('date_diff', text=t('date_diff', self.lang), anchor=tk.W)
        self.tree.heading('original_name', text=t('original_file', self.lang), anchor=tk.W)
        self.tree.heading('original_size', text=t('original_size', self.lang), anchor=tk.E)
        self.tree.heading('original_date', text=t('original_date', self.lang), anchor=tk.W)
        
        # Set column widths and properties
        self.tree.column('filename', width=200, minwidth=150, stretch=tk.YES, anchor=tk.W)
        self.tree.column('size', width=80, minwidth=60, stretch=tk.NO, anchor=tk.E)
        self.tree.column('modified', width=140, minwidth=100, stretch=tk.NO, anchor=tk.W)
        self.tree.column('size_diff', width=80, minwidth=60, stretch=tk.NO, anchor=tk.E)
        self.tree.column('date_diff', width=100, minwidth=80, stretch=tk.NO, anchor=tk.W)
        self.tree.column('original_name', width=200, minwidth=150, stretch=tk.YES, anchor=tk.W)
        self.tree.column('original_size', width=80, minwidth=60, stretch=tk.NO, anchor=tk.E)
        self.tree.column('original_date', width=140, minwidth=100, stretch=tk.NO, anchor=tk.W)
        
        # Hide the full path column (it's only used for reference)
        self.tree.column('full_path', width=0, stretch=tk.NO, minwidth=0)
        
        # Add tag for alternate row colors
        self.tree.tag_configure('oddrow', background='#f0f0f0')
        self.tree.tag_configure('evenrow', background='#ffffff')
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Delete button is now created with other buttons in the button_frame
        
        # Add toggle button for treeview visibility
        self.toggle_tree_btn = ttk.Button(
            self.left_frame,
            text="Hide" if self.tree_visible else "Show",
            command=self.toggle_tree_visibility
        )
        self.toggle_tree_btn.pack(side=tk.BOTTOM, pady=5)
        
        # Create preview container in the right frame
        preview_container = ttk.Frame(self.right_frame, padding=5)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # Preview label
        preview_label = ttk.Label(preview_container, text=t('preview', self.lang), font=('Arial', 12, 'bold'))
        preview_label.pack(anchor='w', pady=(0, 5))
        
        # Preview type selector
        preview_type_frame = ttk.Frame(preview_container)
        preview_type_frame.pack(fill=tk.X, pady=5)
        
        self.preview_type = tk.StringVar(value="image")
        ttk.Radiobutton(preview_type_frame, text="Image", variable=self.preview_type, 
                       value="image", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(preview_type_frame, text="Text", variable=self.preview_type,
                       value="text", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        
        # Canvas for image preview
        self.preview_canvas = tk.Canvas(preview_container, bg='white', highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Text widget for text preview
        self.preview_text = tk.Text(preview_container, wrap=tk.WORD, font=("Arial", 10))
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.pack_forget()  # Hide by default
        
        # Buttons frame for selection controls
        selection_frame = ttk.Frame(self.left_frame)
        selection_frame.pack(fill=tk.X, pady=2)
        
        # Select All button
        self.select_all_btn = ttk.Button(
            selection_frame,
            text=t('select_all', self.lang) if hasattr(t, 'select_all') else 'Select All',
            command=self.select_all_items,
            style='TButton'
        )
        self.select_all_btn.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        
        # Deselect All button
        self.deselect_all_btn = ttk.Button(
            selection_frame,
            text=t('deselect_all', self.lang) if hasattr(t, 'deselect_all') else 'Deselect All',
            command=self.deselect_all_items,
            style='TButton'
        )
        self.deselect_all_btn.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        
        # Buttons frame for delete and preview - renamed to avoid conflict
        action_buttons_frame = ttk.Frame(self.left_frame)
        action_buttons_frame.pack(fill=tk.X, pady=2)
        
        # Preview button
        self.preview_btn = ttk.Button(
            action_buttons_frame,
            text=t('preview', self.lang),
            command=self.preview_selected,
            style='Accent.TButton',  # Make it stand out
            state=tk.DISABLED  # Disabled by default until files are selected
        )
        self.preview_btn.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)
        
        # Pack the right frame if preview is visible
        if self.preview_visible:
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    def choose_color(self, title="Choose a color", initialcolor=None):
        """Open a color chooser dialog and return the selected color."""
        color = colorchooser.askcolor(color=initialcolor, title=title)
        return color[1] if color[1] else None

    def apply_custom_theme(self, primary_color, secondary_color, text_color, bg_color):
        """Apply a custom color theme to the application."""
        # Store colors
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.text_color = text_color
        self.bg_color = bg_color
        
        # Apply colors to widgets
        style = ttk.Style()
        style.configure('.', background=bg_color, foreground=text_color)
        style.configure('TButton', background=primary_color, foreground=text_color)
        style.map('TButton',
                 background=[('active', secondary_color)],
                 foreground=[('active', text_color)])
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color)
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', background=bg_color, foreground=text_color)
        style.map('TNotebook.Tab',
                 background=[('selected', primary_color)],
                 foreground=[('selected', text_color)])
        
        # Apply to root and main container
        self.root.configure(bg=bg_color)
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Frame, ttk.Label, ttk.Button)):
                widget.configure(style='TFrame')
        
        self.show_status("Custom theme applied successfully", "success")

    def select_all_items(self):
        """Select all items in the treeview."""
        if hasattr(self, 'tree'):
            self.tree.selection_set(self.tree.get_children())
            self.on_select(None)  # Update UI based on selection
    
    def deselect_all_items(self):
        """Deselect all items in the treeview."""
        if hasattr(self, 'tree'):
            self.tree.selection_remove(self.tree.selection())
            self.on_select(None)  # Update UI based on selection
    
    def open_theme_editor(self):
        """Open a dialog to customize the application theme."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Customize Theme")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Position the dialog relative to the main window
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Store current colors
        current_primary = self.primary_color
        current_secondary = self.secondary_color
        current_text = self.text_color
        current_bg = self.bg_color
        
        # Create color selection buttons
        def choose_color(color_var, button, title):
            color = self.choose_color(title, color_var.get())
            if color:
                color_var.set(color)
                button.configure(bg=color)
        
        # Primary color
        ttk.Label(dialog, text="Primary Color:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        primary_var = tk.StringVar(value=current_primary)
        primary_btn = tk.Button(dialog, bg=primary_var.get(), width=10, 
                              command=lambda: choose_color(primary_var, primary_btn, "Choose Primary Color"))
        primary_btn.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Secondary color
        ttk.Label(dialog, text="Secondary Color:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        secondary_var = tk.StringVar(value=current_secondary)
        secondary_btn = tk.Button(dialog, bg=secondary_var.get(), width=10,
                                command=lambda: choose_color(secondary_var, secondary_btn, "Choose Secondary Color"))
        secondary_btn.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Text color
        ttk.Label(dialog, text="Text Color:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        text_var = tk.StringVar(value=current_text)
        text_btn = tk.Button(dialog, bg=text_var.get(), width=10,
                           command=lambda: choose_color(text_var, text_btn, "Choose Text Color"))
        text_btn.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Background color
        ttk.Label(dialog, text="Background Color:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        bg_var = tk.StringVar(value=current_bg)
        bg_btn = tk.Button(dialog, bg=bg_var.get(), width=10,
                         command=lambda: choose_color(bg_var, bg_btn, "Choose Background Color"))
        bg_btn.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Preview button
        preview_btn = ttk.Button(dialog, text="Preview",
                               command=lambda: self.apply_custom_theme(
                                   primary_var.get(),
                                   secondary_var.get(),
                                   text_var.get(),
                                   bg_var.get()
                               ))
        preview_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Apply button
        apply_btn = ttk.Button(dialog, text="Apply",
                             command=lambda: [
                                 self.apply_custom_theme(
                                     primary_var.get(),
                                     secondary_var.get(),
                                     text_var.get(),
                                     bg_var.get()
                                 ),
                                 dialog.destroy()
                             ])
        apply_btn.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Cancel button
        cancel_btn = ttk.Button(dialog, text="Cancel",
                              command=dialog.destroy)
        cancel_btn.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Make the dialog modal
        dialog.wait_window()

    def update_file_progress(self, value, max_value=100):
        """Update the individual file progress bar."""
        if not self.is_searching:
            return
            
        if max_value > 0:
            percent = int((value / max_value) * 100)
        else:
            percent = 0
            
        self.progress_var.set(percent)
        self.file_progress_bar['value'] = percent
        self.root.update_idletasks()
        
    def update_file_status(self, filename):
        """Update the current file being processed."""
        if not self.is_searching:
            return
            
        self.current_file = filename
        short_name = os.path.basename(filename)[:30] + '...' if len(filename) > 30 else filename
        self.file_progress_label.config(text=f"Current file: {short_name}")
        self.root.update_idletasks()
        
    def update_overall_progress(self, value, maximum=100):
        """Update the overall progress bar."""
        if not self.is_searching:
            return
            
        self.overall_progress_var.set(value)
        self.progress_bar['maximum'] = maximum
        self.progress_bar['value'] = value
        self.root.update_idletasks()
        
    def clear_status(self):
        """Clear the status message and reset progress bars."""
        self.status_text.set("")
        self.status_details.config(text="")
        if hasattr(self, 'progress_bar'):
            self.progress_bar['value'] = 0
        if hasattr(self, 'file_progress_bar'):
            self.file_progress_bar['value'] = 0
        if hasattr(self, 'file_progress_label'):
            self.file_progress_label.config(text=t('current_file', self.lang) + ":")
        self.root.update_idletasks()
    def update_status_details(self, message, message_type="info"):
        """Update the status text with detailed information.
        
        Args:
            message (str): Detailed status message
            message_type (str): Type of message (info, success, warning, error, etc.)
        """
        if not self.is_searching:
            return
            
        # Show as a progress message if not specified otherwise
        if message_type == "info":
            message_type = "progress"
            
        self.show_status(message, message_type=message_type, show_notification=False)
        self.root.update_idletasks()
        
    def tree_sort_column(self, col, reverse):
        """Sort tree contents when a column header is clicked."""
        # Get all items and their values
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        # Determine data type for sorting
        col_type = str
        if col in ('dup_size', 'orig_size'):
            col_type = float
        elif col in ('dup_date', 'orig_date'):
            col_type = lambda x: float(x or 0)
            
        # Sort the items
        try:
            l.sort(key=lambda t: col_type(t[0]), reverse=reverse)
        except (ValueError, TypeError):
            # Fall back to string comparison if type conversion fails
            l.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
        
        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        
        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.tree_sort_column(col, not reverse))
        
        # Update sort indicators
        if self.tree_sort_column_id:
            self.tree.heading(self.tree_sort_column_id, text=self.tree.heading(self.tree_sort_column_id, 'text').rstrip(' ↓↑'))
        self.tree_sort_column_id = col
        sort_symbol = ' ↓' if reverse else ' ↑'
        current_text = self.tree.heading(col, 'text')
        self.tree.heading(col, text=current_text.rstrip(' ↓↑') + sort_symbol)
        self.tree_sort_reverse = not reverse

    def _on_drop_leave(self, event):
        """Handle drag leave event."""
        if hasattr(self, 'drop_highlight'):
            self.drop_highlight.destroy()
            del self.drop_highlight
            
    def safe_update_status(self, message, message_type="info"):
        """Thread-safe method to update status from background threads.
        
        Args:
            message (str): The status message to display
            message_type (str): Type of message (info, success, warning, error, etc.)
        """
        if not hasattr(self, 'root'):
            return
            
        def _update():
            try:
                self.show_status(message, message_type)
            except Exception as e:
                print(f"Error updating status: {e}")
                
        try:
            self.root.after(0, _update)
        except Exception as e:
            print(f"Error scheduling status update: {e}")

    def on_drop_leave(self, event):
        """Handle drag leave event."""
        if self.drop_highlight:
            self.drop_highlight.place_forget()
    
    def on_drop(self, event):
        """Handle drop event."""
        if self.drop_highlight:
            self.drop_highlight.place_forget()
            
        # Get the dropped items
        try:
            # On Windows, event.data is a string with filenames
            if hasattr(event, 'data'):
                # Remove the {} and split by spaces that aren't preceded by a backslash
                import re
                files = re.split(r'(?<!\\)\s+', event.data.strip('{}'))
                files = [f.replace('\\', '') for f in files if f]
                
                # Take the first valid directory or PDF file
                for path in files:
                    try:
                        if os.path.isdir(path):
                            self.folder_path.set(path)
                            self.find_duplicates()
                            break
                        elif os.path.isfile(path) and path.lower().endswith('.pdf'):
                            # If a PDF file is dropped, use its directory
                            self.folder_path.set(os.path.dirname(path))
                            self.find_duplicates()
                            break
                    except Exception as e:
                        logger.warning(f"Error processing dropped item {path}: {e}")
                        
        except Exception as e:
            messagebox.showerror("Error", f"Could not process dropped item: {str(e)}")
    
    def browse_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(title=t('select_folder', self.lang))
        if folder:
            self.folder_path.set(folder)

    def get_pdf_info(self, file_path):
        """Get PDF metadata including page count and modification time."""
        file_info = {
            'path': file_path,
            'file': os.path.basename(file_path),
            'size_kb': 0,
            'mod_time': 0,
            'page_count': 0,
            'error': None
        }
        
        try:
            # Check if file exists and is accessible
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                file_info['error'] = error_msg
                logger.warning(error_msg)
                self.problematic_files.append(file_info)
                return None
                
            if not os.access(file_path, os.R_OK):
                error_msg = f"No read permission for: {file_path}"
                file_info['error'] = error_msg
                logger.warning(error_msg)
                self.problematic_files.append(file_info)
                return None
                
            # Get file size in KB
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                error_msg = f"Empty file: {file_path}"
                file_info['error'] = error_msg
                logger.warning(error_msg)
                self.problematic_files.append(file_info)
                return None
                
            file_info['size_kb'] = file_size / 1024
            file_info['mod_time'] = os.path.getmtime(file_path)
            
            # Get page count with more robust error handling
            try:
                with open(file_path, 'rb') as f:
                    try:
                        pdf_reader = PdfReader(f)
                        file_info['page_count'] = len(pdf_reader.pages)
                        
                        if file_info['page_count'] == 0:
                            error_msg = f"No pages in PDF: {os.path.basename(file_path)}"
                            file_info['error'] = error_msg
                            logger.warning(error_msg)
                            self.problematic_files.append(file_info)
                        
                        # Try to access some basic metadata to verify PDF is not completely broken
                        try:
                            _ = pdf_reader.metadata
                        except Exception as meta_err:
                            error_msg = f"PDF metadata access error: {str(meta_err)}"
                            file_info['error'] = error_msg
                            if not self.suppress_warnings:
                                logger.warning(f"{os.path.basename(file_path)} - {error_msg}")
                            self.problematic_files.append(file_info)
                        
                    except (PdfReadError, PyPDF2.errors.PdfReadError) as e:
                        error_msg = f"Corrupted PDF: {str(e)}"
                        file_info['error'] = error_msg
                        if not self.suppress_warnings:
                            logger.warning(f"{os.path.basename(file_path)} - {error_msg}")
                        self.problematic_files.append(file_info)
                        file_info['page_count'] = 0
                        
                    except Exception as e:
                        error_msg = f"Error reading PDF: {type(e).__name__} - {str(e)}"
                        file_info['error'] = error_msg
                        logger.warning(f"{os.path.basename(file_path)} - {error_msg}")
                        self.problematic_files.append(file_info)
                        file_info['page_count'] = 0
                    
                    return file_info
                    
            except Exception as e:
                error_msg = f"Error processing PDF: {type(e).__name__} - {str(e)}"
                file_info['error'] = error_msg
                logger.error(f"{file_path} - {error_msg}")
                self.problematic_files.append(file_info)
                return None
                
        except Exception as e:
            error_msg = f"Unexpected error processing file: {type(e).__name__} - {str(e)}"
            file_info['error'] = error_msg
            logger.error(f"{file_path} - {error_msg}")
            self.problematic_files.append(file_info)
            return None

    def apply_filters(self, file_info):
        """Check if file passes all active filters."""
        if not self.filters_active.get():
            return True
            
        # Size filter
        if self.filter_size_min.get() or self.filter_size_max.get():
            try:
                size_min = float(self.filter_size_min.get()) if self.filter_size_min.get() else 0
                size_max = float(self.filter_size_max.get()) if self.filter_size_max.get() else float('inf')
                if not (size_min <= file_info['size_kb'] <= size_max):
                    return False
            except ValueError:
                pass
                
        # Date filter
        if self.filter_date_from.get() or self.filter_date_to.get():
            try:
                from datetime import datetime
                mod_time = datetime.fromtimestamp(file_info['mod_time']).date()
                
                if self.filter_date_from.get():
                    date_from = datetime.strptime(self.filter_date_from.get(), '%Y-%m-%d').date()
                    if mod_time < date_from:
                        return False
                        
                if self.filter_date_to.get():
                    date_to = datetime.strptime(self.filter_date_to.get(), '%Y-%m-%d').date()
                    if mod_time > date_to:
                        return False
            except Exception:
                pass
                
        # Page count filter
        if self.filter_pages_min.get() or self.filter_pages_max.get():
            try:
                min_pages = int(self.filter_pages_min.get()) if self.filter_pages_min.get() else 0
                max_pages = int(self.filter_pages_max.get()) if self.filter_pages_max.get() else float('inf')
                if not (min_pages <= file_info['page_count'] <= max_pages):
                    return False
            except ValueError:
                pass
                
        return True

    def calculate_pdf_hash(self, file_info):
        """Calculate hash for a PDF file with caching of file info.
        
        Args:
            file_info: Dictionary containing file information including 'path'
            
        Returns:
            str: MD5 hash of the file content or None if cancelled
        """
        if not self.is_searching:
            print("[INFO] Processing cancelled")
            return None
            
        file_path = file_info['path']
        
        try:
            # Calculate MD5 hash of the file content
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    if not self.is_searching:
                        print(f"[INFO] Cancelled while reading {file_path}")
                        return None
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
            return True  # Passed all filters
            
        except Exception as e:
            self.show_status(f"Error applying filters: {str(e)}", "error")
            return True  # If there's an error, include the file to be safe
    
    def calculate_pdf_hash(self, file_info):
        """Calculate hash for a PDF file with caching of file info.
        
        Args:
            file_info: Dictionary containing file information including 'path'
            
        Returns:
            str: MD5 hash of the file content or None if cancelled
        """
        if not self.is_searching:
            print("[INFO] Processing cancelled")
            return None
            
        file_path = file_info['path']
        
        try:
            # Calculate MD5 hash of the file content
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    if not self.is_searching:
                        print(f"[INFO] Cancelled while reading {file_path}")
                        return None
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
        except Exception as e:
            print(f"[ERROR] Error calculating hash for {file_path}: {e}")
            return None

    def _process_pdf_file(self, file_path, hash_map, lock):
        """Process a single PDF file and return (file_hash, file_path)."""
        try:
            # Skip if search was cancelled
            if hasattr(self, 'stop_search') and self.stop_search:
                return None
                
            # Update progress
            self.update_file_status(os.path.basename(file_path))
            
            # Get file info
            file_info = self.get_pdf_info(file_path)
            if not file_info:
                return None
            
            # Apply filters if active
            if hasattr(self, 'filters_active') and self.filters_active.get():
                if not self.apply_filters(file_info):
                    return None  # Skip file if it doesn't match filters
                
            # Calculate hash
            file_hash = self.calculate_pdf_hash(file_info)
            if not file_hash:
                return None
                
            # Return the hash and file path
            return (file_hash, file_path)

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            print(error_msg)
            self.show_status(error_msg, "error")
            return None
    
    def _find_pdf_files(self, folder, stop_event):
        """Generator that yields PDF files with cancellation support."""
        for root, _, files in os.walk(folder):
            if stop_event.is_set():
                return
                
            for file in files:
                if stop_event.is_set():
                    return
                    
                if file.lower().endswith(".pdf"):
                    yield os.path.join(root, file)

    def perform_search(self, folder):
        if not self.is_searching:
            return
            
        # Set process priority if in low priority mode
        if hasattr(self, 'low_priority') and self.low_priority.get():
            self._set_process_priority()

        # Clear previous results
        self.duplicates = []
        self.problematic_files = []
        
        # For thread-safe operations
        pdf_hash_map = {}
        results_lock = threading.Lock()
        stop_event = threading.Event()
        duplicate_counter = 0
        start_time = time.time()
        
        # Check cache first if enabled
        cache_enabled = hasattr(self, 'use_cache') and self.use_cache.get()
        cache_file = os.path.join(self.cache_dir, f"scan_cache_{hash(folder)}.json")
        
        # Load from cache if available
        if cache_enabled and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Check if cache is for the same folder and not too old (1 day)
                if (cache_data.get('folder') == folder and 
                    time.time() - cache_data.get('timestamp', 0) < 86400):
                    
                    # Ensure the loaded data has the correct structure
                    raw_duplicates = cache_data.get('duplicates', [])
                    self.duplicates = []
                    
                    # Process each group in the cache
                    for group in raw_duplicates:
                        if isinstance(group, (list, tuple)):
                            # Ensure all items in the group are strings
                            valid_group = [f for f in group if isinstance(f, str) and f.strip()]
                            if len(valid_group) > 1:  # Only keep groups with duplicates
                                self.duplicates.append(valid_group)
                    
                    # Process file info
                    raw_file_info = cache_data.get('file_info', [])
                    self.all_pdf_files = []
                    for file_list in raw_file_info:
                        if isinstance(file_list, (list, tuple)):
                            valid_files = [f for f in file_list if isinstance(f, str) and f.strip()]
                            if valid_files:
                                self.all_pdf_files.append(valid_files)
                    
                    # Update UI with cached results
                    self.root.after(0, lambda: self._update_results_ui())
                    self.root.after(0, lambda: self.safe_update_status(
                        f"Loaded {len(self.duplicates)} duplicate groups from cache", "info"))
                    return
            except Exception as e:
                print(f"[WARNING] Failed to load cache: {e}")
        
        try:
            # First pass: collect all PDF files with progress
            self.safe_update_status("Scanning for PDF files...")
            
            # Get total number of PDFs for progress tracking
            pdf_files = list(self._find_pdf_files(folder, stop_event))
            total_pdfs = len(pdf_files)
            if total_pdfs == 0:
                self.safe_update_status(t('no_pdfs_found', self.lang))
                return
                
            # Configure thread pool based on system capabilities
            max_workers = min(32, (os.cpu_count() or 1) * 4)
            processed_count = 0
            
            self.safe_update_status(f"Found {total_pdfs} PDF files. Starting duplicate detection...")
            
            # Process files in batches to balance memory usage and performance
            batch_size = max(50, min(500, total_pdfs // 10))  # Dynamic batch size
            
            # Adjust thread pool size for low priority mode
            if hasattr(self, 'low_priority') and self.low_priority.get():
                max_workers = max(1, max_workers // 2)  # Use fewer threads in low priority mode
                
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Process files in batches
                for i in range(0, total_pdfs, batch_size):
                    if stop_event.is_set():
                        break
                        
                    batch = pdf_files[i:i + batch_size]
                    batch_futures = []
                    
                    # Submit batch for processing
                    for file_path in batch:
                        if stop_event.is_set():
                            break
                        future = executor.submit(
                            self._process_pdf_file,
                            file_path,
                            pdf_hash_map,
                            results_lock
                        )
                        batch_futures.append(future)
                    
                    # Process batch results
                    for future in as_completed(batch_futures):
                        if stop_event.is_set():
                            break
                            
                        result = future.result()
                        if result:  # Only process if we got a valid result
                            file_hash, file_path = result
                            with results_lock:
                                if file_hash in pdf_hash_map:
                                    pdf_hash_map[file_hash].append(file_path)
                                else:
                                    pdf_hash_map[file_hash] = [file_path]
                        
                        # Update progress
                        processed_count += 1
                        progress = (processed_count / total_pdfs) * 100
                        self.update_overall_progress(progress, 100)
                        self.update_status_details(f"Processed {processed_count}/{total_pdfs} files. Found {duplicate_counter} duplicates.")
                        
                        # Allow UI to update
                        if processed_count % 10 == 0:
                            self.root.update_idletasks()
                            
                    # After processing all files in batch, update duplicates list
                    with results_lock:
                        # Ensure we only keep lists of valid file paths
                        self.duplicates = []
                        for file_list in pdf_hash_map.values():
                            if len(file_list) > 1:  # Only consider groups with duplicates
                                # Ensure all items in the list are strings (file paths)
                                valid_files = [f for f in file_list if isinstance(f, str) and f.strip()]
                                if len(valid_files) > 1:  # Only add if we still have duplicates
                                    self.duplicates.append(valid_files)
                        duplicate_counter = len(self.duplicates)
            
            # Save to cache if enabled
            if cache_enabled and not stop_event.is_set():
                try:
                    # Prepare clean data for caching
                    clean_duplicates = []
                    for group in self.duplicates:
                        if isinstance(group, (list, tuple)):
                            clean_group = [f for f in group if isinstance(f, str) and f.strip()]
                            if len(clean_group) > 1:
                                clean_duplicates.append(clean_group)
                    
                    clean_file_info = []
                    for file_list in pdf_hash_map.values():
                        if isinstance(file_list, (list, tuple)):
                            clean_files = [f for f in file_list if isinstance(f, str) and f.strip()]
                            if clean_files:
                                clean_file_info.append(clean_files)
                    
                    cache_data = {
                        'folder': folder,
                        'timestamp': time.time(),
                        'duplicates': clean_duplicates,
                        'file_info': clean_file_info
                    }
                    
                    # Ensure cache directory exists
                    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                    
                    # Save to cache file
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                        
                except Exception as e:
                    print(f"[WARNING] Failed to save cache: {e}")
            
            # Final update
            if not stop_event.is_set():
                # Store all processed files for reference
                self.all_pdf_files = list(pdf_hash_map.values())
                
                # Update UI with results
                elapsed_time = time.time() - start_time
                time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                
                if duplicate_counter > 0:
                    self.show_status(
                        f"Found {duplicate_counter} duplicate(s) in {total_pdfs} files. "
                        f"Scan completed in {time_str}.",
                        "warning"
                    )
                else:
                    self.show_status(
                        f"No duplicates found in {total_pdfs} files. "
                        f"Scan completed in {time_str}.",
                        "success"
                    )

        except Exception as e:
            if self.is_searching:  # Only show error if search wasn't cancelled
                self.safe_update_status(f"Error during search: {str(e)}")
                print(f"Error in perform_search: {e}")
                import traceback
                traceback.print_exc()
                
                try:
                    messagebox.showerror(
                        t('error', self.lang) if hasattr(self, 'lang') else "Error", 
                        f"An error occurred while scanning: {str(e)}"
                    )
                except Exception as e:
                    print(f"Error showing error message: {e}")
        
        # Cleanup code that runs in all cases
        stop_event.set()
        self.is_searching = False
        
        try:
            self.find_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
            # Reset progress bar
            self.progress_bar['value'] = 0
            self.progress_bar['maximum'] = 100
            self.update_status_details("Ready")
            
            # Update UI
            self.root.update_idletasks()
            
            # Clean up any remaining resources
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                except Exception as e:
                    print(f"Error cleaning up temporary directory: {e}")
            
            # Store scan results if we have them
            if hasattr(self, 'all_pdf_files') and hasattr(self, 'duplicates'):
                try:
                    self.scan_results = {
                        'duplicates': self.duplicates,
                        'file_info': [self.get_pdf_info(path) for path in self.all_pdf_files],
                        'scan_time': time.time() - start_time,
                        'file_count': len(self.all_pdf_files),
                        'duplicate_count': len(self.duplicates)
                    }
                    
                    # Enable save button since we have results
                    if hasattr(self, 'save_btn'):
                        self.save_btn.config(state=tk.NORMAL)
                except Exception as e:
                    print(f"Error saving scan results: {e}")
            
            # Calculate elapsed time for status messages
            elapsed_time = time.time() - start_time
            time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            
            # Update status with results
            if not hasattr(self, 'duplicates') or not self.duplicates:
                status_msg = f"No duplicates found. Scanned {total_pdfs} files in {time_str}"
                self.show_status(status_msg, "success")
                
                if total_pdfs > 0 and hasattr(self, 'last_scan_folder') and self.last_scan_folder:
                    try:
                        messagebox.showinfo(
                            "Scan Complete",
                            f"No duplicate files found.\n\n"
                            f"Scanned {total_pdfs} files in {time_str}.",
                            detail=f"Folder: {os.path.basename(self.last_scan_folder)}"
                        )
                    except Exception as e:
                        print(f"Error showing completion message: {e}")
            else:
                dup_count = len(self.duplicates)
                status_msg = (f"Found {dup_count} duplicate(s) in {total_pdfs} files. "
                             f"Scan completed in {time_str}.")
                self.show_status(status_msg, "success" if dup_count == 0 else "warning")
                
                if hasattr(self, 'last_scan_folder') and self.last_scan_folder:
                    try:
                        messagebox.showinfo(
                            "Scan Complete",
                            f"Found {dup_count} duplicate file(s).\n\n"
                            f"Scanned {total_pdfs} files in {time_str}.",
                            detail=f"Folder: {os.path.basename(self.last_scan_folder)}"
                        )
                    except Exception as e:
                        print(f"Error showing completion message: {e}")
                        
        except Exception as e:
            print(f"Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
            if self.is_searching:  # Only cleanup if search wasn't cancelled
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.status_text.set("")
                self.is_searching = False

    def preview_selected(self):
        """Preview the selected file(s)."""
        selected_items = self.tree.selection()
        if not selected_items:
            self.show_status("No files selected for preview", "warning")
            return
            
        # For now, just preview the first selected file
        self.update_preview()

    def undo_last_delete(self):
        """Restore the most recently deleted files."""
        if not self.undo_stack:
            self.show_status("Nothing to undo", "info")
            return
            
        last_action = self.undo_stack.pop()
        if last_action['type'] != 'delete' or not last_action['files']:
            self.show_status("Nothing to undo", "info")
            return
            
        restored = 0
        failed = 0
        
        for file_info in last_action['files']:
            try:
                # Check if file exists in recycle bin/trash
                if not os.path.exists(file_info['path']):
                    # In a real app, you would restore from recycle bin here
                    # For now, we'll just skip and report as failed
                    failed += 1
                    continue
                    
                # Add back to tree view
                self.tree.insert(
                    "", "end", 
                    values=(file_info['path'], file_info['original']),
                    iid=file_info['item_id']
                )
                
                # Add back to duplicates list
                self.duplicates.append((file_info['path'], file_info['original']))
                restored += 1
                
            except Exception as e:
                print(f"Error undeleting {file_info['path']}: {e}")
                failed += 1
        
        # Update UI
        if restored > 0:
            self.show_status(f"Restored {restored} file(s)", "success")
            
            # Disable undo button if stack is empty
            if not self.undo_stack:
                self.menu_manager.update_undo_menu_item(tk.DISABLED)
        
        if failed > 0:
            self.show_status(
                f"Restored {restored} file(s), failed to restore {failed}",
                "warning"
            )
    
    # Recent folders menu is now handled by the RecentFolders class
    
    def add_to_recent_folders(self, folder_path):
        """
        Add a folder to the recent folders list.
        
        Args:
            folder_path: Path to the folder to add
        """
        if hasattr(self, 'recents') and self.recents and folder_path:
            self.recents.add_folder(folder_path)
    
    def clear_recent_folders(self):
        """
        Clear the recent folders list.
        
        Returns:
            bool: True if folders were cleared, False otherwise
        """
        if hasattr(self, 'recents') and self.recents:
            return self.recents.clear()
        return False
    
    def load_recent_folder(self, folder_path):
        """
        Load a folder from the recent folders list.
        
        Args:
            folder_path: Path to the folder to load
        """
        if not os.path.isdir(folder_path):
            self.show_status(f"Folder not found: {folder_path}", "error")
            # Let the RecentFolders class handle removing invalid paths
            self.recents.remove_invalid_paths()
            return
            
        # Update the folder path and trigger duplicate search
        self.folder_path.set(folder_path)
        self.find_duplicates()
        
        # Update the recent folders list with the newly loaded folder
        self.add_to_recent_folders(folder_path)
    
    def _setup_status_bar(self):
        """Set up the status bar and notification system."""
        # Status bar frame
        self.status_frame = ttk.Frame(self.root, padding="5 1 5 1")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status label
        self.status_text = tk.StringVar()
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_text,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Notification history button
        self.history_btn = ttk.Button(
            self.status_frame,
            text="⏱️",
            width=3,
            command=self.show_notification_history,
            style='TButton'
        )
        self.history_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Initialize recent folders
        from app_struct.recents import RecentFolders
        self.recents = RecentFolders(self)
        self.recents.on_folder_selected = self.load_recent_folder
        
        # Define message type styles
        self.message_styles = {
            'info': {'fg': '#000000', 'bg': '#e6f3ff', 'icon': 'ℹ️'},
            'success': {'fg': '#155724', 'bg': '#d4edda', 'icon': '✅'},
            'warning': {'fg': '#856404', 'bg': '#fff3cd', 'icon': '⚠️'},
            'error': {'fg': '#721c24', 'bg': '#f8d7da', 'icon': '❌'},
            'scanning': {'fg': '#004e8c', 'bg': '#cce4f7', 'icon': '⏳'},
            'progress': {'fg': '#0c5460', 'bg': '#d1ecf1', 'icon': '⏳'},
            'debug': {'fg': '#383d41', 'bg': '#e2e3e5', 'icon': '🐛'}
        }
        
        # Configure styles for different message types
        style = ttk.Style()
        for msg_type, style_info in self.message_styles.items():
            style.configure(f'{msg_type}.TFrame', background=style_info['bg'])
            style.configure(f'{msg_type}.TLabel', 
                          foreground=style_info['fg'], 
                          background=style_info['bg'])
    
    def show_status(self, message, message_type="info", timeout=5000, show_notification=True):
        """Show a status message with appropriate styling.
        
        Args:
            message (str): The message to display
            message_type (str): Type of message (info, success, warning, error, scanning, progress, debug)
            timeout (int): Time in milliseconds before message clears (0 for no timeout)
            show_notification (bool): Whether to add to notification history
        """
        if not hasattr(self, 'status_label') or not hasattr(self, 'status_text'):
            return
            
        # Get style for message type
        style = self.message_styles.get(message_type.lower(), self.message_styles['info'])
        
        # Update status label with timestamp and icon
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"{style['icon']} [{timestamp}] {message}"
        self.status_text.set(formatted_message)
        
        # Update styling
        self.status_label.config(
            foreground=style['fg'],
            background=style['bg']
        )
        self.status_frame.configure(style=f'{message_type}.TFrame')
        
        # Add to notification history
        if show_notification and message_type not in ('progress', 'scanning'):
            self._add_to_notification_history(formatted_message, message_type)
        
        # Schedule clearing the message
        if hasattr(self, '_status_timeout'):
            self.root.after_cancel(self._status_timeout)
            
        if timeout > 0 and message_type not in ('scanning', 'progress'):
            self._status_timeout = self.root.after(
                timeout, 
                self.clear_status
            )
            
        # Play sound for important notifications
        if message_type in ('error', 'warning') and self.settings.get('enable_sounds', True):
            self._play_notification_sound(message_type)
    
    def _add_to_notification_history(self, message, message_type):
        """Add a message to the notification history."""
        if not hasattr(self, 'notification_history'):
            self.notification_history = []
            
        # Add new message to beginning of list
        timestamp = datetime.now()
        self.notification_history.insert(0, {
            'message': message,
            'type': message_type,
            'timestamp': timestamp
        })
        
        # Trim history if needed
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[:self.max_history]
    
    def show_notification_history(self):
        """Show a window with notification history."""
        if not hasattr(self, 'notification_history') or not self.notification_history:
            messagebox.showinfo("Notification History", "No notifications in history.")
            return
            
        history_win = tk.Toplevel(self.root)
        history_win.title("Notification History")
        history_win.geometry("600x400")
        
        # Create a text widget with scrollbar
        frame = ttk.Frame(history_win)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text = tk.Text(
            frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add notifications to text widget
        text.config(state=tk.NORMAL)
        for idx, note in enumerate(self.notification_history):
            # Add separator between entries (except first one)
            if idx > 0:
                text.insert(tk.END, "\n" + "-" * 80 + "\n\n")
                
            # Format timestamp
            timestamp = note['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            
            # Get style for message type
            style = self.message_styles.get(note['type'], self.message_styles['info'])
            
            # Insert message with timestamp
            text.insert(tk.END, f"[{timestamp}]\n", 'timestamp')
            text.insert(tk.END, f"{note['message']}\n")
            
            # Configure tags for styling
            text.tag_configure('timestamp', font=('Segoe UI', 8, 'italic'), foreground='#666666')
            text.tag_configure(note['type'], 
                             foreground=style['fg'], 
                             background=style['bg'],
                             font=('Segoe UI', 10, 'bold'))
            
            # Apply style to the message
            text.tag_add(note['type'], f"{idx*3+2}.0", f"{idx*3+2}.end")
        
        # Add clear button
        btn_frame = ttk.Frame(history_win)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        clear_btn = ttk.Button(
            btn_frame,
            text="Clear History",
            command=lambda: self._clear_notification_history(history_win)
        )
        clear_btn.pack(side=tk.RIGHT)
        
        close_btn = ttk.Button(
            btn_frame,
            text="Close",
            command=history_win.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        text.config(state=tk.DISABLED)
        text.see(tk.END)
    
    def _clear_notification_history(self, window):
        """Clear the notification history."""
        if hasattr(self, 'notification_history'):
            self.notification_history = []
            window.destroy()
            self.show_status("Notification history cleared", "info")
            
        if hasattr(self, 'file_progress_label'):
            self.file_progress_label.config(text=t('current_file', self.lang) + ":")
        self.root.update_idletasks()

    def show_help(self):
        """Show the help window with user guide and instructions."""
        from app_struct.help import HelpWindow
        HelpWindow.show_help(self.root, self.lang)

    def load_settings(self):
        """
        Load application settings from config file.
        
        Returns:
            dict: Dictionary containing application settings
        """
        default_settings = {
            'theme': 'light',
            'lang': 'en',
            'recent_folders': [],
            'suppress_warnings': True,
            'check_updates': True,
            'tree_visible': True,
            'preview_visible': True,
            'quick_compare': False,
            'filters_visible': True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with default settings to ensure all keys exist
                    for key, value in default_settings.items():
                        if key not in loaded_settings:
                            loaded_settings[key] = value
                    return loaded_settings
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings: {e}")
                # If there's an error, return default settings and try to save them
                try:
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(default_settings, f, indent=4, ensure_ascii=False)
                except IOError as e:
                    print(f"Error creating default settings file: {e}")
        
        return default_settings

    def save_settings(self):
        """
        Save current settings to config file.
        
        Also ensures the settings directory exists before saving.
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Save current recent folders to settings before saving
            if hasattr(self, 'recents') and self.recents:
                self.settings['recent_folders'] = self.recents.get_recent_folders()
            
            # Save to file with pretty printing and unicode support
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
                
        except (IOError, OSError) as e:
            print(f"Error saving settings: {e}")
            # Try to show an error message to the user if possible
            if hasattr(self, 'show_status'):
                self.show_status(f"Failed to save settings: {e}", "error")

    def change_theme(self, theme_name):
        """Change the application theme."""
        self.theme_manager.apply_theme(theme_name)
        self.settings['theme'] = theme_name
        self.save_settings()

    def set_language(self, lang):
        """Change the application language."""
        self.lang = lang
        self.settings['language'] = lang
        self.save_settings()
        
        # Update UI elements with new language
        if hasattr(self, 'menu_bar'):
            self.menu_bar.destroy()
            self.menu_bar = self.create_menu()
            self.root.config(menu=self.menu_bar)
            
        # Update drag and drop manager language
        if hasattr(self, 'drag_drop_manager'):
            self.drag_drop_manager.set_language(lang)
            
        # Update any other UI elements that need language refresh
        self.refresh_language()

    def _restart_application(self):
        """Internal method to restart the application."""
        # Read the stored folder if it exists
        current_folder = None
        if os.path.exists('temp_folder.txt'):
            with open('temp_folder.txt', 'r') as f:
                current_folder = f.read().strip()
            try:
                os.remove('temp_folder.txt')
            except:
                pass
        
        # Destroy the current window
        self.root.destroy()
        
        # Create a new application instance
        main()

    def toggle_suppress_warnings(self):
        """Toggle PDF warning suppression and save the setting."""
        self.suppress_warnings = self.suppress_warnings_var.get()
        self.settings['suppress_warnings'] = self.suppress_warnings
        self.save_settings()
        
        if self.suppress_warnings:
            self.show_status("PDF warnings are now suppressed", "info")
        else:
            self.show_status("PDF warnings are now enabled", "info")
            
    def _setup_drag_drop(self):
        """Set up drag and drop functionality."""
        try:
            # Initialize drag and drop manager
            self.drag_drop_manager = DragDropManager(
                root=self.root,
                on_drop_callback=self._handle_dropped_folder,
                lang=self.lang if hasattr(self, 'lang') else 'en'
            )
            print("Drag and drop initialized successfully")
            
        except Exception as e:
            print(f"Warning: Could not set up drag and drop: {e}")

    def _handle_dropped_folder(self, folder_path):
        """Handle a dropped folder."""
        try:
            self.folder_path.set(folder_path)
            self.show_status(
                self.drag_drop_manager._get_translation('scanning_folder').format(folder_path), 
                "info"
            )
            self.add_to_recent_folders(folder_path)
            self.find_duplicates()
        except Exception as e:
            error_msg = f"Error processing dropped folder: {str(e)}"
            print(error_msg)
            self.show_status(error_msg, "error")
    
    def refresh_language(self):
        """Refresh the UI with the new language."""
    def update_preview(self):
        """Update the preview based on the selected item."""
        self.clear_preview()
        
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        file_path = item['values'][0]  # First column contains the file path
        
        if not os.path.exists(file_path):
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "File not found")
            self.preview_text.config(state=tk.DISABLED)
            return
            
        if self.preview_type.get() == "image":
            self.show_image_preview(file_path)
        else:
            self.show_text_preview(file_path)

    def clear_preview(self):
        """Clear the preview area."""
        if hasattr(self, 'current_preview_image'):
            self.current_preview_image = None
            self.preview_canvas.delete("all")
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)

    def show_image_preview(self, file_path):
        """Show an image preview of the PDF."""
        try:
            # Convert first page of PDF to image
            images = convert_from_path(file_path, first_page=1, last_page=1)
            if images:
                # Resize image to fit preview area
                width, height = self.preview_canvas.winfo_width(), self.preview_canvas.winfo_height()
                if width <= 1 or height <= 1:  # If canvas not yet sized
                    width, height = 400, 500  # Default size
                    
                image = images[0].resize((width, height), Image.Resampling.LANCZOS)
                self.current_preview_image = ImageTk.PhotoImage(image)
                self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.current_preview_image)
        except Exception as e:
            print(f"Error generating preview: {e}")
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Error generating preview: {str(e)}")
            self.preview_text.config(state=tk.DISABLED)
            
    def show_text_preview(self, file_path):
        """Show a text preview of the PDF."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                # Extract text from first page only for preview
                if len(pdf_reader.pages) > 0:
                    text = pdf_reader.pages[0].extract_text()
                    
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, text or "No text found in the first page")
                self.preview_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Error reading PDF: {str(e)}")
            self.preview_text.config(state=tk.DISABLED)

    def check_updates(self, force=False):
        """Check for application updates.
        
        Args:
            force: If True, force a check even if auto-updates are disabled
        """
        # Skip if auto-updates are disabled and this is not a manual check
        if not force and not self.settings.get('check_updates', True):
            return
            
        def run_update_check():
            try:
                # Get current version
                from app_struct.version import get_version
                current_version = get_version()
                
                # Check for updates
                update_available, version, url = check_for_updates(
                    parent=self.root if force else None,
                    current_version=current_version,
                    force_check=force
                )
                
                # If update is available, show dialog
                if update_available and version and url:
                    if messagebox.askyesno(
                        "Update Available",
                        f"A new version {version} is available.\n\n"
                        f"Current version: {current_version}\n"
                        f"New version: {version}\n\n"
                        "Would you like to download it now?",
                        parent=self.root if force else None
                    ):
                        import webbrowser
                        webbrowser.open(url)
                
                # If this was a manual check and no updates are available
                elif force:
                    messagebox.showinfo(
                        "No Updates",
                        f"You are using the latest version ({current_version}).",
                        parent=self.root
                    )
                        
            except Exception as e:
                logger.error(f"Error in update check: {e}")
                if force:  # Only show error if user manually checked
                    messagebox.showerror(
                        "Update Error",
                        f"Failed to check for updates: {str(e)}",
                        parent=self.root
                    )
        
        # Run update check in a separate thread to avoid freezing the UI
        thread = threading.Thread(target=run_update_check, daemon=True)
        thread.start()

    def on_startup(self):
        """Handle application startup tasks."""
        # Check for updates on startup (only if not checked recently)
        self.check_updates(force=False)

    def on_closing(self):
        """Handle window closing event."""
        if self.is_searching:
            self.is_searching = False
            self.after_cancel(self._after_id) if hasattr(self, '_after_id') else None
        
        # Save window position and size
        self.settings['window_geometry'] = self.root.geometry()
        self.save_settings()
        
        # Clean up resources
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Error cleaning up temporary directory: {e}")
        
        # Close the application
        self.root.quit()
        self.root.destroy()
        
    def toggle_suppress_warnings(self):
        """Toggle PDF warning suppression and save the setting."""
        self.suppress_warnings = self.suppress_warnings_var.get()
        self.settings['suppress_warnings'] = self.suppress_warnings
        self.save_settings()
        
        if self.suppress_warnings:
            self.show_status("PDF warnings are now suppressed", "info")
        else:
            self.show_status("PDF warnings are now enabled", "info")
            
    def find_duplicates(self):
        """Start the duplicate PDF finding process."""
        if not self.folder_path.get():
            self.show_status("Please select a folder first", "error")
            return
            
        if not os.path.isdir(self.folder_path.get()):
            self.show_status("Selected folder does not exist", "error")
            return
            
        if hasattr(self, 'is_searching') and self.is_searching:
            self.cancel_scan()
            return
            
        # Reset UI state
        self.duplicates = []
        self.all_pdf_files = []
        self.problematic_files = []
        if hasattr(self, 'tree'):
            self.tree.delete(*self.tree.get_children())
        if hasattr(self, 'clear_preview'):
            self.clear_preview()
        
        # Update UI
        self.is_searching = True
        if hasattr(self, 'find_btn'):
            self.find_btn.config(text=t('stop_scan', self.lang) if hasattr(t, 'stop_scan') else 'Stop Scan')
        if hasattr(self, 'stop_btn'):
            self.stop_btn.config(state=tk.NORMAL)
        if hasattr(self, 'save_btn'):
            self.save_btn.config(state=tk.DISABLED)
        
        # Start search in a separate thread
        self.search_thread = threading.Thread(
            target=self.perform_search,
            args=(self.folder_path.get(),),
            daemon=True
        )
        self.search_thread.start()
        
        # Start progress monitoring
        if hasattr(self, 'monitor_search'):
            self.monitor_search()
    
    def monitor_search(self):
        """Monitor the search thread and update UI."""
        if hasattr(self, 'search_thread') and self.search_thread.is_alive():
            # Update progress
            if hasattr(self, 'progress_var') and hasattr(self, 'progress_bar'):
                try:
                    # Get the integer value from the IntVar
                    progress_value = self.progress_var.get()
                    self.progress_bar['value'] = progress_value
                    self.progress_bar.update()
                except (AttributeError, tk.TclError) as e:
                    print(f"Error updating progress bar: {e}")
            
            # Check again after 100ms
            self.root.after(100, self.monitor_search)
        elif hasattr(self, 'is_searching') and self.is_searching:
            # Search completed normally
            self.is_searching = False
            if hasattr(self, 'find_btn'):
                self.find_btn.config(text=t('find_duplicates', self.lang))
            if hasattr(self, 'stop_btn'):
                self.stop_btn.config(state=tk.DISABLED)
            
            # Update UI with results
            if hasattr(self, '_update_results_ui'):
                self._update_results_ui()
    
    def cancel_scan(self):
        """Cancel the current scan operation."""
        if hasattr(self, 'is_searching') and self.is_searching:
            self.is_searching = False
            self.show_status("Cancelling scan...", "warning")
            
            # Stop any running threads
            if hasattr(self, 'search_thread') and self.search_thread.is_alive():
                # Set stop event if it exists
                if hasattr(self, 'stop_event'):
                    self.stop_event.set()
                
                # Wait for thread to finish (with timeout)
                self.search_thread.join(timeout=2.0)
                
                if self.search_thread.is_alive():
                    print("Warning: Search thread did not stop gracefully")
            
            # Reset UI
            if hasattr(self, 'find_btn'):
                self.find_btn.config(text=t('find_duplicates', self.lang))
            if hasattr(self, 'stop_btn'):
                self.stop_btn.config(state=tk.DISABLED)
            self.show_status("Scan cancelled", "info")
    
    def _update_results_ui(self):
        """Update the UI with the scan results."""
        if not hasattr(self, 'duplicates') or not self.duplicates:
            self.show_status("No duplicates found", "success")
            return
            
        # Clear existing items
        if hasattr(self, 'tree'):
            self.tree.delete(*self.tree.get_children())
        
        # Add duplicates to treeview
        for dup_group in self.duplicates:
            if not dup_group or len(dup_group) < 2:
                continue
                
            # Sort by file size (descending) and modification time (newest first)
            dup_group.sort(
                key=lambda x: (
                    os.path.getsize(x) if os.path.exists(x) else 0,
                    os.path.getmtime(x) if os.path.exists(x) else 0
                ),
                reverse=True
            )
            
            # Get original file info (first in the sorted list)
            original_path = dup_group[0]
            original_size = os.path.getsize(original_path) if os.path.exists(original_path) else 0
            original_mtime = os.path.getmtime(original_path) if os.path.exists(original_path) else 0
            original_date = datetime.fromtimestamp(original_mtime).strftime('%Y-%m-%d %H:%M:%S') if original_mtime > 0 else 'Unknown'
            
            # Add to treeview
            for i, file_path in enumerate(dup_group):
                try:
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
                    file_date = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S') if file_mtime > 0 else 'Unknown'
                    
                    # Calculate size difference from original
                    size_diff = ""
                    if i > 0 and original_size > 0:
                        diff_percent = ((file_size - original_size) / original_size) * 100
                        size_diff = f"{diff_percent:+.2f}%"
                    
                    # Calculate date difference from original
                    date_diff = ""
                    if i > 0 and original_mtime > 0 and file_mtime > 0:
                        diff_days = (file_mtime - original_mtime) / (24 * 3600)
                        if abs(diff_days) >= 1:
                            date_diff = f"{diff_days:+.1f} days"
                        else:
                            diff_hours = diff_days * 24
                            date_diff = f"{diff_hours:+.1f} hours"
                    
                    # Mark the first file as the "original" (largest file, newest)
                    is_original = (i == 0)
                    
                    if hasattr(self, 'tree'):
                        self.tree.insert(
                            '', 'end',
                            values=(
                                os.path.basename(file_path),  # Duplicate file name
                                f"{file_size / (1024 * 1024):.2f} MB" if file_size > 0 else "0 MB",  # Size
                                file_date,  # Modification date
                                size_diff,  # Size difference from original
                                date_diff,  # Date difference from original
                                os.path.basename(original_path),  # Original file name
                                f"{original_size / (1024 * 1024):.2f} MB" if original_size > 0 else "0 MB",  # Original size
                                original_date,  # Original modification date
                                file_path  # Full path (hidden)
                            ),
                            tags=('original' if is_original else 'duplicate')
                        )
                except Exception as e:
                    print(f"Error adding file to treeview: {e}")
                    
            # Add a separator between groups
            if hasattr(self, 'tree'):
                self.tree.insert('', 'end', values=('',) * 9, tags=('separator',))
        
        # Configure tag colors if tree exists
        if hasattr(self, 'tree'):
            self.tree.tag_configure('original', background='#e6f7e6')  # Light green for original
            self.tree.tag_configure('duplicate', background='#f9f9f9')  # Light gray for duplicates
            self.tree.tag_configure('separator', background='#cccccc')  # Gray for separators
        
        # Update status
        dup_count = len(self.duplicates) if hasattr(self, 'duplicates') else 0
        self.show_status(
            f"Found {dup_count} group(s) of duplicate files",
            "success" if dup_count == 0 else "warning"
        )
        
        # Enable save button
        if hasattr(self, 'save_btn'):
            self.save_btn.config(state=tk.NORMAL if dup_count > 0 else tk.DISABLED)
    
    def save_scan_results(self):
        """Save scan results to a CSV file using ScanManager."""
        try:
            # Passa esplicitamente i duplicati al gestore di scansione
            if not hasattr(self, 'duplicates') or not self.duplicates:
                self.show_status("No scan results to save", "warning")
                return False
                
            # Assicurati che il gestore di scansione abbia i duplicati correnti
            self.scan_manager.duplicates = self.duplicates
            
            # Salva i risultati
            result = self.scan_manager.save_scan_results()
            
            if result:
                self.show_status("Scan results saved successfully", "success")
            return result
            
        except Exception as e:
            error_msg = f"Error saving scan results: {str(e)}"
            print(f"ERROR: {error_msg}")
            print("Traceback:", traceback.format_exc())
            if hasattr(self, 'show_status'):
                self.show_status(error_msg, "error")
            messagebox.showerror("Save Error", error_msg)
            return False
            
    def load_scan_results(self):
        """Load scan results from a previously saved CSV file using ScanManager."""
        try:
            # Delegate to ScanManager to handle loading
            result = self.scan_manager.load_scan_results()
            
            if result is not None:
                duplicates, all_pdf_files, problematic_files = result
                
                # Update application state
                self.duplicates = duplicates
                self.all_pdf_files = all_pdf_files
                self.problematic_files = problematic_files
                
                # Update UI
                if hasattr(self, 'tree'):
                    self.tree.delete(*self.tree.get_children())
                self._update_results_ui()
                
                # Show success message
                self.show_status(f"Loaded {len(duplicates)} duplicate groups from file", "success")
                return True
            return False
                
        except Exception as e:
            error_msg = f"Error loading scan results: {str(e)}"
            print(f"ERROR: {error_msg}")
            print("Traceback:", traceback.format_exc())
            if hasattr(self, 'show_status'):
                self.show_status(error_msg, "error")
            messagebox.showerror("Load Error", error_msg)
            return False
    
    def show_problematic_files(self):
        """Show a dialog with files that had issues during processing."""
        if not hasattr(self, 'problematic_files') or not self.problematic_files:
            messagebox.showinfo("No Issues", "No problematic files found.")
            return
            
        # Create a dialog to show problematic files
        dialog = tk.Toplevel(self.root)
        dialog.title("Problematic Files")
        dialog.geometry("600x400")
        
        # Add a text widget to display the files
        text = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Insert the list of problematic files
        text.insert(tk.END, "The following files had issues during processing:\n\n")
        for file_path, error in self.problematic_files:
            text.insert(tk.END, f"• {file_path}\n")
            text.insert(tk.END, f"  Error: {error}\n\n")
        
        # Disable text widget
        text.config(state=tk.DISABLED)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(dialog, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        
        # Add a close button
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        close_button = ttk.Button(button_frame, text="Close", command=dialog.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)

def main():
    # Use TkinterDnD's Tk
    root = TkinterDnD.Tk()
    
    # Set application icon
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            myappid = 'com.github.nsfr750.pdfduplicatefinder'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        # Try to load the icon from the executable directory
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not set window icon: {e}")
    
    # Create and run the application
    app = PDFDuplicateApp(root)
    
    # Check for stored folder path
    if os.path.exists('temp_folder.txt'):
        try:
            with open('temp_folder.txt', 'r') as f:
                folder = f.read().strip()
                if os.path.exists(folder):
                    app.folder_path.set(folder)
            os.remove('temp_folder.txt')
        except Exception as e:
            print(f"Error loading stored folder: {e}")
    
    # Drag and drop is now handled by DragDropManager
    
    # Handle window close event
    def on_closing():
        # Clean up any temporary files
        if os.path.exists('temp_folder.txt'):
            try:
                os.remove('temp_folder.txt')
            except:
                pass
                
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            app.on_closing()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Schedule the startup tasks to run after the main window is displayed
    root.after(1000, app.on_startup)
    
    # Start the main loop
    root.mainloop()

def test_filters():
    """Test the filter functionality with sample data."""
    # Create a test app instance
    root = tk.Tk()
    app = PDFDuplicateApp(root)
    
    # Test data
    test_files = [
        {'path': 'test1.pdf', 'size': 1024, 'mtime': 1625000000, 'pages': 10},  # 1KB
        {'path': 'test2.pdf', 'size': 2048, 'mtime': 1625086400, 'pages': 5},   # 2KB
        {'path': 'test3.pdf', 'size': 5120, 'mtime': 1625172800, 'pages': 20}   # 5KB
    ]
    
    # Enable filters
    app.filters_active.set(True)
    
    # Test 1: Size filter
    print("\n=== Testing Size Filter ===")
    app.size_min_var.set('1.5')
    app.size_max_var.set('3')
    for file in test_files:
        result = app.apply_filters(file)
        print(f"File: {file['path']} - Size: {file['size']/1024:.1f}KB - Passes: {result}")
    
    # Test 2: Date filter
    print("\n=== Testing Date Filter ===")
    app.date_from_var.set('2021-06-29')
    app.date_to_var.set('2021-06-30')
    for file in test_files:
        result = app.apply_filters(file)
        mtime_str = datetime.datetime.fromtimestamp(file['mtime']).strftime('%Y-%m-%d')
        print(f"File: {file['path']} - Date: {mtime_str} - Passes: {result}")
    
    # Test 3: Page count filter
    print("\n=== Testing Page Count Filter ===")
    app.pages_min_var.set('5')
    app.pages_max_var.set('15')
    for file in test_files:
        result = app.apply_filters(file)
        print(f"File: {file['path']} - Pages: {file['pages']} - Passes: {result}")
    
    root.destroy()

if __name__ == "__main__":
    import sys
    
    if '--test-filters' in sys.argv:
        test_filters()
    else:
        main()