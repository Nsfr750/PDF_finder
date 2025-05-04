import os
import hashlib
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class PDFDuplicateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Duplicate Finder")
        self.root.geometry("800x600")

        self.folder_path = tk.StringVar()
        self.duplicates = []

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
        sponsor_menu.add_command(label="Sponsor", command=self.show_sponsor)
        menu_bar.add_cascade(label="Sponsor", menu=sponsor_menu)

        # UI Elements
        tk.Label(root, text="Folder to Scan:", font=("Arial", 12)).pack(pady=10)
        tk.Entry(root, textvariable=self.folder_path, width=50, font=("Arial", 10)).pack(pady=5)
        tk.Button(root, text="Browse", command=self.browse_folder, font=("Arial", 10)).pack(pady=5)
        tk.Button(root, text="Find Duplicates", command=self.find_duplicates, font=("Arial", 12)).pack(pady=20)

        # Table for displaying duplicates
        self.tree = ttk.Treeview(root, columns=("File Path", "Original File"), show="headings", height=15)
        self.tree.heading("File Path", text="Duplicate File")
        self.tree.heading("Original File", text="Original File")
        self.tree.column("File Path", width=350)
        self.tree.column("Original File", width=350)
        self.tree.pack(pady=10)

        # Delete selected button
        tk.Button(root, text="Delete Selected", command=self.delete_selected, font=("Arial", 12)).pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select a Folder")
        if folder:
            self.folder_path.set(folder)

    def calculate_pdf_hash(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
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

        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        self.duplicates = []

        pdf_hash_map = {}
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    pdf_hash = self.calculate_pdf_hash(file_path)
                    if pdf_hash:
                        if pdf_hash in pdf_hash_map:
                            original_file = pdf_hash_map[pdf_hash]
                            self.duplicates.append((file_path, original_file))
                            self.tree.insert("", tk.END, values=(file_path, original_file))
                        else:
                            pdf_hash_map[pdf_hash] = file_path

        if not self.duplicates:
            messagebox.showinfo("Info", "No duplicate PDFs found.")
        else:
            messagebox.showinfo("Info", f"Found {len(self.duplicates)} duplicate files.")

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
        messagebox.showinfo("Help", "To use this app:\n1. Select a folder to scan.\n2. Click 'Find Duplicates'.\n3. Select files from the list and click 'Delete Selected'.")

    def show_about(self):
        messagebox.showinfo("About", "PDF Duplicate Finder v2.0\nDeveloped by Nsfr750\nDetect and remove duplicate PDF files.")

    def show_sponsor(self):
        messagebox.showinfo("Sponsor", "Support the development of this app!\nVisit: https://github.com/sponsors/Nsfr750")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFDuplicateApp(root)
    root.mainloop()