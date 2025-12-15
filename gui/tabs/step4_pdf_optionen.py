"""
Step 4: PDF-Optionen (VEREINFACHT)
===================================

Nur noch: Musterklausuren ja/nein
Alles andere wird automatisch entschieden!
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox,
    QCheckBox, QTextEdit
)
from PyQt6.QtGui import QFont


class Step4PDFOptionen(QWidget):
    """Step 4: PDF-Optionen - VEREINFACHT"""
    
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
        info = QLabel(
            "Konfigurieren Sie die Optionen für den Klassensatz.\n"
            "Kopfzeile, Running Head und Seitenlogik werden automatisch angewendet."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Musterklausuren
        muster_group = QGroupBox("📄 Musterklausuren")
        muster_layout = QVBoxLayout(muster_group)
        
        self.muster_check = QCheckBox(
            "Musterklausuren vor dem Klassensatz einfügen"
        )
        self.muster_check.setChecked(True)
        self.muster_check.setToolTip(
            "Fügt vor dem Klassensatz 2 Musterklausuren ein:\n"
            "1x ohne Lösung (für dich)\n"
            "1x mit Lösung (für Nachbesprechung)"
        )
        muster_layout.addWidget(self.muster_check)
        
        layout.addWidget(muster_group)
        
        # Automatische Einstellungen (Info)
        auto_group = QGroupBox("⚙️ Automatische Einstellungen")
        auto_layout = QVBoxLayout(auto_group)
        
        auto_text = QTextEdit()
        auto_text.setReadOnly(True)
        auto_text.setMaximumHeight(200)
        auto_text.setHtml("""
        <p>Die folgenden Einstellungen werden <b>automatisch</b> angewendet:</p>
        <ul>
        <li><b>Kopfzeile:</b> Immer aktiv (Logo + QR + Infos)</li>
        <li><b>Running Head:</b> Auf Seiten 2-4</li>
        <li><b>Seitenlogik:</b>
            <ul>
            <li>3 Umbrüche → 4 Seiten → Reorder 4-1-2-3</li>
            <li>2 Umbrüche → 4 Seiten (+ leere S. 4) → Reorder 4-1-2-3</li>
            <li>0-1 Umbrüche → 1-2 Seiten → Kein Reorder</li>
            </ul>
        </li>
        <li><b>QR-Codes:</b> Automatisch für jeden Schüler (KaSuSId)</li>
        <li><b>Ausgabe:</b> Eine einzelne PDF-Datei für den Klassensatz</li>
        </ul>
        """)
        auto_layout.addWidget(auto_text)
        
        layout.addWidget(auto_group)
        
        # Zusammenfassung
        summary_group = QGroupBox("📋 Zusammenfassung")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        layout.addStretch()
        
    def on_enter(self):
        """Wird aufgerufen wenn Step 4 betreten wird"""
        self.update_summary()
        
    def update_summary(self):
        """Zusammenfassung aktualisieren"""
        klausur = self.parent_tab.klausur
        
        # Anzahl Aufgaben
        anzahl_aufgaben = len(klausur.aufgaben_ids) if hasattr(klausur, 'aufgaben_ids') else 0
        
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
        seiten = page_breaks + 1
        
        # Reorder-Logik
        if page_breaks >= 2:
            if page_breaks == 2:
                reorder_info = "4 Seiten (+ leere S. 4) → Reorder 4-1-2-3"
            else:  # >= 3
                reorder_info = f"{seiten} Seiten → Reorder 4-1-2-3"
        else:
            reorder_info = f"{seiten} Seite(n) → Kein Reorder"
        
        # Schüleranzahl
        try:
            db = self.parent_tab.db
            schueler_count = db.get_schueler_count_by_klasse(
                klausur.schuljahr,
                klausur.schule_kuerzel,
                klausur.klasse
            )
        except:
            schueler_count = 0
        
        # Musterklausuren
        muster_text = "Ja (2 Klausuren)" if self.muster_check.isChecked() else "Nein"
        
        summary_html = f"""
        <h3>📄 {klausur.thema}</h3>
        <p><b>Klasse:</b> {klausur.klasse} ({klausur.schule_kuerzel.upper()})<br>
        <b>Fach:</b> {klausur.fach} | <b>Typ:</b> {klausur.typ}<br>
        <b>Datum:</b> {klausur.datum} | <b>Dauer:</b> {klausur.zeit_minuten} Min</p>
        
        <p><b>Aufgaben:</b> {anzahl_aufgaben}<br>
        <b>Gesamtpunkte:</b> {total_punkte}<br>
        <b>Seitenumbrüche:</b> {page_breaks}<br>
        <b>→ Seitenlogik:</b> {reorder_info}</p>
        
        <p><b>Schüler:</b> {schueler_count}<br>
        <b>Musterklausuren:</b> {muster_text}</p>
        
        <p><b>→ Ausgabe:</b> 1 PDF-Datei (Klassensatz)</p>
        """
        
        self.summary_text.setHtml(summary_html)
        
    def validate(self):
        """Validierung"""
        return True
        
    def save_data(self):
        """Daten speichern"""
        klausur = self.parent_tab.klausur
        
        # Speichere nur Musterklausuren-Option
        klausur.pdf_options = {
            'musterklausuren': self.muster_check.isChecked()
        }
        
        print(f"Step 4 gespeichert: Musterklausuren={self.muster_check.isChecked()}")
        
    def reset(self):
        """Zurücksetzen"""
        self.muster_check.setChecked(True)
        self.summary_text.clear()
