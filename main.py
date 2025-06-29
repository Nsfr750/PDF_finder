import os
import hashlib
import tempfile
import json
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
    import send2trash
except ImportError:
    send2trash = None
    print("Note: send2trash module not found. Using standard file deletion.")
    print("Install with: pip install send2trash")


class PDFDuplicateApp:
    def __init__(self, root):
        self.root = root
        
        # Initialize cache directory
        self.cache_dir = os.path.join(os.path.expanduser('~'), '.pdf_duplicate_finder')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Add cache settings
        self.use_cache = tk.BooleanVar(value=True)
        self.low_priority = tk.BooleanVar(value=False)
        
        # Set window title with version
        self.root.title("PDF Duplicate Finder")
        self.root.geometry('1600x900')
        # Initialize color theme variables
        self.primary_color = "#007bff"
        self.secondary_color = "#0056b3"
        self.text_color = "#000000"
        self.bg_color = "#f8f9fa"
        
        # Set window icon if available
        try:
            self.root.iconbitmap('icon.ico')
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
        
        # Set up the UI without menu first
        self._setup_ui()
        
        # Set up drag and drop
        self._setup_drag_drop()
        
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
        self.min_size = tk.IntVar(self.root, value=0)
        self.max_size = tk.IntVar(self.root, value=100000)  # 100MB default max
        self.ignore_small = tk.BooleanVar(self.root, value=False)
        self.ignore_large = tk.BooleanVar(self.root, value=False)
        self.ignore_blank = tk.BooleanVar(self.root, value=True)
        self.ignore_small_size = tk.IntVar(self.root, value=5)  # 5KB
        self.ignore_large_size = tk.IntVar(self.root, value=50000)  # 50MB
        
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
        
        # Filter variables
        self.filter_size_min = tk.StringVar(self.root)
        self.filter_size_max = tk.StringVar(self.root)
        self.filter_date_from = tk.StringVar(self.root)
        self.filter_date_to = tk.StringVar(self.root)
        self.filter_pages_min = tk.StringVar(self.root)
        self.filter_pages_max = tk.StringVar(self.root)
        self.filters_active = tk.BooleanVar(self.root, value=False)
        
        # Other UI state variables
        self.recent_folders = self.settings.get('recent_folders', [])
        self.max_recent_folders = 10
        self.undo_stack = []
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
        selection = self.tree.selection()
        if not selection:
            return
            
        # Get the selected item
        item = self.tree.item(selection[0])
        
        # Update preview if preview area exists
        if hasattr(self, 'preview_text'):
            self.update_preview()

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
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame for controls and treeview
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind F5 to refresh
        self.root.bind('<F5>', lambda e: self.find_duplicates() if self.folder_path.get() else None)
        self.root.bind('<Control-z>', lambda e: self.undo_last_delete() if hasattr(self, 'menu_manager') and hasattr(self.menu_manager, 'undo_menu_item') and self.menu_manager.undo_menu_item['state'] == tk.NORMAL else None)
        
        # Enable drag and drop with tkinterdnd2
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        self.root.dnd_bind('<<DropEnter>>', self.on_drop_enter)
        self.root.dnd_bind('<<DropLeave>>', self.on_drop_leave)
        
        # Store drop target highlight
        self.drop_highlight = None
        
        # Apply saved theme
        self.change_theme(self.settings.get('theme', 'light'))

        # Main container for search controls and results
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add drop target highlight (initially hidden)
        self.drop_highlight = ttk.Label(
            main_container, 
            text=t('drop_folder_here', self.lang), 
            background='#e6f3ff', 
            foreground='#0066cc',
            relief='solid',
            borderwidth=2
        )
        self.drop_highlight.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.8, relheight=0.8)
        self.drop_highlight.place_forget()  # Hide by default

        # Left side - Search controls and tree
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Search controls at the top of left frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)

        # Move search controls to search frame
        tk.Label(search_frame, text=t('select_folder', self.lang), font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.folder_path, width=50, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text=t('browse', self.lang), command=self.browse_folder, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Search buttons frame
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Buttons frame for find/stop
        action_frame = ttk.Frame(button_frame)
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
                 
        # Save results button
        self.save_btn = tk.Button(button_frame, text=t('save_results', self.lang), command=self.save_scan_results,
                               font=("Arial", 10), state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Load results button
        tk.Button(button_frame, text=t('load_results', self.lang), command=self.load_scan_results,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # Progress bar and status below search controls
        self.progress_frame = ttk.Frame(left_frame)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        # Filters section
        filter_frame = ttk.LabelFrame(left_frame, text=t('filters', self.lang))
        filter_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Size filter
        size_frame = ttk.LabelFrame(filter_frame, text=t('file_size_kb', self.lang))
        size_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(size_frame, text=t('min', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(size_frame, textvariable=self.filter_size_min, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(size_frame, text="-").pack(side=tk.LEFT, padx=2)
        ttk.Entry(size_frame, textvariable=self.filter_size_max, width=8).pack(side=tk.LEFT, padx=2)
        
        # Date filter
        date_frame = ttk.LabelFrame(filter_frame, text=t('modified_date', self.lang))
        date_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(date_frame, text=t('from', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(date_frame, textvariable=self.filter_date_from, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Label(date_frame, text=t('to', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(date_frame, textvariable=self.filter_date_to, width=10).pack(side=tk.LEFT, padx=2)
        
        # Page count filter
        page_frame = ttk.LabelFrame(filter_frame, text=t('page_count', self.lang))
        page_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(page_frame, text=t('min', self.lang) + ":").pack(side=tk.LEFT, padx=2)
        ttk.Entry(page_frame, textvariable=self.filter_pages_min, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(page_frame, text="-").pack(side=tk.LEFT, padx=2)
        ttk.Entry(page_frame, textvariable=self.filter_pages_max, width=5).pack(side=tk.LEFT, padx=2)
        
        # Filter toggle button
        ttk.Checkbutton(
            filter_frame, 
            text=t('enable_filters', self.lang), 
            variable=self.filters_active,
            command=self.toggle_filters
        ).pack(pady=5)
        
        # Compare mode selection
        compare_frame = ttk.LabelFrame(left_frame, text=t('compare_mode', self.lang))
        compare_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Radiobutton(
            compare_frame, 
            text=t('full_compare', self.lang), 
            variable=self.compare_mode,
            value="full"
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(
            compare_frame, 
            text=t('quick_compare', self.lang), 
            variable=self.compare_mode,
            value="quick"
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Batch processing controls
        batch_frame = ttk.LabelFrame(left_frame, text=t('processing_options', self.lang))
        batch_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Batch size control
        ttk.Label(batch_frame, text=t('batch_size', self.lang) + ":").pack(side=tk.LEFT, padx=5)
        self.batch_size_var = IntVar(value=self.batch_size)
        batch_slider = Scale(batch_frame, from_=1, to=50, orient=HORIZONTAL, 
                           variable=self.batch_size_var, showvalue=1, length=200)
        batch_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Worker threads control
        ttk.Label(batch_frame, text=t('threads', self.lang) + ":").pack(side=tk.LEFT, padx=5)
        self.workers_var = IntVar(value=self.max_workers)
        workers_slider = Scale(batch_frame, from_=1, to=os.cpu_count() or 4, orient=HORIZONTAL,
                             variable=self.workers_var, showvalue=1, length=100)
        workers_slider.pack(side=tk.LEFT, padx=5, fill=tk.X)
        
        # Cache and low-priority mode controls
        cache_frame = ttk.LabelFrame(left_frame, text=t('cache_and_priority', self.lang))
        cache_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Cache toggle
        ttk.Checkbutton(
            cache_frame, 
            text=t('enable_cache', self.lang), 
            variable=self.use_cache,
            command=self.clear_cache_if_needed
        ).pack(side=tk.LEFT, padx=5)
        
        # Low-priority mode toggle
        ttk.Checkbutton(
            cache_frame, 
            text=t('low_priority_mode', self.lang), 
            variable=self.low_priority
        ).pack(side=tk.LEFT, padx=5)
        
        # Progress bars frame
        progress_bars_frame = ttk.Frame(self.progress_frame)
        progress_bars_frame.pack(fill=tk.X, pady=2)
        
        # Overall progress bar
        self.progress_bar = ttk.Progressbar(progress_bars_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 2))
        
        # Individual file progress bar
        self.file_progress_frame = ttk.Frame(progress_bars_frame)
        self.file_progress_frame.pack(fill=tk.X, pady=(0, 2))
        
        self.file_progress_label = ttk.Label(self.file_progress_frame, text=t('current_file', self.lang) + ":")
        self.file_progress_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_progress_bar = ttk.Progressbar(self.file_progress_frame, mode='determinate')
        self.file_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status label
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_text)
        self.status_label.pack(pady=2)
        
        # Status details label
        self.status_details = ttk.Label(self.progress_frame, text="", wraplength=600, justify=tk.LEFT)
        self.status_details.pack(fill=tk.X, pady=(0, 5))
        
        # Configure progress bars
        self.progress_bar.configure(maximum=100, variable=self.overall_progress_var)
        self.file_progress_bar.configure(maximum=100, variable=self.progress_var)
        self.current_file = ""
        
        # Create tree frame for results
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Configure and pack tree in its frame
        self.tree = ttk.Treeview(tree_frame, columns=("dup_path", "dup_size", "dup_date", "orig_path", "orig_size", "orig_date"), 
                               show="headings", height=15, selectmode='extended')
        
        # Configure columns
        columns = [
            ("dup_path", t('duplicate_file', self.lang), 300, 'w'),  # 'w' for west (left)
            ("dup_size", t('size_kb', self.lang), 80, 'e'),      # 'e' for east (right)
            ("dup_date", t('modified', self.lang), 150, 'w'),     # 'w' for west (left)
            ("orig_path", t('original_file', self.lang), 300, 'w'), # 'w' for west (left)
            ("orig_size", t('size_kb', self.lang), 80, 'e'),     # 'e' for east (right)
            ("orig_date", t('modified', self.lang), 150, 'w')      # 'w' for west (left)
        ]
        
        for col_id, heading, width, anchor in columns:
            self.tree.heading(col_id, text=heading, command=lambda c=col_id: self.tree_sort_column(c, False))
            self.tree.column(col_id, width=width, anchor=anchor)
        
        # Store sort state
        self.tree_sort_column_id = None
        self.tree_sort_reverse = False
        
        # Add scrollbars to tree
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        # Pack scrollbars and tree
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind tree selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Right frame for preview
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Preview options
        preview_options = ttk.Frame(right_frame)
        preview_options.pack(fill=tk.X, pady=(0, 5))
        ttk.Radiobutton(preview_options, text=t('image_preview', self.lang), variable=self.preview_type, 
                        value="image", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(preview_options, text=t('text_preview', self.lang), variable=self.preview_type, 
                        value="text", command=self.update_preview).pack(side=tk.LEFT, padx=5)

        # Preview area
        preview_container = ttk.Frame(right_frame, relief="solid", borderwidth=1)
        preview_container.pack(fill=tk.BOTH, expand=True)

        # Canvas for image preview
        self.preview_canvas = tk.Canvas(preview_container, bg="white")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)

        # Text widget for text preview
        self.preview_text = tk.Text(preview_container, wrap=tk.WORD, font=("Arial", 10))
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.pack_forget()

        # Buttons frame for delete and preview
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Preview button
        preview_btn = ttk.Button(
            button_frame,
            text=t('preview', self.lang),
            command=self.preview_selected,
            style='Accent.TButton'  # Make it stand out
        )
        preview_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Delete button
        delete_btn = ttk.Button(
            button_frame,
            text=t('delete_selected', self.lang),
            command=self.delete_selected,
            style='Danger.TButton'  # Use a red button for delete
        )
        delete_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
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
    def update_status_details(self, message):
        """Update the status text with detailed information."""
        if not self.is_searching:
            return
            
        self.status_text.set(message)
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

    def on_drop_enter(self, event):
        """Handle drag enter event."""
        if self.drop_highlight:
            self.drop_highlight.lift()
            self.drop_highlight.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.8, relheight=0.8)
        return 'copy'
    
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
                logger.warning(f"{os.path.basename(file_path)} - {error_msg}")
                self.problematic_files.append(file_info)
                return file_info
                
        except Exception as e:
            error_msg = f"Error getting file info: {type(e).__name__} - {str(e)}"
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
            
        except Exception as e:
            print(f"[ERROR] Error calculating hash for {file_path}: {e}")
            return None

    def toggle_filters(self):
        """Toggle the enabled state of filter controls."""
        state = 'normal' if self.filters_active.get() else 'disabled'
        
        # Get all filter widgets and change their state
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Entry, ttk.Combobox)) and 'filter' in str(widget):
                widget.state([state])
        
        # Update status
        if self.filters_active.get():
            self.status_text.set("Filters enabled. Only matching files will be processed.")
        else:
            self.status_text.set("Filters disabled. All files will be processed.")
            
        # Force UI update
        self.root.update_idletasks()
        
    def _set_process_priority(self):
        """Set process priority based on settings."""
        if hasattr(self, 'low_priority') and self.low_priority.get():
            try:
                import psutil
                p = psutil.Process()
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            except (ImportError, AttributeError):
                # Fallback for non-Windows or if psutil not available
                try:
                    import os
                    os.nice(10)  # Lower priority on Unix-like systems
                except (AttributeError, ImportError):
                    pass
    
    def clear_cache(self):
        """Clear all cached scan results."""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.startswith('scan_cache_') and filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
            self.show_status("Cache cleared", "info")
        except Exception as e:
            self.show_status(f"Failed to clear cache: {e}", "error")
    
    def clear_cache_if_needed(self):
        """Clear cache if it was disabled and is being re-enabled."""
        if not hasattr(self, '_cache_was_disabled'):
            self._cache_was_disabled = not self.use_cache.get()
            return
            
        if self._cache_was_disabled and self.use_cache.get():
            if messagebox.askyesno(
                "Clear Cache",
                "Would you like to clear the existing cache when re-enabling it?"
            ):
                self.clear_cache()
        self._cache_was_disabled = not self.use_cache.get()
    
    def _process_pdf_file(self, file_path, hash_map, lock):
        """Process a single PDF file and update the hash map."""
        if not self.is_searching:
            return None
            
        # Set process priority for this thread if in low priority mode
        if hasattr(self, 'low_priority') and self.low_priority.get():
            self._set_process_priority()
            
        try:
            # Get file info first
            file_info = self.get_pdf_info(file_path)
            if not file_info:
                return None
                
            # Calculate hash
            file_hash = self.calculate_pdf_hash(file_info)
            if not file_hash:
                return None, None
                
            # Update results thread-safely
            with results_lock:
                if file_hash in hash_map:
                    original_file = hash_map[file_hash]['path']
                    return file_path, original_file
                else:
                    hash_map[file_hash] = file_info
                    return None, None
                    
        except Exception as e:
            print(f"[ERROR] Error processing {file_path}: {e}")
            return None, None

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
        
        if cache_enabled and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                if cache_data.get('folder') == folder:
                    cache_time = os.path.getmtime(cache_file)
                    folder_mtime = max(os.path.getmtime(root) for root, _, _ in os.walk(folder))
                    
                    if cache_time > folder_mtime:
                        self.safe_update_status("Loading results from cache...")
                        self.duplicates = cache_data.get('duplicates', [])
                        self.all_pdf_files = cache_data.get('file_info', [])
                        self._update_results_ui()
                        self.safe_update_status("Results loaded from cache")
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
                            
                        duplicate = future.result()
                        if duplicate and duplicate[0] and duplicate[1]:
                            with results_lock:
                                self.duplicates.append(duplicate)
                                duplicate_counter += 1
                        
                        # Update progress
                        processed_count += 1
                        progress = (processed_count / total_pdfs) * 100
                        self.update_overall_progress(progress, 100)
                        self.update_status_details(f"Processed {processed_count}/{total_pdfs} files. Found {duplicate_counter} duplicates.")
                        
                        # Allow UI to update
                        if processed_count % 10 == 0:
                            self.root.update_idletasks()
            
            # Save to cache if enabled
            if cache_enabled and not stop_event.is_set():
                try:
                    cache_data = {
                        'folder': folder,
                        'timestamp': time.time(),
                        'duplicates': self.duplicates,
                        'file_info': list(pdf_hash_map.values())
                    }
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f)
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
        
    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.show_status("No files selected for deletion", "warning")
            return
            
        # Ask for confirmation
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_items)} file(s)?\n\n"
            "This action cannot be undone.",
            icon='warning'
        ):
            self.show_status("Deletion cancelled", "info")
            return

        deleted_files = []
        failed_deletions = []
        
        for item in selected_items:
            file_path = self.tree.item(item)['values'][0]  # Get file path from first column
            try:
                # Add to undo stack before deleting
                if not hasattr(self, 'undo_stack'):
                    self.undo_stack = []
                
                # Store file info for potential undo
                file_info = {
                    'path': file_path,
                    'values': self.tree.item(item)['values']
                }
                
                # Try to use send2trash if available, otherwise use os.remove
                if send2trash is not None:
                    send2trash(file_path)
                else:
                    os.remove(file_path)
                
                # Remove from tree
                self.tree.delete(item)
                deleted_files.append(file_info)
                
                # Remove from duplicates list if it exists there
                if hasattr(self, 'duplicates'):
                    self.duplicates = [d for d in self.duplicates if d[0] != file_path]
                
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
                failed_deletions.append((file_path, str(e)))
        
        # Add to undo stack if any files were deleted
        if deleted_files:
            self.undo_stack.append({
                'type': 'delete',
                'files': deleted_files,
                'timestamp': time.time()
            })
            
            # Limit undo stack size
            if len(self.undo_stack) > self.max_undo_steps:
                self.undo_stack.pop(0)
            
            # Enable undo menu item
            if hasattr(self, 'menu_manager') and hasattr(self.menu_manager, 'update_undo_menu_item'):
                self.menu_manager.update_undo_menu_item(tk.NORMAL)
        
        # Show status message
        if deleted_files and not failed_deletions:
            self.show_status(f"Deleted {len(deleted_files)} file(s)", "success")
        elif deleted_files and failed_deletions:
            self.show_status(
                f"Deleted {len(deleted_files)} file(s), "
                f"failed to delete {len(failed_deletions)}",
                "warning"
            )
        else:
            self.show_status("Failed to delete selected files", "error")
            
        # Log any failures
        for file_path, error in failed_deletions:
            print(f"Error deleting {file_path}: {error}")
    
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
    
    def update_recent_folders_menu(self):
        """Update the recent folders menu with current list."""
        if not hasattr(self, 'menu_manager') or not hasattr(self.menu_manager, 'recent_menu'):
            return
            
        # Clear current items
        self.menu_manager.recent_menu.delete(0, 'end')
        
        if not self.recent_folders:
            self.menu_manager.recent_menu.add_command(
                label=t('no_recent_folders', self.lang),
                state=tk.DISABLED
            )
            return
            
        for i, folder in enumerate(self.recent_folders, 1):
            # Show only the last 2 parts of the path for brevity
            display_path = os.path.join(*Path(folder).parts[-2:]) if len(Path(folder).parts) > 1 else folder
            
            self.menu_manager.recent_menu.add_command(
                label=f"{i}. {display_path}",
                command=lambda f=folder: self.load_recent_folder(f),
                accelerator=f"Ctrl+{i}" if i <= 9 else ""
            )
            
            # Add keyboard shortcuts (Ctrl+1 to Ctrl+9)
            if i <= 9:
                self.root.bind(f'<Control-Key-{i}>', 
                    lambda e, f=folder: self.load_recent_folder(f))
        
        # Add separator and clear option
        self.menu_manager.recent_menu.add_separator()
        self.menu_manager.recent_menu.add_command(
            label=t('clear_recent_folders', self.lang),
            command=self.clear_recent_folders
        )
    
    def load_recent_folder(self, folder_path):
        """Load a folder from the recent folders list."""
        if not os.path.isdir(folder_path):
            self.show_status(f"Folder not found: {folder_path}", "error")
            # Remove non-existent folder from recent list
            self.recent_folders = [f for f in self.recent_folders if f != folder_path]
            self.update_recent_folders_menu()
            return
            
        self.folder_path.set(folder_path)
        self.find_duplicates()
    
    def clear_recent_folders(self):
        """Clear the recent folders list."""
        if self.recent_folders:
            if messagebox.askyesno(
                "Clear Recent Folders",
                "Are you sure you want to clear the recent folders list?"
            ):
                self.recent_folders = []
                self.update_recent_folders_menu()
                self.show_status("Recent folders cleared", "info")
    
    def add_to_recent_folders(self, folder_path):
        """Add a folder to the recent folders list."""
        if not folder_path:
            return
            
        # Remove if already in list
        self.recent_folders = [f for f in self.recent_folders if f != folder_path]
        
        # Add to beginning of list
        self.recent_folders.insert(0, folder_path)
        
        # Trim to max length
        if len(self.recent_folders) > self.max_recent_folders:
            self.recent_folders = self.recent_folders[:self.max_recent_folders]
        
        # Update settings
        self.settings['recent_folders'] = self.recent_folders
        self.save_settings()
        
        # Update menu
        self.update_recent_folders_menu()
    
    def show_status(self, message, message_type="info", timeout=5000):
        """Show a status message with appropriate styling."""
        # Set text and color based on message type
        colors = {
            'info': ('#000000', '#e6f3ff'),  # Black on light blue
            'success': ('#155724', '#d4edda'),  # Dark green on light green
            'warning': ('#856404', '#fff3cd'),  # Dark yellow on light yellow
            'error': ('#721c24', '#f8d7da'),    # Dark red on light red
            'scanning': ('#004e8c', '#cce4f7')  # Dark blue on light blue
        }
        
        fg, bg = colors.get(message_type.lower(), ('#000000', '#e6f3ff'))
        
        # Update status label
        self.status_text.set(message)
        self.status_label.config(foreground=fg)
        
        # Update status bar background
        self.status_label.master.configure(style=f'{message_type}.TFrame' if message_type != 'info' else 'TFrame')
        
        # Schedule clearing the message
        if hasattr(self, '_status_timeout'):
            self.root.after_cancel(self._status_timeout)
        
        if timeout > 0 and message_type not in ('scanning',):
            self._status_timeout = self.root.after(
                timeout, 
                lambda: self.clear_status() if message_type != 'scanning' else None
            )
    
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

    def show_help(self):
        # For brevity, this help text is not translated in detail. You can add translation keys for each section if desired.
        help_text = (
            f"{t('app_title', self.lang)}\n\n"
            "Features:\n"
            f"1. {t('find_duplicates', self.lang)} based on content\n"
            f"2. {t('image_preview', self.lang)}/{t('text_preview', self.lang)}\n"
            f"3. {t('delete_selected', self.lang)}\n\n"
            "How to Use:\n"
            f"1. {t('select_folder', self.lang)}\n"
            f"2. Click '{t('find_duplicates', self.lang)}'\n"
            "   - Progress and status will be shown\n"
            "   - Click again to cancel the scan\n"
            "3. Review found duplicates in the list\n"
            f"4. Select a PDF to preview its contents ({t('image_preview', self.lang)}/{t('text_preview', self.lang)})\n"
            f"5. {t('delete_selected', self.lang)}\n\n"
            "Note: The app compares PDF contents, not just filenames,\n"
            "ensuring accurate duplicate detection."
        )
        messagebox.showinfo(t('help_menu', self.lang), help_text)

    def load_settings(self):
        """Load application settings from config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {'theme': 'light', 'lang': 'en'}

    def save_settings(self):
        """Save current settings to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def change_theme(self, theme_name):
        """Change the application theme."""
        self.theme_manager.apply_theme(theme_name)
        self.settings['theme'] = theme_name
        self.save_settings()

    def change_language(self, lang):
        """Change the application language."""
        if lang != self.lang:
            # Update settings
            self.lang = lang
            self.settings['lang'] = lang
            self.save_settings()
            
            # Update menu texts if menu manager is already initialized
            if hasattr(self, 'menu_manager'):
                self.menu_manager.update_menu_texts()
                
            # Store the current window state and folder
            was_maximized = self.root.state() == 'zoomed'
            geometry = self.root.geometry()
            current_folder = self.folder_path.get()
            
            # Store the current folder for the new instance
            if current_folder:
                with open('temp_folder.txt', 'w') as f:
                    f.write(current_folder)
            
            # Schedule the application to restart after a short delay
            self.root.after(100, self._restart_application)
    
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
            # Try to remove any existing drop target handlers if the method exists
            if hasattr(self.root, 'drop_target_remove'):
                self.root.drop_target_remove()
            
            # Enable drag and drop
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
            
            # Bind drag and drop events
            self.root.drop_target = DND_FILES
            self.root.dnd_bind('<<DropEnter>>', self._on_drop_enter)
            self.root.dnd_bind('<<DropLeave>>', self._on_drop_leave)
        except Exception as e:
            print(f"Warning: Could not set up drag and drop: {e}")
            # Continue without drag and drop functionality
    
    def _on_drop_enter(self, event):
        """Handle drag enter event."""
        if event.data:
            return True  # Accept the drop
        return False  # Reject the drop
    
    def _on_drop_leave(self, event):
        """Handle drag leave event."""
        pass
    
    def _on_drop(self, event):
        """Handle drop event."""
        if not event.data:
            return
            
        # Get the dropped file/folder path
        file_path = event.data.strip('{}')
        
        # Handle the dropped path
        if os.path.isdir(file_path):
            self.folder_path.set(file_path)
            self.find_duplicates()
        elif file_path.lower().endswith('.pdf'):
            self.folder_path.set(os.path.dirname(file_path))
            self.find_duplicates()
    
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
            self.preview_text.insert(tk.END, f"Error: {str(e)}")
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
            if hasattr(self, 'progress_var'):
                self.progress_bar['value'] = self.progress_var
                self.progress_bar.update()
            
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
                
            # Sort by file size (descending)
            dup_group.sort(key=lambda x: os.path.getsize(x) if os.path.exists(x) else 0, reverse=True)
            
            # Add to treeview
            for i, file_path in enumerate(dup_group):
                try:
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
                    file_date = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S') if file_mtime > 0 else 'Unknown'
                    
                    # Mark the first file as the "original" (largest file)
                    is_original = (i == 0)
                    
                    if hasattr(self, 'tree'):
                        self.tree.insert(
                            '', 'end',
                            values=(
                                os.path.basename(file_path),
                                f"{file_size / (1024 * 1024):.2f} MB" if file_size > 0 else "0 MB",
                                file_date,
                                "Original" if is_original else "Duplicate",
                                file_path
                            ),
                            tags=('original' if is_original else 'duplicate')
                        )
                except Exception as e:
                    print(f"Error adding file to treeview: {e}")
        
        # Configure tag colors if tree exists
        if hasattr(self, 'tree'):
            self.tree.tag_configure('original', background='#e6f7e6')  # Light green for original
            self.tree.tag_configure('duplicate', background='#f9f9f9')  # Light gray for duplicates
        
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
        """Save the current scan results to a JSON file."""
        if not hasattr(self, 'duplicates') or not self.duplicates:
            messagebox.showinfo("No Results", "No scan results to save.")
            return
            
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Scan Results"
        )
        
        if not file_path:  # User cancelled
            return
            
        try:
            # Prepare data to save
            scan_data = {
                'scan_timestamp': datetime.now().isoformat(),
                'folder_scanned': self.folder_path.get(),
                'duplicate_groups': [],
                'file_info': {}
            }
            
            # Add file info for all files in duplicates
            file_info = {}
            for group in self.duplicates:
                group_info = []
                for file_path in group:
                    if file_path not in file_info:
                        try:
                            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                            file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
                            file_info[file_path] = {
                                'size_bytes': file_size,
                                'size_mb': file_size / (1024 * 1024) if file_size > 0 else 0,
                                'modified': datetime.fromtimestamp(file_mtime).isoformat() if file_mtime > 0 else 'Unknown',
                                'exists': os.path.exists(file_path)
                            }
                        except Exception as e:
                            file_info[file_path] = {
                                'error': str(e),
                                'exists': False
                            }
                    group_info.append(file_path)
                scan_data['duplicate_groups'].append(group_info)
            
            scan_data['file_info'] = file_info
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(scan_data, f, indent=2, ensure_ascii=False)
                
            self.show_status(f"Scan results saved to {os.path.basename(file_path)}", "success")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save scan results: {str(e)}")
            print(f"Error saving scan results: {e}")
            import traceback
            traceback.print_exc()
    
    def load_scan_results(self):
        """Load scan results from a previously saved JSON file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Scan Results"
        )
        
        if not file_path:  # User cancelled
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                scan_data = json.load(f)
                
            # Reset current state
            self.duplicates = scan_data.get('duplicate_groups', [])
            self.folder_path.set(scan_data.get('folder_scanned', ''))
            
            # Update UI
            if hasattr(self, 'tree'):
                self.tree.delete(*self.tree.get_children())
                
            self._update_results_ui()
            
            self.show_status("Scan results loaded successfully", "success")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load scan results: {str(e)}")
            print(f"Error loading scan results: {e}")
            import traceback
            traceback.print_exc()
    
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
        text.insert(tk.END, "The following files had issues during processing:\\n\\n")
        for file_path, error in self.problematic_files:
            text.insert(tk.END, f"• {file_path}\\n")
            text.insert(tk.END, f"  Error: {error}\\n\\n")
        
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
    
    # Set up drag and drop
    def handle_drop(event):
        # Get the dropped file/folder path
        file_path = event.data.strip('{}')
        if os.path.isdir(file_path):
            app.folder_path.set(file_path)
        elif os.path.isfile(file_path) and file_path.lower().endswith('.pdf'):
            app.folder_path.set(os.path.dirname(file_path))
    
    # Register drop target
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', handle_drop)
    
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

if __name__ == "__main__":
    main()