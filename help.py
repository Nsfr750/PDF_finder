import tkinter as tk
from tkinter import ttk

class HelpWindow:
    @staticmethod
    def show_help(root):
        help_dialog = tk.Toplevel(root)
        help_dialog.title('PDF Finder - Help')
        help_dialog.geometry('600x500')
        help_dialog.transient(root)
        help_dialog.grab_set()

        # Main container with padding
        main_frame = ttk.Frame(help_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text='PDF Duplicate Finder - Help', font=('Helvetica', 16, 'bold'))
        title.pack(pady=(0, 20))

        # Create a text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, padx=10, pady=10)
        scrollbar.config(command=text.yview)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Help content
        help_text = """How to use PDF Duplicate Finder:

1. Select a folder containing PDF files to scan for duplicates.
2. Click 'Search for Duplicates' to start the scanning process.
3. The application will analyze the PDFs and display any duplicates found.
4. For each set of duplicates:
   - Select a file in the list to preview it
   - Use the 'Delete Selected' button to remove unwanted duplicates
   - Toggle between 'Image Preview' and 'Text Preview' to view different aspects of the PDF

Customization:
- Change between Light and Dark themes from View > Theme menu
- Theme preferences are saved between sessions
- Adjust window size as needed - the interface is responsive

Tips:
- The scanning process may take some time for large collections
- Image-based comparison is more accurate but slower
- Text-based comparison is faster but may miss visual duplicates
- Always verify before deleting any files
- Use horizontal scrollbar to view long file paths

Keyboard Shortcuts:
- Ctrl+O: Open folder
- F5: Start new search
- F1: Show this help
- Ctrl+Q: Quit application
- Delete: Remove selected files
- Delete: Remove selected file
- Esc: Close preview

For additional support, please contact us through the 'About' section.
"""
        
        # Insert help text
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)  # Make it read-only

        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        close_btn = ttk.Button(button_frame, text='Close', command=help_dialog.destroy)
        close_btn.pack(side=tk.RIGHT)

        # Center the window
        help_dialog.update_idletasks()
        width = help_dialog.winfo_width()
        height = help_dialog.winfo_height()
        x = (help_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (help_dialog.winfo_screenheight() // 2) - (height // 2)
        help_dialog.geometry(f'{width}x{height}+{x}+{y}')
