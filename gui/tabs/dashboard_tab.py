"""
Dashboard-Tab
=============

Übersicht und Schnellzugriff
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QListWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class DashboardTab(QWidget):
    """Dashboard - Startseite"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Willkommens-Text
        welcome_label = QLabel("Willkommen im Klausurengenerator!")
        welcome_font = QFont()
        welcome_font.setPointSize(18)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        layout.addWidget(welcome_label)
        
        # Beschreibung
        desc_label = QLabel(
            "Erstellen Sie professionelle Klassenarbeiten und Klausuren "
            "mit automatischer PDF-Generierung."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # Schnellaktionen
        actions_group = QGroupBox("Schnellaktionen")
        actions_layout = QVBoxLayout(actions_group)
        
        neue_klausur_btn = QPushButton("📝 Neue Klausur erstellen")
        neue_klausur_btn.setMinimumHeight(50)
        neue_klausur_btn.clicked.connect(self.neue_klausur)
        actions_layout.addWidget(neue_klausur_btn)
        
        aufgaben_btn = QPushButton("📚 Aufgaben durchsuchen")
        aufgaben_btn.setMinimumHeight(50)
        aufgaben_btn.clicked.connect(self.aufgaben_oeffnen)
        actions_layout.addWidget(aufgaben_btn)
        
        layout.addWidget(actions_group)
        
        # Letzte Klausuren (Platzhalter)
        recent_group = QGroupBox("Letzte Klausuren")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.addItem("Noch keine Klausuren erstellt")
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        
        # Statistik (Platzhalter)
        stats_layout = QHBoxLayout()
        
        aufgaben_stat = self.create_stat_widget("Aufgaben", "0")
        klausuren_stat = self.create_stat_widget("Klausuren", "0")
        grafiken_stat = self.create_stat_widget("Grafiken", "0")
        
        stats_layout.addWidget(aufgaben_stat)
        stats_layout.addWidget(klausuren_stat)
        stats_layout.addWidget(grafiken_stat)
        
        layout.addLayout(stats_layout)
        
        layout.addStretch()
        
    def create_stat_widget(self, label, value):
        """Statistik-Widget erstellen"""
        
        group = QGroupBox(label)
        layout = QVBoxLayout(group)
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(value_label)
        
        return group
        
    def neue_klausur(self):
        """Neue Klausur erstellen"""
        if self.main_window:
            self.main_window.neue_klausur()
            
    def aufgaben_oeffnen(self):
        """Aufgaben-Tab öffnen"""
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(2)
