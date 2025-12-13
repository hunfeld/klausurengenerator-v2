"""
Step 5: PDF-Generierung
========================

Progress-Anzeige und PDF-Download mit vollständiger Backend-Integration
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QDesktopServices
from PyQt6.QtCore import QUrl

from core.latex_generator import generate_latex_for_klausur
from core.pdf_compiler import PDFCompiler
from core.pdf_reorderer import PDFReorderer
from pathlib import Path
import tempfile
import shutil


class PDFGeneratorThread(QThread):
    """Thread für PDF-Generierung (damit GUI nicht einfriert)"""
    
    progress = pyqtSignal(int, str)  # Progress (0-100), Status-Text
    finished = pyqtSignal(bool, str, str)  # Success, Message/Error, PDF-Path
    
    def __init__(self, klausur):
        super().__init__()
        self.klausur = klausur
        self.pdf_path = None
        
    def run(self):
        """PDF generieren (in separatem Thread)"""
        try:
            self.progress.emit(5, "Klausur-Daten werden vorbereitet...")
            
            # LaTeX-Code generieren
            self.progress.emit(15, "LaTeX-Code wird generiert...")
            latex_code = generate_latex_for_klausur(self.klausur)
            
            self.progress.emit(25, f"✅ LaTeX generiert ({len(latex_code)} Zeichen)")
            
            # PDF kompilieren
            self.progress.emit(30, "PDF wird kompiliert (kann 30-60 Sek dauern)...")
            compiler = PDFCompiler()
            pdf_bytes = compiler.compile_latex(latex_code)
            
            if not pdf_bytes:
                self.finished.emit(False, "Fehler bei PDF-Kompilierung", "")
                return
            
            self.progress.emit(65, "✅ PDF kompiliert")
            
            # Temporäre Datei erstellen
            temp_dir = Path(tempfile.gettempdir()) / "klausurengenerator"
            temp_dir.mkdir(exist_ok=True)
            
            temp_pdf = temp_dir / f"{self.klausur.dateiname_basis}_temp.pdf"
            
            with open(temp_pdf, 'wb') as f:
                f.write(pdf_bytes)
            
            self.progress.emit(75, "Seiten werden für Duplex-Druck umsortiert...")
            
            # Seiten umsortieren (4-1-2-3)
            reorderer = PDFReorderer()
            final_pdf = temp_dir / f"{self.klausur.dateiname_basis}_Komplett.pdf"
            
            success = reorderer.reorder_pdf(str(temp_pdf), str(final_pdf))
            
            if not success:
                # Falls Reordering fehlschlägt, verwende Original
                final_pdf = temp_pdf
                self.progress.emit(85, "⚠️ Reordering übersprungen")
            else:
                self.progress.emit(85, "✅ Seiten umsortiert")
            
            self.pdf_path = str(final_pdf)
            
            self.progress.emit(95, "PDF wird finalisiert...")
            self.progress.emit(100, "Fertig!")
            
            # Dateigröße ermitteln
            size_mb = final_pdf.stat().st_size / (1024 * 1024)
            
            self.finished.emit(
                True, 
                f"PDF erfolgreich generiert! ({size_mb:.1f} MB)", 
                self.pdf_path
            )
            
        except Exception as e:
            import traceback
            error_msg = f"Fehler: {e}\n\n{traceback.format_exc()}"
            self.finished.emit(False, error_msg, "")


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
        
        # Scroll zum Ende
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
        
    def on_finished(self, success, message, pdf_path):
        """Generierung abgeschlossen"""
        
        if success:
            self.title_label.setText("✅ PDF erfolgreich generiert!")
            self.title_label.setStyleSheet("color: #28a745;")
            
            self.pdf_path = pdf_path
            pdf_file = Path(pdf_path)
            
            # Dateiinfo
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            
            # Seitenzahl aus PDF ermitteln
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                page_count = len(reader.pages)
            except:
                page_count = "?"
            
            self.pdf_info_label.setText(
                f"<b>Datei:</b> {pdf_file.name}<br>"
                f"<b>Seiten:</b> {page_count}<br>"
                f"<b>Größe:</b> {size_mb:.2f} MB<br>"
                f"<b>Pfad:</b> {pdf_path}"
            )
            
            self.success_widget.setVisible(True)
            
        else:
            self.title_label.setText("❌ Fehler bei PDF-Generierung")
            self.title_label.setStyleSheet("color: #dc3545;")
            self.status_label.setText("Fehler aufgetreten")
            
            QMessageBox.critical(self, "Fehler", message)
            
            # Start-Button wieder anzeigen
            self.start_btn.setVisible(True)
            
    def save_pdf(self):
        """PDF speichern unter..."""
        if not self.pdf_path:
            return
        
        klausur = self.parent_tab.klausur
        default_name = f"{klausur.dateiname_basis}_Komplett.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF speichern",
            default_name,
            "PDF-Dateien (*.pdf)"
        )
        
        if file_path:
            try:
                shutil.copy2(self.pdf_path, file_path)
                QMessageBox.information(
                    self, 
                    "Gespeichert", 
                    f"PDF gespeichert unter:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    f"Fehler beim Speichern:\n{e}"
                )
            
    def open_pdf(self):
        """PDF öffnen"""
        if not self.pdf_path:
            return
        
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.pdf_path))
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Öffnen:\n{e}"
            )
        
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
        self.pdf_path = None
