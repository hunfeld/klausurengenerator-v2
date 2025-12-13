"""
Step 4: PDF-Optionen
=====================

Auswahl welche PDFs generiert werden sollen
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QGroupBox, QComboBox, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.database import get_database


class Step4PDFOptionen(QWidget):
    """Step 4: PDF-Optionen auswählen"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.db = get_database()
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        
        # Titel
        title = QLabel("Schritt 4/5: PDF-Optionen")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        info_label = QLabel(
            "Wählen Sie aus, welche PDF-Varianten generiert werden sollen."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin: 10px 0;")
        main_layout.addWidget(info_label)
        
        # Optionen
        optionen_group = QGroupBox("Was soll generiert werden?")
        optionen_layout = QVBoxLayout(optionen_group)
        
        self.muster_ohne_cb = QCheckBox("Muster ohne Lösung (1 Exemplar)")
        self.muster_ohne_cb.setChecked(True)
        self.muster_ohne_cb.stateChanged.connect(self.update_preview)
        optionen_layout.addWidget(self.muster_ohne_cb)
        
        self.muster_mit_cb = QCheckBox("Muster mit Lösung (1 Exemplar)")
        self.muster_mit_cb.setChecked(True)
        self.muster_mit_cb.stateChanged.connect(self.update_preview)
        optionen_layout.addWidget(self.muster_mit_cb)
        
        self.klassensatz_ohne_cb = QCheckBox("Klassensatz ohne Lösung (personalisiert)")
        self.klassensatz_ohne_cb.setChecked(True)
        self.klassensatz_ohne_cb.stateChanged.connect(self.on_klassensatz_changed)
        optionen_layout.addWidget(self.klassensatz_ohne_cb)
        
        self.klassensatz_mit_cb = QCheckBox("Klassensatz mit Lösung (personalisiert)")
        self.klassensatz_mit_cb.setChecked(False)
        self.klassensatz_mit_cb.stateChanged.connect(self.on_klassensatz_changed)
        optionen_layout.addWidget(self.klassensatz_mit_cb)
        
        main_layout.addWidget(optionen_group)
        
        # Klassen-Auswahl (nur wenn Klassensatz)
        klasse_group = QGroupBox("Klassensatz-Optionen")
        klasse_layout = QVBoxLayout(klasse_group)
        
        klasse_info = QHBoxLayout()
        klasse_info.addWidget(QLabel("Klasse:"))
        
        self.klasse_label = QLabel()
        self.klasse_label.setStyleSheet("font-weight: bold;")
        klasse_info.addWidget(self.klasse_label)
        
        klasse_info.addStretch()
        
        klasse_info.addWidget(QLabel("Schuljahr:"))
        self.schuljahr_combo = QComboBox()
        self.schuljahr_combo.addItems(["2024/2025", "2025/2026"])
        self.schuljahr_combo.currentTextChanged.connect(self.load_schueler)
        klasse_info.addWidget(self.schuljahr_combo)
        
        klasse_layout.addLayout(klasse_info)
        
        schueler_layout = QHBoxLayout()
        schueler_layout.addWidget(QLabel("Schüler:"))
        
        self.schueler_count_label = QLabel()
        self.schueler_count_label.setStyleSheet("font-weight: bold;")
        schueler_layout.addWidget(self.schueler_count_label)
        
        schueler_layout.addStretch()
        
        reload_btn = QPushButton("🔄 Neu laden")
        reload_btn.clicked.connect(self.load_schueler)
        schueler_layout.addWidget(reload_btn)
        
        klasse_layout.addLayout(schueler_layout)
        
        self.klasse_group = klasse_group
        main_layout.addWidget(klasse_group)
        
        # Vorschau
        preview_group = QGroupBox("Vorschau")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_text)
        
        main_layout.addWidget(preview_group)
        
        main_layout.addStretch()
        
    def on_enter(self):
        """Wird aufgerufen wenn Step betreten wird"""
        klausur = self.parent_tab.klausur
        
        # Klasse anzeigen
        self.klasse_label.setText(f"{klausur.klasse} ({klausur.schule_kuerzel})")
        
        # Schuljahr setzen
        idx = self.schuljahr_combo.findText(klausur.schuljahr)
        if idx >= 0:
            self.schuljahr_combo.setCurrentIndex(idx)
        
        # Schüler laden
        self.load_schueler()
        
        # Preview aktualisieren
        self.update_preview()
        
    def on_klassensatz_changed(self):
        """Klassensatz-Checkbox wurde geändert"""
        klassensatz_gewuenscht = (
            self.klassensatz_ohne_cb.isChecked() or 
            self.klassensatz_mit_cb.isChecked()
        )
        
        self.klasse_group.setEnabled(klassensatz_gewuenscht)
        
        if klassensatz_gewuenscht:
            self.load_schueler()
        
        self.update_preview()
        
    def load_schueler(self):
        """Schüler aus Datenbank laden"""
        try:
            klausur = self.parent_tab.klausur
            schuljahr = self.schuljahr_combo.currentText()
            
            # Schüler laden
            schueler_data = self.db.get_schueler_by_klasse(
                schuljahr=schuljahr,
                schule=klausur.schule_kuerzel,
                klasse=klausur.klasse
            )
            
            # In Schueler-Objekte konvertieren
            from core.models import Schueler
            klausur.schueler = [Schueler.from_dict(s) for s in schueler_data]
            
            # Anzeige aktualisieren
            anzahl = len(klausur.schueler)
            self.schueler_count_label.setText(f"{anzahl} Schüler geladen")
            
            if anzahl == 0:
                self.schueler_count_label.setStyleSheet("font-weight: bold; color: red;")
                QMessageBox.warning(
                    self,
                    "Keine Schüler",
                    f"Keine Schüler gefunden für {klausur.klasse} im Schuljahr {schuljahr}."
                )
            else:
                self.schueler_count_label.setStyleSheet("font-weight: bold; color: green;")
            
            self.update_preview()
            
        except Exception as e:
            print(f"Fehler beim Laden der Schüler: {e}")
            QMessageBox.warning(self, "Fehler", f"Fehler beim Laden:\n{e}")
            
    def update_preview(self):
        """Vorschau aktualisieren"""
        klausur = self.parent_tab.klausur
        
        parts = []
        total_seiten = 0
        
        # Seitenzahl pro Variante (vereinfacht: 4 Seiten)
        seiten_pro_variante = 4
        
        if self.muster_ohne_cb.isChecked():
            parts.append(f"• Seiten 1-{seiten_pro_variante}: Muster ohne Lösung")
            total_seiten += seiten_pro_variante
        
        if self.muster_mit_cb.isChecked():
            start = total_seiten + 1
            end = total_seiten + seiten_pro_variante
            parts.append(f"• Seiten {start}-{end}: Muster mit Lösung")
            total_seiten += seiten_pro_variante
        
        anzahl_schueler = len(klausur.schueler)
        
        if self.klassensatz_ohne_cb.isChecked() and anzahl_schueler > 0:
            start = total_seiten + 1
            end = total_seiten + (anzahl_schueler * seiten_pro_variante)
            parts.append(
                f"• Seiten {start}-{end}: Klassensatz ohne Lösung "
                f"({anzahl_schueler} Schüler × {seiten_pro_variante} Seiten)"
            )
            total_seiten += anzahl_schueler * seiten_pro_variante
        
        if self.klassensatz_mit_cb.isChecked() and anzahl_schueler > 0:
            start = total_seiten + 1
            end = total_seiten + (anzahl_schueler * seiten_pro_variante)
            parts.append(
                f"• Seiten {start}-{end}: Klassensatz mit Lösung "
                f"({anzahl_schueler} Schüler × {seiten_pro_variante} Seiten)"
            )
            total_seiten += anzahl_schueler * seiten_pro_variante
        
        if not parts:
            preview = "<b>⚠️ Keine Optionen ausgewählt</b>"
        else:
            preview = "<b>PDF-Inhalt:</b><br><br>"
            preview += "<br>".join(parts)
            preview += f"<br><br><b>Gesamt: {total_seiten} Seiten</b>"
            
            # Geschätzte Dateigröße
            mb = (total_seiten * 0.03)  # ~30 KB pro Seite
            preview += f"<br>Geschätzte Größe: ~{mb:.1f} MB"
        
        self.preview_text.setHtml(preview)
        
    def validate(self):
        """Validierung"""
        
        # Mindestens eine Option ausgewählt?
        if not any([
            self.muster_ohne_cb.isChecked(),
            self.muster_mit_cb.isChecked(),
            self.klassensatz_ohne_cb.isChecked(),
            self.klassensatz_mit_cb.isChecked()
        ]):
            QMessageBox.warning(
                self,
                "Keine Option",
                "Bitte wählen Sie mindestens eine PDF-Option aus."
            )
            return False
        
        # Wenn Klassensatz: Schüler vorhanden?
        if (self.klassensatz_ohne_cb.isChecked() or self.klassensatz_mit_cb.isChecked()):
            klausur = self.parent_tab.klausur
            if len(klausur.schueler) == 0:
                QMessageBox.warning(
                    self,
                    "Keine Schüler",
                    "Für Klassensatz müssen Schüler geladen sein."
                )
                return False
        
        return True
        
    def save_data(self):
        """Daten speichern"""
        klausur = self.parent_tab.klausur
        
        klausur.muster_ohne_loesung = self.muster_ohne_cb.isChecked()
        klausur.muster_mit_loesung = self.muster_mit_cb.isChecked()
        klausur.klassensatz_ohne_loesung = self.klassensatz_ohne_cb.isChecked()
        klausur.klassensatz_mit_loesung = self.klassensatz_mit_cb.isChecked()
        
        print(f"Step 4 gespeichert: Optionen gesetzt, {len(klausur.schueler)} Schüler")
        
    def reset(self):
        """Zurücksetzen"""
        self.muster_ohne_cb.setChecked(True)
        self.muster_mit_cb.setChecked(True)
        self.klassensatz_ohne_cb.setChecked(True)
        self.klassensatz_mit_cb.setChecked(False)
