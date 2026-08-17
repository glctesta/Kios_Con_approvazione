"""
Kiosk Request Logger
Module for tracking and logging all kiosk requests for usage monitoring
"""
import socket
import logging
from datetime import datetime
from typing import Optional
from company_config import EMPLOYER_ID

logger = logging.getLogger(__name__)


class KioskRequestLogger:
    """
    Gestisce il logging di tutte le richieste effettuate tramite il kiosk
    per monitorare l'utilizzo del sistema
    """

    def __init__(self, db_connection):
        """
        Inizializza il logger delle richieste

        Args:
            db_connection: Istanza DatabaseConnection
        """
        self.db_connection = db_connection

    def get_client_ip(self) -> str:
        """
        Recupera l'indirizzo IP del terminale/kiosk

        Returns:
            str: Indirizzo IP o 'Unknown' se non recuperabile
        """
        try:
            # Ottiene l'IP del host locale
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except Exception as e:
            logger.warning(f"Impossibile recuperare IP: {e}")
            return "Unknown"

    def get_employee_name_from_badge(self, badge_number: str) -> Optional[str]:
        """
        Recupera il nome del dipendente dal badge usando la query personalizzata

        Args:
            badge_number: Numero badge del dipendente (10 cifre)

        Returns:
            str: Nome completo dipendente o None se non trovato
        """
        try:
            conn = self.db_connection.connect()

            query = f"""
            SELECT e.EmployeeSurname + ' ' + e.EmployeeName AS EmployeeName 
            FROM ResetServices.dbo.tbuserkey U 
            INNER JOIN employee.dbo.employees e 
                ON e.employeeid = u.idanga 
            INNER JOIN employee.dbo.EmployeeHireHistory H 
                ON h.employeeid = e.EmployeeId 
                AND h.employeerid = {EMPLOYER_ID} 
                AND h.EndWorkDate IS NULL 
            INNER JOIN employee.dbo.EmployeeAddress A 
                ON a.EmployeeId = e.EmployeeId 
                AND a.dateout IS NULL
            INNER JOIN employee.dbo.EmployeeBadgeHistory BH 
                ON bh.EmployeeHireHistoryId = h.EmployeeHireHistoryId 
                AND bh.dateout IS NULL
            INNER JOIN employee.dbo.badges B 
                ON b.BadgeId = BH.BadgeID
            WHERE b.NoBadge = ?
            """

            with conn.cursor() as cursor:
                # Normalizza badge a 10 cifre
                normalized_badge = badge_number.zfill(10)
                cursor.execute(query, (normalized_badge,))
                result = cursor.fetchone()

                if result:
                    employee_name = result[0]
                    logger.debug(f"Badge {badge_number} -> {employee_name}")
                    return employee_name

                logger.warning(f"Nessun dipendente trovato per badge: {badge_number}")
                return None

        except Exception as e:
            logger.error(f"Errore nel recupero nome dipendente da badge: {e}")
            return None

    def log_request(
        self,
        badge_number: str,
        request_what: str,
        executed: bool = True,
        ip_override: Optional[str] = None
    ) -> bool:
        """
        Registra una richiesta nella tabella KiosRequestes

        Args:
            badge_number: Numero badge del dipendente
            request_what: Descrizione della richiesta (es. "Certificato Medico", "Richiesta Ferie")
            executed: Se la richiesta è stata eseguita con successo
            ip_override: IP del client (se non specificato, usa get_client_ip())

        Returns:
            bool: True se registrato con successo, False altrimenti
        """
        try:
            conn = self.db_connection.connect()

            # Recupera nome dipendente dal badge
            employee_name = self.get_employee_name_from_badge(badge_number)
            if not employee_name:
                employee_name = f"Badge_{badge_number}"

            # Recupera IP
            ip_address = ip_override if ip_override else self.get_client_ip()

            # Inserisci nella tabella KiosRequestes
            query = """
            INSERT INTO [Employee].[dbo].[KiosRequestes]
                ([RequestDate], [IpRequest], [RequestBy], [RequestWhat], [Executed])
            VALUES
                (GETDATE(), ?, ?, ?, ?)
            """

            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        ip_address,
                        employee_name,
                        request_what,
                        1 if executed else 0
                    )
                )
                conn.commit()

            logger.info(
                f"Richiesta loggata: {employee_name} - {request_what} - IP: {ip_address}"
            )
            return True

        except Exception as e:
            logger.error(f"Errore nel logging della richiesta kiosk: {e}")
            # Non fare raise per non bloccare il flusso principale
            return False

    def log_certificate_request(self, badge_number: str, reason: str, executed: bool = True) -> bool:
        """
        Log specifico per richieste certificato

        Args:
            badge_number: Numero badge
            reason: Motivo del certificato
            executed: Se generato con successo

        Returns:
            bool: True se registrato
        """
        request_what = f"Certificato - {reason}"
        return self.log_request(badge_number, request_what, executed)

    def log_absence_report_request(self, badge_number: str, year: int, executed: bool = True) -> bool:
        """
        Log specifico per report assenze

        Args:
            badge_number: Numero badge
            year: Anno del report
            executed: Se generato con successo

        Returns:
            bool: True se registrato
        """
        request_what = f"Raport Absențe - Anno {year}"
        return self.log_request(badge_number, request_what, executed)

    def log_absence_request_submission(
        self,
        badge_number: str,
        request_type: str,
        executed: bool = True
    ) -> bool:
        """
        Log specifico per sottomissione richieste assenza

        Args:
            badge_number: Numero badge
            request_type: Tipo di richiesta (es. "Ferie", "Malattia")
            executed: Se registrata con successo

        Returns:
            bool: True se registrato
        """
        request_what = f"Cerere Absență - {request_type}"
        return self.log_request(badge_number, request_what, executed)

    def log_request_status_check(self, badge_number: str, executed: bool = True) -> bool:
        """
        Log specifico per verifica stato richieste

        Args:
            badge_number: Numero badge
            executed: Se operazione riuscita

        Returns:
            bool: True se registrato
        """
        request_what = "Verificare Stare Cerere"
        return self.log_request(badge_number, request_what, executed)
