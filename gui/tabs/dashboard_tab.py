"""
Dashboard-Tab
=============

Übersicht mit Live-Statistiken und letzten Klausuren
v1.0.5 - Doppelklick zum Bearbeiten hinzugefügt
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QListWidget, QListWidgetItem,
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.database import get_database


class DashboardTab(QWidget):
    """Dashboard - Startseite mit Live-Daten"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.db = get_database()
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Willkommens-Text
        welcome_label = QLabel("Willkommen im Klausurengenerator!")
        welcome_font = QFont()
        welcome_font.setPointSize(18)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        layout.addWidget(welcome_label)
        
        # Beschreibung
        desc_label = QLabel(
            "Erstellen Sie professionelle Klassenarbeiten und Klausuren "
            "mit automatischer PDF-Generierung."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # Schnellaktionen
        actions_group = QGroupBox("Schnellaktionen")
        actions_layout = QVBoxLayout(actions_group)
        
        neue_klausur_btn = QPushButton("📝 Neue Klausur erstellen")
        neue_klausur_btn.setMinimumHeight(50)
        neue_klausur_btn.clicked.connect(self.neue_klausur)
        actions_layout.addWidget(neue_klausur_btn)
        
        aufgaben_btn = QPushButton("📚 Aufgaben durchsuchen")
        aufgaben_btn.setMinimumHeight(50)
        aufgaben_btn.clicked.connect(self.aufgaben_oeffnen)
        actions_layout.addWidget(aufgaben_btn)
        
        layout.addWidget(actions_group)
        
        # Statistik mit echten Daten
        stats_layout = QHBoxLayout()
        
        self.aufgaben_stat = self.create_stat_widget("Aufgaben", "...")
        self.klausuren_stat = self.create_stat_widget("Klausuren", "...")
        self.grafiken_stat = self.create_stat_widget("Grafiken", "...")
        self.schueler_stat = self.create_stat_widget("Schüler", "...")
        
        stats_layout.addWidget(self.aufgaben_stat)
        stats_layout.addWidget(self.klausuren_stat)
        stats_layout.addWidget(self.grafiken_stat)
        stats_layout.addWidget(self.schueler_stat)
        
        layout.addLayout(stats_layout)
        
        # Letzte Klausuren
        recent_group = QGroupBox("Letzte Klausuren (Doppelklick zum Bearbeiten)")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(200)
        # NEU: Doppelklick-Signal verbinden!
        self.recent_list.itemDoubleClicked.connect(self.klausur_bearbeiten)
        recent_layout.addWidget(self.recent_list)
        
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.clicked.connect(self.load_data)
        recent_layout.addWidget(refresh_btn)
        
        layout.addWidget(recent_group)
        
        layout.addStretch()
        
        # Initial Daten laden
        self.load_data()
        
    def create_stat_widget(self, label, value):
        """Statistik-Widget erstellen"""
        
        group = QGroupBox(label)
        layout = QVBoxLayout(group)
        
        value_label = QLabel(value)
        value_label.setObjectName("stat_value")
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(value_label)
        
        # Speichere Label-Referenz für Updates
        group.value_label = value_label
        
        return group
        
    def load_data(self):
        """Daten aus Datenbank laden"""
        
        try:
            # Statistiken laden
            stats = self.db.get_statistics()
            
            # Statistik-Widgets aktualisieren
            self.aufgaben_stat.value_label.setText(str(stats.get('aufgaben', 0)))
            self.klausuren_stat.value_label.setText(str(stats.get('klausuren', 0)))
            self.grafiken_stat.value_label.setText(str(stats.get('grafiken', 0)))
            self.schueler_stat.value_label.setText(str(stats.get('schueler', 0)))
            
            # Letzte Klausuren laden
            self.load_recent_klausuren()
            
        except Exception as e:
            print(f"Fehler beim Laden der Dashboard-Daten: {e}")
            import traceback
            traceback.print_exc()
            
    def load_recent_klausuren(self):
        """
        Letzte Klausuren aus DB laden
        
        JETZT AUS DER RICHTIGEN TABELLE: klausuren
        """
        
        try:
            self.recent_list.clear()
            
            # Nutze die Methode aus database.py (greift auf 'klausuren' zu!)
            klausuren = self.db.get_recent_klausuren(limit=10)
            
            if klausuren:
                for klausur in klausuren:
                    # Format: "Mathematik - Lineare Funktionen (8a, 15.03.2024)"
                    fach = klausur.get('fach', 'Unbekannt')
                    titel = klausur.get('titel', 'Ohne Titel')
                    klasse = klausur.get('klasse', '?')
                    datum = klausur.get('datum', '?')
                    
                    text = f"{fach} - {titel} ({klasse}, {datum})"
                    
                    item = QListWidgetItem(text)
                    # Speichere komplette Klausur-Daten im Item!
                    item.setData(Qt.ItemDataRole.UserRole, klausur)
                    self.recent_list.addItem(item)
            else:
                self.recent_list.addItem("Noch keine Klausuren erstellt")
                
        except Exception as e:
            print(f"Fehler beim Laden der Klausuren: {e}")
            import traceback
            traceback.print_exc()
            self.recent_list.addItem(f"Fehler beim Laden: {e}")
            
    def klausur_bearbeiten(self, item):
        """
        Klausur bearbeiten (bei Doppelklick)
        
        NEU: Öffnet Wizard im Edit-Modus
        """
        # Klausur-Daten aus Item holen
        klausur_data = item.data(Qt.ItemDataRole.UserRole)
        
        if not klausur_data or not isinstance(klausur_data, dict):
            return
        
        # Öffne Wizard im Edit-Modus
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(1)  # Klausur-Tab
            klausur_tab = self.main_window.tabs.widget(1)
            if hasattr(klausur_tab, 'load_klausur_for_edit'):
                klausur_tab.load_klausur_for_edit(klausur_data)
            
    def neue_klausur(self):
        """Neue Klausur erstellen"""
        if self.main_window:
            # Wechsle zu Klausur-Tab und resette Wizard
            self.main_window.tabs.setCurrentIndex(1)
            klausur_tab = self.main_window.tabs.widget(1)
            if hasattr(klausur_tab, 'reset_wizard'):
                klausur_tab.reset_wizard()
            
    def aufgaben_oeffnen(self):
        """Aufgaben-Tab öffnen"""
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(3)  # Aufgaben ist jetzt Index 3!
            
    def showEvent(self, event):
        """Wird aufgerufen wenn Tab angezeigt wird"""
        super().showEvent(event)
        # Daten neu laden wenn Tab angezeigt wird
        self.load_data()
