"""
Generatore Report Storico Assenze
Genera PDF professionale con situazione ferie, malattie e permessi
"""

import io
import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from company_config import EMPLOYER_ID
from PIL import Image
from reportlab.lib.utils import ImageReader

logger = logging.getLogger(__name__)


class AbsenceReportGenerator:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.logo_path = 'logo.png'
        
        # Registra font DejaVuSans per caratteri rumeni (ă, â, î, ș, ț)
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
            self.font_name = 'DejaVuSans'
            self.font_bold = 'DejaVuSans-Bold'
            logger.info("Font DejaVuSans registrati con successo")
        except Exception as e:
            logger.warning(f"Impossibile registrare font DejaVuSans: {e}. Uso Helvetica.")
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
    
    def generate_report(self, badge_number, year=None):
        """
        Genera report PDF storico assenze
        
        Args:
            badge_number: Numero badge dipendente
            year: Anno di riferimento (default: anno corrente)
        
        Returns:
            str: Percorso del PDF generato o None in caso di errore
        """
        try:
            if year is None:
                year = datetime.now().year
            
            # Recupera dati assenze
            absence_data = self._get_absence_data(badge_number, year)
            
            if not absence_data:
                logger.error(f"Nessun dato trovato per badge {badge_number}")
                return None
            
            # Genera PDF
            pdf_path = self._generate_pdf(absence_data, year)
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"Errore generazione report assenze: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _get_absence_data(self, badge_number, year):
        """Esegue query per recuperare dati assenze"""
        try:
            cursor = self.conn.cursor()
            
            query = f"""
            DECLARE @NoBadge VARCHAR(50) = ?
            DECLARE @Anno INT = ?
            DECLARE @DataRiferimento DATE = DATEFROMPARTS(@Anno, 12, 31)
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
        END AS Anni,
        CASE 
            WHEN h.HireDate <= @DataRiferimento THEN
                CASE 
                    WHEN DAY(@DataRiferimento) >= DAY(h.HireDate) THEN
                        CASE 
                            WHEN MONTH(@DataRiferimento) >= MONTH(h.HireDate)
                            THEN MONTH(@DataRiferimento) - MONTH(h.HireDate)
                            ELSE 12 + MONTH(@DataRiferimento) - MONTH(h.HireDate)
                        END
                    ELSE
                        CASE 
                            WHEN MONTH(@DataRiferimento) > MONTH(h.HireDate)
                            THEN MONTH(@DataRiferimento) - MONTH(h.HireDate) - 1
                            ELSE 11 + MONTH(@DataRiferimento) - MONTH(h.HireDate)
                        END
                END
            ELSE 0
        END AS Mesi,
        CASE 
            WHEN h.HireDate <= @DataRiferimento THEN
                CASE 
                    WHEN DAY(@DataRiferimento) >= DAY(h.HireDate)
                    THEN DAY(@DataRiferimento) - DAY(h.HireDate)
                    ELSE DAY(EOMONTH(DATEADD(MONTH, -1, @DataRiferimento))) - DAY(h.HireDate) + DAY(@DataRiferimento)
                END
            ELSE 0
        END AS Giorni
    FROM 
        employee.dbo.employees E
        INNER JOIN employee.dbo.EmployeeHireHistory H 
            ON e.EmployeeId = h.EmployeeId 
            AND h.EmployeerId = {EMPLOYER_ID} 
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
        CAST(C.Anni AS VARCHAR) + ' ani, ' +
        CAST(C.Mesi AS VARCHAR) + ' luni, ' +
        CAST(C.Giorni AS VARCHAR) + ' zile' AS AnzianitaDettagliata,
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
        D.DateFrom,
        D.DateTo,
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
        INNER JOIN [Timeclocking].[dbo].[Employee] TE2 ON D.IDEmployee = TE2.IDEmployee AND TE2.DataStop IS NULL AND D.DateFrom >= TE2.DataStart
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
),
MalattieRequestCTE AS (
    SELECT 
        IDEmployee,
        SUM(IsGiornoLavorativo) AS GiorniMalattiaRequest
    FROM 
        GiorniAssenzeEspansi
    WHERE 
        IDRequestType = 9
        AND IsAnnoCorrente = 1
    GROUP BY 
        IDEmployee
),
GiorniMedicalEspansi AS (
    SELECT 
        D.IDEmployee,
        DATEADD(DAY, N.n, M.FromData) AS DataCorrente
    FROM 
        [Timeclocking].[dbo].[EmployeeRequestEntireDay] D
        INNER JOIN [Timeclocking].[dbo].[Employee] TE2 ON D.IDEmployee = TE2.IDEmployee AND TE2.DataStop IS NULL AND D.DateFrom >= TE2.DataStart
        INNER JOIN [Timeclocking].[dbo].[MedicalRequest] M 
            ON D.IDEmployeeRequestEntireDay = M.IDEmployeeRequestEntireDay
        CROSS JOIN Numbers N
    WHERE 
        DATEADD(DAY, N.n, M.FromData) <= M.ToData
        AND M.FromData <= @FineAnno
        AND M.ToData >= @InizioAnno
        AND DATEADD(DAY, N.n, M.FromData) >= @InizioAnno
        AND DATEADD(DAY, N.n, M.FromData) <= @FineAnno
),
MalattieMedicalCTE AS (
    SELECT 
        IDEmployee,
        COUNT(*) AS GiorniMalattiaMedical -- Cambiato SUM a COUNT per contare i giorni
    FROM 
        GiorniMedicalEspansi
    GROUP BY 
        IDEmployee
),
PermessiCTE AS (
    SELECT 
        IDEmployee,
        SUM(IsGiornoLavorativo) AS GiorniPermessi
    FROM 
        GiorniAssenzeEspansi
    WHERE 
        IDRequestType = 12
        AND IsAnnoCorrente = 1
    GROUP BY 
        IDEmployee
)
SELECT 
    F.IDEmployee,
    F.EmployeeName,
    F.EmployeeSurname,
    F.NoBadge,
    F.HireDate,
    F.AnzianitaDettagliata AS Anzianita,
    F.Anni AS AnniCompleti,
    F.Mesi AS MesiCompleti,
    F.Giorni AS GiorniCompleti,
    F.HolidayPerYear AS FerieContratto,
    F.FerieAnnoCorrente AS FerieAnnoCorrente,
    F.GiorniBonusAnzianita AS BonusAnzianita,
    ISNULL(FSAP.TotaleFerieSpettantiAnniPrecedenti, 0) AS FerieSpettantiAnniPrecedenti,
    ISNULL(FUAP.FerieUsateAnniPrecedenti, 0) AS FerieUsateAnniPrecedenti,
    ISNULL(FSAP.TotaleFerieSpettantiAnniPrecedenti, 0) - ISNULL(FUAP.FerieUsateAnniPrecedenti, 0) AS ResiduoAnniPrecedenti,
    F.FerieAnnoCorrente + F.GiorniBonusAnzianita + 
    (ISNULL(FSAP.TotaleFerieSpettantiAnniPrecedenti, 0) - ISNULL(FUAP.FerieUsateAnniPrecedenti, 0)) AS FerieTotaliDisponibili,
    ISNULL(FUAC.FerieUsateAnnoCorrente, 0) AS FerieUsateAnnoCorrente,
    F.FerieAnnoCorrente + F.GiorniBonusAnzianita + 
    (ISNULL(FSAP.TotaleFerieSpettantiAnniPrecedenti, 0) - ISNULL(FUAP.FerieUsateAnniPrecedenti, 0)) - 
    ISNULL(FUAC.FerieUsateAnnoCorrente, 0) AS ResiduoFinale,
    CASE 
        WHEN F.HireDate > @DataRiferimento THEN 'Non ancora assunto'
        WHEN F.FerieAnnoCorrente + F.GiorniBonusAnzianita + 
             (ISNULL(FSAP.TotaleFerieSpettantiAnniPrecedenti, 0) - ISNULL(FUAP.FerieUsateAnniPrecedenti, 0)) - 
             ISNULL(FUAC.FerieUsateAnnoCorrente, 0) < 0 
        THEN 'ECCEDENZA'
        WHEN F.FerieAnnoCorrente + F.GiorniBonusAnzianita + 
             (ISNULL(FSAP.TotaleFerieSpettantiAnniPrecedenti, 0) - ISNULL(FUAP.FerieUsateAnniPrecedenti, 0)) - 
             ISNULL(FUAC.FerieUsateAnnoCorrente, 0) = 0 
        THEN 'ESAURITE'
        ELSE 'OK'
    END AS Stato,
    ISNULL(MM.GiorniMalattiaMedical, 0) AS MalattiaFromRequest,
    ISNULL(MM.GiorniMalattiaMedical, 0) AS MalattiaFromMedical,
    ISNULL(MM.GiorniMalattiaMedical, 0) AS MalattiaTotale,
    ISNULL(P.GiorniPermessi, 0) AS Permessi
FROM 
    FerieSpettantiCTE F
    LEFT JOIN FerieSpettantiAnniPrecedentiCTE FSAP ON F.IDEmployee = FSAP.IDEmployee
    LEFT JOIN FerieUsateAnniPrecedentiCTE FUAP ON F.IDEmployee = FUAP.IDEmployee
    LEFT JOIN FerieUsateAnnoCorrenteCTE FUAC ON F.IDEmployee = FUAC.IDEmployee
    LEFT JOIN MalattieRequestCTE MR ON F.IDEmployee = MR.IDEmployee
    LEFT JOIN MalattieMedicalCTE MM ON F.IDEmployee = MM.IDEmployee
    LEFT JOIN PermessiCTE P ON F.IDEmployee = P.IDEmployee;

            """
            
            cursor.execute(query, (badge_number, year))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Converti risultato in dizionario
            columns = [column[0] for column in cursor.description]
            data = dict(zip(columns, row))
            
            return data
            
        except Exception as e:
            logger.error(f"Errore query assenze: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _get_bonus_rules(self):
        """Recupera regole bonus anzianità dal database"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT 
                noYears,
                FixValueOnBrutSalary AS GiorniBonus
            FROM 
                [Employee].[dbo].[BonusTypeSeniotiry]
            WHERE 
                BonusTypeValueId = 4 
                AND dateout IS NULL
            ORDER BY 
                noYears
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            rules = []
            for row in rows:
                rules.append({
                    'anni': row[0],
                    'giorni_bonus': row[1]
                })
            
            return rules
            
        except Exception as e:
            logger.error(f"Errore recupero regole bonus: {str(e)}")
            return []
    
    def _draw_disclaimer_footer(self, canvas_obj, width, y_position=30):
        """
        Disegna il disclaimer in rumeno nel footer della pagina
        
        Args:
            canvas_obj: Oggetto canvas di ReportLab
            width: Larghezza della pagina
            y_position: Posizione Y del footer (default: 30)
        """
        disclaimer_text = (
            "Dacă datele solicitate nu corespund cu ceea ce vă amintiți, vă rugăm să vă adresați "
            "biroului de Personal al Vandewiele România. Țineți cont că sistemul este în fază de "
            "dezvoltare și ar putea genera erori. Ne cerem scuze în avans, în cazul în care ar trebui "
            "să se întâmple. Vă mulțumim pentru înțelegere, Biroul Resurse Umane."
        )
        
        canvas_obj.setFont(self.font_name, 8)
        
        # Calcola larghezza massima per il testo (margini 50px per lato)
        max_width = width - 100
        
        # Dividi il testo in righe
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = disclaimer_text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if stringWidth(test_line, self.font_name, 8) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Disegna le righe centrate
        y = y_position
        for line in reversed(lines):  # Inizia dal basso
            canvas_obj.drawCentredString(width / 2, y, line)
            y += 10  # Spaziatura tra le righe
    
    def _generate_pdf(self, data, year):
        """Genera PDF report"""
        try:
            # Crea cartella temp se non esiste
            os.makedirs('temp', exist_ok=True)
            
            # Nome file PDF
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"Raport_Absente_{data['NoBadge']}_{year}_{timestamp}.pdf"
            pdf_path = os.path.join('temp', pdf_filename)
            
            # Crea PDF
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            
            # Logo aziendale
            y = height - 60
            if os.path.exists(self.logo_path):
                try:
                    logo = ImageReader(self.logo_path)
                    c.drawImage(logo, 50, y, width=100, height=40, preserveAspectRatio=True)
                except:
                    pass
            
            # Titolo
            y = height - 100
            c.setFont(self.font_bold, 16)
            c.drawCentredString(width / 2, y, f"RAPORT ISTORIC ABSENȚE - {year}")
            
            # Data generazione
            y -= 30
            c.setFont(self.font_name, 10)
            c.drawCentredString(width / 2, y, f"Generat: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            # Dati dipendente
            y -= 40
            c.setFont(self.font_bold, 12)
            c.drawString(50, y, "DATE ANGAJAT")
            
            y -= 20
            c.setFont(self.font_name, 10)
            c.drawString(50, y, f"Nume: {data['EmployeeSurname']} {data['EmployeeName']}")
            
            y -= 15
            c.drawString(50, y, f"Badge: {data['NoBadge']}")
            
            y -= 15
            c.drawString(50, y, f"Data angajării: {data['HireDate'].strftime('%d.%m.%Y') if data['HireDate'] else 'N/A'}")
            
            y -= 15
            c.drawString(50, y, f"Vechime: {data['Anzianita']}")
            
            # Sezione FERIE
            y -= 40
            c.setFont(self.font_bold, 12)
            c.drawString(50, y, "CONCEDIU DE ODIHNĂ (FERIE)")
            
            # Tabella ferie
            y -= 25
            ferie_data = [
                ['Descriere', 'Zile'],
                ['Zile contract anual', str(int(data['FerieContratto']))],
                ['Zile anul curent', str(int(data['FerieAnnoCorrente']))],
                ['Bonus vechime', str(int(data['BonusAnzianita']))],
                ['Reziduu ani precedenți', str(int(data['ResiduoAnniPrecedenti']))],
                ['Total disponibil', str(int(data['FerieTotaliDisponibili']))],
                ['Utilizate anul curent', str(int(data['FerieUsateAnnoCorrente']))],
                ['REZIDUU FINAL', str(int(data['ResiduoFinale']))]
            ]
            
            table = Table(ferie_data, colWidths=[350, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -2), self.font_name),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                ('FONTNAME', (0, -1), (-1, -1), self.font_bold),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8fafc')]),
            ]))
            
            table.wrapOn(c, width, height)
            table.drawOn(c, 50, y - 200)
            
            y -= 220
            
            # Sezione MALATTIE E PERMESSI
            y -= 20
            c.setFont(self.font_bold, 12)
            c.drawString(50, y, "ALTE ABSENȚE")
            
            y -= 25
            altre_data = [
                ['Tip absență', 'Zile'],
                ['Concediu medical (boală)', str(int(data['MalattiaTotale']))],
                ['Învoiri (permise)', str(int(data['Permessi']))]
            ]
            
            table2 = Table(altre_data, colWidths=[350, 100])
            table2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ]))
            
            table2.wrapOn(c, width, height)
            table2.drawOn(c, 50, y - 80)
            
            y -= 100
            
            # Disclaimer in rumeno (prima pagina)
            self._draw_disclaimer_footer(c, width, y_position=30)
            
            # Nuova pagina per regole bonus
            c.showPage()
            
            # Regole bonus anzianità
            y = height - 60
            c.setFont(self.font_bold, 14)
            c.drawString(50, y, "REGULI BONUS VECHIME")
            
            y -= 30
            c.setFont(self.font_name, 10)
            c.drawString(50, y, "Conform legislației muncii din România și contractului colectiv de muncă,")
            y -= 15
            c.drawString(50, y, "angajații beneficiază de zile suplimentare de concediu în funcție de vechime:")
            
            # Recupera regole bonus
            bonus_rules = self._get_bonus_rules()
            
            y -= 30
            if bonus_rules:
                bonus_data = [['Vechime (ani)', 'Zile bonus']]
                for rule in bonus_rules:
                    bonus_data.append([
                        f"{rule['anni']} ani sau mai mult",
                        str(int(rule['giorni_bonus']))
                    ])
                
                table3 = Table(bonus_data, colWidths=[300, 150])
                table3.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#d1fae5')]),
                ]))
                
                table3.wrapOn(c, width, height)
                table3.drawOn(c, 50, y - (len(bonus_rules) * 25 + 30))
                
                y -= (len(bonus_rules) * 25 + 60)
            
            # Note finali
            y -= 30
            c.setFont(self.font_bold, 10)
            c.drawString(50, y, "NOTE:")
            
            y -= 20
            c.setFont(self.font_name, 9)
            c.drawString(50, y, "• Zilele de concediu sunt calculate doar pentru zilele lucrătoare (luni-vineri)")
            y -= 15
            c.drawString(50, y, "• Sărbătorile legale și weekendurile nu sunt incluse în calcul")
            y -= 15
            c.drawString(50, y, "• Bonusul de vechime se acordă automat la atingerea vechimii respective")
            y -= 15
            c.drawString(50, y, "• Concediul neefectuat se reportează în anul următor")
            
            # Disclaimer in rumeno
            self._draw_disclaimer_footer(c, width, y_position=30)
            
            c.save()
            
            logger.info(f"PDF report generato: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Errore generazione PDF: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
