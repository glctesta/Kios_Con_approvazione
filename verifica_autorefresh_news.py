"""
Script di Test per Verificare il Sistema Auto-Refresh delle News

Questo script:
1. Inserisce una news di test nel database
2. Attende 5 minuti
3. Verifica che la news sia stata rilevata dal sistema
4. Pulisce la news di test

Utilizzo:
    python verifica_autorefresh_news.py
"""

import pyodbc
import time
from datetime import datetime, timedelta
import sys

# Configurazione database
DB_CONFIG = {
    'server': 'PC-PORTATILE-PC\\MSSQLSERVER02',
    'database': 'Employee',
    'trusted_connection': 'yes'
}


def crea_connessione():
    """Crea connessione al database"""
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"❌ Errore connessione database: {e}")
        return None


def inserisci_news_test():
    """Inserisce una news di test"""
    conn = crea_connessione()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Data di inizio e fine
        start_date = datetime.now()
        end_date = start_date + timedelta(hours=1)  # Valida per 1 ora
        
        test_message = f"🔄 TEST AUTO-REFRESH - Creata alle {start_date.strftime('%H:%M:%S')}"
        
        query = """
        INSERT INTO [Employee].[dbo].[News] 
            ([EmployeerId], [StartNews], [EndNews], [News], [Publisher], [IsMandatory])
        OUTPUT INSERTED.NewId
        VALUES 
            (NULL, ?, ?, ?, 'Test Sistema', 0)
        """
        
        cursor.execute(query, (start_date, end_date, test_message))
        
        # Recupera ID della news inserita
        news_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✅ News di test inserita con successo!")
        print(f"   ID: {news_id}")
        print(f"   Messaggio: {test_message}")
        print(f"   Valida fino alle: {end_date.strftime('%H:%M:%S')}")
        
        return news_id
        
    except Exception as e:
        print(f"❌ Errore inserimento news: {e}")
        return None
    finally:
        conn.close()


def verifica_news_presente(news_id):
    """Verifica se la news è presente nel risultato della query API"""
    conn = crea_connessione()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        current_date = datetime.now()
        
        query = """
        SELECT COUNT(*) 
        FROM [Employee].[dbo].[News]
        WHERE NewId = ? 
          AND ? >= StartNews 
          AND ? <= EndNews
        """
        
        cursor.execute(query, (news_id, current_date, current_date))
        count = cursor.fetchone()[0]
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Errore verifica news: {e}")
        return False
    finally:
        conn.close()


def elimina_news_test(news_id):
    """Elimina la news di test"""
    conn = crea_connessione()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        query = "DELETE FROM [Employee].[dbo].[News] WHERE NewId = ?"
        cursor.execute(query, (news_id,))
        conn.commit()
        
        print(f"🗑️  News di test eliminata (ID: {news_id})")
        return True
        
    except Exception as e:
        print(f"❌ Errore eliminazione news: {e}")
        return False
    finally:
        conn.close()


def main():
    """Funzione principale del test"""
    print("=" * 70)
    print("TEST SISTEMA AUTO-REFRESH NEWS")
    print("=" * 70)
    print()
    
    # Step 1: Inserisci news di test
    print("📝 STEP 1: Inserimento news di test...")
    news_id = inserisci_news_test()
    
    if not news_id:
        print("❌ Test fallito: impossibile inserire news di test")
        sys.exit(1)
    
    print()
    
    # Step 2: Verifica immediata
    print("🔍 STEP 2: Verifica immediata...")
    if verifica_news_presente(news_id):
        print("✅ News presente nel database e valida")
    else:
        print("⚠️  News non trovata (potrebbe essere un problema di date)")
    
    print()
    
    # Step 3: Informazioni per l'utente
    print("📋 STEP 3: Istruzioni per il test manuale")
    print("-" * 70)
    print("1. Aprire l'applicazione Kiosk nel browser")
    print("2. Navigare alla pagina principale (launcher)")
    print("3. Aprire la Console del browser (F12 → Console)")
    print("4. Attendere il prossimo auto-refresh (massimo 5 minuti)")
    print("5. Nella console dovreste vedere:")
    print("   - 'Auto-refresh news...'")
    print("   - 'News modificate, aggiornamento in corso...'")
    print("6. La news di test dovrebbe apparire nella rotazione")
    print()
    print(f"   Cercate il messaggio che contiene: 'TEST AUTO-REFRESH'")
    print("-" * 70)
    print()
    
    # Step 4: Attesa e countdown
    print("⏱️  STEP 4: Attesa per il prossimo auto-refresh...")
    print("    (Il sistema controlla ogni 5 minuti)")
    print()
    
    wait_minutes = 5
    wait_seconds = wait_minutes * 60
    
    user_input = input(f"Vuoi attendere {wait_minutes} minuti per il test automatico? (s/n): ")
    
    if user_input.lower() == 's':
        print()
        print(f"⏳ Attendere {wait_minutes} minuti...")
        
        for remaining in range(wait_seconds, 0, -30):
            mins = remaining // 60
            secs = remaining % 60
            print(f"   Tempo rimanente: {mins:02d}:{secs:02d}", end='\r')
            time.sleep(30)
        
        print()
        print("✅ Tempo di attesa completato!")
        print()
        
        # Verifica ancora presente
        if verifica_news_presente(news_id):
            print("✅ La news è ancora valida e dovrebbe essere stata rilevata")
        else:
            print("⚠️  La news potrebbe essere scaduta")
    else:
        print()
        print("⏩ Attesa automatica saltata")
    
    print()
    
    # Step 5: Cleanup
    user_cleanup = input("Vuoi eliminare la news di test? (s/n): ")
    
    if user_cleanup.lower() == 's':
        elimina_news_test(news_id)
    else:
        print(f"ℹ️  News di test mantenuta (ID: {news_id})")
        print(f"   Per eliminarla manualmente:")
        print(f"   DELETE FROM [Employee].[dbo].[News] WHERE NewId = {news_id}")
    
    print()
    print("=" * 70)
    print("TEST COMPLETATO")
    print("=" * 70)


if __name__ == "__main__":
    main()
