"""
Script per inserire una news di test VALIDA nel database
"""
import sys
sys.path.append('.')

from datetime import datetime, timedelta
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
    
    # Date per la news
    now = datetime.now()
    start_date = now - timedelta(hours=1)  # Iniziata 1 ora fa
    end_date = now + timedelta(days=7)     # Termina tra 7 giorni
    
    news_message = "Bine ați venit la sistemul Kiosk HR! Aceasta este o comunicare de test."
    publisher = "IT Department - Test"
    
    print(f"Inserimento news di test...")
    print(f"  Inizio: {start_date}")
    print(f"  Fine: {end_date}")
    print(f"  Messaggio: {news_message}")
    print("-" * 60)
    
    # Query di inserimento
    insert_query = """
    INSERT INTO [Employee].[dbo].[News] 
        ([EmployeerId], [StartNews], [EndNews], [News], [Publisher], [IsMandatory])
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    cursor.execute(insert_query, (
        2,              # EmployeerId
        start_date,     # StartNews
        end_date,       # EndNews
        news_message,   # News
        publisher,      # Publisher
        0               # IsMandatory (0 = normale, 1 = obbligatoria)
    ))
    
    conn.commit()
    
    print("✓ News inserita con successo!")
    
    # Verifica inserimento
    cursor.execute("SELECT @@IDENTITY")
    new_id = cursor.fetchone()[0]
    print(f"✓ ID news creata: {new_id}")
    
    # Verifica che sia attiva
    current_date = datetime.now()
    query_check = """
    SELECT NewId, StartNews, EndNews, News 
    FROM [Employee].[dbo].[News]
    WHERE NewId = ? AND ? >= StartNews AND ? <= EndNews
    """
    
    cursor.execute(query_check, (new_id, current_date, current_date))
    result = cursor.fetchone()
    
    if result:
        print(f"✓ News ATTIVA e visibile nel kiosk!")
        print(f"\nRiavviare il server (se non già fatto) per vedere la news.")
    else:
        print("✗ Attenzione: news inserita ma non risulta attiva")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("COMPLETATO! Aprire il browser su http://localhost:5000")
    print("=" * 60)
    
except Exception as e:
    print(f"ERRORE: {str(e)}")
    import traceback
    traceback.print_exc()
