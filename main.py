#!/usr/bin/env python3
"""
Klausurengenerator v2.0 - Entry Point
======================================

Einheitliche Desktop-Anwendung für Klausuren-Erstellung.

Autor: Hermann-Josef
Datum: 12.12.2024
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Projekt-Root zum Python-Path hinzufügen
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


def main():
    """Hauptfunktion - Startet die Anwendung"""
    
    # High-DPI-Support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Application erstellen
    app = QApplication(sys.argv)
    app.setApplicationName("Klausurengenerator")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Gymnasium Dörpen")
    
    # Icon setzen (falls vorhanden)
    # icon_path = project_root / "resources" / "icon.png"
    # if icon_path.exists():
    #     app.setWindowIcon(QIcon(str(icon_path)))
    
    # Stylesheet laden
    stylesheet_path = project_root / "resources" / "stylesheets" / "main.qss"
    if stylesheet_path.exists():
        with open(stylesheet_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    # Hauptfenster erstellen und anzeigen
    window = MainWindow()
    window.show()
    
    # Event-Loop starten
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
