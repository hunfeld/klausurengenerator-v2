#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaTeX Generator für Klausurengenerator
Version 2.4.3: Mit Grafik-Support via API (Base64-Upload)

FINAL VERSION - Produktiv, ohne Debug-Meldungen

Prozess:
1. Normale A4-PDF generieren (identisch zur Klausur)
2. PDF → PNG konvertieren
3. PNG automatisch trimmen (weißen Rand entfernen)
4. Optional: PNG → PDF zurück (oder PNG als Preview verwenden)
"""

import requests
import json
from pathlib import Path
import sqlite3
from typing import Optional, Dict, List, Tuple
import hashlib
import io
import base64
import re


class LaTeXGenerator:
    """
    Service-Klasse für LaTeX-PDF-Generierung via latex.ytotech.com
    """
    
    def __init__(self, api_url: str = "https://latex.ytotech.com/builds/sync", db_path: str = None):
        self.api_url = api_url
        self.header = self.get_default_header()
        self.db_path = db_path or (Path(__file__).parent.parent / 'sus.db')
    
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
        """Standard-Header für alle PDFs"""
        return r"""
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[ngerman]{babel}
\usepackage{graphicx}
\usepackage{qrcode}
\usepackage{tikz}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage[margin=2cm]{geometry}
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
