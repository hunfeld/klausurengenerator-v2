# 📝 Klausurengenerator v2.0

> **Desktop-Anwendung für die professionelle Erstellung von Klassenarbeiten und Klausuren**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange.svg)](https://github.com/hunfeld/klausurengenerator-v2)

---

## 🎯 Überblick

Der **Klausurengenerator v2.0** ist eine einheitliche Desktop-Anwendung zur Verwaltung und Erstellung von Klassenarbeiten, Klausuren und Tests. Die Anwendung bietet einen durchgängigen Workflow von der Aufgaben-Auswahl bis zur fertigen PDF-Generierung.

### ✨ Hauptfeatures

- ✅ **5-Step-Wizard** - Intuitive Klausur-Erstellung
- ✅ **Aufgaben-Pool** - Wiederverwendbare Aufgaben-Bibliothek
- ✅ **LaTeX-Integration** - Professionelle Dokument-Generierung
- ✅ **Automatische PDFs** - Muster und Klassensätze mit QR-Codes
- ✅ **SQLite-Datenbank** - Lokale, schnelle Datenverwaltung
- ✅ **Einheitliches Design** - Konsistente, moderne Oberfläche

---

## 🚀 Quick Start

### Installation

```bash
# Repository klonen
git clone https://github.com/hunfeld/klausurengenerator-v2.git
cd klausurengenerator-v2

# Dependencies installieren
pip install -r requirements.txt

# Datenbank bereitstellen (eigene sus.db kopieren)
# Windows:
copy "C:\path\to\your\sus.db" database\sus.db

# Linux/macOS:
cp /path/to/your/sus.db database/sus.db

# Anwendung starten
python main.py
```

### Anforderungen

- **Python:** 3.11 oder höher
- **Betriebssystem:** Windows 10+, macOS, Linux
- **RAM:** Mindestens 4 GB
- **Festplatte:** ~50 MB für Anwendung + Datenbankgröße

---

## 📊 Die 5 Tabs

### 1. 📊 Dashboard
Übersicht, Statistiken und Schnellzugriff zu kürzlich erstellten Klausuren.

### 2. 📝 Klausur erstellen
**5-Step-Wizard:**
1. **Setup** - Schule, Fach, Klasse, Datum, Thema
2. **Aufgaben** - Auswahl mit Filter und Preview
3. **Anordnung** - Drag & Drop, Seitenumbrüche
4. **Optionen** - Muster/Klassensatz, mit/ohne Lösung
5. **PDF** - Generierung mit Progress-Anzeige

### 3. 📚 Aufgaben
Verwaltung des Aufgaben-Pools: Erstellen, Bearbeiten, Suchen, Filtern.

### 4. 🖼️ Grafiken
Grafik-Pool mit Upload, Thumbnails und Tags.

### 5. ⚙️ Einstellungen
Schulen, Templates und System-Konfiguration.

---

## 🏗️ Technologie-Stack

| Komponente | Technologie |
|-----------|-------------|
| **GUI** | PyQt6 |
| **Datenbank** | SQLite |
| **PDF-Generierung** | LaTeX (via API) |
| **PDF-Verarbeitung** | PyPDF2 |
| **QR-Codes** | python-qrcode |
| **Styling** | QSS (Qt StyleSheets) |

---

## 📁 Projektstruktur

```
klausurengenerator_v2/
├── main.py                      # Entry Point
├── requirements.txt             # Dependencies
├── README.md                    # Dieses Dokument
├── GITHUB_SETUP.md              # Setup-Anleitung
│
├── gui/                         # GUI-Komponenten
│   ├── main_window.py           # Hauptfenster
│   ├── tabs/                    # Die 5 Tabs
│   │   ├── dashboard_tab.py
│   │   ├── klausur_tab.py
│   │   ├── step2_aufgabenauswahl.py
│   │   ├── aufgaben_tab.py
│   │   ├── grafiken_tab.py
│   │   └── einstellungen_tab.py
│   └── dialogs/                 # Dialoge
│
├── core/                        # Kernlogik
│   ├── database.py              # Datenbank-Anbindung
│   ├── models.py                # Datenmodelle
│   ├── latex_generator.py       # LaTeX-Generierung
│   ├── pdf_compiler.py          # PDF-Erstellung
│   └── pdf_reorderer.py         # Seiten-Umsortierung
│
├── utils/                       # Hilfsfunktionen
│   └── latex_helper.py
│
├── resources/                   # Ressourcen
│   └── stylesheets/
│       └── main.qss             # Stylesheet
│
└── database/
    └── sus.db                   # SQLite-Datenbank (nicht im Repo)
```

---

## 📈 Entwicklungs-Status

**Aktuell: v2.0-alpha** (In aktiver Entwicklung)

### ✅ Fertiggestellt
- [x] Projektstruktur
- [x] Hauptfenster mit Tab-System
- [x] Datenbank-Anbindung
- [x] Alle Datenmodelle
- [x] Wizard Step 1 (Setup)
- [x] Wizard Step 2 (Aufgaben-Auswahl)

### 🚧 In Arbeit
- [ ] Wizard Step 3 (Anordnung)
- [ ] Wizard Step 4 (PDF-Optionen)
- [ ] Wizard Step 5 (PDF-Generierung)
- [ ] LaTeX-Generator (aus v1.8 portieren)

### 📋 Geplant
- [ ] Aufgaben-Verwaltung (vollständig)
- [ ] Grafik-Pool
- [ ] Dashboard mit echten Daten
- [ ] Testing & Polishing

**Fortschritt:** ~35% ███████░░░░░░░░░░░░░

---

## 🤝 Beitragen

Dieses Projekt ist derzeit in aktiver Entwicklung für das **Gymnasium Dörpen**.

Feedback und Vorschläge sind willkommen via:
- GitHub Issues
- Pull Requests
- Direkte Kommunikation

---

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details.

---

## 👨‍💻 Autor

**Hermann-Josef Hunfeld**  
Gymnasium Dörpen

- GitHub: [@hunfeld](https://github.com/hunfeld)

---

## 🙏 Danksagung

Entwickelt für die Erstellung professioneller Klassenarbeiten und Klausuren am Gymnasium Dörpen mit Unterstützung von Claude (Anthropic).

---

**Status:** 🚀 In aktiver Entwicklung | **Version:** 2.0-alpha | **Letzte Aktualisierung:** Dezember 2024
