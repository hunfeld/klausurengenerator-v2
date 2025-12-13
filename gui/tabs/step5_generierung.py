"""
Step 5: PDF-Generierung
========================

Progress-Anzeige und PDF-Download
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class PDFGeneratorThread(QThread):
    """Thread für PDF-Generierung (damit GUI nicht einfriert)"""
    
    progress = pyqtSignal(int, str)  # Progress (0-100), Status-Text
    finished = pyqtSignal(bool, str)  # Success, Message/Error
    
    def __init__(self, klausur):
        super().__init__()
        self.klausur = klausur
        
    def run(self):
        """PDF generieren (in separatem Thread)"""
        try:
            self.progress.emit(10, "Klausur-Daten werden vorbereitet...")
            
            # TODO: LaTeX-Code generieren
            self.progress.emit(30, "LaTeX-Code wird generiert...")
            
            # TODO: PDF kompilieren
            self.progress.emit(60, "PDF wird kompiliert...")
            
            # TODO: Seiten umsortieren (4-1-2-3)
            self.progress.emit(80, "Seiten werden für Duplex-Druck umsortiert...")
            
            # TODO: Datei speichern
            self.progress.emit(95, "PDF wird gespeichert...")
            
            self.progress.emit(100, "Fertig!")
            self.finished.emit(True, "PDF erfolgreich generiert!")
            
        except Exception as e:
            self.finished.emit(False, f"Fehler: {e}")


class Step5Generierung(QWidget):
    """Step 5: PDF generieren"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.pdf_path = None
        self.generator_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        
        # Titel
        self.title_label = QLabel("Schritt 5/5: PDF wird generiert...")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        main_layout.addWidget(self.title_label)
        
        main_layout.addSpacing(20)
        
        # Status-Liste
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        main_layout.addWidget(self.status_text)
        
        # Progress-Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Status-Label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        main_layout.addSpacing(20)
        
        # Erfolg-Bereich (initial versteckt)
        self.success_widget = QWidget()
        success_layout = QVBoxLayout(self.success_widget)
        
        success_title = QLabel("✅ PDF erfolgreich generiert!")
        success_title_font = QFont()
        success_title_font.setPointSize(14)
        success_title_font.setBold(True)
        success_title.setFont(success_title_font)
        success_title.setStyleSheet("color: #28a745;")
        success_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_layout.addWidget(success_title)
        
        self.pdf_info_label = QLabel()
        self.pdf_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_layout.addWidget(self.pdf_info_label)
        
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Speichern unter...")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self.save_pdf)
        btn_layout.addWidget(self.save_btn)
        
        self.open_btn = QPushButton("👁️ PDF öffnen")
        self.open_btn.setMinimumHeight(40)
        self.open_btn.clicked.connect(self.open_pdf)
        btn_layout.addWidget(self.open_btn)
        
        success_layout.addLayout(btn_layout)
        
        self.success_widget.setVisible(False)
        main_layout.addWidget(self.success_widget)
        
        main_layout.addStretch()
        
        # Start-Button (initial sichtbar)
        self.start_btn = QPushButton("🚀 PDF jetzt generieren")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.clicked.connect(self.start_generation)
        main_layout.addWidget(self.start_btn)
        
    def on_enter(self):
        """Wird aufgerufen wenn Step betreten wird"""
        # Zusammenfassung anzeigen
        klausur = self.parent_tab.klausur
        
        summary = f"<b>Zusammenfassung:</b><br>"
        summary += f"• Fach: {klausur.fach}<br>"
        summary += f"• Klasse: {klausur.klasse}<br>"
        summary += f"• Thema: {klausur.thema}<br>"
        summary += f"• Aufgaben: {klausur.anzahl_aufgaben}<br>"
        summary += f"• Punkte: {klausur.gesamtpunkte}<br>"
        
        if klausur.muster_ohne_loesung:
            summary += "• ✓ Muster ohne Lösung<br>"
        if klausur.muster_mit_loesung:
            summary += "• ✓ Muster mit Lösung<br>"
        if klausur.klassensatz_ohne_loesung:
            summary += f"• ✓ Klassensatz ohne Lösung ({klausur.anzahl_schueler} Schüler)<br>"
        if klausur.klassensatz_mit_loesung:
            summary += f"• ✓ Klassensatz mit Lösung ({klausur.anzahl_schueler} Schüler)<br>"
        
        self.status_text.setHtml(summary)
        
    def start_generation(self):
        """PDF-Generierung starten"""
        
        self.start_btn.setVisible(False)
        self.status_label.setText("Generierung läuft...")
        
        klausur = self.parent_tab.klausur
        
        # Thread starten
        self.generator_thread = PDFGeneratorThread(klausur)
        self.generator_thread.progress.connect(self.on_progress)
        self.generator_thread.finished.connect(self.on_finished)
        self.generator_thread.start()
        
    def on_progress(self, value, text):
        """Progress-Update"""
        self.progress_bar.setValue(value)
        self.status_label.setText(text)
        
        # Log
        current = self.status_text.toPlainText()
        self.status_text.setPlainText(current + f"\n{text}")
        
    def on_finished(self, success, message):
        """Generierung abgeschlossen"""
        
        if success:
            self.title_label.setText("✅ PDF erfolgreich generiert!")
            self.title_label.setStyleSheet("color: #28a745;")
            
            klausur = self.parent_tab.klausur
            filename = f"{klausur.dateiname_basis}_Komplett.pdf"
            
            self.pdf_info_label.setText(
                f"<b>Datei:</b> {filename}<br>"
                f"<b>Seiten:</b> ~100 (geschätzt)<br>"
                f"<b>Größe:</b> ~3 MB (geschätzt)"
            )
            
            self.success_widget.setVisible(True)
            
        else:
            self.title_label.setText("❌ Fehler bei PDF-Generierung")
            self.title_label.setStyleSheet("color: #dc3545;")
            self.status_label.setText(message)
            
            QMessageBox.critical(self, "Fehler", message)
            
            # Start-Button wieder anzeigen
            self.start_btn.setVisible(True)
            
    def save_pdf(self):
        """PDF speichern unter..."""
        klausur = self.parent_tab.klausur
        default_name = f"{klausur.dateiname_basis}_Komplett.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF speichern",
            default_name,
            "PDF-Dateien (*.pdf)"
        )
        
        if file_path:
            # TODO: Datei kopieren
            QMessageBox.information(self, "Gespeichert", f"PDF gespeichert unter:\n{file_path}")
            
    def open_pdf(self):
        """PDF öffnen"""
        # TODO: PDF mit Standard-Viewer öffnen
        QMessageBox.information(self, "Info", "PDF würde hier geöffnet werden")
        
    def validate(self):
        """Validierung"""
        return True
        
    def save_data(self):
        """Daten speichern"""
        print("Step 5: PDF generiert")
        
    def reset(self):
        """Zurücksetzen"""
        self.progress_bar.setValue(0)
        self.status_label.clear()
        self.status_text.clear()
        self.success_widget.setVisible(False)
        self.start_btn.setVisible(True)
        self.title_label.setText("Schritt 5/5: PDF wird generiert...")
        self.title_label.setStyleSheet("")
