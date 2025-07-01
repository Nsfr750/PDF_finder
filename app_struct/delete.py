"""
Module for handling file deletion operations.
"""
import os
import time
from tkinter import messagebox

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None

class FileDeleter:
    """Handles file deletion operations with undo support."""
    
    def __init__(self, app):
        """Initialize the FileDeleter with a reference to the main application."""
        self.app = app
        self.max_undo_steps = getattr(app, 'max_undo_steps', 10)
    
    def delete_selected(self):
        """Delete the currently selected files."""
        try:
            selected_items = self.app.tree.selection()
            if not selected_items:
                self.app.show_status("No files selected for deletion", "warning")
                return
                
            # Ask for confirmation with file count
            confirm_msg = (
                f"Sei sicuro di voler eliminare {len(selected_items)} file?\n\n"
                "Questa azione non può essere annullata."
            )
            
            if not messagebox.askyesno("Conferma eliminazione", confirm_msg, icon='warning'):
                self.app.show_status("Eliminazione annullata", "info")
                return

            deleted_files = []
            failed_deletions = []
            
            for item in selected_items:
                try:
                    # Get file info from the tree item
                    item_values = self.app.tree.item(item)['values']
                    if not item_values:  # Skip if no values
                        continue
                        
                    # Get file path from first column and ensure it's a string
                    file_path = str(item_values[0])
                    
                    # Debug: print the file path we're trying to delete
                    print(f"Tentativo di eliminazione: {file_path}")
                    print(f"File esiste: {os.path.exists(file_path)}")
                    
                    # List of possible locations to search for the file
                    possible_paths = [file_path]  # Try the original path first
                    
                    # Try the directory of the last scan file
                    if hasattr(self.app, 'last_scan_file') and self.app.last_scan_file:
                        csv_dir = os.path.dirname(self.app.last_scan_file)
                        filename = os.path.basename(file_path)
                        possible_paths.append(os.path.join(csv_dir, filename))
                    
                    # Try the original scan directory if available
                    if hasattr(self.app, 'scan_dir') and self.app.scan_dir:
                        filename = os.path.basename(file_path)
                        possible_paths.append(os.path.join(self.app.scan_dir, filename))
                    
                    # Try the PDF directory on the desktop
                    desktop_pdf_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'PDF')
                    if os.path.exists(desktop_pdf_dir):
                        filename = os.path.basename(file_path)
                        possible_paths.append(os.path.join(desktop_pdf_dir, filename))
                    
                    # Try the current working directory as last resort
                    possible_paths.append(os.path.join(os.getcwd(), os.path.basename(file_path)))
                    
                    # Print the search paths for debugging after all paths are added
                    print(f"Percorsi di ricerca: {possible_paths}")
                    
                    # Try to find the first existing path
                    file_found = False
                    for path in possible_paths:
                        if os.path.exists(path):
                            file_path = path
                            file_found = True
                            print(f"Trovato file in: {file_path}")
                            break
                    
                    if not file_found:
                        raise FileNotFoundError(
                            f"Impossibile trovare il file in nessuna delle seguenti posizioni: "
                            f"{', '.join(possible_paths)}"
                        )
                    
                    # Initialize undo stack if it doesn't exist
                    if not hasattr(self.app, 'undo_stack'):
                        self.app.undo_stack = []
                    
                    # Store file info for potential undo
                    file_info = {
                        'path': file_path,
                        'values': item_values,
                        'item_id': item  # Store the tree item ID for restoration
                    }
                    
                    # Try to delete the file
                    try:
                        if send2trash is not None:
                            send2trash(file_path)
                        else:
                            os.remove(file_path)
                        
                        # Remove from tree
                        self.app.tree.delete(item)
                        deleted_files.append(file_info)
                        
                        # Remove from duplicates list
                        if hasattr(self.app, 'duplicates'):
                            self.app.duplicates = [
                                group for group in self.app.duplicates 
                                if not any(file_path == f[0] if isinstance(f, (list, tuple)) else file_path == f 
                                         for f in group)
                            ]
                            
                    except Exception as e:
                        error_msg = f"Errore durante l'eliminazione di {os.path.basename(file_path)}: {str(e)}"
                        print(error_msg)
                        failed_deletions.append((file_path, str(e)))
                        
                except Exception as e:
                    error_msg = f"Errore durante l'elaborazione del file: {str(e)}"
                    print(error_msg)
                    failed_deletions.append((f"Item {item}", str(e)))
            
            # Update undo stack
            if deleted_files:
                self.app.undo_stack.append({
                    'type': 'delete',
                    'files': deleted_files,
                    'timestamp': time.time()
                })
                
                # Limit undo stack size
                if hasattr(self.app, 'max_undo_steps'):
                    if len(self.app.undo_stack) > self.max_undo_steps:
                        self.app.undo_stack.pop(0)
                
                # Update UI
                if hasattr(self.app, 'menu_manager') and hasattr(self.app.menu_manager, 'update_undo_menu_item'):
                    self.app.menu_manager.update_undo_menu_item('normal')
            
            # Show appropriate status message
            if deleted_files and not failed_deletions:
                self.app.show_status(f"Eliminati {len(deleted_files)} file con successo", "success")
            elif deleted_files and failed_deletions:
                self.app.show_status(
                    f"Eliminati {len(deleted_files)} file, "
                    f"errore nell'eliminazione di {len(failed_deletions)} file",
                    "warning"
                )
            else:
                self.app.show_status("Impossibile eliminare i file selezionati", "error")
                
            # Log any failures
            for file_path, error in failed_deletions:
                print(f"Errore durante l'eliminazione di {os.path.basename(file_path)}: {error}")
                
        except Exception as e:
            error_msg = f"Errore durante l'eliminazione: {str(e)}"
            print(error_msg)
            self.app.show_status(error_msg, "error")
