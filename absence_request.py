"""
Modulo Richiesta Assenza
Gestisce le richieste di assenza (ferie, permessi, ecc.)
"""

import logging
import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from utils import log_service_operation

logger = logging.getLogger(__name__)


class AbsenceRequestManager:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.logo_path = 'logo.png'
        
        # Registra font DejaVuSans per caratteri rumeni
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
            self.font_name = 'DejaVuSans'
            self.font_bold = 'DejaVuSans-Bold'
        except Exception as e:
            logger.warning(f"Font DejaVuSans non disponibili: {e}")
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
    
    def get_request_types(self):
        """Recupera tipi di richiesta disponibili"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT 
                IDRequestType,
                RequestName,
                IsConsideredEntireDay
            FROM [Timeclocking].[dbo].[RequestType]
            WHERE IDRequestType IN (1, 7, 10, 12)
            ORDER BY RequestName
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            request_types = []
            for row in rows:
                request_types.append({
                    'id': row[0],
                    'name': row[1],
                    'entire_day': row[2]
                })
            
            return request_types
            
        except Exception as e:
            logger.error(f"Errore recupero tipi richiesta: {str(e)}")
            return []
    
    def get_holidays(self, year):
        """Recupera giorni festivi per un anno"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT DISTINCT
                DATEFROMPARTS(YearPublicHoliday, MonthPublicHoliday, DayPublicHoliday) AS DataFestivo
            FROM [Timeclocking].[dbo].[PublicHoliday]
            WHERE YearPublicHoliday = ?
            """
            
            cursor.execute(query, (year,))
            rows = cursor.fetchall()
            
            holidays = [row[0] for row in rows]
            return holidays
            
        except Exception as e:
            logger.error(f"Errore recupero festività: {str(e)}")
            return []
    
    def calculate_working_days(self, start_date, end_date, holidays):
        """Calcola giorni lavorativi escludendo weekend e festività"""
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Verifica se è weekend (sabato=5, domenica=6)
            if current_date.weekday() < 5:  # Lunedì=0, Venerdì=4
                # Verifica se non è festivo
                if current_date not in holidays:
                    working_days += 1
            
            current_date += timedelta(days=1)
        
        return working_days
    
    def get_available_vacation_days(self, badge_number, year):
        """Calcola giorni di ferie disponibili per un dipendente"""
        try:
            cursor = self.conn.cursor()
            
            # Query complessa per calcolare ferie disponibili
            query = """
            DECLARE @NoBadge VARCHAR(50) = ?
            DECLARE @Anno INT = ?
            DECLARE @DataRiferimento DATE = GETDATE()
            DECLARE @InizioAnno DATE = DATEFROMPARTS(@Anno, 1, 1)
            DECLARE @FineAnno DATE = DATEFROMPARTS(@Anno, 12, 31)

            ;WITH 
            Numbers AS (
                SELECT a.n + b.n + c.n AS n 
                FROM (
                    SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 
                    UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
                ) a
                CROSS JOIN (
                    SELECT 0 AS n UNION ALL SELECT 10 UNION ALL SELECT 20 UNION ALL SELECT 30 UNION ALL SELECT 40 
                    UNION ALL SELECT 50 UNION ALL SELECT 60 UNION ALL SELECT 70 UNION ALL SELECT 80 UNION ALL SELECT 90
                ) b
                CROSS JOIN (
                    SELECT 0 AS n UNION ALL SELECT 100 UNION ALL SELECT 200 UNION ALL SELECT 300
                ) c
                WHERE a.n + b.n + c.n <= 365
            ),
            BonusAnzianitaCTE AS (
                SELECT 
                    noYears,
                    FixValueOnBrutSalary AS GiorniBonus
                FROM 
                    [Employee].[dbo].[BonusTypeSeniotiry]
                WHERE 
                    BonusTypeValueId = 4 
                    AND dateout IS NULL
            ),
            FestiviCTE AS (
                SELECT DISTINCT
                    DATEFROMPARTS(YearPublicHoliday, MonthPublicHoliday, DayPublicHoliday) AS DataFestivo
                FROM 
                    [Timeclocking].[dbo].[PublicHoliday]
                WHERE 
                    YearPublicHoliday BETWEEN @Anno - 50 AND @Anno + 1
            ),
            CalcoloAnzianitaCTE AS (
                SELECT 
                    te.IDEmployee,
                    h.EmployeeHireHistoryId,
                    e.EmployeeName,
                    e.EmployeeSurname,
                    b.NoBadge,
                    h.HireDate,
                    h.HolidayPerYear,
                    CASE 
                        WHEN h.HireDate <= @DataRiferimento THEN
                            CASE 
                                WHEN MONTH(@DataRiferimento) > MONTH(h.HireDate) 
                                    OR (MONTH(@DataRiferimento) = MONTH(h.HireDate) AND DAY(@DataRiferimento) >= DAY(h.HireDate))
                                THEN DATEDIFF(YEAR, h.HireDate, @DataRiferimento)
                                ELSE DATEDIFF(YEAR, h.HireDate, @DataRiferimento) - 1
                            END
                        ELSE 0
                    END AS Anni
                FROM 
                    employee.dbo.employees E
                    INNER JOIN employee.dbo.EmployeeHireHistory H 
                        ON e.EmployeeId = h.EmployeeId 
                        AND h.EmployeerId = 2 
                        AND h.EndWorkDate IS NULL
                    INNER JOIN [Timeclocking].[dbo].[Employee] TE 
                        ON e.EmployeeNID COLLATE Latin1_General_CI_AI = te.UniqueID COLLATE Latin1_General_CI_AI
                        AND te.DataStop IS NULL
                    INNER JOIN employee.dbo.EmployeeBadgeHistory BH 
                        ON h.EmployeeHireHistoryId = bh.EmployeeHireHistoryId 
                        AND bh.DateOut IS NULL
                    INNER JOIN employee.dbo.Badges B 
                        ON bh.BadgeID = b.BadgeId
                WHERE 
                    b.NoBadge COLLATE Latin1_General_CI_AI = @NoBadge COLLATE Latin1_General_CI_AI
            ),
            FerieSpettantiCTE AS (
                SELECT 
                    C.*,
                    ISNULL((
                        SELECT TOP 1 GiorniBonus 
                        FROM BonusAnzianitaCTE 
                        WHERE noYears <= C.Anni
                        ORDER BY noYears DESC
                    ), 0) AS GiorniBonusAnzianita,
                    CASE 
                        WHEN YEAR(C.HireDate) = @Anno THEN 
                            CEILING(CAST(C.HolidayPerYear AS FLOAT) * 
                                   (DATEDIFF(DAY, C.HireDate, @DataRiferimento) + 1) / 
                                   (CASE WHEN (@Anno % 4 = 0 AND @Anno % 100 != 0) OR (@Anno % 400 = 0) 
                                         THEN 366 ELSE 365 END))
                        WHEN YEAR(C.HireDate) < @Anno THEN 
                            C.HolidayPerYear
                        ELSE 
                            0
                    END AS FerieAnnoCorrente
                FROM CalcoloAnzianitaCTE C
            ),
            FerieSpettantiPerAnnoCTE AS (
                SELECT 
                    F.IDEmployee,
                    YEAR(F.HireDate) + (N.n / 10) AS Anno,
                    CASE 
                        WHEN YEAR(F.HireDate) = YEAR(F.HireDate) + (N.n / 10) THEN 
                            CEILING(CAST(F.HolidayPerYear AS FLOAT) * 
                                   (DATEDIFF(DAY, F.HireDate, DATEFROMPARTS(YEAR(F.HireDate) + (N.n / 10), 12, 31)) + 1) / 
                                   (CASE WHEN ((YEAR(F.HireDate) + (N.n / 10)) % 4 = 0 AND (YEAR(F.HireDate) + (N.n / 10)) % 100 != 0) 
                                          OR ((YEAR(F.HireDate) + (N.n / 10)) % 400 = 0) 
                                         THEN 366 ELSE 365 END))
                        WHEN YEAR(F.HireDate) < YEAR(F.HireDate) + (N.n / 10) THEN 
                            F.HolidayPerYear
                        ELSE 
                            0
                    END AS FerieSpettanti
                FROM 
                    FerieSpettantiCTE F
                    CROSS JOIN Numbers N
                WHERE 
                    N.n % 10 = 0
                    AND (N.n / 10) <= 30
                    AND YEAR(F.HireDate) + (N.n / 10) < @Anno
            ),
            FerieSpettantiAnniPrecedentiCTE AS (
                SELECT 
                    IDEmployee,
                    SUM(FerieSpettanti) AS TotaleFerieSpettantiAnniPrecedenti
                FROM 
                    FerieSpettantiPerAnnoCTE
                GROUP BY 
                    IDEmployee
            ),
            GiorniAssenzeEspansi AS (
                SELECT 
                    D.IDEmployee,
                    D.IDRequestType,
                    DATEADD(DAY, N.n, D.DateFrom) AS DataCorrente,
                    CASE 
                        WHEN DATEADD(DAY, N.n, D.DateFrom) < @InizioAnno THEN 1
                        ELSE 0
                    END AS IsAnniPrecedenti,
                    CASE 
                        WHEN DATEADD(DAY, N.n, D.DateFrom) >= @InizioAnno 
                            AND DATEADD(DAY, N.n, D.DateFrom) <= @FineAnno THEN 1
                        ELSE 0
                    END AS IsAnnoCorrente,
                    CASE 
                        WHEN DATEPART(WEEKDAY, DATEADD(DAY, N.n, D.DateFrom)) IN (1, 7) THEN 0
                        WHEN EXISTS (
                            SELECT 1 
                            FROM FestiviCTE F 
                            WHERE F.DataFestivo = DATEADD(DAY, N.n, D.DateFrom)
                        ) THEN 0
                        ELSE 1
                    END AS IsGiornoLavorativo
                FROM 
                    [Timeclocking].[dbo].[EmployeeRequestEntireDay] D
                    CROSS JOIN Numbers N
                WHERE 
                    DATEADD(DAY, N.n, D.DateFrom) <= D.DateTo
                    AND D.DateFrom <= DATEADD(YEAR, 1, @FineAnno)
            ),
            FerieUsateAnniPrecedentiCTE AS (
                SELECT 
                    IDEmployee,
                    SUM(IsGiornoLavorativo) AS FerieUsateAnniPrecedenti
                FROM 
                    GiorniAssenzeEspansi
                WHERE 
                    IDRequestType = 1
                    AND IsAnniPrecedenti = 1
                GROUP BY 
                    IDEmployee
            ),
            FerieUsateAnnoCorrenteCTE AS (
                SELECT 
                    IDEmployee,
                    SUM(IsGiornoLavorativo) AS FerieUsateAnnoCorrente
                FROM 
                    GiorniAssenzeEspansi
                WHERE 
                    IDRequestType = 1
                    AND IsAnnoCorrente = 1
                GROUP BY 
                    IDEmployee
            )
            SELECT 
                F.IDEmployee,
                F.EmployeeHireHistoryId,
                F.EmployeeName,
                F.EmployeeSurname,
                F.NoBadge,
                F.FerieAnnoCorrente + F.GiorniBonusAnzianita + 
                (ISNULL(FSAP.TotaleFerieSpettantiAnniPrecedenti, 0) - ISNULL(FUAP.FerieUsateAnniPrecedenti, 0)) - 
                ISNULL(FUAC.FerieUsateAnnoCorrente, 0) AS GiorniDisponibili
            FROM 
                FerieSpettantiCTE F
                LEFT JOIN FerieSpettantiAnniPrecedentiCTE FSAP ON F.IDEmployee = FSAP.IDEmployee
                LEFT JOIN FerieUsateAnniPrecedentiCTE FUAP ON F.IDEmployee = FUAP.IDEmployee
                LEFT JOIN FerieUsateAnnoCorrenteCTE FUAC ON F.IDEmployee = FUAC.IDEmployee
            """
            
            cursor.execute(query, (badge_number, year))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id_employee': row[0],
                    'hire_history_id': row[1],
                    'employee_name': row[2],
                    'employee_surname': row[3],
                    'badge_number': row[4],
                    'available_days': int(row[5]) if row[5] else 0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Errore calcolo giorni disponibili: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def check_duplicate_request(self, hire_history_id, request_type_id, date_start, date_end):
        """Verifica se esiste già una richiesta uguale"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT COUNT(*) AS NumDuplicates
            FROM [Employee].[dbo].[AbsenceRequestes]
            WHERE [EmployrrHireHistoryId] = ?
                AND [IDRequestType] = ?
                AND [DateStart] = ?
                AND [DateEnd] = ?
                AND [Approved] IS NOT NULL  -- Solo richieste già processate
            """
            
            cursor.execute(query, (hire_history_id, request_type_id, date_start, date_end))
            row = cursor.fetchone()
            
            num_duplicates = int(row[0]) if row else 0
            
            if num_duplicates > 0:
                logger.warning(f"Richiesta duplicata trovata: {num_duplicates} occorrenze")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Errore verifica duplicati: {str(e)}")
            # In caso di errore, permettiamo la richiesta (fail-safe)
            return False
    
    def validate_absence_date_rule(self, request_type_id, date_start):
        """
        Verifica se la data di inizio assenza rispetta le regole DayNoZone.
        
        Returns:
            dict: {
                'valid': bool,
                'message': str (messaggio errore in rumeno se non valido),
                'day_no_zone': int (numero di giorni di preavviso richiesti)
            }
        """
        try:
            cursor = self.conn.cursor()
            
            # Verifica se esiste una regola DayNoZone per questo tipo di richiesta
            query = """
            SELECT [DayNoZone]
            FROM [Employee].[dbo].[AbsenceRules]
            WHERE [IDRequestType] = ?
                AND [DayNoZone] IS NOT NULL
                AND [DateOut] IS NULL
            """
            
            cursor.execute(query, (request_type_id,))
            row = cursor.fetchone()
            
            # Se non c'è regola, la validazione passa
            if not row or row[0] is None:
                return {
                    'valid': True,
                    'message': '',
                    'day_no_zone': 0
                }
            
            day_no_zone = int(row[0])
            
            # Calcola la data minima consentita (oggi + DayNoZone giorni)
            today = datetime.now().date()
            min_allowed_date = today + timedelta(days=day_no_zone)
            
            # Converti date_start in date se è datetime
            if isinstance(date_start, datetime):
                date_start_check = date_start.date()
            else:
                date_start_check = date_start
            
            # Verifica se la data di inizio è valida
            if date_start_check < min_allowed_date:
                # Formatta la data massima per la richiesta in formato rumeno
                max_request_date_str = min_allowed_date.strftime('%d.%m.%Y')
                
                # Messaggio in rumeno
                message = (
                    f"ATENȚIE: Cererea nu poate fi înregistrată!\n\n"
                    f"Data maximă pentru înregistrarea acestei cereri este {max_request_date_str}.\n\n"
                    f"Conform regulilor companiei, această cerere trebuie înregistrată "
                    f"cu cel puțin {day_no_zone} zile înainte.\n\n"
                    f"Pentru cazuri speciale, vă rugăm să contactați responsabilul dumneavoastră direct."
                )
                
                logger.warning(
                    f"Validazione fallita: data {date_start_check} < data minima {min_allowed_date} "
                    f"(DayNoZone={day_no_zone})"
                )
                
                return {
                    'valid': False,
                    'message': message,
                    'day_no_zone': day_no_zone
                }
            
            # Validazione superata
            return {
                'valid': True,
                'message': '',
                'day_no_zone': day_no_zone
            }
            
        except Exception as e:
            logger.error(f"Errore validazione regole data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # In caso di errore, permettiamo la richiesta (fail-safe)
            return {
                'valid': True,
                'message': '',
                'day_no_zone': 0
            }
    
    def create_registry_entry(self, year, request_date, issued_by, employeer_id=2):
        """Crea entry nel registro tramite stored procedure"""
        try:
            cursor = self.conn.cursor()
            
            # Prepara parametri per SP
            registry_type_id = 1000
            
            # Con pyodbc, per recuperare OUTPUT parameter devo usare una query separata
            # Esegui stored procedure
            sql = """
            DECLARE @RegistroId INT
            
            EXEC [Employee].[dbo].[Registro]
                @RegistryTypeId = ?,
                @anno = ?,
                @DataDocumento = ?,
                @IussedBy = ?,
                @EmployeerId = ?,
                @RegistroId = @RegistroId OUTPUT
            
            SELECT @RegistroId AS RegistroId
            """
            
            cursor.execute(sql, (registry_type_id, year, request_date, issued_by, employeer_id))
            
            # Recupera ID generato
            row = cursor.fetchone()
            result_id = int(row[0]) if row and row[0] else None
            
            self.conn.commit()
            
            logger.info(f"Registry entry creato: RegistroId = {result_id}")
            
            return result_id
            
        except Exception as e:
            logger.error(f"Errore creazione registry: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.conn.rollback()
            return None
    
    def save_absence_request(self, registro_id, hire_history_id, request_type_id, 
                            date_start, date_end, from_time=None, to_time=None,
                            username="Unknown", request_type_name="Richiesta Assenza"):
        """Salva richiesta assenza nel database"""
        try:
            cursor = self.conn.cursor()
            
            # Con pyodbc, devo usare SET NOCOUNT ON per evitare problemi con INSERT + SELECT
            query = """
            SET NOCOUNT ON
            
            INSERT INTO [Employee].[dbo].[AbsenceRequestes]
                ([RegistroId], [EmployrrHireHistoryId], [IDRequestType], 
                 [DateStart], [DateEnd], [FromTime], [ToTime], 
                 [Approved], [ApprovedBy], [DateSys])
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL, GETDATE())
            
            SELECT SCOPE_IDENTITY() AS AbsenceRequestId
            """
            
            cursor.execute(query, (registro_id, hire_history_id, request_type_id, 
                                  date_start, date_end, from_time, to_time))
            
            row = cursor.fetchone()
            absence_request_id = int(row[0]) if row and row[0] else None
            
            self.conn.commit()
            
            # Log dettagliato con orari se presenti
            time_info = ""
            if from_time and to_time:
                time_info = f", Orario: {from_time} - {to_time}"
            
            logger.info(f"Richiesta assenza salvata: AbsenceRequestId = {absence_request_id}{time_info}")
            
            # Log operazione riuscita
            log_service_operation(
                self.conn,
                username=username,
                service_name=f"Richiesta Assenza - {request_type_name}",
                success=True,
                additional_info=f"Periodo: {date_start} - {date_end}{time_info}, RequestId: {absence_request_id}"
            )
            
            return absence_request_id
            
        except Exception as e:
            logger.error(f"Errore salvataggio richiesta: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.conn.rollback()
            
            # Log operazione fallita
            log_service_operation(
                self.conn,
                username=username,
                service_name=f"Richiesta Assenza - {request_type_name}",
                success=False,
                error_message=str(e)
            )
            
            return None
    
    def get_manager_emails(self, employee_hire_history_id):
        """Recupera email manager tramite stored procedure GetManager"""
        try:
            cursor = self.conn.cursor()
            
            # Crea e popola la table variable
            # Nota: con pyodbc non possiamo usare direttamente table-valued parameters
            # Dobbiamo usare un approccio alternativo
            query = """
            DECLARE @Ids dbo.EmployeeIdTableType;
            
            INSERT INTO @Ids VALUES (?);
            
            -- Esegui la SP
            EXEC GetManager @Ids;
            """
            
            cursor.execute(query, (employee_hire_history_id,))
            rows = cursor.fetchall()
            
            emails = []
            for row in rows:
                # Assumo che la SP restituisca email nella prima colonna
                if row[0]:
                    email = row[0].strip()
                    if email and '@' in email:
                        emails.append(email)
            
            logger.info(f"Email manager trovate: {emails}")
            return emails
            
        except Exception as e:
            logger.error(f"Errore recupero email manager: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # In caso di errore, restituisci lista vuota invece di bloccare
            return []
    
    def get_registry_info(self, registro_id):
        """Recupera informazioni registro"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT DocName, DocDate
            FROM [Employee].[dbo].[Registry]
            WHERE RegistroId = ?
            """
            
            cursor.execute(query, (registro_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'doc_name': row[0],
                    'doc_date': row[1]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Errore recupero registry info: {str(e)}")
            return None
    
    def generate_confirmation_pdf(self, employee_data, request_data, registry_info):
        """Genera PDF di conferma richiesta"""
        try:
            # Crea cartella temp
            os.makedirs('temp', exist_ok=True)
            
            # Nome file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"Confirmare_Cerere_{registry_info['doc_name']}_{timestamp}.pdf"
            pdf_path = os.path.join('temp', pdf_filename)
            
            # Crea PDF
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            
            # Logo
            y = height - 60
            if os.path.exists(self.logo_path):
                try:
                    logo = ImageReader(self.logo_path)
                    c.drawImage(logo, 50, y, width=100, height=40, preserveAspectRatio=True)
                except:
                    pass
            
            # Titolo
            y = height - 120
            c.setFont(self.font_bold, 18)
            c.drawCentredString(width / 2, y, "CONFIRMARE CERERE ABSENȚĂ")
            
            # Numero richiesta
            y -= 40
            c.setFont(self.font_bold, 14)
            c.drawCentredString(width / 2, y, f"Nr. {registry_info['doc_name']}")
            
            y -= 20
            c.setFont(self.font_name, 10)
            c.drawCentredString(width / 2, y, 
                              f"Data: {registry_info['doc_date'].strftime('%d.%m.%Y')}")
            
            # Separatore
            y -= 30
            c.line(50, y, width - 50, y)
            
            # Dati dipendente
            y -= 40
            c.setFont(self.font_bold, 12)
            c.drawString(50, y, "DATE ANGAJAT")
            
            y -= 25
            c.setFont(self.font_name, 10)
            c.drawString(50, y, f"Nume: {employee_data['surname']} {employee_data['name']}")
            
            y -= 20
            c.drawString(50, y, f"Badge: {employee_data['badge']}")
            
            # Dati richiesta
            y -= 40
            c.setFont(self.font_bold, 12)
            c.drawString(50, y, "DETALII CERERE")
            
            y -= 25
            c.setFont(self.font_name, 10)
            c.drawString(50, y, f"Tip absență: {request_data['type_name']}")
            
            y -= 20
            c.drawString(50, y, f"Perioada: {request_data['date_start'].strftime('%d.%m.%Y')} - {request_data['date_end'].strftime('%d.%m.%Y')}")
            
            y -= 20
            c.drawString(50, y, f"Zile lucrătoare: {request_data['working_days']}")
            
            # Messaggio conferma
            y -= 50
            c.setFont(self.font_bold, 11)
            c.drawString(50, y, "STARE CERERE:")
            
            y -= 25
            c.setFont(self.font_name, 10)
            
            # Testo conferma
            text_lines = [
                "Cererea dumneavoastră a fost înregistrată cu succes în sistem.",
                "",
                "⚠️ IMPORTANT:",
                "Această cerere este ÎN AȘTEPTARE de verificare și aprobare.",
                "",
                "Până când cererea nu va fi aprobată oficial, aceasta NU se consideră acceptată.",
                "Veți primi confirmarea scrisă din partea superiorului direct sau a",
                "departamentului de resurse umane.",
                "",
                "Puteți verifica starea cererii dumneavoastră oricând de la acest kiosk",
                f"introducând numărul cererii: {registry_info['doc_name']}"
            ]
            
            for line in text_lines:
                c.drawString(70, y, line)
                y -= 15
            
            # Footer
            y = 80
            c.setFont(self.font_name, 8)
            c.drawCentredString(width / 2, y, 
                              f"Document generat automat - {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            y -= 15
            c.drawCentredString(width / 2, y, 
                              "Acest document este doar o confirmare de înregistrare, nu reprezintă aprobare.")
            
            c.save()
            
            logger.info(f"PDF conferma generato: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Errore generazione PDF: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
