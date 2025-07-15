import re
import sqlite3
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import sys
from datetime import datetime

# Setze explizit den Pfad zur tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:/Users/moahm/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
POPPLER_PATH = r"C:/Users/moahm/AppData/Local/Programs/poppler-24.08.0/Library/bin"

def analyze_new_pdf(pdf_path: Path):
    """Analysiert die neue PDF und zeigt den OCR-Text"""
    print(f"🔍 Analysiere PDF: {pdf_path}")
    
    try:
        images = convert_from_path(str(pdf_path), dpi=300, poppler_path=POPPLER_PATH)
        print(f"✅ {len(images)} Seiten gefunden")
        
        for i, img in enumerate(images):
            print(f"\n📄 Seite {i+1}:")
            text = pytesseract.image_to_string(img, lang='deu', config='--psm 6')
            print("=" * 50)
            print(text)
            print("=" * 50)
            
            # Suche nach Schlüsselwörtern
            keywords = ['Fahrzeug', 'Kennzeichen', 'Referent', 'Netto', 'Brutto', 'Gesamt', 'Summe', 'EUR', '€']
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"🔑 Gefundene Schlüsselwörter: {found_keywords}")
            
            # Suche nach Zahlen (Beträge)
            amounts = re.findall(r'\d+[\d\.,]*\s*(?:EUR|€)', text)
            if amounts:
                print(f"💰 Gefundene Beträge: {amounts}")
            
            # Suche nach Kennzeichen (W-Format)
            license_plates = re.findall(r'W\s*\d{3,5}\s*[A-Z]*\s*T?X', text, re.IGNORECASE)
            if license_plates:
                print(f"🚗 Gefundene Kennzeichen: {license_plates}")
            
            print("\n")
            
    except Exception as e:
        print(f"❌ Fehler beim Analysieren: {e}")

if __name__ == "__main__":
    pdf_path = Path("rechnung.25003898.pdf")
    if pdf_path.exists():
        analyze_new_pdf(pdf_path)
    else:
        print(f"❌ Datei nicht gefunden: {pdf_path}") 