import os
import logging
import psutil
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QMessageBox, QCheckBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer
import send2trash
# Import language manager
from ..lang.lang_manager import SimpleLanguageManager

logger = logging.getLogger('PDFDuplicateFinder')

class DeleteConfirmationDialog(QDialog):
    """Dialog to confirm file deletion."""
    def __init__(self, file_paths, parent=None, title=None, message=None):
        super().__init__(parent)
        self.language_manager = SimpleLanguageManager()
        self.tr = self.language_manager.tr
        self.file_paths = file_paths if isinstance(file_paths, list) else [file_paths]
        self.permanently = False
        self.setWindowTitle(title or self.tr("delete.confirm_deletion", "Confirm Deletion"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        
        # Warning message
        if message:
            msg = message
        elif len(self.file_paths) == 1:
            msg = self.tr(
                "delete.confirm_single_file", 
                "Are you sure you want to delete this file?\n\n{filename}"
            ).format(filename=os.path.basename(self.file_paths[0]))
        else:
            file_list = "\n".join(f"• {os.path.basename(f)}" for f in self.file_paths[:5])
            if len(self.file_paths) > 5:
                file_list += "\n• ..." + self.tr("delete.and_x_more", "and {count} more").format(count=len(self.file_paths) - 5)
            msg = self.tr(
                "delete.confirm_multiple_files", 
                "Are you sure you want to delete {count} files?\n\n{file_list}"
            ).format(count=len(self.file_paths), file_list=file_list)
            
        label = QLabel(msg)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Permanently delete option
        self.permanent_check = QCheckBox(self.tr(
            "delete.permanently_delete", 
            "Permanently delete (bypass recycle bin)"
        ))
        self.permanent_check.stateChanged.connect(self.toggle_permanent)
        layout.addWidget(self.permanent_check)
        
        # Warning for permanent deletion
        self.warning_label = QLabel(f"<span style='color: red;'>{self.tr('delete.permanent_warning', 'Warning: Files will be permanently deleted and cannot be recovered!')}</span>")
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)
        
        # Buttons
        button_box = QHBoxLayout()
        
        cancel_btn = QPushButton(self.tr("common.cancel", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        
        delete_btn = QPushButton(self.tr("common.delete", "Delete"))
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(self.accept)
        
        button_box.addStretch()
        button_box.addWidget(cancel_btn)
        button_box.addWidget(delete_btn)
        
        layout.addLayout(button_box)
    
    def toggle_permanent(self, state):
        """Toggle the permanent deletion warning."""
        self.permanently = state == Qt.CheckState.Checked
        self.warning_label.setVisible(self.permanently)
    
    def move_to_trash(self):
        """Return True if files should be moved to trash instead of permanent deletion."""
        return not self.permanently

def _get_process_using_file(file_path):
    """Try to find which process is using the given file."""
    if not os.path.exists(file_path):
        return SimpleLanguageManager().tr("delete.unknown_file_not_found", "Unknown (file not found)")
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                if proc.info['open_files']:
                    for file in proc.info['open_files']:
                        if file.path.lower() == os.path.abspath(file_path).lower():
                            return SimpleLanguageManager().tr(
                                "delete.process_using_file", 
                                "{process_name} (PID: {pid})"
                            ).format(process_name=proc.info['name'], pid=proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logger.debug(SimpleLanguageManager().tr("delete.error_checking_processes", "Error checking processes for file {file_path}: {error}").format(
            file_path=file_path, error=e
        ))
    
    return SimpleLanguageManager().tr("delete.unknown_process", "Unknown process")

def _show_file_in_use_dialog(parent, file_path, process_info):
    """Show a dialog when a file is in use."""
    tr = SimpleLanguageManager().tr
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle(tr("delete.file_in_use_title", "File in Use"))
    msg.setText(tr(
        "delete.cannot_delete_file", 
        "Cannot delete file: {filename}"
    ).format(filename=os.path.basename(file_path)))
    msg.setInformativeText(tr(
        "delete.file_in_use_message", 
        "The file is being used by another program.\n\n"
        "Process: {process_info}\n"
        "Location: {location}"
    ).format(process_info=process_info, location=os.path.dirname(file_path)))
    
    retry_btn = msg.addButton(tr("common.retry", "&Retry"), QMessageBox.ButtonRole.ActionRole)
    skip_btn = msg.addButton(tr("common.skip", "&Skip"), QMessageBox.ButtonRole.RejectRole)
    close_btn = msg.addButton(tr("common.close", "&Close"), QMessageBox.ButtonRole.AcceptRole)
    
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
    tr = SimpleLanguageManager().tr
    
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
            logger.warning(tr("delete.file_does_not_exist", "File does not exist: {path}").format(path=path))
    
    if not existing_files:
        return 0, len(non_existent)
    
    # Show confirmation dialog
    dialog = DeleteConfirmationDialog(
        existing_files,
        parent=parent,
        title=tr("delete.confirm_deletion", "Confirm Deletion"),
        message=tr(
            "delete.confirm_deletion_message", 
            "Are you sure you want to delete {count} file(s)?"
        ).format(count=len(existing_files))
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
                        logger.info(tr("delete.permanently_deleted", "Permanently deleted: {path}").format(path=file_path))
                    except PermissionError as perm_error:
                        last_error = str(perm_error)
                        process_info = _get_process_using_file(file_path)
                        error_msg = tr(
                            "delete.permission_denied", 
                            "Permission denied while deleting {filename}. "
                        ).format(filename=os.path.basename(file_path))
                        
                        if process_info != tr("delete.unknown_process", "Unknown process"):
                            error_msg += tr(
                                "delete.file_in_use_by", 
                                "The file is being used by: {process_info}"
                            ).format(process_info=process_info)
                        else:
                            error_msg += tr(
                                "delete.file_in_use_generic", 
                                "The file might be in use or you don't have permission to delete it."
                            )
                        
                        # Show error to user
                        if retry_count == max_retries:  # Only show on last attempt
                            QMessageBox.information(
                                parent,
                                tr("delete.delete_failed", "Delete Failed"),
                                error_msg
                            )
                else:
                    try:
                        send2trash.send2trash(file_path)
                        deleted = True
                        success += 1
                        logger.info(tr("delete.moved_to_recycle_bin", "Moved to recycle bin: {path}").format(path=file_path))
                    except Exception as trash_error:
                        last_error = str(trash_error)
                        logger.warning(tr("delete.recycle_bin_operation_failed", "Recycle bin operation failed for {path}: {error}").format(
                            path=file_path, error=last_error
                        ))
                        
                        # If recycle bin fails, ask user if they want to try permanent deletion
                        if retry_count == 0:  # Only ask once per file
                            msg = QMessageBox(parent)
                            msg.setIcon(QMessageBox.Icon.Warning)
                            msg.setWindowTitle(tr("delete.recycle_bin_failed", "Recycle Bin Failed"))
                            msg.setText(tr(
                                "delete.cannot_move_to_recycle_bin", 
                                "Could not move to Recycle Bin: {filename}"
                            ).format(filename=os.path.basename(file_path)))
                            msg.setInformativeText(tr(
                                "delete.recycle_bin_operation_failed_message", 
                                "The file could not be moved to the Recycle Bin.\n"
                                "Error: {error}\n\n"
                                "Would you like to permanently delete the file instead?"
                            ).format(error=last_error))
                            
                            permanent_btn = msg.addButton(tr("delete.permanently_delete", "Permanently Delete"), QMessageBox.ButtonRole.YesRole)
                            skip_btn = msg.addButton(tr("common.skip", "Skip"), QMessageBox.ButtonRole.NoRole)
                            retry_btn = msg.addButton(tr("common.retry", "Retry"), QMessageBox.ButtonRole.ResetRole)
                            
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
                logger.error(tr("delete.unexpected_error_deleting", "Unexpected error deleting {path}: {error}").format(
                    path=file_path, error=last_error
                ))
                retry_count += 1
                if retry_count > max_retries:
                    break
                time.sleep(retry_delay)
        
        if not deleted:
            failed += 1
            logger.error(tr("delete.failed_to_delete", "Failed to delete {path} after {max_retries} attempts").format(
                path=file_path, max_retries=max_retries
            ))
            if last_error:
                logger.error(tr("delete.last_error", "Last error: {error}").format(error=last_error))
    
    # Show summary of results
    if success > 0 or failed > 0:
        summary = []
        if success > 0:
            summary.append(tr("delete.successfully_deleted", "Successfully deleted: {count} file(s)").format(count=success))
        if failed > 0:
            summary.append(tr("delete.failed_to_delete_summary", "Failed to delete: {count} file(s)").format(count=failed))
        
        if parent and (success > 0 or failed > 0):
            QMessageBox.information(
                parent,
                tr("delete.deletion_complete", "Deletion Complete"),
                "\n".join(summary)
            )
    
    return success, failed
