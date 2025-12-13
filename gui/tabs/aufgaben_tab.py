"""
Aufgaben-Tab
============

Aufgaben-Verwaltung mit Tabellen-Ansicht und Filter
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.database import get_database


class AufgabenTab(QWidget):
    """Aufgaben-Verwaltung"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.db = get_database()
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Aufgaben-Verwaltung")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Filter & Suche
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Suche:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Titel oder Themengebiet...")
        self.search_edit.textChanged.connect(self.filter_aufgaben)
        filter_layout.addWidget(self.search_edit, 2)
        
        filter_layout.addWidget(QLabel("Fach:"))
        
        self.fach_combo = QComboBox()
        self.fach_combo.addItems(["Alle", "Mathematik", "Physik", "Informatik"])
        self.fach_combo.currentTextChanged.connect(self.filter_aufgaben)
        filter_layout.addWidget(self.fach_combo, 1)
        
        layout.addLayout(filter_layout)
        
        # Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Titel", "Fach", "Themengebiet", "Schwierigkeit", "Punkte", "AFB"
        ])
        
        # Header-Größen
        header_table = self.table.horizontalHeader()
        header_table.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header_table.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header_table.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header_table.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        neue_btn = QPushButton("➕ Neue Aufgabe")
        neue_btn.clicked.connect(self.neue_aufgabe)
        btn_layout.addWidget(neue_btn)
        
        btn_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.clicked.connect(self.load_aufgaben)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Statistik
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
        
        # Initial laden
        self.load_aufgaben()
        
    def load_aufgaben(self):
        """Aufgaben aus DB laden"""
        
        try:
            aufgaben = self.db.get_aufgaben()
            
            self.table.setRowCount(len(aufgaben))
            
            for row, aufgabe_dict in enumerate(aufgaben):
                self.table.setItem(row, 0, QTableWidgetItem(str(aufgabe_dict['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(aufgabe_dict['titel'] or ''))
                self.table.setItem(row, 2, QTableWidgetItem(aufgabe_dict['fach'] or ''))
                self.table.setItem(row, 3, QTableWidgetItem(aufgabe_dict['themengebiet'] or ''))
                self.table.setItem(row, 4, QTableWidgetItem(aufgabe_dict['schwierigkeit'] or ''))
                self.table.setItem(row, 5, QTableWidgetItem(str(aufgabe_dict['punkte'] or 0)))
                self.table.setItem(row, 6, QTableWidgetItem(aufgabe_dict['anforderungsbereich'] or ''))
            
            self.update_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden:\n{e}")
            
    def filter_aufgaben(self):
        """Aufgaben filtern"""
        
        search_text = self.search_edit.text().lower()
        fach = self.fach_combo.currentText()
        
        for row in range(self.table.rowCount()):
            show_row = True
            
            if search_text:
                titel = self.table.item(row, 1).text().lower()
                thema = self.table.item(row, 3).text().lower()
                if search_text not in titel and search_text not in thema:
                    show_row = False
            
            if fach != "Alle":
                row_fach = self.table.item(row, 2).text()
                if row_fach != fach:
                    show_row = False
            
            self.table.setRowHidden(row, not show_row)
        
        self.update_stats()
        
    def update_stats(self):
        """Statistik aktualisieren"""
        
        total = self.table.rowCount()
        visible = sum(1 for row in range(total) if not self.table.isRowHidden(row))
        
        self.stats_label.setText(f"Angezeigt: {visible} von {total} Aufgaben")
        
    def neue_aufgabe(self):
        """Neue Aufgabe erstellen"""
        QMessageBox.information(
            self,
            "TODO",
            "Aufgaben-Editor wird in nächster Version implementiert."
        )
        
    def showEvent(self, event):
        """Wird aufgerufen wenn Tab angezeigt wird"""
        super().showEvent(event)
        self.load_aufgaben()
