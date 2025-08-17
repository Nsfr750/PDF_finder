"""
Translation dictionaries for PDF_Finder.

This module contains all the translation strings used in the application,
organized by language code and then by functional area.
"""

# Base translations structure
TRANSLATIONS = {
    "en": {
        # Common UI elements
        "common": {
            "ok": "OK",
            "cancel": "Cancel",
            "yes": "Yes",
            "no": "No",
            "close": "Close",
            "save": "Save",
            "open": "Open",
            "delete": "Delete",
            "edit": "Edit",
            "help": "Help",
            "about": "About",
            "preferences": "Preferences",
            "exit": "Exit",
            "none": "None"
        },
        
        # Menu items
        "menu": {
            "file": "File",
            "edit": "Edit",
            "view": "View",
            "tools": "Tools",
            "help": "Help",
            "language": "Language"
        },
        
        # File Menu
        "file": {
            "open": "&Open Folder...",
            "save_results": "&Save Results...",
            "load_results": "&Load Results...",
            "settings": "&Settings...",
            "exit": "E&xit",
            "recent_folders": "Recent Folders",
            "clear_recent_folders": "Clear Recent Folders"
        },
        
        # Edit Menu
        "edit": {
            "delete": "&Delete",
            "select_all": "Select &All"
        },
        
        # View Menu
        "view": {
            "view_log": "View &Log...",
            "toolbar": "&Toolbar",
            "statusbar": "Status &Bar"
        },
        
        # Tools Menu
        "tools": {
            "check_updates": "Check for &Updates...",
            "pdf_viewer": "PDF &Viewer..."
        },
        
        # Help Menu
        "help": {
            "documentation": "&Documentation",
            "markdown_docs": "&Markdown Documentation",
            "sponsor": "&Sponsor...",
            "about": "&About..."
        },
        
        # Tooltips
        "tooltips": {
            "open_folder": "Open a folder to scan for duplicate PDFs",
            "save_results": "Save the current scan results to a file",
            "load_results": "Load previously saved scan results",
            "settings": "Configure application settings",
            "exit": "Exit the application",
            "view_log": "View the application log",
            "check_updates": "Check for application updates",
            "documentation": "Open the documentation in your web browser",
            "markdown_docs": "View markdown documentation",
            "sponsor": "Support the development of this application",
            "about": "Show information about this application",
            "delete": "Delete selected files",
            "select_all": "Select all files",
            "pdf_viewer": "Open PDF viewer"
        },
        
        # Status messages
        "status": {
            "ready": "Ready",
            "loading": "Loading...",
            "saving": "Saving...",
            "processing": "Processing..."
        },
        
        # Error messages
        "errors": {
            "file_not_found": "File not found: {}",
            "invalid_file": "Invalid file format",
            "save_error": "Error saving file"
        },
        
        # Application specific
        "app": {
            "name": "PDF Finder",
            "version": "Version {}",
            "search": "Search",
            "search_placeholder": "Search PDFs...",
            "no_results": "No results found",
            "select_folder": "Select Folder",
            "scanning": "Scanning...",
            "files_scanned": "{} files scanned",
            "duplicates_found": "{} duplicates found"
        },
        
        # About dialog
        "about": {
            "title": "About PDF Duplicate Finder",
            "app_name": "PDF Duplicate Finder",
            "version": "Version {version}",
            "logo_placeholder": "LOGO",
            "description": "A tool to find and manage duplicate PDF files on your computer.\n\n"
                          "PDF Duplicate Finder helps you save disk space by identifying and removing "
                          "duplicate PDF documents based on their content.",
            "system_info": "<b>System Information:</b>",
            "copyright": " 2025 Nsfr750\nThis software is licensed under the GPL3 License.",
            "github_button": "GitHub",
            "memory_info": "{available:.1f} GB available of {total:.1f} GB",
            "psutil_not_available": "psutil not available",
            "system_info_error": "Error getting system information: {error}",
            "system_info_html": """
                <html>
                <body>
                <h3>System Information</h3>
                <table>
                <tr><td><b>Operating System:</b></td><td>{os_info}</td></tr>
                <tr><td><b>Python Version:</b></td><td>{python_version}</td></tr>
                <tr><td><b>Qt Version:</b></td><td>{qt_version}</td></tr>
                <tr><td><b>PyQt Version:</b></td><td>{pyqt_version}</td></tr>
                <tr><td><b>Screen Resolution:</b></td><td>{resolution}</td></tr>
                <tr><td><b>Memory:</b></td><td>{memory_info}</td></tr>
                </table>
                </body>
                </html>
            """
        },
        
        # Help Dialog
        "help": {
            "window_title": "Help",
            "init_success": "Help dialog initialized successfully",
            "init_error": "Error initializing help dialog: {error}",
            "ui_init_error": "Error initializing UI: {error}",
            "language_changed": "UI retranslated to {language}",
            "translation_error": "Error translating key '{key}': {error}",
            "language_switched": "Language switched to {language}",
            "language_switch_error": "Error switching language: {error}",
            "link_open_error": "Error opening link {url}: {error}",
            "language": {
                "en": "English",
                "it": "Italiano"
            },
            "content": {
                "en": """
                    <h1>PDF Duplicate Finder - Help</h1>
                    
                    <h2>Getting Started</h2>
                    <p>PDF Duplicate Finder helps you find and manage duplicate PDF files on your computer.</p>
                    
                    <h2>How to Use</h2>
                    <ol>
                        <li>Click <b>Scan Folder</b> to select a directory to scan for duplicate PDFs</li>
                        <li>Review the duplicate groups found</li>
                        <li>Use the navigation buttons to move between groups and files</li>
                        <li>Select files and use <b>Keep</b> or <b>Delete</b> to manage duplicates</li>
                    </ol>
                    
                    <h2>Keyboard Shortcuts</h2>
                    <ul>
                        <li><b>Ctrl+O</b>: Open folder to scan</li>
                        <li><b>Ctrl+Q</b>: Quit the application</li>
                        <li><b>F1</b>: Show this help</li>
                    </ul>
                    
                    <h2>Need More Help?</h2>
                    <p>Visit our <a href="https://github.com/Nsfr750/PDF_Finder">GitHub repository</a> for more information and documentation.</p>
                """,
                "it": """
                    <h1>PDF Duplicate Finder - Aiuto</h1>
                    
                    <h2>Introduzione</h2>
                    <p>PDF Duplicate Finder ti aiuta a trovare e gestire i file PDF duplicati sul tuo computer.</p>
                    
                    <h2>Come Usare</h2>
                    <ol>
                        <li>Clicca su <b>Scansiona Cartella</b> per selezionare una directory da analizzare</li>
                        <li>Esamina i gruppi di duplicati trovati</li>
                        <li>Usa i pulsanti di navigazione per spostarti tra i gruppi e i file</li>
                        <li>Seleziona i file e usa <b>Mantieni</b> o <b>Elimina</b> per gestire i duplicati</li>
                    </ol>
                    
                    <h2>Scorciatoie da Tastiera</h2>
                    <ul>
                        <li><b>Ctrl+O</b>: Apri cartella da scansionare</li>
                        <li><b>Ctrl+Q</b>: Esci dall'applicazione</li>
                        <li><b>F1</b>: Mostra questo aiuto</li>
                    </ul>
                    
                    <h2>Serve altro aiuto?</h2>
                    <p>Visita la nostra <a href="https://github.com/Nsfr750/PDF_Finder">repository GitHub</a> per maggiori informazioni e documentazione.</p>
                """
            }
        },
        
        # Delete Dialog and Operations
        "delete": {
            # Confirmation dialogs
            "confirm_deletion": "Confirm Deletion",
            "confirm_single_file": "Are you sure you want to delete this file?\n\n{filename}",
            "confirm_multiple_files": "Are you sure you want to delete {count} files?\n\n{file_list}",
            "confirm_deletion_message": "Are you sure you want to delete {count} file(s)?",
            "and_x_more": "and {count} more",
            
            # Delete options
            "permanently_delete": "Permanently delete (bypass recycle bin)",
            "permanent_warning": "Warning: Files will be permanently deleted and cannot be recovered!",
            
            # File in use dialogs
            "file_in_use_title": "File in Use",
            "cannot_delete_file": "Cannot delete file: {filename}",
            "file_in_use_message": "The file is being used by another program.\n\nProcess: {process_info}\nLocation: {location}",
            "file_in_use_by": "The file is being used by: {process_info}",
            "file_in_use_generic": "The file might be in use or you don't have permission to delete it.",
            
            # Process information
            "unknown_file_not_found": "Unknown (file not found)",
            "unknown_process": "Unknown process",
            "process_using_file": "{process_name} (PID: {pid})",
            "error_checking_processes": "Error checking processes for file {file_path}: {error}",
            
            # Error messages
            "permission_denied": "Permission denied while deleting {filename}. ",
            "delete_failed": "Delete Failed",
            "file_does_not_exist": "File does not exist: {path}",
            "permanently_deleted": "Permanently deleted: {path}",
            "moved_to_recycle_bin": "Moved to recycle bin: {path}",
            "recycle_bin_failed": "Recycle Bin Failed",
            "cannot_move_to_recycle_bin": "Could not move to Recycle Bin: {filename}",
            "recycle_bin_operation_failed": "Recycle bin operation failed for {path}: {error}",
            "recycle_bin_operation_failed_message": "The file could not be moved to the Recycle Bin.\nError: {error}\n\nWould you like to permanently delete the file instead?",
            "unexpected_error_deleting": "Unexpected error deleting {path}: {error}",
            "failed_to_delete": "Failed to delete {path} after {max_retries} attempts",
            "last_error": "Last error: {error}",
            
            # Results/summary
            "deletion_complete": "Deletion Complete",
            "successfully_deleted": "Successfully deleted: {count} file(s)",
            "failed_to_delete_summary": "Failed to delete: {count} file(s)",
            
            # Buttons (already in common)
            # "common.cancel": "Cancel",
            # "common.delete": "Delete",
            # "common.retry": "&Retry",
            # "common.skip": "&Skip",
            # "common.close": "&Close"
        },
        
        # Dialogs
        "dialogs": {
            "confirm_delete": "Are you sure you want to delete the selected items?",
            "confirm_exit": "Do you want to save changes before exiting?",
            "select_folder": "Select a folder to scan for PDFs"
        },
        
        # Scan Manager
        "scan": {
            "no_pdf_files_found": "No PDF files found in the selected directories.",
            "found_pdf_files": "Found {count} PDF files to process",
            "skipping_nonexistent_file": "Skipping non-existent file: {path}",
            "could_not_extract_info": "Could not extract info from {path}",
            "created_temp_dir": "Created temporary directory: {path}",
            "could_not_calculate_hash": "Could not calculate image hash for {path}: {error}",
            "could_not_delete_temp_file": "Could not delete temporary file {path}: {error}",
            "error_processing_file": "Error processing {path}: {error}",
            "processed_file": "Processed: {path}",
            "finding_duplicates": "Finding duplicate PDFs...",
            "found_duplicate_groups": "Found {count} groups of duplicates",
            "error_in_scan_worker": "Error in scan worker:",
            "scan_error_message": "An error occurred during scanning: {error}",
            "cleaned_up_temp_dir": "Cleaned up temporary directory: {path}",
            "could_not_remove_temp_dir": "Could not remove temporary directory {path}: {error}",
            "scanning_dialog_text": "Scanning for duplicate PDFs...",
            "scanning_title": "Scanning",
            "scanning_progress": "Scanning... ({current}/{total} files)",
            "scan_completed": "Scan completed. Found {count} duplicate groups.",
            "scan_error_title": "Scan Error",
            "no_pdf_files": "No PDF files found in the selected directories.",
            "non_existent_file": "Skipping non-existent file: {file}",
            "error_extracting_info": "Could not extract info from {file}",
            "error_processing_file": "Error processing {file}: {error}",
            "error_during_scan": "An error occurred during scanning: {error}",
            "error_calculating_image_hash": "Could not calculate image hash for {file}: {error}",
            "error_deleting_temp_file": "Could not delete temporary file {file}: {error}",
            "error_cleanup_temp_dir": "Could not remove temporary directory {dir}: {error}",
            "found_pdf_files": "Found {count} PDF files to process",
            "finding_duplicates": "Finding duplicate PDFs...",
            "found_duplicate_groups": "Found {count} groups of duplicates",
            "processed_file": "Processed: {file}",
            "created_temp_dir": "Created temporary directory: {dir}",
            "cleanup_temp_dir": "Cleaned up temporary directory: {dir}",
            "error_in_scan_worker": "Error in scan worker:",
            "completed_groups": "Scan completed. Found {count} duplicate groups.",
            "scanning_title": "Scanning",
            "scanning_message": "Scanning for duplicate PDFs...",
            "scanning_progress": "Scanning... ({current}/{total} files)",
            "error_title": "Scan Error",
        },
        
        # File List Widget
        "file_list": {
            # Column headers
            "column_name": "Name",
            "column_size": "Size",
            "column_pages": "Pages",
            
            # Group titles and tooltips
            "group_title": "Duplicate Group {group_num} ({file_count} files)",
            "group_tooltip": "<b>Group {group_num}: {file_count} duplicate files</b><br>Size: {size}{savings}",
            "space_savings": "Space savings: {savings}",
            
            # Page count strings
            "pages_single": "{count} page",
            "pages_multiple": "{count} pages",
            
            # Context menu actions
            "action_expand_all": "Expand All",
            "action_collapse_all": "Collapse All",
            "action_open_all": "Open All in Group",
            "action_show_all": "Show All in Explorer",
            "action_open_file": "Open File",
            "action_show_in_explorer": "Show in Explorer",
            
            # File size formatting
            "size_bytes": "{size} B",
            "size_kb": "{size:.1f} KB",
            "size_mb": "{size:.1f} MB",
            "size_gb": "{size:.1f} GB"
        },
        
        # Recent Folders
        "recent_folders": {
            "clear_recent": "Clear Recent Folders",
            "no_recent_folders": "No recent folders"
        },
        
        # Recent Files Management
        "recents": {
            "cannot_add_nonexistent_path": "Cannot add non-existent path to recents: {path}",
            "error_loading": "Error loading recent files: {error}",
            "error_saving": "Error saving recent files: {error}",
            "clear_recent_files": "Clear Recent Files",
            "clear_recent_files_confirm": "Are you sure you want to clear all recent files?",
            "no_recent_files": "No recent files",
            "recent_files": "Recent Files",
            "open_recent": "Open Recent",
            "file_not_found": "File not found: {path}",
            "error_opening_file": "Error opening file: {error}",
            "max_recent_files_reached": "Maximum number of recent files reached. Oldest items will be removed.",
            "cannot_add_nonexistent": "Cannot add non-existent path to recents: {path}",
        },
        
        # Language Manager
        "language_manager": {
            "initializing": "Initializing LanguageManager...",
            "settings_file": "Settings file: {file}",
            "current_language": "Current language from settings: {lang}",
            "language_not_available": "Language '{lang}' not available, falling back to '{default_lang}'",
            "initialized": "LanguageManager initialized with language: {lang}",
            "loaded_translations": "Loaded main translations for languages: {languages}",
            "merged_help_translations": "Merged help translations for languages: {languages}",
            "load_translations_error": "Failed to load translations: {error}",
            "unsupported_language": "Attempted to set unsupported language: {lang}",
            "language_changing": "Changing language from {old_lang} to {new_lang}",
            "translation_error": "Error translating key '{key}': {error}"
        },
        "language": {
            "english": "English",
            "italian": "Italiano"
        },
        
        # Log Viewer
        "log_viewer": {
            "window_title": "Log Viewer",
            "filter_by_level": "Filter by level:",
            "level_all": "ALL",
            "level_debug": "DEBUG",
            "level_info": "INFO",
            "level_warning": "WARNING",
            "level_error": "ERROR",
            "level_critical": "CRITICAL",
            "search": "Search:",
            "search_placeholder": "Search in logs...",
            "refresh": "Refresh",
            "clear_logs": "Clear Logs",
            "save_as": "Save As...",
            "file_not_found": "Log file not found: {file}",
            "entries_loaded": "Loaded {count} log entries",
            "error": "Error",
            "load_error": "Failed to load log file: {error}",
            "showing_entries": "Showing {filtered} of {total} entries",
            "filter_error": "Error filtering logs: {error}",
            "confirm_clear": "Confirm Clear",
            "confirm_clear_message": "Are you sure you want to clear all log entries? This cannot be undone.",
            "logs_cleared": "Logs cleared",
            "clear_error": "Failed to clear log file: {error}",
            "no_entries": "No Entries",
            "no_entries_message": "No log entries to save.",
            "save_logs": "Save Logs",
            "log_files": "Log Files (*.log);;All Files (*)",
            "save_success": "Save Successful",
            "save_success_message": "Logs saved to: {file}",
            "save_error": "Failed to save log file: {error}"
        },
        
        # Main Window
        "main_window": {
            "title": "PDF Duplicate Finder",
            "retranslate_error": "Error in retranslate callback: {error}",
            "scanning_folder": "Scanning folder: {folder}",
            "scan_complete": "Scan complete. Found {count} PDF files.",
            "no_pdfs_found": "No PDF files found in the selected folder.",
            "duplicates_found": "Found {count} potential duplicate groups.",
            "processing_file": "Processing: {file}",
            "error_loading_file": "Error loading file: {file}",
            "file_not_found": "File not found: {file}",
            "invalid_pdf": "Invalid PDF file: {file}",
            "no_duplicates_found": "No duplicate PDFs found.",
            "scan_cancelled": "Scan cancelled by user.",
            "saving_results": "Saving results...",
            "results_saved": "Results saved to: {path}",
            "deleting_files": "Deleting {count} files...",
            "files_deleted": "{count} files deleted successfully.",
            "confirm_delete": "Are you sure you want to delete {count} selected files?",
            "confirm_delete_title": "Confirm Deletion",
            "file_in_use": "File is in use and cannot be deleted: {file}",
            "permission_denied": "Permission denied when trying to delete: {file}",
            "deletion_cancelled": "File deletion cancelled by user.",
            "deletion_complete": "Deletion complete.",
            "deletion_summary": "Deleted {deleted} of {total} files successfully.",
            "view_logs": "View Logs",
            "open_containing_folder": "Open Containing Folder",
            "file_properties": "File Properties"
        },
        
        # Menu Items
        "menu": {
            "file": "File",
            "file_open": "Open Folder",
            "file_exit": "Exit",
            "tools": "Tools",
            "language": "Language",
            "help": "Help",
            "help_about": "About"
        },
        
        # Dialog Titles and Messages
        "dialog": {
            "select_folder": "Select Folder to Scan",
            "about_title": "About PDF Duplicate Finder",
            "about_text": "<h2>PDF Duplicate Finder</h2><p>Version: {version}</p><p>Find and manage duplicate PDF files on your computer.</p><p> 2025 PDF Duplicate Finder</p>"
        },
        
        # Error Messages
        "error": {
            "not_implemented": "Subclasses must implement {method} method"
        },
        
        # PDF Utilities
        "pdf_utils": {
            "metadata_extraction_warning": "Could not extract metadata from {file}: {error}",
            "file_info_error": "Error getting info for {file}: {error}",
            "hash_calculation_error": "Error calculating hash for {file}: {error}",
            "image_hash_error": "Error calculating image hash for {file}: {error}",
            "page_extraction_error": "Error extracting first page from {file}: {error}",
            "using_preprocessed_files": "Using {count} pre-processed files",
            "file_access_warning": "Could not access file {file}: {error}",
            "directory_access_error": "Error accessing directory {dir}: {error}",
            "found_pdf_files": "Found {count} PDF files to process",
            "temp_file_cleanup_warning": "Could not delete temporary file {file}: {error}",
            "processing_progress": "Processed {current}/{total} files",
            "file_processing_error": "Error processing file {file}: {error}",
            "potential_duplicates_found": "Found {count} potential duplicate groups based on size",
            "duplicate_groups_found": "Found {count} duplicate groups",
            "duplicate_finding_error": "Error finding duplicates: {error}",
            "no_duplicates_found": "No duplicate PDFs found in the specified directory",
            "scan_completed": "Scan completed. Found {count} duplicate groups.",
            "error_scanning": "Error scanning directory: {error}",
            "invalid_threshold": "Invalid threshold value. Must be between 0.0 and 1.0",
            "invalid_hash_size": "Invalid hash size. Must be a positive integer",
            "invalid_directory": "Directory does not exist: {path}",
            "no_pdf_files_found": "No PDF files found in the specified directory"
        },
        
        # PDF Preview Widget
        "preview": {
            "window_title": "PDF Preview",
            "window_title_with_file": "PDF Preview - {filename}",
            "file_not_found": "File not found",
            "no_pages_found": "No pages found in PDF",
            "error_loading_pdf": "Error loading PDF: {error}",
            "error_displaying_page": "Error displaying page: {error}",
            "page_status": "Page {current} of {total}"
        },
        
        # PDF Viewer
        "pdf_viewer": {
            # Window titles
            "window_title": "PDF Viewer",
            "window_title_with_file": "{} - PDF Viewer",
            
            # Actions
            "actions": {
                "open": "Open",
                "zoom_in": "Zoom In",
                "zoom_out": "Zoom Out",
                "fit_width": "Fit Width",
                "fit_page": "Fit Page",
                "prev_page": "Previous",
                "next_page": "Next"
            },
            
            # Dialogs
            "dialogs": {
                "open_file": "Open PDF"
            },
            
            # File filters
            "file_filter": "PDF Files (*.pdf)",
            
            # Status messages
            "status": {
                "page_of": "Page {current} of {total} | {width} x {height} | {zoom:.0%}"
            },
            
            # Page navigation
            "page_number": "Page {current} of {total}",
            
            # Error messages
            "errors": {
                "open_error": "Error Opening PDF",
                "could_not_open": "Could not open {file}: {error}",
                "render_error": "Error rendering page: {error}",
                "invalid_page": "Invalid page number",
                "file_not_found": "File not found: {}"
            }
        },
        
        # PDF Scanner
        "scanner": {
            # Status messages
            "status": {
                "scanning": "Scanning PDF files...",
                "finding_duplicates": "Finding duplicates...",
                "complete": "Scan complete!",
                "cancelled": "Scan cancelled",
                "processing_file": "Processing {current}/{total}: {file}",
                "found_duplicates": "Found {count} duplicate groups"
            },
            # Error messages
            "error": {
                "prefix": "Error: {error}",
                "during_scan": "Error during scanning: {error}",
                "processing_file": "Error processing {path}: {error}",
                "invalid_directory": "Invalid directory: {path}",
                "permission_denied": "Permission denied: {path}",
                "file_too_large": "File too large: {path} ({size} > {max_size})",
                "file_too_small": "File too small: {path} ({size} < {min_size})",
                "invalid_pdf": "Invalid PDF file: {path}",
                "unknown_error": "Unknown error: {error}"
            },
            # Warning messages
            "warning": {
                "access_denied": "Cannot access {path}: {error}",
                "loading_pdf": "Error loading PDF {path}: {error}",
                "skipping_file": "Skipping file {path}: {reason}",
                "empty_file": "Empty file: {path}",
                "encrypted_pdf": "Encrypted PDF (not supported): {path}",
                "corrupt_pdf": "Corrupt PDF file: {path}"
            },
            # Success messages
            "success": {
                "scan_complete": "Scan complete. Found {groups} duplicate groups with {files} files.",
                "space_savings": "Potential space savings: {size} MB",
                "files_processed": "Processed {count} files in {time:.1f} seconds",
                "duplicates_found": "Found {count} potential duplicates"
            },
            # UI elements
            "ui": {
                "start_scan": "Start Scan",
                "stop_scan": "Stop Scan",
                "scan_progress": "Scan Progress",
                "scan_results": "Scan Results",
                "no_duplicates_found": "No duplicate files found.",
                "select_files_to_compare": "Select files to compare",
                "compare_selected": "Compare Selected",
                "select_all": "Select All",
                "deselect_all": "Deselect All",
                "delete_selected": "Delete Selected"
            },
            # Scanner related strings
            "scanning_pdfs": "Scanning PDF files...",
            "finding_duplicates": "Finding duplicates...",
            "scan_complete": "Scan complete!",
            "scan_error": "Error during scanning: {error}",
            "error_prefix": "Error: {error}",
            "access_error": "Cannot access {path}: {error}",
            "processing_error": "Error processing {path}: {error}",
            "load_error": "Error loading PDF {file}: {error}",
            "file_processed": "Processed {current}/{total} files",
            "duplicates_found": "Found {count} duplicate groups",
            "space_savings": "Potential space savings: {size} MB"
        },
        
        # Search and Duplicates
        "search_dup": {
            "header": "Duplicate Files",
            "no_duplicates": "No duplicate files found.",
            "group": {
                "singular": "1 duplicate file",
                "plural": "{count} duplicate files"
            },
            "tooltip": {
                "file": "File: {path}",
                "size": "Size: {size:,} bytes",
                "modified": "Modified: {date}",
                "empty_group": "No duplicate files in this group",
                "group": "Click to expand/collapse - {count} duplicate files"
            },
            "original_indicator": "(Original)",
            "context_menu": {
                "open_file": "Open File",
                "open_containing_folder": "Open Containing Folder",
                "mark_as_original": "Mark as Original",
                "delete_file": "Delete File",
                "compare_files": "Compare Files"
            },
            "status": {
                "scanning": "Scanning for duplicates...",
                "completed": "Scan completed. Found {groups} duplicate groups with {files} files.",
                "no_duplicates_found": "No duplicate files found.",
                "processing": "Processing {current}/{total} files...",
                "cancelled": "Scan cancelled by user.",
                "error": "Error scanning for duplicates: {error}",
                "deleting": "Deleting {count} files...",
                "deleted": "Successfully deleted {count} files.",
                "delete_error": "Error deleting files: {error}",
                "marking_original": "Marking file as original...",
                "marked_original": "File marked as original.",
                "mark_original_error": "Error marking file as original: {error}"
            },
            "confirmation": {
                "delete_title": "Confirm Deletion",
                "delete_message": "Are you sure you want to delete {count} file(s)?\nThis action cannot be undone.",
                "delete_button": "Delete",
                "cancel_button": "Cancel"
            },
            "columns": {
                "filename": "Filename",
                "path": "Path",
                "size": "Size",
                "modified": "Modified",
                "status": "Status"
            },
            "file_actions": {
                "open": "Open",
                "open_folder": "Open Folder",
                "properties": "Properties",
                "copy_path": "Copy Path"
            },
            "group_actions": {
                "select_all": "Select All",
                "deselect_all": "Deselect All",
                "expand_all": "Expand All",
                "collapse_all": "Collapse All"
            },
            "view_options": {
                "show_originals_only": "Show Originals Only",
                "group_by_size": "Group by Size",
                "group_by_date": "Group by Date",
                "group_by_name": "Group by Name"
            },
            "filter": {
                "placeholder": "Filter duplicates...",
                "size_range": "Size Range",
                "date_range": "Date Range",
                "file_type": "File Type"
            }
        },
        
        # Sponsor Dialog
        "sponsor": {
            "window_title": "Support Development",
            "title": "Support PDF Duplicate Finder",
            "ways_to_support": "Ways to Support:",
            "other_ways": {
                "title": "Other Ways to Help:",
                "star": "Star the project on",
                "report": "Report bugs and suggest features",
                "share": "Share with others who might find it useful"
            },
            "message": "If you find this application useful, please consider supporting its development.\n\nYour support helps cover hosting costs and encourages further development.",
            "buttons": {
                "donate_paypal": "Donate with PayPal",
                "copy_monero": "Copy Monero Address",
                "copied": "Copied!"
            },
            "links": {
                "github_sponsors": "GitHub Sponsors",
                "paypal": "PayPal Donation"
            },
            "monero": {
                "label": "Monero:",
                "qr_tooltip": "Scan to donate XMR"
            },
            "qr_tooltip": "Scan to donate XMR"
        },
        
        # Update functionality
        "updates": {
            "window_title": "Check for Updates",
            "checking": "Checking for updates...",
            "update_available": "Version {latest_version} is available! (Current: {current_version})",
            "no_updates": "You're using the latest version ({current_version}).",
            "error_checking": "Error checking for updates: {error_msg}",
            "no_release_notes": "No release notes available.",
            "whats_new": "What's New in v",
            "buttons": {
                "download": "Download Update"
            }
        },
        
        # Markdown Viewer
        "markdown_viewer": {
            "window_title": "Documentation Viewer",
            "no_docs_dir_title": "Documentation Directory Not Found",
            "no_docs_dir_msg": "Created documentation directory at: {}",
            "no_files_title": "No Documentation Found",
            "no_files_msg": "No markdown (.md) files found in the documentation directory: {}",
            "no_files_in_dir_msg": "No markdown files found in the documentation directory: {}",
            "error_loading_file": "Error loading file: {}",
            "documentation": "&Documentation",
            "documentation_tooltip": "View documentation in markdown format"
        },
        
        # UI Components
        "ui": {
            # Preview widget
            "preview_placeholder": "Preview will be shown here",
            "preview_of": "Preview of: {file_path}",
            
            # Status bar
            "status_ready": "Ready",
            
            # File list
            "no_files_loaded": "No files loaded",
            "files_loaded": "{count} files loaded",
            "duplicates_found": "{count} duplicates found",
            "scan_complete": "Scan complete",
            "scan_cancelled": "Scan cancelled",
            "scan_error": "Error during scan: {error}",
            "deleting_files": "Deleting {count} files...",
            "deletion_complete": "Deletion complete",
            "deletion_error": "Error deleting files: {error}",
            "no_duplicates_found": "No duplicate files found"
        },
    },
    
    # Italian translations
    "it": {
        "common": {
            "ok": "OK",
            "cancel": "Annulla",
            "yes": "Sì",
            "no": "No",
            "close": "Chiudi",
            "save": "Salva",
            "open": "Apri",
            "delete": "Elimina",
            "edit": "Modifica",
            "help": "Aiuto",
            "about": "Informazioni",
            "preferences": "Preferenze",
            "exit": "Esci",
            "none": "nessuno"
        },
        
        # Menu items
        "menu": {
            "file": "File",
            "edit": "Modifica",
            "view": "Visualizza",
            "tools": "Strumenti",
            "help": "Aiuto",
            "language": "Lingua"
        },
        
        # File Menu
        "file": {
            "open": "&Apri cartella...",
            "save_results": "&Salva risultati...",
            "load_results": "&Carica risultati...",
            "settings": "&Impostazioni...",
            "exit": "&Esci",
            "recent_folders": "Cartelle Recenti",
            "clear_recent_folders": "Cancella Cronologia"
        },
        
        # Edit Menu
        "edit": {
            "delete": "&Elimina",
            "select_all": "Seleziona &Tutto"
        },
        
        # View Menu
        "view": {
            "view_log": "Visualizza &log...",
            "toolbar": "Barra &Strumenti",
            "statusbar": "Barra di &Stato"
        },
        
        # Tools Menu
        "tools": {
            "check_updates": "Cerca &aggiornamenti...",
            "pdf_viewer": "Visualizzatore &PDF..."
        },
        
        # Help Menu
        "help": {
            "documentation": "&Documentazione",
            "markdown_docs": "&Documentazione Markdown",
            "sponsor": "&Sostienici...",
            "about": "&Informazioni su..."
        },
        
        # Tooltips
        "tooltips": {
            "open_folder": "Apri una cartella per cercare PDF duplicati",
            "save_results": "Salva i risultati della scansione corrente in un file",
            "load_results": "Carica i risultati di una scansione precedente",
            "settings": "Configura le impostazioni dell'applicazione",
            "exit": "Esci dall'applicazione",
            "view_log": "Visualizza il registro dell'applicazione",
            "check_updates": "Controlla la presenza di aggiornamenti per l'applicazione",
            "documentation": "Apri la documentazione nel browser web predefinito",
            "markdown_docs": "Visualizza la documentazione in formato markdown",
            "sponsor": "Supporta lo sviluppo di questa applicazione",
            "about": "Mostra informazioni su questa applicazione",
            "delete": "Elimina i file selezionati",
            "select_all": "Seleziona tutti i file",
            "pdf_viewer": "Apri il visualizzatore PDF"
        },
        
        # Status messages
        "status": {
            "ready": "Pronto",
            "loading": "Caricamento...",
            "saving": "Salvataggio...",
            "processing": "Processamento..."
        },
        
        # Error messages
        "errors": {
            "file_not_found": "File non trovato: {}",
            "invalid_file": "Formato file non valido",
            "save_error": "Errore salvataggio file"
        },
        
        # Application specific
        "app": {
            "name": "PDF Finder",
            "version": "Versione {}",
            "search": "Cerca",
            "search_placeholder": "Cerca nei PDF...",
            "no_results": "Nessun risultato trovato",
            "select_folder": "Seleziona Cartella",
            "scanning": "Analisi in corso...",
            "files_scanned": "{} file analizzati",
            "duplicates_found": "{} duplicati trovati"
        },
        
        # About dialog
        "about": {
            "title": "Informazioni su PDF Duplicate Finder",
            "app_name": "PDF Duplicate Finder",
            "version": "Versione {version}",
            "logo_placeholder": "LOGO",
            "description": "Uno strumento per trovare e gestire i file PDF duplicati sul tuo computer.\n\n"
                          "PDF Duplicate Finder ti aiuta a risparmiare spazio su disco identificando e rimuovendo "
                          "i documenti PDF duplicati in base al loro contenuto.",
            "system_info": "<b>Informazioni sul sistema:</b>",
            "copyright": " 2025 Nsfr750\nQuesto software è rilasciato sotto licenza GPL3.",
            "github_button": "GitHub",
            "memory_info": "{available:.1f} GB disponibili di {total:.1f} GB",
            "psutil_not_available": "psutil non disponibile",
            "system_info_error": "Errore durante il recupero delle informazioni sul sistema: {error}",
            "system_info_html": """
                <html>
                <body>
                <h3>Informazioni sul sistema</h3>
                <table>
                <tr><td><b>Sistema operativo:</b></td><td>{os_info}</td></tr>
                <tr><td><b>Versione Python:</b></td><td>{python_version}</td></tr>
                <tr><td><b>Versione Qt:</b></td><td>{qt_version}</td></tr>
                <tr><td><b>Versione PyQt:</b></td><td>{pyqt_version}</td></tr>
                <tr><td><b>Risoluzione dello schermo:</b></td><td>{resolution}</td></tr>
                <tr><td><b>Memoria:</b></td><td>{memory_info}</td></tr>
                </table>
                </body>
                </html>
            """
        },
        
        # Help Dialog
        "help": {
            "window_title": "Aiuto",
            "init_success": "Finestra di aiuto inizializzata con successo",
            "init_error": "Errore durante l'inizializzazione della finestra di aiuto: {error}",
            "ui_init_error": "Errore durante l'inizializzazione dell'interfaccia utente: {error}",
            "language_changed": "Interfaccia tradotta in {language}",
            "translation_error": "Errore durante la traduzione dell'interfaccia: {error}",
            "language_switched": "Lingua cambiata in {language}",
            "language_switch_error": "Errore durante il cambio lingua: {error}",
            "link_open_error": "Errore durante l'apertura del link {url}: {error}",
            "language": {
                "en": "English",
                "it": "Italiano"
            }
        },
        
        # Recent Files Management
        "recents": {
            "cannot_add_nonexistent_path": "Impossibile aggiungere un percorso inesistente ai recenti: {path}",
            "error_loading": "Errore nel caricamento dei file recenti: {error}",
            "error_saving": "Errore nel salvataggio dei file recenti: {error}",
            "clear_recent_files": "Cancella file recenti",
            "clear_recent_files_confirm": "Sei sicuro di voler cancellare tutti i file recenti?",
            "no_recent_files": "Nessun file recente",
            "recent_files": "File recenti",
            "open_recent": "Apri recente",
            "file_not_found": "File non trovato: {path}",
            "error_opening_file": "Errore nell'apertura del file: {error}",
            "max_recent_files_reached": "Raggiunto il numero massimo di file recenti. I file più vecchi verranno rimossi.",
            "cannot_add_nonexistent": "Impossibile aggiungere un percorso inesistente ai recenti: {path}",
        },
        
        # Main Window
        "main_window": {
            "title": "PDF Duplicate Finder",
            "retranslate_error": "Errore nella ritraduzione dell'interfaccia: {error}",
            "scanning_folder": "Analisi della cartella: {folder}",
            "scan_complete": "Analisi completata. Trovati {count} file PDF.",
            "no_pdfs_found": "Nessun file PDF trovato nella cartella selezionata.",
            "duplicates_found": "Trovati {count} gruppi di potenziali duplicati.",
            "processing_file": "Elaborazione: {file}",
            "error_loading_file": "Errore nel caricamento del file: {file}",
            "file_not_found": "File non trovato: {file}",
            "invalid_pdf": "File PDF non valido: {file}",
            "no_duplicates_found": "Nessun PDF duplicato trovato.",
            "scan_cancelled": "Scansione annullata dall'utente.",
            "saving_results": "Salvataggio risultati...",
            "results_saved": "Risultati salvati in: {path}",
            "deleting_files": "Eliminazione di {count} file...",
            "files_deleted": "{count} file eliminati con successo.",
            "confirm_delete": "Sei sicuro di voler eliminare i {count} file selezionati?",
            "confirm_delete_title": "Conferma Eliminazione",
            "file_in_use": "Il file è in uso e non può essere eliminato: {file}",
            "permission_denied": "Permesso negato durante il tentativo di eliminare: {file}",
            "deletion_cancelled": "Eliminazione file annullata dall'utente.",
            "deletion_complete": "Eliminazione completata.",
            "deletion_summary": "Eliminati {deleted} file su {total} con successo.",
            "view_logs": "Visualizza Log",
            "open_containing_folder": "Apri cartella contenitore",
            "file_properties": "Proprietà file"
        },
        
        # Menu Items
        "menu": {
            "file": "File",
            "file_open": "Apri cartella",
            "file_exit": "Esci",
            "tools": "Strumenti",
            "language": "Lingua",
            "help": "Aiuto",
            "help_about": "Informazioni"
        },
        
        # Dialog Titles and Messages
        "dialog": {
            "select_folder": "Seleziona la cartella da analizzare",
            "about_title": "Informazioni su Cerca Duplicati PDF",
            "about_text": "<h2>Cerca Duplicati PDF</h2><p>Versione: {version}</p><p>Trova e gestisci i file PDF duplicati sul tuo computer.</p><p> 2025 Cerca Duplicati PDF</p>"
        },
        
        # Error Messages
        "error": {
            "not_implemented": "Le sottoclassi devono implementare il metodo {method}"
        },
        
        # PDF Utilities
        "pdf_utils": {
            "metadata_extraction_warning": "Impossibile estrarre i metadati da {file}: {error}",
            "file_info_error": "Errore nel recupero delle informazioni per {file}: {error}",
            "hash_calculation_error": "Errore nel calcolo dell'hash per {file}: {error}",
            "image_hash_error": "Errore nel calcolo dell'hash dell'immagine per {file}: {error}",
            "page_extraction_error": "Errore nell'estrazione della prima pagina da {file}: {error}",
            "using_preprocessed_files": "Utilizzo di {count} file pre-elaborati",
            "file_access_warning": "Impossibile accedere al file {file}: {error}",
            "directory_access_error": "Errore nell'accesso alla directory {dir}: {error}",
            "found_pdf_files": "Trovati {count} file PDF da elaborare",
            "temp_file_cleanup_warning": "Impossibile eliminare il file temporaneo {file}: {error}",
            "processing_progress": "Elaborati {current}/{total} file",
            "file_processing_error": "Errore nell'elaborazione del file {file}: {error}",
            "potential_duplicates_found": "Trovati {count} potenziali gruppi di duplicati in base alla dimensione",
            "duplicate_groups_found": "Trovati {count} gruppi di duplicati",
            "duplicate_finding_error": "Errore nella ricerca dei duplicati: {error}",
            "no_duplicates_found": "Nessun PDF duplicato trovato nella directory specificata",
            "scan_completed": "Scansione completata. Trovati {count} gruppi di duplicati.",
            "error_scanning": "Errore durante la scansione della directory: {error}",
            "invalid_threshold": "Valore di soglia non valido. Deve essere compreso tra 0.0 e 1.0",
            "invalid_hash_size": "Dimensione hash non valida. Deve essere un numero intero positivo",
            "invalid_directory": "La directory non esiste: {path}",
            "no_pdf_files_found": "Nessun file PDF trovato nella directory specificata"
        },
        
        # PDF Preview Widget (Italian)
        "preview": {
            "window_title": "Anteprima PDF",
            "window_title_with_file": "Anteprima PDF - {filename}",
            "file_not_found": "File non trovato",
            "no_pages_found": "Nessuna pagina trovata nel PDF",
            "error_loading_pdf": "Errore nel caricamento del PDF: {error}",
            "error_displaying_page": "Errore nella visualizzazione della pagina: {error}",
            "page_status": "Pagina {current} di {total}"
        },
        
        # PDF Viewer
        "pdf_viewer": {
            # Window titles
            "window_title": "Visualizzatore PDF",
            "window_title_with_file": "{} - Visualizzatore PDF",
            
            # Actions
            "actions": {
                "open": "Apri",
                "zoom_in": "Ingrandisci",
                "zoom_out": "Rimpicciolisci",
                "fit_width": "Adatta alla larghezza",
                "fit_page": "Adatta alla pagina",
                "prev_page": "Precedente",
                "next_page": "Successiva"
            },
            
            # Dialogs
            "dialogs": {
                "open_file": "Apri PDF"
            },
            
            # File filters
            "file_filter": "File PDF (*.pdf)",
            
            # Status messages
            "status": {
                "page_of": "Pagina {current} di {total} | {width} x {height} | {zoom:.0%}"
            },
            
            # Page navigation
            "page_number": "Pagina {current} di {total}",
            
            # Error messages
            "errors": {
                "open_error": "Errore nell'apertura del PDF",
                "could_not_open": "Impossibile aprire {file}: {error}",
                "render_error": "Errore nel rendering della pagina: {error}",
                "invalid_page": "Numero di pagina non valido",
                "file_not_found": "File non trovato: {}"
            }
        },
        
        # PDF Scanner
        "scanner": {
            # Status messages
            "status": {
                "scanning": "Analisi dei file PDF in corso...",
                "finding_duplicates": "Ricerca di duplicati...",
                "complete": "Scansione completata!",
                "cancelled": "Scansione annullata",
                "processing_file": "Elaborazione {current}/{total}: {file}",
                "found_duplicates": "Trovati {count} gruppi di duplicati"
            },
            # Error messages
            "error": {
                "prefix": "Errore: {error}",
                "during_scan": "Errore durante la scansione: {error}",
                "processing_file": "Errore durante l'elaborazione di {path}: {error}",
                "invalid_directory": "Directory non valida: {path}",
                "permission_denied": "Permesso negato: {path}",
                "file_too_large": "File troppo grande: {path} ({size} > {max_size})",
                "file_too_small": "File troppo piccolo: {path} ({size} < {min_size})",
                "invalid_pdf": "File PDF non valido: {path}",
                "unknown_error": "Errore sconosciuto: {error}"
            },
            # Warning messages
            "warning": {
                "access_denied": "Impossibile accedere a {path}: {error}",
                "loading_pdf": "Errore nel caricamento del PDF {path}: {error}",
                "skipping_file": "File saltato {path}: {reason}",
                "empty_file": "File vuoto: {path}",
                "encrypted_pdf": "PDF crittografato (non supportato): {path}",
                "corrupt_pdf": "File PDF corrotto: {path}"
            },
            # Success messages
            "success": {
                "scan_complete": "Scansione completata. Trovati {groups} gruppi di duplicati con {files} file.",
                "space_savings": "Possibile risparmio di spazio: {size} MB",
                "files_processed": "Elaborati {count} file in {time:.1f} secondi",
                "duplicates_found": "Trovati {count} potenziali duplicati"
            },
            # UI elements
            "ui": {
                "start_scan": "Avvia Scansione",
                "stop_scan": "Ferma Scansione",
                "scan_progress": "Avanzamento Scansione",
                "scan_results": "Risultati Scansione",
                "no_duplicates_found": "Nessun file duplicato trovato.",
                "select_files_to_compare": "Seleziona i file da confrontare",
                "compare_selected": "Confronta Selezionati",
                "select_all": "Seleziona Tutti",
                "deselect_all": "Deseleziona Tutti",
                "delete_selected": "Elimina Selezionati"
            },
            # Scanner related strings
            "scanning_pdfs": "Analisi dei file PDF in corso...",
            "finding_duplicates": "Ricerca di duplicati...",
            "scan_complete": "Scansione completata!",
            "scan_error": "Errore durante la scansione: {error}",
            "error_prefix": "Errore: {error}",
            "access_error": "Impossibile accedere a {path}: {error}",
            "processing_error": "Errore durante l'elaborazione di {path}: {error}",
            "load_error": "Errore durante il caricamento del PDF {file}: {error}",
            "file_processed": "Elaborati {current}/{total} file",
            "duplicates_found": "Trovati {count} gruppi di duplicati",
            "space_savings": "Possibile risparmio di spazio: {size} MB"
        },
        
        # Search and Duplicates
        "search_dup": {
            "header": "File Duplicati",
            "no_duplicates": "Nessun file duplicato trovato.",
            "group": {
                "singular": "1 file duplicato",
                "plural": "{count} file duplicati"
            },
            "tooltip": {
                "file": "File: {path}",
                "size": "Dimensione: {size:,} byte",
                "modified": "Modificato: {date}",
                "empty_group": "Nessun file duplicato in questo gruppo",
                "group": "Clicca per espandere/ridurre - {count} file duplicati"
            },
            "original_indicator": "(Originale)",
            "context_menu": {
                "open_file": "Apri File",
                "open_containing_folder": "Apri Cartella Contenitore",
                "mark_as_original": "Segna come Originale",
                "delete_file": "Elimina File",
                "compare_files": "Confronta File"
            },
            "status": {
                "scanning": "Ricerca duplicati in corso...",
                "completed": "Scansione completata. Trovati {groups} gruppi con {files} file duplicati.",
                "no_duplicates_found": "Nessun file duplicato trovato.",
                "processing": "Elaborazione file {current}/{total}...",
                "cancelled": "Scansione annullata dall'utente.",
                "error": "Errore durante la ricerca dei duplicati: {error}",
                "deleting": "Eliminazione di {count} file...",
                "deleted": "Eliminati correttamente {count} file.",
                "delete_error": "Errore durante l'eliminazione dei file: {error}",
                "marking_original": "Impostazione del file come originale...",
                "marked_original": "File impostato come originale.",
                "mark_original_error": "Errore durante l'impostazione del file come originale: {error}"
            },
            "confirmation": {
                "delete_title": "Conferma Eliminazione",
                "delete_message": "Sei sicuro di voler eliminare {count} file?\nQuesta azione non può essere annullata.",
                "delete_button": "Elimina",
                "cancel_button": "Annulla"
            },
            "columns": {
                "filename": "Nome File",
                "path": "Percorso",
                "size": "Dimensione",
                "modified": "Modificato",
                "status": "Stato"
            },
            "file_actions": {
                "open": "Apri",
                "open_folder": "Apri Cartella",
                "properties": "Proprietà",
                "copy_path": "Copia Percorso"
            },
            "group_actions": {
                "select_all": "Seleziona Tutto",
                "deselect_all": "Deseleziona Tutto",
                "expand_all": "Espandi Tutto",
                "collapse_all": "Comprimi Tutto"
            },
            "view_options": {
                "show_originals_only": "Mostra Solo Originali",
                "group_by_size": "Raggruppa per Dimensione",
                "group_by_date": "Raggruppa per Data",
                "group_by_name": "Raggruppa per Nome"
            },
            "filter": {
                "placeholder": "Filtra duplicati...",
                "size_range": "Intervallo Dimensioni",
                "date_range": "Intervallo Date",
                "file_type": "Tipo File"
            }
        },
        
        # Sponsor Dialog
        "sponsor": {
            "window_title": "Supporta lo Sviluppo",
            "title": "Supporta PDF Duplicate Finder",
            "ways_to_support": "Come Supportare:",
            "other_ways": {
                "title": "Altri Modi per Aiutare:",
                "star": "Metti una stella al progetto su",
                "report": "Segnala bug e suggerisci funzionalità",
                "share": "Condividi con chi potrebbe trovarlo utile"
            },
            "message": "Se trovi utile questa applicazione, valuta di supportare il suo sviluppo.\n\nIl tuo aiuto copre i costi di hosting e incoraggia ulteriori sviluppi.",
            "buttons": {
                "donate_paypal": "Dona con PayPal",
                "copy_monero": "Copia Indirizzo Monero",
                "copied": "Copiato!"
            },
            "links": {
                "github_sponsors": "GitHub Sponsors",
                "paypal": "Donazione PayPal"
            },
            "monero": {
                "label": "Monero:",
                "qr_tooltip": "Scansiona per donare XMR"
            },
            "qr_tooltip": "Scansiona per donare XMR"
        },
        
        # Update functionality
        "updates": {
            "window_title": "Controlla Aggiornamenti",
            "checking": "Controllo aggiornamenti in corso...",
            "update_available": "Versione {latest_version} disponibile! (Attuale: {current_version})",
            "no_updates": "Stai utilizzando l'ultima versione disponibile ({current_version}).",
            "error_checking": "Errore durante il controllo degli aggiornamenti: {error_msg}",
            "no_release_notes": "Nessuna nota di rilascio disponibile.",
            "whats_new": "Novità della versione ",
            "buttons": {
                "download": "Scarica Aggiornamento"
            }
        },
        
        # Markdown Viewer
        "markdown_viewer": {
            "window_title": "Visualizzatore Documentazione",
            "no_docs_dir_title": "Directory Documentazione Non Trovata",
            "no_docs_dir_msg": "Creata directory documentazione in: {}",
            "no_files_title": "Nessuna Documentazione Trovata",
            "no_files_msg": "Nessun file markdown (.md) trovato nella directory della documentazione: {}",
            "no_files_in_dir_msg": "Nessun file markdown trovato nella directory della documentazione: {}",
            "error_loading_file": "Errore nel caricamento del file: {}",
            "documentation": "&Documentazione",
            "documentation_tooltip": "Visualizza la documentazione in formato markdown"
        },
        
        # Delete Dialog and Operations (Italian)
        "delete": {
            # Confirmation dialogs
            "confirm_deletion": "Conferma eliminazione",
            "confirm_single_file": "Sei sicuro di voler eliminare questo file?\n\n{filename}",
            "confirm_multiple_files": "Sei sicuro di voler eliminare {count} file?\n\n{file_list}",
            "confirm_deletion_message": "Sei sicuro di voler eliminare {count} file?",
            "and_x_more": "e altri {count}",
            
            # Delete options
            "permanently_delete": "Elimina definitivamente (ignora il cestino)",
            "permanent_warning": "Attenzione: i file verranno eliminati definitivamente e non potranno essere recuperati!",
            
            # File in use dialogs
            "file_in_use_title": "File in uso",
            "cannot_delete_file": "Impossibile eliminare il file: {filename}",
            "file_in_use_message": "Il file è in uso da un altro programma.\n\nProcesso: {process_info}\nPosizione: {location}",
            "file_in_use_by": "Il file è in uso da: {process_info}",
            "file_in_use_generic": "Il file potrebbe essere in uso o non si dispone delle autorizzazioni necessarie per eliminarlo.",
            
            # Process information
            "unknown_file_not_found": "Sconosciuto (file non trovato)",
            "unknown_process": "Processo sconosciuto",
            "process_using_file": "{process_name} (PID: {pid})",
            "error_checking_processes": "Errore durante il controllo dei processi per il file {file_path}: {error}",
            
            # Error messages
            "permission_denied": "Permesso negato durante l'eliminazione di {filename}. ",
            "delete_failed": "Eliminazione non riuscita",
            "file_does_not_exist": "Il file non esiste: {path}",
            "permanently_deleted": "Eliminato definitivamente: {path}",
            "moved_to_recycle_bin": "Spostato nel cestino: {path}",
            "recycle_bin_failed": "Operazione cestino non riuscita",
            "cannot_move_to_recycle_bin": "Impossibile spostare nel cestino: {filename}",
            "recycle_bin_operation_failed": "Operazione di spostamento nel cestino non riuscita per {path}: {error}",
            "recycle_bin_operation_failed_message": "Impossibile spostare il file nel Cestino.\nErrore: {error}\n\nVuoi eliminare definitivamente il file?",
            "unexpected_error_deleting": "Errore imprevisto durante l'eliminazione di {path}: {error}",
            "failed_to_delete": "Impossibile eliminare {path} dopo {max_retries} tentativi",
            "last_error": "Ultimo errore: {error}",
            
            # Results/summary
            "deletion_complete": "Eliminazione completata",
            "successfully_deleted": "Eliminati correttamente: {count} file",
            "failed_to_delete_summary": "Impossibile eliminare: {count} file",
            
            # Buttons (already in common)
            # "common.cancel": "Annulla",
            # "common.delete": "Elimina",
            # "common.retry": "&Riprova",
            # "common.skip": "&Salta",
            # "common.close": "&Chiudi"
        },
        
        # File List Widget
        "file_list": {
            # Column headers
            "column_name": "Nome",
            "column_size": "Dimensione",
            "column_pages": "Pagine",
            
            # Group titles and tooltips
            "group_title": "Gruppo duplicati {group_num} ({file_count} file)",
            "group_tooltip": "<b>Gruppo {group_num}: {file_count} file duplicati</b><br>Dimensione: {size}{savings}",
            "space_savings": "Risparmio spazio: {savings}",
            
            # Page count strings
            "pages_single": "{count} pagina",
            "pages_multiple": "{count} pagine",
            
            # Context menu actions
            "action_expand_all": "Espandi tutto",
            "action_collapse_all": "Comprimi tutto",
            "action_open_all": "Apri tutto nel gruppo",
            "action_show_all": "Mostra tutto in Esplora",
            "action_open_file": "Apri file",
            "action_show_in_explorer": "Mostra in Esplora file",
            
            # File size formatting
            "size_bytes": "{size} B",
            "size_kb": "{size:.1f} KB",
            "size_mb": "{size:.1f} MB",
            "size_gb": "{size:.1f} GB"
        },
        
        # Recent Folders
        "recent_folders": {
            "clear_recent": "Cancella cartelle recenti",
            "no_recent_folders": "Nessuna cartella recente"
        },
        
        # Scan-related strings
        "scan": {
            # Error messages
            "no_pdf_files": "Nessun file PDF trovato nelle directory selezionate.",
            "non_existent_file": "File inesistente ignorato: {file}",
            "error_extracting_info": "Impossibile estrarre informazioni da {file}",
            "error_processing_file": "Errore durante l'elaborazione di {file}: {error}",
            "error_during_scan": "Si è verificato un errore durante la scansione: {error}",
            "error_calculating_image_hash": "Impossibile calcolare l'hash dell'immagine per {file}: {error}",
            "error_deleting_temp_file": "Impossibile eliminare il file temporaneo {file}: {error}",
            "error_cleanup_temp_dir": "Impossibile rimuovere la directory temporanea {dir}: {error}",
            
            # Status messages
            "found_pdf_files": "Trovati {count} file PDF da elaborare",
            "finding_duplicates": "Ricerca di PDF duplicati in corso...",
            "found_duplicate_groups": "Trovati {count} gruppi di duplicati",
            "processed_file": "Elaborato: {file}",
            "created_temp_dir": "Creata directory temporanea: {dir}",
            "cleanup_temp_dir": "Pulizia directory temporanea: {dir}",
            "error_in_scan_worker": "Errore nel worker di scansione:",
            "completed_groups": "Scansione completata. Trovati {count} gruppi di duplicati.",
            
            # UI strings
            "scanning_title": "Scansione",
            "scanning_message": "Ricerca di PDF duplicati in corso...",
            "scanning_progress": "Scansione... ({current}/{total} file)",
            "error_title": "Errore di Scansione",
        },
        
        # UI Components
        "ui": {
            # Preview widget
            "preview_placeholder": "L'anteprima verrà mostrata qui",
            "preview_of": "Anteprima di: {file_path}",
            
            # Status bar
            "status_ready": "Pronto",
            
            # File list
            "no_files_loaded": "Nessun file caricato",
            "files_loaded": "{count} file caricati",
            "duplicates_found": "Trovati {count} duplicati",
            "scan_complete": "Scansione completata",
            "scan_cancelled": "Scansione annullata",
            "scan_error": "Errore durante la scansione: {error}",
            "deleting_files": "Eliminazione di {count} file in corso...",
            "deletion_complete": "Eliminazione completata",
            "deletion_error": "Errore durante l'eliminazione dei file: {error}",
            "no_duplicates_found": "Nessun file duplicato trovato"
        },
    }
}

# Help translations (can be separated if needed)
HELP_TRANSLATIONS = {
    "en": {
        "help": {
            "welcome": "Welcome to PDF Finder",
            "usage": "Usage instructions..."
        }
    },
    "it": {
        "help": {
            "welcome": "Benvenuto in PDF Finder",
            "usage": "Istruzioni per l'uso..."
        }
    }
}
