"""
LaTeX Helper Functions
======================

Hilfs-Funktionen für LaTeX-Generierung
"""

import re
from datetime import datetime


def escape_latex(text: str) -> str:
    """
    Escaped LaTeX-Sonderzeichen in Text
    
    Args:
        text: Text zum Escapen
        
    Returns:
        Escaped Text
    """
    
    if not text:
        return ""
    
    # LaTeX-Sonderzeichen
    replacements = {
        '\\': r'\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '$': r'\$',
        '&': r'\&',
        '%': r'\%',
        '#': r'\#',
        '_': r'\_',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    
    return result


def format_datum_deutsch(datum_str: str) -> str:
    """
    Formatiert Datum im deutschen Format
    
    Args:
        datum_str: Datum als String (YYYY-MM-DD oder DD.MM.YYYY)
        
    Returns:
        Datum im Format "TT.MM.YYYY"
    """
    
    if not datum_str:
        return ""
    
    try:
        # Wenn bereits im deutschen Format
        if '.' in datum_str:
            return datum_str
        
        # Wenn im ISO-Format (YYYY-MM-DD)
        if '-' in datum_str:
            parts = datum_str.split('-')
            if len(parts) == 3:
                return f"{parts[2]}.{parts[1]}.{parts[0]}"
        
        return datum_str
        
    except Exception:
        return datum_str


def generate_qr_code_data(kasusid: int, schueler_id: int) -> str:
    """
    Generiert QR-Code-Daten für Schüler
    
    Args:
        kasusid: Klausur-SuS-ID (eindeutige Klausur-Nummer)
        schueler_id: Schüler-ID
        
    Returns:
        QR-Code-String
    """
    
    # Format: KASUSID-SCHUELERID
    # Beispiel: "100001-12345"
    return f"{kasusid}-{schueler_id}"


def sanitize_filename(filename: str) -> str:
    """
    Bereinigt Dateinamen von ungültigen Zeichen
    
    Args:
        filename: Dateiname
        
    Returns:
        Bereinigter Dateiname
    """
    
    # Ersetze ungültige Zeichen
    invalid_chars = r'[<>:"/\\|?*]'
    clean = re.sub(invalid_chars, '_', filename)
    
    # Entferne führende/trailing Leerzeichen und Punkte
    clean = clean.strip('. ')
    
    # Max 255 Zeichen
    if len(clean) > 255:
        clean = clean[:255]
    
    return clean


def cm_to_pt(cm: float) -> float:
    """
    Konvertiert Zentimeter zu Points (LaTeX-Einheit)
    
    Args:
        cm: Zentimeter
        
    Returns:
        Points
    """
    
    # 1 cm = 28.3465 pt
    return cm * 28.3465


def pt_to_cm(pt: float) -> float:
    """
    Konvertiert Points zu Zentimetern
    
    Args:
        pt: Points
        
    Returns:
        Zentimeter
    """
    
    return pt / 28.3465


def format_punktzahl(punkte: int, singular: str = "Punkt", plural: str = "Punkte") -> str:
    """
    Formatiert Punktzahl mit korrekter Singular/Plural-Form
    
    Args:
        punkte: Anzahl Punkte
        singular: Singular-Form
        plural: Plural-Form
        
    Returns:
        Formatierte Punktzahl
    """
    
    if punkte == 1:
        return f"{punkte} {singular}"
    else:
        return f"{punkte} {plural}"


def split_aufgabentext(text: str, max_length: int = 1000) -> list[str]:
    """
    Teilt langen Aufgabentext in Chunks auf
    
    Args:
        text: Aufgabentext
        max_length: Maximale Länge pro Chunk
        
    Returns:
        Liste von Text-Chunks
    """
    
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Teile bei Absätzen
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_length:
            if current_chunk:
                current_chunk += '\n\n'
            current_chunk += para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def validate_latex_code(latex_code: str) -> tuple[bool, str]:
    """
    Validiert LaTeX-Code (Basis-Checks)
    
    Args:
        latex_code: LaTeX-Code
        
    Returns:
        (is_valid, error_message)
    """
    
    if not latex_code.strip():
        return False, "LaTeX-Code ist leer"
    
    # Prüfe Balance von geschweiften Klammern
    open_braces = latex_code.count('{')
    close_braces = latex_code.count('}')
    
    if open_braces != close_braces:
        return False, f"Ungleiche Anzahl von Klammern: {open_braces} öffnende, {close_braces} schließende"
    
    # Prüfe Balance von $-Zeichen (Mathe-Mode)
    dollar_count = latex_code.count('$')
    
    if dollar_count % 2 != 0:
        return False, f"Ungerade Anzahl von $ (Mathe-Mode): {dollar_count}"
    
    # Prüfe Balance von \\[ und \\]
    display_math_open = latex_code.count(r'\[')
    display_math_close = latex_code.count(r'\]')
    
    if display_math_open != display_math_close:
        return False, f"Ungleiche Anzahl von \\[ ({display_math_open}) und \\] ({display_math_close})"
    
    return True, ""


def generate_latex_table(data: list[list[str]], header: list[str] = None) -> str:
    """
    Generiert LaTeX-Tabellen-Code
    
    Args:
        data: Daten als 2D-Liste
        header: Optional - Tabellen-Header
        
    Returns:
        LaTeX-Code für Tabelle
    """
    
    if not data:
        return ""
    
    num_cols = len(data[0])
    
    lines = []
    lines.append(r"\begin{tabular}{" + "|".join(["l"] * num_cols) + "}")
    lines.append(r"\hline")
    
    if header:
        lines.append(" & ".join([escape_latex(h) for h in header]) + r" \\")
        lines.append(r"\hline")
    
    for row in data:
        lines.append(" & ".join([escape_latex(str(cell)) for cell in row]) + r" \\")
    
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    
    return "\n".join(lines)


def wrap_in_minipage(content: str, width: str = r"\textwidth") -> str:
    """
    Wrapped Content in Minipage (für besseres Layout)
    
    Args:
        content: LaTeX-Content
        width: Breite der Minipage
        
    Returns:
        Minipage-LaTeX-Code
    """
    
    return f"\\begin{{minipage}}{{{width}}}\n{content}\n\\end{{minipage}}"


def create_vspace(cm: float) -> str:
    """
    Erstellt vertikalen Abstand
    
    Args:
        cm: Abstand in Zentimetern
        
    Returns:
        LaTeX-Code für vspace
    """
    
    return f"\\vspace{{{cm}cm}}"


def create_hspace(cm: float) -> str:
    """
    Erstellt horizontalen Abstand
    
    Args:
        cm: Abstand in Zentimetern
        
    Returns:
        LaTeX-Code für hspace
    """
    
    return f"\\hspace{{{cm}cm}}"
