"""
Module for handling scan results saving and loading functionality.
"""
import os
import csv
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class ScanManager:
    """
    Handles saving and loading of scan results.
    """
    
    def __init__(self, root: tk.Tk, app):
        """
        Initialize the ScanManager.
        
        Args:
            root: The root Tkinter window
            app: Reference to the main application instance
        """
        self.root = root
        self.app = app
        self.last_save_dir = None
        
    def save_scan_results(self) -> bool:
        """
        Save the current scan results to a CSV file.
        
        This is a wrapper that handles exceptions during the save operation.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            return self._save_scan_results_impl()
        except Exception as e:
            error_msg = f"Error saving scan results: {str(e)}"
            print(error_msg)
            if hasattr(self.app, 'show_status'):
                self.app.show_status(error_msg, "error")
            messagebox.showerror("Error", f"Failed to save scan results: {str(e)}")
            return False
    
    def _save_scan_results_impl(self) -> bool:
        """
        Implementation of save_scan_results using asksaveasfile.
        """
        if not hasattr(self.app, 'duplicates') or not self.app.duplicates:
            messagebox.showinfo("No Results", "No scan results to save.")
            return False
        
        # Get the current date and time for the filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create a default filename with timestamp
        default_filename = f"duplicate_scan_results_{timestamp}.csv"
        
        # Clean up the filename to remove any invalid characters
        import re
        default_filename = re.sub(r'[<>:"/\\|?*]', '_', default_filename)
        
        # Set the default save directory to the user's Documents folder
        documents_dir = os.path.join(os.path.expanduser('~'), 'Documents')
        
        # Ensure the Documents directory exists
        os.makedirs(documents_dir, exist_ok=True)
        
        # Create the full default path in Documents
        default_path = os.path.join(documents_dir, default_filename)
        
        # Debug output
        print(f"DEBUG: Default save path: {default_path}")
        
        # Ask user for save location
        selected_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=documents_dir,  # Always start in Documents
            initialfile=default_filename,
            title="Save Duplicate Scan Results As"
        )
        
        if not selected_path:  # User cancelled
            print("DEBUG: User cancelled save operation")
            return False
            
        # Convert to string and clean up
        selected_path = str(selected_path).strip()
        if not selected_path:
            return False
            
        print(f"DEBUG: Selected path after cleanup: {selected_path}")
            
        # Ensure the path is absolute
        if not os.path.isabs(selected_path):
            selected_path = os.path.abspath(selected_path)
            
        # Normalize the path
        selected_path = os.path.normpath(selected_path)
        
        # Ensure we have a .csv extension
        base, ext = os.path.splitext(selected_path)
        if not ext or ext.lower() != '.csv':
            selected_path = f"{base}.csv"
            
        # Ensure the target directory exists
        os.makedirs(os.path.dirname(selected_path) or '.', exist_ok=True)
        
        # Update last save directory for next time
        self.last_save_dir = os.path.dirname(selected_path)
        
        # Use the final path for saving
        file_path = selected_path
        print(f"DEBUG: Final file path before saving: {file_path}")
        
        # Prepare data for CSV
        rows = []
        
        # Add header
        rows.append(["Group ID", "File Path", "File Size (KB)", "Last Modified", "Is Original"])
        
        # Add data rows
        for group_id, group in enumerate(self.app.duplicates, 1):
            if not group:
                continue
                
            # Sort files by size (smallest first) and modification time (newest first)
            def get_file_sort_key(file_path):
                # Ensure file_path is a string and not a list
                if isinstance(file_path, (list, tuple)):
                    file_path = file_path[0] if file_path else ''
                file_path = str(file_path)
                
                try:
                    size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
                    return (size, -mtime)
                except (OSError, TypeError) as e:
                    print(f"Warning: Could not get file info for sorting {file_path}: {str(e)}")
                    return (0, 0)
            
            sorted_group = sorted(group, key=get_file_sort_key)
            
            # Mark the first file as original
            for i, file_item in enumerate(sorted_group):
                # Ensure file_path is a string and not a list
                file_path = file_item[0] if isinstance(file_item, (list, tuple)) and file_item else file_item
                file_path = str(file_path) if file_path is not None else ''
                
                # Skip invalid paths
                if not file_path or not isinstance(file_path, str):
                    print(f"Warning: Invalid file path in group {group_id}: {file_path}")
                    continue
                
                try:
                    if os.path.exists(file_path):
                        file_size = round(os.path.getsize(file_path) / 1024, 2)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        file_size = 0
                        mod_time = 'N/A'
                        print(f"Warning: File not found: {file_path}")
                except Exception as e:
                    print(f"Warning: Error processing file {file_path}: {str(e)}")
                    file_size = 0
                    mod_time = 'N/A'
                rows.append([
                    group_id,
                    file_path,
                    file_size,
                    mod_time,
                    'Yes' if i == 0 else 'No'
                ])
        
        # Write to CSV
        try:
            # Create a safe copy of the file path
            save_path = str(file_path)  # Make a copy of the original path
            
            # Ensure we have a valid file path
            if not save_path:
                raise ValueError("No file path provided")
                
            # Normalize the path to handle any path separators or other issues
            save_path = os.path.normpath(save_path.strip())
            
            # Ensure the directory exists
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
            
            # Ensure we have a .csv extension
            base, ext = os.path.splitext(save_path)
            if not ext or ext.lower() != '.csv':
                save_path = f"{base}.csv"
                
            # Debug output
            print(f"DEBUG: Final save path before writing: {save_path}")
            print(f"DEBUG: Save directory: {os.path.dirname(save_path)}")
            print(f"DEBUG: File exists before save: {os.path.exists(save_path)}")
            print(f"DEBUG: About to write to file: {save_path}")
            
            # Ensure the directory exists
            save_dir = os.path.dirname(save_path)
            os.makedirs(save_dir, exist_ok=True)
            
            # Debug output
            print(f"DEBUG: Final save path: {save_path}")
            print(f"DEBUG: Save directory: {save_dir}")
            print(f"DEBUG: File exists before writing: {os.path.exists(save_path)}")
            
            # Create a temporary file first to ensure we can write
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"temp_{os.path.basename(save_path)}")
            
            try:
                # Write to temporary file first
                with open(temp_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
                
                # Verify the temporary file was created
                if not os.path.exists(temp_file):
                    raise IOError(f"Failed to create temporary file at {temp_file}")
                
                # Ensure the target directory exists
                os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
                
                # Copy the temporary file to the final location
                import shutil
                shutil.copy2(temp_file, save_path)
                
                # Verify the final file was created
                if not os.path.exists(save_path):
                    raise IOError(f"Failed to create final file at {save_path}")
                
                # Verify the file has the correct extension
                if not save_path.lower().endswith('.csv'):
                    raise ValueError(f"File was not saved with .csv extension: {save_path}")
                
                print(f"DEBUG: File exists after writing: {os.path.exists(save_path)}")
                print(f"DEBUG: File size after writing: {os.path.getsize(save_path) if os.path.exists(save_path) else 0} bytes")
                
                # Get absolute path and show success message
                abs_path = os.path.abspath(save_path)
                status_msg = f"Scan results saved to:\n{abs_path}"
                print(f"DEBUG: {status_msg}")
                
                if hasattr(self.app, 'show_status'):
                    self.app.show_status(status_msg, "success")
                
                return True
                
            finally:
                # Clean up the temporary file
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"Warning: Failed to remove temporary file {temp_file}: {str(e)}")
                
                # Ask if user wants to open the file
                if messagebox.askyesno(
                    "Save Successful", 
                    f"Scan results saved to:\n{abs_path}\n\nDo you want to open the file?"
                ):
                    try:
                        os.startfile(abs_path)  # Open the file with default application
                    except Exception as e:
                        print(f"DEBUG: Could not open file: {e}")
                        messagebox.showerror("Error", f"Could not open file: {e}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error writing CSV file: {str(e)}"
            print(error_msg)
            if hasattr(self.app, 'show_status'):
                self.app.show_status(error_msg, "error")
            messagebox.showerror("Error", f"Failed to save scan results: {str(e)}")
            return False
    
    def load_scan_results(self) -> Optional[Tuple[Dict, List, List]]:
        """
        Load scan results from a previously saved CSV file.
        
        Returns:
            Tuple containing (duplicates, all_pdf_files, problematic_files) if successful, None otherwise
        """
        try:
            # Set initial directory for file dialog
            documents_dir = os.path.join(os.path.expanduser('~'), 'Documents')
            initial_dir = self.last_save_dir if (self.last_save_dir and os.path.isdir(self.last_save_dir)) else documents_dir
            
            # Ask user to select a file
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir=initial_dir,
                title="Load Duplicate Scan Results"
            )
            
            if not file_path:  # User cancelled
                return None
                
            print(f"DEBUG: Loading scan results from: {file_path}")
            
            # Update last save directory
            self.last_save_dir = os.path.dirname(file_path)
            
            # Group files by group_id
            groups = {}
            all_files = set()
            
            # Read and parse the CSV file
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header
                
                # Validate header
                if not header or len(header) < 2:  # At least Group ID and File Path are required
                    raise ValueError("Invalid CSV format. Missing required columns.")
                
                # Process each row
                for row_num, row in enumerate(reader, 2):  # Start from line 2 (after header)
                    if not row:  # Skip empty rows
                        continue
                        
                    try:
                        if len(row) < 2:  # At least group_id and file_path are required
                            print(f"Warning: Skipping invalid row {row_num}: Not enough columns")
                            continue
                            
                        group_id = row[0].strip()
                        file_path = row[1].strip()
                        
                        if not group_id or not file_path:
                            print(f"Warning: Skipping row {row_num}: Missing group ID or file path")
                            continue
                            
                        # Initialize group if it doesn't exist
                        if group_id not in groups:
                            groups[group_id] = []
                        
                        # Add file to its group and to the all_files set
                        groups[group_id].append(file_path)
                        all_files.add(file_path)
                        
                    except Exception as e:
                        print(f"Warning: Error processing row {row_num}: {str(e)}")
                        continue
            
            if not groups:
                raise ValueError("No valid duplicate groups found in the CSV file.")
            
            # Convert groups to list of duplicate groups
            duplicates = list(groups.values())
            
            # For backward compatibility
            all_pdf_files = list(all_files)
            problematic_files = []
            
            # Update application state
            if hasattr(self.app, 'duplicates'):
                self.app.duplicates = duplicates
                self.app.all_pdf_files = all_pdf_files
                self.app.problematic_files = problematic_files
            
            # Update UI if the method exists
            if hasattr(self.app, 'update_results_ui'):
                self.app.update_results_ui()
            
            # Show success message
            success_msg = f"Loaded {len(duplicates)} duplicate groups from {os.path.basename(file_path)}"
            print(f"DEBUG: {success_msg}")
            
            if hasattr(self.app, 'show_status'):
                self.app.show_status(success_msg, "success")
            
            messagebox.showinfo(
                "Load Successful",
                f"Successfully loaded {len(duplicates)} duplicate groups\n"
                f"Total files: {len(all_files)}"
            )
            
            return duplicates, all_pdf_files, problematic_files
            
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
        except PermissionError:
            error_msg = f"Permission denied when accessing: {file_path}"
        except csv.Error as e:
            error_msg = f"Error reading CSV file: {str(e)}"
        except Exception as e:
            error_msg = f"Error loading scan results: {str(e)}"
        
        print(f"ERROR: {error_msg}")
        if hasattr(self.app, 'show_status'):
            self.app.show_status(error_msg, "error")
        messagebox.showerror("Error", error_msg)
        return None
