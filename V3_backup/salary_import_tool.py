"""
Optimiertes Gehalts-Import-Tool für das Dashboard
Integration in die bestehende Dashboard-Struktur
"""

import re
import sqlite3
from pathlib import Path
from pdf2image import convert_from_path
import pdfplumber
import pytesseract
import sys
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os

# Setze explizit den Pfad zur tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\moahm\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Passe diesen Pfad ggf. an deine Poppler-Installation an
POPPLER_PATH = r"C:\Users\moahm\AppData\Local\Programs\poppler-24.08.0\Library\bin"

@dataclass
class PayrollEntry:
    """Datenklasse für Gehaltsabrechnungs-Einträge"""
    dienstnehmer: str
    dn_nr: str
    brutto: float
    zahlbetrag: float
    page_number: int
    confidence: float

class _ConsoleEncodingSafeFilter(logging.Filter):
    """Filtert Zeichen aus Log-Messages heraus, die in der aktuellen Konsole nicht darstellbar sind.
    Betrifft nur den Konsolen-Handler – Datei-Logs bleiben unverändert (inkl. Emojis)."""
    def __init__(self, target_stream_encoding: Optional[str] = None):
        super().__init__()
        self._enc = target_stream_encoding or (getattr(sys.stdout, 'encoding', None) or 'cp1252')

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            try:
                # Schnellpfad: falls encodierbar, nichts ändern
                msg.encode(self._enc)
            except UnicodeEncodeError:
                # Zeichen, die nicht encodierbar sind, entfernen
                safe_chars: List[str] = []
                for ch in msg:
                    try:
                        ch.encode(self._enc)
                        safe_chars.append(ch)
                    except UnicodeEncodeError:
                        # auslassen (typisch: Emojis)
                        continue
                msg = ''.join(safe_chars)
                # Setze die bereits formatierte Message zurück in den Record
                record.msg = msg
                record.args = ()
        except Exception:
            # Bei Problemen Filter nicht blockieren
            return True
        return True

class SalaryImportTool:
    """Optimiertes Import-Tool für Gehaltsabrechnungen"""
    
    def __init__(self, salaries_db_path: Path, drivers_db_path: Path):
        self.salaries_db_path = salaries_db_path
        self.drivers_db_path = drivers_db_path
        # Map von normalisierten Token-Tuples -> (driver_id, kanonischer_name)
        self.driver_cache: Dict[tuple, tuple] = {}
        # Zusätzliche Map für schnellen Lookup: driver_id -> kanonischer_name
        self.driver_id_to_name: Dict[int, str] = {}
        
        # Logging für das Tool zuerst einrichten
        self.setup_logging()
        
        # Dann Fahrer-Cache laden
        self.load_driver_cache()
        
    def setup_logging(self):
        """Konfiguriert das Logging für das Import-Tool"""
        # Erstelle einen Logger für diese Instanz
        self.logger = logging.getLogger(f"SalaryImportTool_{id(self)}")
        self.logger.setLevel(logging.INFO)
        
        # Entferne bestehende Handler um Duplikate zu vermeiden
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Erstelle neue Handler
        file_handler = logging.FileHandler('salary_import.log', encoding='utf-8')
        console_handler = logging.StreamHandler()
        
        # Formatter erstellen
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Nur für Konsole: nicht-darstellbare Zeichen (z. B. Emojis) herausfiltern
        console_handler.addFilter(_ConsoleEncodingSafeFilter(getattr(sys.stdout, 'encoding', None)))
        
        # Handler hinzufügen
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        # Laute pdfminer/pdfplumber-Logs unterdrücken (CropBox etc.)
        for noisy in (
            "pdfminer",
            "pdfminer.pdfpage",
            "pdfminer.pdfinterp",
            "pdfminer.layout",
            "pdfminer.converter",
            "pdfminer.pdfdocument",
            "pdfminer.pdftypes",
            "pdfplumber",
        ):
            logging.getLogger(noisy).setLevel(logging.ERROR)
        
    def load_driver_cache(self):
        """Lädt alle Fahrer in den Cache für schnelleres Matching"""
        try:
            conn = sqlite3.connect(str(self.drivers_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT driver_id, first_name, last_name FROM drivers")
            drivers = cursor.fetchall()
            
            # Cache zurücksetzen
            self.driver_cache.clear()
            self.driver_id_to_name.clear()

            for driver_id, first_name, last_name in drivers:
                # Kanonischer Name aus Stammdaten
                canonical_name = f"{first_name or ''} {last_name or ''}".strip()
                # Normalisierte Namen als Schlüssel
                normalized_name = self.normalize_name(canonical_name)
                self.driver_cache[tuple(normalized_name)] = (driver_id, canonical_name)
                self.driver_id_to_name[int(driver_id)] = canonical_name
                
            conn.close()
            self.logger.info(f"✅ {len(drivers)} Fahrer in Cache geladen")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Laden des Fahrer-Caches: {e}")
    
    def normalize_name(self, name: str) -> List[str]:
        """Optimierte Namensnormalisierung"""
        return [token for token in re.findall(r'[a-zA-Zäöüß]+', name.lower())]
    
    def _generate_token_variants(self, tokens: List[str]) -> set:
        """Erzeugt Varianten der Tokens (inkl. Zusammenziehungen), um Splits/Merges zu erkennen."""
        variants = set(tokens)
        # Paarweise Zusammenziehungen angrenzender Tokens
        for i in range(len(tokens) - 1):
            variants.add(tokens[i] + tokens[i + 1])
        # Gesamte Zusammenziehung
        if tokens:
            variants.add(''.join(tokens))
        # Sonderfall: 'el' Präfix mit folgendem Token (arabische Namen)
        for i, t in enumerate(tokens[:-1]):
            if t == 'el':
                variants.add('el' + tokens[i + 1])
        return variants

    def match_driver_optimized(self, dienstnehmer: str) -> Tuple[Optional[int], Optional[str]]:
        """Fuzzy-Fahrermatching analog zum Umsatzmatching. Liefert (driver_id, kanonischer_name)."""
        if not dienstnehmer or not dienstnehmer.strip():
            return None, None

        def clean_name(name: str) -> str:
            s = str(name).lower()
            # Sonderfälle/Normalisierung
            s = s.replace('-', ' ').replace('_', ' ')
            # Nicht-Buchstaben entfernen
            s = re.sub(r"[^a-zäöüß\s]", " ", s)
            # Mehrfach-Leerzeichen reduzieren
            s = re.sub(r"\s+", " ", s)
            # arabische Präfixe normalisieren
            s = re.sub(r"\bal\s+", "el ", s)
            # OCR-Korrektur: 'ei' als separates Token als 'el' interpretieren
            s = re.sub(r"\bei\b", "el", s)
            return s.strip()

        def levenshtein_distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

        def fuzzy_match_score(search_name: str, target_name: str, max_distance: int = 3) -> float:
            if not search_name or not target_name:
                return 0.0
            if search_name == target_name:
                return 100.0
            search_tokens = clean_name(search_name).split()
            target_tokens = clean_name(target_name).split()
            def extend_el(tokens):
                ext = tokens.copy()
                for i, token in enumerate(tokens):
                    if token == 'el' and i + 1 < len(tokens):
                        ext.append('el' + tokens[i + 1])
                # Neu: Paarweise Merges zur Erkennung von Splits ("ah"+"madeey"→"ahmadeey")
                for i in range(len(tokens) - 1):
                    ext.append(tokens[i] + tokens[i + 1])
                return ext
            s_ext = extend_el(search_tokens)
            t_ext = extend_el(target_tokens)
            set_s, set_t = set(s_ext), set(t_ext)
            inter = set_s & set_t
            union = set_s | set_t
            inter_size = len(inter)
            if inter_size == 0 and levenshtein_distance(search_name, target_name) > max_distance:
                return 0.0
            dice = (2 * inter_size) / max(1, (len(set_s) + len(set_t)))
            jaccard = inter_size / max(1, len(union))
            coverage = inter_size / max(1, len(set_s))
            order_bonus = 0.0
            if search_tokens and target_tokens and search_tokens[0] == target_tokens[0]:
                order_bonus += 8.0
            if search_tokens and target_tokens and search_tokens[-1] == target_tokens[-1]:
                order_bonus += 8.0
            prefix_bonus = 0.0
            for st in search_tokens:
                if any(tt.startswith(st) or st.startswith(tt) for tt in target_tokens):
                    prefix_bonus += 2.0
            prefix_bonus = min(prefix_bonus, 8.0)
            arabic_bonus = 0.0
            if any(t == 'el' or t.startswith('el') for t in search_tokens) and any(t == 'el' or t.startswith('el') for t in target_tokens):
                arabic_bonus = 20.0
            dist = levenshtein_distance(search_name, target_name)
            max_len = max(len(search_name), len(target_name))
            norm_dist = (dist / max_len) if max_len else 1.0
            distance_score = max(0.0, 100.0 - (norm_dist * 100.0)) / 100.0
            base = (0.55 * dice + 0.20 * coverage + 0.10 * jaccard + 0.15 * distance_score) * 100.0
            return float(max(0.0, min(100.0, base + order_bonus + prefix_bonus + arabic_bonus)))

        search_clean = clean_name(dienstnehmer)
        search_tokens = search_clean.split()
        if not search_tokens:
            return None, None

        best = None  # (score, coverage, driver_id, canonical_name)
        for driver_id, canonical_name in self.driver_id_to_name.items():
            cand_clean = clean_name(canonical_name)
            score = fuzzy_match_score(search_clean, cand_clean, max_distance=3)
            cand_tokens = cand_clean.split()
            inter = len(set(search_tokens) & set(cand_tokens))
            coverage = inter / max(1, len(set(search_tokens)))
            order_ok = False
            if cand_tokens:
                if search_tokens[0:1] == cand_tokens[0:1]:
                    order_ok = True
                if search_tokens[-1:] == cand_tokens[-1:]:
                    order_ok = True
            if search_clean and search_clean in cand_clean:
                order_ok = True
            # Schwellen aus dem Umsatzmatching
            order_ok_relaxed = (
                order_ok
                or sorted(search_tokens) == sorted(cand_tokens)
                or (coverage >= 0.67 and len(search_tokens) >= 2)
            )
            # Zusätzliche Akzeptanz: Wenn genau eine benachbarte Token-Zusammenziehung der Such-Tokens
            # eine tokenweise Übereinstimmung mit den Kandidaten ergibt (Reihenfolge egal)
            merge_ok = False
            merge_coverage_ok = False
            if len(search_tokens) >= 2:
                cand_set = set(cand_tokens)
                for i in range(len(search_tokens) - 1):
                    merged = search_tokens[:i] + [search_tokens[i] + search_tokens[i + 1]] + search_tokens[i + 2:]
                    merged_set = set(merged)
                    if merged_set == cand_set:
                        merge_ok = True
                        merge_coverage_ok = True
                        break
                    inter2 = len(merged_set & set(cand_tokens))
                    cov2 = inter2 / max(1, len(merged_set))
                    if cov2 >= 0.5:
                        merge_coverage_ok = True
                
            if score >= 65 and ((coverage >= 0.5) or merge_coverage_ok) and (order_ok_relaxed or merge_ok):
                if best is None or score > best[0] or (score == best[0] and coverage > best[1]):
                    best = (score, coverage, driver_id, canonical_name)
        if best is not None:
            return best[2], best[3]
        # Fallback: eindeutige Token-Set-Gleichheit (z. B. 'Ahmed Osama' ↔ 'Osama Ahmed')
        search_tokens_set = set(search_tokens)
        equal_set_candidates: List[Tuple[int, str]] = []
        for driver_id, canonical_name in self.driver_id_to_name.items():
            cand_tokens = clean_name(canonical_name).split()
            if set(cand_tokens) == search_tokens_set and len(cand_tokens) == len(search_tokens):
                equal_set_candidates.append((driver_id, canonical_name))
        if len(equal_set_candidates) == 1:
            did, cname = equal_set_candidates[0]
            return did, cname
        return None, None
    
    def extract_text_optimized(self, image) -> str:
        """Optimierte Textextraktion mit Fallback-Strategien"""
        # Erste OCR-Versuche mit verschiedenen PSM-Modi
        psm_modes = [6, 11, 8, 13]  # Verschiedene OCR-Modi für bessere Ergebnisse
        
        for psm in psm_modes:
            try:
                text = pytesseract.image_to_string(
                    image, 
                    lang='deu', 
                    config=f'--psm {psm} --oem 3'
                )
                if text.strip():
                    return text
            except Exception as e:
                self.logger.warning(f"OCR-Fehler mit PSM {psm}: {e}")
                continue
        
        return ""
    
    def extract_payroll_data(self, text: str, page_number: int) -> List[PayrollEntry]:
        """Optimierte Extraktion von Gehaltsdaten mit verbesserten Regex-Mustern"""
        entries = []
        
        # Verbesserte Regex-Muster mit höherer Präzision
        patterns = {
            # Toleriert OCR-Fehler (fehlendes 'r') und Varianten /in, In
            'Dienstnehmer': r'Dienstnehme(?:r(?:/in|In)?)?\W*[:\-]?\s*(.*?)(?=\s*DN[- ]?Nr|$)',
            'DN-Nr.': r'DN[- ]?Nr\.?\W*[:\-]?\s*(\d+)',
            # Erlaubt 'Brutto-Bezug' zusätzlich
            'Brutto': r'Brutto(?:-?Bezug)?\W*[:\-]?\s*([\d\.,]+)',
            # Akzeptiert auch 'Auszahlungsbetrag' und 'Netto(betrag)'
            'Zahlbetrag': r'(?:Zahlbetrag|Auszahlungsbetrag|Netto(?:betrag)?)\W*[:\-]?\s*([\d\.,]+)'
        }
        
        # Text in Zeilen aufteilen für bessere Verarbeitung
        lines = text.split('\n')
        
        current_entry = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Suche nach allen Mustern in der aktuellen Zeile
            for key, pattern in patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if key == 'Dienstnehmer':
                        # Falls bereits ein Name vorhanden ist, vorherigen Datensatz finalisieren
                        if 'Dienstnehmer' in current_entry:
                            try:
                                entry = PayrollEntry(
                                    dienstnehmer=current_entry.get('Dienstnehmer', ''),
                                    dn_nr=current_entry.get('DN-Nr.', ''),
                                    brutto=self.parse_amount(current_entry.get('Brutto', '0')),
                                    zahlbetrag=self.parse_amount(current_entry.get('Zahlbetrag', '0')),
                                    page_number=page_number,
                                    confidence=0.8
                                )
                                entries.append(entry)
                            except ValueError as e:
                                self.logger.warning(f"Fehler beim Parsen der Daten: {e}")
                            # Neuer aktueller Eintrag beginnt mit erkanntem Namen
                            current_entry = {}
                        current_entry['Dienstnehmer'] = value
                    else:
                        current_entry[key] = value
        
        # Am Ende der Seite letzten Eintrag (falls vorhanden) finalisieren
        if 'Dienstnehmer' in current_entry:
            try:
                entry = PayrollEntry(
                    dienstnehmer=current_entry.get('Dienstnehmer', ''),
                    dn_nr=current_entry.get('DN-Nr.', ''),
                    brutto=self.parse_amount(current_entry.get('Brutto', '0')),
                    zahlbetrag=self.parse_amount(current_entry.get('Zahlbetrag', '0')),
                    page_number=page_number,
                    confidence=0.8
                )
                entries.append(entry)
            except ValueError as e:
                self.logger.warning(f"Fehler beim Parsen der Daten: {e}")
        
        return entries
    
    def parse_amount(self, amount_str: str) -> float:
        """Optimierte Betragsparsing mit Fehlerbehandlung"""
        try:
            # Entferne alle Leerzeichen und ersetze Komma durch Punkt
            cleaned = amount_str.replace(' ', '').replace(',', '.')
            # Entferne alle Punkte außer dem letzten (für Tausender-Trennzeichen)
            if cleaned.count('.') > 1:
                parts = cleaned.split('.')
                cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def process_single_page(self, image, page_number: int) -> List[PayrollEntry]:
        """Verarbeitet eine einzelne PDF-Seite"""
        try:
            text = self.extract_text_optimized(image)
            if not text.strip():
                self.logger.warning(f"Kein Text auf Seite {page_number} extrahiert")
                return []
            
            entries = self.extract_payroll_data(text, page_number)
            self.logger.info(f"Seite {page_number}: {len(entries)} Einträge gefunden")
            return entries
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Verarbeitung von Seite {page_number}: {e}")
            return []

    # === Schneller Pfad: pdfplumber-first, OCR nur wenn nötig ===
    def _plumber_extract_page_texts(self, pdf_path: Path) -> Dict[int, str]:
        texts: Dict[int, str] = {}
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    t = page.extract_text(x_tolerance=1, y_tolerance=1) or ""
                    texts[i] = t
        except Exception as e:
            self.logger.warning(f"plumber-Extraktion fehlgeschlagen: {e}")
        return texts

    def _plumber_header_from_page(self, pdf_path: Path, page_number: int) -> Tuple[str, str]:
        dn = ''
        dnnr = ''
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                if 1 <= page_number <= len(pdf.pages):
                    page = pdf.pages[page_number - 1]
                    words = page.extract_words(x_tolerance=2, y_tolerance=2)
                    # Dienstnehmer: Token beginnend mit 'Dienstnehme'
                    for w in words:
                        t = (w.get('text', '') or '')
                        if re.match(r"^Dienstnehme", t, re.IGNORECASE):
                            y = float(w.get('top', 0.0))
                            x_right = float(w.get('x1', 0.0))
                            right_words = [ww for ww in words if abs(float(ww.get('top', 0.0)) - y) <= 2.0 and float(ww.get('x0', 0.0)) > x_right]
                            line = ' '.join((ww.get('text', '') or '') for ww in right_words)
                            line = self._normalize_inline(line)
                            line = re.split(r"\b(DN\W*Nr|Monat|Firma|Unternehmen)\b", line, flags=re.IGNORECASE)[0].strip()
                            line = re.split(r"\s\d{2,}.*", line)[0].strip()
                            if line:
                                dn = line
                                break
                    # DN-Nr.: kombiniert oder getrennt, Zahl rechts daneben
                    label_pat = re.compile(r"^(?:DN\W*Nr|DNr)\.?[:]?$", re.IGNORECASE)
                    dn_only_pat = re.compile(r"^DN$", re.IGNORECASE)
                    for w in words:
                        t = (w.get('text', '') or '').strip()
                        if label_pat.match(t) or dn_only_pat.match(t):
                            y = float(w.get('top', 0.0))
                            x_right = float(w.get('x1', 0.0))
                            same_line = [ww for ww in words if abs(float(ww.get('top', 0.0)) - y) <= 3.0 and float(ww.get('x0', 0.0)) > x_right]
                            numeric_right = sorted([ww for ww in same_line if re.match(r"^\d{1,8}$", (ww.get('text', '') or '').strip())], key=lambda a: float(a.get('x0', 0.0)))
                            if numeric_right:
                                dnnr = (numeric_right[0].get('text', '') or '').strip()
                                break
                            near_right = sorted([ww for ww in words if (y - 8.0) <= float(ww.get('top', 0.0)) <= (y + 8.0) and float(ww.get('x0', 0.0)) > x_right and re.match(r"^\d{1,8}$", (ww.get('text', '') or '').strip())], key=lambda a: (abs(float(a.get('top', 0.0)) - y), float(a.get('x0', 0.0))))
                            if near_right:
                                dnnr = (near_right[0].get('text', '') or '').strip()
                                break
        except Exception:
            pass
        return dn, dnnr

    # Vorgecompilete Muster (schneller Pfad)
    _RE_DIENSTNEHMER_LINE = re.compile(r"Dienstnehme(?:r(?:/in|In)?)?\s*:\s*([^\n]+)", re.IGNORECASE)
    _RE_DIENSTNEHMER = re.compile(r"Dienstnehme(?:r(?:/in|In)?)?\W*[:\-]?\s*(.*?)(?=\s*(DN\W*Nr|Monat|Firma|Unternehmen|El\b)|$)", re.IGNORECASE)
    _RE_DNNR = re.compile(r"(?:DN\s*[\-‑–—]?\s*Nr|DNr)\.?\s*[:]?\s*(\d+)", re.IGNORECASE)
    _RE_BRUTTO = re.compile(r"Brutto(?:-?Bezug)?\W*[:\-]?\s*([\d\.,]+)", re.IGNORECASE)
    _RE_ZAHLBETRAG = re.compile(r"(?:Zahlbetrag|Auszahlungsbetrag|Netto(?:betrag)?)\W*[:\-]?\s*([\d\.,]+)", re.IGNORECASE)

    def _normalize_inline(self, s: str) -> str:
        s = s.replace('\xa0', ' ')
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    def _to_float(self, amount_str: str) -> float:
        s = (amount_str or "").replace(" ", "").replace(".", "").replace(",", ".")
        try:
            return float(s)
        except Exception:
            return 0.0

    def _find_page_header_fields_fast(self, text: str) -> Tuple[str, str]:
        dn = ''
        dnnr = ''
        m = self._RE_DIENSTNEHMER_LINE.search(text)
        if m:
            raw = self._normalize_inline(m.group(1))
            raw = re.split(r"\b(DN\s*[-]?\s*Nr|Monat|Firma|Unternehmen)\b", raw, flags=re.IGNORECASE)[0].strip()
            raw = re.split(r"\s\d{2,}.*", raw)[0].strip()
            parts = raw.split()
            if len(parts) > 4:
                raw = " ".join(parts[:4])
            dn = raw
        else:
            lines = text.splitlines()
            for i, raw in enumerate(lines):
                if re.search(r"Dienstnehme(?:r(?:/in|In)?)?\b", raw, re.IGNORECASE):
                    for j in range(i + 1, min(i + 5, len(lines))):
                        candidate = lines[j].strip()
                        if candidate:
                            if re.match(r"^\d{3,}\b", candidate):
                                continue
                            dn = self._normalize_inline(candidate)
                            break
                    break
        m2 = self._RE_DNNR.search(text)
        if m2:
            dnnr = m2.group(1).strip()
        else:
            lines = text.splitlines()
            for raw in lines[:80]:
                mm = self._RE_DNNR.search(raw)
                if mm:
                    dnnr = mm.group(1).strip()
                    break
        if not dn:
            name_line = None
            for raw in text.splitlines()[:20]:
                cand = self._normalize_inline(raw)
                if not cand or len(cand) < 5:
                    continue
                if re.search(r"\d{2}[/\-.]\d{4}|Brutto|Netto|Zahlbetrag|Betrag|Einbehalte|Bemessung|Bezug|Monat", cand, re.IGNORECASE):
                    continue
                tokens = cand.split()
                if 2 <= len(tokens) <= 5 and all(t[0].isalpha() and t[0].isupper() and not re.search(r"\d", t) for t in tokens):
                    name_line = cand
                    break
            if name_line:
                dn = name_line
        return dn, dnnr
    
    def import_single_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """Importiert eine einzelne PDF-Datei mit schnellem pdfplumber-first Ansatz und gibt Ergebnisse zurück"""
        self.logger.info(f"🔍 Verarbeite Datei: {pdf_path}")

        match = re.search(r'Abrechnungen?\s+(\d{2})_(\d{4})', pdf_path.name, re.IGNORECASE)
        if not match:
            self.logger.error(f"⚠️ Dateiname {pdf_path} entspricht nicht dem Abrechnungs-Muster.")
            return {"success": False, "error": "Ungültiger Dateiname", "imported_count": 0}

        month = int(match.group(1))
        year = int(match.group(2))
        table_name = f"{month:02d}_{str(year)[-2:]}"
        self.logger.info(f"📊 Erstelle Tabelle: {table_name} (Monat: {month}, Jahr: {year})")

        # 1) Plumber first
        plumber_texts = self._plumber_extract_page_texts(pdf_path)
        doc_dn_default = ''
        doc_dnnr_default = ''
        if 1 in plumber_texts and plumber_texts[1].strip():
            dn_d, dnnr_d = self._find_page_header_fields_fast(plumber_texts[1])
            doc_dn_default, doc_dnnr_default = dn_d, dnnr_d
        if not doc_dn_default or not doc_dnnr_default:
            dn_p, dnnr_p = self._plumber_header_from_page(pdf_path, 1)
            if dn_p and not doc_dn_default:
                doc_dn_default = dn_p
            if dnnr_p and not doc_dnnr_default:
                doc_dnnr_default = dnnr_p

        # 2) Bilder nur für Seiten ohne brauchbaren Text
        images = []
        try:
            if any(not (plumber_texts.get(i, "").strip()) for i in range(1, (len(plumber_texts) or 0) + 1)):
                images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
        except Exception as e:
            # Fallback: komplette OCR
            images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)

        all_entries: List[PayrollEntry] = []
        num_pages = max(len(plumber_texts), len(images)) or 0
        for i in range(1, num_pages + 1):
            text = plumber_texts.get(i, "")
            if not text.strip() and images:
                img = images[i - 1] if i - 1 < len(images) else None
                if img is not None:
                    text = self.extract_text_optimized(img)
            if not text.strip():
                continue

            # Header pro Seite bestimmen (Text, dann Positionen)
            dn_def, dnnr_def = self._find_page_header_fields_fast(text)
            if not dn_def or not dnnr_def:
                dn_p, dnnr_p = self._plumber_header_from_page(pdf_path, i)
                dn_def = dn_def or dn_p
                dnnr_def = dnnr_def or dnnr_p

            # Einträge aus Text extrahieren
            # Zeilenweise Parsing: eine Zeile liefert oft alle Werte, ansonsten seitenweite Suche
            entries: List[PayrollEntry] = []
            current: Dict[str, str] = {}
            for raw in text.splitlines():
                line = raw.strip()
                if not line:
                    continue
                m = self._RE_DIENSTNEHMER.search(line)
                if m:
                    if 'Dienstnehmer' in current:
                        entries.append(PayrollEntry(
                            dienstnehmer=current.get('Dienstnehmer', ''),
                            dn_nr=current.get('DN-Nr.', '') or dnnr_def or doc_dnnr_default,
                            brutto=self._to_float(current.get('Brutto', '0')),
                            zahlbetrag=self._to_float(current.get('Zahlbetrag', '0')),
                            page_number=i,
                            confidence=0.9,
                        ))
                        current = {}
                    current['Dienstnehmer'] = m.group(1).strip() or dn_def or doc_dn_default
                m = self._RE_DNNR.search(line)
                if m:
                    current['DN-Nr.'] = m.group(1).strip()
                m = self._RE_BRUTTO.search(line)
                if m:
                    current['Brutto'] = m.group(1).strip()
                m = self._RE_ZAHLBETRAG.search(line)
                if m:
                    current['Zahlbetrag'] = m.group(1).strip()

            if 'Dienstnehmer' in current or any([current.get('Brutto'), current.get('Zahlbetrag')]):
                entries.append(PayrollEntry(
                    dienstnehmer=current.get('Dienstnehmer', '') or dn_def or doc_dn_default,
                    dn_nr=current.get('DN-Nr.', '') or dnnr_def or doc_dnnr_default,
                    brutto=self._to_float(current.get('Brutto', '0')),
                    zahlbetrag=self._to_float(current.get('Zahlbetrag', '0')),
                    page_number=i,
                    confidence=0.9,
                ))

            # Fallback: seitenweite Suche falls nichts erfasst
            if not entries:
                dn_match = self._RE_DIENSTNEHMER.search(text)
                id_match = self._RE_DNNR.search(text)
                br_match = self._RE_BRUTTO.search(text)
                zb_match = self._RE_ZAHLBETRAG.search(text)
                if any([dn_match, id_match, br_match, zb_match]):
                    entries.append(PayrollEntry(
                        dienstnehmer=(dn_match.group(1).strip() if dn_match else (dn_def or doc_dn_default)),
                        dn_nr=(id_match.group(1).strip() if id_match else (dnnr_def or doc_dnnr_default)),
                        brutto=self._to_float(br_match.group(1)) if br_match else 0.0,
                        zahlbetrag=self._to_float(zb_match.group(1)) if zb_match else 0.0,
                        page_number=i,
                        confidence=0.8,
                    ))

            all_entries.extend(entries)

        # Falls der schnelle Pfad nichts geliefert hat: Fallback auf alten OCR-Flow
        if not all_entries:
            try:
                images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
            except Exception as e:
                self.logger.error(f"Fehler beim Konvertieren der PDF (Fallback): {e}")
                return {"success": False, "error": f"PDF-Konvertierung fehlgeschlagen: {e}", "imported_count": 0}
            for i, img in enumerate(images):
                entries = self.process_single_page(img, i + 1)
                all_entries.extend(entries)

        result = self.save_to_database(all_entries, table_name)
        return {
            "success": True,
            "table_name": table_name,
            "imported_count": result,
            "total_entries": len(all_entries),
            "month": month,
            "year": year
        }
    
    def create_new_driver(self, dienstnehmer: str, dn_nr: str = None) -> Optional[int]:
        """Erstellt einen neuen Fahrer in der drivers-Tabelle und gibt die driver_id zurück"""
        try:
            # Verbindung zur Fahrerdatenbank
            conn = sqlite3.connect(str(self.drivers_db_path))
            cursor = conn.cursor()
            
            # Namen in Vor- und Nachname aufteilen (arabische Namen korrekt behandeln)
            name_parts = dienstnehmer.strip().split()
            if len(name_parts) >= 2:
                # Bei arabischen Namen ist oft der letzte Teil der Vorname
                # Prüfe auf arabische Präfixe wie "El-", "Al-", "Abd-", etc.
                if any(part.startswith(('El-', 'Al-', 'Abd-', 'Abu-', 'Ibn-')) for part in name_parts):
                    # Bei arabischen Namen: Letzter Teil = Vorname, Rest = Nachname
                    first_name = name_parts[-1]
                    last_name = ' '.join(name_parts[:-1])
                else:
                    # Standard: Erster Teil = Vorname, Rest = Nachname
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
            else:
                first_name = dienstnehmer.strip()
                last_name = ""
            
            # driver_id aus dn_nr ableiten (falls verfügbar)
            driver_id = None
            if dn_nr and dn_nr.strip().isdigit():
                driver_id = int(dn_nr.strip())
            
            # Prüfen ob Fahrer mit dieser driver_id bereits existiert
            if driver_id:
                cursor.execute("SELECT driver_id FROM drivers WHERE driver_id = ?", (driver_id,))
                if cursor.fetchone():
                    self.logger.info(f"⚠️ Fahrer mit driver_id {driver_id} existiert bereits")
                    conn.close()
                    return driver_id
            
            # Neuen Fahrer einfügen
            if driver_id:
                # Mit spezifischer driver_id (aus dn_nr)
                cursor.execute("""
                    INSERT INTO drivers (driver_id, driver_license_number, first_name, last_name, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (driver_id, f"DN{dn_nr}", first_name, last_name, "active"))
                new_driver_id = driver_id
            else:
                # Ohne spezifische driver_id (Auto-Increment)
                cursor.execute("""
                    INSERT INTO drivers (driver_license_number, first_name, last_name, status)
                    VALUES (?, ?, ?, ?)
                """, (f"DN_{first_name}_{last_name}", first_name, last_name, "active"))
                new_driver_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            # Cache aktualisieren
            canonical_name = f"{first_name} {last_name}".strip()
            self.driver_id_to_name[new_driver_id] = canonical_name
            
            self.logger.info(f"🆕 Neuer Fahrer angelegt: {canonical_name} (ID: {new_driver_id}, DN-Nr: {dn_nr})")
            return new_driver_id
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Anlegen des neuen Fahrers: {e}")
            return None

    def save_to_database(self, entries: List[PayrollEntry], table_name: str) -> int:
        """Speichert Einträge in der Datenbank und legt neue Fahrer automatisch an"""
        try:
            conn = sqlite3.connect(str(self.salaries_db_path))
            cursor = conn.cursor()
            
            # Tabelle anlegen
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER,
                dienstnehmer TEXT,
                dn_nr TEXT,
                brutto REAL,
                zahlbetrag REAL,
                page_number INTEGER,
                confidence REAL,
                import_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Einträge einfügen
            inserted_count = 0
            new_drivers_created = 0
            
            for entry in entries:
                # 1) DN-Nr.-basierte Zuordnung (falls verfügbar)
                matched_driver_id = None
                matched_name = None
                dn = str(entry.dn_nr or '').strip()
                if dn.isdigit():
                    dn_int = int(dn)
                    if dn_int in self.driver_id_to_name:
                        matched_driver_id = dn_int
                        matched_name = self.driver_id_to_name[dn_int]
                
                # 2) Fuzzy-Matching nur wenn noch nichts gefunden
                if matched_driver_id is None:
                    matched_driver_id, matched_name = self.match_driver_optimized(entry.dienstnehmer)
                
                # 3) Wenn kein Match gefunden, neuen Fahrer anlegen
                if matched_driver_id is None and entry.dienstnehmer.strip():
                    matched_driver_id = self.create_new_driver(entry.dienstnehmer, entry.dn_nr)
                    if matched_driver_id:
                        new_drivers_created += 1
                        matched_name = entry.dienstnehmer
                
                stored_dienstnehmer = matched_name if matched_name else entry.dienstnehmer

                cursor.execute(f'''INSERT INTO "{table_name}" 
                    (driver_id, dienstnehmer, dn_nr, brutto, zahlbetrag, page_number, confidence) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (matched_driver_id, stored_dienstnehmer, entry.dn_nr, entry.brutto,
                     entry.zahlbetrag, entry.page_number, entry.confidence))
                inserted_count += 1
            
            conn.commit()
            conn.close()
            
            if new_drivers_created > 0:
                self.logger.info(f"✅ {inserted_count} Einträge in Tabelle {table_name} gespeichert, {new_drivers_created} neue Fahrer angelegt")
            else:
                self.logger.info(f"✅ {inserted_count} Einträge in Tabelle {table_name} gespeichert")
            return inserted_count
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern in Datenbank: {e}")
            return 0
    
    def get_import_status(self) -> Dict[str, any]:
        """Gibt den aktuellen Import-Status zurück"""
        try:
            conn = sqlite3.connect(str(self.salaries_db_path))
            cursor = conn.cursor()
            
            # Alle Tabellen auflisten
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_%'")
            tables = cursor.fetchall()
            
            # Statistiken für jede Tabelle
            table_stats = {}
            for (table_name,) in tables:
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cursor.fetchone()[0]
                table_stats[table_name] = count
            
            conn.close()
            
            return {
                "total_tables": len(tables),
                "table_stats": table_stats,
                "last_import": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen des Import-Status: {e}")
            return {"error": str(e)}

# Globale Funktionen für einfache Integration
def create_import_tool(salaries_db_path: str = None, drivers_db_path: str = None) -> SalaryImportTool:
    """Erstellt eine Instanz des Import-Tools mit Standard-Pfaden"""
    if salaries_db_path is None:
        salaries_db_path = Path(__file__).parent / "SQL" / "salaries.db"
    if drivers_db_path is None:
        drivers_db_path = Path(__file__).parent / "SQL" / "database.db"
    
    return SalaryImportTool(Path(salaries_db_path), Path(drivers_db_path))

def import_salary_pdf(pdf_path: str, salaries_db_path: str = None, drivers_db_path: str = None) -> Dict[str, any]:
    """Einfache Funktion zum Importieren einer einzelnen PDF"""
    tool = create_import_tool(salaries_db_path, drivers_db_path)
    return tool.import_single_pdf(Path(pdf_path))

def get_salary_import_status(salaries_db_path: str = None) -> Dict[str, any]:
    """Gibt den Import-Status zurück"""
    tool = create_import_tool(salaries_db_path)
    return tool.get_import_status()

# Kompatibilitätsfunktion für das bestehende System
def import_salarie(pdf_path: Path, salaries_db_path: Path, drivers_db_path: Path):
    """Kompatibilitätsfunktion für das bestehende System"""
    tool = SalaryImportTool(salaries_db_path, drivers_db_path)
    result = tool.import_single_pdf(pdf_path)
    
    if result["success"]:
        print(f"✅ Abrechnung verarbeitet und in Tabelle {result['table_name']} gespeichert.")
        print(f"📊 {result['imported_count']} Einträge importiert")
    else:
        print(f"❌ Import fehlgeschlagen: {result['error']}")
    
    return result 