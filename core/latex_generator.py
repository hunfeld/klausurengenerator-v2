"""
LaTeX-Generator
===============

Generiert LaTeX-Code aus Klausur-Objekten
Portiert und erweitert aus klassensatz_generator_v1.8.py
"""

from typing import List, Dict, Tuple
from core.models import Klausur, KlausurAufgabe, Schueler
from utils.latex_helper import (
    escape_latex, 
    format_datum_deutsch, 
    generate_qr_code_data,
    sanitize_filename,
    cm_to_pt
)
import base64
from io import BytesIO


class LaTeXGenerator:
    """Generiert LaTeX-Code für Klausuren"""
    
    def __init__(self, klausur: Klausur):
        self.klausur = klausur
        
    def generate_complete_latex(self) -> str:
        """
        Generiert kompletten LaTeX-Code für alle Varianten
        
        Returns:
            LaTeX-Code als String
        """
        
        parts = []
        
        # Document-Header
        parts.append(self._generate_header())
        
        # Begin Document
        parts.append(r"\begin{document}")
        parts.append("")
        
        # Muster ohne Lösung
        if self.klausur.muster_ohne_loesung:
            parts.append("% ====== MUSTER OHNE LÖSUNG ======")
            parts.append(self._generate_muster(mit_loesung=False, ist_muster=True))
            parts.append(r"\newpage")
            parts.append("")
        
        # Muster mit Lösung
        if self.klausur.muster_mit_loesung:
            parts.append("% ====== MUSTER MIT LÖSUNG ======")
            parts.append(self._generate_muster(mit_loesung=True, ist_muster=True))
            parts.append(r"\newpage")
            parts.append("")
        
        # Klassensatz ohne Lösung
        if self.klausur.klassensatz_ohne_loesung:
            parts.append("% ====== KLASSENSATZ OHNE LÖSUNG ======")
            for schueler in self.klausur.schueler:
                parts.append(f"% Schüler: {schueler.vollname}")
                parts.append(self._generate_schueler_klausur(schueler, mit_loesung=False))
                parts.append(r"\newpage")
                parts.append("")
        
        # Klassensatz mit Lösung
        if self.klausur.klassensatz_mit_loesung:
            parts.append("% ====== KLASSENSATZ MIT LÖSUNG ======")
            for schueler in self.klausur.schueler:
                parts.append(f"% Schüler: {schueler.vollname} (mit Lösung)")
                parts.append(self._generate_schueler_klausur(schueler, mit_loesung=True))
                parts.append(r"\newpage")
                parts.append("")
        
        # End Document
        parts.append(r"\end{document}")
        
        return "\n".join(parts)
        
    def _generate_header(self) -> str:
        """Generiert LaTeX-Header mit Packages und Settings"""
        
        header = r"""\documentclass[a4paper,11pt]{article}

% Encoding & Language
\usepackage[utf8]{inputenc}
\usepackage[ngerman]{babel}
\usepackage[T1]{fontenc}

% Math
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}

% Graphics & Tables
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{booktabs}

% Page Layout
\usepackage{geometry}
\geometry{
    a4paper,
    left=2cm,
    right=2cm,
    top=3cm,
    bottom=2cm
}

% Headers & Footers
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% QR-Codes (falls benötigt)
\usepackage{qrcode}

% Aufzählungen
\usepackage{enumitem}

% Farben
\usepackage{xcolor}

% Spacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}

"""
        
        return header
        
    def _generate_muster(self, mit_loesung: bool = False, ist_muster: bool = True) -> str:
        """Generiert Muster-Exemplar"""
        
        parts = []
        
        # Header für erste Seite
        parts.append(self._generate_first_page_header(
            schueler_name="MUSTER" if ist_muster else None,
            qr_code_data=None
        ))
        
        # Titel
        parts.append(r"\begin{center}")
        parts.append(r"\LARGE\textbf{" + escape_latex(self.klausur.thema) + r"}")
        parts.append(r"\end{center}")
        parts.append(r"\vspace{1em}")
        
        # Metadata-Box
        parts.append(self._generate_metadata_box())
        parts.append(r"\vspace{1em}")
        
        # Aufgaben
        for ka in self.klausur.aufgaben:
            if ka.ist_aktiv:
                parts.append(self._generate_aufgabe(ka, mit_loesung))
                parts.append("")
        
        return "\n".join(parts)
        
    def _generate_schueler_klausur(self, schueler: Schueler, mit_loesung: bool = False) -> str:
        """Generiert personalisierte Schüler-Klausur mit QR-Code"""
        
        parts = []
        
        # QR-Code-Daten generieren
        qr_data = generate_qr_code_data(
            kasusid=100001,  # TODO: Aus DB holen
            schueler_id=schueler.schueler_id
        )
        
        # Header für erste Seite mit QR-Code
        parts.append(self._generate_first_page_header(
            schueler_name=schueler.vollname,
            qr_code_data=qr_data
        ))
        
        # Titel
        parts.append(r"\begin{center}")
        parts.append(r"\LARGE\textbf{" + escape_latex(self.klausur.thema) + r"}")
        parts.append(r"\end{center}")
        parts.append(r"\vspace{1em}")
        
        # Metadata-Box
        parts.append(self._generate_metadata_box())
        parts.append(r"\vspace{1em}")
        
        # Aufgaben
        for ka in self.klausur.aufgaben:
            if ka.ist_aktiv:
                parts.append(self._generate_aufgabe(ka, mit_loesung))
                parts.append("")
        
        return "\n".join(parts)
        
    def _generate_first_page_header(
        self, 
        schueler_name: str = None,
        qr_code_data: str = None
    ) -> str:
        """
        Generiert Header für erste Seite
        
        Auf Seite 1: Voller Header mit Logo und QR-Code
        Ab Seite 2: Nur laufende Kopfzeile (wird per fancyhdr gesetzt)
        """
        
        parts = []
        
        # Erste Seite: Spezieller Header
        parts.append(r"\thispagestyle{fancy}")
        
        # Logo und QR-Code Zeile
        if qr_code_data:
            parts.append(r"\fancyhead[L]{\includegraphics[height=1.5cm]{logo.png}}")  # TODO: Logo aus DB
            parts.append(r"\fancyhead[R]{\qrcode[height=1.5cm]{" + qr_code_data + r"}}")
        
        # Laufender Header ab Seite 2
        parts.append(r"\fancyhead[C]{" + escape_latex(f"{self.klausur.fach} - {self.klausur.klasse}") + r"}")
        parts.append(r"\fancyfoot[C]{\thepage}")
        
        # Name des Schülers (falls vorhanden)
        if schueler_name:
            parts.append(r"\noindent\textbf{Name:} " + escape_latex(schueler_name) + r"\\[0.5em]")
        
        return "\n".join(parts)
        
    def _generate_metadata_box(self) -> str:
        """Generiert Metadata-Box mit Fach, Datum, Zeit, etc."""
        
        parts = []
        
        parts.append(r"\noindent")
        parts.append(r"\begin{tabularx}{\textwidth}{@{}lXlX@{}}")
        parts.append(r"\textbf{Fach:} & " + escape_latex(self.klausur.fach) + r" & ")
        parts.append(r"\textbf{Datum:} & " + format_datum_deutsch(self.klausur.datum) + r" \\")
        parts.append(r"\textbf{Klasse:} & " + escape_latex(self.klausur.klasse) + r" & ")
        parts.append(r"\textbf{Zeit:} & " + str(self.klausur.zeit_minuten) + r" Minuten \\")
        parts.append(r"\textbf{Typ:} & " + escape_latex(self.klausur.typ) + r" Nr. " + str(self.klausur.nummer) + r" & ")
        parts.append(r"\textbf{Punkte:} & " + str(self.klausur.gesamtpunkte) + r" \\")
        parts.append(r"\end{tabularx}")
        
        return "\n".join(parts)
        
    def _generate_aufgabe(self, ka: KlausurAufgabe, mit_loesung: bool) -> str:
        """Generiert einzelne Aufgabe"""
        
        aufgabe = ka.aufgabe
        parts = []
        
        # Aufgaben-Header
        parts.append(r"\subsection*{Aufgabe " + str(ka.reihenfolge) + r"}")
        parts.append(r"\textit{" + escape_latex(aufgabe.titel) + r"} \hfill ")
        parts.append(r"\textbf{(" + str(aufgabe.punkte) + r" Punkte)}")
        parts.append(r"\vspace{0.5em}")
        parts.append("")
        
        # LaTeX-Code der Aufgabe
        if aufgabe.latex_code:
            parts.append(aufgabe.latex_code)
        else:
            # Fallback: Aufgaben-Daten als Text
            parts.append(r"\textbf{[Aufgabentext fehlt]}")
            parts.append("")
            parts.append(f"% Aufgaben-ID: {aufgabe.id}")
            parts.append(f"% Themengebiet: {aufgabe.themengebiet}")
        
        parts.append("")
        
        # Platz für Lösung
        if not mit_loesung:
            platz = aufgabe.platzbedarf_min if aufgabe.platzbedarf_min > 0 else 5.0
            parts.append(r"\vspace{" + str(platz) + r"cm}")
        else:
            # Lösung einfügen
            parts.append(r"\vspace{0.5em}")
            parts.append(r"\textcolor{blue}{\textbf{Lösung:}}")
            parts.append(r"\vspace{0.3em}")
            
            if aufgabe.loesung_generiert:
                parts.append(r"\textcolor{blue}{")
                parts.append(r"% TODO: Lösung aus DB/KI")
                parts.append(r"[Musterlösung wird hier eingefügt]")
                parts.append(r"}")
            else:
                parts.append(r"\textcolor{blue}{[Keine Lösung verfügbar]}")
            
            parts.append("")
        
        # Seitenumbruch falls markiert
        if ka.seite_nr > 1 and ka == self.klausur.aufgaben[-1]:
            parts.append(r"\newpage")
        
        return "\n".join(parts)
    
    def get_estimated_pages(self) -> int:
        """
        Schätzt Anzahl der Seiten
        
        Returns:
            Geschätzte Seitenzahl
        """
        
        # Grobe Schätzung: 
        # - Erste Seite: Header + Metadata + 1-2 Aufgaben
        # - Pro weitere Seite: ~2-3 Aufgaben
        
        anzahl_aufgaben = len([ka for ka in self.klausur.aufgaben if ka.ist_aktiv])
        
        if anzahl_aufgaben <= 2:
            return 1
        elif anzahl_aufgaben <= 5:
            return 2
        elif anzahl_aufgaben <= 8:
            return 3
        else:
            return 4


def generate_latex_for_klausur(klausur: Klausur) -> str:
    """
    Convenience-Funktion
    
    Args:
        klausur: Klausur-Objekt
        
    Returns:
        LaTeX-Code
    """
    generator = LaTeXGenerator(klausur)
    return generator.generate_complete_latex()
