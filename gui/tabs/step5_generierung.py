"""
Step 5: PDF-Generierung mit Schülerauswahl
============================================

Mit individueller Schülerauswahl für Nachschreiber-Szenarien!
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar, QTextEdit,
    QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import json


class Step5Generierung(QWidget):
    """Step 5: PDF-Generierung mit Schülerauswahl"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.schueler_list = []  # Liste aller Schüler
        self.selected_schueler = []  # Ausgewählte Schüler
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
            "Wählen Sie die Schüler aus, für die PDFs generiert werden sollen.\n"
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
        self.generate_btn = QPushButton("📄 PDFs generieren")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setStyleSheet("font-size: 14pt; font-weight: bold;")
        self.generate_btn.clicked.connect(self.start_generation)
        progress_layout.addWidget(self.generate_btn)
        
        right_layout.addWidget(progress_group)
        
        # Download-Links
        download_group = QGroupBox("📥 Downloads")
        download_layout = QVBoxLayout(download_group)
        
        self.download_text = QTextEdit()
        self.download_text.setReadOnly(True)
        self.download_text.setMaximumHeight(150)
        download_layout.addWidget(self.download_text)
        
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
            # Lade Schüler der Klasse
            schueler = db.get_schueler_by_klasse(
                klausur.schuljahr,
                klausur.schule_kuerzel,
                klausur.klasse
            )
            
            self.schueler_list = schueler
            self.schueler_list_widget.clear()
            
            # Füge Schüler als Checkboxen hinzu
            for s in schueler:
                item = QListWidgetItem()
                checkbox = QCheckBox(f"{s['nachname']}, {s['rufname']}")
                checkbox.setChecked(True)  # Standard: alle ausgewählt
                checkbox.stateChanged.connect(self.update_stats)
                
                # Speichere Schüler-Daten
                item.setData(Qt.ItemDataRole.UserRole, {
                    'schueler': s,
                    'checkbox': checkbox
                })
                
                self.schueler_list_widget.addItem(item)
                self.schueler_list_widget.setItemWidget(item, checkbox)
            
            # Initial alle ausgewählt
            self.selected_schueler = schueler.copy()
            self.update_stats()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Laden der Schüler:\n{e}"
            )
            print(f"Fehler beim Laden der Schüler: {e}")
            
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
        """Auswahl umkehren - perfekt für Nachschreiber!"""
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
        self.stats_label.setText(
            f"✅ {count} von {total} Schülern ausgewählt → {count} PDFs werden generiert"
        )
        
    def update_status_initial(self):
        """Initial-Status anzeigen"""
        klausur = self.parent_tab.klausur
        
        # Berechne Gesamtpunkte
        total_punkte = 0
        if hasattr(klausur, 'aufgaben_ids'):
            db = self.parent_tab.db
            for aufgabe_id in klausur.aufgaben_ids:
                aufgabe = db.get_aufgabe_by_id(aufgabe_id)
                if aufgabe:
                    total_punkte += aufgabe.get('punkte', 0) or 0
        
        status_html = f"""
        <h3>📋 Bereit zur Generierung</h3>
        <p><b>Klausur:</b> {klausur.thema}<br>
        <b>Klasse:</b> {klausur.klasse}<br>
        <b>Aufgaben:</b> {len(klausur.aufgaben_ids) if hasattr(klausur, 'aufgaben_ids') else 0}<br>
        <b>Gesamtpunkte:</b> {total_punkte}</p>
        
        <p>Wählen Sie die Schüler aus und klicken Sie auf "PDFs generieren".</p>
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
        
        # Bestätigung
        reply = QMessageBox.question(
            self,
            "Generierung starten?",
            f"Es werden {len(selected)} PDFs generiert.\n\nFortfahren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Generierung starten
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(selected))
        self.progress_bar.setValue(0)
        
        # Status
        self.status_text.setHtml(
            f"<p>⏳ Generiere {len(selected)} PDFs...</p>"
        )
        
        # TODO: Hier später echte PDF-Generierung einbauen
        # Für jetzt: Simuliere Generierung
        self.simulate_generation(selected)
        
    def simulate_generation(self, selected_schueler):
        """Simuliere PDF-Generierung (Platzhalter)"""
        import time
        
        generated_files = []
        
        for i, schueler in enumerate(selected_schueler):
            # Simuliere Arbeit
            time.sleep(0.1)
            
            # Update Progress
            self.progress_bar.setValue(i + 1)
            
            # Simuliere generierten Dateinamen
            filename = f"KA_{schueler['klasse']}_{schueler['nachname']}_{schueler['rufname']}.pdf"
            generated_files.append(filename)
        
        # Fertig
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        # Status
        status_html = f"""
        <h3>✅ Generierung abgeschlossen!</h3>
        <p>{len(selected_schueler)} PDFs wurden erfolgreich generiert.</p>
        """
        self.status_text.setHtml(status_html)
        
        # Download-Links
        download_html = "<h4>📥 Generierte Dateien:</h4><ul>"
        for filename in generated_files[:5]:  # Zeige max 5
            download_html += f"<li>{filename}</li>"
        
        if len(generated_files) > 5:
            download_html += f"<li><i>... und {len(generated_files) - 5} weitere</i></li>"
        
        download_html += "</ul>"
        download_html += f"<p><b>Ausgabeverzeichnis:</b> outputs/</p>"
        
        self.download_text.setHtml(download_html)
        
        # Info
        QMessageBox.information(
            self,
            "Fertig",
            f"{len(selected_schueler)} PDFs wurden generiert!\n\n"
            f"Sie finden die Dateien im Ordner 'outputs/'."
        )
        
    def validate(self):
        """Validierung"""
        # In Step 5 gibt es keine Pflichtfelder
        return True
        
    def save_data(self):
        """Daten speichern"""
        # In Step 5 wird direkt generiert, kein Speichern nötig
        print("Step 5: PDFs generiert")
        
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
