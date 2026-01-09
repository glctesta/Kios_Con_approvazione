"""
Script di test per verificare il recupero delle news dal database
"""
import sys
import io
# Configura UTF-8 per output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import datetime
sys.path.append('.')

from config_manager import ConfigManager
from db_connection import DatabaseConnection

def test_news_query():
    """Testa la query per recuperare le news attive"""
    print("=" * 60)
    print("TEST RECUPERO NEWS DA Employee.dbo.News")
    print("=" * 60)
    
    config_manager = ConfigManager()
    db_connection = DatabaseConnection(config_manager)
    
    try:
        conn = db_connection.connect()
        if not conn:
            print("❌ ERRORE: Impossibile connettersi al database")
            return
        
        cursor = conn.cursor()
        current_date = datetime.now()
        
        print(f"\n📅 Data/Ora corrente: {current_date}")
        print("\n" + "=" * 60)
        
        # Query per recuperare news attive
        query = """
        SELECT 
            NewId,
            EmployeerId,
            StartNews,
            EndNews,
            News,
            Publisher,
            IsMandatory
        FROM [Employee].[dbo].[News]
        WHERE ? >= StartNews AND ? <= EndNews
        ORDER BY IsMandatory DESC, StartNews ASC
        """
        
        print("\n🔍 Esecuzione query:")
        print(query)
        print(f"\nParametri: current_date = {current_date}")
        
        cursor.execute(query, (current_date, current_date))
        rows = cursor.fetchall()
        
        print("\n" + "=" * 60)
        print(f"📊 RISULTATI: {len(rows)} news trovate")
        print("=" * 60)
        
        if not rows:
            print("\n⚠️  Nessuna news attiva trovata al momento")
            print("\n💡 Suggerimenti:")
            print("   1. Verificare che esistano record nella tabella Employee.dbo.News")
            print("   2. Controllare che current_date sia compreso tra StartNews e EndNews")
            print("   3. Verificare i valori dei campi StartNews ed EndNews dei record esistenti")
        else:
            for idx, row in enumerate(rows, 1):
                print(f"\n📰 News #{idx}:")
                print(f"   ID: {row[0]}")
                print(f"   Employer ID: {row[1]}")
                print(f"   Inizio validità: {row[2]}")
                print(f"   Fine validità: {row[3]}")
                print(f"   Messaggio: {row[4][:100]}{'...' if len(row[4]) > 100 else ''}")
                print(f"   Pubblicato da: {row[5]}")
                print(f"   Obbligatorio: {'✅ SÌ' if row[6] else '⭕ NO'}")
        
        # Controlliamo anche tutti i record esistenti nella tabella
        print("\n" + "=" * 60)
        print("🔍 CONTROLLO TUTTI I RECORD NELLA TABELLA")
        print("=" * 60)
        
        query_all = """
        SELECT 
            NewId,
            StartNews,
            EndNews,
            News,
            Publisher,
            IsMandatory
        FROM [Employee].[dbo].[News]
        ORDER BY StartNews DESC
        """
        
        cursor.execute(query_all)
        all_rows = cursor.fetchall()
        
        print(f"\n📋 Totale record in tabella: {len(all_rows)}")
        
        if all_rows:
            for idx, row in enumerate(all_rows, 1):
                is_active = row[1] <= current_date <= row[2]
                status = "🟢 ATTIVA" if is_active else "🔴 NON ATTIVA"
                print(f"\n{status} - Record #{idx}:")
                print(f"   ID: {row[0]}")
                print(f"   Periodo: {row[1]} → {row[2]}")
                print(f"   Messaggio: {row[3][:80]}{'...' if len(row[3]) > 80 else ''}")
                print(f"   Publisher: {row[4]}")
                print(f"   Mandatory: {'✅' if row[5] else '⭕'}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Test completato con successo!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRORE durante il test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_news_query()
