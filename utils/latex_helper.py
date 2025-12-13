"""
LaTeX-Hilfsfunktionen
=====================

Escaping und Formatierung für LaTeX
"""

import re
from typing import Dict


# Zeichen die in LaTeX escaped werden müssen
LATEX_SPECIAL_CHARS = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}',
    '\\': r'\textbackslash{}',
}


def escape_latex(text: str) -> str:
    """
    Escape Sonderzeichen für LaTeX
    
    Args:
        text: Text mit potentiellen Sonderzeichen
        
    Returns:
        Escaped Text
    """
    if not text:
        return ""
    
    # Backslash muss zuerst escaped werden
    text = text.replace('\\', r'\textbackslash{}')
    
    # Dann die anderen Zeichen
    for char, replacement in LATEX_SPECIAL_CHARS.items():
        if char != '\\':  # Backslash schon behandelt
            text = text.replace(char, replacement)
    
    return text


def cm_to_pt(cm: float) -> float:
    """
    Zentimeter zu Points konvertieren
    
    Args:
        cm: Länge in Zentimetern
        
    Returns:
        Länge in Points (pt)
    """
    return cm * 28.3465


def vspace_to_stretch(vspace_cm: float, total_cm: float) -> float:
    """
    \\vspace zu \\stretch konvertieren
    
    Args:
        vspace_cm: Gewünschter Platz in cm
        total_cm: Gesamt verfügbarer Platz in cm
        
    Returns:
        Stretch-Faktor
    """
    if total_cm <= 0:
        return 1.0
    
    return vspace_cm / total_cm


def format_datum_deutsch(datum: str) -> str:
    """
    Datum in deutsches Format
    
    Args:
        datum: Datum in verschiedenen Formaten
        
    Returns:
        DD.MM.YYYY
    """
    # Entferne Bindestriche/Slashes
    datum = datum.replace('-', '.').replace('/', '.')
    
    parts = datum.split('.')
    
    if len(parts) == 3:
        # Prüfe ob bereits DD.MM.YYYY
        if len(parts[0]) <= 2:
            return datum  # Schon korrekt
        # Sonst YYYY.MM.DD -> DD.MM.YYYY
        else:
            return f"{parts[2]}.{parts[1]}.{parts[0]}"
    
    return datum


def sanitize_filename(filename: str) -> str:
    """
    Dateiname bereinigen (nur sichere Zeichen)
    
    Args:
        filename: Original-Dateiname
        
    Returns:
        Bereinigter Dateiname
    """
    # Erlaube nur: Buchstaben, Zahlen, -, _
    filename = re.sub(r'[^a-zA-Z0-9_\-.]', '_', filename)
    
    # Mehrfache Unterstriche entfernen
    filename = re.sub(r'_+', '_', filename)
    
    return filename


def generate_qr_code_data(kasusid: int, schueler_id: int) -> str:
    """
    QR-Code-Daten generieren
    
    Args:
        kasusid: KasusID (5-stellig)
        schueler_id: Schüler-ID
        
    Returns:
        QR-Code-String
    """
    return f"{kasusid:05d}-{schueler_id:04d}"
