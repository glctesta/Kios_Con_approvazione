"""
Script di test per verificare il funzionamento del Kiosk Request Logger
"""
import sys
from config_manager import ConfigManager
from db_connection import DatabaseConnection
from kiosk_request_logger import KioskRequestLogger

def test_logging():
    print("=" * 60)
    print("TEST KIOSK REQUEST LOGGER")
    print("=" * 60)
    print()
    
    try:
        # Inizializza connessione
        print("1. Inizializzazione database...")
        config_manager = ConfigManager()
        db_connection = DatabaseConnection(config_manager)
        print("   ✓ Database connection OK")
        
        # Inizializza logger
        print("\n2. Inizializzazione Kiosk Logger...")
        kiosk_logger = KioskRequestLogger(db_connection)
        print("   ✓ Kiosk Logger OK")
        
        # Test get IP
        print("\n3. Test recupero IP...")
        ip = kiosk_logger.get_client_ip()
        print(f"   ✓ IP rilevato: {ip}")
        
        # Test log generico
        print("\n4. Test logging richiesta generica...")
        result = kiosk_logger.log_request(
            badge_number="0000000001",
            request_what="TEST - Verifica Sistema Logging",
            executed=True
        )
        
        if result:
            print("   ✓ Richiesta registrata con successo!")
        else:
            print("   ✗ ERRORE: Richiesta NON registrata!")
            return False
        
        # Verifica in database
        print("\n5. Verifica record in database...")
        conn = db_connection.connect()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT TOP 5 
                    KiosRequestId,
                    RequestDate,
                    IpRequest,
                    RequestBy,
                    RequestWhat,
                    Executed
                FROM Employee.dbo.KiosRequestes
                ORDER BY RequestDate DESC
            """)
            
            rows = cursor.fetchall()
            
            if rows:
                print(f"   ✓ Trovati {len(rows)} record(i):")
                print()
                print("   | ID | Data/Ora           | IP              | Utente        | Richiesta")
                print("   " + "-" * 80)
                for row in rows:
                    print(f"   | {row[0]:3d} | {row[1]} | {row[2]:15s} | {row[3]:13s} | {row[4][:30]}")
            else:
                print("   ✗ NESSUN RECORD TROVATO!")
                return False
        
        print()
        print("=" * 60)
        print("✓✓✓ TEST COMPLETATO CON SUCCESSO! ✓✓✓")
        print("=" * 60)
        print()
        print("Il sistema di logging funziona correttamente.")
        print("Se le richieste dal Kiosk non vengono registrate,")
        print("verifica che l'applicazione sia stata riavviata.")
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗✗✗ ERRORE NEL TEST! ✗✗✗")
        print("=" * 60)
        print(f"\nErrore: {str(e)}")
        
        import traceback
        print("\nTraceback completo:")
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    success = test_logging()
    sys.exit(0 if success else 1)
