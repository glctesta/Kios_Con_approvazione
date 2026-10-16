"""
diagnose_news.py  —  Diagnostica tabella News
Esegui: python diagnose_news.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from db_connection import DatabaseConnection
from datetime import datetime

config_manager = ConfigManager()
db = DatabaseConnection(config_manager)

print()
print("=" * 65)
print("  DIAGNOSI TABELLA NEWS")
print("=" * 65)

try:
    conn = db.connect()
    cursor = conn.cursor()
    now = datetime.now()
    print(f"\nData/ora attuale  : {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Struttura colonne
    print("\n[1] Colonne della tabella Employee.dbo.News")
    print("-" * 65)
    try:
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_CATALOG = 'Employee' AND TABLE_NAME = 'News'
            ORDER BY ORDINAL_POSITION
        """)
        cols = cursor.fetchall()
        if cols:
            for c in cols:
                print(f"  {c[0]:<30} {c[1]:<15} nullable={c[2]}")
        else:
            print("  Tabella non trovata o vuota!")
    except Exception as e:
        print(f"  Errore: {e}")

    # 2. Tutte le news (senza filtro data)
    print("\n[2] Tutte le righe nella tabella (senza filtro data)")
    print("-" * 65)
    try:
        cursor.execute("SELECT TOP 20 * FROM [Employee].[dbo].[News] ORDER BY StartNews DESC")
        rows = cursor.fetchall()
        if rows:
            # header
            headers = [d[0] for d in cursor.description]
            print("  " + " | ".join(f"{h[:18]:<18}" for h in headers))
            print("  " + "-" * (21 * len(headers)))
            for r in rows:
                vals = []
                for v in r:
                    if hasattr(v, 'strftime'):
                        vals.append(v.strftime('%Y-%m-%d'))
                    elif v is None:
                        vals.append('NULL')
                    else:
                        vals.append(str(v)[:18])
                print("  " + " | ".join(f"{v:<18}" for v in vals))
        else:
            print("  Tabella VUOTA — nessuna riga trovata.")
    except Exception as e:
        print(f"  Errore: {e}")

    # 3. News visibili adesso (stessa query di app.py)
    print(f"\n[3] News visibili ADESSO ({now.strftime('%Y-%m-%d %H:%M')})")
    print("-" * 65)
    try:
        cursor.execute("""
            SELECT NewId, EmployeerId, StartNews, EndNews,
                   LEFT(News, 60) AS NewsPreview,
                   IsMandatory, Printable
            FROM [Employee].[dbo].[News]
            WHERE ? >= StartNews AND ? <= EndNews
            ORDER BY IsMandatory DESC, StartNews ASC
        """, (now, now))
        rows = cursor.fetchall()
        if rows:
            print(f"  Trovate {len(rows)} news attive:")
            for r in rows:
                print(f"\n  ID={r[0]}  EmployeerId={r[1]}  Mandatory={r[5]}  Printable={r[6]}")
                print(f"  Dal {r[2]}  al {r[3]}")
                print(f"  Testo: {r[4]}")
        else:
            print("  Nessuna news attiva per la data corrente.")
            print()
            print("  Possibili cause:")
            print("  - StartNews > oggi  (la news inizia in futuro)")
            print("  - EndNews   < oggi  (la news e' scaduta)")
            print("  - I campi data sono NULL")
    except Exception as e:
        print(f"  Errore query: {e}")
        import traceback
        traceback.print_exc()

    # 4. Controlla se esiste la colonna IsMandatory e Printable
    print("\n[4] Verifica colonne IsMandatory e Printable")
    print("-" * 65)
    for col in ('IsMandatory', 'Printable'):
        try:
            cursor.execute(f"SELECT TOP 1 {col} FROM [Employee].[dbo].[News]")
            cursor.fetchone()
            print(f"  {col:<15} OK")
        except Exception as e:
            print(f"  {col:<15} MANCANTE o ERRORE: {e}")

except Exception as e:
    print(f"\nERRORE CONNESSIONE: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 65)
input("Premi INVIO per chiudere...")
