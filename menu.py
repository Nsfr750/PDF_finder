import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinterdnd2 import DND_FILES
import os
import json
from pathlib import Path
from translations import t

class MenuManager:
    def __init__(self, root, app):
        """
        Initialize the MenuManager.
        
        Args:
            root: The root Tkinter window
            app: Reference to the main application instance
        """
        self.root = root
        self.app = app
        self.menu_bar = None
        self.recent_menu = None
        self.undo_menu_item = None
        self.theme_var = None
        
    def create_menu_bar(self):
        """Create and return the main menu bar."""
        self.menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = self._create_file_menu()
        
        # Edit menu
        edit_menu = self._create_edit_menu()
        
        # View menu with theme and language submenus
        view_menu = self._create_view_menu()
        
        # Help menu
        help_menu = self._create_help_menu()
        
        # Add all menus to the menu bar
        self.menu_bar.add_cascade(label=t('file_menu', self.app.lang), menu=file_menu)
        self.menu_bar.add_cascade(label=t('edit_menu', self.app.lang), menu=edit_menu)
        self.menu_bar.add_cascade(label=t('view_menu', self.app.lang), menu=view_menu)
        self.menu_bar.add_cascade(label=t('help_menu', self.app.lang), menu=help_menu)
        
        # Set the menu bar
        self.root.config(menu=self.menu_bar)
        
        return self.menu_bar
    
    def _create_file_menu(self):
        """Create and return the File menu."""
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        
        # Recent folders submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0, postcommand=self.app.update_recent_folders_menu)
        file_menu.add_cascade(label=t('recent_folders', self.app.lang), menu=self.recent_menu)
        file_menu.add_separator()
        file_menu.add_command(label=t('exit', self.app.lang), command=self.app.root.quit)
        
        return file_menu
    
    def _create_edit_menu(self):
        """Create and return the Edit menu."""
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.undo_menu_item = edit_menu.add_command(
            label=t('undo_delete', self.app.lang),
            command=self.app.undo_last_delete,
            state=tk.DISABLED
        )
        return edit_menu
    
    def _create_view_menu(self):
        """Create and return the View menu with theme and language submenus."""
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        self.theme_var = tk.StringVar(value=self.app.settings.get('theme', 'light'))
        theme_menu.add_radiobutton(
            label=t('light_theme', self.app.lang),
            command=lambda: self.app.change_theme('light'),
            variable=self.theme_var,
            value='light'
        )
        theme_menu.add_radiobutton(
            label=t('dark_theme', self.app.lang),
            command=lambda: self.app.change_theme('dark'),
            variable=self.theme_var,
            value='dark'
        )
        view_menu.add_cascade(label=t('theme_menu', self.app.lang), menu=theme_menu)
        
        # Language submenu
        language_menu = self._create_language_menu()
        view_menu.add_cascade(label=t('language_menu', self.app.lang), menu=language_menu)
        
        return view_menu
    
    def _create_language_menu(self):
        """Create and return the Language submenu."""
        language_menu = tk.Menu(self.menu_bar, tearoff=0)
        
        # Add all supported languages
        languages = [
            ('en', 'english'),
            ('it', 'italian'),
            ('es', 'spanish'),
            ('pt', 'portuguese'),
            ('ru', 'russian'),
            ('ar', 'arabic')
        ]
        
        for lang_code, lang_key in languages:
            language_menu.add_radiobutton(
                label=t(lang_key, lang_code),
                command=lambda lc=lang_code: self.app.change_language(lc),
                value=lang_code,
                variable=tk.StringVar(value=self.app.lang)
            )
        
        return language_menu
    
    def _create_help_menu(self):
        """Create and return the Help menu."""
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(
            label=t('help_menu', self.app.lang), 
            command=self.app.show_help, 
            accelerator="F1"
        )
        help_menu.add_separator()
        help_menu.add_command(
            label=t('check_updates', self.app.lang), 
            command=self.app.check_updates
        )
        help_menu.add_command(
            label=t('about_menu', self.app.lang), 
            command=self.app.show_about
        )
        if hasattr(self.app, 'sponsor'):
            help_menu.add_command(
                label=t('sponsor_menu', self.app.lang), 
                command=self.app.sponsor.show_sponsor
            )
        
        return help_menu
    
    def update_menu_texts(self):
        """Update all menu texts with current language."""
        if not self.menu_bar:
            return
            
        # Update main menu labels
        self.menu_bar.entryconfig(0, label=t('file_menu', self.app.lang))
        self.menu_bar.entryconfig(1, label=t('edit_menu', self.app.lang))
        self.menu_bar.entryconfig(2, label=t('view_menu', self.app.lang))
        self.menu_bar.entryconfig(3, label=t('help_menu', self.app.lang))
        
        # Update other menu items as needed
        # (The actual menu items will be recreated with the new language when the menu is reopened)
    
    def update_undo_menu_item(self, state):
        """Update the state of the Undo menu item."""
        if self.undo_menu_item:
            self.undo_menu_item['state'] = state
