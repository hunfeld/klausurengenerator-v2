# 📝 v1.0 User Guide

## 🎯 Willkommen zum Klausurengenerator v1.0!

Diese Anleitung zeigt dir, wie du professionelle Klausuren, Klassenarbeiten und Tests erstellst.

---

## 🚀 Schnellstart (5 Minuten)

### 1. **Anwendung starten**
```bash
python main.py
```

### 2. **Dashboard öffnet sich**
- Siehst du Statistiken? ✅
- Siehst du "Letzte Klausuren"? ✅

### 3. **Erste Klausur erstellen**
- Klick: **"Neue Klausur erstellen"**
- Folge dem 5-Step-Wizard
- Fertig! 🎉

---

## 📊 Die 5 Tabs

### 1. **Dashboard** 📊
**Was du siehst:**
- Live-Statistiken (Aufgaben, Klausuren, Grafiken, Schüler)
- Letzte 10 Klausuren
- Schnellaktionen

**Was du tun kannst:**
- "Neue Klausur erstellen" → Öffnet Wizard
- "Aufgaben durchsuchen" → Öffnet Aufgaben-Tab

---

### 2. **Klausur erstellen** 📝

**Der 5-Step-Wizard:**

#### **Step 1: Setup**
- Schule wählen (GYD, OBS, GYMPAP)
- Fach eingeben (z.B. Mathematik)
- Klasse (z.B. 8a)
- Datum
- Thema (z.B. "Lineare Funktionen")
- Typ (Klassenarbeit, Klausur, Test)
- Nummer (z.B. 1)

→ Klick "Weiter"

#### **Step 2: Aufgaben auswählen**
- **Suche** nach Titel/Thema
- **Filter** nach Fach
- **Klick** auf Aufgabe zum Auswählen
- **Gesamtpunkte** werden automatisch berechnet

→ Klick "Weiter"

#### **Step 3: Anordnung**
- **Drag & Drop** zum Umsortieren
- **Seitenumbrüche** festlegen (optional)
- **Vorschau** der Reihenfolge

→ Klick "Weiter"

#### **Step 4: PDF-Optionen**
Wähle, was du brauchst:

- ✅ **Muster ohne Lösung** (für Schüler-Ansicht)
- ✅ **Muster mit Lösung** (für Lehrer)
- ✅ **Klassensatz ohne Lösung** (personalisiert mit QR-Code)
- ✅ **Klassensatz mit Lösung** (für Nachbesprechung)

→ Klick "Weiter"

#### **Step 5: PDF generieren**
- **Zusammenfassung** prüfen
- **"PDF jetzt generieren"** klicken
- **Warte 30-60 Sekunden**
- **Download** erscheint automatisch!

✅ **Fertig!**

---

### 3. **Aufgaben** 📚

**Aufgaben-Verwaltung:**

#### **Neue Aufgabe erstellen**
1. Klick "➕ Neue Aufgabe"
2. Fülle Formular aus:
   - **Titel** (z.B. "Steigung berechnen")
   - **Fach** (Mathematik/Physik/Informatik)
   - **Themengebiet** (z.B. Lineare Funktionen)
   - **Schwierigkeit** (leicht/mittel/schwer)
   - **Punkte** (z.B. 10)
   - **AFB** (I, II, III)
   - **Jahrgangsstufe** (5-13)
   - **Schulform** (Gymnasium/Oberschule)
   - **Platzbedarf** (in cm für Lösungsraum)
   - **Schlagwörter** (Tags)
   - **LaTeX-Code** (Aufgabentext)
3. Klick "OK"

#### **Aufgabe bearbeiten**
- **Doppelklick** auf Aufgabe in Tabelle
- Oder: Auswählen + "✏️ Bearbeiten"
- Änderungen vornehmen
- Speichern

#### **Aufgabe löschen**
- Aufgabe auswählen
- Klick "🗑️ Löschen"
- Bestätigen (⚠️ nicht rückgängig!)

#### **Aufgaben filtern**
- **Suche:** Titel oder Themengebiet eingeben
- **Fach:** Dropdown-Auswahl
- **Schwierigkeit:** Dropdown-Auswahl
- **Statistik:** Zeigt gefilterte/gesamt Aufgaben

---

### 4. **Grafiken** 🖼️

**Grafik-Pool:**

#### **Grafik hochladen**
1. Klick "⬆️ Grafik hochladen"
2. Datei auswählen (PNG, JPG, SVG, PDF)
3. **Preview** erscheint automatisch
4. **Name** eingeben (oder Dateinamen übernehmen)
5. **Beschreibung** (optional)
6. **Tags** (optional, z.B. "Geometrie, Dreieck")
7. Klick "OK"

✅ **Grafik wird gespeichert!**

#### **Grafik löschen**
- **Klick** auf 🗑️ unter Grafik
- Bestätigen (⚠️ nicht rückgängig!)

#### **Grafiken verwenden**
- TODO: Integration in Aufgaben (v1.1)

---

### 5. **Einstellungen** ⚙️

**System-Konfiguration:**

- Schulen verwalten
- Templates bearbeiten
- Einstellungen anpassen

*Noch in Entwicklung für v1.1*

---

## 🎨 PDF-Features

### **Was die PDFs können:**

✅ **Professionelles Layout**
- Logo der Schule (aus DB)
- Running Header (Fach, Klasse)
- Metadata-Box (Datum, Zeit, Punkte)

✅ **Personalisierung**
- QR-Code pro Schüler
- Name auf Blatt
- Eindeutige KasusID

✅ **Duplex-Druck-Optimierung**
- Automatische Seiten-Umsortierung (4-1-2-3)
- Perfekt für Doppelseitigen Druck
- Einfach falten → Richtige Reihenfolge!

✅ **Varianten**
- Muster (mit/ohne Lösung)
- Klassensatz (personalisiert)
- Lösungsplatz automatisch

---

## 💡 Tipps & Tricks

### **Aufgaben effizient erstellen**
1. **Templates nutzen:** Ähnliche Aufgaben kopieren & anpassen
2. **Schlagwörter:** Erleichtern späteres Finden
3. **Platzbedarf:** Realistisch schätzen (5-10 cm)

### **LaTeX-Code**
```latex
Beispiel:
Gegeben ist die Funktion $f(x) = 2x + 3$.

\begin{enumerate}
  \item Bestimme die Steigung.
  \item Zeichne den Graphen.
\end{enumerate}
```

### **Workflow-Optimierung**
1. **Aufgaben vorbereiten** (in Ruhe)
2. **Klausur zusammenstellen** (5 Min)
3. **PDF generieren** (1 Min)
4. **Fertig!**

### **Schnelle Klausur**
- Aufgaben aus Pool wählen
- Keine neue Aufgaben erstellen
- Drag & Drop für Anordnung
- → In 5 Minuten fertig!

---

## ⚠️ Troubleshooting

### **PDF-Generierung dauert lange**
- **Normal:** 30-60 Sekunden
- **LaTeX-API:** Braucht Zeit für Kompilierung
- **Tipp:** Kaffee holen ☕

### **Logo wird nicht angezeigt**
- **Prüfen:** Logo in schulen-Tabelle vorhanden?
- **Format:** PNG empfohlen
- **Größe:** < 2 MB

### **Aufgabe erscheint nicht**
- **Filter prüfen:** Fach/Schwierigkeit richtig?
- **Suche leeren:** Evtl. Tippfehler?
- **Aktualisieren:** Klick 🔄

### **QR-Code fehlt**
- **Nur bei Klassensatz:** Muster hat keinen QR
- **Prüfen:** Schüler-Daten vorhanden?

---

## 📈 Best Practices

### **Aufgaben-Organisation**
- **Themengebiete** konsistent benennen
- **Schlagwörter** systematisch nutzen
- **Schwierigkeit** ehrlich einstufen

### **Klausur-Planung**
- **Zeit:** 1-2 Min pro Punkt
- **Schwierigkeit:** Mix aus leicht/mittel/schwer
- **Seitenumbrüche:** Bei thematischen Wechseln

### **Dateiverwaltung**
- **PDF speichern:** Unter sinnvollem Namen
- **Backup:** Regelmäßig DB sichern
- **Ordner:** Nach Fach/Klasse/Datum

---

## 🎯 Häufige Fragen (FAQ)

**Q: Kann ich Grafiken in Aufgaben einbetten?**
A: Ja! Upload in Grafik-Pool, dann in LaTeX referenzieren (v1.1)

**Q: Wie viele Aufgaben passen auf eine Seite?**
A: Abhängig von Platzbedarf. Grob: 2-3 Aufgaben

**Q: Kann ich die Reihenfolge nachträglich ändern?**
A: Ja, in Step 3 per Drag & Drop

**Q: Werden Lösungen automatisch generiert?**
A: Noch nicht - Feature für v1.1 geplant (KI)

**Q: Kann ich mehrere Klassen gleichzeitig?**
A: Einen Wizard-Durchlauf pro Klasse, aber schnell!

**Q: Wo ist meine sus.db?**
A: `database/sus.db` - **Regelmäßig sichern!**

---

## 🆘 Support

**Bei Problemen:**
1. Diese Anleitung nochmal lesen
2. GitHub Issues: https://github.com/hunfeld/klausurengenerator-v2/issues
3. Direkt melden: hunfeld@gymnasium-doerpen.de

---

## 🎉 Viel Erfolg!

**Mit dem Klausurengenerator v1.0:**
- Sparst du Zeit ⏰
- Erstellst professionelle Klausuren 📝
- Hast alles organisiert 📊

**Happy Teaching!** 👨‍🏫

---

**Version:** 1.0  
**Stand:** 14. Dezember 2024  
**Autor:** Hermann-Josef Hunfeld, Gymnasium Dörpen
