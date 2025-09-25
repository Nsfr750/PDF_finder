"""Filter dialog for PDF scanning options."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QFormLayout, QDialogButtonBox, QDateEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime, timedelta

class FilterDialog(QDialog):
    """Dialog for setting up PDF scanning filters."""
    
    filters_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the filter dialog."""
        super().__init__(parent)
        self.setWindowTitle("PDF Filters")
        self.setMinimumWidth(400)
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Size filter group
        size_group = QGroupBox("File Size")
        size_layout = QHBoxLayout()
        
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 1024 * 1024 * 1024)  # Up to 1GB
        self.min_size_spin.setSuffix(" KB")
        
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1, 1024 * 1024 * 1024)
        self.max_size_spin.setValue(100 * 1024)  # 100MB default
        self.max_size_spin.setSuffix(" KB")
        
        size_layout.addWidget(QLabel("Min:"))
        size_layout.addWidget(self.min_size_spin)
        size_layout.addWidget(QLabel("Max:"))
        size_layout.addWidget(self.max_size_spin)
        size_layout.addStretch()
        size_group.setLayout(size_layout)
        
        # Date filter group
        date_group = QGroupBox("Last Modified")
        date_layout = QFormLayout()
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        
        date_layout.addRow("From:", self.date_from)
        date_layout.addRow("To:", self.date_to)
        date_group.setLayout(date_layout)
        
        # Text comparison group
        text_group = QGroupBox("Text Comparison")
        text_layout = QVBoxLayout()
        
        self.enable_text_compare = QCheckBox("Enable text comparison")
        self.enable_text_compare.setChecked(True)
        
        self.similarity_spin = QDoubleSpinBox()
        self.similarity_spin.setRange(0.1, 1.0)
        self.similarity_spin.setSingleStep(0.1)
        self.similarity_spin.setValue(0.8)
        
        text_layout.addWidget(self.enable_text_compare)
        text_layout.addWidget(QLabel("Minimum text similarity:"))
        text_layout.addWidget(self.similarity_spin)
        text_group.setLayout(text_layout)
        
        # Name filter group
        name_group = QGroupBox("File Name")
        name_layout = QVBoxLayout()
        
        self.name_pattern = QLineEdit()
        self.name_pattern.setPlaceholderText("e.g., *report*.pdf")
        
        name_layout.addWidget(QLabel("Pattern:"))
        name_layout.addWidget(self.name_pattern)
        name_group.setLayout(name_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Reset |
            QDialogButtonBox.StandardButton.Cancel
        )
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_filters)
        buttons.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self.reset_filters)
        
        # Main layout
        layout.addWidget(size_group)
        layout.addWidget(date_group)
        layout.addWidget(name_group)
        layout.addWidget(text_group)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_filters(self):
        """Get the current filter settings."""
        return {
            'min_size': self.min_size_spin.value() * 1024,  # Convert KB to bytes
            'max_size': self.max_size_spin.value() * 1024,
            'date_from': self.date_from.date().toPyDate(),
            'date_to': self.date_to.date().toPyDate(),
            'name_pattern': self.name_pattern.text().strip(),
            'enable_text_compare': self.enable_text_compare.isChecked(),
            'min_similarity': self.similarity_spin.value()
        }
    
    def set_filters(self, filters):
        """Set the filter values."""
        self.min_size_spin.setValue(filters.get('min_size', 0) // 1024)
        self.max_size_spin.setValue(min(filters.get('max_size', 100 * 1024 * 1024) // 1024, 1024 * 1024))
        self.date_from.setDate(filters.get('date_from', QDate.currentDate().addMonths(-1)))
        self.date_to.setDate(filters.get('date_to', QDate.currentDate()))
        self.name_pattern.setText(filters.get('name_pattern', ''))
        self.enable_text_compare.setChecked(filters.get('enable_text_compare', True))
        self.similarity_spin.setValue(filters.get('min_similarity', 0.8))
    
    def apply_filters(self):
        """Apply the current filters and emit signal."""
        self.filters_changed.emit()
    
    def reset_filters(self):
        """Reset all filters to default values."""
        self.min_size_spin.setValue(0)
        self.max_size_spin.setValue(100 * 1024)  # 100MB
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.name_pattern.clear()
        self.enable_text_compare.setChecked(True)
        self.similarity_spin.setValue(0.8)
        self.filters_changed.emit()
