# 📝 CHANGELOG v0.1 - INITIAL RELEASE

**Datum:** 13.12.2024  
**Status:** Alpha - Grundstruktur fertig, Wizard teilweise implementiert

---

## ✅ IMPLEMENTIERT

### Infrastruktur
- ✅ Projektstruktur erstellt
- ✅ `main.py` - Entry Point mit High-DPI Support
- ✅ `.gitignore` - Python/PyQt6 optimiert
- ✅ `requirements.txt` - Alle Dependencies
- ✅ `README.md` - GitHub-ready Dokumentation
- ✅ `GITHUB_SETUP.md` - Setup-Anleitung für hunfeld
- ✅ `START.bat` - Windows-Starter

### Core-Module
- ✅ `core/database.py` - Vollständige SQLite-Anbindung
  - Singleton-Pattern
  - Context Manager für Connections
  - CRUD für alle Tabellen (Schulen, Schüler, Aufgaben, etc.)
  - Statistiken
  - KasusID-Counter
  
- ✅ `core/models.py` - Alle Datenmodelle
  - `Schule`, `Schueler`, `Aufgabe`, `AufgabenTemplate`
  - `Klausur`, `KlausurAufgabe`, `Grafik`
  - Properties für berechnete Werte (Gesamtpunkte, Zeit, etc.)

### Utils
- ✅ `utils/latex_helper.py`
  - LaTeX-Escaping
  - cm ↔ pt Konvertierung
  - vspace → stretch Konvertierung
  - Datum-Formatierung
  - Dateinamen-Sanitizing
  - QR-Code-Daten-Generierung

### GUI - Hauptstruktur
- ✅ `gui/main_window.py` - Hauptfenster
  - 5-Tab-System (Dashboard, Klausur, Aufgaben, Grafiken, Einstellungen)
  - Menüleiste (Datei, Bearbeiten, Hilfe)
  - Statusleiste
  - Shortcuts (Ctrl+N, Ctrl+Q, etc.)
  - Zentrier-Funktion
  - Über-Dialog

### GUI - Tabs (Basis)
- ✅ `gui/tabs/dashboard_tab.py`
  - Willkommenstext
  - Schnellaktionen (Neue Klausur, Aufgaben durchsuchen)
  - Platzhalter für letzte Klausuren
  - Statistik-Widgets (Aufgaben, Klausuren, Grafiken)

- ✅ `gui/tabs/aufgaben_tab.py`
  - Platzhalter mit [+ Neue Aufgabe] Button

- ✅ `gui/tabs/grafiken_tab.py`
  - Platzhalter mit Upload-Button

- ✅ `gui/tabs/einstellungen_tab.py`
  - Datenbank-Pfad-Anzeige
  - Schulen-Verwaltung (Platzhalter)
  - Templates-Verwaltung (Platzhalter)
  - Versions-Info

### GUI - Klausur-Wizard (Hauptfeature!)

#### ✅ Wizard-Infrastruktur (`klausur_tab.py`)
- ✅ `KlausurTab` - Haupt-Wizard-Klasse
  - `klausur: Klausur` - Zentrales Datenmodell
  - `goto_step()` - Navigation zwischen Steps
  - `next_step()` - Mit Validierung
  - `prev_step()` - Zurück-Navigation
  - `reset_wizard()` - Neustart

- ✅ `WizardHeader` - Progress-Anzeige
  - 5 Steps mit Pfeilen
  - Farbcodierung (Aktiv: Blau, Erledigt: Grün, Offen: Grau)

- ✅ `NavigationButtons` - Steuerung
  - Zurück/Weiter/Abbrechen Buttons
  - Kontext-sensitive (Step 5: "Fertig")

#### ✅ Step 1: Setup (`Step1Setup`)
**Vollständig implementiert mit:**
- Schule-Auswahl (aus Datenbank geladen)
- Fach-Auswahl (Mathematik/Physik/Informatik mit Kürzeln)
- Jahrgangsstufe (5-13)
- Klasse (dynamisch aus DB geladen, Fallback-Generierung)
- Schuljahr (2024/2025, 2025/2026)
- Typ (Klassenarbeit/Klausur/Test)
- Nummer (1-10)
- Datum (DatePicker mit Kalender)
- Bearbeitungszeit (45/60/90 Min)
- Thema (Textfeld mit Validierung)

**Features:**
- Dynamisches Laden der Klassen basierend auf Schule + Schuljahr
- Validierung (Thema Pflichtfeld)
- Speicherung in `Klausur`-Objekt
- Reset-Funktion

#### ✅ Step 2: Aufgaben auswählen (`step2_aufgabenauswahl.py`)
**Vollständig implementiert als separates Modul:**

**Master-Detail-View:**
- **LINKS:** Aufgaben-Tabelle mit Checkboxen
  - Spalten: ✓, Titel, Punkte, Schwierigkeit, Thema
  - Checkbox-basierte Multi-Auswahl
  - Click → Preview rechts
  
- **RECHTS:** Preview-Panel
  - Titel, Themengebiet, Schwierigkeit, Punkte, AFB
  - Kompetenzen
  - LaTeX-Code (erste 500 Zeichen)

**Filter & Suche:**
- Volltext-Suche (Titel + Thema)
- Schwierigkeits-Filter (Alle/Leicht/Mittel/Schwer)
- Automatisches Laden basierend auf Fach + Jahrgangsstufe aus Step 1

**Statistik:**
- Live-Anzeige: Anzahl Aufgaben, Gesamtpunkte, geschätzte Zeit
- Vergleich mit verfügbarer Zeit

**Features:**
- `on_enter()` - Lädt Aufgaben beim Betreten
- `validate()` - Mind. 1 Aufgabe erforderlich
- `save_data()` - Speichert als `KlausurAufgabe`-Liste
- `reset()` - Löscht Auswahl

### Design
- ✅ `resources/stylesheets/main.qss` - Professionelles Stylesheet
  - Konsistente Farben (Primär: #0066cc, Success: #28a745)
  - Tab-Styling
  - Button-States (normal, hover, pressed, disabled)
  - GroupBox-Design
  - Input-Felder mit Focus-State
  - Tabellen & Listen
  - Scrollbars
  - Progress-Bar
  - Checkboxes & Radio-Buttons
  - Tooltips

---

## 🚧 IN ARBEIT

### Step 3: Anordnung
- [ ] Drag & Drop Liste
- [ ] Seite-Nummerierung
- [ ] Seitenumbrüche einfügen
- [ ] Deaktivieren von Aufgaben
- [ ] Live-Statistik

### Step 4: PDF-Optionen
- [ ] Checkboxen (Muster/Klassensatz, mit/ohne Lösung)
- [ ] Schüler aus DB laden
- [ ] Seitenzahl-Berechnung
- [ ] Vorschau

### Step 5: PDF-Generierung
- [ ] Progress-Bar
- [ ] LaTeX-Code-Generierung
- [ ] API-Call (latex.ytotech.com)
- [ ] PDF-Reordering (4-1-2-3)
- [ ] Download-Link

---

## 📋 TODO (Priorisiert)

### Hohe Priorität
1. **Step 3** - Drag & Drop Anordnung
2. **Step 4** - PDF-Optionen
3. **Step 5** - PDF-Generierung
4. **LaTeX-Generator** - aus klassensatz_generator_v1.8.py portieren
5. **PDF-Compiler** - API-Integration
6. **PDF-Reorderer** - 4-1-2-3 Umsortierung

### Mittlere Priorität
7. **Aufgaben-Tab** - Vollständige CRUD-Operationen
8. **Dashboard** - Echte Daten aus DB
9. **Grafik-Pool** - Upload & Verwaltung

### Niedrige Priorität
10. **Einstellungen** - Schulen/Templates verwalten
11. **Testing** - Unit-Tests
12. **Polishing** - Tooltips, Fehlerbehandlung, UX

---

## 🐛 BEKANNTE PROBLEME

- [ ] `database/sus.db` muss vom Nutzer bereitgestellt werden
- [ ] Noch keine Error-Handling für fehlende DB
- [ ] Steps 3-5 sind Platzhalter

---

## 💾 COMMITS EMPFOHLEN

Wenn hunfeld das Repo erstellt hat:

```bash
git add .
git commit -m "v0.1: Initial Release - Grundstruktur + Step 1-2 fertig

- Projektstruktur aufgebaut
- Datenbank-Anbindung vollständig
- Wizard Step 1 (Setup) implementiert
- Wizard Step 2 (Aufgaben-Auswahl) implementiert
- Professional Styling mit QSS
- Dokumentation (README, GITHUB_SETUP)
"
git tag v0.1-alpha
git push origin main --tags
```

---

**Weiter geht's mit Step 3!** 🚀

**Nächstes Changelog:** `CHANGELOG_v0.2.md` (nach Steps 3-5 fertig)
