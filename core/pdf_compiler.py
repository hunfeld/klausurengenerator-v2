"""
PDF-Compiler
============

Kompiliert LaTeX zu PDF via API
"""

import requests
from typing import Optional
from pathlib import Path


class PDFCompiler:
    """Kompiliert LaTeX-Code zu PDF"""
    
    # LaTeX-API Endpoint
    API_URL = "https://latex.ytotech.com/builds/sync"
    
    def __init__(self):
        self.timeout = 120  # 2 Minuten Timeout für große Dokumente
        
    def compile_latex(self, latex_code: str) -> Optional[bytes]:
        """
        Kompiliert LaTeX-Code zu PDF
        
        Args:
            latex_code: LaTeX-Source-Code
            
        Returns:
            PDF als bytes, oder None bei Fehler
        """
        
        try:
            print(f"Kompiliere LaTeX ({len(latex_code)} Zeichen)...")
            
            # API-Request
            response = requests.post(
                self.API_URL,
                json={
                    "compiler": "pdflatex",
                    "resources": [
                        {
                            "main": True,
                            "file": "main.tex",
                            "content": latex_code
                        }
                    ]
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                print("✅ PDF erfolgreich kompiliert!")
                return response.content
            else:
                print(f"❌ API-Fehler: {response.status_code}")
                print(f"Response: {response.text[:500]}")  # Erste 500 Zeichen
                return None
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout nach {self.timeout} Sekunden")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Netzwerk-Fehler: {e}")
            return None
        except Exception as e:
            print(f"❌ Fehler bei PDF-Kompilierung: {e}")
            return None
            
    def compile_to_file(self, latex_code: str, output_path: str) -> bool:
        """
        Kompiliert LaTeX und speichert direkt als Datei
        
        Args:
            latex_code: LaTeX-Source-Code
            output_path: Pfad für Output-PDF
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        
        pdf_data = self.compile_latex(latex_code)
        
        if pdf_data:
            try:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'wb') as f:
                    f.write(pdf_data)
                
                print(f"✅ PDF gespeichert: {output_path}")
                return True
                
            except Exception as e:
                print(f"❌ Fehler beim Speichern: {e}")
                return False
        else:
            return False
    
    def validate_latex(self, latex_code: str) -> tuple[bool, str]:
        """
        Validiert LaTeX-Code (Basis-Check)
        
        Args:
            latex_code: LaTeX-Code zu prüfen
            
        Returns:
            (is_valid, error_message)
        """
        
        # Basis-Checks
        if not latex_code.strip():
            return False, "LaTeX-Code ist leer"
        
        if '\\documentclass' not in latex_code:
            return False, "Kein \\documentclass gefunden"
        
        if '\\begin{document}' not in latex_code:
            return False, "Kein \\begin{document} gefunden"
        
        if '\\end{document}' not in latex_code:
            return False, "Kein \\end{document} gefunden"
        
        # Prüfe Balance von begin/end
        begins = latex_code.count('\\begin{')
        ends = latex_code.count('\\end{')
        
        if begins != ends:
            return False, f"Ungleiche Anzahl von \\begin ({begins}) und \\end ({ends})"
        
        return True, ""


def compile_latex_to_pdf(latex_code: str, output_path: str = None) -> Optional[bytes]:
    """
    Convenience-Funktion für einfache Kompilierung
    
    Args:
        latex_code: LaTeX-Source
        output_path: Optional - wenn angegeben, wird PDF gespeichert
        
    Returns:
        PDF als bytes (oder None bei Fehler)
    """
    compiler = PDFCompiler()
    
    if output_path:
        success = compiler.compile_to_file(latex_code, output_path)
        if success:
            with open(output_path, 'rb') as f:
                return f.read()
        return None
    else:
        return compiler.compile_latex(latex_code)
