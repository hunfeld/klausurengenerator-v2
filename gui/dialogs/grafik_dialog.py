"""
Grafik-Dialog
=============

Dialog zum Hochladen von Grafiken
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QLabel, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os


class GrafikDialog(QDialog):
    """Dialog zum Hochladen von Grafiken"""
    
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle("Grafik hochladen")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_preview()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        
        # Preview
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(300, 300)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Form
        form = QFormLayout()
        
        # Name (vorausgefüllt mit Dateinamen)
        self.name_edit = QLineEdit()
        filename = os.path.basename(self.file_path)
        name_without_ext = os.path.splitext(filename)[0]
        self.name_edit.setText(name_without_ext)
        form.addRow("*Name:", self.name_edit)
        
        # Beschreibung
        self.beschreibung_edit = QTextEdit()
        self.beschreibung_edit.setMaximumHeight(80)
        self.beschreibung_edit.setPlaceholderText("Optional: Beschreibung der Grafik...")
        form.addRow("Beschreibung:", self.beschreibung_edit)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("z.B. Geometrie, Dreieck, Pythagoras")
        form.addRow("Tags:", self.tags_edit)
        
        layout.addLayout(form)
        
        # Datei-Info
        file_size = os.path.getsize(self.file_path) / 1024
        ext = os.path.splitext(self.file_path)[1].upper()[1:]
        
        info_label = QLabel(f"Datei: {filename}\nTyp: {ext}\nGröße: {file_size:.1f} KB")
        info_label.setStyleSheet("color: #666; font-size: 10px; margin-top: 10px;")
        layout.addWidget(info_label)
        
        # Hinweis
        hint = QLabel("* = Pflichtfeld")
        hint.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        layout.addWidget(hint)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def load_preview(self):
        """Preview laden"""
        
        try:
            ext = os.path.splitext(self.file_path)[1].lower()
            
            if ext in ['.png', '.jpg', '.jpeg']:
                pixmap = QPixmap(self.file_path)
                scaled = pixmap.scaled(
                    300, 300,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
            elif ext == '.svg':
                self.preview_label.setText("SVG\n(Vorschau nicht verfügbar)")
            elif ext == '.pdf':
                self.preview_label.setText("PDF\n(Vorschau nicht verfügbar)")
            else:
                self.preview_label.setText("Unbekannter Typ")
                
        except Exception as e:
            print(f"Fehler beim Laden der Vorschau: {e}")
            self.preview_label.setText("Fehler bei Vorschau")
            
    def validate_and_accept(self):
        """Validierung"""
        
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Namen ein.")
            self.name_edit.setFocus()
            return
        
        # Dateigröße prüfen (max 2 MB)
        file_size = os.path.getsize(self.file_path)
        if file_size > 2 * 1024 * 1024:
            reply = QMessageBox.question(
                self,
                "Datei zu groß",
                f"Die Datei ist {file_size / (1024*1024):.1f} MB groß.\n"
                f"Empfohlen: max. 2 MB\n\n"
                f"Trotzdem hochladen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.accept()
        
    def get_data(self):
        """Daten holen"""
        
        # Datei lesen
        with open(self.file_path, 'rb') as f:
            blob = f.read()
        
        # Dateityp
        ext = os.path.splitext(self.file_path)[1].upper()[1:]
        if ext == 'JPG':
            ext = 'JPEG'
        
        # Größe
        file_size = os.path.getsize(self.file_path)
        
        return {
            'name': self.name_edit.text().strip(),
            'beschreibung': self.beschreibung_edit.toPlainText().strip(),
            'dateityp': ext,
            'grafik_blob': blob,
            'groesse_bytes': file_size,
            'tags': self.tags_edit.text().strip()
        }
