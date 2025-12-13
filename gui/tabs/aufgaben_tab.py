"""
Aufgaben-Tab
============

Aufgaben-Pool verwalten
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSplitter, QTableWidget, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AufgabenTab(QWidget):
    """Aufgaben-Verwaltung"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titel
        title = QLabel("Aufgaben-Verwaltung")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Platzhalter
        placeholder = QLabel("Hier kommt die Aufgaben-Verwaltung hin:\n\n"
                           "• Liste aller Aufgaben mit Filter\n"
                           "• Suche und Sortierung\n"
                           "• Detail-Ansicht mit LaTeX-Preview\n"
                           "• Bearbeiten/Löschen/Duplizieren")
        placeholder.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        layout.addWidget(placeholder)
        
        # Button
        btn = QPushButton("+ Neue Aufgabe erstellen")
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.neue_aufgabe)
        layout.addWidget(btn)
        
        layout.addStretch()
        
    def neue_aufgabe(self):
        """Neue Aufgabe erstellen"""
        # TODO: Dialog öffnen
        pass
