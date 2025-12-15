"""
Grafiken-Tab für Klausurengenerator v2.0
========================================

Zeigt alle Grafiken aus der Datenbank mit Vorschau
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from core.database import get_database


class GrafikenTab(QWidget):
    """Tab zur Anzeige aller Grafiken aus der Datenbank"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.setup_ui()
        self.load_grafiken()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Grafiken-Übersicht")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh-Button
        self.refresh_btn = QPushButton("🔄 Aktualisieren")
        self.refresh_btn.clicked.connect(self.load_grafiken)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Split: Links (Tabelle) / Rechts (Vorschau)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Links: Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Aufgabe", "LaTeX-Name", "Dateiname", "Typ", "Größe (KB)"
        ])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_grafik_selected)
        splitter.addWidget(self.table)
        
        # Rechts: Vorschau
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_label = QLabel("🖼️ Vorschau")
        preview_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        preview_layout.addWidget(preview_label)
        
        # Info-Bereich
        self.info_text = QLabel("(Keine Grafik ausgewählt)")
        self.info_text.setWordWrap(True)
        self.info_text.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        preview_layout.addWidget(self.info_text)
        
        # ScrollArea für Bild
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(300)
        
        self.preview_label = QLabel("(Keine Vorschau)")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        scroll.setWidget(self.preview_label)
        preview_layout.addWidget(scroll)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
        # Status-Label
        self.status_label = QLabel("Lade Grafiken...")
        layout.addWidget(self.status_label)
        
    def load_grafiken(self):
        """Grafiken aus DB laden"""
        try:
            grafiken = self.db.get_all_grafiken()
            
            self.table.setRowCount(0)
            
            for grafik in grafiken:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(str(grafik['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(str(grafik['aufgabe_id'])))
                self.table.setItem(row, 2, QTableWidgetItem(grafik['latex_name']))
                self.table.setItem(row, 3, QTableWidgetItem(grafik['dateiname']))
                self.table.setItem(row, 4, QTableWidgetItem(grafik['dateityp']))
                
                # Größe in KB
                groesse_kb = grafik['groesse_bytes'] / 1024 if grafik['groesse_bytes'] else 0
                self.table.setItem(row, 5, QTableWidgetItem(f"{groesse_kb:.1f}"))
                
                # Speichere komplette Grafik als UserRole
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, grafik)
            
            # Status aktualisieren
            count = len(grafiken)
            total_size_mb = sum(g['groesse_bytes'] or 0 for g in grafiken) / (1024 * 1024)
            self.status_label.setText(f"✅ {count} Grafiken geladen ({total_size_mb:.2f} MB)")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden:\n{e}")
            self.status_label.setText("❌ Fehler beim Laden")
            
    def on_grafik_selected(self):
        """Grafik ausgewählt → Vorschau anzeigen"""
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            self.preview_label.clear()
            self.preview_label.setText("(Keine Vorschau)")
            self.info_text.setText("(Keine Grafik ausgewählt)")
            return
        
        row = selected_rows[0].row()
        grafik = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Info anzeigen
        info_html = f"""
        <b>Grafik-ID:</b> {grafik['id']}<br>
        <b>Aufgabe:</b> {grafik['aufgabe_id']}<br>
        <b>LaTeX-Name:</b> {grafik['latex_name']}<br>
        <b>Dateiname:</b> {grafik['dateiname']}<br>
        <b>Typ:</b> {grafik['dateityp']}<br>
        <b>Größe:</b> {grafik['groesse_bytes'] / 1024:.1f} KB<br>
        <b>Auflösung:</b> {grafik['breite_px']}×{grafik['hoehe_px']} px
        """
        self.info_text.setText(info_html)
        
        # Vorschau anzeigen
        try:
            blob = grafik['grafik_blob']
            
            pixmap = QPixmap()
            pixmap.loadFromData(blob)
            
            if pixmap.isNull():
                self.preview_label.setText("❌ Kann Bild nicht laden")
            else:
                # Skalieren auf max 800px Breite
                if pixmap.width() > 800:
                    pixmap = pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
                
                self.preview_label.setPixmap(pixmap)
                self.preview_label.setText("")
                
        except Exception as e:
            self.preview_label.setText(f"❌ Fehler: {e}")
