"""
Klausuren-Verwaltungs-Tab
==========================

Übersicht und Verwaltung aller erstellten Klausuren
Vollständiges CRUD (Create, Read, Update, Delete)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.database import get_database


class KlausurenVerwaltungTab(QWidget):
    """Klausuren-Verwaltung mit CRUD"""
    
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
        header_layout = QHBoxLayout()
        
        header = QLabel("Klausuren verwalten")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Buttons
        self.edit_btn = QPushButton("✏️ Bearbeiten")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_klausur)
        header_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Löschen")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_klausur)
        header_layout.addWidget(self.delete_btn)
        
        self.pdf_btn = QPushButton("📄 PDF neu generieren")
        self.pdf_btn.setEnabled(False)
        self.pdf_btn.clicked.connect(self.regenerate_pdf)
        header_layout.addWidget(self.pdf_btn)
        
        layout.addLayout(header_layout)
        
        # Filter
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Suche:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Titel oder Thema...")
        self.search_edit.textChanged.connect(self.filter_klausuren)
        filter_layout.addWidget(self.search_edit)
        
        filter_layout.addWidget(QLabel("Fach:"))
        self.fach_combo = QComboBox()
        self.fach_combo.addItems(["Alle", "Mathematik", "Physik", "Informatik"])
        self.fach_combo.currentTextChanged.connect(self.filter_klausuren)
        filter_layout.addWidget(self.fach_combo)
        
        filter_layout.addWidget(QLabel("Typ:"))
        self.typ_combo = QComboBox()
        self.typ_combo.addItems(["Alle", "Klassenarbeit", "Klausur", "Test"])
        self.typ_combo.currentTextChanged.connect(self.filter_klausuren)
        filter_layout.addWidget(self.typ_combo)
        
        layout.addLayout(filter_layout)
        
        # Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Titel", "Fach", "Klasse", "Typ", "Datum", 
            "Schule", "Erstellt"
        ])
        
        # Spaltenbreiten
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        # Selektion
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.edit_klausur)
        
        layout.addWidget(self.table)
        
        # Statistik
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
        
        # Daten laden
        self.load_klausuren()
        
    def load_klausuren(self):
        """Klausuren aus DB laden"""
        
        try:
            # Filter-Werte
            search = self.search_edit.text().strip()
            fach = self.fach_combo.currentText()
            typ = self.typ_combo.currentText()
            
            # Query bauen
            query = "SELECT * FROM klausuren WHERE 1=1"
            params = []
            
            if search:
                query += " AND (titel LIKE ? OR fach LIKE ? OR klasse LIKE ?)"
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if fach != "Alle":
                query += " AND fach = ?"
                params.append(fach)
            
            if typ != "Alle":
                query += " AND typ = ?"
                params.append(typ)
            
            query += " ORDER BY erstellt_am DESC"
            
            klausuren = self.db.execute_query(query, tuple(params))
            
            # Tabelle füllen
            self.table.setRowCount(0)
            
            for klausur in klausuren:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # ID (versteckt, aber für Referenz)
                id_item = QTableWidgetItem(str(klausur['id']))
                id_item.setData(Qt.ItemDataRole.UserRole, klausur)
                self.table.setItem(row, 0, id_item)
                
                # Daten
                self.table.setItem(row, 1, QTableWidgetItem(klausur.get('titel', '')))
                self.table.setItem(row, 2, QTableWidgetItem(klausur.get('fach', '')))
                self.table.setItem(row, 3, QTableWidgetItem(klausur.get('klasse', '')))
                self.table.setItem(row, 4, QTableWidgetItem(klausur.get('typ', '')))
                self.table.setItem(row, 5, QTableWidgetItem(klausur.get('datum', '')))
                self.table.setItem(row, 6, QTableWidgetItem(klausur.get('schule', '')))
                
                # Erstellt (nur Datum)
                erstellt = klausur.get('erstellt_am', '')
                if erstellt and ' ' in erstellt:
                    erstellt = erstellt.split(' ')[0]
                self.table.setItem(row, 7, QTableWidgetItem(erstellt))
            
            # Statistik
            total = self.db.execute_query("SELECT COUNT(*) as count FROM klausuren")[0]['count']
            self.stats_label.setText(f"Angezeigt: {len(klausuren)} von {total} Klausuren")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden:\n{e}")
            
    def filter_klausuren(self):
        """Filter anwenden"""
        self.load_klausuren()
        
    def on_selection_changed(self):
        """Selektion geändert"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.pdf_btn.setEnabled(has_selection)
        
    def edit_klausur(self):
        """Klausur bearbeiten"""
        
        selected = self.table.selectedItems()
        if not selected:
            return
        
        # Klausur-Daten holen
        row = selected[0].row()
        klausur_data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Öffne Wizard im Edit-Modus
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(1)  # Klausur-Tab
            klausur_tab = self.main_window.tabs.widget(1)
            if hasattr(klausur_tab, 'load_klausur_for_edit'):
                klausur_tab.load_klausur_for_edit(klausur_data)
            
    def delete_klausur(self):
        """Klausur löschen"""
        
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        klausur_data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Bestätigung
        reply = QMessageBox.question(
            self,
            "Löschen bestätigen",
            f"Klausur '{klausur_data['titel']}' wirklich löschen?\n\n"
            f"ACHTUNG: Dies kann nicht rückgängig gemacht werden!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute_update(
                    "DELETE FROM klausuren WHERE id = ?",
                    (klausur_data['id'],)
                )
                
                QMessageBox.information(self, "Erfolg", "Klausur wurde gelöscht!")
                self.load_klausuren()
                
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen:\n{e}")
                
    def regenerate_pdf(self):
        """PDF neu generieren"""
        
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        klausur_data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        QMessageBox.information(
            self,
            "PDF neu generieren",
            f"PDF-Neugenerierung für '{klausur_data['titel']}'\n\n"
            f"Diese Funktion ist in Vorbereitung.\n"
            f"Verwenden Sie vorerst den Wizard zum Bearbeiten."
        )
        
    def showEvent(self, event):
        """Wird aufgerufen wenn Tab angezeigt wird"""
        super().showEvent(event)
        self.load_klausuren()
