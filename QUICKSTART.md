# QUICKSTART - Klausurengenerator v2.0

## 🚀 Installation & Start

### 1. Dependencies installieren

```bash
cd C:\dev\_claude\klausurengenerator_v2
pip install -r requirements.txt
```

### 2. Anwendung starten

```bash
python main.py
```

---

## 📁 Projektstruktur

```
klausurengenerator_v2/
├── main.py                          # ⭐ START HIER!
├── gui/
│   ├── main_window.py               # Hauptfenster mit 5 Tabs
│   └── tabs/
│       ├── dashboard_tab.py         # Tab 1: Dashboard
│       ├── klausur_tab.py           # Tab 2: Klausur (5-Step-Wizard)
│       ├── aufgaben_tab.py          # Tab 3: Aufgaben
│       ├── grafiken_tab.py          # Tab 4: Grafiken
│       └── einstellungen_tab.py     # Tab 5: Einstellungen
├── core/                            # (noch leer)
├── utils/                           # (noch leer)
├── resources/
│   └── stylesheets/
│       └── main.qss                 # Design
├── database/                        # (Datenbank hier ablegen)
└── requirements.txt
```

---

## 🎯 TAB-STRUKTUR

### Tab 1: 📊 Dashboard
- Übersicht
- Schnellaktionen
- Letzte Klausuren

### Tab 2: 📝 Klausur erstellen (5-Step-Wizard)
**Step 1:** Setup (Schule, Fach, Klasse, Datum)  
**Step 2:** Aufgaben auswählen (mit Filter & Preview)  
**Step 3:** Anordnung (Drag & Drop)  
**Step 4:** PDF-Optionen (Muster/Klassensatz)  
**Step 5:** PDF generieren (Progress)

### Tab 3: 📚 Aufgaben
- Aufgaben-Pool durchsuchen
- Filter nach Fach, Schwierigkeit, etc.
- Neue Aufgabe erstellen

### Tab 4: 🖼️ Grafiken
- Grafik-Pool
- Upload / Zwischenablage
- Thumbnails

### Tab 5: ⚙️ Einstellungen
- Schulen verwalten
- Templates verwalten
- System-Einstellungen

---

## ✅ STATUS

### ✅ FERTIG (Grundgerüst)
- [x] Projektstruktur
- [x] main.py (Entry Point)
- [x] Hauptfenster mit 5 Tabs
- [x] Alle Tab-Dateien mit Basis-UI
- [x] Stylesheet (einheitliches Design)
- [x] Menüleiste
- [x] Statusleiste

### 🚧 TODO (Funktionalität)
- [ ] Datenbank-Anbindung
- [ ] Klausur-Wizard: Step 1 (Formular)
- [ ] Klausur-Wizard: Step 2 (Aufgaben-Auswahl mit DB)
- [ ] Klausur-Wizard: Step 3 (Drag & Drop)
- [ ] Klausur-Wizard: Step 4 (PDF-Optionen)
- [ ] Klausur-Wizard: Step 5 (LaTeX-Generierung)
- [ ] Aufgaben-Tab: DB-Integration
- [ ] Grafiken-Tab: Upload & Anzeige

---

## 🎨 DESIGN-PRINZIPIEN

- **Konsistenz:** Einheitliche Farben, Icons, Abstände
- **Bedienbarkeit:** Klare Beschriftungen, Tooltips
- **Workflow:** Von links nach rechts durch Tabs
- **Feedback:** Statusmeldungen, Progress-Bars

---

## 🔥 NÄCHSTE SCHRITTE

### Priority 1: Klausur-Wizard funktional machen
1. Step 1: Formular mit ComboBoxen, DateEdit, etc.
2. Step 2: Aufgaben aus Datenbank laden
3. Step 3: Drag & Drop implementieren
4. Step 4: PDF-Optionen-Checkboxen
5. Step 5: LaTeX-Code aus v1.8 integrieren

### Priority 2: Datenbank-Modul
- `core/database.py` erstellen
- Connection-Pool
- CRUD-Operationen für Aufgaben, Klausuren, etc.

### Priority 3: LaTeX-PDF-Pipeline
- `core/latex_generator.py` (aus v1.8)
- `core/pdf_compiler.py` (API-Call)
- `core/pdf_reorderer.py` (4-1-2-3)

---

## 📞 HILFE

Bei Problemen:
1. Prüfe ob alle Dependencies installiert sind
2. Prüfe Python-Version (3.11+)
3. Prüfe ob PyQt6 korrekt installiert ist

```bash
python --version
pip list | grep PyQt6
```

---

**Version:** 2.0.0  
**Datum:** 12.12.2024  
**Status:** ✅ Grundgerüst komplett, 🚧 Funktionalität in Arbeit
