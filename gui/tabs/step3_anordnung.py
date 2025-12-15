"""
Step 3: Aufgaben-Anordnung
===========================

Drag & Drop Sortierung + Seitenumbrüche
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox,
    QCheckBox, QSpinBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Step3Anordnung(QWidget):
    """Step 3: Aufgaben anordnen und Seitenumbrüche festlegen"""
    
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
        title = QLabel("Schritt 3/5: Aufgaben anordnen")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Info
        info = QLabel(
            "Sortieren Sie die Aufgaben per Drag & Drop in die gewünschte Reihenfolge.\n"
            "Legen Sie fest, auf welchen Seiten die Aufgaben erscheinen sollen."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Haupt-Bereich: Links (Liste) / Rechts (Optionen)
        main_layout = QHBoxLayout()
        
        # Links: Aufgaben-Liste (Drag & Drop)
        list_group = QGroupBox("📋 Aufgaben-Reihenfolge")
        list_layout = QVBoxLayout(list_group)
        
        self.aufgaben_list = QListWidget()
        self.aufgaben_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.aufgaben_list.itemSelectionChanged.connect(self.on_aufgabe_selected)
        list_layout.addWidget(self.aufgaben_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.move_up_btn = QPushButton("↑ Nach oben")
        self.move_up_btn.setEnabled(False)
        self.move_up_btn.clicked.connect(self.move_up)
        buttons_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("↓ Nach unten")
        self.move_down_btn.setEnabled(False)
        self.move_down_btn.clicked.connect(self.move_down)
        buttons_layout.addWidget(self.move_down_btn)
        
        list_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(list_group, 2)
        
        # Rechts: Optionen
        options_group = QGroupBox("⚙️ Optionen")
        options_layout = QVBoxLayout(options_group)
        
        # Seitenumbrüche
        page_breaks_group = QGroupBox("📄 Seitenumbrüche")
        page_breaks_layout = QFormLayout(page_breaks_group)
        
        self.page_break_check = QCheckBox("Nach dieser Aufgabe Seitenumbruch einfügen")
        self.page_break_check.setEnabled(False)
        self.page_break_check.stateChanged.connect(self.on_page_break_changed)
        page_breaks_layout.addRow(self.page_break_check)
        
        self.force_page_spin = QSpinBox()
        self.force_page_spin.setRange(1, 10)
        self.force_page_spin.setValue(1)
        self.force_page_spin.setEnabled(False)
        self.force_page_spin.valueChanged.connect(self.on_force_page_changed)
        page_breaks_layout.addRow("Seite (fix):", self.force_page_spin)
        
        options_layout.addWidget(page_breaks_group)
        
        # Gesamt-Statistik
        stats_group = QGroupBox("📊 Statistik")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Keine Aufgaben ausgewählt")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        options_layout.addWidget(stats_group)
        
        options_layout.addStretch()
        
        main_layout.addWidget(options_group, 1)
        
        layout.addLayout(main_layout)
        
    def on_enter(self):
        """Wird aufgerufen wenn Step 3 betreten wird"""
        self.load_aufgaben()
        
    def load_aufgaben(self):
        """Aufgaben aus Step 2 laden"""
        klausur = self.parent_tab.klausur
        
        self.aufgaben_list.clear()
        
        if not hasattr(klausur, 'aufgaben_ids') or not klausur.aufgaben_ids:
            QMessageBox.warning(
                self,
                "Keine Aufgaben",
                "Bitte wählen Sie zuerst Aufgaben in Step 2 aus."
            )
            return
        
        # Aufgaben aus DB laden
        db = self.parent_tab.db
        
        total_punkte = 0
        
        for i, aufgabe_id in enumerate(klausur.aufgaben_ids):
            aufgabe = db.get_aufgabe_by_id(aufgabe_id)
            
            if aufgabe:
                punkte = aufgabe.get('punkte', 0) or 0
                total_punkte += punkte
                
                item_text = f"Aufgabe {i+1}: {aufgabe['titel']} ({punkte} P)"
                item = QListWidgetItem(item_text)
                
                # Speichere Metadaten
                item.setData(Qt.ItemDataRole.UserRole, {
                    'aufgabe_id': aufgabe_id,
                    'aufgabe': aufgabe,
                    'page_break': False,
                    'force_page': None
                })
                
                self.aufgaben_list.addItem(item)
        
        # Statistik aktualisieren
        self.update_stats()
        
    def on_aufgabe_selected(self):
        """Aufgabe ausgewählt"""
        selected_items = self.aufgaben_list.selectedItems()
        
        has_selection = len(selected_items) > 0
        self.move_up_btn.setEnabled(has_selection)
        self.move_down_btn.setEnabled(has_selection)
        self.page_break_check.setEnabled(has_selection)
        self.force_page_spin.setEnabled(has_selection)
        
        if has_selection:
            item = selected_items[0]
            data = item.data(Qt.ItemDataRole.UserRole)
            
            # Lade gespeicherte Optionen
            self.page_break_check.blockSignals(True)
            self.page_break_check.setChecked(data.get('page_break', False))
            self.page_break_check.blockSignals(False)
            
            self.force_page_spin.blockSignals(True)
            self.force_page_spin.setValue(data.get('force_page') or 1)
            self.force_page_spin.blockSignals(False)
        
    def on_page_break_changed(self, state):
        """Seitenumbruch-Checkbox geändert"""
        selected_items = self.aufgaben_list.selectedItems()
        
        if selected_items:
            item = selected_items[0]
            data = item.data(Qt.ItemDataRole.UserRole)
            data['page_break'] = (state == Qt.CheckState.Checked.value)
            item.setData(Qt.ItemDataRole.UserRole, data)
            
            # Aktualisiere Anzeige
            self.update_item_display(item)
        
    def on_force_page_changed(self, value):
        """Feste Seite geändert"""
        selected_items = self.aufgaben_list.selectedItems()
        
        if selected_items:
            item = selected_items[0]
            data = item.data(Qt.ItemDataRole.UserRole)
            data['force_page'] = value
            item.setData(Qt.ItemDataRole.UserRole, data)
        
    def update_item_display(self, item):
        """Aktualisiere Item-Text mit Seitenumbruch-Info"""
        data = item.data(Qt.ItemDataRole.UserRole)
        aufgabe = data['aufgabe']
        index = self.aufgaben_list.row(item) + 1
        punkte = aufgabe.get('punkte', 0) or 0
        
        text = f"Aufgabe {index}: {aufgabe['titel']} ({punkte} P)"
        
        if data.get('page_break'):
            text += " [→ Seitenumbruch]"
        
        if data.get('force_page'):
            text += f" [Seite {data['force_page']}]"
        
        item.setText(text)
        
    def move_up(self):
        """Aufgabe nach oben verschieben"""
        current_row = self.aufgaben_list.currentRow()
        
        if current_row > 0:
            item = self.aufgaben_list.takeItem(current_row)
            self.aufgaben_list.insertItem(current_row - 1, item)
            self.aufgaben_list.setCurrentRow(current_row - 1)
            
            # Nummerierung aktualisieren
            self.update_numbering()
        
    def move_down(self):
        """Aufgabe nach unten verschieben"""
        current_row = self.aufgaben_list.currentRow()
        
        if current_row < self.aufgaben_list.count() - 1:
            item = self.aufgaben_list.takeItem(current_row)
            self.aufgaben_list.insertItem(current_row + 1, item)
            self.aufgaben_list.setCurrentRow(current_row + 1)
            
            # Nummerierung aktualisieren
            self.update_numbering()
        
    def update_numbering(self):
        """Nummerierung aller Items aktualisieren"""
        for i in range(self.aufgaben_list.count()):
            item = self.aufgaben_list.item(i)
            self.update_item_display(item)
        
    def update_stats(self):
        """Statistik aktualisieren"""
        count = self.aufgaben_list.count()
        
        if count == 0:
            self.stats_label.setText("Keine Aufgaben ausgewählt")
            return
        
        total_punkte = 0
        page_breaks = 0
        
        for i in range(count):
            item = self.aufgaben_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            
            aufgabe = data['aufgabe']
            total_punkte += aufgabe.get('punkte', 0) or 0
            
            if data.get('page_break'):
                page_breaks += 1
        
        # Geschätzte Seitenzahl (grob)
        estimated_pages = page_breaks + 1
        
        stats_text = f"""
        <b>Anzahl Aufgaben:</b> {count}<br>
        <b>Gesamtpunkte:</b> {total_punkte}<br>
        <b>Seitenumbrüche:</b> {page_breaks}<br>
        <b>≈ Seiten:</b> {estimated_pages}
        """
        
        self.stats_label.setText(stats_text)
        
    def validate(self):
        """Validierung"""
        if self.aufgaben_list.count() == 0:
            QMessageBox.warning(
                self,
                "Keine Aufgaben",
                "Bitte wählen Sie zuerst Aufgaben aus."
            )
            return False
        return True
        
    def save_data(self):
        """Daten speichern"""
        klausur = self.parent_tab.klausur
        
        # Speichere Reihenfolge
        sorted_ids = []
        page_breaks = []
        force_pages = {}
        
        for i in range(self.aufgaben_list.count()):
            item = self.aufgaben_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            
            aufgabe_id = data['aufgabe_id']
            sorted_ids.append(aufgabe_id)
            
            if data.get('page_break'):
                page_breaks.append(i)
            
            if data.get('force_page'):
                force_pages[i] = data['force_page']
        
        # Aktualisiere Klausur-Objekt
        klausur.aufgaben_ids = sorted_ids
        klausur.page_breaks = page_breaks
        klausur.force_pages = force_pages
        
        print(f"Step 3 gespeichert: {len(sorted_ids)} Aufgaben, {len(page_breaks)} Umbrüche")
        
    def reset(self):
        """Zurücksetzen"""
        self.aufgaben_list.clear()
        self.page_break_check.setChecked(False)
        self.force_page_spin.setValue(1)
        self.stats_label.setText("Keine Aufgaben ausgewählt")
