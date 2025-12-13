# KLAUSURENGENERATOR V2.0 - IMPLEMENTIERUNGSPLAN

**Datum:** 12.12.2024  
**Ziel:** Einheitliche Desktop-Anwendung "aus einem Guss"  
**Technologie:** Python 3.11+, PyQt6, SQLite

---

## ÜBERSICHT

### Vision
Eine intuitive, professionelle Desktop-Anwendung für die Erstellung von Klassenarbeiten/Klausuren mit durchgängigem Workflow in einer einzigen Oberfläche.

### Hauptmerkmale
- ✅ **Eine Anwendung** - Alles in einem Fenster
- ✅ **Tab-basiert** - Klarer Workflow
- ✅ **Wizard-artig** - Schritt-für-Schritt durch Klausur-Erstellung
- ✅ **Konsistentes Design** - Einheitliches Look & Feel
- ✅ **Lokale Anwendung** - Keine Server nötig

---

## TAB-STRUKTUR (5 Tabs)

```
┌────────────────────────────────────────────────────────────┐
│ [📊 Dashboard] [📝 Klausur] [📚 Aufgaben] [🖼️ Grafiken] [⚙️]│
├────────────────────────────────────────────────────────────┤
│                                                            │
│              [Tab-spezifischer Inhalt]                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Tab 1: Dashboard (📊)
**Zweck:** Übersicht und Schnellzugriff

**Inhalt:**
- Willkommenstext
- Statistiken (Anzahl Aufgaben, Klausuren, etc.)
- Letzte Klausuren (Liste mit [Öffnen] [PDF])
- Schnellaktionen:
  - [+ Neue Klausur erstellen] → Wechselt zu Tab "Klausur"
  - [Aufgaben durchsuchen] → Wechselt zu Tab "Aufgaben"

**Status:** Prio 2 (nach Klausur-Tab)

---

### Tab 2: Klausur (📝)
**Zweck:** Kompletter Workflow für Klausur-Erstellung

**Struktur:** 5 Sub-Steps (Wizard)
```
Step 1: Setup → Step 2: Auswahl → Step 3: Anordnung → Step 4: Optionen → Step 5: PDF
```

#### Step 1: Setup (Grunddaten)
```
┌────────────────────────────────────────────────────────┐
│ Schritt 1/5: Grunddaten                                │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Schule: [Gymnasium Dörpen ▼]                          │
│ Fach: ○ Mathematik ○ Physik ○ Informatik             │
│ Jahrgangsstufe: [8]                                   │
│ Klasse: [8a ▼]                                        │
│                                                        │
│ Typ: ○ Klassenarbeit ○ Klausur ○ Test                │
│ Nummer: [2]                                           │
│ Datum: [24.03.2025] 📅                                │
│ Bearbeitungszeit: ○ 45 Min ○ 60 Min ○ 90 Min        │
│                                                        │
│ Thema: [Lineare Funktionen__________________]         │
│                                                        │
│ Kapitel (optional):                                   │
│ ☑ Kapitel 3: Lineare Funktionen                      │
│   ☑ 3.1 Proportionale Zuordnungen                    │
│   ☐ 3.2 Funktionsbegriff                             │
│                                                        │
│                    [Abbrechen] [Weiter →]             │
└────────────────────────────────────────────────────────┘
```

**Daten:** Werden in Klausur-Objekt gespeichert (noch nicht in DB)

#### Step 2: Aufgaben auswählen
```
┌────────────────────────────────────────────────────────┐
│ Schritt 2/5: Aufgaben auswählen                        │
├──────────────────────┬─────────────────────────────────┤
│ AUFGABENLISTE        │ PREVIEW                         │
│ (Gefiltert: 18)      │                                 │
├──────────────────────┼─────────────────────────────────┤
│ 🔍 [Suche____] 🔍    │ Aufgabe #142                    │
│                      │                                 │
│ Filter:              │ [LaTeX-Preview]                 │
│ ☑ Kapitel 3.1 (8)    │                                 │
│ ☐ Kapitel 3.2 (6)    │ Metadaten:                     │
│                      │ • Punkte: 4                    │
│ ☐ #142              │ • Zeit: ~6 Min                 │
│   Funktionsterm      │ • Schwierigkeit: Mittel        │
│   4P | ~6min        │                                 │
│                      │                                 │
│ ☑ #89               │ [Zur Auswahl hinzufügen]       │
│   Proportional       │                                 │
│   6P | ~8min        │                                 │
│                      │                                 │
│ ☐ #56               │                                 │
│   Wertetabelle       │                                 │
│   3P | ~5min        │                                 │
├──────────────────────┴─────────────────────────────────┤
│ VORAUSWAHL (2 Aufgaben):                              │
│ • #89 Proportional (6P, 8min) [✕]                    │
│ Σ: 2 Aufgaben | 6 Punkte | 8 Min (37 Min verfügbar) │
│                                                        │
│        [← Zurück] [+ Neue Aufgabe] [Weiter →]        │
└────────────────────────────────────────────────────────┘
```

**Features:**
- Checkbox-basierte Auswahl
- Klick auf Zeile → Preview rechts
- Filter nach Kapitel, Schwierigkeit, AFB
- Volltext-Suche
- Vorauswahl-Bereich unten
- Statistik (Zeit, Punkte)

#### Step 3: Anordnung
```
┌────────────────────────────────────────────────────────┐
│ Schritt 3/5: Aufgaben anordnen                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│ ════════════ SEITE 1 ════════════                      │
│                                                        │
│ ☑ 1. ⋮⋮ Funktionsterm          [✏️] [👁️] [🗑️]         │
│       ⭐⭐ leicht | 3P | ~5min                        │
│                                                        │
│ ☑ 2. ⋮⋮ Proportionale Zuord.   [✏️] [👁️] [🗑️]         │
│       ⭐⭐⭐ mittel | 4P | ~8min                       │
│                                                        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ [📄 Seitenumbruch]                                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                        │
│ ════════════ SEITE 2 ════════════                      │
│                                                        │
│ ☑ 3. ⋮⋮ Funktionsgraph         [✏️] [👁️] [🗑️]         │
│       ⭐⭐⭐⭐ schwer | 6P | ~12min                    │
│                                                        │
├────────────────────────────────────────────────────────┤
│ Statistik:                                            │
│ • Aufgaben: 3 (0 inaktiv)                            │
│ • Punkte: 13                                          │
│ • Zeit: ~25 Min (20 Min verfügbar)                   │
│ • Seiten: 2                                           │
│                                                        │
│              [← Zurück] [Weiter →]                     │
└────────────────────────────────────────────────────────┘
```

**Features:**
- Drag & Drop (⋮⋮) zum Umsortieren
- Checkbox zum Deaktivieren
- Seitenumbrüche einfügen/entfernen
- Live-Statistik

#### Step 4: PDF-Optionen
```
┌────────────────────────────────────────────────────────┐
│ Schritt 4/5: PDF-Optionen                              │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Was soll generiert werden?                            │
│                                                        │
│ ☑ Muster ohne Lösung (1 Exemplar)                    │
│ ☑ Muster mit Lösung (1 Exemplar)                     │
│ ☑ Klassensatz ohne Lösung (24 Schüler)               │
│ ☐ Klassensatz mit Lösung (24 Schüler)                │
│                                                        │
│ Klasse: [8a ▼] → 24 Schüler geladen                  │
│ Schuljahr: [2024/2025 ▼]                              │
│                                                        │
│ ℹ️ Seiten werden automatisch für Duplex umsortiert    │
│    (4-1-2-3), da Klausur 4 Seiten hat.               │
│                                                        │
│ Vorschau:                                             │
│ • Seiten 1-4:   Muster ohne Lösung                   │
│ • Seiten 5-8:   Muster mit Lösung                    │
│ • Seiten 9-104: Klassensatz (24 × 4 Seiten)          │
│                                                        │
│ Gesamt: 104 Seiten | ~2.8 MB (geschätzt)             │
│                                                        │
│              [← Zurück] [PDF generieren →]             │
└────────────────────────────────────────────────────────┘
```

#### Step 5: PDF-Generierung (Progress)
```
┌────────────────────────────────────────────────────────┐
│ Schritt 5/5: PDF wird generiert...                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│ ✓ Klausur-Daten geladen                              │
│ ✓ 24 Schüler geladen                                 │
│ ✓ Aufgaben geladen                                    │
│ ✓ Grafiken geladen                                    │
│ ▶ LaTeX-Code wird generiert...                       │
│   ████████████░░░░░░░░ 60%                           │
│                                                        │
│ Teil 2 von 3: Muster mit Lösung                       │
│                                                        │
│              [Abbrechen]                               │
└────────────────────────────────────────────────────────┘
```

**Nach Erfolg:**
```
┌────────────────────────────────────────────────────────┐
│ ✅ PDF erfolgreich generiert!                          │
├────────────────────────────────────────────────────────┤
│                                                        │
│ 📄 Ma-2_8a_20250324_Komplett.pdf                      │
│                                                        │
│ Inhalt:                                               │
│ • Seiten 1-4:   Muster ohne Lösung                   │
│ • Seiten 5-8:   Muster mit Lösung                    │
│ • Seiten 9-104: Klassensatz (24 Schüler)             │
│                                                        │
│ Größe: 2.8 MB | 104 Seiten                            │
│                                                        │
│ [💾 Speichern unter...] [👁️ PDF öffnen] [Fertig]      │
│                                                        │
│ ── Klausur finalisieren? ──────────────────────────    │
│ ⚠️ Möchtest du die Klausur jetzt speichern?           │
│ • In Datenbank archivieren                            │
│ • Später wieder öffnen und bearbeiten                │
│                                                        │
│         [Nicht speichern] [In DB speichern]           │
└────────────────────────────────────────────────────────┘
```

**Status:** Prio 1 (HÖCHSTE PRIORITÄT)

---

### Tab 3: Aufgaben (📚)
**Zweck:** Aufgaben-Pool verwalten

**Inhalt:**
```
┌────────────────────────────────────────────────────────┐
│ Aufgaben-Verwaltung                                    │
├──────────────────────┬─────────────────────────────────┤
│ LISTE               │ DETAILS                         │
├──────────────────────┼─────────────────────────────────┤
│ 🔍 [Suche___] 🔍     │ Aufgabe #142                    │
│                      │                                 │
│ Filter:              │ [LaTeX-Preview]                 │
│ ☐ Mathematik (85)    │                                 │
│ ☐ Physik (32)        │ Titel: Funktionsterm           │
│ ☐ Informatik (25)    │ Fach: Mathematik               │
│                      │ Kapitel: 3.1                   │
│ Schwierigkeit:       │ Schwierigkeit: Mittel          │
│ ☐ Leicht (45)        │ Punkte: 4                      │
│ ☐ Mittel (68)        │ Zeit: ~6 Min                   │
│ ☐ Schwer (29)        │                                 │
│                      │ [✏️ Bearbeiten] [🗑️ Löschen]    │
│ #142 Funktionsterm   │ [📋 Duplizieren]                │
│ #89 Proportional     │                                 │
│ #56 Wertetabelle     │                                 │
│ ...                  │                                 │
├──────────────────────┴─────────────────────────────────┤
│ [+ Neue Aufgabe erstellen]                            │
└────────────────────────────────────────────────────────┘
```

**Features:**
- Liste aller Aufgaben
- Filter und Suche
- Preview beim Klick
- Bearbeiten/Löschen/Duplizieren
- [+ Neue Aufgabe] → Template-Auswahl-Dialog

**Status:** Prio 3

---

### Tab 4: Grafiken (🖼️)
**Zweck:** Grafik-Pool verwalten

**Inhalt:**
```
┌────────────────────────────────────────────────────────┐
│ Grafik-Pool                                            │
├────────────────────────────────────────────────────────┤
│ 🔍 [Suche____________] 🔍                              │
│                                                        │
│ Filter:                                               │
│ ☐ Koordinatensystem (12)  ☐ Geometrie (23)           │
│ ☐ Funktionen (15)         ☐ Diagramme (8)            │
│                                                        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│ │[Thumb]   │ │[Thumb]   │ │[Thumb]   │               │
│ │Koordin.  │ │Dreieck   │ │Parabel   │               │
│ │512×512   │ │400×300   │ │600×450   │               │
│ │12× verw. │ │5× verw.  │ │8× verw.  │               │
│ └──────────┘ └──────────┘ └──────────┘               │
│                                                        │
│ [📁 Hochladen] [📋 Aus Zwischenablage] [📐 GeoGebra] │
└────────────────────────────────────────────────────────┘
```

**Features:**
- Grid-Ansicht mit Thumbnails
- Upload von Dateien
- Zwischenablage (Strg+V)
- GeoGebra-Import (optional)
- Tags/Filter

**Status:** Prio 4

---

### Tab 5: Einstellungen (⚙️)
**Zweck:** System-Konfiguration

**Inhalt:**
- Schulen verwalten (Logo hochladen)
- Templates verwalten
- Standard-Einstellungen
- Datenbank-Pfad
- Über / Version

**Status:** Prio 5

---

## TECHNISCHE ARCHITEKTUR

### Projektstruktur
```
klausurengenerator_v2/
├── main.py                      # Entry Point
├── gui/
│   ├── __init__.py
│   ├── main_window.py           # Hauptfenster mit Tabs
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── dashboard_tab.py
│   │   ├── klausur_tab.py       # 5-Step-Wizard
│   │   ├── aufgaben_tab.py
│   │   ├── grafiken_tab.py
│   │   └── einstellungen_tab.py
│   └── dialogs/
│       ├── __init__.py
│       ├── aufgabe_erstellen_dialog.py
│       ├── latex_preview_dialog.py
│       └── progress_dialog.py
├── core/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── latex_generator.py
│   ├── pdf_compiler.py
│   └── pdf_reorderer.py
├── utils/
│   ├── __init__.py
│   └── latex_escaper.py
├── resources/
│   └── stylesheets/
│       └── main.qss
├── database/
│   └── sus.db
└── requirements.txt
```

### Technologie-Stack
- **Python:** 3.11+
- **GUI:** PyQt6
- **DB:** SQLite
- **PDF:** LaTeX-API + PyPDF2

---

## IMPLEMENTIERUNGS-REIHENFOLGE

### Phase 1: Grundgerüst (Woche 1)
- [x] Projektstruktur anlegen
- [ ] main.py (Entry Point)
- [ ] main_window.py (Hauptfenster mit 5 Tabs)
- [ ] Stylesheet (einheitliches Design)
- [ ] Datenbank-Anbindung

### Phase 2: Klausur-Tab (Woche 2-3)
- [ ] klausur_tab.py mit 5 Steps
- [ ] Step 1: Setup-Formular
- [ ] Step 2: Aufgaben-Auswahl
- [ ] Step 3: Anordnung (Drag & Drop)
- [ ] Step 4: PDF-Optionen
- [ ] Step 5: Generierung (Progress)

### Phase 3: PDF-Generierung (Woche 4)
- [ ] latex_generator.py (aus v1.8 übernehmen)
- [ ] pdf_compiler.py (LaTeX-API)
- [ ] pdf_reorderer.py (4-1-2-3)
- [ ] Integration in Step 5

### Phase 4: Aufgaben-Tab (Woche 5)
- [ ] aufgaben_tab.py
- [ ] Liste mit Filter/Suche
- [ ] Detail-Ansicht
- [ ] Template-basierte Erstellung

### Phase 5: Grafik-Tab (Woche 6)
- [ ] grafiken_tab.py
- [ ] Upload-Funktionen
- [ ] Zwischenablage
- [ ] Pool-Verwaltung

### Phase 6: Dashboard & Einstellungen (Woche 7)
- [ ] dashboard_tab.py
- [ ] einstellungen_tab.py
- [ ] Polishing & Bugfixes

---

## DESIGN-PRINZIPIEN

### Konsistenz
- Einheitliche Farben
- Einheitliche Icons
- Einheitliche Button-Größen
- Einheitliche Abstände

### Bedienbarkeit
- Klare Beschriftungen
- Tooltips überall
- Fehlermeldungen verständlich
- Undo-Funktionen wo sinnvoll

### Performance
- Lazy Loading von Aufgaben
- Caching von Previews
- Asynchrone PDF-Generierung

---

## NÄCHSTER SCHRITT

**Jetzt:** Hauptfenster mit 5 Tabs erstellen
- main.py
- main_window.py
- Basis-Struktur für alle Tabs
- Stylesheet

**Status:** ✅ Bereit für Implementierung
