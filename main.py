import os
import hashlib
import tempfile
import json
import math
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
from help import HelpWindow
from about import About
from sponsor import Sponsor
from theme import ThemeManager
from translations import TRANSLATIONS, t
from updates import check_for_updates
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
        
        # Set window title with version
        self.root.title("PDF Duplicate Finder")
        
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
        
        # Set up the UI without menu first
        self._setup_ui()
        
        # Set up drag and drop
        self._setup_drag_drop()
        
        # Create menu bar after everything else is initialized
        from menu import MenuManager
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
        self.compare_mode = tk.StringVar(self.root, value='quick')  # 'quick' or 'full'
        self.preview_type = tk.StringVar(self.root, value='text')  # 'text' or 'image'
        
        # Status variables
        self.status_text = tk.StringVar(self.root)
        self.file_progress = tk.IntVar(self.root)
        self.overall_progress_value = tk.IntVar(self.root)
        
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
        
        # Add a menu for file operations
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Add Tools menu
        self.tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=self.tools_menu)
        
        # Add menu items
        self.tools_menu.add_command(
            label="View Problematic Files", 
            command=self.show_problematic_files,
            state=tk.DISABLED
        )
        self.tools_menu.add_separator()
        
        # Add checkbox for suppressing warnings
        self.suppress_warnings_var = tk.BooleanVar(value=self.suppress_warnings)
        self.tools_menu.add_checkbutton(
            label="Suppress PDF Warnings",
            variable=self.suppress_warnings_var,
            command=self.toggle_suppress_warnings
        )
        
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
        
        # Find duplicates button
        tk.Button(button_frame, text=t('find_duplicates', self.lang), command=self.find_duplicates, 
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
                 
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
        self.progress_bar.configure(maximum=100)
        self.file_progress_bar.configure(maximum=100)
        self.progress_var = 0
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

        # Delete selected button
        tk.Button(left_frame, text=t('delete_selected', self.lang), command=self.delete_selected, font=("Arial", 12)).pack(pady=10)
        
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
                
                # Take the first valid directory
                for path in files:
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
            try:
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
                
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__} - {str(e)}"
            file_info['error'] = error_msg
            logger.error(f"{file_path} - {error_msg}")
            import traceback
            traceback.print_exc()
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
        """Calculate hash for a PDF file with caching of file info."""
        file_path = file_info['path']
        try:
            # Update UI with current file being processed
            self.update_file_status(file_path)
            
            if self.compare_mode.get() == 'quick':
                # For quick compare, use file size + first page content hash
                with open(file_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    first_page_text = ''
                    if len(pdf_reader.pages) > 0:
                        first_page = pdf_reader.pages[0]
                        first_page_text = first_page.extract_text() or ''
                        
                        # Update progress for first page
                        self.update_file_progress(1, 1)
                    
                    # Combine file size and first page content for hashing
                    content = f"{file_info['size_kb']}:{first_page_text}"
                    return (file_path, hashlib.md5(content.encode('utf-8')).hexdigest())
            else:
                # Full compare - hash all content
                with open(file_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    content_parts = []
                    
                    for i, page in enumerate(pdf_reader.pages, 1):
                        if not self.is_searching:
                            return (file_path, None)
                            
                        # Update progress for current page
                        self.update_file_progress(i, total_pages)
                        
                        # Extract text from current page
                        page_text = page.extract_text()
                        if page_text:
                            content_parts.append(page_text)
                    
                    # Combine all page texts and hash
                    content = ''.join(content_parts)
                    return (file_path, hashlib.md5(content.encode('utf-8')).hexdigest())
                    
        except Exception as e:
            error_msg = f"Error reading {os.path.basename(file_path)}: {str(e)}"
            self.update_status_details(error_msg)
            print(error_msg)
            return (file_path, None)

    def save_scan_results(self):
        """Save current scan results to a file."""
        if not self.scan_results or 'duplicates' not in self.scan_results:
            messagebox.showwarning("No Results", "No scan results to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Scan Results As"
        )
        
        if not file_path:
            return
            
        try:
            # Prepare data for saving
            save_data = {
                'version': '1.0',
                'scanned_folder': self.last_scan_folder,
                'scan_timestamp': time.time(),
                'duplicates': self.scan_results['duplicates'],
                'file_info': self.scan_results['file_info']  # Already a dictionary
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
                
            messagebox.showinfo("Success", f"Scan results saved to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save scan results: {str(e)}")
            
    def load_scan_results(self):
        """Load scan results from a file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open Scan Results"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                
            if 'version' not in loaded_data or loaded_data['version'] != '1.0':
                raise ValueError("Unsupported file format or version")
                
            # Clear current results
            self.clear_results()
            
            # Update UI with loaded data
            self.folder_path.set(loaded_data.get('scanned_folder', ''))
            self.last_scan_folder = loaded_data.get('scanned_folder', '')
            
            # Store loaded data - keep file_info as a dictionary for direct access
            self.scan_results = {
                'duplicates': loaded_data['duplicates'],
                'file_info': loaded_data['file_info']  # Keep as dictionary
            }
            
            # Update the tree view with all columns
            self.tree.delete(*self.tree.get_children())
            for dup in self.scan_results['duplicates']:
                self.duplicates.append(dup)
                dup_path = dup[0]
                orig_path = dup[1] if len(dup) > 1 else ''
                
                # Get file info or use empty values if not found
                dup_info = self.scan_results['file_info'].get(dup_path, {})
                orig_info = self.scan_results['file_info'].get(orig_path, {}) if orig_path else {}
                
                # Format values for display
                dup_size = f"{dup_info.get('size_kb', 0):.1f}" if dup_info else ''
                dup_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(dup_info.get('mod_time', 0))) if dup_info and 'mod_time' in dup_info else ''
                orig_size = f"{orig_info.get('size_kb', 0):.1f}" if orig_info else ''
                orig_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(orig_info.get('mod_time', 0))) if orig_info and 'mod_time' in orig_info else ''
                
                # Insert into tree with all columns
                self.tree.insert('', 'end', values=(
                    dup_path,
                    dup_size,
                    dup_date,
                    orig_path,
                    orig_size,
                    orig_date
                ))
                
            # Enable save button
            self.save_btn.config(state=tk.NORMAL)
            
            messagebox.showinfo("Success", 
                f"Loaded {len(self.scan_results['duplicates'])} duplicate entries from:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load scan results: {str(e)}")
            
    def clear_results(self):
        """Clear current scan results and UI."""
        self.duplicates = []
        self.all_pdf_files = []
        self.problematic_files = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.clear_preview()
        self.clear_status()
        self.save_btn.config(state=tk.DISABLED)
        
    def find_duplicates(self):
        folder = self.folder_path.get()
        if not folder:
            self.show_status("Please select a folder first", "warning")
            return
            
        if not os.path.isdir(folder):
            self.show_status(f"Folder not found: {folder}", "error")
            return
            
        # Add to recent folders
        self.add_to_recent_folders(folder)
            
        # Clear previous results
        self.clear_results()
        self.last_scan_folder = folder
        
        # Reset progress and set searching flag
        self.is_searching = True
        self.scan_start_time = time.time()
        self.update_overall_progress(0, 100)
        self.update_status_details("Preparing to scan...")
        
        # Update status with folder name
        folder_name = os.path.basename(folder)
        self.show_status(f"Scanning: {folder_name}", "scanning")
        
        # Start scanning in background
        scan_thread = threading.Thread(target=self._scan_folder, args=(folder,), daemon=True)
        scan_thread.start()
    
    def _scan_folder(self, folder):
        """Scan folder for PDF files in a background thread."""
        try:
            if not self.is_searching:
                print("[INFO] Scan was cancelled before starting")
                return
                
            if not os.path.isdir(folder):
                error_msg = f"Folder not found: {folder}"
                print(f"[ERROR] {error_msg}")
                self.show_status(error_msg, "error")
                return
                
            print(f"[INFO] Starting scan in folder: {folder}")
            self.update_status_details("Searching for PDF files...")
            pdf_files = []
            
            try:
                for root, dirs, files in os.walk(folder):
                    if not self.is_searching:
                        print("[INFO] Scan cancelled by user")
                        return
                        
                    for file in files:
                        if not self.is_searching:
                            print("[INFO] Scan cancelled during file processing")
                            return
                            
                        if file.lower().endswith(".pdf"):
                            full_path = os.path.join(root, file)
                            try:
                                # Verify it's actually a file and not a symlink or other type
                                if os.path.isfile(full_path):
                                    pdf_files.append(full_path)
                                    
                                    # Update status every 100 files for better performance
                                    if len(pdf_files) % 100 == 0:
                                        self.update_status_details(f"Found {len(pdf_files)} PDF files so far...")
                                        
                            except Exception as e:
                                print(f"[WARNING] Error accessing {full_path}: {e}")
                                continue
                
                print(f"[INFO] Found {len(pdf_files)} PDF files to process")
                self.all_pdf_files = pdf_files
                total_files = len(pdf_files)
                
                if total_files == 0:
                    self.show_status("No PDF files found in the selected folder", "warning")
                    self.is_searching = False
                    return
                    
                # Process files in batches
                self._process_files_in_batches(pdf_files)
                
            except Exception as e:
                error_msg = f"Error scanning folder: {str(e)}"
                print(f"[ERROR] {error_msg}")
                import traceback
                traceback.print_exc()
                self.show_status(error_msg, "error")
            finally:
                # Ensure we always reset the searching flag
                self.is_searching = False
            
            if total_files == 0:
                self.show_status("No PDF files found in the selected folder", "warning")
                return
            
            # Update progress
            self.update_overall_progress(10, 100)
            self.update_status_details(f"Found {total_files} PDF files, analyzing...")
            
            # Process files in batches and get results
            processed_count, duplicate_count = self._process_files_in_batches(pdf_files)
            
            # Update progress
            self.update_overall_progress(90)
            
            # Finalize results
            self._finalize_scan_results(total_files, duplicate_count)
            
        except Exception as e:
            self.show_status(f"Error processing files: {str(e)}", "error")
            print(f"Error in _scan_folder: {str(e)}")
    
    def _process_files_in_batches(self, pdf_files):
        """Process PDF files in batches to find duplicates.
        
        Args:
            pdf_files: List of PDF file paths to process
        """
        try:
            total_files = len(pdf_files)
            print(f"[DEBUG] Starting to process {total_files} files")
            
            if total_files == 0:
                self.show_status("No PDF files found in the selected folder", "warning")
                return 0, 0
                
            # Initialize progress tracking
            processed_count = 0
            duplicate_count = 0
            batch_size = min(50, max(10, total_files // 20))  # Dynamic batch size
            
            print(f"[DEBUG] Using batch size: {batch_size}")
            
            # Initialize hash map for storing file hashes
            pdf_hash_map = {}
            
            # Process files in batches
            for i in range(0, total_files, batch_size):
                if not self.is_searching:
                    print("[DEBUG] Search cancelled by user")
                    return 0, 0
                    
                # Get current batch
                batch = pdf_files[i:i + batch_size]
                print(f"[DEBUG] Processing batch {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size} "
                      f"(files {i+1}-{min(i + batch_size, total_files)} of {total_files})")
                
                # Update status
                self.update_status_details(
                    f"Processing batch {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size} "
                    f"(files {i+1}-{min(i + batch_size, total_files)} of {total_files})"
                )
                
                # Process the batch
                try:
                    batch_results, new_duplicates, batch_duplicates = self.process_batch(
                        batch, pdf_hash_map, duplicate_count
                    )
                    
                    # Update counts
                    if batch_results is None:  # Search was cancelled
                        print("[DEBUG] Batch processing returned None, search cancelled")
                        return 0, 0
                        
                    processed_count += len(batch_results)
                    duplicate_count = new_duplicates
                    
                    # Add to duplicates list
                    self.duplicates.extend(batch_duplicates)
                    
                    # Update progress
                    progress = 10 + int(80 * (i + len(batch)) / total_files)
                    self.update_overall_progress(progress)
                    
                    # Update status message
                    status_msg = f"Scanned {i + len(batch)}/{total_files} files"
                    if duplicate_count > 0:
                        status_msg += f", found {duplicate_count} duplicates"
                    self.show_status(status_msg, "scanning")
                    
                    print(f"[DEBUG] {status_msg}")
                    
                except Exception as e:
                    print(f"[ERROR] Error processing batch: {str(e)}")
                    print(traceback.format_exc())
                    self.show_status(f"Error processing batch: {str(e)}", "error")
                
                # Allow UI to update
                self.root.update_idletasks()
                
            print(f"[DEBUG] Processing complete. Processed {processed_count} files, found {duplicate_count} duplicates")
            return processed_count, duplicate_count
            
        except Exception as e:
            error_msg = f"Error in _process_files_in_batches: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(traceback.format_exc())
            self.show_status(error_msg, "error")
            return 0, 0

    def show_problematic_files(self):
        """Show a dialog with problematic files."""
        if not self.problematic_files:
            messagebox.showinfo("No Issues Found", "No problematic files were found during the scan.")
            return
            
        # Create a new window
        problem_win = tk.Toplevel(self.root)
        problem_win.title("Problematic Files")
        problem_win.geometry("800x600")
        
        # Add a frame for buttons
        btn_frame = ttk.Frame(problem_win)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add export button
        ttk.Button(btn_frame, text="Export to File", 
                  command=self.export_problematic_files).pack(side=tk.LEFT, padx=5)
        
        # Add close button
        ttk.Button(btn_frame, text="Close", 
                  command=problem_win.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Add a treeview to display problematic files
        columns = ("File", "Path", "Issue")
        tree = ttk.Treeview(problem_win, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200 if col != "Path" else 400)
        
        # Add scrollbar
        vsb = ttk.Scrollbar(problem_win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add data to treeview
        for file_info in self.problematic_files:
            tree.insert("", "end", values=(
                file_info.get('file', ''),
                file_info.get('path', ''),
                file_info.get('error', 'Unknown error')
            ))
    
    def export_problematic_files(self):
        """Export list of problematic files to a text file."""
        if not self.problematic_files:
            return
            
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Problematic Files List As"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("Problematic Files Report\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"Total files with issues: {len(self.problematic_files)}\n\n")
                
                for idx, file_info in enumerate(self.problematic_files, 1):
                    f.write(f"{idx}. {file_info.get('file', '')}\n")
                    f.write(f"   Path: {file_info.get('path', '')}\n")
                    f.write(f"   Issue: {file_info.get('error', 'Unknown')}\n")
                    f.write("-" * 50 + "\n")
                    
            messagebox.showinfo("Export Complete", 
                            f"Successfully exported {len(self.problematic_files)} problematic files to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export file: {str(e)}")
    
    def toggle_suppress_warnings(self):
        """Toggle the suppress warnings setting."""
        self.suppress_warnings = self.suppress_warnings_var.get()
        
    def _finalize_scan_results(self, total_files, duplicate_count):
        """Finalize scan results and update UI."""
        # Update the Tools menu to enable/disable the Problematic Files option
        if hasattr(self, 'tools_menu'):
            state = tk.NORMAL if self.problematic_files else tk.DISABLED
            self.tools_menu.entryconfig("View Problematic Files", state=state)
            
        try:
            # Update progress
            self.update_overall_progress(95)
            self.update_status_details("Finalizing results...")
            
            # Store complete scan results with file info
            self.scan_results = {
                'duplicates': self.duplicates,
                'file_info': {},
                'scan_time': time.time() - getattr(self, 'scan_start_time', time.time()),
                'file_count': total_files,
                'duplicate_count': duplicate_count
            }
            
            # Create a mapping of file paths to their info
            for path in self.all_pdf_files:
                file_info = self.get_pdf_info(path)
                if file_info:  # Only add if we successfully got file info
                    self.scan_results['file_info'][path] = file_info
                    
            # Update the tree with file info
            self.tree.delete(*self.tree.get_children())
            for dup in self.duplicates:
                dup_path = dup[0]
                orig_path = dup[1] if len(dup) > 1 else ''
                
                # Get file info or use empty values if not found
                dup_info = self.scan_results['file_info'].get(dup_path, {})
                orig_info = self.scan_results['file_info'].get(orig_path, {}) if orig_path else {}
                
                # Format values for display
                dup_size = f"{dup_info.get('size_kb', 0):.1f}" if dup_info else ''
                dup_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(dup_info.get('mod_time', 0))) if dup_info and 'mod_time' in dup_info else ''
                orig_size = f"{orig_info.get('size_kb', 0):.1f}" if orig_info else ''
                orig_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(orig_info.get('mod_time', 0))) if orig_info and 'mod_time' in orig_info else ''
                
                # Insert into tree with all columns
                self.tree.insert('', 'end', values=(
                    dup_path,
                    dup_size,
                    dup_date,
                    orig_path,
                    orig_size,
                    orig_date
                ))
            
            # Update progress
            self.update_overall_progress(100)
            self.update_status_details("Done")
            
            # Enable save button
            self.save_btn.config(state=tk.NORMAL)
            
            # Calculate scan duration and format time string
            scan_duration = time.time() - self.scan_start_time
            time_str = time.strftime("%H:%M:%S", time.gmtime(scan_duration))
            
            # Show appropriate status message
            if duplicate_count == 0:
                status_msg = f"No duplicates found in {total_files} files. Scan completed in {time_str}."
                self.show_status(status_msg, "success")
                
                if total_files > 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Scan Complete",
                        f"No duplicate files found.\n\n"
                        f"Scanned {total_files} files in {time_str}.",
                        detail=f"Folder: {os.path.basename(self.last_scan_folder)}"
                    ))
            else:
                status_msg = f"Found {duplicate_count} duplicate(s) in {total_files} files. Scan completed in {time_str}."
                self.show_status(status_msg, "warning" if duplicate_count > 0 else "success")
                
        except Exception as e:
            error_msg = f"Error finalizing results: {str(e)}"
            self.show_status(error_msg, "error")
            print(f"Error in _finalize_scan_results: {error_msg}")
        finally:
            # Ensure we don't have a hanging reference to perform_search
            if hasattr(self, '_perform_search_after_id'):
                self.root.after_cancel(self._perform_search_after_id)
                delattr(self, '_perform_search_after_id')

    def safe_update_status(self, status):
        try:
            if not self.is_searching:
                return
            self.status_text.set(status)
            self.root.update_idletasks()
        except Exception:
            pass

    def process_batch(self, file_batch, pdf_hash_map, duplicate_count):
        batch_results = []
        batch_duplicates = []
        
        print(f"[DEBUG] Processing batch of {len(file_batch)} files")
        
        # First, get file info for all files in batch
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                file_infos = list(filter(None, executor.map(self.get_pdf_info, file_batch)))
            
            print(f"[DEBUG] Got file info for {len(file_infos)} files")
            
            if not file_infos:
                print("[WARNING] No file information was retrieved for this batch")
                return [], 0, []
                
            # Apply filters if active
            filters_active = getattr(self, 'filters_active', None)
            if filters_active and filters_active.get():
                filtered_infos = [info for info in file_infos if info and self.apply_filters(info)]
                print(f"[DEBUG] Filtered from {len(file_infos)} to {len(filtered_infos)} files after applying filters")
                file_infos = filtered_infos
            
            if not file_infos:
                print("[DEBUG] No files to process after filtering")
                return [], duplicate_count, []
                
        except Exception as e:
            print(f"[ERROR] Error processing batch: {e}")
            import traceback
            traceback.print_exc()
            return [], duplicate_count, []
            
        # For quick compare, first group by file size to reduce number of full comparisons
        if self.compare_mode.get() == 'quick':
            size_groups = {}
            
            # Group files by size
            for file_info in file_infos:
                size = int(file_info['size_kb'])
                if size not in size_groups:
                    size_groups[size] = []
                size_groups[size].append(file_info)
            
            # Only process groups with more than one file of the same size
            for size, same_size_infos in size_groups.items():
                if len(same_size_infos) > 1:
                    # Process this group of same-sized files
                    with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        future_to_file = {executor.submit(self.calculate_pdf_hash, file_info): file_info 
                                      for file_info in same_size_infos}
                        for future in concurrent.futures.as_completed(future_to_file):
                            if not self.is_searching:
                                return None, None, None
                                
                            file_info = future_to_file[future]
                            file_path = file_info['path']
                            try:
                                file_path, pdf_hash = future.result()
                                batch_results.append(file_path)
                                
                                if pdf_hash is not None:
                                    if pdf_hash in pdf_hash_map:
                                        original_file = pdf_hash_map[pdf_hash]['path']
                                        batch_duplicates.append((file_path, original_file))
                                        duplicate_count += 1
                                    else:
                                        pdf_hash_map[pdf_hash] = file_info
                            except Exception as e:
                                print(f"Error processing {file_path}: {e}")
                else:
                    # Single file in size group, just add to results
                    batch_results.append(same_size_infos[0]['path'])
        else:
            # Full compare mode - process all files normally
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {executor.submit(self.calculate_pdf_hash, file_info): file_info 
                                for file_info in file_infos}
                for future in concurrent.futures.as_completed(future_to_file):
                    if not self.is_searching:
                        return None, None, None
                        
                    file_info = future_to_file[future]
                    file_path = file_info['path']
                    try:
                        file_path, pdf_hash = future.result()
                        batch_results.append(file_path)
                        
                        if pdf_hash is not None:
                            if pdf_hash in pdf_hash_map:
                                original_file = pdf_hash_map[pdf_hash]['path']
                                batch_duplicates.append((file_path, original_file))
                                duplicate_count += 1
                            else:
                                pdf_hash_map[pdf_hash] = file_info
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        
        return batch_results, duplicate_count, batch_duplicates

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
        
    def perform_search(self, folder):
        if not self.is_searching:
            return

        pdf_hash_map = {}
        duplicate_count = 0
        processed_files = 0
        start_time = time.time()

        try:
            # First pass: collect all PDF files
            self.safe_update_status("Scanning for PDF files...")
            pdf_files = []
            for root, _, files in os.walk(folder):
                if not self.is_searching:
                    return
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_files.append(os.path.join(root, file))
            
            self.all_pdf_files = pdf_files  # Store all PDF files found

            total_pdfs = len(pdf_files)
            if total_pdfs == 0:
                self.safe_update_status(t('no_pdfs_found', self.lang))
                return

            # Update batch size from UI
            self.batch_size = self.batch_size_var.get()
            self.max_workers = self.workers_var.get()
            
            # Configure progress bar
            self.progress_bar['maximum'] = total_pdfs
            self.progress_var = 0
            self.progress_bar['value'] = 0
            self.progress_bar.pack(fill=tk.X, pady=2)
            
            # Process files in batches
            for i in range(0, len(pdf_files), self.batch_size):
                if not self.is_searching:
                    return
                
                # Update status with current mode
                mode = "Quick" if self.compare_mode.get() == 'quick' else "Full"
                self.safe_update_status(f"{mode} compare mode - Scanning batch {i//self.batch_size + 1}/{(len(pdf_files)-1)//self.batch_size + 1}...")
                
                batch = pdf_files[i:i + self.batch_size]
                processed, new_duplicate_count, new_duplicates = self.process_batch(batch, pdf_hash_map, duplicate_count)
                
                if processed is None:  # Search was cancelled
                    return
                    
                processed_files += len(processed)
                duplicate_count = new_duplicate_count
                
                # Update UI with new duplicates
                for dup in new_duplicates:
                    self.duplicates.append(dup)
                    self.tree.insert("", tk.END, values=dup)
                
                # Update progress
                self.progress_var = processed_files
                self.progress_bar['value'] = processed_files
                
                # Calculate estimated time remaining
                elapsed_time = time.time() - start_time
                files_remaining = total_pdfs - processed_files
                if processed_files > 0 and files_remaining > 0:
                    time_per_file = elapsed_time / processed_files
                    remaining_time = time_per_file * files_remaining
                    remaining_str = time.strftime("%H:%M:%S", time.gmtime(remaining_time))
                    self.safe_update_status(
                        f"Processed {processed_files}/{total_pdfs} files. "
                        f"Found {duplicate_count} duplicates. "
                        f"Remaining: ~{remaining_str}"
                    )
                else:
                    self.safe_update_status(f"Processed {processed_files}/{total_pdfs} files. Found {duplicate_count} duplicates.")
                
                # Allow UI to update
                self.root.update_idletasks()

            # Search complete
            if not self.is_searching:  # Check if search was cancelled
                self.show_status("Scan cancelled", "info")
                return
                
            elapsed_time = time.time() - start_time
            time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            
            # Store complete scan results
            self.scan_results = {
                'duplicates': self.duplicates,
                'file_info': [self.get_pdf_info(path) for path in self.all_pdf_files],
                'scan_time': elapsed_time,
                'file_count': total_pdfs,
                'duplicate_count': len(self.duplicates)
            }
            
            # Enable save button since we have results
            self.save_btn.config(state=tk.NORMAL)
            
            # Update status with results
            if not self.duplicates:
                self.show_status(
                    f"No duplicates found. Scanned {total_pdfs} files in {time_str}",
                    "success"
                )
                
                if total_pdfs > 0:
                    messagebox.showinfo(
                        "Scan Complete",
                        f"No duplicate files found.\n\n"
                        f"Scanned {total_pdfs} files in {time_str}.",
                        detail=f"Folder: {os.path.basename(self.last_scan_folder)}"
                    )
            else:
                dup_count = len(self.duplicates)
                self.show_status(
                    f"Found {dup_count} duplicate(s) in {total_pdfs} files. "
                    f"Scan completed in {time_str}.",
                    "success" if dup_count == 0 else "warning"
                )
                
                messagebox.showinfo(
                    "Scan Complete",
                    f"Found {dup_count} duplicate file(s).\n\n"
                    f"Scanned {total_pdfs} files in {time_str}.",
                    detail=f"Folder: {os.path.basename(self.last_scan_folder)}"
                )

        except Exception as e:
            if self.is_searching:  # Only show error if search wasn't cancelled
                messagebox.showerror(t('error', self.lang), f"An error occurred while scanning: {str(e)}")
                import traceback
                traceback.print_exc()

        finally:
            if self.is_searching:  # Only cleanup if search wasn't cancelled
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.status_text.set("")
                self.is_searching = False

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
            file_path, original_file = self.tree.item(item, "values")
            try:
                # Move to recycle bin on Windows
                if os.name == 'nt':
                    import send2trash
                    send2trash.send2trash(file_path)
                else:
                    os.remove(file_path)
                
                # Store deletion info for undo
                deleted_files.append({
                    'path': file_path,
                    'original': original_file,
                    'item_id': item
                })
                
                # Remove from tree
                self.tree.delete(item)
                
                # Remove from duplicates list
                self.duplicates = [d for d in self.duplicates if d[0] != file_path]
                
            except Exception as e:
                failed_deletions.append((file_path, str(e)))
        
        # Update undo stack if we had successful deletions
        if deleted_files:
            self.undo_stack.append({
                'type': 'delete',
                'files': deleted_files,
                'timestamp': time.time()
            })
            
            # Trim undo stack to max size
            if len(self.undo_stack) > self.max_undo_steps:
                self.undo_stack = self.undo_stack[-self.max_undo_steps:]
            
            # Enable undo menu
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

    def _setup_drag_drop(self):
        """Set up drag and drop functionality."""
        # Make the root window a drop target
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self._on_drop)
        
        # Bind drag and drop events
        self.root.drop_target = DND_FILES
        self.root.dnd_bind('<<DropEnter>>', self._on_drop_enter)
        self.root.dnd_bind('<<DropLeave>>', self._on_drop_leave)
    
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
        """Check for application updates."""
        if not force and not self.settings.get('check_updates', True):
            return
            
        def run_update_check():
            try:
                update_available, version, url = check_for_updates()
                if update_available:
                    if messagebox.askyesno(
                        "Update Available",
                        f"A new version {version} is available. Would you like to download it?",
                        parent=self.root
                    ):
                        import webbrowser
                        webbrowser.open(url)
                elif force:
                    messagebox.showinfo(
                        "No Updates",
                        "You are using the latest version.",
                        parent=self.root
                    )
            except Exception as e:
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