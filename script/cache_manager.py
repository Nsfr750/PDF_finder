"""
Cache Manager Module

This module provides UI components for managing the PDF hash cache,
including viewing cache statistics, clearing cache, and configuring cache settings.
"""
import os
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QFormLayout, QSpinBox, QCheckBox, QLineEdit,
    QFileDialog, QMessageBox, QProgressBar, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTabWidget, QWidget,
    QSplitter, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from .hash_cache import HashCache

class CacheManagerDialog(QDialog):
    """
    Dialog for managing PDF hash cache settings and operations.
    """
    
    cache_cleared = pyqtSignal()
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, hash_cache: Optional[HashCache] = None, 
                 current_settings: Optional[Dict[str, Any]] = None,
                 parent=None):
        super().__init__(parent)
        self.hash_cache = hash_cache
        self.current_settings = current_settings or {}
        self.setWindowTitle("Cache Manager")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_current_settings()
        self.refresh_cache_stats()
        
        # Auto-refresh stats every 2 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_cache_stats)
        self.refresh_timer.start(2000)
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Statistics tab
        self.stats_widget = self.create_stats_tab()
        self.tab_widget.addTab(self.stats_widget, "Statistics")
        
        # Settings tab
        self.settings_widget = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_widget, "Settings")
        
        # Operations tab
        self.operations_widget = self.create_operations_tab()
        self.tab_widget.addTab(self.operations_widget, "Operations")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_cache_stats)
        button_layout.addWidget(self.refresh_button)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_stats_tab(self) -> QWidget:
        """Create the statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Cache info group
        info_group = QGroupBox("Cache Information")
        info_layout = QFormLayout()
        
        self.cache_dir_label = QLabel("N/A")
        info_layout.addRow("Cache Directory:", self.cache_dir_label)
        
        self.cache_status_label = QLabel("Not Available")
        info_layout.addRow("Cache Status:", self.cache_status_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Statistics table
        stats_group = QGroupBox("Cache Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Statistic", "Value"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.setAlternatingRowColors(True)
        
        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Cache health indicator
        health_group = QGroupBox("Cache Health")
        health_layout = QVBoxLayout()
        
        self.health_label = QLabel("Cache health status will appear here")
        self.health_label.setWordWrap(True)
        health_layout.addWidget(self.health_label)
        
        self.health_progress = QProgressBar()
        self.health_progress.setRange(0, 100)
        self.health_progress.setValue(0)
        health_layout.addWidget(self.health_progress)
        
        health_group.setLayout(health_layout)
        layout.addWidget(health_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Cache settings group
        settings_group = QGroupBox("Cache Settings")
        settings_layout = QFormLayout()
        
        self.enable_cache_checkbox = QCheckBox("Enable Hash Caching")
        self.enable_cache_checkbox.setToolTip("Enable hash caching for improved performance")
        settings_layout.addRow("Hash Caching:", self.enable_cache_checkbox)
        
        self.max_cache_size_spin = QSpinBox()
        self.max_cache_size_spin.setRange(100, 100000)
        self.max_cache_size_spin.setSuffix(" entries")
        self.max_cache_size_spin.setToolTip("Maximum number of files to cache")
        settings_layout.addRow("Max Cache Size:", self.max_cache_size_spin)
        
        self.cache_ttl_spin = QSpinBox()
        self.cache_ttl_spin.setRange(1, 365)
        self.cache_ttl_spin.setSuffix(" days")
        self.cache_ttl_spin.setToolTip("Time-to-live for cache entries")
        settings_layout.addRow("Cache TTL:", self.cache_ttl_spin)
        
        self.memory_cache_spin = QSpinBox()
        self.memory_cache_spin.setRange(100, 10000)
        self.memory_cache_spin.setSuffix(" entries")
        self.memory_cache_spin.setToolTip("Maximum number of entries in memory cache")
        settings_layout.addRow("Memory Cache Size:", self.memory_cache_spin)
        
        self.cache_dir_edit = QLineEdit()
        self.cache_dir_edit.setToolTip("Directory to store cache files")
        self.cache_dir_edit.setReadOnly(True)
        
        dir_button = QPushButton("Browse...")
        dir_button.clicked.connect(self.browse_cache_dir)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.cache_dir_edit)
        dir_layout.addWidget(dir_button)
        settings_layout.addRow("Cache Directory:", dir_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Performance settings group
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QFormLayout()
        
        self.auto_cleanup_checkbox = QCheckBox("Enable Automatic Cleanup")
        self.auto_cleanup_checkbox.setToolTip("Automatically clean up expired cache entries")
        perf_layout.addRow("Auto Cleanup:", self.auto_cleanup_checkbox)
        
        self.preload_checkbox = QCheckBox("Preload Common Files")
        self.preload_checkbox.setToolTip("Preload frequently accessed files into memory")
        perf_layout.addRow("Preload Files:", self.preload_checkbox)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        layout.addStretch()
        widget.setLayout(widget)
        return widget
    
    def create_operations_tab(self) -> QWidget:
        """Create the operations tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Cache operations group
        ops_group = QGroupBox("Cache Operations")
        ops_layout = QVBoxLayout()
        
        # Clear cache button
        clear_layout = QHBoxLayout()
        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        self.clear_cache_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        clear_layout.addWidget(self.clear_cache_button)
        clear_layout.addStretch()
        ops_layout.addLayout(clear_layout)
        
        # Cleanup expired entries button
        cleanup_layout = QHBoxLayout()
        self.cleanup_button = QPushButton("Cleanup Expired Entries")
        self.cleanup_button.clicked.connect(self.cleanup_expired)
        cleanup_layout.addWidget(self.cleanup_button)
        cleanup_layout.addStretch()
        ops_layout.addLayout(cleanup_layout)
        
        # Optimize cache button
        optimize_layout = QHBoxLayout()
        self.optimize_button = QPushButton("Optimize Cache")
        self.optimize_button.clicked.connect(self.optimize_cache)
        optimize_layout.addWidget(self.optimize_button)
        optimize_layout.addStretch()
        ops_layout.addLayout(optimize_layout)
        
        ops_group.setLayout(ops_layout)
        layout.addWidget(ops_group)
        
        # Operation log
        log_group = QGroupBox("Operation Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_current_settings(self):
        """Load current cache settings."""
        if self.current_settings:
            self.enable_cache_checkbox.setChecked(
                self.current_settings.get('enable_hash_cache', True)
            )
            self.max_cache_size_spin.setValue(
                self.current_settings.get('max_cache_size', 10000)
            )
            self.cache_ttl_spin.setValue(
                self.current_settings.get('cache_ttl_days', 30)
            )
            self.memory_cache_spin.setValue(
                self.current_settings.get('memory_cache_size', 1000)
            )
            
            cache_dir = self.current_settings.get('cache_dir', '')
            if cache_dir:
                self.cache_dir_edit.setText(cache_dir)
            else:
                # Show default cache directory
                from pathlib import Path
                default_dir = Path.home() / '.pdf_finder_cache'
                self.cache_dir_edit.setText(str(default_dir))
    
    def refresh_cache_stats(self):
        """Refresh cache statistics display."""
        if not self.hash_cache:
            self.cache_status_label.setText("Not Available")
            self.stats_table.setRowCount(0)
            self.health_label.setText("Hash cache is not available")
            self.health_progress.setValue(0)
            return
        
        try:
            stats = self.hash_cache.get_cache_stats()
            
            # Update cache status
            self.cache_status_label.setText("Active")
            self.cache_dir_label.setText(stats.get('cache_dir', 'N/A'))
            
            # Update statistics table
            self.stats_table.setRowCount(0)
            
            stats_data = [
                ("Persistent Entries", f"{stats.get('persistent_entries', 0):,}"),
                ("Valid Entries", f"{stats.get('valid_entries', 0):,}"),
                ("Memory Entries", f"{stats.get('memory_entries', 0):,}"),
                ("Total Accesses", f"{stats.get('total_accesses', 0):,}"),
                ("Cache Size", self._format_bytes(stats.get('cache_size_bytes', 0))),
                ("Max Cache Size", f"{stats.get('max_cache_size', 0):,} entries"),
                ("Cache TTL", f"{stats.get('cache_ttl_days', 0)} days")
            ]
            
            for i, (key, value) in enumerate(stats_data):
                self.stats_table.insertRow(i)
                self.stats_table.setItem(i, 0, QTableWidgetItem(key))
                self.stats_table.setItem(i, 1, QTableWidgetItem(value))
            
            # Update health indicator
            self.update_cache_health(stats)
            
        except Exception as e:
            self.log_operation(f"Error refreshing cache stats: {e}")
            self.cache_status_label.setText("Error")
    
    def update_cache_health(self, stats: Dict[str, Any]):
        """Update cache health indicator."""
        try:
            persistent_entries = stats.get('persistent_entries', 0)
            valid_entries = stats.get('valid_entries', 0)
            max_cache_size = stats.get('max_cache_size', 10000)
            
            # Calculate health percentage
            if max_cache_size > 0:
                usage_percentage = (persistent_entries / max_cache_size) * 100
            else:
                usage_percentage = 0
            
            # Calculate validity percentage
            if persistent_entries > 0:
                validity_percentage = (valid_entries / persistent_entries) * 100
            else:
                validity_percentage = 100
            
            # Overall health (weighted average)
            health_percentage = (usage_percentage * 0.3 + validity_percentage * 0.7)
            
            self.health_progress.setValue(int(health_percentage))
            
            # Determine health status
            if health_percentage >= 80:
                health_text = "Cache health is excellent"
                color = "#4CAF50"
            elif health_percentage >= 60:
                health_text = "Cache health is good"
                color = "#FFC107"
            elif health_percentage >= 40:
                health_text = "Cache health is fair"
                color = "#FF9800"
            else:
                health_text = "Cache health is poor"
                color = "#F44336"
            
            self.health_label.setText(f"{health_text} ({health_percentage:.1f}%)")
            self.health_progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
            
        except Exception as e:
            self.health_label.setText("Error calculating cache health")
            self.health_progress.setValue(0)
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
    
    def browse_cache_dir(self):
        """Browse for cache directory."""
        current_dir = self.cache_dir_edit.text()
        if not current_dir:
            current_dir = str(Path.home())
        
        directory = QFileDialog.getExistingDirectory(
            self, "Select Cache Directory", current_dir
        )
        
        if directory:
            self.cache_dir_edit.setText(directory)
    
    def apply_settings(self):
        """Apply cache settings."""
        settings = {
            'enable_hash_cache': self.enable_cache_checkbox.isChecked(),
            'max_cache_size': self.max_cache_size_spin.value(),
            'cache_ttl_days': self.cache_ttl_spin.value(),
            'memory_cache_size': self.memory_cache_spin.value(),
            'cache_dir': self.cache_dir_edit.text()
        }
        
        self.settings_changed.emit(settings)
        self.log_operation("Cache settings applied")
        
        QMessageBox.information(
            self, "Settings Applied", 
            "Cache settings have been applied. Restart may be required for some changes to take effect."
        )
    
    def clear_cache(self):
        """Clear the entire cache."""
        reply = QMessageBox.question(
            self, "Clear Cache",
            "Are you sure you want to clear the entire cache? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.hash_cache and self.hash_cache.clear_cache():
                    self.log_operation("Cache cleared successfully")
                    self.cache_cleared.emit()
                    self.refresh_cache_stats()
                    QMessageBox.information(self, "Cache Cleared", "Cache has been cleared successfully.")
                else:
                    self.log_operation("Failed to clear cache")
                    QMessageBox.warning(self, "Error", "Failed to clear cache.")
            except Exception as e:
                self.log_operation(f"Error clearing cache: {e}")
                QMessageBox.critical(self, "Error", f"Error clearing cache: {e}")
    
    def cleanup_expired(self):
        """Clean up expired cache entries."""
        try:
            if self.hash_cache:
                self.hash_cache._cleanup_cache()
                self.log_operation("Expired entries cleaned up")
                self.refresh_cache_stats()
                QMessageBox.information(self, "Cleanup Complete", "Expired cache entries have been cleaned up.")
            else:
                QMessageBox.warning(self, "Error", "Hash cache is not available.")
        except Exception as e:
            self.log_operation(f"Error cleaning up expired entries: {e}")
            QMessageBox.critical(self, "Error", f"Error cleaning up expired entries: {e}")
    
    def optimize_cache(self):
        """Optimize cache performance."""
        try:
            if self.hash_cache:
                # Force cleanup and memory optimization
                self.hash_cache._cleanup_cache()
                
                # Clear memory cache to free up memory
                with self.hash_cache.lock:
                    self.hash_cache.memory_cache.clear()
                    self.hash_cache.memory_cache_order.clear()
                
                self.log_operation("Cache optimized")
                self.refresh_cache_stats()
                QMessageBox.information(self, "Optimization Complete", "Cache has been optimized for better performance.")
            else:
                QMessageBox.warning(self, "Error", "Hash cache is not available.")
        except Exception as e:
            self.log_operation(f"Error optimizing cache: {e}")
            QMessageBox.critical(self, "Error", f"Error optimizing cache: {e}")
    
    def log_operation(self, message: str):
        """Log an operation message."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        self.refresh_timer.stop()
        super().closeEvent(event)
