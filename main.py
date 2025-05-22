import os
import hashlib
import tempfile
import json
from pathlib import Path
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox, ttk, Button, Tk, Label, Toplevel
import imagehash
from help import HelpWindow
from about import About
from sponsor import Sponsor
from theme import ThemeManager
from translations import TRANSLATIONS, t



class PDFDuplicateApp:
    def __init__(self, root):
        self.root = root
        # Language settings
        self.config_file = Path("pdf_finder_config.json")
        self.settings = self.load_settings()
        self.lang = self.settings.get('lang', 'en')
        self.root.title(t('app_title', self.lang))
        self.root.geometry("1024x768")
        self.folder_path = tk.StringVar()
        self.duplicates = []
        self.preview_type = tk.StringVar(value="image")
        self.current_preview_image = None
        self.status_text = tk.StringVar(value="")
        self.is_searching = False

        # Initialize theme manager and sponsor first
        self.theme_manager = ThemeManager(self.root)
        self.sponsor = Sponsor(root)
        
        # Create menu
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        # Create View menu for theme selection
        view_menu = tk.Menu(menu_bar, tearoff=0)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'light'))
        theme_menu.add_radiobutton(
            label=t('light_theme', self.lang),
            command=lambda: self.change_theme('light'),
            variable=self.theme_var,
            value='light'
        )
        theme_menu.add_radiobutton(
            label=t('dark_theme', self.lang),
            command=lambda: self.change_theme('dark'),
            variable=self.theme_var,
            value='dark'
        )
        view_menu.add_cascade(label=t('theme_menu', self.lang), menu=theme_menu)
        menu_bar.add_cascade(label=t('view_menu', self.lang), menu=view_menu)

        # Language menu
        language_menu = tk.Menu(menu_bar, tearoff=0)
        language_menu.add_radiobutton(label=t('english', 'en'), command=lambda: self.change_language('en'), value='en', variable=tk.StringVar(value=self.lang))
        language_menu.add_radiobutton(label=t('italian', 'it'), command=lambda: self.change_language('it'), value='it', variable=tk.StringVar(value=self.lang))
        menu_bar.add_cascade(label=t('language_menu', self.lang), menu=language_menu)

        # Create Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label=t('help_menu', self.lang), command=self.show_help, accelerator="F1")
        help_menu.add_separator()
        help_menu.add_command(label=t('about_menu', self.lang), command=self.show_about)
        help_menu.add_command(label=t('sponsor_menu', self.lang), command=self.sponsor.show_sponsor)
        menu_bar.add_cascade(label=t('help_menu', self.lang), menu=help_menu)
        
        # Apply saved theme
        self.change_theme(self.settings.get('theme', 'light'))

        # Main container for search controls and results
        main_container = ttk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

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

        # Find duplicates button
        tk.Button(left_frame, text=t('find_duplicates', self.lang), command=self.find_duplicates, font=("Arial", 12)).pack(pady=5)

        # Progress bar and status below search controls
        self.progress_frame = ttk.Frame(left_frame)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_text)
        self.status_label.pack(pady=2)
        
        # Configure progress bar
        self.progress_bar.configure(maximum=100)
        
        # Tree frame for results
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Configure and pack tree in its frame
        self.tree = ttk.Treeview(tree_frame, columns=("File Path", "Original File"), show="headings", height=15)
        self.tree.heading("File Path", text="Duplicate File")
        self.tree.heading("Original File", text="Original File")
        self.tree.column("File Path", width=350)
        self.tree.column("Original File", width=350)

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

    def browse_folder(self):
        folder = filedialog.askdirectory(title=t('select_folder', self.lang))
        if folder:
            self.folder_path.set(folder)

    def calculate_pdf_hash(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                content = ''.join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
                return hashlib.md5(content.encode('utf-8')).hexdigest()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def find_duplicates(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning(t('warning', self.lang), t('please_select_folder', self.lang))
            return

        if self.is_searching:
            # If already searching, cancel the search
            self.is_searching = False
            self.status_text.set(t('cancelling_search', self.lang))
            self.root.update_idletasks()
            return

        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        self.duplicates = []
        self.is_searching = True

        # Configure progress bar
        self.progress_bar.pack(fill=tk.X, pady=2)
        self.progress_bar.start(10)
        self.status_text.set(t('initializing_scan', self.lang))
        self.root.update_idletasks()
        
        # Schedule the search to run in the background
        self.root.after(100, self.perform_search, folder)

    def safe_update_status(self, status):
        try:
            if not self.is_searching:
                return
            self.status_text.set(status)
            self.root.update_idletasks()
        except Exception:
            pass

    def perform_search(self, folder):
        if not self.is_searching:
            return

        pdf_hash_map = {}
        total_files = 0
        duplicate_count = 0

        try:
            # First pass: count total PDF files
            pdf_files = []
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(".pdf"):
                        pdf_files.append(os.path.join(root, file))

            total_pdfs = len(pdf_files)
            if total_pdfs == 0:
                self.safe_update_status(t('no_pdfs_found', self.lang))
                return

            # Second pass: process files
            for file_path in pdf_files:
                if not self.is_searching:
                    return

                total_files += 1
                self.safe_update_status(f"Scanning PDF {total_files} of {total_pdfs}...")

                pdf_hash = self.calculate_pdf_hash(file_path)
                if pdf_hash:
                    if pdf_hash in pdf_hash_map:
                        original_file = pdf_hash_map[pdf_hash]
                        self.duplicates.append((file_path, original_file))
                        self.tree.insert("", tk.END, values=(file_path, original_file))
                        duplicate_count += 1
                        self.safe_update_status(f"Found {duplicate_count} duplicates ({total_files} of {total_pdfs} scanned)")
                    else:
                        pdf_hash_map[pdf_hash] = file_path

            # Search complete
            if not self.duplicates:
                messagebox.showinfo(t('info', self.lang), t('no_duplicates_found', self.lang))
            else:
                messagebox.showinfo(t('info', self.lang), t('duplicates_found', self.lang, count=len(self.duplicates)))

        except Exception as e:
            if self.is_searching:  # Only show error if search wasn't cancelled
                messagebox.showerror(t('error', self.lang), f"An error occurred while scanning: {str(e)}")

        finally:
            if self.is_searching:  # Only cleanup if search wasn't cancelled
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.status_text.set("")
                self.is_searching = False

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(t('warning', self.lang), t('no_files_selected', self.lang))
            return

        for item in selected_items:
            file_path, _ = self.tree.item(item, "values")
            try:
                os.remove(file_path)
                self.tree.delete(item)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
                messagebox.showerror(t('error', self.lang), f"Could not delete {file_path}. Check the console for details.")
        
        messagebox.showinfo(t('info', self.lang), t('files_deleted', self.lang))

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
        self.lang = lang
        self.settings['lang'] = lang
        self.save_settings()
        self.refresh_language()

    def refresh_language(self):
        # Re-initialize the UI to update all text
        self.root.destroy()
        new_root = tk.Tk()
        app = PDFDuplicateApp(new_root)
        new_root.mainloop()
        
    def show_about(self):
        About.show_about(self.root)

    def show_sponsor(self):
        self.sponsor.show_sponsor()

    def on_select(self, event):
        self.update_preview()

    def update_preview(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.clear_preview()
            return

        file_path, _ = self.tree.item(selected_items[0], "values")
        if not os.path.exists(file_path):
            self.clear_preview()
            return

        if self.preview_type.get() == "image":
            self.show_image_preview(file_path)
        else:
            self.show_text_preview(file_path)

    def clear_preview(self):
        self.preview_canvas.delete("all")
        self.preview_text.delete(1.0, tk.END)
        if self.current_preview_image:
            self.current_preview_image = None

    def show_image_preview(self, file_path):
        self.preview_text.pack_forget()
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self.preview_canvas.delete("all")

        try:
            # Get total page count
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                total_pages = len(pdf.pages)

            # Convert first page to image
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(file_path, first_page=1, last_page=1, output_folder=temp_dir)
                if images:
                    img = images[0]
                    
                    # Update canvas and wait for it to be properly sized
                    self.preview_canvas.update()
                    
                    # Calculate scaling to fit the canvas while maintaining aspect ratio
                    canvas_width = self.preview_canvas.winfo_width()
                    canvas_height = self.preview_canvas.winfo_height()
                    
                    # If canvas dimensions are too small, use minimum dimensions
                    if canvas_width < 100: canvas_width = 400
                    if canvas_height < 100: canvas_height = 600
                    
                    img_width, img_height = img.size
                    scale = min(canvas_width/img_width, canvas_height/img_height)
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    self.current_preview_image = ImageTk.PhotoImage(img)
                    
                    # Center the image
                    x = (canvas_width - new_width) // 2
                    y = (canvas_height - new_height) // 2
                    self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.current_preview_image)
                    
                    # Add page count text
                    self.preview_canvas.create_text(
                        10, 10,
                        anchor=tk.NW,
                        text=f"Page 1 of {total_pages}",
                        fill="black",
                        font=("Arial", 10)
                    )
        except Exception as e:
            self.preview_canvas.create_text(10, 10, anchor=tk.NW, text=f"Error loading preview: {str(e)}")

    def show_text_preview(self, file_path):
        self.preview_canvas.pack_forget()
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.delete(1.0, tk.END)

        try:
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                if len(pdf.pages) > 0:
                    text = pdf.pages[0].extract_text()
                    self.preview_text.insert(1.0, text)
                else:
                    self.preview_text.insert(1.0, "No text content found in the first page.")
        except Exception as e:
            self.preview_text.insert(1.0, f"Error loading text preview: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFDuplicateApp(root)
    root.mainloop()