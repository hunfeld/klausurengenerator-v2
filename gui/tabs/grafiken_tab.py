"""
Grafiken-Tab
============

Grafik-Pool verwalten
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QFont


class GrafikenTab(QWidget):
    """Grafik-Pool-Verwaltung"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titel
        title = QLabel("Grafik-Pool")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Platzhalter
        placeholder = QLabel("Hier kommt der Grafik-Pool hin:\n\n"
                           "• Grid-Ansicht mit Thumbnails\n"
                           "• Upload-Funktion\n"
                           "• Zwischenablage (Strg+V)\n"
                           "• Tags und Filter")
        placeholder.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        layout.addWidget(placeholder)
        
        # Buttons
        upload_btn = QPushButton("📁 Grafik hochladen")
        upload_btn.setMinimumHeight(40)
        layout.addWidget(upload_btn)
        
        layout.addStretch()
