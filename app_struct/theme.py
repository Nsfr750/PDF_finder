"""
Theme management for PDF Duplicate Finder.
Provides light and dark theme support.
"""
import tkinter as tk
import tkinter.ttk as ttk

# Light theme colors
LIGHT_THEME = {
    'bg': '#f0f0f0',
    'fg': '#000000',
    'button_bg': '#e1e1e1',
    'button_fg': '#000000',
    'button_active': '#d0d0d0',
    'highlight': '#0078d7',
    'text_bg': '#ffffff',
    'text_fg': '#000000',
    'tree_bg': '#ffffff',
    'tree_fg': '#000000',
    'tree_selected': '#e1e1e1',
    'menu_bg': '#f0f0f0',
    'menu_fg': '#000000',
    'menu_active_bg': '#e1e1e1',
    'menu_active_fg': '#000000',
}

# Dark theme colors
DARK_THEME = {
    'bg': '#2d2d2d',
    'fg': '#e0e0e0',
    'button_bg': '#3d3d3d',
    'button_fg': '#e0e0e0',
    'button_active': '#4d4d4d',
    'highlight': '#0078d7',
    'text_bg': '#1e1e1e',
    'text_fg': '#e0e0e0',
    'tree_bg': '#252526',
    'tree_fg': '#e0e0e0',
    'tree_selected': '#3d3d3d',
    'menu_bg': '#2d2d2d',
    'menu_fg': '#e0e0e0',
    'menu_active_bg': '#3d3d3d',
    'menu_active_fg': '#ffffff',
}

class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.current_theme = 'light'
        self.themes = {
            'light': LIGHT_THEME,
            'dark': DARK_THEME
        }
    
    def apply_theme(self, theme_name):
        """Apply the specified theme to the application."""
        if theme_name not in self.themes:
            theme_name = 'light'
            
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure ttk widgets
        style.configure('.', background=theme['bg'], foreground=theme['fg'])
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        style.configure('TButton', 
                       background=theme['button_bg'], 
                       foreground=theme['button_fg'],
                       borderwidth=1)
        style.map('TButton',
                 background=[('active', theme['button_active'])])
        
        # Treeview
        style.configure('Treeview', 
                       background=theme['tree_bg'],
                       foreground=theme['tree_fg'],
                       fieldbackground=theme['tree_bg'],
                       selectbackground='#0078d7',  # Blue background for selected items
                       selectforeground='#ffffff')   # White text for selected items
        style.map('Treeview', 
                 background=[('selected', '#0078d7')],  # Blue background for selected items
                 foreground=[('selected', '#ffffff')])  # White text for selected items
        
        # Scrollbars
        style.configure('Vertical.TScrollbar', 
                       background=theme['button_bg'],
                       troughcolor=theme['bg'],
                       arrowcolor=theme['fg'])
        style.configure('Horizontal.TScrollbar', 
                       background=theme['button_bg'],
                       troughcolor=theme['bg'],
                       arrowcolor=theme['fg'])
        
        # Menu
        self.root.option_add('*Menu.background', theme['menu_bg'])
        self.root.option_add('*Menu.foreground', theme['menu_fg'])
        self.root.option_add('*Menu.activeBackground', theme['menu_active_bg'])
        self.root.option_add('*Menu.activeForeground', theme['menu_active_fg'])
        
        # Update all widgets
        self.update_widgets(self.root, theme)
    
    def update_widgets(self, widget, theme):
        """Recursively update widget colors."""
        try:
            # Update widget background and foreground
            if widget.winfo_children():
                for child in widget.winfo_children():
                    self.update_widgets(child, theme)
            
            # Update specific widget types
            if isinstance(widget, tk.Text):
                widget.config(
                    bg=theme['text_bg'],
                    fg=theme['text_fg'],
                    insertbackground=theme['fg']
                )
            elif isinstance(widget, tk.Canvas):
                widget.config(bg=theme['text_bg'])
            elif isinstance(widget, ttk.Entry):
                widget.config(fieldbackground=theme['text_bg'], 
                             foreground=theme['text_fg'])
            
        except tk.TclError:
            # Skip widgets that don't support certain options
            pass

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
        return new_theme
