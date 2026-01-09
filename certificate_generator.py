"""
Generatore di Certificati PDF
Sostituisce la logica VBA per la creazione di adeverințe
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from PIL import Image
import io
import os
import logging
from utils import log_service_operation

logger = logging.getLogger(__name__)


class CertificateGenerator:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.logo_path = 'logo.png'  # Logo nella root del progetto
        
        # Registra font per caratteri rumeni
        self.font_name = 'Helvetica'  # Default fallback
        self.font_bold = 'Helvetica-Bold'
        
        try:
            # Prova percorsi multipli per DejaVu
            dejavu_paths = [
                ('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf'),  # Cartella corrente
                ('fonts/DejaVuSans.ttf', 'fonts/DejaVuSans-Bold.ttf'),  # Sottocartella
                (r'C:\Windows\Fonts\DejaVuSans.ttf', r'C:\Windows\Fonts\DejaVuSans-Bold.ttf'),  # Sistema
                # Percorso alternativo Windows
                (os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'DejaVuSans.ttf'),
                 os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'DejaVuSans-Bold.ttf'))
            ]
            
            font_registered = False
            for regular_path, bold_path in dejavu_paths:
                if os.path.exists(regular_path):
                    try:
                        pdfmetrics.registerFont(TTFont('DejaVu', regular_path))
                        if os.path.exists(bold_path):
                            pdfmetrics.registerFont(TTFont('DejaVu-Bold', bold_path))
                        else:
                            pdfmetrics.registerFont(TTFont('DejaVu-Bold', regular_path))
                        
                        self.font_name = 'DejaVu'
                        self.font_bold = 'DejaVu-Bold'
                        font_registered = True
                        logger.info(f"Font DejaVu registrato da: {regular_path}")
                        break
                    except Exception as e:
                        logger.debug(f"Errore registrazione font da {regular_path}: {e}")
                        continue
            
            # Se DejaVu non trovato, prova Arial Unicode MS (Windows)
            if not font_registered:
                arial_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arial.ttf')
                arial_bold_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arialbd.ttf')
                
                if os.path.exists(arial_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Arial', arial_path))
                        if os.path.exists(arial_bold_path):
                            pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
                        else:
                            pdfmetrics.registerFont(TTFont('Arial-Bold', arial_path))
                        
                        self.font_name = 'Arial'
                        self.font_bold = 'Arial-Bold'
                        font_registered = True
                        logger.info("Font Arial registrato per supporto Unicode")
                    except Exception as e:
                        logger.warning(f"Errore registrazione Arial: {e}")
            
            if not font_registered:
                logger.warning("Nessun font Unicode trovato, uso Helvetica (caratteri rumeni potrebbero non visualizzarsi)")
                
        except Exception as e:
            logger.error(f"Errore generale registrazione font: {str(e)}")
    
    def _get_administrator_signature(self):
        """Recupera firma amministratore dal database"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT [Signature]
            FROM [Employee].[dbo].[Administrators] 
            WHERE adminid = 3
            """
            
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row and row[0]:
                # La firma è memorizzata come BLOB/VARBINARY
                return row[0]
            else:
                logger.warning("Firma amministratore non trovata nel database")
                return None
        
        except Exception as e:
            logger.error(f"Errore recupero firma amministratore: {str(e)}")
            return None
    
    def _make_signature_transparent(self, signature_data):
        """
        Converte firma con sfondo bianco in trasparente
        
        Args:
            signature_data: Bytes dell'immagine firma
        
        Returns:
            Image: Immagine PIL con sfondo trasparente
        """
        try:
            # Carica immagine
            img = Image.open(io.BytesIO(signature_data))
            
            # Converti in RGBA se necessario
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Ottieni dati pixel
            datas = img.getdata()
            
            # Lista per nuovi pixel
            new_data = []
            
            # Soglia per considerare un pixel "bianco" (regolabile)
            white_threshold = 240
            
            for item in datas:
                # Se il pixel è quasi bianco, rendilo trasparente
                # Controlla RGB (ignora alpha se presente)
                if item[0] > white_threshold and item[1] > white_threshold and item[2] > white_threshold:
                    # Trasparente (RGBA)
                    new_data.append((255, 255, 255, 0))
                else:
                    # Mantieni pixel originale con alpha pieno
                    if len(item) == 4:
                        new_data.append(item)
                    else:
                        new_data.append((item[0], item[1], item[2], 255))
            
            # Applica nuovi dati
            img.putdata(new_data)
            
            logger.info("Sfondo firma convertito in trasparente")
            return img
            
        except Exception as e:
            logger.warning(f"Errore conversione trasparenza firma: {str(e)}")
            # Ritorna immagine originale se conversione fallisce
            return Image.open(io.BytesIO(signature_data))
    
    
    def _sign_pdf_digital(self, pdf_path, cert_path=None, cert_password=None):
        """
        Firma digitalmente il PDF usando certificato digitale (PKCS#12/PEM)
        
        Args:
            pdf_path: Percorso del PDF da firmare
            cert_path: Percorso certificato (.pfx, .p12, .pem) - opzionale
            cert_password: Password certificato - opzionale
        
        Returns:
            bool: True se firma riuscita o non necessaria, False se errore critico
        """
        try:
            from pdf_digital_signer import PDFDigitalSigner, create_visible_signature_field
            from reportlab.lib.pagesizes import A4
            
            logger.info(f"Tentativo firma digitale PDF: {pdf_path}")
            
            # Controlla se esiste file certificato nella cartella
            cert_files = [
                'certificate.pfx',
                'certificate.p12',
                'certificate.pem',
                'cert.pfx',
                'cert.p12'
            ]
            
            found_cert = None
            for cert_file in cert_files:
                if os.path.exists(cert_file):
                    found_cert = cert_file
                    logger.info(f"Trovato certificato: {cert_file}")
                    break
            
            # Usa certificato specificato o quello trovato
            cert_to_use = cert_path or found_cert
            
            if not cert_to_use:
                logger.warning("Nessun certificato trovato - PDF non firmato digitalmente")
                logger.info("Per firmare digitalmente, inserire file certificato: certificate.pfx/p12/pem")
                return True  # Non è errore critico
            
            # Inizializza signer
            signer = PDFDigitalSigner(
                cert_path=cert_to_use,
                cert_password=cert_password or os.environ.get('CERT_PASSWORD')
            )
            
            # Crea campo firma visibile (bottom-right)
            page_width, page_height = A4
            sig_field = create_visible_signature_field(
                page_width=page_width,
                page_height=page_height,
                position='bottom-right',
                width=180,
                height=70
            )
            
            # Firma il PDF
            signed_path = signer.sign_pdf(
                input_pdf_path=pdf_path,
                output_pdf_path=pdf_path,  # Sovrascrivi
                signature_field_spec=sig_field,
                reason='Documento ufficiale aziendale',
                location='Sede legale'
            )
            
            if signed_path == pdf_path:
                logger.info(f"PDF firmato digitalmente con successo: {pdf_path}")
                return True
            else:
                logger.warning(f"Firma digitale completata con warning")
                return True
                
        except ImportError as e:
            logger.warning(f"pyHanko non installato - PDF non firmato: {e}")
            logger.info("Installare con: pip install pyHanko pyhanko-certvalidator")
            return True  # Non blocchiamo l'applicazione
        except FileNotFoundError as e:
            logger.warning(f"Certificato non trovato: {e}")
            return True  # Non blocchiamo
        except Exception as e:
            logger.warning(f"Firma digitale non disponibile: {str(e)}")
            logger.debug(f"Dettagli errore firma", exc_info=True)
            return True  # Non blocchiamo l'applicazione

    
    def generate_certificate(self, employee_hire_history_id, reason, typed_reason='', group_id=0):
        """
        Genera certificato basato sul tipo
        
        Args:
            employee_hire_history_id: ID storico assunzione dipendente
            reason: Motivo del certificato
            typed_reason: Motivo personalizzato (se richiesto)
            group_id: Gruppo certificato (2 = Adeverința 7, altro = generica)
        
        Returns:
            dict con success, document_number, pdf_path, etc.
        """
        username = "Unknown"
        service_name = f"Genera Certificato - {reason[:50]}"
        
        try:
            # Determina tipo certificato
            registry_type_id = 737 if group_id == 2 else 736
            
            # Genera numero documento tramite stored procedure
            doc_info = self._generate_document_number(
                registry_type_id=registry_type_id,
                employee_hire_history_id=employee_hire_history_id,
                note=typed_reason if typed_reason else reason
            )
            
            # Recupera dati dipendente
            employee_data = self._get_employee_data(employee_hire_history_id)
            username = employee_data.get('full_name', 'Unknown')
            
            # Recupera dati azienda
            company_data = self._get_company_data()
            
            # Genera PDF
            if registry_type_id == 737:
                # Adeverința 7 (certificato medico)
                medical_data = self._get_medical_data(employee_data['timeclock_id'])
                children_data = self._get_children_data(employee_data['employee_id'])
                
                pdf_path = self._generate_adv7_pdf(
                    doc_info=doc_info,
                    employee=employee_data,
                    company=company_data,
                    medical=medical_data,
                    children=children_data
                )
                
                # Registra documento nel database
                self._register_document(
                    employee_hire_history_id=employee_hire_history_id,
                    registry_type_id=registry_type_id,
                    pdf_path=pdf_path,
                    registry_id=doc_info['registry_id'],
                    note=typed_reason if typed_reason else reason
                )
                
                # Prepara email
                email_body = self._prepare_email_body(employee_data, 'Adeverința 7')
                
                # Log operazione riuscita
                log_service_operation(
                    self.conn,
                    username=username,
                    service_name=service_name,
                    success=True,
                    additional_info=f"Doc: {doc_info['doc_number']}, Type: Adeverința 7"
                )
                
                return {
                    'success': True,
                    'document_number': doc_info['doc_number'],
                    'document_date': doc_info['doc_date'],
                    'registry_id': doc_info['registry_id'],
                    'pdf_path': pdf_path.replace('\\', '/'),  # Normalizza path per URL
                    'email_required': True,
                    'email_subject': "New request 'Adeverința 7'",
                    'email_body': email_body
                }
            else:
                # Certificato generico
                pdf_path = self._generate_generic_certificate_pdf(
                    doc_info=doc_info,
                    employee=employee_data,
                    company=company_data,
                    reason=typed_reason if typed_reason else reason
                )
                
                # Log operazione riuscita
                log_service_operation(
                    self.conn,
                    username=username,
                    service_name=service_name,
                    success=True,
                    additional_info=f"Doc: {doc_info['doc_number']}, Type: Generico"
                )
                
                return {
                    'success': True,
                    'document_number': doc_info['doc_number'],
                    'document_date': doc_info['doc_date'],
                    'registry_id': doc_info['registry_id'],
                    'pdf_path': pdf_path.replace('\\', '/'),  # Normalizza path per URL
                    'email_required': False
                }
        
        except Exception as e:
            logger.error(f"Errore nella generazione certificato: {str(e)}")
            
            # Log operazione fallita
            log_service_operation(
                self.conn,
                username=username,
                service_name=service_name,
                success=False,
                error_message=str(e)
            )
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_document_number(self, registry_type_id, employee_hire_history_id, note):
        """Chiama stored procedure per generare numero documento"""
        try:
            cursor = self.conn.cursor()
            
            # Recupera EmployeerId
            cursor.execute("""
                SELECT EmployeerId 
                FROM Employee.dbo.EmployeeHireHistory 
                WHERE EmployeeHireHistoryId = ?
            """, (employee_hire_history_id,))
            
            row = cursor.fetchone()
            if not row:
                raise Exception("Dipendente non trovato")
            
            employeer_id = row[0]
            current_date = datetime.now().date()
            current_year = datetime.now().year
            
            # Chiama stored procedure
            cursor.execute("""
                EXEC Employee.dbo.Registro 
                    @RegistryTypeId = ?,
                    @anno = ?,
                    @DataDocumento = ?,
                    @IussedBy = 'WebApp',
                    @EmployeerId = ?,
                    @Accessid = NULL,
                    @DocumentTypeId = NULL,
                    @Nota = ?
            """, (registry_type_id, current_year, current_date, employeer_id, note))
            
            # Recupera risultato
            row = cursor.fetchone()
            if not row:
                raise Exception("Errore nella generazione numero documento")
            
            return {
                'registry_id': row[0],
                'doc_number': row[1],
                'doc_date': current_date.strftime('%d-%m-%Y')
            }
        
        except Exception as e:
            logger.error(f"Errore generazione numero documento: {str(e)}")
            raise
    
    def _get_employee_data(self, employee_hire_history_id):
        """Recupera dati completi dipendente"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT 
                E.EmployeeId,
                E.EmployeeSurname + ' ' + E.EmployeeName AS FullName,
                E.EmployeeNID AS CNP,
                E.EmployeeSex,
                LTRIM(
                    ISNULL('Strada ' + LTRIM(RTRIM(A.Street)), '') +
                    ISNULL(' Nr. ' + LTRIM(RTRIM(A.NumeroCivico)), '') +
                    ISNULL(', Bloc ' + LTRIM(RTRIM(A.Bloc)), '') +
                    ISNULL(' Scara ' + LTRIM(RTRIM(A.Scala)), '') +
                    ISNULL(' Etaj ' + LTRIM(RTRIM(A.Piano)), '') +
                    ISNULL(' Ap. ' + LTRIM(RTRIM(A.Apartment)), '')
                ) AS Address,
                T.TownName,
                C.CountyName,
                N.NationName,
                ED.DocSerie + ' ' + ED.DocNumber AS DocumentID,
                ET.IDEmployee AS TimeclockID
            FROM employee.dbo.employees E
            INNER JOIN employee.dbo.EmployeeAddress A 
                ON E.EmployeeId = A.EmployeeId AND A.DateOut IS NULL
            INNER JOIN employee.geo.Towns T 
                ON E.BirthCityId = T.TownId
            INNER JOIN employee.geo.Counties C 
                ON T.CountyId = C.CountyId
            INNER JOIN employee.geo.Nations N 
                ON C.NationId = N.NationId
            INNER JOIN employee.dbo.EmployeeDocuments ED 
                ON A.EmployeeId = ED.EmployeeId AND ED.DateOut IS NULL
            INNER JOIN employee.dbo.EmployeeHireHistory H 
                ON E.EmployeeId = H.EmployeeId AND H.EndWorkDate IS NULL
            INNER JOIN Timeclocking.dbo.Employee ET 
                ON E.EmployeeNID COLLATE Database_default = ET.UniqueID 
                AND ET.DataStop IS NULL
            WHERE H.EmployeeHireHistoryId = ?
            """
            
            cursor.execute(query, (employee_hire_history_id,))
            row = cursor.fetchone()
            
            if not row:
                raise Exception("Dati dipendente non trovati")
            
            return {
                'employee_id': row[0],
                'full_name': row[1],
                'cnp': row[2],
                'sex': row[3],
                'address': row[4],
                'town': row[5],
                'county': row[6],
                'nation': row[7],
                'document_id': row[8],
                'timeclock_id': row[9]
            }
        
        except Exception as e:
            logger.error(f"Errore recupero dati dipendente: {str(e)}")
            raise
    
    def _get_company_data(self):
        """Recupera dati azienda"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT 
                S.DenomSoc,
                S.ind1,
                S.ind2,
                S.cui,
                S.NRC,
                S.nazione,
                S.citta,
                S.CAP,
                S.JUD,
                EA.EmployeeName + ' ' + EA.EmployeeSurname AS Administrator
            FROM resetservices.dbo.tbsocieta S
            INNER JOIN employee.dbo.Employeers E 
                ON S.CUI COLLATE database_default = E.EmployeerFiscalCode
            INNER JOIN employee.dbo.Administrators A 
                ON E.EmployeerId = A.EmployeerId AND A.DateOut IS NULL
            INNER JOIN employee.dbo.employees EA 
                ON A.EmployeeID = EA.EmployeeId
            WHERE E.EmployeerId = 2
            """
            
            cursor.execute(query)
            row = cursor.fetchone()
            
            if not row:
                raise Exception("Dati azienda non trovati")
            
            return {
                'name': row[0],
                'address1': row[1],
                'address2': row[2],
                'cui': row[3],
                'nrc': row[4],
                'nation': row[5],
                'city': row[6],
                'cap': row[7],
                'county': row[8],
                'administrator': row[9]
            }
        
        except Exception as e:
            logger.error(f"Errore recupero dati azienda: {str(e)}")
            raise
    
    def _get_medical_data(self, timeclock_employee_id):
        """Recupera dati congedi medici ultimi 12 mesi"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT 
                E.EmployeeName,
                E.EmployeeSurname,
                MT.Description,
                M.IsContinue,
                M.SeriesCM,
                M.NoCM,
                FORMAT(M.FromData, 'd', 'ro-ro') AS DateStart,
                FORMAT(M.ToData, 'd', 'ro-ro') AS DateFinish,
                DATEDIFF(DAY, M.FromData, M.ToData) AS Days
            FROM Timeclocking.dbo.MedicalRequest M
            INNER JOIN Timeclocking.dbo.EmployeeRequestEntireDay D 
                ON M.IDEmployeeRequestEntireDay = D.IDEmployeeRequestEntireDay
            INNER JOIN Timeclocking.dbo.Employee E 
                ON D.IDEmployee = E.IDEmployee
            INNER JOIN Timeclocking.dbo.MedicalRequestType MT 
                ON M.IDMedicalRequestType = MT.IDMedicalRequestType
            WHERE E.IDEmployee = ? 
                AND M.FromData >= DATEADD(DAY, -365, GETDATE())
            ORDER BY M.FromData
            """
            
            cursor.execute(query, (timeclock_employee_id,))
            
            medical_records = []
            for row in cursor.fetchall():
                medical_records.append({
                    'description': row[2],
                    'is_continue': row[3],
                    'series': row[4],
                    'number': row[5],
                    'date_start': row[6],
                    'date_finish': row[7],
                    'days': row[8]
                })
            
            return medical_records
        
        except Exception as e:
            logger.error(f"Errore recupero dati medici: {str(e)}")
            return []
    
    def _get_children_data(self, employee_id):
        """Recupera dati figli dipendente"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            SELECT 
                ROW_NUMBER() OVER(ORDER BY ChildBirthDate) AS Nr,
                ChildName,
                CNPChild
            FROM employee.dbo.EmployeeChildren EC
            INNER JOIN Employee.dbo.RelativeTypes RT 
                ON EC.FamilyRelativeId = RT.FamilyRelativeId
            WHERE EmployeeId = ? AND EC.DateOut IS NULL
            """
            
            cursor.execute(query, (employee_id,))
            
            children = []
            for row in cursor.fetchall():
                children.append({
                    'number': row[0],
                    'name': row[1],
                    'cnp': row[2]
                })
            
            return children
        
        except Exception as e:
            logger.error(f"Errore recupero dati figli: {str(e)}")
            return []
    
    def _generate_adv7_pdf(self, doc_info, employee, company, medical, children):
        """Genera PDF Adeverința 7 (certificato medico) - Formato completo come VBA"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"Adv7_{timestamp}.pdf"
        pdf_path = os.path.join('temp', filename)
        
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        margin_left = 50
        margin_right = width - 50
        
        # Logo aziendale
        y = height - 60
        if os.path.exists(self.logo_path):
            try:
                logo = ImageReader(self.logo_path)
                c.drawImage(logo, margin_left, y, width=100, height=40, preserveAspectRatio=True)
            except:
                pass
        
        # Intestazione azienda (in alto a destra)
        y = height - 60
        c.setFont(self.font_bold, 11)
        c.drawRightString(margin_right, y, company['name'].upper())
        y -= 14
        c.setFont(self.font_name, 9)
        c.drawRightString(margin_right, y, company['address1'])
        y -= 12
        c.drawRightString(margin_right, y, f"CUI: {company['cui']} | NRC: {company['nrc']}")
        y -= 12
        c.drawRightString(margin_right, y, f"{company['cap']} {company['city']}, {company['county']}, {company['nation']}")
        
        # Numero e data documento
        y -= 30
        c.setFont(self.font_name, 10)
        c.drawString(margin_left, y, f"Nr. de înregistrare {doc_info['doc_number']}")
        y -= 14
        c.drawString(margin_left, y, f"Din data {doc_info['doc_date']}")
        
        # Titolo
        y -= 30
        c.setFont(self.font_bold, 14)
        c.drawCentredString(width / 2, y, "ADEVERINȚĂ")
        
        # Determina genere
        sesso = "domnul" if employee['sex'] == 'M' else "domna"
        
        # Calcola totale giorni malattia
        total_days = sum(record['days'] for record in medical) if medical else 0
        
        # Corpo del certificato - Testo legale completo
        y -= 25
        c.setFont(self.font_name, 9)
        
        # Paragrafo 1 - Certificazione
        text = (
            f"Prin prezenta se certifică faptul că {sesso} {employee['full_name']}, "
            f"CNP: {employee['cnp']}, carte de identitate {employee['document_id']}, "
            f"cu domiciliul în {employee['address']}, {employee['town']} [{employee['county']}] "
            f"are calitate de persoană asigurată pentru concedii și indemnizații de asigurări "
            f"sociale de sănătate în sistemul de asigurări sociale de sănătate și îndeplinește "
            f"stagiul de asigurare*) prevăzut la art. 7 din Ordonanța de urgență a Guvernului "
            f"nr. 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate, "
            f"aprobată cu modificări și completări prin Legea nr. 399/2006, cu modificările și "
            f"completările ulterioare."
        )
        
        y = self._draw_wrapped_text(c, text, margin_left, y, margin_right - margin_left, 9)
        
        # Nota legale
        y -= 10
        c.setFont(self.font_name, 8)
        note_text = (
            "*) Adeverința se eliberează și persoanelor aflate în concediu medical pentru "
            "situațiile prevăzute la art. 9 și 31 din Ordonanța de urgență a Guvernului nr. 158/2005, "
            "aprobată cu modificări și completări prin Legea nr. 399/2006, cu modificările și "
            "completările ulterioare, în vederea gestionării numărului de zile de concediu medical "
            "acordate pentru aceste afecțiuni."
        )
        y = self._draw_wrapped_text(c, note_text, margin_left, y, margin_right - margin_left, 8)
        
        # Sezione coasigurati (familiari)
        y -= 15
        c.setFont(self.font_name, 9)
        c.drawString(margin_left, y, "Persoana mai sus menționată figurează în evidențele noastre cu următorii coasigurați")
        y -= 12
        c.drawString(margin_left, y, "(soț/soție, părinți, aflați în întreținere):")
        
        y -= 15
        c.setFont(self.font_bold, 9)
        c.drawString(margin_left, y, "Nr.")
        c.drawString(margin_left + 30, y, "Nume")
        c.drawString(margin_left + 250, y, "CNP")
        y -= 12
        
        c.setFont(self.font_name, 9)
        if children:
            for child in children:
                c.drawString(margin_left, y, str(child['number']))
                c.drawString(margin_left + 30, y, child['name'])
                c.drawString(margin_left + 250, y, child['cnp'])
                y -= 12
        else:
            c.drawString(margin_left, y, "--")
            c.drawString(margin_left + 250, y, "---")
            y -= 12
        
        # Validità e dichiarazione
        y -= 15
        c.setFont(self.font_name, 9)
        validity_text = (
            f"Prezenta adeverință are o perioadă de valabilitate de 30 de zile de la data emiterii. "
            f"Sub sancțiunile aplicate faptei de fals în acte publice, declar că datele din adeverință "
            f"sunt corecte și complete. Numărul de zile de concediu medical de care persoana asigurată "
            f"a beneficiat în ultimele 12 luni este de {total_days} zile, până la data de "
            f"{datetime.now().strftime('%d.%m.%Y')}, aferente fiecărui cod de indemnizație în parte, "
            f"fiecărei sarcini, precum și fiecărui copil bolnav, după cum urmează:"
        )
        y = self._draw_wrapped_text(c, validity_text, margin_left, y, margin_right - margin_left, 9)
        
        # Tabella congedi medici
        if medical and len(medical) > 0:
            y -= 15
            c.setFont(self.font_bold, 8)
            c.drawString(margin_left, y, "Tip concediu")
            c.drawString(margin_left + 120, y, "Serie/Nr CM")
            c.drawString(margin_left + 200, y, "Data început")
            c.drawString(margin_left + 280, y, "Data sfârșit")
            c.drawString(margin_left + 360, y, "Zile")
            y -= 2
            c.line(margin_left, y, margin_right, y)
            y -= 12
            
            c.setFont(self.font_name, 8)
            for record in medical:
                if y < 100:  # Nuova pagina se necessario
                    c.showPage()
                    y = height - 50
                    c.setFont(self.font_name, 8)
                
                c.drawString(margin_left, y, record['description'][:25])
                c.drawString(margin_left + 120, y, f"{record['series']}/{record['number']}")
                c.drawString(margin_left + 200, y, record['date_start'])
                c.drawString(margin_left + 280, y, record['date_finish'])
                c.drawString(margin_left + 360, y, str(record['days']))
                y -= 11
        else:
            y -= 15
            c.setFont(self.font_name, 9)
            c.drawString(margin_left, y, "Nu există concedii medicale în ultimele 12 luni.")
            y -= 15
        
        # Firma e data
        y -= 30
        if y < 150:
            c.showPage()
            y = height - 50
        
        c.setFont(self.font_name, 10)
        c.drawString(margin_left, y, f"Data: {doc_info['doc_date']}")
        
        
        # Nome e titolo amministratore
        c.setFont(self.font_name, 10)
        c.drawString(width - 200, y - 20, company['administrator'])
        c.drawString(width - 200, y - 35, "Administrator")
        
        # Firma amministratore dal database (SOTTO il nome)
        signature_data = self._get_administrator_signature()
        if signature_data:
            try:
                signature_image = Image.open(io.BytesIO(signature_data))
                signature_reader = ImageReader(signature_image)
                # Firma sotto il nome
                c.drawImage(signature_reader, width - 220, y - 110, width=180, height=75, preserveAspectRatio=True)
            except Exception as e:
                logger.warning(f"Errore caricamento firma: {str(e)}")
        
        c.save()
        
        # Firma digitale PDF
        self._sign_pdf_digital(pdf_path)
        
        return pdf_path
    
    def _draw_wrapped_text(self, canvas_obj, text, x, y, max_width, font_size):
        """Helper per disegnare testo con word wrap"""
        from reportlab.pdfbase.pdfmetrics import stringWidth
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if stringWidth(test_line, self.font_name, font_size) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            canvas_obj.drawString(x, y, line)
            y -= font_size + 3
        
        return y
        c.drawString(width - 200, y - 85, "Administrator")
        
        c.save()
        
        # Firma digitale PDF
        self._sign_pdf_digital(pdf_path)
        
        return pdf_path
    
    def _generate_generic_certificate_pdf(self, doc_info, employee, company, reason):
        """Genera PDF certificato generico"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"Certificate_{timestamp}.pdf"
        pdf_path = os.path.join('temp', filename)
        
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Logo aziendale
        if os.path.exists(self.logo_path):
            logo = ImageReader(self.logo_path)
            c.drawImage(logo, 30, height - 80, width=100, height=40, preserveAspectRatio=True)
        
        # Intestazione azienda
        y = height - 100
        c.setFont(self.font_bold, 12)
        c.drawString(30, y, company['name'])
        y -= 15
        c.setFont(self.font_name, 10)
        c.drawString(30, y, f"{company['address1']}, {company['city']}, {company['county']}")
        y -= 12
        c.drawString(30, y, f"CUI: {company['cui']} | NRC: {company['nrc']}")
        
        # Numero e data documento
        y -= 30
        c.setFont(self.font_name, 10)
        c.drawString(width - 200, y, f"Nr. {doc_info['doc_number']}")
        y -= 12
        c.drawString(width - 200, y, f"Data: {doc_info['doc_date']}")
        
        # Titolo
        y -= 40
        c.setFont(self.font_bold, 14)
        title = "ADEVERINȚĂ"
        c.drawCentredString(width / 2, y, title)
        
        # Corpo del certificato
        y -= 30
        c.setFont(self.font_name, 11)
        
        text_lines = [
            f"Subsemnatul/a {company['administrator']}, în calitate de administrator al {company['name']},",
            f"cu sediul în {company['city']}, {company['address1']},",
            f"CUI {company['cui']}, NRC {company['nrc']},",
            "",
            f"Adeveresc că domnul/doamna {employee['full_name']},",
            f"CNP {employee['cnp']}, domiciliat/ă în {employee['address']}, {employee['town']}, {employee['county']},",
            f"CI/BI seria {employee['document_id']},",
            "",
            "este angajat/ă al societății noastre.",
            "",
            f"Motiv: {reason}"
        ]
        
        for line in text_lines:
            c.drawString(50, y, line)
            y -= 15
        
        # Firma e data
        y -= 40
        c.setFont(self.font_name, 10)
        c.drawString(50, y, f"Data: {doc_info['doc_date']}")
        
        
        # Nome e titolo amministratore
        c.drawString(width - 200, y - 20, company['administrator'])
        c.drawString(width - 200, y - 35, "Administrator")
        
        # Firma amministratore dal database (SOTTO il nome)
        signature_data = self._get_administrator_signature()
        if signature_data:
            try:
                signature_image = Image.open(io.BytesIO(signature_data))
                signature_reader = ImageReader(signature_image)
                # Firma sotto il nome
                c.drawImage(signature_reader, width - 220, y - 110, width=180, height=75, preserveAspectRatio=True)
            except Exception as e:
                logger.warning(f"Errore caricamento firma: {str(e)}")
        
        c.save()
        
        # Firma digitale PDF
        self._sign_pdf_digital(pdf_path)
        
        return pdf_path
    
    def _register_document(self, employee_hire_history_id, registry_type_id, pdf_path, registry_id, note):
        """Registra documento nel database"""
        try:
            cursor = self.conn.cursor()
            
            query = """
            INSERT INTO employee.dbo.EmployeeHireHistoryDocs
            (EmployeeHireHistoryId, TipoRegistroId, PathAndDoc, DateIn, IsFilanlPath, RegistroId, Motive)
            SELECT ?, ?, ?, GETDATE(), 1, ?, ?
            WHERE NOT EXISTS (
                SELECT * FROM employee.dbo.EmployeeHireHistoryDocs 
                WHERE PathAndDoc = ?
            )
            """
            
            cursor.execute(query, (
                employee_hire_history_id,
                registry_type_id,
                pdf_path,
                registry_id,
                note,
                pdf_path
            ))
            
            self.conn.commit()
        
        except Exception as e:
            logger.error(f"Errore registrazione documento: {str(e)}")
            raise
    
    def _prepare_email_body(self, employee, certificate_type):
        """Prepara corpo email"""
        return f"""
        <html>
        <body>
            <p>Good morning,</p>
            <p>Employee <strong>{employee['full_name']}</strong> has requested a new certificate type '<strong>{certificate_type}</strong>' for medical reasons.</p>
            <p>The certificate has been generated and is attached to this email.</p>
            <br>
            <p>Best regards,</p>
            <p>HR System</p>
        </body>
        </html>
        """
