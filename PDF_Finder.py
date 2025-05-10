import os
import hashlib
import tempfile
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox, ttk, Button, Tk, Label, Toplevel
import imagehash

# Sponsor Class
class Sponsor:
    def show_sponsor_window(self):
        sponsor_root = Toplevel()
        sponsor_root.geometry("300x200")
        sponsor_root.title("Sponsor")
        sponsor_root.transient(sponsor_root.master)  # Make window modal

        title_label = tk.Label(sponsor_root, text="Support Us", font=("Arial", 16))
        title_label.pack(pady=10)

        def open_patreon():
            import webbrowser
            webbrowser.open("https://www.patreon.com/Nsfr750")

        def open_github():
            import webbrowser
            webbrowser.open("https://github.com/sponsors/Nsfr750")

        def open_discord():
            import webbrowser
            webbrowser.open("https://discord.gg/BvvkUEP9")

        def open_paypal():
            import webbrowser
            webbrowser.open("https://paypal.me/3dmega")

        # Create and place buttons
        patreon_button = tk.Button(sponsor_root, text="Join the Patreon!", command=open_patreon)
        patreon_button.pack(pady=5)

        github_button = tk.Button(sponsor_root, text="GitHub", command=open_github)
        github_button.pack(pady=5)

        discord_button = tk.Button(sponsor_root, text="Join on Discord", command=open_discord)
        discord_button.pack(pady=5)

        paypal_button = tk.Button(sponsor_root, text="Pay me a Coffee", command=open_paypal)
        paypal_button.pack(pady=5)

        # Center the window
        sponsor_root.update_idletasks()
        width = sponsor_root.winfo_width()
        height = sponsor_root.winfo_height()
        x = (sponsor_root.winfo_screenwidth() // 2) - (width // 2)
        y = (sponsor_root.winfo_screenheight() // 2) - (height // 2)
        sponsor_root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make window modal
        sponsor_root.grab_set()
        sponsor_root.focus_set()

class PDFDuplicateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Duplicate Finder")
        self.root.geometry("1024x768")
        self.folder_path = tk.StringVar()
        self.duplicates = []
        self.preview_type = tk.StringVar(value="image")
        self.current_preview_image = None
        self.status_text = tk.StringVar(value="")
        self.is_searching = False

        # Create menu
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        # Add Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How to Use", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Add About menu
        about_menu = tk.Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="About", menu=about_menu)

        # Add Sponsor menu
        sponsor_menu = tk.Menu(menu_bar, tearoff=0)
        sponsor = Sponsor()
        sponsor_menu.add_command(label="Sponsor Us", command=sponsor.show_sponsor_window)
        menu_bar.add_cascade(label="Sponsor", menu=sponsor_menu)

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
        tk.Label(search_frame, text="Folder to Scan:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.folder_path, width=50, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Browse", command=self.browse_folder, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Find duplicates button
        tk.Button(left_frame, text="Find Duplicates", command=self.find_duplicates, font=("Arial", 12)).pack(pady=5)

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
        ttk.Radiobutton(preview_options, text="Image Preview", variable=self.preview_type, 
                        value="image", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(preview_options, text="Text Preview", variable=self.preview_type, 
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
        tk.Button(left_frame, text="Delete Selected", command=self.delete_selected, font=("Arial", 12)).pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select a Folder")
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
            messagebox.showwarning("Warning", "Please select a folder to scan.")
            return

        if self.is_searching:
            # If already searching, cancel the search
            self.is_searching = False
            self.status_text.set("Cancelling search...")
            self.root.update_idletasks()
            return

        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        self.duplicates = []
        self.is_searching = True

        # Configure progress bar
        self.progress_bar.pack(fill=tk.X, pady=2)
        self.progress_bar.start(10)
        self.status_text.set("Initializing scan...")
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
                self.safe_update_status("No PDF files found in the selected folder.")
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
                messagebox.showinfo("Info", "No duplicate PDFs found.")
            else:
                messagebox.showinfo("Info", f"Found {len(self.duplicates)} duplicate files.")

        except Exception as e:
            if self.is_searching:  # Only show error if search wasn't cancelled
                messagebox.showerror("Error", f"An error occurred while scanning: {str(e)}")

        finally:
            if self.is_searching:  # Only cleanup if search wasn't cancelled
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.status_text.set("")
                self.is_searching = False

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No files selected for deletion.")
            return

        for item in selected_items:
            file_path, _ = self.tree.item(item, "values")
            try:
                os.remove(file_path)
                self.tree.delete(item)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
                messagebox.showerror("Error", f"Could not delete {file_path}. Check the console for details.")
        
        messagebox.showinfo("Info", "Selected files have been deleted.")

    def show_help(self):
        help_text = (
            "PDF Duplicate Finder Help\n\n"
            "Features:\n"
            "1. Find duplicate PDFs based on content\n"
            "2. Preview PDFs (image or text)\n"
            "3. Manage and delete duplicates\n\n"
            "How to Use:\n"
            "1. Select a folder to scan\n"
            "2. Click 'Find Duplicates' to start scanning\n"
            "   - Progress and status will be shown\n"
            "   - Click again to cancel the scan\n"
            "3. Review found duplicates in the list\n"
            "4. Select a PDF to preview its contents\n"
            "   - Switch between image/text preview\n"
            "5. Select duplicates and click 'Delete Selected' to remove them\n\n"
            "Note: The app compares PDF contents, not just filenames,\n"
            "ensuring accurate duplicate detection."
        )
        messagebox.showinfo("Help", help_text)

    def show_about(self):
        messagebox.showinfo("About", "PDF Duplicate Finder v2.2\nDeveloped by Nsfr750\nDetect and remove duplicate PDF files.")

    def show_sponsor(self):
        messagebox.showinfo("Sponsor", "Support the development of this app!\nVisit: https://github.com/sponsors/Nsfr750")

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