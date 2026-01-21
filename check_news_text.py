# -*- coding: utf-8 -*-
"""Verifica testo news dal database"""
from db_connection import DatabaseConnection
from config_manager import ConfigManager

config = ConfigManager()
db = DatabaseConnection(config)
if db.connect():
    cursor = db.connection.cursor()
    cursor.execute("""
        SELECT TOP 5 NewId, News, LEN(News) as Lunghezza, Printable
        FROM [Employee].[dbo].[News]
        ORDER BY NewId DESC
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        news_id, text, length, printable = row
        has_dots = '. ' in text
        has_exclaim = '! ' in text
        has_question = '? ' in text
        
        print(f"\n{'='*60}")
        print(f"NewId: {news_id}")
        print(f"Lunghezza: {length} caratteri")
        print(f"Printable: {printable} {'[STAMPABILE]' if printable == 1 else '[NON STAMPABILE]'}")
        print(f"Contiene '. ': {has_dots}")
        print(f"Contiene '! ': {has_exclaim}")
        print(f"Contiene '? ': {has_question}")
        print(f"{'='*60}")
        print(f"Testo:\n{text}")
        print(f"{'='*60}\n")
    
    cursor.close()
    db.disconnect()
else:
    print("ERRORE connessione database")
