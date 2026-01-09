"""
Script semplice per verificare news nel database
"""
import sys
sys.path.append('.')

from datetime import datetime
from config_manager import ConfigManager
from db_connection import DatabaseConnection

config_manager = ConfigManager()
db_connection = DatabaseConnection(config_manager)

try:
    conn = db_connection.connect()
    if not conn:
        print("ERRORE: Impossibile connettersi al database")
        sys.exit(1)
    
    cursor = conn.cursor()
    current_date = datetime.now()
    
    print(f"Data corrente: {current_date}")
    print("-" * 60)
    
    # Query per news attive
    query = """
    SELECT 
        NewId, StartNews, EndNews, News, Publisher, IsMandatory
    FROM [Employee].[dbo].[News]
    WHERE ? >= StartNews AND ? <= EndNews
    ORDER BY IsMandatory DESC, StartNews ASC
    """
    
    cursor.execute(query, (current_date, current_date))
    rows = cursor.fetchall()
    
    print(f"NEWS ATTIVE TROVATE: {len(rows)}")
    print("-" * 60)
    
    if rows:
        for idx, row in enumerate(rows, 1):
            print(f"\nNews #{idx}:")
            print(f"  ID: {row[0]}")
            print(f"  Periodo: {row[1]} -> {row[2]}")
            print(f"  Messaggio: {row[3][:100]}")
            print(f"  Publisher: {row[4]}")
            print(f"  Mandatory: {row[5]}")
    else:
        print("\nNESSUNA NEWS ATTIVA!")
        print("\nVerifica tutti i record nella tabella...")
        
        query_all = "SELECT NewId, StartNews, EndNews FROM [Employee].[dbo].[News]"
        cursor.execute(query_all)
        all_rows = cursor.fetchall()
        
        print(f"Totale record in tabella: {len(all_rows)}")
        
        if all_rows:
            for row in all_rows:
                is_active = row[1] <= current_date <= row[2]
                status = "ATTIVA" if is_active else "NON ATTIVA"
                print(f"  ID {row[0]}: {row[1]} -> {row[2]} [{status}]")
        else:
            print("TABELLA VUOTA - Nessun record trovato!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERRORE: {str(e)}")
    import traceback
    traceback.print_exc()
