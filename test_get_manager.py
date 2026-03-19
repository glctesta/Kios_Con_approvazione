#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test per verificare cosa ritorna GetManager SP"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from db_connection import DatabaseConnection
from config_manager import ConfigManager

# Connetti al database
config_manager = ConfigManager()
db_conn = DatabaseConnection(config_manager)
conn = db_conn.connect()

if not conn:
    print("ERRORE: Impossibile connettersi al database")
    sys.exit(1)

cursor = conn.cursor()

# Test con hire_history_id = 2068 (dal log)
hire_history_id = 2068

print(f"\n=== TEST GET_MANAGER per hire_history_id={hire_history_id} ===\n")

# Prova 1: Query con DECLARE e SP (con SET NOCOUNT)
print("[TEST 1] DECLARE @Ids con SET NOCOUNT...")
query1 = """
SET NOCOUNT ON;
DECLARE @Ids dbo.EmployeeIdTableType;
INSERT INTO @Ids VALUES (?);
EXEC GetManager @Ids;
"""

try:
    cursor.execute(query1, (hire_history_id,))
    # Prova a leggere i risultati
    try:
        rows = cursor.fetchall()
        if rows:
            print(f"Righe ritornate: {len(rows)}")
            for i, row in enumerate(rows):
                print(f"  Riga {i}: {row}")
                print(f"    Tipo: {type(row)}, Numero colonne: {len(row)}")
                for j, field in enumerate(row):
                    print(f"      Campo {j}: tipo={type(field)}, valore='{field}'")
        else:
            print("Nessuna riga ritornata da fetchall()")
            # Prova nextset
            if cursor.nextset():
                print("Risultati in nextset()...")
                rows = cursor.fetchall()
                print(f"Righe ritornate: {len(rows)}")
                for i, row in enumerate(rows):
                    print(f"  Riga {i}: {row}")
    except Exception as fetch_error:
        print(f"Errore nel fetchall: {str(fetch_error)}")
except Exception as e:
    print(f"ERRORE: {str(e)}")
    import traceback
    traceback.print_exc()

# Prova 2: Esegui tutto in una transazione
print("\n[TEST 2] Transazione completa...")
query2 = """
DECLARE @Ids dbo.EmployeeIdTableType;
INSERT INTO @Ids VALUES (?);
EXEC GetManager @Ids;
"""

try:
    # Con pyodbc, devi usare una connessione con autocommit=False
    cursor = conn.cursor()
    cursor.execute(query2, (hire_history_id,))
    
    # Dopo l'esecuzione, prova a leggere i risultati
    rows = cursor.fetchall()
    print(f"Primo fetchall() ritorna: {len(rows) if rows else 0} righe")
    if rows:
        for i, row in enumerate(rows):
            print(f"  Riga {i}: {row}")
except Exception as e:
    print(f"ERRORE: {str(e)}")
    import traceback
    traceback.print_exc()

conn.close()
print("\n=== FINE TEST ===\n")
