"""Test standalone per absence_report"""
import sys
import traceback

print("=== TEST ABSENCE REPORT ===")

try:
    print("1. Import db_connection...")
    from db_connection import DatabaseConnection
    print("   OK")
    
    print("2. Import config_manager...")
    from config_manager import ConfigManager
    print("   OK")
    
    print("3. Import absence_report...")
    from absence_report import AbsenceReportGenerator
    print("   OK")
    
    print("4. Creazione ConfigManager...")
    cm = ConfigManager()
    print("   OK")
    
    print("5. Creazione DatabaseConnection...")
    db = DatabaseConnection(cm)
    print("   OK")
    
    print("6. Connessione database...")
    conn = db.connect()
    if conn:
        print("   OK - Connesso!")
    else:
        print("   ERRORE - Connessione fallita")
        sys.exit(1)
    
    print("7. Creazione AbsenceReportGenerator...")
    gen = AbsenceReportGenerator(conn)
    print("   OK")
    
    print("8. Test generazione report...")
    badge = "0002435935"
    year = 2025
    print(f"   Badge: {badge}, Anno: {year}")
    
    pdf_path = gen.generate_report(badge, year)
    
    if pdf_path:
        print(f"   OK - PDF generato: {pdf_path}")
    else:
        print("   ERRORE - Generazione fallita")
    
    print("\n=== TEST COMPLETATO CON SUCCESSO ===")
    
except Exception as e:
    print(f"\n!!! ERRORE: {str(e)} !!!")
    traceback.print_exc()
    sys.exit(1)
