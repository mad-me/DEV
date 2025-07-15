import re

# Teste das Regex-Muster
filename = "Abrechnungen 05_2025.pdf"
pattern = r'Abrechnungen?\s+(\d{2})_(\d{4})'
match = re.search(pattern, filename, re.IGNORECASE)

print(f"Dateiname: {filename}")
print(f"Regex-Muster: {pattern}")
print(f"Match gefunden: {match is not None}")

if match:
    month = int(match.group(1))
    year = int(match.group(2))
    table_name = f"{month:02d}_{str(year)[-2:]}"
    print(f"Monat: {month}")
    print(f"Jahr: {year}")
    print(f"Tabellenname: {table_name}")
else:
    print("Kein Match gefunden!") 