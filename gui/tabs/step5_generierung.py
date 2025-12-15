"""
Step 5: PDF-Generierung mit ECHTER Klassensatz-Generierung
============================================================

Generiert EINE PDF-Datei für den Klassensatz mit:
- Optional: 2 Musterklausuren (ohne + mit Lösung)
- Alle ausgewählten Schüler-Klausuren
- Automatische Seitenlogik (Reorder 4-1-2-3 wenn nötig)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar, QTextEdit,
    QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
from pathlib import Path
import json
from datetime import datetime


class PDFGeneratorThread(QThread):
    """Background-Thread für PDF-Generierung"""
    
    progress = pyqtSignal(int, str)  # (value, message)
    finished = pyqtSignal(bool, str, str)  # (success, message, filepath)
    
    def __init__(self, klausur, selected_schueler, musterklausuren, db, latex_gen):
        super().__init__()
        self.klausur = klausur
        self.selected_schueler = selected_schueler
        self.musterklausuren = musterklausuren
        self.db = db
        self.latex_gen = latex_gen
        
    def run(self):
        """PDF-Generierung ausführen"""
        try:
            # Ausgabeverzeichnis erstellen
            output_dir = Path('outputs')
            output_dir.mkdir(exist_ok=True)
            
            # Dateiname generieren
            datum_str = self.klausur.datum.replace('.', '-')
            filename = f"{datum_str}_{self.klausur.klasse}_{self.klausur.thema.replace(' ', '_')}_Klassensatz.pdf"
            output_path = output_dir / filename
            
            self.progress.emit(10, "Lade Aufgaben aus DB...")
            
            # Aufgaben laden
            aufgaben = []
            for aufgabe_id in self.klausur.aufgaben_ids:
                aufgabe = self.db.get_aufgabe_by_id(aufgabe_id)
                if aufgabe:
                    aufgaben.append(aufgabe)
            
            if not aufgaben:
                self.finished.emit(False, "Keine Aufgaben gefunden!", "")
                return
            
            self.progress.emit(30, "Generiere LaTeX-Code...")
            
            # LaTeX Generator aufrufen
            pdf_bytes = self.latex_gen.generate_klassensatz(
                klausur=self.klausur,
                aufgaben=aufgaben,
                schueler_list=self.selected_schueler,
                mit_musterklausuren=self.musterklausuren,
                progress_callback=lambda p, msg: self.progress.emit(p, msg)
            )
            
            if not pdf_bytes:
                self.finished.emit(False, "PDF-Generierung fehlgeschlagen!", "")
                return
            
            self.progress.emit(90, "Speichere PDF...")
            
            # PDF speichern
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            
            self.progress.emit(100, "Fertig!")
            self.finished.emit(True, f"Klassensatz erfolgreich erstellt!", str(output_path))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit(False, f"Fehler: {str(e)}", "")


class Step5Generierung(QWidget):
    """Step 5: PDF-Generierung mit Schülerauswahl"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.schueler_list = []
        self.selected_schueler = []
        self.generator_thread = None
        self.output_filepath = None
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)
        
        # Titel
        title = QLabel("Schritt 5/5: PDF-Generierung")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Info
        info = QLabel(
            "Wählen Sie die Schüler aus, für die der Klassensatz generiert werden soll.\n"
            "💡 Tipp: Mit 'Auswahl umkehren' können Sie schnell nur Nachschreiber auswählen!"
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Haupt-Layout
        main_layout = QHBoxLayout()
        
        # Links: Schülerauswahl
        left_layout = QVBoxLayout()
        
        schueler_group = QGroupBox("👥 Schülerauswahl")
        schueler_layout = QVBoxLayout(schueler_group)
        
        # Buttons für Massenauswahl
        buttons_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Alle auswählen")
        self.select_all_btn.clicked.connect(self.select_all)
        buttons_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("❌ Alle abwählen")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        buttons_layout.addWidget(self.deselect_all_btn)
        
        self.invert_btn = QPushButton("🔄 Auswahl umkehren")
        self.invert_btn.clicked.connect(self.invert_selection)
        self.invert_btn.setToolTip(
            "Kehrt die Auswahl um - praktisch für Nachschreiber!\n"
            "1. Alle auswählen\n"
            "2. Nachschreiber abwählen\n"
            "3. Auswahl umkehren"
        )
        buttons_layout.addWidget(self.invert_btn)
        
        schueler_layout.addLayout(buttons_layout)
        
        # Schüler-Liste mit Checkboxen
        self.schueler_list_widget = QListWidget()
        schueler_layout.addWidget(self.schueler_list_widget)
        
        # Statistik
        self.stats_label = QLabel("Keine Schüler geladen")
        schueler_layout.addWidget(self.stats_label)
        
        left_layout.addWidget(schueler_group)
        
        main_layout.addLayout(left_layout, 2)
        
        # Rechts: Generierung
        right_layout = QVBoxLayout()
        
        # Progress-Bereich
        progress_group = QGroupBox("⚙️ Generierung")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        progress_layout.addWidget(self.status_text)
        
        # Generate-Button
        self.generate_btn = QPushButton("📄 Klassensatz generieren")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setStyleSheet("font-size: 14pt; font-weight: bold;")
        self.generate_btn.clicked.connect(self.start_generation)
        progress_layout.addWidget(self.generate_btn)
        
        right_layout.addWidget(progress_group)
        
        # Download-Bereich
        download_group = QGroupBox("📥 Ausgabe")
        download_layout = QVBoxLayout(download_group)
        
        self.download_text = QTextEdit()
        self.download_text.setReadOnly(True)
        self.download_text.setMaximumHeight(100)
        download_layout.addWidget(self.download_text)
        
        # Ordner öffnen Button
        self.open_folder_btn = QPushButton("📁 Ordner öffnen")
        self.open_folder_btn.setVisible(False)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        download_layout.addWidget(self.open_folder_btn)
        
        right_layout.addWidget(download_group)
        
        main_layout.addLayout(right_layout, 1)
        
        layout.addLayout(main_layout)
        
    def on_enter(self):
        """Wird aufgerufen wenn Step 5 betreten wird"""
        self.load_schueler()
        self.update_status_initial()
        
    def load_schueler(self):
        """Schüler aus DB laden"""
        klausur = self.parent_tab.klausur
        db = self.parent_tab.db
        
        try:
            schueler = db.get_schueler_by_klasse(
                klausur.schuljahr,
                klausur.schule_kuerzel,
                klausur.klasse
            )
            
            self.schueler_list = schueler
            self.schueler_list_widget.clear()
            
            for s in schueler:
                item = QListWidgetItem()
                checkbox = QCheckBox(f"{s['nachname']}, {s['rufname']}")
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.update_stats)
                
                item.setData(Qt.ItemDataRole.UserRole, {
                    'schueler': s,
                    'checkbox': checkbox
                })
                
                self.schueler_list_widget.addItem(item)
                self.schueler_list_widget.setItemWidget(item, checkbox)
            
            self.selected_schueler = schueler.copy()
            self.update_stats()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Laden der Schüler:\n{e}"
            )
            
    def select_all(self):
        """Alle Schüler auswählen"""
        for i in range(self.schueler_list_widget.count()):
            item = self.schueler_list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            checkbox = data['checkbox']
            checkbox.setChecked(True)
        
        self.update_stats()
        
    def deselect_all(self):
        """Alle Schüler abwählen"""
        for i in range(self.schueler_list_widget.count()):
            item = self.schueler_list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            checkbox = data['checkbox']
            checkbox.setChecked(False)
        
        self.update_stats()
        
    def invert_selection(self):
        """Auswahl umkehren"""
        for i in range(self.schueler_list_widget.count()):
            item = self.schueler_list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            checkbox = data['checkbox']
            checkbox.setChecked(not checkbox.isChecked())
        
        self.update_stats()
        
    def update_stats(self):
        """Statistik aktualisieren"""
        count = 0
        
        for i in range(self.schueler_list_widget.count()):
            item = self.schueler_list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            checkbox = data['checkbox']
            
            if checkbox.isChecked():
                count += 1
        
        total = len(self.schueler_list)
        
        # Berücksichtige Musterklausuren
        klausur = self.parent_tab.klausur
        muster = 2 if (hasattr(klausur, 'pdf_options') and klausur.pdf_options.get('musterklausuren', True)) else 0
        
        self.stats_label.setText(
            f"✅ {count} von {total} Schülern ausgewählt\n"
            f"→ {muster + count} Klausuren im Klassensatz"
        )
        
    def update_status_initial(self):
        """Initial-Status anzeigen"""
        klausur = self.parent_tab.klausur
        
        # Gesamtpunkte
        total_punkte = 0
        if hasattr(klausur, 'aufgaben_ids'):
            db = self.parent_tab.db
            for aufgabe_id in klausur.aufgaben_ids:
                aufgabe = db.get_aufgabe_by_id(aufgabe_id)
                if aufgabe:
                    total_punkte += aufgabe.get('punkte', 0) or 0
        
        # Seitenumbrüche
        page_breaks = len(klausur.page_breaks) if hasattr(klausur, 'page_breaks') else 0
        
        status_html = f"""
        <h3>📋 Bereit zur Generierung</h3>
        <p><b>Klausur:</b> {klausur.thema}<br>
        <b>Klasse:</b> {klausur.klasse}<br>
        <b>Aufgaben:</b> {len(klausur.aufgaben_ids) if hasattr(klausur, 'aufgaben_ids') else 0}<br>
        <b>Gesamtpunkte:</b> {total_punkte}<br>
        <b>Seitenumbrüche:</b> {page_breaks}</p>
        
        <p>Wählen Sie die Schüler aus und klicken Sie auf "Klassensatz generieren".</p>
        """
        
        self.status_text.setHtml(status_html)
        
    def start_generation(self):
        """PDF-Generierung starten"""
        
        # Sammle ausgewählte Schüler
        selected = []
        
        for i in range(self.schueler_list_widget.count()):
            item = self.schueler_list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            checkbox = data['checkbox']
            
            if checkbox.isChecked():
                selected.append(data['schueler'])
        
        if not selected:
            QMessageBox.warning(
                self,
                "Keine Schüler",
                "Bitte wählen Sie mindestens einen Schüler aus."
            )
            return
        
        # Musterklausuren?
        klausur = self.parent_tab.klausur
        musterklausuren = klausur.pdf_options.get('musterklausuren', True) if hasattr(klausur, 'pdf_options') else True
        
        # Bestätigung
        muster_text = "2 Musterklausuren + " if musterklausuren else ""
        reply = QMessageBox.question(
            self,
            "Generierung starten?",
            f"Es wird ein Klassensatz generiert:\n"
            f"{muster_text}{len(selected)} Schüler-Klausuren\n\n"
            f"→ Eine einzelne PDF-Datei\n\n"
            f"Fortfahren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # UI vorbereiten
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.open_folder_btn.setVisible(False)
        self.download_text.clear()
        
        # Status
        self.status_text.setHtml(
            f"<p>⏳ Generiere Klassensatz...</p>"
        )
        
        # LaTeX Generator vorbereiten
        from utils.latex_generator import LaTeXGenerator
        db_path = Path(__file__).parent.parent.parent / 'database' / 'sus.db'
        latex_gen = LaTeXGenerator(db_path=str(db_path))
        
        # Thread starten
        self.generator_thread = PDFGeneratorThread(
            klausur=klausur,
            selected_schueler=selected,
            musterklausuren=musterklausuren,
            db=self.parent_tab.db,
            latex_gen=latex_gen
        )
        
        self.generator_thread.progress.connect(self.on_progress)
        self.generator_thread.finished.connect(self.on_finished)
        self.generator_thread.start()
        
    def on_progress(self, value, message):
        """Progress-Update"""
        self.progress_bar.setValue(value)
        
        current_html = self.status_text.toHtml()
        self.status_text.setHtml(
            current_html + f"<p>{message}</p>"
        )
        
    def on_finished(self, success, message, filepath):
        """Generierung abgeschlossen"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        if success:
            self.output_filepath = filepath
            
            # Status
            status_html = f"""
            <h3>✅ Klassensatz erfolgreich generiert!</h3>
            <p>{message}</p>
            """
            self.status_text.setHtml(status_html)
            
            # Download-Link
            filename = Path(filepath).name
            download_html = f"""
            <p><b>📄 Datei:</b> {filename}</p>
            <p><b>📁 Pfad:</b> {filepath}</p>
            """
            self.download_text.setHtml(download_html)
            
            # Ordner-Button
            self.open_folder_btn.setVisible(True)
            
            # Info
            QMessageBox.information(
                self,
                "Fertig!",
                f"Klassensatz wurde erfolgreich generiert!\n\n"
                f"Datei: {filename}\n\n"
                f"Sie können den Ordner jetzt öffnen."
            )
        else:
            # Fehler
            status_html = f"""
            <h3>❌ Fehler bei der Generierung</h3>
            <p>{message}</p>
            """
            self.status_text.setHtml(status_html)
            
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler bei der PDF-Generierung:\n\n{message}"
            )
        
    def open_output_folder(self):
        """Ausgabe-Ordner öffnen"""
        if self.output_filepath:
            folder = Path(self.output_filepath).parent
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
        
    def validate(self):
        """Validierung"""
        return True
        
    def save_data(self):
        """Daten speichern"""
        print("Step 5: Klassensatz generiert")
        
    def reset(self):
        """Zurücksetzen"""
        self.schueler_list_widget.clear()
        self.schueler_list.clear()
        self.selected_schueler.clear()
        self.stats_label.setText("Keine Schüler geladen")
        self.status_text.clear()
        self.download_text.clear()
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.open_folder_btn.setVisible(False)
        self.output_filepath = None
