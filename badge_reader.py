"""
Badge Reader Module
Gestisce la lettura del badge RFID e il recupero dati dipendente
"""
import logging

logger = logging.getLogger(__name__)


class BadgeReader:
    def __init__(self, db_connection):
        self.conn = db_connection
    
    def normalize_badge_number(self, badge_number):
        """
        Normalizza il numero badge a 10 caratteri con padding di zeri a sinistra
        
        Args:
            badge_number: Numero badge letto dal lettore RFID
        
        Returns:
            Numero badge normalizzato a 10 caratteri
        """
        # Rimuovi spazi e converti a stringa
        badge_str = str(badge_number).strip()
        
        # Padding con zeri a sinistra fino a 10 caratteri
        normalized = badge_str.zfill(10)
        
        logger.info(f"Badge normalizzato: {badge_number} -> {normalized}")
        return normalized
    
    def get_employee_by_badge(self, badge_number):
        """
        Recupera dati dipendente tramite numero badge
        
        Args:
            badge_number: Numero badge RFID
        
        Returns:
            dict con dati dipendente o None se non trovato
        """
        try:
            # Normalizza numero badge
            normalized_badge = self.normalize_badge_number(badge_number)
            
            cursor = self.conn.cursor()
            
            query = """
            SELECT 
                H.EmployeeHireHistoryId,
                UPPER(E.EmployeeSurname + ' ' + E.EmployeeName) AS Employee,
                E.EmployeeId,
                E.EmployeeSex,
                BN.NoBadge
            FROM employee.dbo.employees E
            INNER JOIN employee.dbo.EmployeeHireHistory H 
                ON E.EmployeeId = H.EmployeeId
            INNER JOIN employee.dbo.EmployeeBadgeHistory B 
                ON H.EmployeeHireHistoryId = B.EmployeeHireHistoryId 
                AND B.DateOut IS NULL
            INNER JOIN employee.dbo.Badges BN 
                ON BN.BadgeId = B.BadgeID
            WHERE BN.NoBadge = ?
            """
            
            cursor.execute(query, (normalized_badge,))
            row = cursor.fetchone()
            
            if row:
                employee_data = {
                    'hire_history_id': row[0],
                    'full_name': row[1],
                    'employee_id': row[2],
                    'sex': row[3],
                    'badge_number': row[4]
                }
                
                logger.info(f"Dipendente trovato: {employee_data['full_name']} (Badge: {normalized_badge})")
                return employee_data
            else:
                logger.warning(f"Nessun dipendente trovato per badge: {normalized_badge}")
                return None
        
        except Exception as e:
            logger.error(f"Errore nella lettura badge: {str(e)}")
            raise
    
    def validate_badge_access(self, badge_number):
        """
        Valida se il badge ha accesso al sistema
        
        Args:
            badge_number: Numero badge RFID
        
        Returns:
            tuple (is_valid, employee_data, error_message)
        """
        try:
            employee_data = self.get_employee_by_badge(badge_number)
            
            if employee_data:
                return (True, employee_data, None)
            else:
                return (False, None, "Badge non riconosciuto o dipendente non attivo")
        
        except Exception as e:
            return (False, None, f"Errore di sistema: {str(e)}")
