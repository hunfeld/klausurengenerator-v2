# 🚀 GITHUB SETUP - KLAUSURENGENERATOR V2.0

**Erstellt für:** hunfeld  
**Datum:** 13.12.2024

---

## ⚡ SCHNELL-SETUP (5 Minuten)

### Schritt 1: Repository erstellen

Öffne PowerShell/Terminal in: `C:\dev\_claude\klausurengenerator_v2`

```bash
cd C:\dev\_claude\klausurengenerator_v2
git init
git add .
git commit -m "Initial commit: Klausurengenerator v2.0 - Desktop App mit PyQt6"
```

### Schritt 2: Auf GitHub pushen

**Option A - Mit GitHub CLI (empfohlen):**
```bash
gh repo create klausurengenerator-v2 --public --source=. --push --description "Desktop-Anwendung für Klausuren-Erstellung mit LaTeX und SQLite"
```

**Option B - Manuell:**
1. Gehe zu: https://github.com/new
2. Repository Name: `klausurengenerator-v2`
3. Description: `Desktop-Anwendung für Klausuren-Erstellung mit PyQt6, LaTeX und SQLite`
4. Public ✓
5. Create repository

Dann:
```bash
git remote add origin https://github.com/hunfeld/klausurengenerator-v2.git
git branch -M main
git push -u origin main
```

### Schritt 3: Fertig! ✅

Repository ist online: `https://github.com/hunfeld/klausurengenerator-v2`

---

## 📋 WAS IST DRIN?

### ✅ Bereits implementiert:

**Grundstruktur:**
- ✅ PyQt6 Hauptfenster mit 5 Tabs
- ✅ Professionelles Stylesheet (main.qss)
- ✅ Vollständige Datenbank-Anbindung (SQLite)
- ✅ Alle Datenmodelle (Klausur, Aufgabe, Schüler, etc.)

**Klausur-Wizard:**
- ✅ Step 1: Setup-Formular (Schule, Fach, Klasse, Datum, Thema)
- ✅ Step 2: Aufgaben-Auswahl (Master-Detail-View mit Filter)
- 🚧 Step 3: Anordnung (in Arbeit)
- 🚧 Step 4: PDF-Optionen (in Arbeit)
- 🚧 Step 5: PDF-Generierung (in Arbeit)

**Sonstiges:**
- ✅ Dashboard-Tab (Basis)
- ✅ Aufgaben-Tab (Basis)
- ✅ Grafiken-Tab (Basis)
- ✅ Einstellungen-Tab (Basis)

---

## 🔄 WORKFLOW AB JETZT

### Claude entwickelt weiter:
1. Nach jedem Feature: `CHANGELOG_vX.X.md` mit Details
2. Du kannst jederzeit committen:
   ```bash
   git add .
   git commit -m "Feature: [Was Claude gemacht hat]"
   git push
   ```

### Regelmäßige Updates:
- Nach jedem Step: Commit-Empfehlung in CHANGELOG
- Nach Phase: Testing-Anleitung
- Am Ende: Final Release

---

## 📦 INSTALLATION FÜR ANDERE NUTZER

Später können andere das Projekt so nutzen:

```bash
# Klonen
git clone https://github.com/hunfeld/klausurengenerator-v2.git
cd klausurengenerator-v2

# Dependencies installieren
pip install -r requirements.txt

# Eigene Datenbank kopieren
copy "C:\path\to\sus.db" database\sus.db

# Starten
python main.py
```

---

## 🎯 NÄCHSTE SCHRITTE

1. ✅ Du: Repository erstellen (siehe oben)
2. ✅ Claude: Entwickelt weiter ohne dich zu stören
3. ✅ Du: Checkst später die CHANGELOG Dateien
4. ✅ Du: Commitest wenn du willst

---

## 📞 FRAGEN?

Einfach in GitHub Issues posten oder Claude fragen!

**Let's go!** 🚀
