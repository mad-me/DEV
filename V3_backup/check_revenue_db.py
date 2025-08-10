import sqlite3
import os

# Prüfe Revenue-DB
if os.path.exists('SQL/revenue.db'):
    conn = sqlite3.connect('SQL/revenue.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Revenue-DB Tabellen:', [t[0] for t in tables])
    
    # Prüfe Daten in W135CTX Tabelle
    if 'W135CTX' in [t[0] for t in tables]:
        cursor.execute("SELECT COUNT(*) FROM W135CTX")
        count = cursor.fetchone()[0]
        print(f'W135CTX Revenue-Daten: {count} Einträge')
        
        if count > 0:
            cursor.execute("SELECT DISTINCT cw FROM W135CTX ORDER BY cw")
            weeks = cursor.fetchall()
            print(f'W135CTX Wochen mit Daten: {[w[0] for w in weeks]}')
    
    conn.close()
else:
    print('Revenue-DB existiert nicht')

# Prüfe Running-Costs-DB
if os.path.exists('SQL/running_costs.db'):
    conn = sqlite3.connect('SQL/running_costs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Running-Costs-DB Tabellen:', [t[0] for t in tables])
    
    # Prüfe Daten in W135CTX Tabelle
    if 'W135CTX' in [t[0] for t in tables]:
        cursor.execute("SELECT COUNT(*) FROM W135CTX")
        count = cursor.fetchone()[0]
        print(f'W135CTX Running-Costs-Daten: {count} Einträge')
        
        if count > 0:
            cursor.execute("SELECT DISTINCT cw FROM W135CTX ORDER BY cw")
            weeks = cursor.fetchall()
            print(f'W135CTX Wochen mit Daten: {[w[0] for w in weeks]}')
    
    conn.close()
else:
    print('Running-Costs-DB existiert nicht')
