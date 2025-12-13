"""
Datenmodelle
============

Klassen für Aufgaben, Klausuren, Schüler, etc.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Schule:
    """Schule"""
    id: int
    kuerzel: str
    name: str
    logo: Optional[bytes] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schule':
        """Aus Dictionary erstellen"""
        return cls(
            id=data['id'],
            kuerzel=data['kuerzel'],
            name=data['name'],
            logo=data.get('logo')
        )


@dataclass
class Schueler:
    """Schüler"""
    id: int
    schuljahr: str
    schule: str
    schueler_id: int
    rufname: str
    nachname: str
    klasse: str
    account: Optional[str] = None
    geschlecht: Optional[str] = None
    geburtstag: Optional[str] = None
    jahrgangsstufe: Optional[int] = None
    
    @property
    def vollname(self) -> str:
        """Vollständiger Name"""
        return f"{self.rufname} {self.nachname}"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schueler':
        """Aus Dictionary erstellen"""
        return cls(
            id=data['id'],
            schuljahr=data['schuljahr'],
            schule=data['schule'],
            schueler_id=data['schueler_id'],
            rufname=data['rufname'],
            nachname=data['nachname'],
            klasse=data['klasse'],
            account=data.get('account'),
            geschlecht=data.get('geschlecht'),
            geburtstag=data.get('geburtstag'),
            jahrgangsstufe=data.get('jahrgangsstufe')
        )


@dataclass
class AufgabenTemplate:
    """Aufgaben-Template"""
    id: int
    name: str
    latex_code: str
    fach: Optional[str] = None
    beschreibung: Optional[str] = None
    platzhalter: Optional[str] = None
    empfohlener_platzbedarf: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AufgabenTemplate':
        """Aus Dictionary erstellen"""
        return cls(
            id=data['id'],
            name=data['name'],
            latex_code=data['latex_code'],
            fach=data.get('fach'),
            beschreibung=data.get('beschreibung'),
            platzhalter=data.get('platzhalter'),
            empfohlener_platzbedarf=data.get('empfohlener_platzbedarf')
        )


@dataclass
class Aufgabe:
    """Aufgabe"""
    id: int
    template_id: int
    titel: str
    aufgaben_daten: str
    fach: str
    latex_code: str
    themengebiet: Optional[str] = None
    schwierigkeit: Optional[str] = None
    schlagwoerter: Optional[str] = None
    anforderungsbereich: Optional[str] = None
    punkte: int = 0
    kompetenzen: Optional[str] = None
    jahrgangsstufe: Optional[int] = None
    schulform: Optional[str] = None
    platzbedarf_min: float = 0.0
    ist_variation: bool = False
    erstellt_am: Optional[str] = None
    
    @property
    def geschaetzte_zeit(self) -> int:
        """Geschätzte Bearbeitungszeit in Minuten (2 Min pro Punkt)"""
        return self.punkte * 2
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Aufgabe':
        """Aus Dictionary erstellen"""
        return cls(
            id=data['id'],
            template_id=data['template_id'],
            titel=data['titel'],
            aufgaben_daten=data['aufgaben_daten'],
            fach=data.get('fach', ''),
            latex_code=data.get('latex_code', ''),
            themengebiet=data.get('themengebiet'),
            schwierigkeit=data.get('schwierigkeit'),
            schlagwoerter=data.get('schlagwoerter'),
            anforderungsbereich=data.get('anforderungsbereich'),
            punkte=data.get('punkte', 0),
            kompetenzen=data.get('kompetenzen'),
            jahrgangsstufe=data.get('jahrgangsstufe'),
            schulform=data.get('schulform'),
            platzbedarf_min=data.get('platzbedarf_min', 0.0),
            ist_variation=bool(data.get('ist_variation', False)),
            erstellt_am=data.get('erstellt_am')
        )


@dataclass
class KlausurAufgabe:
    """Aufgabe innerhalb einer Klausur"""
    aufgabe: Aufgabe
    reihenfolge: int
    seite_nr: int = 1
    ist_aktiv: bool = True


@dataclass
class Klausur:
    """Klausur (temporäres Objekt während Erstellung)"""
    
    # Setup-Daten (Step 1)
    schule: Optional[Schule] = None
    schule_kuerzel: str = ""
    fach: str = ""
    fach_kuerzel: str = ""
    jahrgangsstufe: int = 0
    klasse: str = ""
    typ: str = "Klassenarbeit"  # Klassenarbeit, Klausur, Test
    nummer: int = 1
    datum: str = ""
    zeit_minuten: int = 45
    thema: str = ""
    schuljahr: str = "2024/2025"
    
    # Aufgaben (Step 2 + 3)
    aufgaben: List[KlausurAufgabe] = field(default_factory=list)
    
    # PDF-Optionen (Step 4)
    muster_ohne_loesung: bool = True
    muster_mit_loesung: bool = True
    klassensatz_ohne_loesung: bool = True
    klassensatz_mit_loesung: bool = False
    
    # Schüler (für Klassensatz)
    schueler: List[Schueler] = field(default_factory=list)
    
    # Metadaten
    seitenzahl: int = 4
    
    @property
    def gesamtpunkte(self) -> int:
        """Gesamtpunktzahl aller aktiven Aufgaben"""
        return sum(ka.aufgabe.punkte for ka in self.aufgaben if ka.ist_aktiv)
    
    @property
    def geschaetzte_zeit(self) -> int:
        """Geschätzte Zeit aller Aufgaben in Minuten"""
        return sum(ka.aufgabe.geschaetzte_zeit for ka in self.aufgaben if ka.ist_aktiv)
    
    @property
    def anzahl_aufgaben(self) -> int:
        """Anzahl aktiver Aufgaben"""
        return sum(1 for ka in self.aufgaben if ka.ist_aktiv)
    
    @property
    def anzahl_schueler(self) -> int:
        """Anzahl Schüler"""
        return len(self.schueler)
    
    @property
    def dateiname_basis(self) -> str:
        """Basis-Dateiname für PDF"""
        # Format: Ma-2_8a_20250324
        datum_formatted = self.datum.replace("-", "").replace(".", "")
        return f"{self.fach_kuerzel}-{self.nummer}_{self.klasse}_{datum_formatted}"
    
    def to_dict(self) -> Dict[str, Any]:
        """In Dictionary konvertieren (für Speicherung)"""
        return {
            'fach': self.fach,
            'fach_kuerzel': self.fach_kuerzel,
            'jahrgangsstufe': self.jahrgangsstufe,
            'klasse': self.klasse,
            'typ': self.typ,
            'nummer': self.nummer,
            'datum': self.datum,
            'zeit_minuten': self.zeit_minuten,
            'thema': self.thema,
            'schuljahr': self.schuljahr,
            'seitenzahl': self.seitenzahl,
            'gesamtpunkte': self.gesamtpunkte
        }


@dataclass
class Grafik:
    """Grafik aus Pool"""
    id: int
    name: str
    dateityp: str
    grafik_blob: bytes
    beschreibung: Optional[str] = None
    breite_px: Optional[int] = None
    hoehe_px: Optional[int] = None
    groesse_bytes: Optional[int] = None
    tags: Optional[str] = None
    verwendet_in: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Grafik':
        """Aus Dictionary erstellen"""
        return cls(
            id=data['id'],
            name=data['name'],
            dateityp=data['dateityp'],
            grafik_blob=data['grafik_blob'],
            beschreibung=data.get('beschreibung'),
            breite_px=data.get('breite_px'),
            hoehe_px=data.get('hoehe_px'),
            groesse_bytes=data.get('groesse_bytes'),
            tags=data.get('tags'),
            verwendet_in=data.get('verwendet_in', 0)
        )
