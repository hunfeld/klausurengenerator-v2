# 📝 Klausurengenerator v2.0

> **Desktop-Anwendung für die professionelle Erstellung von Klassenarbeiten und Klausuren**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)](https://pypi.org/project/PyQt6/)
[![Status](https://img.shields.io/badge/Status-85%25%20Ready-brightgreen.svg)](https://github.com/hunfeld/klausurengenerator-v2)

---

## 🎯 Überblick

Der **Klausurengenerator v2.0** ist eine professionelle Desktop-Anwendung zur Verwaltung und Erstellung von Klassenarbeiten, Klausuren und Tests. Die Anwendung bietet einen durchgängigen Workflow von der Aufgaben-Auswahl bis zur fertigen PDF-Generierung mit automatischer Duplex-Druck-Optimierung.

### ✨ Hauptfeatures

- ✅ **5-Step-Wizard** - Intuitive Klausur-Erstellung (100% fertig)
- ✅ **PDF-Engine** - LaTeX → PDF → Duplex-Reordering (100% fertig)
- ✅ **Dashboard** - Live-Statistiken aus Datenbank
- ✅ **Aufgaben-Pool** - Wiederverwendbare Aufgaben mit Filter & Suche
- ✅ **QR-Codes** - Automatische Schüler-Zuordnung
- ✅ **SQLite-Datenbank** - Lokale, schnelle Datenverwaltung
- ✅ **Einheitliches Design** - Moderne, professionelle Oberfläche

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
- **Internet:** Für LaTeX-PDF-Kompilierung (https://latex.ytotech.com)

---

## 📊 Die 5 Tabs

### 1. 📊 Dashboard ✅
**Übersicht mit Live-Daten:**
- Statistiken (Aufgaben, Klausuren, Grafiken, Schüler)
- Letzte 10 Klausuren
- Schnellaktionen

### 2. 📝 Klausur erstellen ✅
**5-Step-Wizard (komplett funktionsfähig):**
1. **Setup** - Schule, Fach, Klasse, Datum, Thema
2. **Aufgaben** - Auswahl mit Filter und Preview
3. **Anordnung** - Drag & Drop, Seitenumbrüche
4. **Optionen** - Muster/Klassensatz, mit/ohne Lösung
5. **PDF** - Generierung in ~30-60 Sekunden!

### 3. 📚 Aufgaben ✅
**Aufgaben-Verwaltung:**
- Tabellen-Ansicht mit 7 Spalten
- Live-Suche (Titel, Themengebiet)
- Fach-Filter
- Statistik-Anzeige
- Editor (in Planung)

### 4. 🖼️ Grafiken ⏳
Grafik-Pool mit Upload, Thumbnails und Tags (in Planung).

### 5. ⚙️ Einstellungen ⏳
Schulen, Templates und System-Konfiguration (in Planung).

---

## 🎬 Workflow: Von der Idee zum PDF

```
1. Dashboard öffnen
   ↓
2. "Neue Klausur erstellen"
   ↓
3. Wizard durchlaufen (5 Steps)
   • Grunddaten eingeben (2 Min)
   • Aufgaben auswählen (2 Min)
   • Anordnen (1 Min)
   • Optionen wählen (30 Sek)
   ↓
4. "PDF generieren" klicken
   ↓
5. Warten (30-60 Sek)
   ↓
6. Fertiges PDF herunterladen! ✅

Gesamt: ~6 Minuten
```

---

## 🏗️ Technologie-Stack

| Komponente | Technologie |
|-----------|-------------|
| **GUI** | PyQt6 |
| **Datenbank** | SQLite |
| **PDF-Kompilierung** | LaTeX API (latex.ytotech.com) |
| **PDF-Verarbeitung** | PyPDF2 (Reordering) |
| **QR-Codes** | python-qrcode |
| **Styling** | QSS (Qt StyleSheets) |

---

## 📁 Projektstruktur

```
klausurengenerator_v2/
├── main.py                      # Entry Point
├── requirements.txt             # Dependencies
├── README.md                    # Dieses Dokument
│
├── gui/                         # GUI-Komponenten
│   ├── main_window.py           # Hauptfenster
│   ├── tabs/                    # Die 5 Tabs
│   │   ├── dashboard_tab.py         ✅ Live-Dashboard
│   │   ├── klausur_tab.py           ✅ Wizard-Controller
│   │   ├── step2_aufgabenauswahl.py ✅ Aufgaben wählen
│   │   ├── step3_anordnung.py       ✅ Drag & Drop
│   │   ├── step4_pdf_optionen.py    ✅ PDF-Optionen
│   │   ├── step5_generierung.py     ✅ PDF-Generierung
│   │   ├── aufgaben_tab.py          ✅ Aufgaben-Verwaltung
│   │   ├── grafiken_tab.py          ⏳ In Planung
│   │   └── einstellungen_tab.py     ⏳ In Planung
│   └── dialogs/                 # Dialoge
│
├── core/                        # Kernlogik
│   ├── database.py              ✅ Datenbank-Anbindung
│   ├── models.py                ✅ Datenmodelle
│   ├── latex_generator.py       ✅ LaTeX-Generierung
│   ├── pdf_compiler.py          ✅ PDF-Erstellung (API)
│   └── pdf_reorderer.py         ✅ Seiten-Umsortierung (4-1-2-3)
│
├── utils/                       # Hilfsfunktionen
│   └── latex_helper.py          ✅ LaTeX-Utilities
│
├── resources/                   # Ressourcen
│   └── stylesheets/
│       └── main.qss             ✅ Professional Styling
│
└── database/
    └── sus.db                   # SQLite-Datenbank (nicht im Repo)
```

---

## 📈 Entwicklungs-Status

**Aktuell: v2.0-beta** (85% fertig - produktiv nutzbar!)

### ✅ Fertiggestellt (100%)
- [x] Projektstruktur
- [x] Hauptfenster mit Tab-System
- [x] Datenbank-Anbindung (SQLite)
- [x] Alle Datenmodelle
- [x] **PDF-Engine komplett:**
  - [x] LaTeX-Generator
  - [x] PDF-Compiler (via API)
  - [x] PDF-Reorderer (Duplex-Druck)
- [x] **5-Step-Wizard:**
  - [x] Step 1: Setup
  - [x] Step 2: Aufgaben-Auswahl
  - [x] Step 3: Anordnung
  - [x] Step 4: PDF-Optionen
  - [x] Step 5: PDF-Generierung
- [x] Dashboard mit Live-Daten
- [x] Aufgaben-Tab (Basis)

### 🚧 In Arbeit (15%)
- [ ] Aufgaben-Editor (CRUD vollständig)
- [ ] Grafik-Pool
- [ ] Logo aus DB laden
- [ ] KasusID aus DB
- [ ] Lösungen generieren (KI)
- [ ] Templates erweitern
- [ ] Testing & Polishing

### 📋 Nice-to-Have
- [ ] Export nach Excel
- [ ] Statistiken & Reports
- [ ] Multi-User-Support
- [ ] Cloud-Sync

**Fortschritt:** 85% ████████████████████░

---

## 🎯 PDF-Features

### Was die PDF-Engine kann:

✅ **Muster ohne Lösung** - Lehrer-Exemplar  
✅ **Muster mit Lösung** - Mit Musterlösung  
✅ **Klassensatz ohne Lösung** - Personalisiert mit QR-Codes  
✅ **Klassensatz mit Lösung** - Für Nachbesprechung  
✅ **Duplex-Druck-Optimierung** - Automatische Seiten-Umsortierung (4-1-2-3)  
✅ **Running Headers** - Ab Seite 2  
✅ **Logo-Integration** - Schul-Logo im Header  
✅ **QR-Codes** - Für automatische Zuordnung  

### Performance:

| Aktion | Dauer |
|--------|-------|
| LaTeX generieren | ~0.5 Sek |
| PDF kompilieren | 30-60 Sek |
| PDF umsortieren | ~1 Sek |
| **Gesamt (Muster)** | **~35 Sek** |
| **Gesamt (30 Schüler)** | **~40 Sek** |

---

## 🧪 Testing

### Wie du es testen kannst:

```bash
# 1. Setup
git pull
pip install -r requirements.txt
python main.py

# 2. Dashboard checken
→ Siehst du echte Zahlen? ✅

# 3. Klausur erstellen
→ Wizard durchlaufen
→ PDF generieren
→ Download & Öffnen ✅

# 4. Aufgaben durchsuchen
→ Filter & Suche testen ✅
```

---

## 📝 Changelog

Siehe [MEILENSTEIN_2_Anwendung_85_Prozent.md](MEILENSTEIN_2_Anwendung_85_Prozent.md) für Details.

---

## 🤝 Beitragen

Dieses Projekt ist in aktiver Entwicklung für das **Gymnasium Dörpen**.

Feedback willkommen via:
- GitHub Issues
- Pull Requests
- Direkte Kommunikation

---

## 👨‍💻 Autor

**Hermann-Josef Hunfeld**  
Gymnasium Dörpen

- GitHub: [@hunfeld](https://github.com/hunfeld)
- E-Mail: hunfeld@gymnasium-doerpen.de

---

## 🙏 Danksagung

Entwickelt für die Erstellung professioneller Klassenarbeiten und Klausuren am Gymnasium Dörpen mit Unterstützung von Claude (Anthropic).

**Besonderer Dank an:**
- Die Fachschaften Mathematik, Physik und Informatik
- Alle Beta-Tester

---

**Status:** ✅ **85% fertig - Produktiv nutzbar!** | **Version:** 2.0-beta | **Letzte Aktualisierung:** 13. Dezember 2024

**Nächstes Ziel:** v1.0 Release (Q1 2025)
