"""
Grafiken-Tab
============

Grafik-Pool mit Upload, Thumbnail-Ansicht und Verwaltung
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame, QMessageBox, QFileDialog,
    QLineEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QImage

from core.database import get_database
from gui.dialogs.grafik_dialog import GrafikDialog
import os


class GrafikWidget(QFrame):
    """Widget für einzelne Grafik-Vorschau"""
    
    def __init__(self, grafik_data, parent=None):
        super().__init__(parent)
        self.grafik_data = grafik_data
        self.parent_tab = parent
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMaximumWidth(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(180, 180)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        
        # Lade Thumbnail
        self.load_thumbnail()
        
        layout.addWidget(self.thumbnail_label)
        
        # Name
        name_label = QLabel(self.grafik_data['name'])
        name_label.setWordWrap(True)
        name_label.setMaximumWidth(180)
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        # Info
        info_text = f"{self.grafik_data['dateityp']}"
        if self.grafik_data.get('groesse_bytes'):
            size_kb = self.grafik_data['groesse_bytes'] / 1024
            info_text += f" • {size_kb:.1f} KB"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setMaximumWidth(30)
        delete_btn.clicked.connect(self.delete_grafik)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
    def load_thumbnail(self):
        """Thumbnail aus BLOB laden"""
        
        try:
            blob = self.grafik_data.get('grafik_blob')
            if blob:
                # BLOB zu QPixmap
                image = QImage()
                image.loadFromData(blob)
                
                pixmap = QPixmap.fromImage(image)
                
                # Skalieren auf 180x180
                scaled = pixmap.scaled(
                    180, 180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.thumbnail_label.setPixmap(scaled)
            else:
                self.thumbnail_label.setText("Kein Bild")
                
        except Exception as e:
            print(f"Fehler beim Laden des Thumbnails: {e}")
            self.thumbnail_label.setText("Fehler")
            
    def delete_grafik(self):
        """Grafik löschen"""
        
        reply = QMessageBox.question(
            self,
            "Löschen bestätigen",
            f"Grafik '{self.grafik_data['name']}' wirklich löschen?\n\n"
            f"ACHTUNG: Dies kann nicht rückgängig gemacht werden!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db = get_database()
                db.delete_grafik(self.grafik_data['id'])
                
                # Parent-Tab neu laden
                if self.parent_tab:
                    self.parent_tab.load_grafiken()
                    
                QMessageBox.information(self, "Erfolg", "Grafik wurde gelöscht!")
                
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen:\n{e}")


class GrafikenTab(QWidget):
    """Grafik-Pool Verwaltung"""
    
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
        
        header = QLabel("Grafik-Pool")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Upload-Button
        upload_btn = QPushButton("⬆️ Grafik hochladen")
        upload_btn.setMinimumHeight(35)
        upload_btn.clicked.connect(self.upload_grafik)
        header_layout.addWidget(upload_btn)
        
        layout.addLayout(header_layout)
        
        # Suche
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Suche:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Name oder Tags...")
        self.search_edit.textChanged.connect(self.filter_grafiken)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Scroll-Bereich für Grafiken
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container für Grid
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)
        
        # Statistik
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
        
        # Initial laden
        self.load_grafiken()
        
    def load_grafiken(self):
        """Grafiken aus DB laden"""
        
        try:
            # Clear Grid
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Grafiken laden
            grafiken = self.db.get_grafiken()
            
            # Grid füllen (3 Spalten)
            row = 0
            col = 0
            
            for grafik in grafiken:
                widget = GrafikWidget(grafik, self)
                self.grid_layout.addWidget(widget, row, col)
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            
            # Statistik
            self.stats_label.setText(f"Gesamt: {len(grafiken)} Grafiken")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden:\n{e}")
            
    def filter_grafiken(self):
        """Grafiken filtern (TODO: Implementierung)"""
        # TODO: Filter implementieren
        pass
        
    def upload_grafik(self):
        """Grafik hochladen"""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Grafik auswählen",
            "",
            "Bilder (*.png *.jpg *.jpeg *.svg *.pdf);;Alle Dateien (*.*)"
        )
        
        if not file_path:
            return
        
        # Dialog öffnen
        dialog = GrafikDialog(self, file_path)
        if dialog.exec():
            grafik_data = dialog.get_data()
            
            try:
                self.db.create_grafik(grafik_data)
                QMessageBox.information(self, "Erfolg", "Grafik wurde hochgeladen!")
                self.load_grafiken()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Hochladen:\n{e}")
                
    def showEvent(self, event):
        """Wird aufgerufen wenn Tab angezeigt wird"""
        super().showEvent(event)
        self.load_grafiken()
