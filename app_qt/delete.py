import os
import logging
import psutil
import time
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QMessageBox, QCheckBox, QApplication
)
from PySide6.QtCore import Qt, QTimer
import send2trash

logger = logging.getLogger('PDFDuplicateFinder')

class DeleteConfirmationDialog(QDialog):
    """Dialog to confirm file deletion."""
    def __init__(self, file_paths, parent=None, title=None, message=None):
        super().__init__(parent)
        self.file_paths = file_paths if isinstance(file_paths, list) else [file_paths]
        self.permanently = False
        self.setWindowTitle(title or "Confirm Deletion")
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        
        # Warning message
        if message:
            msg = message
        elif len(self.file_paths) == 1:
            msg = f"Are you sure you want to delete this file?\n\n{os.path.basename(self.file_paths[0])}"
        else:
            file_list = "\n".join(f"• {os.path.basename(f)}" for f in self.file_paths[:5])
            if len(self.file_paths) > 5:
                file_list += "\n• ...and {len(self.file_paths) - 5} more"
            msg = f"Are you sure you want to delete {len(self.file_paths)} files?\n\n{file_list}"
            
        label = QLabel(msg)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Permanently delete option
        self.permanent_check = QCheckBox("Permanently delete (bypass recycle bin)")
        self.permanent_check.stateChanged.connect(self.toggle_permanent)
        layout.addWidget(self.permanent_check)
        
        # Warning for permanent deletion
        self.warning_label = QLabel("<span style='color: red;'>Warning: Files will be permanently deleted and cannot be recovered!</span>")
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)
        
        # Buttons
        button_box = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(self.accept)
        
        button_box.addStretch()
        button_box.addWidget(cancel_btn)
        button_box.addWidget(delete_btn)
        
        layout.addLayout(button_box)
    
    def toggle_permanent(self, state):
        """Toggle the permanent deletion warning."""
        self.permanently = state == Qt.Checked
        self.warning_label.setVisible(self.permanently)
    
    def move_to_trash(self):
        """Return True if files should be moved to trash instead of permanent deletion."""
        return not self.permanently

def _get_process_using_file(file_path):
    """Try to find which process is using the given file."""
    if not os.path.exists(file_path):
        return "Unknown (file not found)"
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                if proc.info['open_files']:
                    for file in proc.info['open_files']:
                        if file.path.lower() == os.path.abspath(file_path).lower():
                            return f"{proc.info['name']} (PID: {proc.info['pid']})"
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logger.debug(f"Error checking processes for file {file_path}: {e}")
    
    return "Unknown process"

def _show_file_in_use_dialog(parent, file_path, process_info):
    """Show a dialog when a file is in use."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("File in Use")
    msg.setText(f"Cannot delete file: {os.path.basename(file_path)}")
    msg.setInformativeText(
        f"The file is being used by another program.\n\n"
        f"Process: {process_info}\n"
        f"Location: {os.path.dirname(file_path)}"
    )
    
    retry_btn = msg.addButton("&Retry", QMessageBox.ActionRole)
    skip_btn = msg.addButton("&Skip", QMessageBox.RejectRole)
    close_btn = msg.addButton("&Close", QMessageBox.AcceptRole)
    
    msg.setDefaultButton(retry_btn)
    msg.exec()
    
    if msg.clickedButton() == retry_btn:
        return "retry"
    elif msg.clickedButton() == skip_btn:
        return "skip"
    return "close"

def delete_files(file_paths, parent=None, use_recycle_bin=True, max_retries=3, retry_delay=1):
    """
    Delete files with confirmation dialog and retry logic.
    
    Args:
        file_paths: List of file paths to delete
        parent: Parent widget for dialogs
        use_recycle_bin: If True, move to recycle bin instead of permanent deletion
        max_retries: Maximum number of retry attempts for locked files
        retry_delay: Delay between retry attempts in seconds
        
    Returns:
        tuple: (success_count, failed_count) - counts of successful and failed deletions
    """
    if not file_paths:
        return 0, 0
        
    # Filter out non-existent files
    existing_files = []
    non_existent = []
    
    for path in file_paths:
        if os.path.exists(path):
            existing_files.append(path)
        else:
            non_existent.append(path)
            logger.warning(f"File does not exist: {path}")
    
    if not existing_files:
        return 0, len(non_existent)
    
    # Show confirmation dialog
    dialog = DeleteConfirmationDialog(
        existing_files,
        parent=parent,
        title="Confirm Deletion",
        message=f"Are you sure you want to delete {len(existing_files)} file(s)?"
    )
    
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return 0, 0  # User cancelled
    
    permanently = not dialog.move_to_trash()
    success = 0
    failed = len(non_existent)  # Count non-existent files as failed
    
    # Delete the files
    remaining_files = existing_files.copy()
    
    while remaining_files:
        file_path = remaining_files.pop(0)
        retry_count = 0
        deleted = False
        
        while retry_count <= max_retries and not deleted:
            try:
                if permanently:
                    os.remove(file_path)
                else:
                    try:
                        send2trash.send2trash(file_path)
                    except Exception as trash_error:
                        # If recycle bin fails, ask user if they want to permanently delete
                        logger.warning(f"Recycle bin operation failed: {file_path}")
                        logger.debug(f"Recycle bin error: {trash_error}")
                        
                        # Show a more specific error message for OLE errors
                        error_msg = str(trash_error)
                        if hasattr(trash_error, 'winerror') and 'OLE' in str(trash_error):
                            error_msg = "The file couldn't be moved to the recycle bin. This can happen if the file is too large for the recycle bin or the recycle bin is disabled."
                        
                        # Ask user if they want to permanently delete
                        reply = QMessageBox.question(
                            parent,
                            "Recycle Bin Error",
                            f"{error_msg}\n\nDo you want to permanently delete the file instead?\n\n{os.path.basename(file_path)}",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                        )
                        
                        if reply == QMessageBox.StandardButton.Yes:
                            try:
                                os.remove(file_path)
                                logger.info(f"Permanently deleted after recycle bin failure: {file_path}")
                            except Exception as perm_error:
                                logger.error(f"Failed to permanently delete {file_path}: {perm_error}")
                                raise  # Re-raise to be handled by the outer exception handler
                        else:
                            # User chose not to delete, count as failed
                            raise Exception("User chose not to delete permanently")
                
                success += 1
                logger.info(f"{'Permanently ' if permanently else ''}Deleted: {file_path}")
                deleted = True
                
            except OSError as os_error:
                if hasattr(os_error, 'winerror') and os_error.winerror == 32:  # File in use
                    retry_count += 1
                    if retry_count > max_retries:
                        # Get process info and show dialog
                        process_info = _get_process_using_file(file_path)
                        result = _show_file_in_use_dialog(parent, file_path, process_info)
                        
                        if result == "retry":
                            retry_count = 0  # Reset retry counter
                            QApplication.processEvents()  # Keep UI responsive
                            time.sleep(retry_delay)
                            continue
                        elif result == "skip":
                            logger.warning(f"Skipped file in use: {file_path}")
                            failed += 1
                            break
                        else:  # Close
                            # Put remaining files back and exit
                            remaining_files.append(file_path)
                            return success, failed + len(remaining_files)
                    
                    # Simple retry with delay
                    time.sleep(retry_delay)
                    continue
                else:
                    # Other OS error
                    error_msg = str(os_error)
                    if hasattr(os_error, 'winerror'):
                        error_msg = f"Windows error {os_error.winerror}: {error_msg}"
                    logger.error(f"Failed to delete {file_path}: {error_msg}")
                    failed += 1
                    break
                    
            except Exception as e:
                logger.error(f"Unexpected error deleting {file_path}: {e}", exc_info=True)
                failed += 1
                break
    
    # Show results if we have a parent window
    if parent:
        if failed > 0 and success > 0:
            QMessageBox.warning(
                parent,
                "Deletion Complete",
                f"Successfully deleted {success} file(s).\n"
                f"Failed to delete {failed} file(s).\n\n"
                "Check the log for details."
            )
        elif failed > 0:
            QMessageBox.critical(
                parent,
                "Deletion Failed",
                f"Failed to delete {failed} file(s).\n\n"
                "Check the log for details."
            )
        elif success > 0:
            QMessageBox.information(
                parent,
                "Deletion Complete",
                f"Successfully deleted {success} file(s)."
            )
    
    return success, failed
