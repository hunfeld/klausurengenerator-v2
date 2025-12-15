"""
Step 4: PDF-Optionen
=====================

Konfiguration für PDF-Generierung
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QCheckBox, QComboBox, QFormLayout, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


class Step4PDFOptionen(QWidget):
    """Step 4: PDF-Optionen konfigurieren"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)
        
        # Titel
        title = QLabel("Schritt 4/5: PDF-Optionen")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Info
        info = QLabel("Konfigurieren Sie die Optionen für die PDF-Generierung.")
        layout.addWidget(info)
        
        # Haupt-Layout
        main_layout = QHBoxLayout()
        
        # Links: Optionen
        left_layout = QVBoxLayout()
        
        # Kopf-/Fußzeile
        header_group = QGroupBox("📄 Kopf- und Fußzeile")
        header_layout = QVBoxLayout(header_group)
        
        self.show_header_check = QCheckBox("Kopfzeile anzeigen (Logo + Infos)")
        self.show_header_check.setChecked(True)
        header_layout.addWidget(self.show_header_check)
        
        self.show_footer_check = QCheckBox("Fußzeile anzeigen (Seitenzahlen)")
        self.show_footer_check.setChecked(True)
        header_layout.addWidget(self.show_footer_check)
        
        left_layout.addWidget(header_group)
        
        # Lösungen
        solution_group = QGroupBox("🔍 Lösungen")
        solution_layout = QVBoxLayout(solution_group)
        
        self.generate_solutions_check = QCheckBox("Lösungen generieren (separates PDF)")
        self.generate_solutions_check.setChecked(False)
        solution_layout.addWidget(self.generate_solutions_check)
        
        left_layout.addWidget(solution_group)
        
        # Punkteverteilung
        points_group = QGroupBox("📊 Punkteverteilung")
        points_layout = QFormLayout(points_group)
        
        self.show_points_check = QCheckBox("Punkte bei Aufgaben anzeigen")
        self.show_points_check.setChecked(True)
        points_layout.addRow(self.show_points_check)
        
        self.show_total_check = QCheckBox("Gesamtpunktzahl anzeigen")
        self.show_total_check.setChecked(True)
        points_layout.addRow(self.show_total_check)
        
        left_layout.addWidget(points_group)
        
        # QR-Codes
        qr_group = QGroupBox("🔲 QR-Codes")
        qr_layout = QVBoxLayout(qr_group)
        
        self.generate_qr_check = QCheckBox("QR-Codes für Schüler generieren")
        self.generate_qr_check.setChecked(True)
        self.generate_qr_check.setToolTip(
            "Jeder Schüler erhält einen eindeutigen QR-Code zur Identifikation"
        )
        qr_layout.addWidget(self.generate_qr_check)
        
        left_layout.addWidget(qr_group)
        
        # Drucker-Optionen
        print_group = QGroupBox("🖨️ Druck-Optionen")
        print_layout = QFormLayout(print_group)
        
        self.duplex_combo = QComboBox()
        self.duplex_combo.addItems([
            "Einseitig (simplex)",
            "Doppelseitig (duplex)",
            "Doppelseitig mit Reorder (für manuellen Druck)"
        ])
        self.duplex_combo.setCurrentIndex(2)  # Duplex mit Reorder als Default
        print_layout.addRow("Druckmodus:", self.duplex_combo)
        
        left_layout.addWidget(print_group)
        
        left_layout.addStretch()
        main_layout.addLayout(left_layout, 1)
        
        # Rechts: Vorschau/Zusammenfassung
        right_layout = QVBoxLayout()
        
        summary_group = QGroupBox("📋 Zusammenfassung")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(300)
        summary_layout.addWidget(self.summary_text)
        
        right_layout.addWidget(summary_group)
        right_layout.addStretch()
        
        main_layout.addLayout(right_layout, 1)
        
        layout.addLayout(main_layout)
        
    def on_enter(self):
        """Wird aufgerufen wenn Step 4 betreten wird"""
        self.update_summary()
        
    def update_summary(self):
        """Zusammenfassung aktualisieren"""
        klausur = self.parent_tab.klausur
        
        # Hole Aufgaben-Infos
        anzahl_aufgaben = len(klausur.aufgaben_ids) if hasattr(klausur, 'aufgaben_ids') else 0
        
        # Berechne Gesamtpunkte
        total_punkte = 0
        if hasattr(klausur, 'aufgaben_ids'):
            db = self.parent_tab.db
            for aufgabe_id in klausur.aufgaben_ids:
                aufgabe = db.get_aufgabe_by_id(aufgabe_id)
                if aufgabe:
                    total_punkte += aufgabe.get('punkte', 0) or 0
        
        # Hole Schüleranzahl
        try:
            db = self.parent_tab.db
            schueler_count = db.get_schueler_count_by_klasse(
                klausur.schuljahr,
                klausur.schule_kuerzel,
                klausur.klasse
            )
        except:
            schueler_count = 0
        
        summary_html = f"""
        <h3>📄 {klausur.thema}</h3>
        <p><b>Schule:</b> {klausur.schule_kuerzel.upper()}<br>
        <b>Klasse:</b> {klausur.klasse}<br>
        <b>Fach:</b> {klausur.fach}<br>
        <b>Typ:</b> {klausur.typ}<br>
        <b>Datum:</b> {klausur.datum}<br>
        <b>Dauer:</b> {klausur.zeit_minuten} Minuten</p>
        
        <p><b>Aufgaben:</b> {anzahl_aufgaben}<br>
        <b>Gesamtpunkte:</b> {total_punkte}<br>
        <b>Schüler:</b> {schueler_count}</p>
        
        <p><b>→ PDFs werden generiert:</b> {schueler_count} Klassensatz-PDFs</p>
        """
        
        self.summary_text.setHtml(summary_html)
        
    def validate(self):
        """Validierung"""
        return True
        
    def save_data(self):
        """Daten speichern"""
        klausur = self.parent_tab.klausur
        
        # Speichere PDF-Optionen
        klausur.pdf_options = {
            'show_header': self.show_header_check.isChecked(),
            'show_footer': self.show_footer_check.isChecked(),
            'generate_solutions': self.generate_solutions_check.isChecked(),
            'show_points': self.show_points_check.isChecked(),
            'show_total': self.show_total_check.isChecked(),
            'generate_qr': self.generate_qr_check.isChecked(),
            'duplex_mode': self.duplex_combo.currentIndex()
        }
        
        print(f"Step 4 gespeichert: PDF-Optionen konfiguriert")
        
    def reset(self):
        """Zurücksetzen"""
        self.show_header_check.setChecked(True)
        self.show_footer_check.setChecked(True)
        self.generate_solutions_check.setChecked(False)
        self.show_points_check.setChecked(True)
        self.show_total_check.setChecked(True)
        self.generate_qr_check.setChecked(True)
        self.duplex_combo.setCurrentIndex(2)
        self.summary_text.clear()
