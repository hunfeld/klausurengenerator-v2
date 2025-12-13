"""
Step 3: Aufgaben anordnen
==========================

Drag & Drop Liste mit Seitenumbrüchen und Live-Statistik
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDrag
from PyQt6.QtCore import QMimeData


class Step3Anordnung(QWidget):
    """Step 3: Aufgaben anordnen mit Drag & Drop"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        
        # Titel
        title = QLabel("Schritt 3/5: Aufgaben anordnen")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        info_label = QLabel(
            "Ziehen Sie die Aufgaben per Drag & Drop in die gewünschte Reihenfolge. "
            "Fügen Sie Seitenumbrüche ein oder deaktivieren Sie Aufgaben bei Bedarf."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin: 10px 0;")
        main_layout.addWidget(info_label)
        
        # Liste
        list_label = QLabel("<b>Aufgaben-Reihenfolge</b>")
        main_layout.addWidget(list_label)
        
        self.aufgaben_list = QListWidget()
        self.aufgaben_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.aufgaben_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.aufgaben_list.model().rowsMoved.connect(self.on_order_changed)
        main_layout.addWidget(self.aufgaben_list, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.umbruch_btn = QPushButton("📄 Seitenumbruch einfügen")
        self.umbruch_btn.clicked.connect(self.insert_page_break)
        self.umbruch_btn.setEnabled(False)
        btn_layout.addWidget(self.umbruch_btn)
        
        self.remove_umbruch_btn = QPushButton("✕ Seitenumbruch entfernen")
        self.remove_umbruch_btn.clicked.connect(self.remove_page_break)
        self.remove_umbruch_btn.setEnabled(False)
        btn_layout.addWidget(self.remove_umbruch_btn)
        
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        # Statistik
        stats_group = QGroupBox("Statistik")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel()
        stats_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(stats_group)
        
        # Selektion-Handler
        self.aufgaben_list.itemSelectionChanged.connect(self.on_selection_changed)
        
    def on_enter(self):
        """Wird aufgerufen wenn Step betreten wird"""
        self.load_aufgaben()
        
    def load_aufgaben(self):
        """Aufgaben aus Klausur-Objekt laden"""
        self.aufgaben_list.clear()
        
        klausur = self.parent_tab.klausur
        
        for klausur_aufgabe in klausur.aufgaben:
            aufgabe = klausur_aufgabe.aufgabe
            
            # Item erstellen
            item_text = f"{klausur_aufgabe.reihenfolge}. {aufgabe.titel} ({aufgabe.punkte}P, ~{aufgabe.geschaetzte_zeit} Min)"
            
            if not klausur_aufgabe.ist_aktiv:
                item_text = f"[DEAKTIVIERT] {item_text}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, klausur_aufgabe)
            
            # Checkbox für Aktiv/Inaktiv
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if klausur_aufgabe.ist_aktiv else Qt.CheckState.Unchecked
            )
            
            self.aufgaben_list.addItem(item)
        
        self.update_stats()
        
    def on_selection_changed(self):
        """Selektion geändert"""
        selected = self.aufgaben_list.selectedItems()
        self.umbruch_btn.setEnabled(len(selected) > 0)
        self.remove_umbruch_btn.setEnabled(False)  # TODO: Implementieren
        
    def on_order_changed(self):
        """Reihenfolge wurde geändert"""
        # Reihenfolge-Nummern aktualisieren
        for i in range(self.aufgaben_list.count()):
            item = self.aufgaben_list.item(i)
            klausur_aufgabe = item.data(Qt.ItemDataRole.UserRole)
            klausur_aufgabe.reihenfolge = i + 1
            
            # Text aktualisieren
            aufgabe = klausur_aufgabe.aufgabe
            item_text = f"{klausur_aufgabe.reihenfolge}. {aufgabe.titel} ({aufgabe.punkte}P, ~{aufgabe.geschaetzte_zeit} Min)"
            
            if not klausur_aufgabe.ist_aktiv:
                item_text = f"[DEAKTIVIERT] {item_text}"
            
            item.setText(item_text)
        
        self.update_stats()
        
    def insert_page_break(self):
        """Seitenumbruch nach ausgewählter Aufgabe einfügen"""
        selected = self.aufgaben_list.selectedItems()
        if not selected:
            return
        
        row = self.aufgaben_list.row(selected[0])
        
        # Separator-Item einfügen
        separator = QListWidgetItem("━━━━━━━━━━━━━━ SEITENUMBRUCH ━━━━━━━━━━━━━━")
        separator.setFlags(Qt.ItemFlag.NoItemFlags)  # Nicht anklickbar
        separator.setBackground(Qt.GlobalColor.lightGray)
        separator.setData(Qt.ItemDataRole.UserRole, "PAGE_BREAK")
        
        self.aufgaben_list.insertItem(row + 1, separator)
        
        # Seiten-Nummern aktualisieren
        self.update_page_numbers()
        
    def remove_page_break(self):
        """Seitenumbruch entfernen"""
        # TODO: Implementieren
        pass
        
    def update_page_numbers(self):
        """Seiten-Nummern für alle Aufgaben aktualisieren"""
        current_page = 1
        
        for i in range(self.aufgaben_list.count()):
            item = self.aufgaben_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            
            if data == "PAGE_BREAK":
                current_page += 1
            elif isinstance(data, object) and hasattr(data, 'seite_nr'):
                data.seite_nr = current_page
        
        self.update_stats()
        
    def update_stats(self):
        """Statistik aktualisieren"""
        klausur = self.parent_tab.klausur
        
        aktive = sum(1 for ka in klausur.aufgaben if ka.ist_aktiv)
        inaktive = len(klausur.aufgaben) - aktive
        punkte = sum(ka.aufgabe.punkte for ka in klausur.aufgaben if ka.ist_aktiv)
        zeit = sum(ka.aufgabe.geschaetzte_zeit for ka in klausur.aufgaben if ka.ist_aktiv)
        
        # Seiten zählen
        seiten = 1
        for i in range(self.aufgaben_list.count()):
            item = self.aufgaben_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == "PAGE_BREAK":
                seiten += 1
        
        stats_text = (
            f"<b>Aufgaben:</b> {aktive} aktiv"
        )
        
        if inaktive > 0:
            stats_text += f" ({inaktive} deaktiviert)"
        
        stats_text += f"<br><b>Gesamtpunkte:</b> {punkte}<br>"
        stats_text += f"<b>Geschätzte Zeit:</b> ~{zeit} Min<br>"
        stats_text += f"<b>Seiten:</b> {seiten}"
        
        self.stats_label.setText(stats_text)
        
    def validate(self):
        """Validierung"""
        klausur = self.parent_tab.klausur
        
        # Mindestens 1 aktive Aufgabe
        aktive = sum(1 for ka in klausur.aufgaben if ka.ist_aktiv)
        
        if aktive == 0:
            QMessageBox.warning(
                self,
                "Keine aktiven Aufgaben",
                "Mindestens eine Aufgabe muss aktiviert sein."
            )
            return False
        
        return True
        
    def save_data(self):
        """Daten speichern"""
        # Checkbox-Status in Klausur-Objekt übernehmen
        for i in range(self.aufgaben_list.count()):
            item = self.aufgaben_list.item(i)
            klausur_aufgabe = item.data(Qt.ItemDataRole.UserRole)
            
            if isinstance(klausur_aufgabe, object) and hasattr(klausur_aufgabe, 'ist_aktiv'):
                klausur_aufgabe.ist_aktiv = (item.checkState() == Qt.CheckState.Checked)
        
        print(f"Step 3 gespeichert: Anordnung mit {self.aufgaben_list.count()} Items")
        
    def reset(self):
        """Zurücksetzen"""
        self.aufgaben_list.clear()
