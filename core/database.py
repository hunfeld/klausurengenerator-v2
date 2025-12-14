"""
Datenbank-Verwaltung
====================

SQLite-Anbindung für sus.db - v1.0.6 update_klausur() hinzugefügt
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class Database:
    """Zentrale Datenbank-Klasse"""
    
    def __init__(self, db_path: str = "database/sus.db"):
        """
        Initialisiere Datenbankverbindung
        
        Args:
            db_path: Pfad zur SQLite-Datenbank
        """
        self.db_path = Path(db_path)
        
        # Prüfe ob Datenbank existiert
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Datenbank nicht gefunden: {self.db_path}\n"
                f"Bitte kopiere sus.db in den Ordner database/"
            )
    
    @contextmanager
    def get_connection(self):
        """
        Context Manager für Datenbankverbindung
        
        Verwendung:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ...")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Zugriff über Spaltennamen
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Führe SELECT-Query aus und gib Ergebnisse zurück
        
        Args:
            query: SQL-Query
            params: Parameter für Query (?, ?, ...)
            
        Returns:
            Liste von Dictionaries (Spaltenname -> Wert)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Konvertiere sqlite3.Row zu Dict
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Führe INSERT/UPDATE/DELETE aus
        
        Args:
            query: SQL-Query
            params: Parameter für Query
            
        Returns:
            Anzahl betroffener Zeilen
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Führe INSERT aus und gib neue ID zurück
        
        Args:
            query: SQL-Query
            params: Parameter für Query
            
        Returns:
            ID des neu eingefügten Datensatzes
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    # ============================================================
    # SCHULEN
    # ============================================================
    
    def get_schulen(self) -> List[Dict[str, Any]]:
        """Alle Schulen laden"""
        return self.execute_query(
            "SELECT id, kuerzel, name FROM schulen ORDER BY name"
        )
    
    def get_schule_by_kuerzel(self, kuerzel: str) -> Optional[Dict[str, Any]]:
        """Schule anhand Kürzel laden"""
        results = self.execute_query(
            "SELECT * FROM schulen WHERE kuerzel = ?",
            (kuerzel,)
        )
        return results[0] if results else None
    
    def get_logo_for_school(self, schule_kuerzel: str) -> Optional[bytes]:
        """
        Logo einer Schule laden (BLOB)
        
        Args:
            schule_kuerzel: z.B. 'gyd', 'obs', 'gympap'
            
        Returns:
            Logo als Bytes oder None
        """
        results = self.execute_query(
            "SELECT logo FROM schulen WHERE kuerzel = ?",
            (schule_kuerzel,)
        )
        
        if results and results[0]['logo']:
            return results[0]['logo']
        return None
    
    # ============================================================
    # SCHÜLER
    # ============================================================
    
    def get_schueler_by_klasse(
        self, 
        schuljahr: str, 
        schule: str, 
        klasse: str
    ) -> List[Dict[str, Any]]:
        """
        Schüler einer Klasse laden
        
        Args:
            schuljahr: z.B. "2024/2025"
            schule: "gyd", "gympap", "obs"
            klasse: z.B. "8a"
        """
        return self.execute_query(
            """
            SELECT * FROM schueler 
            WHERE schuljahr = ? AND schule = ? AND klasse = ?
            ORDER BY nachname, rufname
            """,
            (schuljahr, schule, klasse)
        )
    
    def get_schueler_count_by_klasse(
        self,
        schuljahr: str,
        schule: str, 
        klasse: str
    ) -> int:
        """Anzahl Schüler in Klasse"""
        result = self.execute_query(
            """
            SELECT COUNT(*) as count FROM schueler
            WHERE schuljahr = ? AND schule = ? AND klasse = ?
            """,
            (schuljahr, schule, klasse)
        )
        return result[0]['count'] if result else 0
    
    def get_klassen_by_schule(
        self,
        schuljahr: str,
        schule: str
    ) -> List[str]:
        """Alle Klassen einer Schule"""
        results = self.execute_query(
            """
            SELECT DISTINCT klasse FROM schueler
            WHERE schuljahr = ? AND schule = ?
            ORDER BY klasse
            """,
            (schuljahr, schule)
        )
        return [r['klasse'] for r in results if r['klasse']]
    
    # ============================================================
    # AUFGABEN
    # ============================================================
    
    def get_aufgaben(
        self,
        fach: Optional[str] = None,
        jahrgangsstufe: Optional[int] = None,
        schwierigkeit: Optional[str] = None,
        suchtext: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Aufgaben laden mit optionalen Filtern
        
        Args:
            fach: "Mathematik", "Physik", "Informatik"
            jahrgangsstufe: 5-13
            schwierigkeit: "leicht", "mittel", "schwer"
            suchtext: Volltext-Suche in Titel/Themengebiet
        """
        query = "SELECT * FROM aufgaben WHERE 1=1"
        params = []
        
        if fach:
            query += " AND fach = ?"
            params.append(fach)
        
        if jahrgangsstufe:
            query += " AND jahrgangsstufe = ?"
            params.append(jahrgangsstufe)
        
        if schwierigkeit:
            query += " AND schwierigkeit = ?"
            params.append(schwierigkeit)
        
        if suchtext:
            query += " AND (titel LIKE ? OR themengebiet LIKE ?)"
            search_pattern = f"%{suchtext}%"
            params.extend([search_pattern, search_pattern])
        
        query += " ORDER BY erstellt_am DESC"
        
        return self.execute_query(query, tuple(params))
    
    def get_aufgabe_by_id(self, aufgabe_id: int) -> Optional[Dict[str, Any]]:
        """Einzelne Aufgabe laden"""
        results = self.execute_query(
            "SELECT * FROM aufgaben WHERE id = ?",
            (aufgabe_id,)
        )
        return results[0] if results else None
    
    def create_aufgabe(self, data: Dict[str, Any]) -> int:
        """
        Neue Aufgabe erstellen
        
        Args:
            data: Dictionary mit Aufgaben-Daten
            
        Returns:
            ID der neuen Aufgabe
        """
        query = """
            INSERT INTO aufgaben (
                template_id, titel, themengebiet, schwierigkeit,
                schlagwoerter, aufgaben_daten, fach, anforderungsbereich,
                punkte, kompetenzen, jahrgangsstufe, schulform,
                platzbedarf_min, latex_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('template_id', 1),
            data['titel'],
            data.get('themengebiet', ''),
            data.get('schwierigkeit', 'mittel'),
            data.get('schlagwoerter', ''),
            data.get('aufgaben_daten', ''),
            data.get('fach', ''),
            data.get('anforderungsbereich', 'II'),
            data.get('punkte', 0),
            data.get('kompetenzen', ''),
            data.get('jahrgangsstufe', 0),
            data.get('schulform', 'Gymnasium'),
            data.get('platzbedarf_min', 0.0),
            data.get('latex_code', '')
        )
        
        return self.execute_insert(query, params)
    
    def update_aufgabe(self, data: Dict[str, Any]) -> int:
        """Aufgabe aktualisieren"""
        query = """
            UPDATE aufgaben SET
                titel = ?, themengebiet = ?, schwierigkeit = ?,
                schlagwoerter = ?, fach = ?, anforderungsbereich = ?,
                punkte = ?, jahrgangsstufe = ?, schulform = ?,
                platzbedarf_min = ?, latex_code = ?
            WHERE id = ?
        """
        
        params = (
            data['titel'],
            data.get('themengebiet', ''),
            data.get('schwierigkeit', 'mittel'),
            data.get('schlagwoerter', ''),
            data.get('fach', ''),
            data.get('anforderungsbereich', 'II'),
            data.get('punkte', 0),
            data.get('jahrgangsstufe', 0),
            data.get('schulform', 'Gymnasium'),
            data.get('platzbedarf_min', 0.0),
            data.get('latex_code', ''),
            data['id']
        )
        
        return self.execute_update(query, params)
    
    def delete_aufgabe(self, aufgabe_id: int) -> int:
        """Aufgabe löschen"""
        return self.execute_update(
            "DELETE FROM aufgaben WHERE id = ?",
            (aufgabe_id,)
        )
    
    # ============================================================
    # TEMPLATES
    # ============================================================
    
    def get_templates(self, fach: Optional[str] = None) -> List[Dict[str, Any]]:
        """Aufgaben-Templates laden"""
        query = "SELECT * FROM aufgabentemplates"
        params = []
        
        if fach:
            query += " WHERE fach = ?"
            params.append(fach)
        
        query += " ORDER BY name"
        
        return self.execute_query(query, tuple(params))
    
    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Einzelnes Template laden"""
        results = self.execute_query(
            "SELECT * FROM aufgabentemplates WHERE id = ?",
            (template_id,)
        )
        return results[0] if results else None
    
    # ============================================================
    # KLAUSUREN (NEUE TABELLE!)
    # ============================================================
    
    def get_recent_klausuren(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Letzte Klausuren laden (für Dashboard)
        
        WICHTIG: Greift auf 'klausuren' Tabelle zu (nicht klausuren_alt!)
        """
        query = """
            SELECT 
                id,
                titel,
                datum,
                fach,
                jahrgangsstufe,
                klasse,
                schule,
                typ,
                zeit_minuten,
                aufgaben_json,
                seitenumbrueche_json,
                erstellt_am
            FROM klausuren
            ORDER BY erstellt_am DESC
            LIMIT ?
        """
        
        return self.execute_query(query, (limit,))
    
    def create_klausur(self, data: Dict[str, Any]) -> int:
        """
        Neue Klausur erstellen
        
        Args:
            data: Dictionary mit Klausur-Daten
            
        Returns:
            ID der neuen Klausur
        """
        query = """
            INSERT INTO klausuren (
                titel, datum, fach, jahrgangsstufe, typ,
                schule, klasse, zeit_minuten, aufgaben_json,
                seitenumbrueche_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data['titel'],
            data.get('datum', ''),
            data.get('fach', ''),
            data.get('jahrgangsstufe', 0),
            data.get('typ', 'Klassenarbeit'),
            data.get('schule', ''),
            data.get('klasse', ''),
            data.get('zeit_minuten', 45),
            data.get('aufgaben_json', '[]'),
            data.get('seitenumbrueche_json', '[]')
        )
        
        return self.execute_insert(query, params)
    
    def update_klausur(self, data: Dict[str, Any]) -> int:
        """
        Klausur aktualisieren
        
        NEU! Für Edit-Modus
        
        Args:
            data: Dictionary mit Klausur-Daten (muss 'id' enthalten!)
            
        Returns:
            Anzahl geänderter Zeilen (sollte 1 sein)
        """
        query = """
            UPDATE klausuren SET
                titel = ?,
                datum = ?,
                fach = ?,
                jahrgangsstufe = ?,
                typ = ?,
                schule = ?,
                klasse = ?,
                zeit_minuten = ?,
                aufgaben_json = ?,
                seitenumbrueche_json = ?
            WHERE id = ?
        """
        
        params = (
            data['titel'],
            data.get('datum', ''),
            data.get('fach', ''),
            data.get('jahrgangsstufe', 0),
            data.get('typ', 'Klassenarbeit'),
            data.get('schule', ''),
            data.get('klasse', ''),
            data.get('zeit_minuten', 45),
            data.get('aufgaben_json', '[]'),
            data.get('seitenumbrueche_json', '[]'),
            data['id']  # WHERE-Bedingung!
        )
        
        return self.execute_update(query, params)
    
    def get_klausur_by_id(self, klausur_id: int) -> Optional[Dict[str, Any]]:
        """Einzelne Klausur laden"""
        results = self.execute_query(
            "SELECT * FROM klausuren WHERE id = ?",
            (klausur_id,)
        )
        return results[0] if results else None
    
    # ============================================================
    # KLAUSURVORLAGEN (Templates für Klausuren)
    # ============================================================
    
    def get_klausurvorlagen(self, fach: Optional[str] = None) -> List[Dict[str, Any]]:
        """Klausur-Vorlagen laden"""
        query = "SELECT * FROM klausurvorlagen"
        params = []
        
        if fach:
            query += " WHERE fach_bezeichnung = ?"
            params.append(fach)
        
        query += " ORDER BY erstellt_am DESC"
        
        return self.execute_query(query, tuple(params))
    
    def create_klausurvorlage(self, data: Dict[str, Any]) -> int:
        """Neue Klausur-Vorlage erstellen"""
        query = """
            INSERT INTO klausurvorlagen (
                fach_bezeichnung, fach_kuerzel, nummer, thema,
                beschreibung, art, seitenzahl, gesamtpunkte
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data['fach_bezeichnung'],
            data['fach_kuerzel'],
            data['nummer'],
            data['thema'],
            data.get('beschreibung', ''),
            data.get('art', 'Klassenarbeit'),
            data.get('seitenzahl', 4),
            data.get('gesamtpunkte', 0)
        )
        
        return self.execute_insert(query, params)
    
    # ============================================================
    # KASUSID COUNTER
    # ============================================================
    
    def get_next_kasusid(self) -> int:
        """Nächste KasusID generieren"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Aktuellen Wert holen
            cursor.execute(
                "SELECT letzter_wert FROM kasusid_counter WHERE id = 1"
            )
            result = cursor.fetchone()
            
            if not result:
                # Counter initialisieren
                cursor.execute(
                    "INSERT INTO kasusid_counter (id, letzter_wert) VALUES (1, 100000)"
                )
                current = 100000
            else:
                current = result[0]
            
            # Inkrementieren
            next_id = current + 1
            cursor.execute(
                "UPDATE kasusid_counter SET letzter_wert = ?, aktualisiert_am = CURRENT_TIMESTAMP WHERE id = 1",
                (next_id,)
            )
            
            conn.commit()
            return next_id
    
    # ============================================================
    # GRAFIKEN
    # ============================================================
    
    def get_grafiken(self) -> List[Dict[str, Any]]:
        """Alle Grafiken laden (Alias für get_grafiken_pool)"""
        return self.get_grafiken_pool()
    
    def get_grafiken_pool(self) -> List[Dict[str, Any]]:
        """Alle Grafiken aus Pool laden"""
        return self.execute_query(
            "SELECT * FROM grafiken_pool ORDER BY erstellt_am DESC"
        )
    
    def get_grafik_by_id(self, grafik_id: int) -> Optional[Dict[str, Any]]:
        """Einzelne Grafik laden"""
        results = self.execute_query(
            "SELECT * FROM grafiken_pool WHERE id = ?",
            (grafik_id,)
        )
        return results[0] if results else None
    
    def create_grafik(self, data: Dict[str, Any]) -> int:
        """
        Neue Grafik erstellen
        
        Args:
            data: Dictionary mit Grafik-Daten
                - name: str
                - beschreibung: str
                - dateityp: str (PNG, JPG, SVG, PDF)
                - grafik_blob: bytes
                - groesse_bytes: int
                - tags: str
                
        Returns:
            ID der neuen Grafik
        """
        query = """
            INSERT INTO grafiken_pool (
                name, beschreibung, dateityp, grafik_blob,
                groesse_bytes, tags
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data['name'],
            data.get('beschreibung', ''),
            data['dateityp'],
            data['grafik_blob'],
            data.get('groesse_bytes', 0),
            data.get('tags', '')
        )
        
        return self.execute_insert(query, params)
    
    def delete_grafik(self, grafik_id: int) -> int:
        """Grafik löschen"""
        return self.execute_update(
            "DELETE FROM grafiken_pool WHERE id = ?",
            (grafik_id,)
        )
    
    # ============================================================
    # STATISTIKEN
    # ============================================================
    
    def get_statistics(self) -> Dict[str, int]:
        """Allgemeine Statistiken"""
        stats = {}
        
        # Anzahl Aufgaben
        result = self.execute_query("SELECT COUNT(*) as count FROM aufgaben")
        stats['aufgaben'] = result[0]['count'] if result else 0
        
        # Anzahl Klausuren (aus klausuren Tabelle!)
        result = self.execute_query("SELECT COUNT(*) as count FROM klausuren")
        stats['klausuren'] = result[0]['count'] if result else 0
        
        # Anzahl Grafiken
        result = self.execute_query("SELECT COUNT(*) as count FROM grafiken_pool")
        stats['grafiken'] = result[0]['count'] if result else 0
        
        # Anzahl Schüler
        result = self.execute_query("SELECT COUNT(*) as count FROM schueler")
        stats['schueler'] = result[0]['count'] if result else 0
        
        return stats


# Singleton-Instanz
_db_instance: Optional[Database] = None


def get_database(db_path: str = "database/sus.db") -> Database:
    """
    Globale Datenbank-Instanz holen (Singleton-Pattern)
    
    Args:
        db_path: Pfad zur Datenbank
        
    Returns:
        Database-Instanz
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = Database(db_path)
    
    return _db_instance
