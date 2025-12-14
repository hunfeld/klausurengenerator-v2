"""
Klausur-Tab mit 5-Step-Wizard
==============================

Step 1: Setup (Grunddaten)
Step 2: Aufgaben auswählen
Step 3: Anordnung
Step 4: PDF-Optionen
Step 5: Generierung

v1.0.11 - Bugfix: blockSignals() während Initialisierung
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, 
    QFrame, QGroupBox, QComboBox, QRadioButton, QButtonGroup, QSpinBox,
    QLineEdit, QDateEdit, QMessageBox, QFormLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

from core.database import get_database
from core.models import Klausur, Schule


class KlausurTab(QWidget):
    """Klausur-Erstellung mit 5-Step-Wizard"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.current_step = 0
        
        # Klausur-Objekt
        self.klausur = Klausur()
        
        # Edit-Modus Flag
        self.edit_mode = False
        self.klausur_id = None
        
        # Datenbank
        self.db = get_database()
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Progress-Header
        self.header = WizardHeader()
        layout.addWidget(self.header)
        
        # Content-Bereich (Stacke die 5 Steps)
        self.content_stack = QStackedWidget()
        
        # Die 5 Steps
        self.step1 = Step1Setup(self)
        self.step2 = Step2AufgabenAuswahl(self)
        self.step3 = Step3Anordnung(self)
        self.step4 = Step4PDFOptionen(self)
        self.step5 = Step5Generierung(self)
        
        self.content_stack.addWidget(self.step1)
        self.content_stack.addWidget(self.step2)
        self.content_stack.addWidget(self.step3)
        self.content_stack.addWidget(self.step4)
        self.content_stack.addWidget(self.step5)
        
        layout.addWidget(self.content_stack, 1)
        
        # Navigation-Buttons
        self.nav_widget = NavigationButtons(self)
        layout.addWidget(self.nav_widget)
        
        # Starte bei Step 1
        self.goto_step(0)
        
    def goto_step(self, step_index):
        """Zu einem bestimmten Step wechseln"""
        
        if 0 <= step_index < 5:
            self.current_step = step_index
            self.content_stack.setCurrentIndex(step_index)
            self.header.set_current_step(step_index)
            self.nav_widget.update_buttons(step_index)
            
            # Step-spezifische Aktionen
            current_widget = self.content_stack.currentWidget()
            if hasattr(current_widget, 'on_enter'):
                current_widget.on_enter()
            
    def next_step(self):
        """Zum nächsten Step"""
        
        # Validierung des aktuellen Steps
        current_widget = self.content_stack.currentWidget()
        if hasattr(current_widget, 'validate'):
            if not current_widget.validate():
                return  # Validierung fehlgeschlagen
                
        # Daten speichern
        if hasattr(current_widget, 'save_data'):
            current_widget.save_data()
            
        # Weiter zum nächsten Step
        if self.current_step < 4:
            self.goto_step(self.current_step + 1)
        else:
            # Step 5 fertig -> Klausur in DB speichern
            self.save_klausur_to_db()
            
            # Zurück zu Dashboard
            self.reset_wizard()
            if self.main_window:
                self.main_window.tabs.setCurrentIndex(0)
            
    def prev_step(self):
        """Zum vorherigen Step"""
        if self.current_step > 0:
            self.goto_step(self.current_step - 1)
            
    def reset_wizard(self):
        """Wizard zurücksetzen"""
        self.klausur = Klausur()
        self.edit_mode = False
        self.klausur_id = None
        self.goto_step(0)
        
        # Alle Steps zurücksetzen
        self.step1.reset()
        self.step2.reset()
        self.step3.reset()
        self.step4.reset()
        self.step5.reset()
    
    def load_klausur_for_edit(self, klausur_data):
        """
        Klausur für Bearbeitung laden
        
        NEU! Für Edit-Modus
        
        Args:
            klausur_data: Dictionary mit Klausur-Daten aus DB
        """
        # Edit-Modus aktivieren
        self.edit_mode = True
        self.klausur_id = klausur_data.get('id')
        
        # Daten ins Klausur-Objekt laden
        klausur = self.klausur
        klausur.schule_kuerzel = klausur_data.get('schule', 'gyd')
        klausur.fach = klausur_data.get('fach', 'Mathematik')
        klausur.klasse = klausur_data.get('klasse', '')
        klausur.jahrgangsstufe = klausur_data.get('jahrgangsstufe', 8)
        klausur.typ = klausur_data.get('typ', 'Klassenarbeit')
        klausur.datum = klausur_data.get('datum', '')
        klausur.zeit_minuten = klausur_data.get('zeit_minuten', 45)
        klausur.thema = klausur_data.get('titel', '')  # titel -> thema
        
        # Step 1 UI mit Daten füllen
        self.step1.load_from_klausur(klausur_data)
        
        # Gehe zu Step 1
        self.goto_step(0)
        
        # Info anzeigen
        QMessageBox.information(
            self,
            "Klausur bearbeiten",
            f"Klausur '{klausur.thema}' wird geladen.\n\n"
            f"Sie können jetzt die Daten ändern und am Ende speichern."
        )
    
    def save_klausur_to_db(self):
        """
        Klausur in DB speichern
        
        NEU! Unterscheidet zwischen CREATE und UPDATE
        """
        try:
            klausur = self.klausur
            
            # Daten vorbereiten
            data = {
                'titel': klausur.thema,
                'datum': klausur.datum,
                'fach': klausur.fach,
                'jahrgangsstufe': klausur.jahrgangsstufe,
                'typ': klausur.typ,
                'schule': klausur.schule_kuerzel,
                'klasse': klausur.klasse,
                'zeit_minuten': klausur.zeit_minuten,
                'aufgaben_json': '[]',  # TODO: Aufgaben aus Steps 2-3
                'seitenumbrueche_json': '[]'  # TODO: Aus Step 3
            }
            
            if self.edit_mode and self.klausur_id:
                # UPDATE
                data['id'] = self.klausur_id
                self.db.update_klausur(data)
                
                QMessageBox.information(
                    self,
                    "Erfolg",
                    f"Klausur '{klausur.thema}' wurde aktualisiert!"
                )
            else:
                # CREATE
                new_id = self.db.create_klausur(data)
                
                QMessageBox.information(
                    self,
                    "Erfolg",
                    f"Klausur '{klausur.thema}' wurde erstellt!\n(ID: {new_id})"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Speichern:\n{e}"
            )


class WizardHeader(QFrame):
    """Progress-Header für die 5 Steps"""
    
    def __init__(self):
        super().__init__()
        
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMaximumHeight(80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        self.step_labels = []
        
        steps = [
            "1. Setup",
            "2. Aufgaben",
            "3. Anordnung",
            "4. Optionen",
            "5. PDF"
        ]
        
        for i, step_text in enumerate(steps):
            step_label = QLabel(step_text)
            step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.step_labels.append(step_label)
            layout.addWidget(step_label)
            
            if i < len(steps) - 1:
                arrow = QLabel("→")
                layout.addWidget(arrow)
                
    def set_current_step(self, index):
        """Aktiven Step hervorheben"""
        
        for i, label in enumerate(self.step_labels):
            if i == index:
                label.setStyleSheet("font-weight: bold; color: #0066cc; font-size: 14pt;")
            elif i < index:
                label.setStyleSheet("color: #28a745; font-size: 12pt;")  # Grün = erledigt
            else:
                label.setStyleSheet("color: #999; font-size: 12pt;")  # Grau = offen


class NavigationButtons(QWidget):
    """Navigation-Buttons unten"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        self.back_btn = QPushButton("← Zurück")
        self.back_btn.clicked.connect(parent_tab.prev_step)
        
        self.next_btn = QPushButton("Weiter →")
        self.next_btn.clicked.connect(parent_tab.next_step)
        
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(parent_tab.reset_wizard)
        
        layout.addWidget(self.cancel_btn)
        layout.addStretch()
        layout.addWidget(self.back_btn)
        layout.addWidget(self.next_btn)
        
    def update_buttons(self, step_index):
        """Buttons je nach Step anpassen"""
        
        # Zurück-Button
        self.back_btn.setEnabled(step_index > 0)
        
        # Weiter-Button
        if step_index == 4:
            if self.parent_tab.edit_mode:
                self.next_btn.setText("Speichern")
            else:
                self.next_btn.setText("Fertig")
        else:
            self.next_btn.setText("Weiter →")


# ============================================================
# STEP 1: SETUP (GRUNDDATEN)
# ============================================================

class Step1Setup(QWidget):
    """Step 1: Grunddaten eingeben"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.db = get_database()
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        # ScrollArea für längere Formulare
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)
        
        # Titel
        title = QLabel("Schritt 1/5: Grunddaten")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Schule
        schule_group = QGroupBox("Schule")
        schule_layout = QFormLayout(schule_group)
        
        self.schule_combo = QComboBox()
        self.schule_combo.currentIndexChanged.connect(self.on_schule_changed)
        schule_layout.addRow("Schule:", self.schule_combo)
        
        layout.addWidget(schule_group)
        
        # Fach
        fach_group = QGroupBox("Fach")
        fach_layout = QVBoxLayout(fach_group)
        
        self.fach_buttons = QButtonGroup(self)
        faecher = [
            ("Mathematik", "Ma"),
            ("Physik", "Ph"),
            ("Informatik", "If")
        ]
        
        fach_radios_layout = QHBoxLayout()
        for i, (fach, kuerzel) in enumerate(faecher):
            radio = QRadioButton(fach)
            radio.setProperty("kuerzel", kuerzel)
            self.fach_buttons.addButton(radio, i)
            fach_radios_layout.addWidget(radio)
            
            if i == 0:  # Mathematik als Default
                radio.setChecked(True)
        
        fach_layout.addLayout(fach_radios_layout)
        layout.addWidget(fach_group)
        
        # Klasse
        klasse_group = QGroupBox("Klasse")
        klasse_layout = QFormLayout(klasse_group)
        
        # Jahrgangsstufe
        self.jahrgangsstufe_spin = QSpinBox()
        self.jahrgangsstufe_spin.setRange(5, 13)
        self.jahrgangsstufe_spin.setValue(8)
        self.jahrgangsstufe_spin.valueChanged.connect(self.on_jahrgangsstufe_changed)
        klasse_layout.addRow("Jahrgangsstufe:", self.jahrgangsstufe_spin)
        
        # Klasse (editable ComboBox!)
        self.klasse_combo = QComboBox()
        self.klasse_combo.setEditable(True)  # WICHTIG: User kann auch eigene eingeben!
        klasse_layout.addRow("Klasse:", self.klasse_combo)
        
        # Schuljahr
        self.schuljahr_combo = QComboBox()
        self.schuljahr_combo.currentIndexChanged.connect(self.on_schuljahr_changed)
        klasse_layout.addRow("Schuljahr:", self.schuljahr_combo)
        
        layout.addWidget(klasse_group)
        
        # Typ und Nummer
        typ_group = QGroupBox("Typ und Nummer")
        typ_layout = QFormLayout(typ_group)
        
        # Typ
        typ_hlayout = QHBoxLayout()
        self.typ_buttons = QButtonGroup(self)
        typen = ["Klassenarbeit", "Klausur", "Test"]
        
        for i, typ in enumerate(typen):
            radio = QRadioButton(typ)
            self.typ_buttons.addButton(radio, i)
            typ_hlayout.addWidget(radio)
            
            if i == 0:  # Klassenarbeit als Default
                radio.setChecked(True)
        
        typ_layout.addRow("Typ:", typ_hlayout)
        
        # Nummer
        self.nummer_spin = QSpinBox()
        self.nummer_spin.setRange(1, 10)
        self.nummer_spin.setValue(1)
        typ_layout.addRow("Nummer:", self.nummer_spin)
        
        layout.addWidget(typ_group)
        
        # Datum und Zeit
        termin_group = QGroupBox("Termin")
        termin_layout = QFormLayout(termin_group)
        
        # Datum
        self.datum_edit = QDateEdit()
        self.datum_edit.setCalendarPopup(True)
        self.datum_edit.setDate(QDate.currentDate())
        self.datum_edit.setDisplayFormat("dd.MM.yyyy")
        # Verbinde Signal für automatische Schuljahr-Berechnung
        self.datum_edit.dateChanged.connect(self.on_datum_changed)
        termin_layout.addRow("Datum:", self.datum_edit)
        
        # Bearbeitungszeit
        zeit_hlayout = QHBoxLayout()
        self.zeit_buttons = QButtonGroup(self)
        zeiten = [45, 60, 90]
        
        for i, minuten in enumerate(zeiten):
            radio = QRadioButton(f"{minuten} Min")
            radio.setProperty("minuten", minuten)
            self.zeit_buttons.addButton(radio, i)
            zeit_hlayout.addWidget(radio)
            
            if i == 0:  # 45 Min als Default
                radio.setChecked(True)
        
        termin_layout.addRow("Bearbeitungszeit:", zeit_hlayout)
        
        layout.addWidget(termin_group)
        
        # Thema
        thema_group = QGroupBox("Thema")
        thema_layout = QFormLayout(thema_group)
        
        self.thema_edit = QLineEdit()
        self.thema_edit.setPlaceholderText("z.B. Lineare Funktionen")
        thema_layout.addRow("Thema:", self.thema_edit)
        
        layout.addWidget(thema_group)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # JETZT ERST am Ende: Initial-Daten laden
        # WICHTIG: Signals blocken während Initialisierung!
        self.schule_combo.blockSignals(True)
        self.schuljahr_combo.blockSignals(True)
        self.jahrgangsstufe_spin.blockSignals(True)
        
        self.load_schulen()
        self.populate_schuljahre()
        self.update_schuljahr_from_datum()
        self.load_klassen()
        
        # Signals wieder freigeben
        self.schule_combo.blockSignals(False)
        self.schuljahr_combo.blockSignals(False)
        self.jahrgangsstufe_spin.blockSignals(False)
        
    def populate_schuljahre(self):
        """
        Schuljahre für Dropdown generieren
        
        FORMAT: "25/26" (nicht "2025/2026"!)
        """
        current_year = QDate.currentDate().year()
        
        self.schuljahr_combo.clear()
        
        # Generiere 3 Jahre zurück und 2 Jahre voraus
        for offset in range(-3, 3):
            year = current_year + offset
            # Format: "25/26" statt "2025/2026"
            schuljahr = f"{year % 100:02d}/{(year + 1) % 100:02d}"
            self.schuljahr_combo.addItem(schuljahr)
    
    def on_datum_changed(self):
        """
        Wird aufgerufen wenn Datum geändert wird
        
        NEU: Berechnet Schuljahr automatisch
        """
        self.update_schuljahr_from_datum()
    
    def on_schule_changed(self):
        """Wird aufgerufen wenn Schule geändert wird"""
        self.load_klassen()
    
    def on_schuljahr_changed(self):
        """Wird aufgerufen wenn Schuljahr geändert wird"""
        self.load_klassen()
    
    def update_schuljahr_from_datum(self):
        """
        Berechne Schuljahr aus Datum
        
        Logik: 
        - August bis Dezember → Jahr/Jahr+1
        - Januar bis Juli → Jahr-1/Jahr
        
        FORMAT: "25/26" (nicht "2025/2026"!)
        """
        datum = self.datum_edit.date()
        year = datum.year()
        month = datum.month()
        
        if month >= 8:  # August - Dezember
            schuljahr = f"{year % 100:02d}/{(year + 1) % 100:02d}"
        else:  # Januar - Juli
            schuljahr = f"{(year - 1) % 100:02d}/{year % 100:02d}"
        
        # Setze im Dropdown
        index = self.schuljahr_combo.findText(schuljahr)
        if index >= 0:
            self.schuljahr_combo.setCurrentIndex(index)
        else:
            # Falls nicht in Liste, hinzufügen
            self.schuljahr_combo.addItem(schuljahr)
            self.schuljahr_combo.setCurrentText(schuljahr)
        
    def load_schulen(self):
        """Schulen aus DB laden"""
        try:
            schulen = self.db.get_schulen()
            self.schule_combo.clear()
            
            for schule in schulen:
                self.schule_combo.addItem(schule['name'], schule['kuerzel'])
                
        except Exception as e:
            print(f"Fehler beim Laden der Schulen: {e}")
            # Fallback
            self.schule_combo.addItem("Gymnasium Dörpen", "gyd")
            self.schule_combo.addItem("Gymnasium Papenburg", "gympap")
            self.schule_combo.addItem("Oberschule", "obs")
    
    def on_jahrgangsstufe_changed(self):
        """Wird aufgerufen wenn Jahrgangsstufe geändert wird"""
        self.load_klassen()
    
    def load_klassen(self):
        """
        Klassen laden basierend auf Schule, Schuljahr und Jahrgangsstufe
        
        WICHTIG: Nutzt DB-Abfrage mit korrektem Schuljahr-Format!
        """
        try:
            schule_kuerzel = self.schule_combo.currentData()
            schuljahr = self.schuljahr_combo.currentText()
            jahrgangsstufe = self.jahrgangsstufe_spin.value()
            
            print(f"DEBUG load_klassen: schule={schule_kuerzel}, schuljahr={schuljahr}, stufe={jahrgangsstufe}")
            
            if schule_kuerzel and schuljahr:
                # Alle Klassen der Schule für dieses Schuljahr
                alle_klassen = self.db.get_klassen_by_schule(schuljahr, schule_kuerzel)
                print(f"DEBUG alle_klassen aus DB: {alle_klassen}")
                
                # Filtere nach Jahrgangsstufe
                klassen = [k for k in alle_klassen if k.startswith(str(jahrgangsstufe))]
                print(f"DEBUG gefiltert nach Stufe {jahrgangsstufe}: {klassen}")
                
                self.klasse_combo.clear()
                
                if klassen:
                    self.klasse_combo.addItems(klassen)
                else:
                    # Fallback: Generiere Standard-Klassen
                    print(f"DEBUG: Keine Klassen gefunden, nutze Fallback")
                    self.klasse_combo.addItems([
                        f"{jahrgangsstufe}a", 
                        f"{jahrgangsstufe}b", 
                        f"{jahrgangsstufe}c"
                    ])
                
        except Exception as e:
            print(f"Fehler beim Laden der Klassen: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: Generiere Klassen basierend auf Jahrgangsstufe
            jahrgangsstufe = self.jahrgangsstufe_spin.value()
            self.klasse_combo.clear()
            self.klasse_combo.addItems([
                f"{jahrgangsstufe}a", 
                f"{jahrgangsstufe}b", 
                f"{jahrgangsstufe}c"
            ])
    
    def load_from_klausur(self, klausur_data):
        """
        UI mit Klausur-Daten füllen
        
        NEU! Für Edit-Modus
        """
        # Signals blocken während Laden
        self.schule_combo.blockSignals(True)
        self.schuljahr_combo.blockSignals(True)
        self.jahrgangsstufe_spin.blockSignals(True)
        self.datum_edit.blockSignals(True)
        
        # Schule
        schule_kuerzel = klausur_data.get('schule', 'gyd')
        index = self.schule_combo.findData(schule_kuerzel)
        if index >= 0:
            self.schule_combo.setCurrentIndex(index)
        
        # Fach
        fach = klausur_data.get('fach', 'Mathematik')
        for button in self.fach_buttons.buttons():
            if button.text() == fach:
                button.setChecked(True)
                break
        
        # Jahrgangsstufe ZUERST setzen
        jahrgangsstufe = klausur_data.get('jahrgangsstufe', 8)
        self.jahrgangsstufe_spin.setValue(jahrgangsstufe)
        
        # Datum DANN setzen
        datum_str = klausur_data.get('datum', '')
        if datum_str:
            try:
                datum = QDate.fromString(datum_str, "dd.MM.yyyy")
                self.datum_edit.setDate(datum)
            except:
                pass
        
        # Schuljahr berechnen
        self.update_schuljahr_from_datum()
        
        # Klassen laden
        self.load_klassen()
        
        # Klasse setzen (NACH load_klassen!)
        klasse = klausur_data.get('klasse', '')
        if klasse:
            # Prüfe ob in Dropdown
            index = self.klasse_combo.findText(klasse)
            if index >= 0:
                self.klasse_combo.setCurrentIndex(index)
            else:
                # Nicht in Dropdown → manuell setzen (editable!)
                self.klasse_combo.setCurrentText(klasse)
        
        # Typ
        typ = klausur_data.get('typ', 'Klassenarbeit')
        for button in self.typ_buttons.buttons():
            if button.text() == typ:
                button.setChecked(True)
                break
        
        # Zeit
        zeit_minuten = klausur_data.get('zeit_minuten', 45)
        for button in self.zeit_buttons.buttons():
            if button.property("minuten") == zeit_minuten:
                button.setChecked(True)
                break
        
        # Thema
        titel = klausur_data.get('titel', '')
        self.thema_edit.setText(titel)
        
        # Signals wieder freigeben
        self.schule_combo.blockSignals(False)
        self.schuljahr_combo.blockSignals(False)
        self.jahrgangsstufe_spin.blockSignals(False)
        self.datum_edit.blockSignals(False)
    
    def validate(self):
        """Validierung"""
        
        # Thema darf nicht leer sein
        if not self.thema_edit.text().strip():
            QMessageBox.warning(
                self,
                "Fehlende Angabe",
                "Bitte geben Sie ein Thema ein."
            )
            self.thema_edit.setFocus()
            return False
        
        return True
        
    def save_data(self):
        """Daten in Klausur-Objekt speichern"""
        klausur = self.parent_tab.klausur
        
        # Schule
        klausur.schule_kuerzel = self.schule_combo.currentData()
        
        # Fach
        fach_button = self.fach_buttons.checkedButton()
        klausur.fach = fach_button.text()
        klausur.fach_kuerzel = fach_button.property("kuerzel")
        
        # Klasse
        klausur.jahrgangsstufe = self.jahrgangsstufe_spin.value()
        klausur.klasse = self.klasse_combo.currentText()  # Kann auch manuell eingegeben sein!
        klausur.schuljahr = self.schuljahr_combo.currentText()
        
        # Typ
        typ_button = self.typ_buttons.checkedButton()
        klausur.typ = typ_button.text()
        klausur.nummer = self.nummer_spin.value()
        
        # Termin
        klausur.datum = self.datum_edit.date().toString("dd.MM.yyyy")
        
        zeit_button = self.zeit_buttons.checkedButton()
        klausur.zeit_minuten = zeit_button.property("minuten")
        
        # Thema
        klausur.thema = self.thema_edit.text().strip()
        
        print(f"Step 1 gespeichert: {klausur.fach} {klausur.klasse} - {klausur.thema}")
        
    def reset(self):
        """Zurücksetzen"""
        self.thema_edit.clear()
        self.jahrgangsstufe_spin.setValue(8)
        self.nummer_spin.setValue(1)
        self.datum_edit.setDate(QDate.currentDate())
        
        # Defaults
        self.fach_buttons.button(0).setChecked(True)
        self.typ_buttons.button(0).setChecked(True)
        self.zeit_buttons.button(0).setChecked(True)


# ============================================================
# STEP 2: AUFGABEN AUSWÄHLEN (Platzhalter)
# ============================================================

class Step2AufgabenAuswahl(QWidget):
    """Step 2: Aufgaben aus Pool auswählen"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        
        title = QLabel("Schritt 2/5: Aufgaben auswählen")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # TODO: Master-Detail-View
        placeholder = QLabel("🚧 Wird als nächstes implementiert...")
        placeholder.setStyleSheet("color: #666; font-size: 14pt; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        
        layout.addStretch()
    
    def on_enter(self):
        """Wird aufgerufen wenn dieser Step betreten wird"""
        klausur = self.parent_tab.klausur
        print(f"Step 2: Laden Aufgaben für {klausur.fach}, Stufe {klausur.jahrgangsstufe}")
        
    def validate(self):
        """Validierung"""
        # TODO: Mindestens 1 Aufgabe?
        return True
        
    def save_data(self):
        """Daten speichern"""
        pass
        
    def reset(self):
        """Zurücksetzen"""
        pass


# ============================================================
# STEP 3-5: Platzhalter (werden später implementiert)
# ============================================================

class Step3Anordnung(QWidget):
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        layout = QVBoxLayout(self)
        label = QLabel("🚧 Step 3: Wird implementiert...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
    def validate(self): return True
    def save_data(self): pass
    def reset(self): pass


class Step4PDFOptionen(QWidget):
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        layout = QVBoxLayout(self)
        label = QLabel("🚧 Step 4: Wird implementiert...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
    def validate(self): return True
    def save_data(self): pass
    def reset(self): pass


class Step5Generierung(QWidget):
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        layout = QVBoxLayout(self)
        label = QLabel("🚧 Step 5: Wird implementiert...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
    def validate(self): return True
    def save_data(self): pass
    def reset(self): pass
