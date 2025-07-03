import os
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from send2trash import send2trash

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

def delete_files(file_paths, parent=None, use_recycle_bin=True):
    """
    Delete files with confirmation dialog.
    
    Args:
        file_paths: List of file paths to delete
        parent: Parent widget for dialogs
        use_recycle_bin: If True, move to recycle bin instead of permanent deletion
        
    Returns:
        tuple: (success_count, failed_count) - counts of successful and failed deletions
    """
    if not file_paths:
        return 0, 0
    
    # Convert single file path to list
    if not isinstance(file_paths, (list, tuple)):
        file_paths = [file_paths]
    
    # Filter out non-existent files
    existing_files = [f for f in file_paths if os.path.exists(f)]
    non_existent = set(file_paths) - set(existing_files)
    
    # Log non-existent files
    for file_path in non_existent:
        logger.warning(f"File not found, skipping: {file_path}")
    
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
    for file_path in existing_files:
        try:
            if permanently:
                os.remove(file_path)
            else:
                send2trash.send2trash(file_path)
                
            success += 1
            logger.info(f"{'Permanently ' if permanently else ''}Deleted: {file_path}")
            
        except Exception as e:
            failed += 1
            logger.error(f"Error deleting {file_path}: {e}")
    
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
