"""
Aufgaben-Dialog
===============

Dialog zum Erstellen und Bearbeiten von Aufgaben
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QSpinBox, QDialogButtonBox, QMessageBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt


class AufgabeDialog(QDialog):
    """Dialog zum Erstellen/Bearbeiten von Aufgaben"""
    
    def __init__(self, parent, aufgabe_data=None):
        super().__init__(parent)
        self.aufgabe_data = aufgabe_data
        self.setWindowTitle("Aufgabe bearbeiten" if aufgabe_data else "Neue Aufgabe")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self.setup_ui()
        
        if aufgabe_data:
            self.load_data(aufgabe_data)
            
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Titel
        self.titel_edit = QLineEdit()
        self.titel_edit.setPlaceholderText("z.B. Lineare Funktionen - Steigung berechnen")
        form.addRow("*Titel:", self.titel_edit)
        
        # Fach
        self.fach_combo = QComboBox()
        self.fach_combo.addItems(["Mathematik", "Physik", "Informatik"])
        form.addRow("*Fach:", self.fach_combo)
        
        # Themengebiet
        self.themengebiet_edit = QLineEdit()
        self.themengebiet_edit.setPlaceholderText("z.B. Lineare Funktionen")
        form.addRow("Themengebiet:", self.themengebiet_edit)
        
        # Schwierigkeit
        self.schwierigkeit_combo = QComboBox()
        self.schwierigkeit_combo.addItems(["leicht", "mittel", "schwer"])
        self.schwierigkeit_combo.setCurrentIndex(1)  # Default: mittel
        form.addRow("Schwierigkeit:", self.schwierigkeit_combo)
        
        # Punkte
        self.punkte_spin = QSpinBox()
        self.punkte_spin.setRange(1, 100)
        self.punkte_spin.setValue(10)
        form.addRow("*Punkte:", self.punkte_spin)
        
        # AFB
        self.afb_combo = QComboBox()
        self.afb_combo.addItems(["I", "II", "III"])
        self.afb_combo.setCurrentIndex(1)  # Default: II
        form.addRow("*Anforderungsbereich:", self.afb_combo)
        
        # Jahrgangsstufe
        self.jahrgangsstufe_spin = QSpinBox()
        self.jahrgangsstufe_spin.setRange(5, 13)
        self.jahrgangsstufe_spin.setValue(8)
        form.addRow("Jahrgangsstufe:", self.jahrgangsstufe_spin)
        
        # Schulform
        self.schulform_combo = QComboBox()
        self.schulform_combo.addItems(["Gymnasium", "Oberschule"])
        form.addRow("Schulform:", self.schulform_combo)
        
        # Platzbedarf
        self.platzbedarf_spin = QDoubleSpinBox()
        self.platzbedarf_spin.setRange(0.0, 30.0)
        self.platzbedarf_spin.setValue(5.0)
        self.platzbedarf_spin.setSuffix(" cm")
        self.platzbedarf_spin.setSingleStep(0.5)
        form.addRow("Platzbedarf:", self.platzbedarf_spin)
        
        # Schlagwörter
        self.schlagwoerter_edit = QLineEdit()
        self.schlagwoerter_edit.setPlaceholderText("z.B. Steigung, y-Achsenabschnitt, Graph")
        form.addRow("Schlagwörter:", self.schlagwoerter_edit)
        
        layout.addLayout(form)
        
        # LaTeX-Code (größeres Feld)
        layout.addWidget(QLabel("*LaTeX-Code:"))
        self.latex_edit = QTextEdit()
        self.latex_edit.setPlaceholderText(
            "LaTeX-Code der Aufgabe...\n\n"
            "Beispiel:\n"
            "Gegeben ist die lineare Funktion $f(x) = 2x + 3$.\n\n"
            "\\begin{enumerate}\n"
            "  \\item Bestimme die Steigung.\n"
            "  \\item Zeichne den Graphen.\n"
            "\\end{enumerate}"
        )
        self.latex_edit.setMinimumHeight(250)
        layout.addWidget(self.latex_edit)
        
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
        
    def load_data(self, data):
        """Daten in Dialog laden"""
        
        self.titel_edit.setText(data.get('titel', ''))
        
        if data.get('fach'):
            idx = self.fach_combo.findText(data['fach'])
            if idx >= 0:
                self.fach_combo.setCurrentIndex(idx)
        
        self.themengebiet_edit.setText(data.get('themengebiet', ''))
        
        if data.get('schwierigkeit'):
            idx = self.schwierigkeit_combo.findText(data['schwierigkeit'])
            if idx >= 0:
                self.schwierigkeit_combo.setCurrentIndex(idx)
        
        self.punkte_spin.setValue(data.get('punkte', 10))
        
        if data.get('anforderungsbereich'):
            idx = self.afb_combo.findText(data['anforderungsbereich'])
            if idx >= 0:
                self.afb_combo.setCurrentIndex(idx)
        
        self.jahrgangsstufe_spin.setValue(data.get('jahrgangsstufe', 8))
        
        if data.get('schulform'):
            idx = self.schulform_combo.findText(data['schulform'])
            if idx >= 0:
                self.schulform_combo.setCurrentIndex(idx)
        
        self.platzbedarf_spin.setValue(data.get('platzbedarf_min', 5.0))
        
        self.schlagwoerter_edit.setText(data.get('schlagwoerter', ''))
        
        self.latex_edit.setPlainText(data.get('latex_code', ''))
        
    def validate_and_accept(self):
        """Validierung vor Accept"""
        
        # Pflichtfelder prüfen
        if not self.titel_edit.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Titel ein.")
            self.titel_edit.setFocus()
            return
        
        if not self.latex_edit.toPlainText().strip():
            reply = QMessageBox.question(
                self,
                "LaTeX-Code fehlt",
                "Es wurde kein LaTeX-Code eingegeben.\n"
                "Möchten Sie trotzdem fortfahren?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.latex_edit.setFocus()
                return
        
        self.accept()
        
    def get_data(self):
        """Daten aus Dialog holen"""
        
        return {
            'template_id': 1,  # TODO: Template-Auswahl
            'titel': self.titel_edit.text().strip(),
            'fach': self.fach_combo.currentText(),
            'themengebiet': self.themengebiet_edit.text().strip(),
            'schwierigkeit': self.schwierigkeit_combo.currentText(),
            'punkte': self.punkte_spin.value(),
            'anforderungsbereich': self.afb_combo.currentText(),
            'jahrgangsstufe': self.jahrgangsstufe_spin.value(),
            'schulform': self.schulform_combo.currentText(),
            'platzbedarf_min': self.platzbedarf_spin.value(),
            'schlagwoerter': self.schlagwoerter_edit.text().strip(),
            'latex_code': self.latex_edit.toPlainText().strip(),
            'aufgaben_daten': '{}',  # TODO: JSON-Daten
        }


from PyQt6.QtWidgets import QLabel
