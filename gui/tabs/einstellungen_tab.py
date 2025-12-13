"""
Einstellungen-Tab
=================

System-Konfiguration
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, 
    QPushButton, QFormLayout, QLineEdit
)
from PyQt6.QtGui import QFont


class EinstellungenTab(QWidget):
    """Einstellungen und Konfiguration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titel
        title = QLabel("Einstellungen")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Datenbank
        db_group = QGroupBox("Datenbank")
        db_layout = QFormLayout(db_group)
        
        db_path_edit = QLineEdit("database/sus.db")
        db_path_edit.setReadOnly(True)
        db_layout.addRow("Pfad:", db_path_edit)
        
        layout.addWidget(db_group)
        
        # Schulen
        schulen_group = QGroupBox("Schulen")
        schulen_layout = QVBoxLayout(schulen_group)
        
        placeholder = QLabel("• Gymnasium Dörpen\n• Gymnasium Papenburg\n• Oberschule")
        schulen_layout.addWidget(placeholder)
        
        schulen_btn = QPushButton("Schulen verwalten...")
        schulen_layout.addWidget(schulen_btn)
        
        layout.addWidget(schulen_group)
        
        # Templates
        templates_group = QGroupBox("Templates")
        templates_layout = QVBoxLayout(templates_group)
        
        templates_btn = QPushButton("Templates verwalten...")
        templates_layout.addWidget(templates_btn)
        
        layout.addWidget(templates_group)
        
        layout.addStretch()
        
        # Version
        version_label = QLabel("Version 2.0.0 | Dezember 2024")
        version_label.setStyleSheet("color: #999; font-size: 10pt;")
        layout.addWidget(version_label)
