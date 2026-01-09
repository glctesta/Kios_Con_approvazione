"""
Script per verificare news e salvare output su file
"""
import sys
sys.path.append('.')

from datetime import datetime
from config_manager import ConfigManager
from db_connection import DatabaseConnection

def main():
    config_manager = ConfigManager()
    db_connection = DatabaseConnection(config_manager)
    
    output_lines = []
    
    try:
        conn = db_connection.connect()
        if not conn:
            output_lines.append("ERRORE: Impossibile connettersi al database")
            return output_lines
        
        cursor = conn.cursor()
        current_date = datetime.now()
        
        output_lines.append(f"Data corrente: {current_date}")
        output_lines.append("=" * 80)
        
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
        
        output_lines.append(f"\n>>> NEWS ATTIVE TROVATE: {len(rows)}")
        output_lines.append("=" * 80)
        
        if rows:
            for idx, row in enumerate(rows, 1):
                output_lines.append(f"\nNews #{idx}:")
                output_lines.append(f"  ID: {row[0]}")
                output_lines.append(f"  Inizio: {row[1]}")
                output_lines.append(f"  Fine: {row[2]}")
                output_lines.append(f"  Messaggio: {row[3][:150]}")
                output_lines.append(f"  Publisher: {row[4]}")
                output_lines.append(f"  Mandatory: {row[5]}")
        else:
            output_lines.append("\n>>> NESSUNA NEWS ATTIVA AL MOMENTO!")
            output_lines.append("\nVerifica TUTTI i record nella tabella...")
            output_lines.append("=" * 80)
            
            query_all = """
            SELECT NewId, StartNews, EndNews, News, Publisher, IsMandatory 
            FROM [Employee].[dbo].[News]
            ORDER BY StartNews DESC
            """
            cursor.execute(query_all)
            all_rows = cursor.fetchall()
            
            output_lines.append(f"\nTotale record in tabella: {len(all_rows)}")
            
            if all_rows:
                for row in all_rows:
                    is_active = row[1] <= current_date <= row[2]
                    status = "ATTIVA" if is_active else "NON ATTIVA"
                    output_lines.append(f"\n[{status}] ID {row[0]}:")
                    output_lines.append(f"  Periodo: {row[1]} -> {row[2]}")
                    output_lines.append(f"  Messaggio: {row[3][:100]}")
                    output_lines.append(f"  Publisher: {row[4]}")
                    
                    # Spiega perché non è attiva
                    if not is_active:
                        if current_date < row[1]:
                            output_lines.append(f"  MOTIVO: Inizia in futuro (tra {(row[1] - current_date).days} giorni)")
                        elif current_date > row[2]:
                            delta = current_date - row[2]
                            if delta.days > 0:
                                output_lines.append(f"  MOTIVO: Scaduta {delta.days} giorni fa")
                            else:
                                hours = delta.seconds // 3600
                                minutes = (delta.seconds % 3600) // 60
                                output_lines.append(f"  MOTIVO: Scaduta {hours}h {minutes}m fa")
            else:
                output_lines.append("\nLA TABELLA E' COMPLETAMENTE VUOTA!")
                output_lines.append("Eseguire INSERT per creare nuove news.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        output_lines.append(f"\nERRORE: {str(e)}")
        import traceback
        output_lines.append(traceback.format_exc())
    
    return output_lines

if __name__ == '__main__':
    lines = main()
    
    # Stampa a console
    for line in lines:
        print(line)
    
    # Salva su file
    with open('news_check_result.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("\n" + "=" * 80)
    print("Output salvato in: news_check_result.log")
