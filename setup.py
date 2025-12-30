"""
Script di Setup Iniziale
Configura database e verifica dipendenze
"""
import sys
import os

def check_dependencies():
    """Verifica che tutte le dipendenze siano installate"""
    print("🔍 Verifica dipendenze...")
    
    required_modules = [
        'flask',
        'pyodbc',
        'reportlab',
        'PIL',
        'cryptography'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - MANCANTE")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Moduli mancanti: {', '.join(missing)}")
        print("Esegui: pip install -r requirements.txt")
        return False
    
    print("✅ Tutte le dipendenze sono installate!\n")
    return True


def setup_database_config():
    """Configura connessione database"""
    print("📊 Configurazione Database SQL Server")
    print("=" * 50)
    
    from config_manager import ConfigManager
    
    # Chiedi credenziali
    print("\nInserisci le credenziali del database:")
    server = input("Server SQL (es: localhost\\SQLEXPRESS): ").strip()
    database = input("Database (default: Employee): ").strip() or "Employee"
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    # Salva configurazione
    try:
        config = ConfigManager()
        config.save_config(
            driver='ODBC Driver 18 for SQL Server',
            server=server,
            database=database,
            username=username,
            password=password
        )
        print("\n✅ Configurazione database salvata con successo!")
        return True
    except Exception as e:
        print(f"\n❌ Errore nel salvataggio configurazione: {str(e)}")
        return False


def test_database_connection():
    """Testa connessione al database"""
    print("\n🔌 Test connessione database...")
    
    try:
        from db_connection import DatabaseConnection
        from config_manager import ConfigManager
        
        config_manager = ConfigManager()
        db = DatabaseConnection(config_manager)
        
        conn = db.connect()
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        
        print(f"✅ Connessione riuscita!")
        print(f"   SQL Server: {version[:50]}...")
        
        db.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Errore connessione: {str(e)}")
        return False


def verify_images():
    """Verifica presenza immagini"""
    print("\n🖼️  Verifica immagini...")
    
    images = [
        ('Images/Image32.png', 'Logo aziendale'),
        ('Images/SignatureAdministrator.png', 'Firma amministratore')
    ]
    
    all_ok = True
    for path, desc in images:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✅ {desc}: {path} ({size} bytes)")
        else:
            print(f"  ❌ {desc}: {path} - NON TROVATO")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Alcune immagini mancano. Aggiungile nella cartella Images/")
    
    return all_ok


def create_temp_directory():
    """Crea directory temp per PDF"""
    print("\n📁 Creazione directory temp...")
    
    try:
        os.makedirs('temp', exist_ok=True)
        print("  ✅ Directory temp/ creata")
        return True
    except Exception as e:
        print(f"  ❌ Errore: {str(e)}")
        return False


def main():
    """Esegue setup completo"""
    print("=" * 60)
    print("🚀 SETUP SISTEMA GENERARE ADEVERINȚE")
    print("=" * 60)
    print()
    
    # 1. Verifica dipendenze
    if not check_dependencies():
        print("\n❌ Setup interrotto. Installa le dipendenze mancanti.")
        sys.exit(1)
    
    # 2. Crea directory temp
    create_temp_directory()
    
    # 3. Verifica immagini
    verify_images()
    
    # 4. Configura database
    print()
    risposta = input("Vuoi configurare la connessione al database? (s/n): ").lower()
    if risposta == 's':
        if setup_database_config():
            # 5. Test connessione
            test_database_connection()
    
    # Riepilogo finale
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETATO!")
    print("=" * 60)
    print()
    print("Prossimi passi:")
    print("1. Verifica che le immagini siano presenti in Images/")
    print("2. Avvia l'applicazione: python app.py")
    print("3. Apri browser: http://localhost:5000")
    print("4. Testa con un badge RFID")
    print()
    print("Per maggiori informazioni, leggi:")
    print("  - README.md (documentazione completa)")
    print("  - GUIDA_RAPIDA.md (guida rapida)")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrotto dall'utente.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {str(e)}")
        sys.exit(1)
