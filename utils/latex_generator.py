#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaTeX Generator für Klausurengenerator
Version 2.5.0: ERWEITERT mit Klassensatz-Generierung

ÄNDERUNGEN v2.5.0:
- + Klassensatz-Generierung (generate_klassensatz)
- + Running Header auf Seiten 2-4
- + Automatisches Page Reordering (4-1-2-3)
- + Musterklausuren-Support
- + Leere Seite 4 bei 2 Umbrüchen

Basierend auf klassensatz_generator_v1_8.py
"""

import requests
import json
from pathlib import Path
import sqlite3
from typing import Optional, Dict, List, Tuple, Callable
import hashlib
import io
import base64
import re
from PyPDF2 import PdfReader, PdfWriter


LATEX_API_URL = "https://latex.ytotech.com/builds/sync"


class LaTeXGenerator:
    """
    Service-Klasse für LaTeX-PDF-Generierung via latex.ytotech.com
    MIT Klassensatz-Support!
    """
    
    def __init__(self, api_url: str = LATEX_API_URL, db_path: str = None):
        self.api_url = api_url
        self.header = self.get_default_header()
        self.db_path = Path(db_path) if db_path else (Path(__file__).parent.parent / 'database' / 'sus.db')
    
    # ========================================================================
    # KLASSENSATZ-GENERIERUNG (NEU!)
    # ========================================================================
    
    def generate_klassensatz(
        self,
        klausur,
        aufgaben: List[Dict],
        schueler_list: List[Dict],
        mit_musterklausuren: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> Optional[bytes]:
        """
        Generiert Klassensatz-PDF (EINE Datei für alle Schüler)
        
        Args:
            klausur: Klausur-Objekt mit Metadaten
            aufgaben: Liste der Aufgaben-Dicts
            schueler_list: Liste der Schüler-Dicts
            mit_musterklausuren: Musterklausuren vor dem Klassensatz?
            progress_callback: Callback(value, message) für Progress
        
        Returns:
            PDF als bytes oder None bei Fehler
        """
        
        try:
            if progress_callback:
                progress_callback(10, "Lade Logo und Grafiken...")
            
            # Logo laden
            logo_blob = self._hole_schul_logo(klausur.schule_kuerzel)
            
            # Grafiken laden
            aufgaben_ids = [a['id'] for a in aufgaben]
            grafiken = self._hole_aufgaben_grafiken(aufgaben_ids)
            
            if progress_callback:
                progress_callback(30, "Generiere LaTeX-Code...")
            
            # LaTeX Code generieren
            latex_code = self._baue_klassensatz_latex(
                klausur=klausur,
                aufgaben=aufgaben,
                schueler_list=schueler_list,
                mit_musterklausuren=mit_musterklausuren
            )
            
            if progress_callback:
                progress_callback(50, "Kompiliere PDF mit API (kann 10-30 Sek dauern)...")
            
            # PDF kompilieren
            pdf_bytes = self._kompiliere_mit_api(
                latex_code=latex_code,
                logo_blob=logo_blob,
                grafiken=grafiken
            )
            
            if not pdf_bytes:
                return None
            
            # Page Reordering (wenn nötig)
            page_breaks = len(klausur.page_breaks) if hasattr(klausur, 'page_breaks') else 0
            
            if page_breaks >= 2:
                if progress_callback:
                    progress_callback(70, "Sortiere Seiten um (4-1-2-3)...")
                
                pdf_bytes = self._sortiere_pdf_seiten(pdf_bytes, pages_per_student=4)
                if not pdf_bytes:
                    return None
            
            if progress_callback:
                progress_callback(100, "Fertig!")
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Fehler in generate_klassensatz: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _baue_klassensatz_latex(
        self,
        klausur,
        aufgaben: List[Dict],
        schueler_list: List[Dict],
        mit_musterklausuren: bool
    ) -> str:
        """Baut kompletten LaTeX-Code für Klassensatz"""
        
        # Header
        latex = r"""\documentclass[a4paper,12pt]{exam}
% Pakete
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[ngerman]{babel}
\usepackage{graphicx}
\usepackage{qrcode}
\usepackage{tikz}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage[margin=1cm]{geometry}
\usepackage{multicol}
\usepackage{changepage}
\usepackage{lmodern}
\usepackage{ulem}
\usepackage{fancyhdr}
\usepackage{siunitx}
\usepackage{stmaryrd}
\usepackage{enumitem}
\usetikzlibrary{calc}
\setlength{\gridsize}{5.154639mm}
\setlength{\gridlinewidth}{0.1pt}
\usetikzlibrary{angles,quotes,arrows}
\usepackage{pgfplots}
\pgfplotsset{compat=1.15}
\usepackage{mathrsfs}
\usepackage[gen]{eurosym}

% solgrid-Umgebung
\newenvironment{solgrid}[1][2cm]{%
  \vspace{0.3em}
  \begin{adjustwidth}{-3em}{-3em}
  \begin{solutionorgrid}[#1]
}{%
  \end{solutionorgrid}
  \end{adjustwidth}
}

\renewcommand{\questionlabel}{{\large\textcircled{\normalsize \texttt{\thequestion}}}}
\renewcommand{\solutiontitle}{Lösung: }

% Fancyhdr Setup
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\setlength{\headheight}{15pt}
\addtolength{\topmargin}{-3pt}

% Header-Makro
\newcommand{\customheader}[8]{%
  \parindent 0pt
  \begin{tikzpicture}
    \draw[rounded corners=15pt, line width=0.75pt, color=blue] (0,0) rectangle (\textwidth,-2cm);
    \node[anchor=north west] at (0,-0.2) {\includegraphics[height=1.5cm]{logo.png}};
    \node[anchor=north east] at (\textwidth,-0.2) {\qrcode[height=1.5cm]{#3}};
    \draw[color=blue, line width=0.75pt] (\textwidth-2.5cm,-1cm) circle (0.7cm);
    \node[anchor=north, text width=\textwidth-6cm, align=center] at (\textwidth/2, -0.6cm) {%
      \textbf{#4. #1arbeit in der #5 am #6}\\
      \textbf{#7 von #2 (#8)}
    };
  \end{tikzpicture}
}

\begin{document}

"""
        
        # TODO: Musterklausuren (falls aktiviert)
        if mit_musterklausuren:
            latex += "% TODO: Musterklausuren (ohne QR, ohne/mit Lösung)\n\n"
        
        # Seitenumbrüche aus Klausur
        page_breaks = klausur.page_breaks if hasattr(klausur, 'page_breaks') else []
        
        # Für jeden Schüler
        for idx, schueler in enumerate(schueler_list, start=1):
            kasusid = self._hole_naechste_kasusid()
            
            schueler_name = f"{schueler['rufname']} {schueler['nachname']}"
            
            # Running Header (Seiten 2+)
            running_header = f"{klausur.nummer if hasattr(klausur, 'nummer') else '1'}. {klausur.typ} in der {klausur.klasse} von {schueler_name} ({idx})"
            
            latex += f"% Schüler {idx}: {schueler_name}\n"
            latex += f"\\fancyhead[L]{{{self._tex_escape(running_header)}}}\n"
            latex += r"\renewcommand{\headrulewidth}{0.4pt}" + "\n"
            
            # Seite 1: Ohne fancyhdr
            latex += r"\thispagestyle{empty}" + "\n"
            
            # Header (voller Header auf Seite 1)
            latex += (
                f"\\customheader"
                f"{{{self._tex_escape(klausur.fach)}}}"
                f"{{{self._tex_escape(schueler_name)}}}"
                f"{{{kasusid}}}"
                f"{{{getattr(klausur, 'nummer', 1)}}}"
                f"{{{self._tex_escape(klausur.klasse)}}}"
                f"{{{self._tex_escape(klausur.datum)}}}"
                f"{{{self._tex_escape(klausur.thema)}}}"
                f"{{{idx}}}\n\n"
            )
            
            # Aufgaben
            latex += r"\begin{questions}" + "\n\n"
            
            for aufgaben_idx, aufgabe in enumerate(aufgaben):
                latex_code = aufgabe.get('latex_code', '') or ''
                latex += latex_code + "\n"
                
                # Seitenumbruch nach dieser Aufgabe?
                if aufgaben_idx in page_breaks:
                    latex += r"\newpage" + "\n\n"
            
            latex += r"\end{questions}" + "\n\n"
            
            # Falls 2 Umbrüche → Leere Seite 4
            if len(page_breaks) == 2:
                latex += r"\newpage" + "\n"
                latex += r"\vspace*{\fill}" + "\n"
                latex += r"\begin{center}" + "\n"
                latex += r"\Large" + "\n"
                latex += f"Viel Erfolg, {self._tex_escape(schueler['rufname'])}!\n"
                latex += r"\end{center}" + "\n"
                latex += r"\vspace*{\fill}" + "\n"
            else:
                # Abschluss (bei 0-1 oder 3+ Umbrüchen)
                latex += r"\vfill" + "\n"
                latex += r"\begin{flushright}" + "\n"
                latex += f"Viel Erfolg, {self._tex_escape(schueler['rufname'])}!\n"
                latex += r"\end{flushright}" + "\n"
            
            # Nächster Schüler
            if idx < len(schueler_list):
                latex += r"\newpage" + "\n\n"
        
        latex += r"\end{document}" + "\n"
        return latex
    
    def _hole_naechste_kasusid(self) -> int:
        """Holt nächste KaSuSId aus DB und inkrementiert Counter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT letzter_wert FROM kasusid_counter WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            aktueller_wert = row[0]
            naechster_wert = aktueller_wert + 1
            
            cursor.execute("""
                UPDATE kasusid_counter
                SET letzter_wert = ?, aktualisiert_am = CURRENT_TIMESTAMP
                WHERE id = 1
            """, (naechster_wert,))
            
            conn.commit()
            conn.close()
            return naechster_wert
        else:
            # Initialisiere
            cursor.execute("""
                INSERT INTO kasusid_counter (id, letzter_wert)
                VALUES (1, 100001)
            """)
            conn.commit()
            conn.close()
            return 100001
    
    def _hole_schul_logo(self, schule_kuerzel: str) -> Optional[bytes]:
        """Holt Logo-BLOB aus DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT logo FROM schulen WHERE kuerzel = ?", (schule_kuerzel,))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row and row[0] else None
    
    def _hole_aufgaben_grafiken(self, aufgaben_ids: List[int]) -> Dict[str, bytes]:
        """Holt alle Grafiken für gegebene Aufgaben-IDs"""
        if not aufgaben_ids:
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(aufgaben_ids))
        cursor.execute(f"""
            SELECT DISTINCT latex_name, grafik_blob
            FROM aufgaben_grafiken
            WHERE aufgabe_id IN ({placeholders})
        """, aufgaben_ids)
        
        grafiken = {}
        for latex_name, blob in cursor.fetchall():
            if latex_name and blob:
                grafiken[latex_name] = blob
        
        conn.close()
        return grafiken
    
    def _kompiliere_mit_api(
        self,
        latex_code: str,
        logo_blob: Optional[bytes],
        grafiken: Optional[Dict[str, bytes]] = None
    ) -> Optional[bytes]:
        """Kompiliert LaTeX zu PDF via API"""
        
        # Resources
        resources = [{"main": True, "content": latex_code}]
        
        if logo_blob:
            logo_b64 = base64.b64encode(logo_blob).decode("utf-8")
            resources.append({"path": "logo.png", "file": logo_b64})
        
        if grafiken:
            for latex_name, blob in grafiken.items():
                grafik_b64 = base64.b64encode(blob).decode("utf-8")
                resources.append({"path": f"{latex_name}.png", "file": grafik_b64})
        
        payload = {
            "compiler": "pdflatex",
            "resources": resources
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/pdf",
                },
                timeout=120,
            )
            
            if response.status_code in (200, 201):
                ct = response.headers.get("Content-Type", "")
                if ("application/pdf" in ct) or response.content.startswith(b"%PDF"):
                    return response.content
            
            print(f"API-Fehler: Status {response.status_code}")
            return None
            
        except Exception as e:
            print(f"Fehler beim API-Call: {e}")
            return None
    
    def _sortiere_pdf_seiten(
        self,
        input_pdf_bytes: bytes,
        pages_per_student: int = 4
    ) -> Optional[bytes]:
        """Sortiert PDF-Seiten: 1-2-3-4 → 4-1-2-3 (für Duplex-Druck)"""
        
        try:
            reader = PdfReader(io.BytesIO(input_pdf_bytes))
            writer = PdfWriter()
            total_pages = len(reader.pages)
            
            total_students = total_pages // pages_per_student
            
            # Für jeden Schüler: 4-1-2-3
            for student in range(total_students):
                base = student * pages_per_student
                order = [base + 3, base + 0, base + 1, base + 2]
                
                for p in order:
                    if p < total_pages:
                        writer.add_page(reader.pages[p])
            
            out = io.BytesIO()
            writer.write(out)
            return out.getvalue()
            
        except Exception as e:
            print(f"Fehler beim Umsortieren: {e}")
            return None
    
    @staticmethod
    def _tex_escape(s: str) -> str:
        """Escape LaTeX-Sonderzeichen"""
        if s is None:
            return ""
        
        repl = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        return "".join(repl.get(ch, ch) for ch in s)
    
    # ========================================================================
    # AUFGABEN-PREVIEW (BESTEHEND)
    # ========================================================================
    
    def generate_aufgabe_preview_png(self, aufgabe: Dict, mit_loesung: bool = False, 
                                     dpi: int = 150, aufgabe_id: int = None) -> bytes:
        """
        Generiert Preview als PNG (gecroppt) mit Grafik-Support
        
        Args:
            aufgabe: Dict mit 'latex_code'
            mit_loesung: True = Lösungen anzeigen
            dpi: Auflösung (150 = gut, 200 = schärfer)
            aufgabe_id: Optional - für Grafik-Laden aus DB
        
        Returns:
            PNG als bytes (gecroppt)
        """
        # Lade Grafiken als API-Resources (Base64)
        grafik_resources = []
        if aufgabe_id and self.db_path:
            grafik_resources = self.lade_grafiken_als_resources(aufgabe_id)
        
        # Passe LaTeX-Code an (Namen → Dateinamen mit Extension)
        aufgabe = aufgabe.copy()
        if aufgabe_id and self.db_path:
            aufgabe['latex_code'] = self.ersetze_grafik_namen_api(
                aufgabe['latex_code'], 
                aufgabe_id
            )
        
        # Baue LaTeX
        latex_code = self.build_aufgabe_latex(aufgabe, mit_loesung)
        
        # Sende an API mit Grafik-Resources
        pdf_normal = self.send_to_api(latex_code, resources=grafik_resources)
        
        # PDF → PNG + Trim
        png_data = self.pdf_to_png_trimmed(pdf_normal, dpi=dpi)
        
        return png_data
    
    def pdf_to_png_trimmed(self, pdf_data: bytes, dpi: int = 150) -> bytes:
        """
        Konvertiert PDF zu PNG und trimmt weißen Rand
        
        Args:
            pdf_data: PDF als bytes
            dpi: Auflösung
        
        Returns:
            PNG als bytes (gecroppt)
        """
        try:
            from pdf2image import convert_from_bytes
            from PIL import Image, ImageChops
            
            # PDF → PNG
            images = convert_from_bytes(pdf_data, dpi=dpi, first_page=1, last_page=1)
            
            if not images:
                raise Exception("Keine Seiten im PDF")
            
            image = images[0]
            
            # Automatisch trimmen
            bg = Image.new(image.mode, image.size, (255, 255, 255))
            diff = ImageChops.difference(image, bg)
            if diff.mode != 'L':
                diff = diff.convert('L')
            bbox = diff.getbbox()
            
            if bbox:
                padding = 15
                x1 = max(0, bbox[0] - padding)
                y1 = max(0, bbox[1] - padding)
                x2 = min(image.width, bbox[2] + padding)
                y2 = min(image.height, bbox[3] + padding)
                
                image_cropped = image.crop((x1, y1, x2, y2))
            else:
                image_cropped = image
            
            # Als PNG speichern
            png_buffer = io.BytesIO()
            image_cropped.save(png_buffer, format='PNG')
            png_buffer.seek(0)
            
            return png_buffer.read()
            
        except ImportError:
            raise Exception("Benötigte Pakete fehlen. Installiere: pip install pdf2image pillow")
    
    def build_aufgabe_latex(self, aufgabe: Dict, mit_loesung: bool = False) -> str:
        """
        Baut vollständiges LaTeX-Dokument für eine Aufgabe
        
        Args:
            aufgabe: Dict mit 'latex_code'
            mit_loesung: True = Lösungen anzeigen
        
        Returns:
            LaTeX-Code als String
        """
        latex = r"\documentclass[a4paper,12pt]{exam}" + "\n"
        latex += self.header
        
        if mit_loesung:
            latex += r"\printanswers" + "\n"
        
        latex += r"\begin{document}" + "\n\n"
        
        latex += r"\begin{questions}" + "\n"
        latex += aufgabe.get('latex_code', '') + "\n\n"
        latex += r"\end{questions}" + "\n"
        
        latex += r"\end{document}"
        
        return latex
    
    def lade_grafiken_als_resources(self, aufgabe_id: int) -> List[Dict]:
        """
        Lädt alle Grafiken einer Aufgabe aus DB als API-Resources (Base64)
        
        Args:
            aufgabe_id: ID der Aufgabe
        
        Returns:
            Liste von Dicts: [{"path": "bild.png", "file": "base64_string"}]
        """
        if not self.db_path or not aufgabe_id:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT latex_name, grafik_blob, dateityp
                FROM aufgaben_grafiken
                WHERE aufgabe_id = ?
            """, (aufgabe_id,))
            
            resources = []
            
            for row in cursor.fetchall():
                latex_name, blob, typ = row
                
                ext = typ.lower()
                if ext == 'jpg':
                    ext = 'jpeg'
                
                filename = f"{latex_name}.{ext}"
                b64 = base64.b64encode(blob).decode('utf-8')
                
                resources.append({
                    "path": filename,
                    "file": b64  # "file" für Base64!
                })
            
            conn.close()
            return resources
            
        except Exception:
            return []
    
    def ersetze_grafik_namen_api(self, latex_code: str, aufgabe_id: int) -> str:
        """
        Fügt Dateiendungen zu Grafik-Namen im LaTeX-Code hinzu
        
        Args:
            latex_code: LaTeX-Code mit Grafik-Referenzen
            aufgabe_id: ID der Aufgabe
        
        Returns:
            LaTeX-Code mit vollständigen Dateinamen
        """
        if not self.db_path or not aufgabe_id:
            return latex_code
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT latex_name, dateityp
                FROM aufgaben_grafiken
                WHERE aufgabe_id = ?
            """, (aufgabe_id,))
            
            name_map = {}
            for row in cursor.fetchall():
                name, typ = row
                ext = typ.lower()
                if ext == 'jpg':
                    ext = 'jpeg'
                name_map[name] = f"{name}.{ext}"
            
            conn.close()
            
            pattern = r'\\includegraphics(\[[^\]]*\])?\{([^}]+)\}'
            
            def replacer(match):
                optionen = match.group(1) or ''
                name = match.group(2)
                
                if name in name_map:
                    return f'\\includegraphics{optionen}{{{name_map[name]}}}'
                else:
                    return match.group(0)
            
            latex_code = re.sub(pattern, replacer, latex_code)
            return latex_code
            
        except Exception:
            return latex_code
    
    def send_to_api(self, latex_code: str, resources: List[Dict] = None) -> bytes:
        """
        Sendet LaTeX an API mit optionalen Grafik-Resources
        
        Args:
            latex_code: LaTeX-Code
            resources: Liste von zusätzlichen Resources (Grafiken)
        
        Returns:
            PDF als bytes
        """
        payload_resources = [{"main": True, "path": "main.tex", "content": latex_code}]
        
        if resources:
            payload_resources.extend(resources)
        
        payload = {
            "compiler": "pdflatex",
            "resources": payload_resources
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/pdf"
        }
        
        try:
            response = requests.post(self.api_url, data=json.dumps(payload), 
                                    headers=headers, timeout=30)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"LaTeX-API Error: HTTP {response.status_code}\n{response.text}")
            
            return response.content
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network Error: {str(e)}")
    
    def get_default_header(self) -> str:
        """Standard-Header für alle PDFs (MARGIN = 1cm wie Klausuren!)"""
        return r"""
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[ngerman]{babel}
\usepackage{graphicx}
\usepackage{qrcode}
\usepackage{tikz}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage[margin=1cm]{geometry}
\usepackage{multicol}
\usepackage{siunitx}
\usepackage{ulem}
\usepackage{stmaryrd}
\usetikzlibrary{calc}
\setlength{\gridsize}{5.154639mm}
\setlength{\gridlinewidth}{0.1pt}
\usetikzlibrary{angles,quotes,arrows}
\usepackage{pgfplots}
\pgfplotsset{compat=1.15}
\usepackage{mathrsfs}
\usepackage[gen]{eurosym}
\usepackage{enumitem}
\usepackage{changepage}

\newenvironment{solgrid}[1][2cm]{%
  \vspace{0.3em}
  \begin{adjustwidth}{-3em}{-3em}
    \begin{solutionorgrid}[#1]
}{%
    \end{solutionorgrid}
  \end{adjustwidth}
}

\pagestyle{empty}

\tikzset{
  xyz/.style={x={(-.385cm,-.385cm)},y={(1cm,0cm)},z={(0cm,1cm)}},
  flaeche/.style={fill=white!10,opacity=.5},
}

\renewcommand{\solutiontitle}{Lösung: }
"""
