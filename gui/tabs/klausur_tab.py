"""
Klausur-Tab mit 5-Step-Wizard
==============================

Step 1: Setup (Grunddaten)
Step 2: Aufgaben auswählen
Step 3: Anordnung
Step 4: PDF-Optionen
Step 5: Generierung

v2.0.0 - Step 2 komplett implementiert!
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, 
    QFrame, QGroupBox, QComboBox, QRadioButton, QButtonGroup, QSpinBox,
    QLineEdit, QDateEdit, QMessageBox, QFormLayout, QScrollArea, QSplitter,
    QTableWidget, QTableWidgetItem, QTextEdit, QHeaderView, QListWidget,
    QListWidgetItem
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
        klasse_layout.addRow("Jahrgangsstufe:", self.jahrgangsstufe_spin)
        
        # Klasse (editable ComboBox!)
        self.klasse_combo = QComboBox()
        self.klasse_combo.setEditable(True)
        klasse_layout.addRow("Klasse:", self.klasse_combo)
        
        # Schuljahr
        self.schuljahr_combo = QComboBox()
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
            
            if i == 0:
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
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Initial-Daten laden
        self.load_schulen()
        self.populate_schuljahre()
        self.update_schuljahr_from_datum()
        self.load_klassen()
        
        # Signals verbinden (GANZ AM ENDE!)
        self.schule_combo.currentIndexChanged.connect(self.on_schule_changed)
        self.schuljahr_combo.currentIndexChanged.connect(self.on_schuljahr_changed)
        self.jahrgangsstufe_spin.valueChanged.connect(self.on_jahrgangsstufe_changed)
        self.datum_edit.dateChanged.connect(self.on_datum_changed)
        
    def populate_schuljahre(self):
        """Schuljahre generieren (Format: 25/26)"""
        current_year = QDate.currentDate().year()
        self.schuljahr_combo.clear()
        
        for offset in range(-3, 3):
            year = current_year + offset
            schuljahr = f"{year % 100:02d}/{(year + 1) % 100:02d}"
            self.schuljahr_combo.addItem(schuljahr)
    
    def on_datum_changed(self):
        """Datum geändert → Schuljahr berechnen"""
        self.update_schuljahr_from_datum()
    
    def on_schule_changed(self):
        """Schule geändert → Klassen neu laden"""
        self.load_klassen()
    
    def on_schuljahr_changed(self):
        """Schuljahr geändert → Klassen neu laden"""
        self.load_klassen()
    
    def update_schuljahr_from_datum(self):
        """Berechne Schuljahr aus Datum (Format: 25/26)"""
        datum = self.datum_edit.date()
        year = datum.year()
        month = datum.month()
        
        if month >= 8:
            schuljahr = f"{year % 100:02d}/{(year + 1) % 100:02d}"
        else:
            schuljahr = f"{(year - 1) % 100:02d}/{year % 100:02d}"
        
        index = self.schuljahr_combo.findText(schuljahr)
        if index >= 0:
            self.schuljahr_combo.setCurrentIndex(index)
        else:
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
            self.schule_combo.addItem("Gymnasium Dörpen", "gyd")
            self.schule_combo.addItem("Gymnasium Papenburg", "gympap")
            self.schule_combo.addItem("Oberschule", "obs")
    
    def on_jahrgangsstufe_changed(self):
        """Jahrgangsstufe geändert → Klassen neu laden"""
        self.load_klassen()
    
    def load_klassen(self):
        """Klassen laden und nach Jahrgangsstufe filtern"""
        try:
            schule_kuerzel = self.schule_combo.currentData()
            schuljahr = self.schuljahr_combo.currentText()
            jahrgangsstufe = self.jahrgangsstufe_spin.value()
            
            if schule_kuerzel and schuljahr:
                alle_klassen = self.db.get_klassen_by_schule(schuljahr, schule_kuerzel)
                klassen = [k for k in alle_klassen if k.startswith(str(jahrgangsstufe))]
                
                self.klasse_combo.clear()
                
                if klassen:
                    self.klasse_combo.addItems(klassen)
                else:
                    self.klasse_combo.addItems([
                        f"{jahrgangsstufe}a", 
                        f"{jahrgangsstufe}b", 
                        f"{jahrgangsstufe}c"
                    ])
        except Exception as e:
            print(f"Fehler beim Laden der Klassen: {e}")
            jahrgangsstufe = self.jahrgangsstufe_spin.value()
            self.klasse_combo.clear()
            self.klasse_combo.addItems([f"{jahrgangsstufe}a", f"{jahrgangsstufe}b", f"{jahrgangsstufe}c"])
    
    def load_from_klausur(self, klausur_data):
        """UI mit Klausur-Daten füllen (Edit-Modus)"""
        # Signals blocken
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
        
        # Jahrgangsstufe
        jahrgangsstufe = klausur_data.get('jahrgangsstufe', 8)
        self.jahrgangsstufe_spin.setValue(jahrgangsstufe)
        
        # Datum
        datum_str = klausur_data.get('datum', '')
        if datum_str:
            try:
                datum = QDate.fromString(datum_str, "dd.MM.yyyy")
                self.datum_edit.setDate(datum)
            except:
                pass
        
        self.update_schuljahr_from_datum()
        self.load_klassen()
        
        # Klasse
        klasse = klausur_data.get('klasse', '')
        if klasse:
            index = self.klasse_combo.findText(klasse)
            if index >= 0:
                self.klasse_combo.setCurrentIndex(index)
            else:
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
        
        # Signals freigeben
        self.schule_combo.blockSignals(False)
        self.schuljahr_combo.blockSignals(False)
        self.jahrgangsstufe_spin.blockSignals(False)
        self.datum_edit.blockSignals(False)
    
    def validate(self):
        """Validierung"""
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
        
        klausur.schule_kuerzel = self.schule_combo.currentData()
        
        fach_button = self.fach_buttons.checkedButton()
        klausur.fach = fach_button.text()
        klausur.fach_kuerzel = fach_button.property("kuerzel")
        
        klausur.jahrgangsstufe = self.jahrgangsstufe_spin.value()
        klausur.klasse = self.klasse_combo.currentText()
        klausur.schuljahr = self.schuljahr_combo.currentText()
        
        typ_button = self.typ_buttons.checkedButton()
        klausur.typ = typ_button.text()
        klausur.nummer = self.nummer_spin.value()
        
        klausur.datum = self.datum_edit.date().toString("dd.MM.yyyy")
        
        zeit_button = self.zeit_buttons.checkedButton()
        klausur.zeit_minuten = zeit_button.property("minuten")
        
        klausur.thema = self.thema_edit.text().strip()
        
        print(f"Step 1 gespeichert: {klausur.fach} {klausur.klasse} - {klausur.thema}")
        
    def reset(self):
        """Zurücksetzen"""
        self.thema_edit.clear()
        self.jahrgangsstufe_spin.setValue(8)
        self.nummer_spin.setValue(1)
        self.datum_edit.setDate(QDate.currentDate())
        
        self.fach_buttons.button(0).setChecked(True)
        self.typ_buttons.button(0).setChecked(True)
        self.zeit_buttons.button(0).setChecked(True)


# ============================================================
# STEP 2: AUFGABEN AUSWÄHLEN
# ============================================================

class Step2AufgabenAuswahl(QWidget):
    """Step 2: Aufgaben aus Pool auswählen - KOMPLETT IMPLEMENTIERT!"""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.db = get_database()
        
        # Ausgewählte Aufgaben (Liste von IDs)
        self.selected_aufgaben_ids = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI aufbauen"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Titel
        title = QLabel("Schritt 2/5: Aufgaben auswählen")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Haupt-Split: Oben (Aufgaben-Pool) / Unten (Ausgewählte)
        main_split = QSplitter(Qt.Orientation.Vertical)
        
        # ========== OBEN: Aufgaben-Pool ==========
        pool_widget = QWidget()
        pool_layout = QVBoxLayout(pool_widget)
        pool_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        pool_label = QLabel("📚 Aufgaben-Pool")
        pool_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        pool_layout.addWidget(pool_label)
        
        # Filter-Leiste
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 5, 0, 5)
        
        # Suchfeld
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Suche nach Titel/Thema...")
        self.search_edit.textChanged.connect(self.load_aufgaben)
        filter_layout.addWidget(self.search_edit, 2)
        
        # Schwierigkeit
        filter_layout.addWidget(QLabel("Schwierigkeit:"))
        self.schwierigkeit_combo = QComboBox()
        self.schwierigkeit_combo.addItems(["Alle", "leicht", "mittel", "schwer"])
        self.schwierigkeit_combo.currentTextChanged.connect(self.load_aufgaben)
        filter_layout.addWidget(self.schwierigkeit_combo, 1)
        
        # Anforderungsbereich
        filter_layout.addWidget(QLabel("AFB:"))
        self.afb_combo = QComboBox()
        self.afb_combo.addItems(["Alle", "I", "II", "III"])
        self.afb_combo.currentTextChanged.connect(self.load_aufgaben)
        filter_layout.addWidget(self.afb_combo, 1)
        
        pool_layout.addWidget(filter_widget)
        
        # Split: Links (Tabelle) / Rechts (Detail)
        pool_split = QSplitter(Qt.Orientation.Horizontal)
        
        # Links: Tabelle
        self.aufgaben_table = QTableWidget()
        self.aufgaben_table.setColumnCount(6)
        self.aufgaben_table.setHorizontalHeaderLabels([
            "ID", "Titel", "Thema", "Schwierigkeit", "AFB", "Punkte"
        ])
        self.aufgaben_table.horizontalHeader().setStretchLastSection(False)
        self.aufgaben_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.aufgaben_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.aufgaben_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.aufgaben_table.itemSelectionChanged.connect(self.on_aufgabe_selected)
        self.aufgaben_table.doubleClicked.connect(self.add_aufgabe)
        pool_split.addWidget(self.aufgaben_table)
        
        # Rechts: Detail + Button
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        
        detail_label = QLabel("📋 Detail-Ansicht")
        detail_label.setStyleSheet("font-weight: bold;")
        detail_layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)
        
        self.add_btn = QPushButton("➕ Hinzufügen")
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self.add_aufgabe)
        detail_layout.addWidget(self.add_btn)
        
        pool_split.addWidget(detail_widget)
        pool_split.setSizes([600, 300])
        
        pool_layout.addWidget(pool_split)
        main_split.addWidget(pool_widget)
        
        # ========== UNTEN: Ausgewählte Aufgaben ==========
        selected_widget = QWidget()
        selected_layout = QVBoxLayout(selected_widget)
        selected_layout.setContentsMargins(0, 0, 0, 0)
        
        selected_label = QLabel("✅ Ausgewählte Aufgaben")
        selected_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        selected_layout.addWidget(selected_label)
        
        self.selected_list = QListWidget()
        selected_layout.addWidget(self.selected_list)
        
        # Buttons
        selected_buttons = QHBoxLayout()
        
        self.remove_btn = QPushButton("❌ Entfernen")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.remove_aufgabe)
        selected_buttons.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("🗑️ Alle entfernen")
        self.clear_btn.clicked.connect(self.clear_aufgaben)
        selected_buttons.addWidget(self.clear_btn)
        
        selected_buttons.addStretch()
        
        self.count_label = QLabel("0 Aufgaben ausgewählt")
        selected_buttons.addWidget(self.count_label)
        
        selected_layout.addLayout(selected_buttons)
        
        main_split.addWidget(selected_widget)
        main_split.setSizes([400, 200])
        
        layout.addWidget(main_split)
        
        # Signal für selected_list
        self.selected_list.itemSelectionChanged.connect(self.on_selected_item_changed)
    
    def on_enter(self):
        """Wird aufgerufen wenn Step 2 betreten wird"""
        klausur = self.parent_tab.klausur
        print(f"Step 2: Laden Aufgaben für {klausur.fach}, Stufe {klausur.jahrgangsstufe}")
        self.load_aufgaben()
    
    def load_aufgaben(self):
        """Aufgaben aus DB laden mit Filtern"""
        klausur = self.parent_tab.klausur
        
        # Filter aus UI
        suchtext = self.search_edit.text().strip()
        schwierigkeit = self.schwierigkeit_combo.currentText()
        afb = self.afb_combo.currentText()
        
        # DB-Abfrage
        aufgaben = self.db.get_aufgaben(
            fach=klausur.fach,
            jahrgangsstufe=klausur.jahrgangsstufe,
            schwierigkeit=None if schwierigkeit == "Alle" else schwierigkeit,
            anforderungsbereich=None if afb == "Alle" else afb,
            suchtext=suchtext if suchtext else None
        )
        
        # Tabelle füllen
        self.aufgaben_table.setRowCount(0)
        
        for aufgabe in aufgaben:
            row = self.aufgaben_table.rowCount()
            self.aufgaben_table.insertRow(row)
            
            self.aufgaben_table.setItem(row, 0, QTableWidgetItem(str(aufgabe['id'])))
            self.aufgaben_table.setItem(row, 1, QTableWidgetItem(aufgabe['titel'] or ''))
            self.aufgaben_table.setItem(row, 2, QTableWidgetItem(aufgabe['themengebiet'] or ''))
            self.aufgaben_table.setItem(row, 3, QTableWidgetItem(aufgabe['schwierigkeit'] or ''))
            self.aufgaben_table.setItem(row, 4, QTableWidgetItem(aufgabe['anforderungsbereich'] or ''))
            self.aufgaben_table.setItem(row, 5, QTableWidgetItem(str(aufgabe['punkte'] or 0)))
            
            # Speichere komplette Aufgabe als UserRole
            self.aufgaben_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, aufgabe)
    
    def on_aufgabe_selected(self):
        """Aufgabe in Tabelle ausgewählt"""
        selected_rows = self.aufgaben_table.selectedItems()
        
        if not selected_rows:
            self.detail_text.clear()
            self.add_btn.setEnabled(False)
            return
        
        # Erste Zelle der Zeile
        row = selected_rows[0].row()
        aufgabe = self.aufgaben_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Detail anzeigen
        detail_html = f"""
        <h3>{aufgabe['titel']}</h3>
        <p><b>ID:</b> {aufgabe['id']}</p>
        <p><b>Themengebiet:</b> {aufgabe['themengebiet'] or '-'}</p>
        <p><b>Schwierigkeit:</b> {aufgabe['schwierigkeit'] or '-'}</p>
        <p><b>Anforderungsbereich:</b> {aufgabe['anforderungsbereich'] or '-'}</p>
        <p><b>Punkte:</b> {aufgabe['punkte'] or 0}</p>
        <p><b>Platzbedarf:</b> {aufgabe['platzbedarf_min'] or 0.0} cm</p>
        <p><b>Schlagwörter:</b> {aufgabe['schlagwoerter'] or '-'}</p>
        """
        
        self.detail_text.setHtml(detail_html)
        self.add_btn.setEnabled(True)
    
    def add_aufgabe(self):
        """Aufgabe zur Auswahl hinzufügen"""
        selected_rows = self.aufgaben_table.selectedItems()
        
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        aufgabe = self.aufgaben_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        aufgabe_id = aufgabe['id']
        
        # Prüfe ob schon ausgewählt
        if aufgabe_id in self.selected_aufgaben_ids:
            QMessageBox.information(self, "Info", "Diese Aufgabe wurde bereits hinzugefügt.")
            return
        
        # Hinzufügen
        self.selected_aufgaben_ids.append(aufgabe_id)
        
        # In Liste anzeigen
        item = QListWidgetItem(f"#{len(self.selected_aufgaben_ids)}: {aufgabe['titel']} ({aufgabe['punkte']} P)")
        item.setData(Qt.ItemDataRole.UserRole, aufgabe)
        self.selected_list.addItem(item)
        
        # Update Count
        self.update_count()
    
    def on_selected_item_changed(self):
        """Item in selected_list ausgewählt"""
        self.remove_btn.setEnabled(len(self.selected_list.selectedItems()) > 0)
    
    def remove_aufgabe(self):
        """Aufgabe aus Auswahl entfernen"""
        selected_items = self.selected_list.selectedItems()
        
        if not selected_items:
            return
        
        for item in selected_items:
            aufgabe = item.data(Qt.ItemDataRole.UserRole)
            self.selected_aufgaben_ids.remove(aufgabe['id'])
            self.selected_list.takeItem(self.selected_list.row(item))
        
        # Nummerierung aktualisieren
        self.renumber_selected()
        self.update_count()
    
    def clear_aufgaben(self):
        """Alle Aufgaben entfernen"""
        if not self.selected_aufgaben_ids:
            return
        
        reply = QMessageBox.question(
            self,
            "Bestätigung",
            "Wirklich alle Aufgaben entfernen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.selected_aufgaben_ids.clear()
            self.selected_list.clear()
            self.update_count()
    
    def renumber_selected(self):
        """Nummerierung der selected_list aktualisieren"""
        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            aufgabe = item.data(Qt.ItemDataRole.UserRole)
            item.setText(f"#{i+1}: {aufgabe['titel']} ({aufgabe['punkte']} P)")
    
    def update_count(self):
        """Anzahl ausgewählter Aufgaben aktualisieren"""
        count = len(self.selected_aufgaben_ids)
        total_punkte = sum([
            self.selected_list.item(i).data(Qt.ItemDataRole.UserRole)['punkte'] or 0
            for i in range(self.selected_list.count())
        ])
        
        self.count_label.setText(f"{count} Aufgaben ausgewählt ({total_punkte} Punkte)")
        
    def validate(self):
        """Validierung"""
        if not self.selected_aufgaben_ids:
            QMessageBox.warning(
                self,
                "Fehlende Aufgaben",
                "Bitte wählen Sie mindestens eine Aufgabe aus."
            )
            return False
        return True
        
    def save_data(self):
        """Daten speichern"""
        # Speichere IDs im Klausur-Objekt
        self.parent_tab.klausur.aufgaben_ids = self.selected_aufgaben_ids.copy()
        print(f"Step 2 gespeichert: {len(self.selected_aufgaben_ids)} Aufgaben ausgewählt")
        
    def reset(self):
        """Zurücksetzen"""
        self.selected_aufgaben_ids.clear()
        self.selected_list.clear()
        self.search_edit.clear()
        self.schwierigkeit_combo.setCurrentIndex(0)
        self.afb_combo.setCurrentIndex(0)
        self.update_count()


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
