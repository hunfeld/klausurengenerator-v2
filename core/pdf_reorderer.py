"""
PDF-Reorderer
=============

Sortiert PDF-Seiten für optimalen Duplex-Druck um (4-1-2-3 Muster)
"""

from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from typing import List, Optional


class PDFReorderer:
    """
    Sortiert PDF-Seiten für Duplex-Druck um
    
    Standard-Muster für 4-seitige Klausuren:
    - Original: Seite 1, 2, 3, 4
    - Umsortiert: Seite 4, 1, 2, 3
    
    Beim Duplex-Druck (beidseitig) ergibt das:
    - Vorderseite Blatt 1: Seite 4
    - Rückseite Blatt 1: Seite 1
    - Vorderseite Blatt 2: Seite 2
    - Rückseite Blatt 2: Seite 3
    
    Beim Falten in der Mitte: Perfekte Reihenfolge!
    """
    
    def __init__(self):
        self.page_pattern = [3, 0, 1, 2]  # 4-1-2-3 (0-indiziert)
        
    def reorder_pdf(
        self, 
        input_pdf: str, 
        output_pdf: str,
        pattern: Optional[List[int]] = None
    ) -> bool:
        """
        Sortiert PDF-Seiten um
        
        Args:
            input_pdf: Pfad zur Input-PDF
            output_pdf: Pfad zur Output-PDF
            pattern: Optional - eigenes Sortier-Muster (0-indiziert)
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        
        try:
            # PDF laden
            reader = PdfReader(input_pdf)
            total_pages = len(reader.pages)
            
            print(f"PDF laden: {total_pages} Seiten")
            
            # Pattern verwenden
            if pattern is None:
                pattern = self.page_pattern
            
            # Prüfe ob Pattern passt
            if total_pages % len(pattern) != 0:
                print(f"⚠️ Warnung: {total_pages} Seiten passen nicht zu Pattern-Länge {len(pattern)}")
            
            # Neue PDF erstellen
            writer = PdfWriter()
            
            # Seiten umsortieren
            num_blocks = total_pages // len(pattern)
            remainder = total_pages % len(pattern)
            
            for block in range(num_blocks):
                for pattern_idx in pattern:
                    page_idx = block * len(pattern) + pattern_idx
                    if page_idx < total_pages:
                        writer.add_page(reader.pages[page_idx])
                        print(f"  Block {block+1}: Füge Seite {page_idx+1} hinzu")
            
            # Rest-Seiten anhängen (falls vorhanden)
            if remainder > 0:
                print(f"⚠️ {remainder} Rest-Seiten werden unverändert angehängt")
                for i in range(num_blocks * len(pattern), total_pages):
                    writer.add_page(reader.pages[i])
            
            # PDF speichern
            output_path = Path(output_pdf)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_pdf, 'wb') as f:
                writer.write(f)
            
            print(f"✅ PDF umsortiert: {output_pdf}")
            print(f"   {total_pages} Seiten → {len(writer.pages)} Seiten")
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Umsortieren: {e}")
            return False
    
    def reorder_pdf_bytes(
        self,
        pdf_bytes: bytes,
        pattern: Optional[List[int]] = None
    ) -> Optional[bytes]:
        """
        Sortiert PDF-Bytes um (ohne Datei-IO)
        
        Args:
            pdf_bytes: PDF als bytes
            pattern: Optional - eigenes Sortier-Muster
            
        Returns:
            Umsortierte PDF als bytes, oder None bei Fehler
        """
        
        try:
            from io import BytesIO
            
            # PDF aus bytes laden
            reader = PdfReader(BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            
            # Pattern verwenden
            if pattern is None:
                pattern = self.page_pattern
            
            # Neue PDF erstellen
            writer = PdfWriter()
            
            # Seiten umsortieren
            num_blocks = total_pages // len(pattern)
            
            for block in range(num_blocks):
                for pattern_idx in pattern:
                    page_idx = block * len(pattern) + pattern_idx
                    if page_idx < total_pages:
                        writer.add_page(reader.pages[page_idx])
            
            # Rest-Seiten
            remainder = total_pages % len(pattern)
            if remainder > 0:
                for i in range(num_blocks * len(pattern), total_pages):
                    writer.add_page(reader.pages[i])
            
            # Als bytes zurückgeben
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            
            return output.read()
            
        except Exception as e:
            print(f"❌ Fehler beim Umsortieren (bytes): {e}")
            return None
    
    def reorder_multiple_pdfs(
        self,
        input_pdfs: List[str],
        output_pdf: str,
        pattern: Optional[List[int]] = None
    ) -> bool:
        """
        Sortiert mehrere PDFs um und fügt sie zusammen
        
        Args:
            input_pdfs: Liste von Input-PDF-Pfaden
            output_pdf: Pfad zur Output-PDF
            pattern: Optional - Sortier-Muster
            
        Returns:
            True bei Erfolg
        """
        
        try:
            writer = PdfWriter()
            
            if pattern is None:
                pattern = self.page_pattern
            
            for input_pdf in input_pdfs:
                print(f"Verarbeite: {input_pdf}")
                
                reader = PdfReader(input_pdf)
                total_pages = len(reader.pages)
                num_blocks = total_pages // len(pattern)
                
                # Seiten umsortieren
                for block in range(num_blocks):
                    for pattern_idx in pattern:
                        page_idx = block * len(pattern) + pattern_idx
                        if page_idx < total_pages:
                            writer.add_page(reader.pages[page_idx])
                
                # Rest-Seiten
                remainder = total_pages % len(pattern)
                if remainder > 0:
                    for i in range(num_blocks * len(pattern), total_pages):
                        writer.add_page(reader.pages[i])
            
            # Speichern
            output_path = Path(output_pdf)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_pdf, 'wb') as f:
                writer.write(f)
            
            print(f"✅ {len(input_pdfs)} PDFs zusammengeführt: {output_pdf}")
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Zusammenführen: {e}")
            return False
    
    def validate_pdf(self, pdf_path: str) -> tuple[bool, int]:
        """
        Validiert PDF und gibt Seitenzahl zurück
        
        Args:
            pdf_path: Pfad zur PDF
            
        Returns:
            (is_valid, page_count)
        """
        
        try:
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            return True, page_count
        except Exception as e:
            print(f"❌ Ungültige PDF: {e}")
            return False, 0


def reorder_for_duplex_print(input_pdf: str, output_pdf: str) -> bool:
    """
    Convenience-Funktion für Standard-Duplex-Druck
    
    Args:
        input_pdf: Input-PDF-Pfad
        output_pdf: Output-PDF-Pfad
        
    Returns:
        True bei Erfolg
    """
    reorderer = PDFReorderer()
    return reorderer.reorder_pdf(input_pdf, output_pdf)
