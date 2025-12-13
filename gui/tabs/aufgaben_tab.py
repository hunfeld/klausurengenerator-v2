"""
Aufgaben-Tab
============

Vollständige Aufgaben-Verwaltung mit CRUD-Operationen
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.database import get_database
from gui.dialogs.aufgabe_dialog import AufgabeDialog


class AufgabenTab(QWidget):
    """Aufgaben-Verwaltung mit vollständigem CRUD"""
    
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
        
        filter_layout.addWidget(QLabel("Schwierigkeit:"))
        
        self.schwierigkeit_combo = QComboBox()
        self.schwierigkeit_combo.addItems(["Alle", "leicht", "mittel", "schwer"])
        self.schwierigkeit_combo.currentTextChanged.connect(self.filter_aufgaben)
        filter_layout.addWidget(self.schwierigkeit_combo, 1)
        
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
        self.table.doubleClicked.connect(self.edit_aufgabe)
        
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        neue_btn = QPushButton("➕ Neue Aufgabe")
        neue_btn.setMinimumHeight(35)
        neue_btn.clicked.connect(self.neue_aufgabe)
        btn_layout.addWidget(neue_btn)
        
        bearbeiten_btn = QPushButton("✏️ Bearbeiten")
        bearbeiten_btn.setMinimumHeight(35)
        bearbeiten_btn.clicked.connect(self.edit_aufgabe)
        btn_layout.addWidget(bearbeiten_btn)
        
        loeschen_btn = QPushButton("🗑️ Löschen")
        loeschen_btn.setMinimumHeight(35)
        loeschen_btn.clicked.connect(self.delete_aufgabe)
        btn_layout.addWidget(loeschen_btn)
        
        btn_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.setMinimumHeight(35)
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
        schwierigkeit = self.schwierigkeit_combo.currentText()
        
        for row in range(self.table.rowCount()):
            show_row = True
            
            # Suche
            if search_text:
                titel = self.table.item(row, 1).text().lower()
                thema = self.table.item(row, 3).text().lower()
                if search_text not in titel and search_text not in thema:
                    show_row = False
            
            # Fach-Filter
            if fach != "Alle":
                row_fach = self.table.item(row, 2).text()
                if row_fach != fach:
                    show_row = False
            
            # Schwierigkeits-Filter
            if schwierigkeit != "Alle":
                row_schwierigkeit = self.table.item(row, 4).text()
                if row_schwierigkeit != schwierigkeit:
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
        
        dialog = AufgabeDialog(self)
        if dialog.exec():
            aufgabe_data = dialog.get_data()
            
            try:
                self.db.create_aufgabe(aufgabe_data)
                QMessageBox.information(self, "Erfolg", "Aufgabe wurde erstellt!")
                self.load_aufgaben()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Erstellen:\n{e}")
                
    def edit_aufgabe(self):
        """Aufgabe bearbeiten"""
        
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Keine Auswahl", "Bitte wählen Sie eine Aufgabe aus.")
            return
        
        row = selected[0].row()
        aufgabe_id = int(self.table.item(row, 0).text())
        
        # Aufgabe aus DB laden
        aufgabe_dict = self.db.get_aufgabe_by_id(aufgabe_id)
        
        if not aufgabe_dict:
            QMessageBox.warning(self, "Fehler", "Aufgabe nicht gefunden.")
            return
        
        dialog = AufgabeDialog(self, aufgabe_dict)
        if dialog.exec():
            aufgabe_data = dialog.get_data()
            aufgabe_data['id'] = aufgabe_id
            
            try:
                self.db.update_aufgabe(aufgabe_data)
                QMessageBox.information(self, "Erfolg", "Aufgabe wurde aktualisiert!")
                self.load_aufgaben()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Aktualisieren:\n{e}")
                
    def delete_aufgabe(self):
        """Aufgabe löschen"""
        
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Keine Auswahl", "Bitte wählen Sie eine Aufgabe aus.")
            return
        
        row = selected[0].row()
        aufgabe_id = int(self.table.item(row, 0).text())
        titel = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Löschen bestätigen",
            f"Aufgabe '{titel}' wirklich löschen?\n\n"
            f"ACHTUNG: Dies kann nicht rückgängig gemacht werden!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_aufgabe(aufgabe_id)
                QMessageBox.information(self, "Erfolg", "Aufgabe wurde gelöscht!")
                self.load_aufgaben()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen:\n{e}")
        
    def showEvent(self, event):
        """Wird aufgerufen wenn Tab angezeigt wird"""
        super().showEvent(event)
        self.load_aufgaben()
