"""
Step 2: Aufgaben auswählen
===========================

Master-Detail-View mit Filter und Preview
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSplitter, QTableWidget, QTableWidgetItem,
    QTextEdit, QCheckBox, QGroupBox, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.database import get_database
from core.models import Aufgabe, KlausurAufgabe


class Step2AufgabenAuswahl(QWidget):
    """Step 2: Aufgaben aus Pool auswählen"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.db = get_database()
        
        # Alle Aufgaben (werden beim Betreten geladen)
        self.all_aufgaben = []
        
        # Ausgewählte Aufgaben (IDs)
        self.selected_aufgaben_ids = set()
        
        # Current filter
        self.current_difficulty_filter = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Titel
        title = QLabel("Schritt 2/5: Aufgaben auswählen")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        main_layout.addSpacing(10)
        
        # Suche
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Suche:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Titel oder Thema durchsuchen...")
        self.search_edit.textChanged.connect(self.filter_aufgaben)
        search_layout.addWidget(self.search_edit)
        
        main_layout.addLayout(search_layout)
        
        # Filter-Buttons
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Schwierigkeit:"))
        
        self.filter_all_btn = QPushButton("Alle")
        self.filter_all_btn.setCheckable(True)
        self.filter_all_btn.setChecked(True)
        self.filter_all_btn.clicked.connect(lambda: self.set_difficulty_filter(None))
        filter_layout.addWidget(self.filter_all_btn)
        
        self.filter_leicht_btn = QPushButton("Leicht")
        self.filter_leicht_btn.setCheckable(True)
        self.filter_leicht_btn.clicked.connect(lambda: self.set_difficulty_filter("leicht"))
        filter_layout.addWidget(self.filter_leicht_btn)
        
        self.filter_mittel_btn = QPushButton("Mittel")
        self.filter_mittel_btn.setCheckable(True)
        self.filter_mittel_btn.clicked.connect(lambda: self.set_difficulty_filter("mittel"))
        filter_layout.addWidget(self.filter_mittel_btn)
        
        self.filter_schwer_btn = QPushButton("Schwer")
        self.filter_schwer_btn.setCheckable(True)
        self.filter_schwer_btn.clicked.connect(lambda: self.set_difficulty_filter("schwer"))
        filter_layout.addWidget(self.filter_schwer_btn)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # Splitter: Liste links, Preview rechts
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LINKE SEITE: Aufgaben-Liste
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("<b>Verfügbare Aufgaben</b>"))
        
        # Tabelle
        self.aufgaben_table = QTableWidget()
        self.aufgaben_table.setColumnCount(5)
        self.aufgaben_table.setHorizontalHeaderLabels(["✓", "Titel", "Punkte", "Schwierigkeit", "Thema"])
        self.aufgaben_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.aufgaben_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.aufgaben_table.itemSelectionChanged.connect(self.on_aufgabe_selected)
        
        # Spaltenbreiten
        header = self.aufgaben_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 30)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 60)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 100)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        left_layout.addWidget(self.aufgaben_table)
        splitter.addWidget(left_widget)
        
        # RECHTE SEITE: Preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_layout.addWidget(QLabel("<b>Vorschau</b>"))
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Wählen Sie eine Aufgabe aus um eine Vorschau zu sehen.")
        right_layout.addWidget(self.preview_text)
        
        splitter.addWidget(right_widget)
        
        # Verhältnis 60:40
        splitter.setStretchFactor(0, 60)
        splitter.setStretchFactor(1, 40)
        
        main_layout.addWidget(splitter, 1)
        
        # Statistik unten
        stats_group = QGroupBox("Ausgewählte Aufgaben")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Keine Aufgaben ausgewählt")
        stats_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(stats_group)
        
    def on_enter(self):
        """Wird aufgerufen wenn dieser Step betreten wird"""
        klausur = self.parent_tab.klausur
        print(f"Step 2: Laden Aufgaben für {klausur.fach}, Stufe {klausur.jahrgangsstufe}")
        self.load_aufgaben()
        
    def load_aufgaben(self):
        """Aufgaben aus DB laden"""
        try:
            klausur = self.parent_tab.klausur
            self.all_aufgaben = self.db.get_aufgaben(
                fach=klausur.fach,
                jahrgangsstufe=klausur.jahrgangsstufe
            )
            print(f"Gefunden: {len(self.all_aufgaben)} Aufgaben")
            self.filter_aufgaben()
        except Exception as e:
            print(f"Fehler beim Laden der Aufgaben: {e}")
            QMessageBox.warning(self, "Fehler", f"Fehler beim Laden:\n{e}")
    
    def set_difficulty_filter(self, difficulty):
        """Schwierigkeits-Filter setzen"""
        self.current_difficulty_filter = difficulty
        self.filter_all_btn.setChecked(difficulty is None)
        self.filter_leicht_btn.setChecked(difficulty == "leicht")
        self.filter_mittel_btn.setChecked(difficulty == "mittel")
        self.filter_schwer_btn.setChecked(difficulty == "schwer")
        self.filter_aufgaben()
    
    def filter_aufgaben(self):
        """Aufgaben filtern und anzeigen"""
        search_text = self.search_edit.text().lower()
        
        filtered = []
        for aufgabe in self.all_aufgaben:
            if self.current_difficulty_filter:
                if aufgabe.get('schwierigkeit') != self.current_difficulty_filter:
                    continue
            
            if search_text:
                titel = (aufgabe.get('titel') or '').lower()
                thema = (aufgabe.get('themengebiet') or '').lower()
                if search_text not in titel and search_text not in thema:
                    continue
            
            filtered.append(aufgabe)
        
        # Tabelle füllen
        self.aufgaben_table.setRowCount(len(filtered))
        
        for row, aufgabe in enumerate(filtered):
            # Checkbox
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            checkbox = QCheckBox()
            checkbox.setChecked(aufgabe['id'] in self.selected_aufgaben_ids)
            checkbox.stateChanged.connect(
                lambda state, aid=aufgabe['id']: self.toggle_aufgabe(aid, state)
            )
            checkbox_layout.addWidget(checkbox)
            self.aufgaben_table.setCellWidget(row, 0, checkbox_widget)
            
            # Andere Spalten
            self.aufgaben_table.setItem(row, 1, QTableWidgetItem(aufgabe.get('titel', '')))
            self.aufgaben_table.setItem(row, 2, QTableWidgetItem(str(aufgabe.get('punkte', 0))))
            
            schwierigkeit = aufgabe.get('schwierigkeit', '')
            self.aufgaben_table.setItem(row, 3, QTableWidgetItem(schwierigkeit.capitalize() if schwierigkeit else ''))
            self.aufgaben_table.setItem(row, 4, QTableWidgetItem(aufgabe.get('themengebiet', '')))
            
            # ID speichern
            self.aufgaben_table.item(row, 1).setData(Qt.ItemDataRole.UserRole, aufgabe['id'])
        
        self.update_stats()
    
    def toggle_aufgabe(self, aufgabe_id, state):
        """Aufgabe aus/abwählen"""
        if state == Qt.CheckState.Checked.value:
            self.selected_aufgaben_ids.add(aufgabe_id)
        else:
            self.selected_aufgaben_ids.discard(aufgabe_id)
        self.update_stats()
    
    def on_aufgabe_selected(self):
        """Aufgabe wurde ausgewählt -> Preview"""
        selected_rows = self.aufgaben_table.selectedIndexes()
        if not selected_rows:
            self.preview_text.clear()
            return
        
        row = selected_rows[0].row()
        aufgabe_id = self.aufgaben_table.item(row, 1).data(Qt.ItemDataRole.UserRole)
        aufgabe = next((a for a in self.all_aufgaben if a['id'] == aufgabe_id), None)
        
        if aufgabe:
            preview = f"<h3>{aufgabe.get('titel', '')}</h3>"
            preview += f"<p><b>Themengebiet:</b> {aufgabe.get('themengebiet', 'Keine Angabe')}</p>"
            preview += f"<p><b>Schwierigkeit:</b> {aufgabe.get('schwierigkeit', '').capitalize()}</p>"
            preview += f"<p><b>Punkte:</b> {aufgabe.get('punkte', 0)}</p>"
            preview += f"<p><b>Anforderungsbereich:</b> {aufgabe.get('anforderungsbereich', '')}</p>"
            
            if aufgabe.get('kompetenzen'):
                preview += f"<p><b>Kompetenzen:</b> {aufgabe.get('kompetenzen')}</p>"
            
            if aufgabe.get('latex_code'):
                preview += "<hr><p><b>LaTeX-Code:</b></p>"
                preview += f"<pre style='background: #f5f5f5; padding: 10px;'>{aufgabe.get('latex_code')[:500]}</pre>"
            
            self.preview_text.setHtml(preview)
    
    def update_stats(self):
        """Statistik aktualisieren"""
        if not self.selected_aufgaben_ids:
            self.stats_label.setText("Keine Aufgaben ausgewählt")
            return
        
        total_punkte = sum(
            a.get('punkte', 0) for a in self.all_aufgaben 
            if a['id'] in self.selected_aufgaben_ids
        )
        total_zeit = total_punkte * 2
        anzahl = len(self.selected_aufgaben_ids)
        verfuegbar = self.parent_tab.klausur.zeit_minuten
        
        self.stats_label.setText(
            f"✓ {anzahl} Aufgaben | {total_punkte} Punkte | "
            f"~{total_zeit} Min (verfügbar: {verfuegbar} Min)"
        )
        
    def validate(self):
        """Validierung"""
        if not self.selected_aufgaben_ids:
            QMessageBox.warning(self, "Keine Aufgaben", "Bitte wählen Sie mindestens eine Aufgabe aus.")
            return False
        return True
        
    def save_data(self):
        """Daten speichern"""
        klausur = self.parent_tab.klausur
        klausur.aufgaben.clear()
        
        for i, aufgabe_id in enumerate(sorted(self.selected_aufgaben_ids), start=1):
            aufgabe_data = next((a for a in self.all_aufgaben if a['id'] == aufgabe_id), None)
            if aufgabe_data:
                aufgabe = Aufgabe.from_dict(aufgabe_data)
                klausur_aufgabe = KlausurAufgabe(
                    aufgabe=aufgabe, reihenfolge=i, seite_nr=1, ist_aktiv=True
                )
                klausur.aufgaben.append(klausur_aufgabe)
        
        print(f"Step 2 gespeichert: {len(klausur.aufgaben)} Aufgaben")
        
    def reset(self):
        """Zurücksetzen"""
        self.selected_aufgaben_ids.clear()
        self.search_edit.clear()
        self.set_difficulty_filter(None)
        self.preview_text.clear()
        self.update_stats()
