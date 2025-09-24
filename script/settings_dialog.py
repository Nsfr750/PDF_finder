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
from script.simple_lang_manager import SimpleLanguageManager

# Import settings
from .settings import settings

# Set up logger
logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Settings dialog for the application."""
    
    settings_changed = pyqtSignal()
    requires_restart = pyqtSignal()
    
    def __init__(self, parent=None, language_manager=None):
        """Initialize the settings dialog.
        
        Args:
            parent: Parent widget
            language_manager: Language manager for translations
        """
        logger.debug("SettingsDialog.__init__() called")
        logger.debug("Initializing SettingsDialog")
        try:
            super().__init__(parent)
            logger.debug("QDialog initialized")
            
            self.language_manager = language_manager
            logger.debug("language_manager set")
            
            # Set window properties
            self.setWindowTitle(self.language_manager.tr("settings.title"))
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
        self._set_status(self.status_pymupdf, pymupdf_ok, self.tr("settings_dialog.backend_ok") if pymupdf_ok else self.tr("settings_dialog.backend_missing"))
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
        self._set_status(self.status_wand, wand_ok, self.tr("settings_dialog.backend_ok") if wand_ok else self.tr("settings_dialog.backend_missing"))
        if wand_ok:
            results.append(("Wand/Ghostscript", True, "OK"))

        if inline_only:
            return

        # Compose message
        lines = []
        for name, ok, detail in results:
            status = self.tr("settings_dialog.backend_ok") if ok else self.tr("settings_dialog.backend_missing")
            lines.append(f"{name}: {status}")
        msg = "\n".join(lines) if lines else self.tr("settings_dialog.no_backends_tested")

        # Show dialog
        try:
            QMessageBox.information(
                self,
                self.tr("settings_dialog.test_results_title"),
                msg
            )
        except Exception:
            pass
    
    def setup_ui(self):
        """Set up the user interface for the settings dialog."""
        logger.debug("SettingsDialog.setup_ui() called")
        try:
            # Create main layout and widget
            layout = QVBoxLayout()
            self.setLayout(layout)
            
            # Create tab widget
            tabs = QTabWidget()
            layout.addWidget(tabs)
            
            # Create tabs
            general_tab = QWidget()
            pdf_tab = QWidget()
            
            # Add tabs
            tabs.addTab(general_tab, self.tr("settings.general"))
            tabs.addTab(pdf_tab, self.tr("settings.appearance"))
            
            # Set up general tab
            self.setup_general_tab(general_tab)
            
            # Set up PDF tab
            self.setup_pdf_tab(pdf_tab)
            
            # Create button box
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | 
                QDialogButtonBox.StandardButton.Cancel | 
                QDialogButtonBox.StandardButton.Apply
            )
            
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
            
            # Add button box to layout
            layout.addWidget(button_box)
            logger.debug("UI setup completed")
            
        except Exception as e:
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
            
            # Theme selection
            self.theme_combo = QComboBox()
            self.theme_combo.addItem(self.tr("settings.theme_system"), "system")
            self.theme_combo.addItem(self.tr("settings.theme_light"), "light")
            self.theme_combo.addItem(self.tr("settings.theme_dark"), "dark")
            
            layout.addRow(
                QLabel("Theme:"), 
                self.theme_combo
            )
            
            # Application settings
            self.check_updates = QCheckBox(self.tr("settings.check_updates"))
            self.auto_save = QCheckBox(self.tr("settings.auto_save"))
            
            layout.addRow(self.check_updates)
            layout.addRow(self.auto_save)
            
            # Hash cache settings
            cache_group = QGroupBox(self.tr("settings.cache_settings"))
            cache_layout = QFormLayout(cache_group)
            
            # Enable hash cache
            self.enable_hash_cache = QCheckBox(self.tr("settings.enable_hash_cache"))
            cache_layout.addRow(self.enable_hash_cache)
            
            # Cache directory
            cache_dir_layout = QHBoxLayout()
            self.cache_dir = QLineEdit()
            self.cache_dir_browse = QPushButton("...")
            self.cache_dir_browse.setMaximumWidth(30)
            cache_dir_layout.addWidget(self.cache_dir)
            cache_dir_layout.addWidget(self.cache_dir_browse)
            cache_layout.addRow(self.tr("settings.cache_dir"), cache_dir_layout)
            
            # Max cache size
            self.max_cache_size = QSpinBox()
            self.max_cache_size.setRange(100, 100000)
            self.max_cache_size.setValue(10000)
            self.max_cache_size.setSuffix(" " + self.tr("settings.entries"))
            cache_layout.addRow(self.tr("settings.max_cache_size"), self.max_cache_size)
            
            # Cache TTL days
            self.cache_ttl_days = QSpinBox()
            self.cache_ttl_days.setRange(1, 365)
            self.cache_ttl_days.setValue(30)
            self.cache_ttl_days.setSuffix(" " + self.tr("settings.days"))
            cache_layout.addRow(self.tr("settings.cache_ttl_days"), self.cache_ttl_days)
            
            # Memory cache size
            self.memory_cache_size = QSpinBox()
            self.memory_cache_size.setRange(100, 10000)
            self.memory_cache_size.setValue(1000)
            self.memory_cache_size.setSuffix(" " + self.tr("settings.entries"))
            cache_layout.addRow(self.tr("settings.memory_cache_size"), self.memory_cache_size)
            
            layout.addRow(cache_group)
            
            # Connect cache directory browse button
            self.cache_dir_browse.clicked.connect(self._browse_cache_dir)
            
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
            pdf_group = QGroupBox(self.tr("settings_dialog.pdf"))
            pdf_layout = QFormLayout()

            # Backend selection
            self.backend_combo = QComboBox()
            self.backend_combo.addItem(self.tr("settings.backend_auto"), "auto")
            self.backend_combo.addItem("PyMuPDF", "pymupdf")
            self.backend_combo.addItem("Wand / Ghostscript", "wand_ghostscript")
            pdf_layout.addRow(QLabel("Backend:"), self.backend_combo)

            # Ghostscript path
            gs_row = QHBoxLayout()
            self.ghostscript_path_edit = QLineEdit()
            self.ghostscript_browse_btn = QPushButton(self.tr("settings.browse"))
            def _browse_gs():
                f, _ = QFileDialog.getOpenFileName(self, self.tr("settings.select_gs"))
                if f:
                    self.ghostscript_path_edit.setText(f)
            self.ghostscript_browse_btn.clicked.connect(_browse_gs)
            gs_row.addWidget(self.ghostscript_path_edit)
            gs_row.addWidget(self.ghostscript_browse_btn)
            pdf_layout.addRow(QLabel(self.tr("settings.ghostscript_path")), gs_row)

            # Inline status labels for backends
            self.status_pymupdf = QLabel("")
            self.status_wand = QLabel("")
            pdf_layout.addRow(QLabel(self.tr("settings.backend_status")))
            pdf_layout.addRow(QLabel("PyMuPDF:"), self.status_pymupdf)
            pdf_layout.addRow(QLabel("Wand / Ghostscript:"), self.status_wand)

            # Test backends button
            self.test_backends_btn = QPushButton(self.tr("settings.test_backends"))
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
            # Load theme
            current_theme = settings.get('theme', 'system')
            index = self.theme_combo.findData(current_theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
            
            # Load other settings
            self.check_updates.setChecked(settings.get('check_updates', True))
            self.auto_save.setChecked(settings.get('auto_save', True))
            
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
            
            # Load hash cache settings
            self.enable_hash_cache.setChecked(settings.get('enable_hash_cache', False))
            self.cache_dir.setText(settings.get('cache_dir', '') or '')
            self.max_cache_size.setValue(settings.get('max_cache_size', 10000))
            self.cache_ttl_days.setValue(settings.get('cache_ttl_days', 30))
            self.memory_cache_size.setValue(settings.get('memory_cache_size', 1000))
            
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
            # Save theme
            theme = self.theme_combo.currentData()
            settings.set('theme', theme)
            
            # Save application settings
            settings.set('check_updates', self.check_updates.isChecked())
            settings.set('auto_save', self.auto_save.isChecked())
            
            # Save PDF settings
            settings.set('pdf.backend', self.backend_combo.currentData())
            settings.set('pdf.ghostscript_path', self.ghostscript_path_edit.text().strip())
            
            # Save hash cache settings
            settings.set('enable_hash_cache', self.enable_hash_cache.isChecked())
            settings.set('cache_dir', self.cache_dir.text().strip())
            settings.set('max_cache_size', self.max_cache_size.value())
            settings.set('cache_ttl_days', self.cache_ttl_days.value())
            settings.set('memory_cache_size', self.memory_cache_size.value())
            
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
                    self.language_manager.tr("settings_dialog.saved", "Settings Saved"),
                    self.language_manager.tr("settings_dialog.saved_message", "Your settings have been saved.")
                )
                logger.debug("Settings applied")
            
        except Exception as e:
            logger.error(f"ERROR in apply_settings: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                self.language_manager.tr("settings_dialog.error", "Error"),
                self.language_manager.tr("settings_dialog.save_error", "Failed to save settings: {error}").format(error=str(e))
            )
    
    def accept(self):
        """Handle OK button click."""
        logger.debug("SettingsDialog.accept() called")
        try:
            if self.save_settings():
                super().accept()
                
        except Exception as e:
            logger.error(f"ERROR in accept: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                self.language_manager.tr("settings_dialog.error", "Error"),
                self.language_manager.tr("settings_dialog.save_error", "Failed to save settings: {error}").format(error=str(e))
            )

    def tr(self, key: str) -> str:
        """Translate a key using the language manager.
        
        Args:
            key: The translation key
            
        Returns:
            str: The translated text
        """
        if self.language_manager:
            return self.language_manager.tr(key)
        return key

    def _browse_cache_dir(self):
        """Browse for cache directory."""
        logger.debug("Browsing for cache directory")
        try:
            f = QFileDialog.getExistingDirectory(self, self.tr("settings.select_cache_dir"))
            if f:
                self.cache_dir.setText(f)
        except Exception as e:
            logger.error(f"Error browsing for cache directory: {e}")
            import traceback
            traceback.print_exc()

    # End of SettingsDialog class
