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
        last_error = None
        
        while retry_count <= max_retries and not deleted:
            try:
                if permanently or not use_recycle_bin:
                    try:
                        os.remove(file_path)
                        deleted = True
                        success += 1
                        logger.info(f"Permanently deleted: {file_path}")
                    except PermissionError as perm_error:
                        last_error = str(perm_error)
                        process_info = _get_process_using_file(file_path)
                        error_msg = f"Permission denied while deleting {os.path.basename(file_path)}. "
                        if process_info != "Unknown process":
                            error_msg += f"The file is being used by: {process_info}"
                        else:
                            error_msg += "The file might be in use or you don't have permission to delete it."
                        
                        # Show error to user
                        if retry_count == max_retries:  # Only show on last attempt
                            QMessageBox.warning(
                                parent,
                                "Delete Failed",
                                error_msg
                            )
                else:
                    try:
                        send2trash.send2trash(file_path)
                        deleted = True
                        success += 1
                        logger.info(f"Moved to recycle bin: {file_path}")
                    except Exception as trash_error:
                        last_error = str(trash_error)
                        logger.warning(f"Recycle bin operation failed for {file_path}: {last_error}")
                        
                        # If recycle bin fails, ask user if they want to try permanent deletion
                        if retry_count == 0:  # Only ask once per file
                            msg = QMessageBox(parent)
                            msg.setIcon(QMessageBox.Warning)
                            msg.setWindowTitle("Recycle Bin Failed")
                            msg.setText(f"Could not move to Recycle Bin: {os.path.basename(file_path)}")
                            msg.setInformativeText(
                                f"The file could not be moved to the Recycle Bin.\n"
                                f"Error: {last_error}\n\n"
                                "Would you like to permanently delete the file instead?"
                            )
                            
                            permanent_btn = msg.addButton("Permanently Delete", QMessageBox.YesRole)
                            skip_btn = msg.addButton("Skip", QMessageBox.NoRole)
                            retry_btn = msg.addButton("Retry", QMessageBox.ResetRole)
                            
                            msg.setDefaultButton(retry_btn)
                            msg.exec()
                            
                            if msg.clickedButton() == permanent_btn:
                                permanently = True
                                continue  # Retry with permanent deletion
                            elif msg.clickedButton() == skip_btn:
                                break  # Skip this file
                            # else retry
                        
                if not deleted:
                    retry_count += 1
                    if retry_count <= max_retries:
                        time.sleep(retry_delay)
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error deleting {file_path}: {last_error}")
                retry_count += 1
                if retry_count > max_retries:
                    break
                time.sleep(retry_delay)
        
        if not deleted:
            failed += 1
            logger.error(f"Failed to delete {file_path} after {max_retries} attempts")
            if last_error:
                logger.error(f"Last error: {last_error}")
    
    # Show summary of results
    if success > 0 or failed > 0:
        summary = []
        if success > 0:
            summary.append(f"Successfully deleted: {success} file(s)")
        if failed > 0:
            summary.append(f"Failed to delete: {failed} file(s)")
        
        if parent and (success > 0 or failed > 0):
            QMessageBox.information(
                parent,
                "Deletion Complete",
                "\n".join(summary)
            )
    
    return success, failed
