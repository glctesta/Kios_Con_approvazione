import pyodbc
from db_connection import DatabaseConnection
from config_manager import ConfigManager

config_manager = ConfigManager()
db_conn = DatabaseConnection(config_manager)
conn = db_conn.connect()

if not conn:
    print("ERRORE: Impossibile connettersi al database")
else:
    cursor = conn.cursor()
    cursor.execute("SELECT DB_NAME()")
    dbname = cursor.fetchone()[0]
    print(f"Database attuale: {dbname}")
    conn.close()
