"""
Hauptfenster mit Tab-Struktur
==============================

5 Haupttabs:
1. Dashboard
2. Klausur (5-Step-Wizard)
3. Aufgaben
4. Grafiken
5. Einstellungen
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QStatusBar, QMenuBar, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

from gui.tabs.dashboard_tab import DashboardTab
from gui.tabs.klausur_tab import KlausurTab
from gui.tabs.aufgaben_tab import AufgabenTab
from gui.tabs.grafiken_tab import GrafikenTab
from gui.tabs.einstellungen_tab import EinstellungenTab


class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Klausurengenerator v2.0 - Gymnasium Dörpen")
        self.setMinimumSize(QSize(1280, 800))
        
        # Zentriere Fenster auf Bildschirm
        self.center_on_screen()
        
        # UI aufbauen
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        
    def setup_ui(self):
        """UI-Komponenten erstellen"""
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab-Widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(True)
        
        # Tabs hinzufügen
        self.dashboard_tab = DashboardTab(self)
        self.klausur_tab = KlausurTab(self)
        self.aufgaben_tab = AufgabenTab(self)
        self.grafiken_tab = GrafikenTab(self)
        self.einstellungen_tab = EinstellungenTab(self)
        
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        self.tabs.addTab(self.klausur_tab, "📝 Klausur erstellen")
        self.tabs.addTab(self.aufgaben_tab, "📚 Aufgaben")
        self.tabs.addTab(self.grafiken_tab, "🖼️  Grafiken")
        self.tabs.addTab(self.einstellungen_tab, "⚙️  Einstellungen")
        
        # Tab-Wechsel-Signal verbinden
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.tabs)
        
    def setup_menu(self):
        """Menüleiste erstellen"""
        
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("&Datei")
        
        neue_klausur_action = QAction("&Neue Klausur", self)
        neue_klausur_action.setShortcut("Ctrl+N")
        neue_klausur_action.triggered.connect(self.neue_klausur)
        file_menu.addAction(neue_klausur_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Bearbeiten-Menü
        edit_menu = menubar.addMenu("&Bearbeiten")
        
        neue_aufgabe_action = QAction("Neue &Aufgabe", self)
        neue_aufgabe_action.setShortcut("Ctrl+Shift+N")
        neue_aufgabe_action.triggered.connect(self.neue_aufgabe)
        edit_menu.addAction(neue_aufgabe_action)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("&Hilfe")
        
        about_action = QAction("&Über", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_statusbar(self):
        """Statusleiste erstellen"""
        
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Bereit")
        
    def center_on_screen(self):
        """Fenster auf Bildschirm zentrieren"""
        screen_geometry = self.screen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
        
    def on_tab_changed(self, index):
        """Wird aufgerufen wenn Tab gewechselt wird"""
        
        tab_names = [
            "Dashboard",
            "Klausur erstellen",
            "Aufgaben verwalten",
            "Grafiken verwalten",
            "Einstellungen"
        ]
        
        if 0 <= index < len(tab_names):
            self.statusbar.showMessage(f"Tab: {tab_names[index]}")
            
    def neue_klausur(self):
        """Neue Klausur erstellen - Wechselt zu Klausur-Tab"""
        self.tabs.setCurrentIndex(1)  # Klausur-Tab
        self.klausur_tab.reset_wizard()
        
    def neue_aufgabe(self):
        """Neue Aufgabe erstellen - Wechselt zu Aufgaben-Tab"""
        self.tabs.setCurrentIndex(2)  # Aufgaben-Tab
        self.aufgaben_tab.neue_aufgabe()
        
    def show_about(self):
        """Über-Dialog anzeigen"""
        
        QMessageBox.about(
            self,
            "Über Klausurengenerator",
            "<h2>Klausurengenerator v2.0</h2>"
            "<p>Desktop-Anwendung für die Erstellung von Klassenarbeiten und Klausuren.</p>"
            "<p><b>Entwickelt für:</b> Gymnasium Dörpen</p>"
            "<p><b>Autor:</b> Hermann-Josef Hunfeld</p>"
            "<p><b>Technologie:</b> Python 3.11, PyQt6, SQLite</p>"
            "<p><b>Datum:</b> Dezember 2024</p>"
        )
        
    def closeEvent(self, event):
        """Wird beim Schließen des Fensters aufgerufen"""
        
        # TODO: Prüfen ob ungespeicherte Änderungen vorhanden
        
        reply = QMessageBox.question(
            self,
            "Beenden",
            "Möchten Sie den Klausurengenerator wirklich beenden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
