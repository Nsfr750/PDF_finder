"""
Settings dialog for PDF Duplicate Finder.
"""
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QWidget, QFormLayout, QSpinBox, QCheckBox,
    QComboBox, QFileDialog, QLineEdit, QMessageBox, QGroupBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from script.lang_mgr import LanguageManager

# Import settings
from .settings import settings

# Set up logger
logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Settings dialog for the application."""
    
    settings_changed = pyqtSignal()
    # Signal emitted when the language is changed, with the new language code
    language_changed = pyqtSignal(str)
    requires_restart = pyqtSignal()
    
    def __init__(self, parent=None, language_manager=None):
        """Initialize the settings dialog.
        
        Args:
            parent: Parent widget
            language_manager: Language manager for translations
        """
        print("DEBUG: SettingsDialog.__init__() called")
        logger.debug("SettingsDialog.__init__() called")
        logger.debug("Initializing SettingsDialog")
        try:
            print("DEBUG: Calling super().__init__(parent)")
            super().__init__(parent)
            print("DEBUG: QDialog initialized")
            logger.debug("QDialog initialized")
            
            print("DEBUG: Setting language_manager")
            self.language_manager = language_manager
            self.tr = language_manager.tr if language_manager else lambda key, default: default
            print("DEBUG: language_manager set")
            
            print("DEBUG: Getting initial_language")
            # Store the initial language to detect changes
            self.initial_language = settings.get('app.language', 'en')
            print(f"DEBUG: initial_language: {self.initial_language}")
            
            print("DEBUG: Setting window properties")
            # Set window properties
            self.setWindowTitle(self.tr("settings_dialog.title", "Settings"))
            self.setMinimumSize(600, 400)
            print("DEBUG: Window properties set")
            logger.debug("Window properties set")
            
            # Set window flags to ensure it stays on top
            print("DEBUG: Setting window flags")
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            print("DEBUG: Window flags set")
            logger.debug("Window flags set")
            
            # Set up the UI
            print("DEBUG: Setting up UI")
            logger.debug("Setting up UI")
            self.setup_ui()
            
            # Load settings
            print("DEBUG: Loading settings")
            logger.debug("Loading settings")
            self.load_settings()
            
            # Ensure the dialog is visible
            print("DEBUG: Ensuring dialog is visible")
            self.setVisible(True)
            self.raise_()
            self.activateWindow()
            print("DEBUG: Dialog should now be visible")
            logger.debug("Dialog should now be visible")
            
        except Exception as e:
            logger.error(f"ERROR in SettingsDialog.__init__: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _set_status(self, label: QLabel, ok: bool, message: str):
        """Set a colored status message on a QLabel."""
        try:
            label.setText(message)
            color = "#2e7d32" if ok else "#c62828"
            label.setStyleSheet(f"color: {color};")
        except Exception:
            pass

    def test_backends(self, inline_only: bool = False):
        """Validate availability of configured PDF rendering backends.

        Args:
            inline_only: If True, only update inline labels without showing a dialog.
        """
        logger.debug("Testing PDF backends availability")
        results = []

        # Read paths from widgets (not from persisted settings)
        gs_path = (self.ghostscript_path_edit.text() or "").strip()

        # Check PyMuPDF
        pymupdf_ok = False
        try:
            import importlib
            importlib.import_module('fitz')
            pymupdf_ok = True
        except Exception as e:
            results.append(("PyMuPDF", False, str(e)))
        self._set_status(self.status_pymupdf, pymupdf_ok, self.tr("settings_dialog.backend_ok", "OK") if pymupdf_ok else self.tr("settings_dialog.backend_missing", "Missing"))
        if pymupdf_ok:
            results.append(("PyMuPDF", True, "OK"))

        # Check Wand / Ghostscript
        wand_ok = False
        try:
            import importlib, os
            importlib.import_module('wand.image')
            if gs_path and os.path.isfile(gs_path):
                wand_ok = True
        except Exception as e:
            results.append(("Wand/Ghostscript", False, str(e)))
        self._set_status(self.status_wand, wand_ok, self.tr("settings_dialog.backend_ok", "OK") if wand_ok else self.tr("settings_dialog.backend_missing", "Missing or invalid path"))
        if wand_ok:
            results.append(("Wand/Ghostscript", True, "OK"))

        if inline_only:
            return

        # Compose message
        lines = []
        for name, ok, detail in results:
            status = self.tr("settings_dialog.backend_ok", "OK") if ok else self.tr("settings_dialog.backend_missing", "Missing")
            lines.append(f"{name}: {status}")
        msg = "\n".join(lines) if lines else self.tr("settings_dialog.no_backends_tested", "No backends tested")

        # Show dialog
        try:
            QMessageBox.information(
                self,
                self.tr("settings_dialog.test_results_title", "Backend Test Results"),
                msg
            )
        except Exception:
            pass
    
    def setup_ui(self):
        """Set up the user interface for the settings dialog."""
        print("DEBUG: SettingsDialog.setup_ui() called")
        logger.debug("SettingsDialog.setup_ui() called")
        try:
            print("DEBUG: Creating main layout")
            # Create main layout and widget
            layout = QVBoxLayout()
            self.setLayout(layout)
            
            print("DEBUG: Creating tab widget")
            # Create tab widget
            tabs = QTabWidget()
            layout.addWidget(tabs)
            
            print("DEBUG: Creating tabs")
            # Create tabs
            general_tab = QWidget()
            pdf_tab = QWidget()
            
            print("DEBUG: Adding tabs to tab widget")
            # Add tabs
            tabs.addTab(general_tab, self.tr("settings_dialog.general", "General"))
            tabs.addTab(pdf_tab, self.tr("settings_dialog.pdf", "PDF"))
            
            print("DEBUG: Calling setup_general_tab")
            # Set up general tab
            self.setup_general_tab(general_tab)
            
            print("DEBUG: Calling setup_pdf_tab")
            # Set up PDF tab
            self.setup_pdf_tab(pdf_tab)
            
            print("DEBUG: Creating button box")
            # Create button box
            from PyQt6.QtWidgets import QDialogButtonBox
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | 
                QDialogButtonBox.StandardButton.Cancel | 
                QDialogButtonBox.StandardButton.Apply
            )
            
            print("DEBUG: Connecting button signals")
            # Connect buttons
            logger.debug("Connecting button signals")
            button_box.accepted.connect(self.accept)
            button_box.rejected.connect(self.reject)
            apply_button = button_box.button(QDialogButtonBox.StandardButton.Apply)
            if apply_button:
                logger.debug("Apply button found, connecting to apply_settings")
                apply_button.clicked.connect(self.apply_settings)
            else:
                logger.debug("Apply button not found")
            
            print("DEBUG: Adding button box to layout")
            layout.addWidget(button_box)
            print("DEBUG: UI setup completed")
            logger.debug("UI setup completed")
            
        except Exception as e:
            print(f"ERROR in setup_ui: {e}")
            logger.error(f"ERROR in setup_ui: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def setup_general_tab(self, tab):
        """Set up the general settings tab.
        
        Args:
            tab: The tab widget to set up
        """
        logger.debug("SettingsDialog.setup_general_tab() called")
        try:
            layout = QFormLayout(tab)
            
            # Language selection
            self.language_combo = QComboBox()
            self.language_combo.addItem("English", "en")
            self.language_combo.addItem("Italiano", "it")
            logger.debug(f"Language combo initialized with items: {self.language_combo.count()}")
            # Add more languages as needed
            
            layout.addRow(
                QLabel(self.tr("settings_dialog.language", "Language:")), 
                self.language_combo
            )
            
            # Theme selection
            self.theme_combo = QComboBox()
            self.theme_combo.addItem(self.tr("settings_dialog.theme_system", "System"), "system")
            self.theme_combo.addItem(self.tr("settings_dialog.theme_light", "Light"), "light")
            self.theme_combo.addItem(self.tr("settings_dialog.theme_dark", "Dark"), "dark")
            
            layout.addRow(
                QLabel(self.tr("settings_dialog.theme", "Theme:")), 
                self.theme_combo
            )
            
            # Application settings
            self.check_updates = QCheckBox(self.tr("settings_dialog.check_updates", "Check for updates on startup"))
            self.auto_save = QCheckBox(self.tr("settings_dialog.auto_save", "Auto-save settings"))
            
            layout.addRow(self.check_updates)
            layout.addRow(self.auto_save)
            
            logger.debug("General tab setup complete")
            
        except Exception as e:
            logger.error(f"ERROR in setup_general_tab: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def setup_pdf_tab(self, tab):
        """Set up the PDF settings tab.
        
        Args:
            tab: The tab widget to set up
        """
        logger.debug("SettingsDialog.setup_pdf_tab() called")
        try:
            layout = QVBoxLayout(tab)
            
            # PDF rendering backend group
            pdf_group = QGroupBox(self.tr("settings_dialog.pdf", "PDF Rendering"))
            pdf_layout = QFormLayout()

            # Backend selection
            self.backend_combo = QComboBox()
            self.backend_combo.addItem(self.tr("settings_dialog.backend_auto", "Auto (recommended)"), "auto")
            self.backend_combo.addItem("PyMuPDF", "pymupdf")
            self.backend_combo.addItem("Wand / Ghostscript", "wand_ghostscript")
            pdf_layout.addRow(QLabel(self.tr("settings_dialog.backend", "Backend:")), self.backend_combo)

            # Ghostscript path
            gs_row = QHBoxLayout()
            self.ghostscript_path_edit = QLineEdit()
            self.ghostscript_browse_btn = QPushButton(self.tr("settings_dialog.browse", "Browse"))
            def _browse_gs():
                f, _ = QFileDialog.getOpenFileName(self, self.tr("settings_dialog.select_gs", "Select Ghostscript executable"))
                if f:
                    self.ghostscript_path_edit.setText(f)
            self.ghostscript_browse_btn.clicked.connect(_browse_gs)
            gs_row.addWidget(self.ghostscript_path_edit)
            gs_row.addWidget(self.ghostscript_browse_btn)
            pdf_layout.addRow(QLabel(self.tr("settings_dialog.ghostscript_path", "Ghostscript path:")), gs_row)

            # Inline status labels for backends
            self.status_pymupdf = QLabel("")
            self.status_wand = QLabel("")
            pdf_layout.addRow(QLabel(self.tr("settings_dialog.backend_status", "Backend status:")))
            pdf_layout.addRow(QLabel("PyMuPDF:"), self.status_pymupdf)
            pdf_layout.addRow(QLabel("Wand / Ghostscript:"), self.status_wand)

            # Test backends button
            self.test_backends_btn = QPushButton(self.tr("settings_dialog.test_backends", "Test backends"))
            self.test_backends_btn.clicked.connect(self.test_backends)
            pdf_layout.addRow(self.test_backends_btn)

            pdf_group.setLayout(pdf_layout)
            layout.addWidget(pdf_group)
            layout.addStretch()
            
            logger.debug("PDF tab setup complete")
            
        except Exception as e:
            logger.error(f"ERROR in setup_pdf_tab: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def load_settings(self):
        """Load settings into the dialog."""
        logger.debug("SettingsDialog.load_settings() called")
        try:
            # Load language
            current_lang = settings.get('app.language', 'en')
            logger.debug(f"Current language from settings: {current_lang}")
            index = self.language_combo.findData(current_lang)
            logger.debug(f"Language combo index for '{current_lang}': {index}")
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
                logger.debug(f"Language combo set to index {index}: {self.language_combo.currentText()}")
            else:
                logger.debug(f"Language '{current_lang}' not found in combo, keeping default")
            
            # Load theme
            current_theme = settings.get('app.theme', 'system')
            index = self.theme_combo.findData(current_theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
            
            # Load other settings
            self.check_updates.setChecked(settings.get('app.check_updates', True))
            self.auto_save.setChecked(settings.get('app.auto_save', True))
            
            # Load PDF backend settings
            current_backend = settings.get('pdf.backend', 'auto')
            idx = self.backend_combo.findData(current_backend)
            if idx >= 0:
                self.backend_combo.setCurrentIndex(idx)
            self.ghostscript_path_edit.setText(settings.get('pdf.ghostscript_path', '') or '')
            
            # Pre-fill backend status on load (best-effort, non-blocking)
            try:
                self.test_backends(inline_only=True)
            except Exception as e:
                logger.debug(f"Could not test backends on load: {e}")
            
            logger.debug("Settings loaded")
            
        except Exception as e:
            logger.error(f"ERROR in load_settings: {e}")
            import traceback
            traceback.print_exc()
    
    def save_settings(self):
        """Save settings from the dialog."""
        logger.debug("Saving settings")
        try:
            # Get the selected language code
            lang_code = self.language_combo.currentData()
            logger.debug(f"Selected language code: {lang_code}")
            logger.debug(f"Current language in settings: {settings.get('app.language')}")
            
            # Check if language was changed
            if lang_code and lang_code != settings.get('app.language'):
                logger.debug(f"Language changed from {settings.get('app.language')} to {lang_code}")
                settings.set('app.language', lang_code)
                # Emit the language_changed signal with the new language code
                logger.debug(f"Emitting language_changed signal with: {lang_code}")
                self.language_changed.emit(lang_code)
                logger.debug(f"Language changed signal emitted for: {lang_code}")
                self._language_was_changed = True
            else:
                logger.debug("Language not changed or invalid language code")
                
            # Save theme
            theme = self.theme_combo.currentData()
            settings.set('app.theme', theme)
            
            # Save application settings
            settings.set('app.check_updates', self.check_updates.isChecked())
            settings.set('app.auto_save', self.auto_save.isChecked())
            
            # Save PDF settings
            settings.set('pdf.backend', self.backend_combo.currentData())
            settings.set('pdf.ghostscript_path', self.ghostscript_path_edit.text().strip())
            
            logger.debug("Settings saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            return False
    
    def apply_settings(self):
        """Apply settings without closing the dialog."""
        logger.debug("SettingsDialog.apply_settings() called")
        try:
            if self.save_settings():
                QMessageBox.information(
                    self,
                    self.tr("settings_dialog.saved", "Settings Saved"),
                    self.tr("settings_dialog.saved_message", "Your settings have been saved.")
                )
                logger.debug("Settings applied")
            
        except Exception as e:
            logger.error(f"ERROR in apply_settings: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                self.tr("settings_dialog.error", "Error"),
                self.tr("settings_dialog.save_error", "Failed to save settings: {error}").format(error=str(e))
            )
    
    def accept(self):
        """Handle OK button click."""
        logger.debug("SettingsDialog.accept() called")
        try:
            if self.save_settings():
                # If language was changed, inform the user that a restart is needed
                if hasattr(self, '_language_was_changed') and self._language_was_changed:
                    QMessageBox.information(
                        self,
                        self.tr("settings_dialog.restart_required", "Restart Required"),
                        self.tr("settings_dialog.restart_message", 
                              "The application needs to restart for language changes to take effect.")
                    )
                super().accept()
                
        except Exception as e:
            logger.error(f"ERROR in accept: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                self.tr("settings_dialog.error", "Error"),
                self.tr("settings_dialog.save_error", "Failed to save settings: {error}").format(error=str(e))
            )
    
    # End of SettingsDialog class
