"""
LaTeX Rendering Utilities
==========================

Kompiliert LaTeX-Code zu PNG mit Auto-Cropping
"""

import os
import tempfile
import subprocess
from pathlib import Path
from PIL import Image
from typing import Optional


def render_latex_to_png(
    latex_code: str,
    output_path: Optional[str] = None,
    dpi: int = 150,
    crop: bool = True
) -> Optional[str]:
    """
    Rendert LaTeX-Code zu PNG
    
    Args:
        latex_code: LaTeX-Code der Aufgabe
        output_path: Optionaler Pfad für PNG (Standard: temp file)
        dpi: DPI für Rendering (Standard: 150)
        crop: Ränder automatisch entfernen (Standard: True)
        
    Returns:
        Pfad zur generierten PNG-Datei oder None bei Fehler
    """
    
    # Temporäres Verzeichnis erstellen
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # LaTeX-Dokument erstellen
        tex_content = create_latex_document(latex_code)
        tex_file = tmpdir / "aufgabe.tex"
        
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(tex_content)
        
        # LaTeX kompilieren (pdflatex)
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'aufgabe.tex'],
                cwd=tmpdir,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"pdflatex Fehler:\n{result.stdout.decode('utf-8', errors='ignore')}")
                return None
                
        except FileNotFoundError:
            print("FEHLER: pdflatex nicht gefunden! Bitte LaTeX installieren.")
            return None
        except subprocess.TimeoutExpired:
            print("FEHLER: LaTeX-KompilierungTimeout")
            return None
        except Exception as e:
            print(f"FEHLER beim Kompilieren: {e}")
            return None
        
        # PDF zu PNG konvertieren
        pdf_file = tmpdir / "aufgabe.pdf"
        
        if not pdf_file.exists():
            print("FEHLER: PDF wurde nicht erstellt")
            return None
        
        # PDF → PNG mit Ghostscript
        png_file = tmpdir / "aufgabe.png"
        
        try:
            subprocess.run(
                [
                    'gswin64c',  # Windows
                    '-dNOPAUSE',
                    '-dBATCH',
                    '-sDEVICE=png16m',
                    f'-r{dpi}',
                    f'-sOutputFile={png_file}',
                    str(pdf_file)
                ],
                capture_output=True,
                timeout=10
            )
        except FileNotFoundError:
            # Versuche gs (Linux/Mac)
            try:
                subprocess.run(
                    [
                        'gs',
                        '-dNOPAUSE',
                        '-dBATCH',
                        '-sDEVICE=png16m',
                        f'-r{dpi}',
                        f'-sOutputFile={png_file}',
                        str(pdf_file)
                    ],
                    capture_output=True,
                    timeout=10
                )
            except Exception as e:
                print(f"FEHLER: Ghostscript nicht gefunden: {e}")
                return None
        
        if not png_file.exists():
            print("FEHLER: PNG wurde nicht erstellt")
            return None
        
        # Cropping
        if crop:
            try:
                img = Image.open(png_file)
                img = autocrop_image(img)
                img.save(png_file)
            except Exception as e:
                print(f"FEHLER beim Croppen: {e}")
        
        # PNG in finalen Pfad kopieren
        if output_path is None:
            # Temporäre Datei in system temp
            import uuid
            output_path = Path(tempfile.gettempdir()) / f"latex_{uuid.uuid4().hex}.png"
        
        # Kopieren
        import shutil
        shutil.copy(png_file, output_path)
        
        return str(output_path)


def create_latex_document(latex_code: str) -> str:
    """
    Erstellt vollständiges LaTeX-Dokument aus Aufgaben-Code
    
    Args:
        latex_code: LaTeX-Code der Aufgabe
        
    Returns:
        Vollständiges LaTeX-Dokument
    """
    
    template = r"""
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[ngerman]{babel}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{geometry}
\geometry{a4paper, margin=1cm}

\pagestyle{empty}

\begin{document}

""" + latex_code + r"""

\end{document}
"""
    
    return template


def autocrop_image(img: Image.Image, threshold: int = 250) -> Image.Image:
    """
    Entfernt weiße Ränder automatisch
    
    Args:
        img: PIL Image
        threshold: Schwellwert für Weiß (0-255)
        
    Returns:
        Gecropptes Image
    """
    
    # Konvertiere zu RGB falls nötig
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Pixel-Daten
    pixels = img.load()
    width, height = img.size
    
    # Finde Grenzen
    left = width
    right = 0
    top = height
    bottom = 0
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # Nicht-weiß?
            if r < threshold or g < threshold or b < threshold:
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)
    
    # Falls nichts gefunden → Original zurückgeben
    if left >= right or top >= bottom:
        return img
    
    # Padding hinzufügen (10px)
    padding = 10
    left = max(0, left - padding)
    right = min(width, right + padding)
    top = max(0, top - padding)
    bottom = min(height, bottom + padding)
    
    # Croppen
    return img.crop((left, top, right, bottom))


def test_latex_installation() -> dict:
    """
    Testet ob LaTeX und Ghostscript installiert sind
    
    Returns:
        Dictionary mit Status-Informationen
    """
    
    status = {
        'pdflatex': False,
        'ghostscript': False,
        'ready': False
    }
    
    # Test pdflatex
    try:
        result = subprocess.run(
            ['pdflatex', '--version'],
            capture_output=True,
            timeout=5
        )
        status['pdflatex'] = result.returncode == 0
    except:
        pass
    
    # Test Ghostscript
    for gs_cmd in ['gswin64c', 'gs']:
        try:
            result = subprocess.run(
                [gs_cmd, '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                status['ghostscript'] = True
                break
        except:
            pass
    
    status['ready'] = status['pdflatex'] and status['ghostscript']
    
    return status


if __name__ == '__main__':
    # Test
    status = test_latex_installation()
    print(f"LaTeX Installation Status:")
    print(f"  pdflatex: {'✓' if status['pdflatex'] else '✗'}")
    print(f"  Ghostscript: {'✓' if status['ghostscript'] else '✗'}")
    print(f"  Ready: {'✓' if status['ready'] else '✗'}")
    
    if status['ready']:
        # Test-Rendering
        test_code = r"""
\textbf{Aufgabe 1:} Berechne $\int_0^1 x^2 \, dx$

\begin{enumerate}
    \item Stammfunktion bestimmen
    \item Grenzen einsetzen
    \item Ergebnis angeben
\end{enumerate}
"""
        
        print("\nRendering Test...")
        png_path = render_latex_to_png(test_code)
        
        if png_path:
            print(f"✓ PNG erstellt: {png_path}")
        else:
            print("✗ Rendering fehlgeschlagen")
