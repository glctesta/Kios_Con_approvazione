from email_connector import EmailSender
import logging
import re
from typing import List, Optional


logger = logging.getLogger("TraceabilityRS")  # usa la config fatta in main.py

def get_email_recipients(conn, attribute: str = 'Sys_Email_Purchase') -> List[str]:
    """
    Recupera gli indirizzi email dei destinatari dal database per lo specifico attributo.
    Esempi di attributo: 'Sys_Email_Purchase', 'Sys_email_submission'
    """
    try:
        query = """
        SELECT [VALUE]
        FROM traceability_rs.dbo.settings
        WHERE atribute = ?
        """
        with conn.cursor() as cursor:
            cursor.execute(query, attribute)
            results = cursor.fetchall()

        email_list = [row[0] for row in results if row[0]]

        valid_emails = []
        for email in email_list:
            chunks = []
            if ';' in email:
                chunks = [e.strip() for e in email.split(';')]
            elif ',' in email:
                chunks = [e.strip() for e in email.split(',')]
            else:
                chunks = [email.strip()]
            valid_emails.extend([e for e in chunks if e and '@' in e])

        logger.info(f"Indirizzi email trovati per {attribute}: {valid_emails}")
        return valid_emails

    except Exception as e:
        logger.error(f"Errore nel recupero degli indirizzi email ({attribute}): {str(e)}")
        raise





def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    smtp_host: str = "vandewiele-com.mail.protection.outlook.com",
    smtp_port: int = 25,
    is_html: bool = False,  # <-- nuovo parametro opzionale, default False: compatibile
    timeout: int= 15
) -> None:
    """
    Invia l'email ai destinatari specificati.

    Args:
        recipients: Lista di indirizzi email destinatari
        subject: Oggetto dell'email
        body: Corpo dell'email (testo o HTML se is_html=True)
        smtp_host: Host SMTP
        smtp_port: Porta SMTP
        is_html: Se True invia il corpo come HTML (default: False)

    Note: Usa EmailSender già presente nel progetto.
    :param timeout:
    """
    if not recipients:
        logger.error("Nessun destinatario specificato per l'email")
        return

    try:
        sender = EmailSender(smtp_host, smtp_port)

        # ATTENZIONE: credenziali hardcoded – idealmente spostarle in config sicura
        sender.save_credentials(
            "Accounting@Eutron.it",
            "9jHgFhSs7Vf+"
        )

        # Invia email a OGNI destinatario (EmailSender.send_email accetta un singolo indirizzo)
        sent_count = 0
        for recipient in recipients:
            try:
                sender.send_email(
                    to_email=recipient.strip(),
                    subject=subject,
                    body=body,
                    is_html=is_html
                )
                sent_count += 1
                logger.info(f"Email inviata a {recipient}")
            except Exception as e:
                logger.error(f"Errore invio email a {recipient}: {str(e)}")
        
        logger.info(f"Email inviata con successo a {sent_count}/{len(recipients)} destinatari")
        print(f"Email inviata a {sent_count} destinatari")
    except Exception as e:
        logger.error(f"Errore nell'invio dell'email: {str(e)}")
        raise


def get_employee_work_email(conn, employee_name: str) -> Optional[str]:
    """
    Recupera l'indirizzo email lavorativo (WorkEmail) di un dipendente in base al nome completo.

    Args:
        conn: Connessione al database
        employee_name: Nome completo del dipendente (es. "TESTA GIANLUCA")

    Returns:
        L'indirizzo email lavorativo come stringa se trovato, altrimenti None
    """
    try:
        # Dividi il nome in cognome e nome
        # Assumendo formato "COGNOME NOME"
        parts = employee_name.strip().split()
        if len(parts) < 2:
            logger.warning(f"Formato nome non valido: {employee_name}")
            return None
        
        surname = parts[0]
        name = ' '.join(parts[1:])  # In caso di nomi composti
        
        query = """
        SELECT a.WorkEmail 
        FROM employee.dbo.employees e 
        INNER JOIN employee.dbo.EmployeeAddress a 
            ON a.EmployeeId = e.EmployeeId 
            AND a.DateOut IS NULL 
        INNER JOIN employee.dbo.employeehirehistory h 
            ON e.employeeid = h.employeeid 
            AND h.EndWorkDate IS NULL 
            AND h.employeerid = 2
        WHERE e.EmployeeSurname = ? AND e.EmployeeName = ?
        """

        with conn.cursor() as cursor:
            cursor.execute(query, (surname, name))
            row = cursor.fetchone()

        if row and row[0]:
            work_email = row[0].strip()
            logger.info(f"WorkEmail trovata per {employee_name}: {work_email}")
            return work_email

        logger.warning(f"Nessun risultato trovato per: {employee_name}")
        return None

    except Exception as e:
        logger.error(f"Errore nel recupero della WorkEmail per {employee_name}: {e}")
        raise


def log_service_operation(
    conn,
    username: str,
    service_name: str,
    success: bool,
    error_message: Optional[str] = None,
    additional_info: Optional[str] = None
) -> None:
    """
    Registra un'operazione del servizio nel database Employee.dbo.ServiceOperationLog
    
    Args:
        conn: Connessione al database
        username: Nome utente che ha richiesto il servizio (es. badge, nome dipendente)
        service_name: Nome del servizio richiesto (es. "Genera Certificato", "Richiesta Assenza")
        success: True se l'operazione è andata a buon fine, False altrimenti
        error_message: Messaggio di errore in caso di fallimento (opzionale)
        additional_info: Informazioni aggiuntive sull'operazione (opzionale)
    
    Note:
        La tabella ServiceOperationLog deve essere creata nel database Employee.
        Timestamp viene generato automaticamente dal database (GETDATE()).
    """
    try:
        query = """
        INSERT INTO Employee.dbo.ServiceOperationLog 
            (Username, ServiceName, Success, ErrorMessage, AdditionalInfo)
        VALUES (?, ?, ?, ?, ?)
        """
        
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    username[:100],  # Limita a 100 caratteri
                    service_name[:200],  # Limita a 200 caratteri
                    1 if success else 0,  # Converti bool a bit
                    error_message[:4000] if error_message else None,  # Limita lunghezza
                    additional_info[:4000] if additional_info else None  # Limita lunghezza
                )
            )
            conn.commit()
        
        logger.debug(f"Operazione loggata: {service_name} - {username} - {'Success' if success else 'Failed'}")
        
    except Exception as e:
        # Non sollevare eccezione per non bloccare il servizio principale
        # ma logga l'errore
        logger.error(f"Errore nel logging dell'operazione {service_name} per {username}: {e}")
        # Non fare raise per non interrompere il flusso principale