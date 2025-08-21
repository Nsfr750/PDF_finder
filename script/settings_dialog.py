"""
Settings dialog for PDF Duplicate Finder.
"""
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QWidget, QFormLayout, QSpinBox, QCheckBox,
    QComboBox, QFileDialog, QLineEdit, QMessageBox, QGroupBox
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
    language_changed = pyqtSignal()
    requires_restart = pyqtSignal()
    
    def __init__(self, parent=None, language_manager=None):
        """Initialize the settings dialog.
        
        Args:
            parent: Parent widget
            language_manager: Language manager for translations
        """
        logger.debug("Initializing SettingsDialog")
        try:
            super().__init__(parent)
            logger.debug("QDialog initialized")
            
            self.language_manager = language_manager
            self.tr = language_manager.tr if language_manager else lambda key, default: default
            
            # Store the initial language to detect changes
            self.initial_language = settings.get('app.language', 'en')
            
            # Set window properties
            self.setWindowTitle(self.tr("settings_dialog.title", "Settings"))
            self.setMinimumSize(600, 400)
            logger.debug("Window properties set")
            
            # Set window flags to ensure it stays on top
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            logger.debug("Window flags set")
            
            # Set up the UI
            logger.debug("Setting up UI")
            self.setup_ui()
            
            # Load settings
            logger.debug("Loading settings")
            self.load_settings()
            
            # Ensure the dialog is visible
            self.setVisible(True)
            self.raise_()
            self.activateWindow()
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
        """Set up the user interface."""
        logger.debug("Setting up UI components")
        try:
            layout = QVBoxLayout(self)
            
            # Create tab widget
            logger.debug("Creating tab widget")
            self.tab_widget = QTabWidget()
            
            # General tab
            logger.debug("Setting up general tab")
            self.general_tab = QWidget()
            self.setup_general_tab()
            self.tab_widget.addTab(self.general_tab, self.tr("settings_dialog.general", "General"))
            
            # Add more tabs here as needed
            
            # Add tab widget to layout
            layout.addWidget(self.tab_widget)
            
            # Add buttons
            logger.debug("Adding buttons")
            button_box = QHBoxLayout()
            
            self.ok_button = QPushButton(self.tr("common.ok", "OK"))
            self.ok_button.clicked.connect(self.accept)
            
            self.cancel_button = QPushButton(self.tr("common.cancel", "Cancel"))
            self.cancel_button.clicked.connect(self.reject)
            
            self.apply_button = QPushButton(self.tr("common.apply", "Apply"))
            self.apply_button.clicked.connect(self.apply_settings)
            
            button_box.addStretch()
            button_box.addWidget(self.ok_button)
            button_box.addWidget(self.cancel_button)
            button_box.addWidget(self.apply_button)
            
            layout.addLayout(button_box)
            
            logger.debug("UI setup complete")
            
        except Exception as e:
            logger.error(f"ERROR in setup_ui: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def setup_general_tab(self):
        """Set up the general settings tab."""
        logger.debug("Setting up general tab components")
        try:
            layout = QVBoxLayout(self.general_tab)
            
            # Appearance group
            appearance_group = QGroupBox(self.tr("settings_dialog.appearance", "Appearance"))
            appearance_layout = QFormLayout()
            
            # Language selection
            self.language_combo = QComboBox()
            self.language_combo.addItem("English", "en")
            self.language_combo.addItem("Italiano", "it")
            # Add more languages as needed
            
            appearance_layout.addRow(
                QLabel(self.tr("settings_dialog.language", "Language:")),
                self.language_combo
            )
            
            # Theme selection
            self.theme_combo = QComboBox()
            self.theme_combo.addItem(self.tr("settings_dialog.theme_system", "System Default"), "system")
            self.theme_combo.addItem(self.tr("settings_dialog.theme_dark", "Dark"), "dark")
            
            appearance_layout.addRow(
                QLabel(self.tr("settings_dialog.theme", "Theme:")),
                self.theme_combo
            )
            
            appearance_group.setLayout(appearance_layout)
            
            # Application group
            app_group = QGroupBox(self.tr("settings_dialog.application", "Application"))
            app_layout = QFormLayout()
            
            # Check for updates on startup
            self.check_updates = QCheckBox(self.tr("settings_dialog.check_updates", "Check for updates on startup"))
            app_layout.addRow(self.check_updates)
            
            # Auto-save settings
            self.auto_save = QCheckBox(self.tr("settings_dialog.auto_save", "Auto-save settings"))
            app_layout.addRow(self.auto_save)
            
            app_group.setLayout(app_layout)

            # Add groups to layout
            layout.addWidget(appearance_group)
            layout.addWidget(app_group)

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
            
            logger.debug("General tab setup complete")
            
        except Exception as e:
            logger.error(f"ERROR in setup_general_tab: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def load_settings(self):
        """Load settings into the dialog."""
        logger.debug("Loading settings")
        try:
            # Load language
            current_lang = settings.get('app.language', 'en')
            index = self.language_combo.findData(current_lang)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
            
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
            except Exception:
                pass
            
            logger.debug("Settings loaded")
            
        except Exception as e:
            logger.error(f"ERROR in load_settings: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def save_settings(self):
        """Save settings from the dialog."""
        logger.debug("Saving settings")
        try:
            # Get the selected language
            new_language = self.language_combo.currentData()
            
            # Save language
            settings.set('app.language', new_language)
            
            # Save theme
            settings.set('app.theme', self.theme_combo.currentData())
            
            # Save other settings
            settings.set('app.check_updates', self.check_updates.isChecked())
            settings.set('app.auto_save', self.auto_save.isChecked())
            
            # Save PDF backend settings
            settings.set('pdf.backend', self.backend_combo.currentData())
            settings.set('pdf.ghostscript_path', self.ghostscript_path_edit.text().strip())
            
            # Emit signal that settings have changed
            self.settings_changed.emit()
            
            # If language changed, emit a specific signal
            if new_language != self.initial_language:
                self.language_changed.emit()
                self._language_was_changed = True
            
            logger.debug("Settings saved")
            
        except Exception as e:
            logger.error(f"ERROR in save_settings: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def apply_settings(self):
        """Apply settings without closing the dialog."""
        logger.debug("Applying settings")
        try:
            self.save_settings()
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
            raise
    
    def accept(self):
        """Handle OK button click."""
        logger.debug("Accepting settings")
        try:
            self.save_settings()
            
            # If language was changed, we need to restart the application
            if hasattr(self, '_language_was_changed') and self._language_was_changed:
                reply = QMessageBox.information(
                    self,
                    self.tr("settings_dialog.restart_required", "Restart Required"),
                    self.tr("settings_dialog.restart_message", 
                          "The application needs to be restarted for language changes to take effect.\n"
                          "Do you want to restart now?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Emit a signal that the application needs to restart
                    self.requires_restart.emit()
            
            super().accept()
            
            logger.debug("Settings accepted")
            
        except Exception as e:
            logger.error(f"ERROR in accept: {e}")
            import traceback
            traceback.print_exc()
            raise
