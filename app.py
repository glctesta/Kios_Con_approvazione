"""
Applicazione Web per Generazione Certificati/Adeverințe
Sostituisce la form VBA di Access con un'interfaccia web moderna
"""
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from datetime import datetime
import logging
import os
from db_connection import DatabaseConnection
from config_manager import ConfigManager
from certificate_generator import CertificateGenerator
from absence_report import AbsenceReportGenerator
from absence_request import AbsenceRequestManager
from badge_reader import BadgeReader
from kiosk_request_logger import KioskRequestLogger
from utils import send_email, get_email_recipients
from pdf_printer import print_pdf_silent, get_default_printer
from printer_keepalive import start_printer_keepalive, stop_printer_keepalive

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Inizializza connessione database
config_manager = ConfigManager()
db_connection = DatabaseConnection(config_manager)

# Inizializza Kiosk Request Logger per monitoraggio utilizzo
kiosk_logger = KioskRequestLogger(db_connection)




@app.route('/')
def launcher():
    """Pagina launcher principale con menu servizi"""
    return render_template('launcher.html')




@app.route('/certificati')
def certificati():
    """Pagina applicazione certificati/adeverințe"""
    return render_template('index.html')


@app.route('/absente')
def absente():
    """Pagina raport istoric absențe"""
    return render_template('absence.html')


@app.route('/cerere')
def cerere():
    """Pagina cerere absență"""
    return render_template('request.html')


@app.route('/verifica')
def verifica():
    """Pagina verificare stare cerere"""
    return render_template('check.html')


@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.svg',
        mimetype='image/svg+xml'
    )



@app.route('/api/news', methods=['GET'])
def get_news():
    """Recupera messaggi news dal database con priorità per mandatory"""
    conn = None
    try:
        # Crea connessione fresca per evitare "connection broken"
        conn = DatabaseConnection(config_manager).connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Errore connessione database'}), 500
        
        cursor = conn.cursor()
        
        # Data attuale
        current_date = datetime.now()
        
        # Query per recuperare news attive
        # Verifica che current_date sia COMPRESO tra StartNews ed EndNews
        query = """
        SELECT 
            NewId,
            EmployeerId,
            StartNews,
            EndNews,
            News,
            Publisher,
            IsMandatory,
            Printable
        FROM [Employee].[dbo].[News]
        WHERE ? >= StartNews AND ? <= EndNews
        ORDER BY IsMandatory DESC, StartNews ASC
        """
        
        cursor.execute(query, (current_date, current_date))
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({
                'success': True,
                'has_news': False,
                'news': []
            })
        
        # Separa news mandatory da quelle normali
        mandatory_news = []
        regular_news = []
        
        for row in rows:
            news_item = {
                'id': row[0],
                'employee_id': row[1],
                'start_date': row[2].isoformat() if row[2] else None,
                'end_date': row[3].isoformat() if row[3] else None,
                'message': row[4],
                'publisher': row[5],
                'is_mandatory': bool(row[6]),
                'printable': bool(row[7]) if len(row) > 7 else False
            }
            
            if news_item['is_mandatory']:
                mandatory_news.append(news_item)
            else:
                regular_news.append(news_item)
        
        # Se ci sono news mandatory, mostra solo quelle
        if mandatory_news:
            return jsonify({
                'success': True,
                'has_news': True,
                'news': mandatory_news,
                'is_mandatory': True
            })
        else:
            return jsonify({
                'success': True,
                'has_news': True,
                'news': regular_news,
                'is_mandatory': False
            })
        
    except Exception as e:
        logger.error(f"Errore recupero news: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # Chiudi connessione per liberare risorse
        if conn:
            try:
                conn.close()
            except:
                pass


@app.route('/api/slideshow-images', methods=['GET'])
def get_slideshow_images():
    """Recupera lista immagini disponibili per slideshow (file che iniziano con X o S, ordine random)"""
    try:
        import random
        
        images_dir = os.path.join(app.root_path, 'Images')
        
        if not os.path.exists(images_dir):
            return jsonify({
                'success': True,
                'images': []
            })
        
        # Estensioni immagini supportate
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        images = []
        for filename in os.listdir(images_dir):
            # Filtra solo file che iniziano con 'X' o 'S' (case-insensitive)
            first_char = filename.upper()[0] if filename else ''
            if first_char not in ['X', 'S']:
                continue
                
            ext = os.path.splitext(filename)[1].lower()
            if ext in valid_extensions:
                # URL relativo per accedere all'immagine
                images.append(f"/images/{filename}")
        
        # Randomizza l'ordine delle immagini
        random.shuffle(images)
        
        return jsonify({
            'success': True,
            'images': images
        })
        
    except Exception as e:
        logger.error(f"Errore recupero immagini slideshow: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve immagini dalla directory Images"""
    try:
        images_dir = os.path.join(app.root_path, 'Images')
        return send_from_directory(images_dir, filename)
    except Exception as e:
        logger.error(f"Errore serving immagine: {str(e)}")
        return jsonify({'success': False, 'error': 'Immagine non trovata'}), 404


@app.route('/api/validate-badge', methods=['POST'])
def validate_badge():
    """Valida badge RFID e recupera dati dipendente"""
    try:
        data = request.json
        badge_number = data.get('badgeNumber', '').strip()
        
        if not badge_number:
            return jsonify({
                'success': False, 
                'error': 'Numero badge non fornito'
            }), 400
        
        conn = db_connection.connect()
        badge_reader = BadgeReader(conn)
        
        is_valid, employee_data, error_msg = badge_reader.validate_badge_access(badge_number)
        
        if is_valid:
            return jsonify({
                'success': True,
                'employee': {
                    'id': employee_data['hire_history_id'],
                    'name': employee_data['full_name'],
                    'employeeId': employee_data['employee_id'],
                    'sex': employee_data['sex'],
                    'badgeNumber': employee_data['badge_number']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 404
    
    except Exception as e:
        logger.error(f"Errore nella validazione badge: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Recupera lista dipendenti attivi"""
    try:
        conn = db_connection.connect()
        cursor = conn.cursor()
        
        # Query per ottenere dipendenti attivi (dalla form VBA)
        query = """
        SELECT 
            H.EmployeeHireHistoryId,
            UPPER(E.EmployeeSurname + ' ' + E.EmployeeName) COLLATE Database_default AS EmployeeName,
            ET.IDEmployee,
            E.EmployeeSex
        FROM Employee.dbo.employees E
        INNER JOIN Employee.dbo.employeeHireHistory H 
            ON E.employeeid = H.employeeid
        INNER JOIN Timeclocking.dbo.Employee AS ET 
            ON E.EmployeeNID COLLATE Database_default = ET.UniqueID 
            AND ET.DataStop IS NULL
        INNER JOIN Timeclocking.dbo.Company C 
            ON ET.IDCompany = C.IDCompany 
            AND C.CompanyCUI = (select EmployeerFiscalCode as cui from employee.dbo.employeers where employeerid=2)
        WHERE H.endWorkDate IS NULL 
            AND H.employeerid = (
                SELECT employeerid 
                FROM employee.dbo.employeers 
                WHERE employeerFiscalCode = (select EmployeerFiscalCode as cui from employee.dbo.employeers where employeerid=2)
            )
        ORDER BY E.employeeSurName
        """
        
        cursor.execute(query)
        employees = []
        for row in cursor.fetchall():
            employees.append({
                'id': row[0],
                'name': row[1],
                'timeclockId': row[2],
                'sex': row[3]
            })
        
        return jsonify({'success': True, 'employees': employees})
    
    except Exception as e:
        logger.error(f"Errore nel recupero dipendenti: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/certificate-reasons', methods=['GET'])
def get_certificate_reasons():
    """Recupera lista motivi certificato"""
    try:
        conn = db_connection.connect()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            CerificateReasonId,
            CerificateReason,
            CanTypeSpecialReason,
            SameIdGroup
        FROM employee.dbo.CertificateReasons 
        ORDER BY CerificateReason
        """
        
        cursor.execute(query)
        reasons = []
        for row in cursor.fetchall():
            reasons.append({
                'id': row[0],
                'reason': row[1],
                'canTypeSpecial': bool(row[2]),
                'groupId': row[3] if row[3] else 0
            })
        
        return jsonify({'success': True, 'reasons': reasons})
    
    except Exception as e:
        logger.error(f"Errore nel recupero motivi: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/add-reason', methods=['POST'])
def add_reason():
    """Aggiunge nuovo motivo certificato"""
    try:
        data = request.json
        reason = data.get('reason', '').upper()
        can_type_special = data.get('canTypeSpecial', False)
        
        conn = db_connection.connect()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO employee.dbo.CertificateReasons 
        (CerificateReason, CanTypeSpecialReason) 
        VALUES (?, ?)
        """
        
        cursor.execute(query, (reason, 1 if can_type_special else None))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Motivo aggiunto con successo'})
    
    except Exception as e:
        logger.error(f"Errore nell'aggiunta motivo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-certificate', methods=['POST'])
def generate_certificate():
    """Genera certificato e lo stampa/invia"""
    badge_number = None  # Per logging kiosk
    try:
        data = request.json
        employee_id = data.get('employeeId')
        reason = data.get('reason')
        typed_reason = data.get('typedReason', '')
        group_id = data.get('groupId', 0)
        badge_number = data.get('badgeNumber', '')  # Recupera badge per logging
        
        # Validazione
        if not employee_id or not reason:
            return jsonify({
                'success': False, 
                'error': 'Dipendente e motivo sono obbligatori'
            }), 400
        
        conn = db_connection.connect()
        
        # Genera il certificato
        generator = CertificateGenerator(conn)
        result = generator.generate_certificate(
            employee_hire_history_id=employee_id,
            reason=reason,
            typed_reason=typed_reason,
            group_id=group_id
        )
        
        if result['success']:
            pdf_path = result.get('pdf_path')
            
            # Log richiesta kiosk
            if badge_number:
                kiosk_logger.log_certificate_request(badge_number, reason, executed=True)
            
            # Stampa automatica PDF
            print_success = False
            printer_name = None
            if pdf_path and os.path.exists(pdf_path):
                try:
                    printer_name = get_default_printer()
                    logger.info(f"Tentativo stampa PDF su: {printer_name}")
                    print_success = print_pdf_silent(pdf_path, printer_name)
                    if print_success:
                        logger.info(f"PDF inviato alla stampante: {printer_name}")
                    else:
                        logger.warning("Stampa PDF fallita, PDF salvato in temp/")
                except Exception as print_error:
                    logger.error(f"Errore stampa PDF: {str(print_error)}")
            
            # Invia email se richiesto
            if result.get('email_required'):
                try:
                    recipients = get_email_recipients(conn, 'Sys_Email_HR')
                    send_email(
                        recipients=recipients,
                        subject=result['email_subject'],
                        body=result['email_body'],
                        is_html=True
                    )
                except Exception as email_error:
                    logger.warning(f"Errore invio email: {str(email_error)}")
            
            return jsonify({
                'success': True,
                'message': 'Certificato generato con successo',
                'documentNumber': result['document_number'],
                'documentDate': result['document_date'],
                'pdfPath': result.get('pdf_path'),
                'printed': print_success,
                'printerName': printer_name
            })
        else:
            # Log fallimento
            if badge_number:
                kiosk_logger.log_certificate_request(badge_number, reason, executed=False)
            
            return jsonify({
                'success': False,
                'error': result.get('error', 'Errore sconosciuto')
            }), 500
    
    except Exception as e:
        logger.error(f"Errore nella generazione certificato: {str(e)}")
        
        # Log fallimento
        if badge_number:
            kiosk_logger.log_certificate_request(badge_number, reason or "Unknown", executed=False)
        
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/print-pdf/<path:filename>')
def print_pdf(filename):
    """Invia PDF al browser per stampa"""
    try:
        pdf_path = os.path.join('temp', filename)
        if os.path.exists(pdf_path):
            return send_file(pdf_path, mimetype='application/pdf')
        else:
            return jsonify({'success': False, 'error': 'File non trovato'}), 404
    except Exception as e:
        logger.error(f"Errore nell'invio PDF: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-absence-report', methods=['POST'])
def generate_absence_report():
    """Genera raport istoric absențe"""
    try:
        logger.info("=== INIZIO GENERAZIONE REPORT ABSENȚE ===")
        data = request.json
        logger.info(f"Dati ricevuti: {data}")
        
        badge_number = data.get('badgeNumber', '').strip()
        year = data.get('year')
        
        logger.info(f"Badge: {badge_number}, Anno: {year}")
        
        if not badge_number:
            logger.error("Badge number non fornito")
            return jsonify({
                'success': False,
                'error': 'Numero badge non fornito'
            }), 400
        
        if not year:
            year = datetime.now().year
        
        # Genera report
        logger.info("Connessione al database...")
        conn = db_connection.connect()
        if not conn:
            logger.error("Errore connessione database")
            return jsonify({
                'success': False,
                'error': 'Errore connessione database'
            }), 500
        
        # Normalizza badge number (padding con zeri a sinistra)
        badge_reader = BadgeReader(conn)
        normalized_badge = badge_reader.normalize_badge_number(badge_number)
        logger.info(f"Badge normalizzato: {normalized_badge}")
        
        logger.info("Creazione AbsenceReportGenerator...")
        report_generator = AbsenceReportGenerator(conn)
        
        logger.info(f"Generazione report per badge {normalized_badge}, anno {year}...")
        pdf_path = report_generator.generate_report(normalized_badge, year)
        logger.info(f"PDF generato: {pdf_path}")
        
        if not pdf_path:
            # Log fallimento
            kiosk_logger.log_absence_report_request(badge_number, year, executed=False)
            return jsonify({
                'success': False,
                'error': 'Errore generazione report'
            }), 500
        
        # Log successo richiesta
        kiosk_logger.log_absence_report_request(badge_number, year, executed=True)
        
        # Stampa automatica
        printer_name = get_default_printer()
        print_success = False
        
        if printer_name:
            print_success = print_pdf_silent(pdf_path, printer_name)
            logger.info(f"Stampa report: {print_success}")
        
        # Normalizza path per URL
        pdf_filename = os.path.basename(pdf_path)
        pdf_url = f"/api/print-pdf/{pdf_filename}"
        
        return jsonify({
            'success': True,
            'pdf_path': pdf_path,
            'pdf_url': pdf_url,
            'print_success': print_success,
            'printer_name': printer_name or 'Nessuna stampante configurata'
        })
        
    except Exception as e:
        print(f"\n\n!!! ERRORE REPORT ABSENȚE: {str(e)} !!!\n")
        logger.error(f"Errore generazione report absențe: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(traceback.format_exc())
        # Log fallimento
        if 'badge_number' in locals() and badge_number:
            kiosk_logger.log_absence_report_request(badge_number, year if 'year' in locals() else datetime.now().year, executed=False)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========================================
# API RICHIESTE ASSENZA
# ========================================

@app.route('/api/request-types', methods=['GET'])
def get_request_types():
    """Recupera tipi di richiesta disponibili"""
    try:
        conn = db_connection.connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Errore connessione database'}), 500
        
        request_manager = AbsenceRequestManager(conn)
        request_types = request_manager.get_request_types()
        
        return jsonify({
            'success': True,
            'request_types': request_types
        })
        
    except Exception as e:
        logger.error(f"Errore recupero tipi richiesta: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/available-vacation-days', methods=['POST'])
def get_available_vacation_days():
    """Calcola giorni ferie disponibili"""
    try:
        data = request.json
        badge_number = data.get('badgeNumber', '').strip()
        year = data.get('year', datetime.now().year)
        
        if not badge_number:
            return jsonify({'success': False, 'error': 'Badge non fornito'}), 400
        
        conn = db_connection.connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Errore connessione database'}), 500
        
        # Normalizza badge
        badge_reader = BadgeReader(conn)
        normalized_badge = badge_reader.normalize_badge_number(badge_number)
        
        request_manager = AbsenceRequestManager(conn)
        vacation_data = request_manager.get_available_vacation_days(normalized_badge, year)
        
        if vacation_data:
            return jsonify({
                'success': True,
                'available_days': vacation_data['available_days'],
                'employee_name': f"{vacation_data['employee_surname']} {vacation_data['employee_name']}"
            })
        else:
            return jsonify({'success': False, 'error': 'Dati non trovati'}), 404
        
    except Exception as e:
        logger.error(f"Errore calcolo giorni disponibili: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/calculate-working-days', methods=['POST'])
def calculate_working_days():
    """Calcola giorni lavorativi escludendo weekend e festività"""
    try:
        data = request.json
        date_start_str = data.get('dateStart')
        date_end_str = data.get('dateEnd')
        request_type_id = data.get('requestTypeId')
        
        if not date_start_str or not date_end_str:
            return jsonify({'success': False, 'error': 'Date non fornite'}), 400
        
        date_start = datetime.strptime(date_start_str, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end_str, '%Y-%m-%d').date()
        
        conn = db_connection.connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Errore connessione database'}), 500
        
        request_manager = AbsenceRequestManager(conn)
        
        # Recupera festività per l'anno
        year = date_start.year
        holidays = request_manager.get_holidays(year)
        
        # Se il periodo attraversa più anni, recupera anche festività anno successivo
        if date_end.year > year:
            holidays.extend(request_manager.get_holidays(date_end.year))
        
        # Calcola giorni lavorativi
        working_days = request_manager.calculate_working_days(date_start, date_end, holidays)
        
        return jsonify({
            'success': True,
            'working_days': working_days,
            'total_days': (date_end - date_start).days + 1
        })
        
    except Exception as e:
        logger.error(f"Errore calcolo giorni lavorativi: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/submit-absence-request', methods=['POST'])
def submit_absence_request():
    """Invia richiesta assenza"""
    try:
        logger.info("=== INIZIO INVIO RICHIESTA ASSENZA ===")
        data = request.json
        logger.info(f"Dati ricevuti: {data}")
        
        badge_number = data.get('badgeNumber', '').strip()
        request_type_id = data.get('requestTypeId')
        date_start_str = data.get('dateStart')
        date_end_str = data.get('dateEnd')
        
        # Validazioni
        if not badge_number:
            return jsonify({'success': False, 'error': 'Badge non fornito'}), 400
        
        if not request_type_id:
            return jsonify({'success': False, 'error': 'Tipo richiesta non fornito'}), 400
        
        if not date_start_str or not date_end_str:
            return jsonify({'success': False, 'error': 'Date non fornite'}), 400
        
        date_start = datetime.strptime(date_start_str, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end_str, '%Y-%m-%d').date()
        request_date = datetime.now().date()
        year = date_start.year
        
        # Connessione database
        conn = db_connection.connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Errore connessione database'}), 500
        
        # Normalizza badge
        badge_reader = BadgeReader(conn)
        normalized_badge = badge_reader.normalize_badge_number(badge_number)
        logger.info(f"Badge normalizzato: {normalized_badge}")
        
        request_manager = AbsenceRequestManager(conn)
        
        # Se è richiesta ferie (IDRequestType = 1), verifica disponibilità
        if request_type_id == 1:
            logger.info("Verifica disponibilità ferie...")
            vacation_data = request_manager.get_available_vacation_days(normalized_badge, year)
            
            if not vacation_data:
                return jsonify({'success': False, 'error': 'Impossibile verificare giorni disponibili'}), 500
            
            # Calcola giorni lavorativi richiesti
            holidays = request_manager.get_holidays(year)
            if date_end.year > year:
                holidays.extend(request_manager.get_holidays(date_end.year))
            
            working_days = request_manager.calculate_working_days(date_start, date_end, holidays)
            logger.info(f"Giorni lavorativi richiesti: {working_days}")
            logger.info(f"Giorni disponibili: {vacation_data['available_days']}")
            
            if working_days > vacation_data['available_days']:
                return jsonify({
                    'success': False,
                    'error': f"Giorni richiesti ({working_days}) > Giorni disponibili ({vacation_data['available_days']})"
                }), 400
            
            hire_history_id = vacation_data['hire_history_id']
            employee_name = f"{vacation_data['employee_surname']} {vacation_data['employee_name']}"
        else:
            # Per altri tipi di richiesta, recupera solo hire_history_id
            employee_data = badge_reader.get_employee_by_badge(normalized_badge)
            if not employee_data:
                return jsonify({'success': False, 'error': 'Dipendente non trovato'}), 404
            
            hire_history_id = employee_data['hire_history_id']
            employee_name = employee_data['full_name']
            
            holidays = request_manager.get_holidays(year)
            if date_end.year > year:
                holidays.extend(request_manager.get_holidays(date_end.year))
            working_days = request_manager.calculate_working_days(date_start, date_end, holidays)
        
        # Verifica richieste duplicate
        logger.info("Verifica richieste duplicate...")
        is_duplicate = request_manager.check_duplicate_request(
            hire_history_id, request_type_id, date_start, date_end
        )
        
        if is_duplicate:
            logger.warning("Richiesta duplicata rilevata")
            return jsonify({
                'success': False,
                'error': 'Există deja o cerere identică pentru această perioadă. Vă rugăm să verificați cererile anterioare.'
            }), 400
        
        # Verifica regole DayNoZone (preavviso minimo richiesto)
        logger.info("Verifica regole DayNoZone...")
        validation_result = request_manager.validate_absence_date_rule(request_type_id, date_start)
        
        if not validation_result['valid']:
            logger.warning(f"Validazione DayNoZone fallita: {validation_result['message']}")
            return jsonify({
                'success': False,
                'error': validation_result['message']
            }), 400
        
        # Crea entry nel registro
        logger.info("Creazione entry registro...")
        registro_id = request_manager.create_registry_entry(year, request_date, employee_name)
        
        if not registro_id:
            return jsonify({'success': False, 'error': 'Errore creazione registro'}), 500
        
        logger.info(f"Registro creato: {registro_id}")
        
        # Recupera nome tipo richiesta (prima di usarlo)
        request_types = request_manager.get_request_types()
        request_type_name = next((rt['name'] for rt in request_types if rt['id'] == request_type_id), 'Sconosciuto')
        
        # Salva richiesta assenza
        logger.info("Salvataggio richiesta assenza...")
        absence_request_id = request_manager.save_absence_request(
            registro_id, hire_history_id, request_type_id, date_start, date_end,
            username=employee_name,
            request_type_name=request_type_name
        )
        
        if not absence_request_id:
            return jsonify({'success': False, 'error': 'Errore salvataggio richiesta'}), 500
        
        logger.info(f"Richiesta salvata: {absence_request_id}")
        
        # Recupera info registro
        registry_info = request_manager.get_registry_info(registro_id)
        
        if not registry_info:
            return jsonify({'success': False, 'error': 'Errore recupero info registro'}), 500
        
        # Genera PDF conferma
        logger.info("Generazione PDF conferma...")
        employee_data_pdf = {
            'name': employee_name.split()[-1] if ' ' in employee_name else employee_name,
            'surname': employee_name.split()[0] if ' ' in employee_name else '',
            'badge': normalized_badge
        }
        
        request_data_pdf = {
            'type_name': request_type_name,
            'date_start': date_start,
            'date_end': date_end,
            'working_days': working_days
        }
        
        pdf_path = request_manager.generate_confirmation_pdf(employee_data_pdf, request_data_pdf, registry_info)
        
        if not pdf_path:
            return jsonify({'success': False, 'error': 'Errore generazione PDF'}), 500
        
        logger.info(f"PDF generato: {pdf_path}")
        
        # Stampa automatica
        printer_name = get_default_printer()
        print_success = False
        
        if printer_name:
            print_success = print_pdf_silent(pdf_path, printer_name)
            logger.info(f"Stampa: {print_success}")
        
        # Normalizza path per URL
        pdf_filename = os.path.basename(pdf_path)
        pdf_url = f"/api/print-pdf/{pdf_filename}"
        
        # Invia email notifica ai manager
        try:
            logger.info("Recupero email manager...")
            manager_emails = request_manager.get_manager_emails(hire_history_id)
            
            # Se non ci sono manager, usa email fallback
            if not manager_emails:
                logger.warning(f"Nessun manager trovato per hire_history_id {hire_history_id}, uso email fallback")
                manager_emails = ['gianluca.testa@vandewiele.com']
            
            logger.info(f"Invio email a: {manager_emails}")
            
            # Prepara email HTML
            subject = f"Nouă cerere de absență - {registry_info['doc_name']}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #667eea;">Nouă Cerere de Absență</h2>
                
                <p>S-a înregistrat o nouă cerere de absență care necesită aprobare:</p>
                
                <table style="border-collapse: collapse; margin: 20px 0;">
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Număr cerere:</td>
                        <td style="padding: 8px;">{registry_info['doc_name']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Data cerere:</td>
                        <td style="padding: 8px;">{registry_info['doc_date'].strftime('%d.%m.%Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Angajat:</td>
                        <td style="padding: 8px;">{employee_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Tip absență:</td>
                        <td style="padding: 8px;">{request_type_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Perioada:</td>
                        <td style="padding: 8px;">{date_start.strftime('%d.%m.%Y')} - {date_end.strftime('%d.%m.%Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Zile lucrătoare:</td>
                        <td style="padding: 8px;">{working_days}</td>
                    </tr>
                </table>
                
                <p style="color: #f59e0b; font-weight: bold;">⚠️ Această cerere este în așteptare de aprobare.</p>
                
                <p>Vă rugăm să verificați și să aprobați/respingeți cererea în sistemul de management.</p>
                
                <hr style="margin: 30px 0; border: 1px solid #e5e7eb;">
                
                <p style="font-size: 12px; color: #718096;">
                    Acest email a fost generat automat de sistemul Kiosk HR.<br>
                    Nu răspundeți la acest email.
                </p>
            </body>
            </html>
            """
            
            # Invia email usando utils.send_email
            send_email(
                recipients=manager_emails,
                subject=subject,
                body=body,
                is_html=True
            )
            
            logger.info("Email notifica inviata con successo")
                
        except Exception as email_error:
            # Non bloccare la richiesta se l'email fallisce
            logger.error(f"Errore invio email notifica: {str(email_error)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Log richiesta kiosk
        kiosk_logger.log_absence_request_submission(badge_number, request_type_name, executed=True)
        
        return jsonify({
            'success': True,
            'request_number': registry_info['doc_name'],
            'absence_request_id': absence_request_id,
            'registro_id': registro_id,
            'pdf_path': pdf_path,
            'pdf_url': pdf_url,
            'print_success': print_success,
            'printer_name': printer_name or 'Nessuna stampante configurata'
        })
        
    except Exception as e:
        logger.error(f"Errore invio richiesta assenza: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500




@app.route('/api/check-request-status', methods=['POST'])
def check_request_status():
    """Verifica stato richiesta assenza tramite numero richiesta"""
    try:
        data = request.json
        request_number = data.get('requestNumber', '').strip()
        
        if not request_number:
            return jsonify({'success': False, 'error': 'Număr cerere non fornito'}), 400
        
        conn = db_connection.connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Errore connessione database'}), 500
        
        cursor = conn.cursor()
        
        # Query per recuperare info richiesta incluso EmployrrHireHistoryId
        query = """
        SELECT 
            R.DocName AS RequestNumber,
            R.DocDate AS RequestDate,
            AR.AbsenceRequestId,
            AR.IDRequestType,
            RT.RequestName AS RequestType,
            AR.DateStart,
            AR.DateEnd,
            AR.Approved,
            AR.Rejected,
            AR.ApprovedBy,
            DATEDIFF(DAY, AR.DateStart, AR.DateEnd) + 1 AS TotalDays,
            AR.EmployrrHireHistoryId
        FROM [Employee].[dbo].[Registry] R
        INNER JOIN [Employee].[dbo].[AbsenceRequestes] AR 
            ON R.RegistroId = AR.RegistroId
        LEFT JOIN [Timeclocking].[dbo].[RequestType] RT
            ON AR.IDRequestType = RT.IDRequestType
        WHERE R.DocName = ?
        """
        
        cursor.execute(query, (request_number,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'success': False,
                'error': f'Cererea cu numărul {request_number} nu a fost găsită'
            }), 404
        
        # Costruisci risposta
        approved_date = row[7]
        rejected_flag = row[8]
        approved_by = row[9]
        date_start = row[5]
        date_end = row[6]
        hire_history_id = row[11]
        
        # Data attuale
        current_date = datetime.now().date()
        
        # Determina stato approvazione
        # Per essere APPROVATA deve:
        # 1. Approved IS NOT NULL
        # 2. Approved != '1900-01-01'
        # 3. Approved >= DateStart AND Approved <= DateEnd
        # 4. ApprovedBy IS NOT NULL
        
        is_approved = False
        if approved_date and approved_by:
            # Verifica che non sia la data placeholder
            if approved_date.year > 1900:
                # Verifica che sia nel range del periodo richiesto
                if date_start and date_end:
                    if date_start <= approved_date.date() <= date_end:
                        is_approved = True
        
        # Determina se la richiesta è rifiutata esplicitamente
        is_rejected = bool(rejected_flag and rejected_flag != 0)
        
        # Determina se la richiesta è scaduta (expired)
        # Una richiesta è scaduta se:
        # - La data attuale è maggiore della data di inizio
        # - NON è stata approvata (Approved è NULL o placeholder o ApprovedBy è NULL)
        # - NON è stata rifiutata esplicitamente
        is_expired = False
        if date_start and current_date > date_start:
            if not is_approved and not is_rejected:
                is_expired = True
        
        # Determina se è veramente pending (in attesa)
        # Una richiesta è pending se:
        # - La data attuale è <= data di inizio
        # - NON è stata approvata
        # - NON è stata rifiutata
        is_pending = False
        if date_start and current_date <= date_start:
            if not is_approved and not is_rejected:
                is_pending = True
        
        # Determina lo stato finale
        if is_approved:
            status = 'approved'
            status_text = 'Aprobată'
        elif is_rejected:
            status = 'rejected'
            status_text = 'Respinsă'
        elif is_expired:
            status = 'expired'
            status_text = 'Expirată (neautorizată la timp)'
        elif is_pending:
            status = 'pending'
            status_text = 'În așteptare'
        else:
            status = 'unknown'
            status_text = 'Necunoscut'
        
        request_info = {
            'request_number': row[0],
            'request_date': row[1].isoformat() if row[1] else None,
            'absence_request_id': row[2],
            'request_type_id': row[3],
            'request_type': row[4] or 'Necunoscut',
            'date_start': row[5].isoformat() if row[5] else None,
            'date_end': row[6].isoformat() if row[6] else None,
            'approved': approved_date.isoformat() if approved_date else None,
            'rejected': rejected_flag,
            'approved_by': approved_by,
            'working_days': row[10],
            'hire_history_id': hire_history_id,
            'is_approved': is_approved,
            'is_rejected': is_rejected,
            'is_expired': is_expired,
            'is_pending': is_pending,
            'status': status,
            'status_text': status_text,
            'can_resend': is_pending  # Può reinviare solo se è ancora pending
        }
        
        return jsonify({
            'success': True,
            'request': request_info
        })
        
    except Exception as e:
        logger.error(f"Errore verifica stato richiesta: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resend-absence-notification', methods=['POST'])
def resend_absence_notification():
    """Reinvia notifica email ai manager per richiesta assenza pending"""
    try:
        data = request.json
        request_number = data.get('requestNumber', '').strip()
        
        if not request_number:
            return jsonify({'success': False, 'error': 'Număr cerere non fornito'}), 400
        
        conn = db_connection.connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Errore connessione database'}), 500
        
        cursor = conn.cursor()
        
        # Query per recuperare tutte le info necessarie
        query = """
        SELECT 
            R.DocName AS RequestNumber,
            R.DocDate AS RequestDate,
            R.RegistroId,
            AR.AbsenceRequestId,
            AR.IDRequestType,
            RT.RequestName AS RequestType,
            AR.DateStart,
            AR.DateEnd,
            AR.EmployrrHireHistoryId,
            UPPER(E.EmployeeSurname + ' ' + E.EmployeeName) AS EmployeeName,
            DATEDIFF(DAY, AR.DateStart, AR.DateEnd) + 1 AS TotalDays
        FROM [Employee].[dbo].[Registry] R
        INNER JOIN [Employee].[dbo].[AbsenceRequestes] AR 
            ON R.RegistroId = AR.RegistroId
        LEFT JOIN [Timeclocking].[dbo].[RequestType] RT
            ON AR.IDRequestType = RT.IDRequestType
        INNER JOIN [Employee].[dbo].[EmployeeHireHistory] H
            ON AR.EmployrrHireHistoryId = H.EmployeeHireHistoryId
        INNER JOIN [Employee].[dbo].[Employees] E
            ON H.EmployeeId = E.EmployeeId
        WHERE R.DocName = ?
        """
        
        cursor.execute(query, (request_number,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'success': False,
                'error': f'Cererea cu numărul {request_number} nu a fost găsită'
            }), 404
        
        # Estrai dati
        doc_name = row[0]
        doc_date = row[1]
        hire_history_id = row[8]
        employee_name = row[9]
        request_type_name = row[5] or 'Sconosciuto'
        date_start = row[6]
        date_end = row[7]
        working_days = row[10]
        
        # Recupera email manager
        request_manager = AbsenceRequestManager(conn)
        manager_emails = request_manager.get_manager_emails(hire_history_id)
        
        # Se non ci sono manager, usa email fallback
        if not manager_emails:
            logger.warning(f"Nessun manager trovato per hire_history_id {hire_history_id}, uso email fallback")
            manager_emails = ['gianluca.testa@vandewiele.com']
        
        logger.info(f"Reinvio notifica a: {manager_emails}")
        
        # Prepara email HTML (stesso template di submit_absence_request)
        subject = f"Promemoria: Cerere de absență - {doc_name}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #667eea;">🔔 Promemoria: Cerere de Absență în Așteptare</h2>
            
            <p>Această cerere de absență este încă în așteptare de aprobare:</p>
            
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Număr cerere:</td>
                    <td style="padding: 8px;">{doc_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Data cerere:</td>
                    <td style="padding: 8px;">{doc_date.strftime('%d.%m.%Y')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Angajat:</td>
                    <td style="padding: 8px;">{employee_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Tip absență:</td>
                    <td style="padding: 8px;">{request_type_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Perioada:</td>
                    <td style="padding: 8px;">{date_start.strftime('%d.%m.%Y')} - {date_end.strftime('%d.%m.%Y')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Zile lucrătoare:</td>
                    <td style="padding: 8px;">{working_days}</td>
                </tr>
            </table>
            
            <p style="color: #f59e0b; font-weight: bold;">⚠️ Această cerere necesită aprobare urgentă.</p>
            
            <p>Vă rugăm să verificați și să aprobați/respingeți cererea în sistemul de management.</p>
            
            <hr style="margin: 30px 0; border: 1px solid #e5e7eb;">
            
            <p style="font-size: 12px; color: #718096;">
                Acest email a fost generat automat de sistemul Kiosk HR.<br>
                Nu răspundeți la acest email.
            </p>
        </body>
        </html>
        """
        
        # Invia email
        send_email(
            recipients=manager_emails,
            subject=subject,
            body=body,
            is_html=True
        )
        
        logger.info("Email promemoria inviata con successo")
        
        return jsonify({
            'success': True,
            'message': 'Notificare retrimisă cu succes',
            'recipients': manager_emails
        })
        
    except Exception as e:
        logger.error(f"Errore reinvio notifica: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/do-print', methods=['POST'])
@app.route('/api/do-print/<filename>', methods=['GET'])
def print_pdf_endpoint(filename=None):
    """Stampa PDF su stampante predefinita"""
    try:
        # Gestisci GET (con filename nell'URL) o POST (con pdf_path nel body)
        if filename:
            # GET request - filename nell'URL
            pdf_path = os.path.join('temp', filename)
            logger.info(f"GET request - filename: {filename}, path: {pdf_path}")
        else:
            # POST request - pdf_path nel body
            data = request.json
            pdf_path = data.get('pdf_path', '')
            logger.info(f"POST request - pdf_path: {pdf_path}")
        
        if not pdf_path:
            logger.error("Path PDF non fornito")
            return jsonify({'success': False, 'error': 'Path PDF non fornito'}), 400
        
        # Se il path non è assoluto, rendilo assoluto
        if not os.path.isabs(pdf_path):
            pdf_path = os.path.abspath(pdf_path)
            logger.info(f"Path convertito in assoluto: {pdf_path}")
        
        # Verifica che il file esista
        if not os.path.exists(pdf_path):
            logger.error(f"File PDF non trovato: {pdf_path}")
            return jsonify({'success': False, 'error': f'File PDF non trovato: {os.path.basename(pdf_path)}'}), 404
        
        # Ottieni stampante predefinita
        printer_name = get_default_printer()
        logger.info(f"Stampante predefinita: {printer_name}")
        
        if not printer_name:
            logger.error("Nessuna stampante configurata")
            return jsonify({'success': False, 'error': 'Nessuna stampante configurata'}), 500
        
        # Stampa PDF
        logger.info(f"Avvio stampa: {pdf_path} su {printer_name}")
        print_success = print_pdf_silent(pdf_path, printer_name)
        
        if print_success:
            logger.info(f"PDF stampato con successo: {pdf_path}")
            return jsonify({
                'success': True,
                'message': 'PDF stampato con successo',
                'printer_name': printer_name
            })
        else:
            logger.error(f"Errore stampa PDF: {pdf_path}")
            return jsonify({'success': False, 'error': 'Errore durante la stampa'}), 500
        
    except Exception as e:
        logger.error(f"Errore endpoint print-pdf: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500



# ========================================
# API NETWORK MONITORING
# ========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint per verificare connessione server"""
    try:
        # Verifica connessione database
        conn = db_connection.connect()
        db_status = 'ok' if conn else 'error'
        
        return jsonify({
            'status': 'ok',
            'database': db_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/log-offline', methods=['POST'])
def log_offline_event():
    """Registra eventi offline della rete"""
    try:
        from offline_logger import get_offline_logger
        
        data = request.json
        event_type = data.get('event_type')  # 'start' o 'end'
        timestamp = data.get('timestamp')
        duration_seconds = data.get('duration_seconds')
        user_agent = data.get('user_agent')
        page = data.get('page')
        
        offline_logger = get_offline_logger()
        offline_logger.log_event(
            event_type=event_type,
            timestamp=timestamp,
            duration_seconds=duration_seconds,
            user_agent=user_agent,
            page=page
        )
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Errore log offline event: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/offline-statistics', methods=['GET'])
def get_offline_statistics():
    """Recupera statistiche eventi offline"""
    try:
        from offline_logger import get_offline_logger
        
        hours = request.args.get('hours', 24, type=int)
        
        offline_logger = get_offline_logger()
        stats = offline_logger.get_statistics(hours=hours)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Errore recupero statistiche offline: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/news/print', methods=['POST'])
def print_news():
    """Stampa una news specifica con logo e registrazione in KiosRequestes"""
    conn = None  # Inizializza per evitare UnboundLocalError in finally
    try:
        data = request.json
        news_id = data.get('newsId')
        news_text = data.get('newsText')
        news_date = data.get('newsDate')
        publisher = data.get('publisher', 'Sistema')
        printable = data.get('printable', False)  # Nuovo campo
        
        # Controllo se la news è stampabile
        if not printable:
            logger.warning(f"⚠️ Tentativo stampa news {news_id} NON stampabile (Printable=0)")
            return jsonify({
                'success': False, 
                'error': 'Questa news non può essere stampata'
            }), 403
        
        if not news_id or not news_text:
            return jsonify({'success': False, 'error': 'Dati incompleti'}), 400
        
        logger.info(f"📄 Richiesta stampa news ID: {news_id}")
        
        conn = db_connection.connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Errore connessione database'}), 500
        
        # 1. Registra richiesta in KiosRequestes
        ip_address = request.remote_addr or 'Unknown'
        room_name = 'Kiosk HR'
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO [Employee].[dbo].[KiosRequestes] 
                (RequestDate, IpRequest, RequestBy, RequestWhat, Executed)
            VALUES (GETDATE(), ?, ?, ?, 0)
        """, (ip_address, room_name, f'Stampa News {news_id}'))
        conn.commit()
        
        logger.info("✅ Richiesta registrata in KiosRequestes")
        
        # 2. Genera PDF della news
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from datetime import datetime as dt
        
        # Registra font
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
            font_name = 'DejaVuSans'
            font_bold = 'DejaVuSans-Bold'
        except:
            font_name = 'Helvetica'
            font_bold = 'Helvetica-Bold'
        
        # Crea PDF
        pdf_filename = f"news_{news_id}_{dt.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join('temp', pdf_filename)
        
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Logo
        if os.path.exists('logo.png'):
            try:
                img = ImageReader('logo.png')
                c.drawImage(img, 30*mm, height - 40*mm, width=40*mm, height=20*mm, preserveAspectRatio=True)
            except:
                pass
        
        # Titolo
        c.setFont(font_bold, 24)
        c.drawString(80*mm, height - 30*mm, "Comunicare Companiei")
        
        # Linea separatore
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.setLineWidth(2)
        c.line(30*mm, height - 45*mm, width - 30*mm, height - 45*mm)
        
        # Metadati
        y_pos = height - 55*mm
        c.setFont(font_bold, 14)
        c.drawString(30*mm, y_pos, "Data:")
        c.setFont(font_name, 14)
        formatted_date = dt.fromisoformat(news_date.replace('Z', '+00:00')).strftime('%d/%m/%Y') if news_date else dt.now().strftime('%d/%m/%Y')
        c.drawString(70*mm, y_pos, formatted_date)
        
        y_pos -= 8*mm
        c.setFont(font_bold, 14)
        c.drawString(30*mm, y_pos, "Publicat de:")
        c.setFont(font_name, 14)
        c.drawString(70*mm, y_pos, publisher)
        
        y_pos -= 8*mm
        c.setFont(font_bold, 14)
        c.drawString(30*mm, y_pos, "ID Știri:")
        c.setFont(font_name, 14)
        c.drawString(70*mm, y_pos, str(news_id))
        
        y_pos -= 5*mm
        c.setLineWidth(1)
        c.line(30*mm, y_pos, width - 30*mm, y_pos)
        
        # Contenuto con font 18 (ridotto leggermente per più spazio)
        y_pos -= 10*mm
        c.setFont(font_name, 18)
        
        # Margini migliorati
        left_margin = 35*mm  # Maggiore margine sinistro
        max_width = width - 70*mm  # Margini bilanciati
        
        # Split testo su punti per paragrafi
        # Ogni frase dopo un punto inizia su nuova riga
        import re
        
        # Split su punteggiatura (.!?) seguita da spazio
        # Mantiene la punteggiatura nella frase
        sentence_endings = re.split(r'([.!?])\s+', news_text)
        
        sentences = []
        for i in range(0, len(sentence_endings)-1, 2):
            if sentence_endings[i].strip():
                sentence = sentence_endings[i].strip() + sentence_endings[i+1]
                sentences.append(sentence)
        
        # Aggiungi ultima parte se non termina con punteggiatura
        if len(sentence_endings) % 2 == 1 and sentence_endings[-1].strip():
            sentences.append(sentence_endings[-1].strip())
        
        logger.info(f"📝 Split testo in {len(sentences)} frasi per formattazione PDF")
        
        # Word wrap per ogni frase
        lines = []
        for idx, sentence in enumerate(sentences):
            words = sentence.split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if c.stringWidth(test_line, font_name, 18) <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Aggiungi spazio extra dopo ogni frase (tranne l'ultima)
            if idx < len(sentences) - 1:
                lines.append('PARAGRAPH_BREAK')  # Marker speciale invece di stringa vuota
        
        logger.info(f"📄 Formattate {len(lines)} righe (inclusi {sentences.__len__()-1} spazi paragrafo)")
        
        # Stampa linee con spaziatura migliorata
        line_height = 6.5*mm
        paragraph_spacing = 3*mm  # Spazio extra tra paragrafi
        
        for line in lines:
            if y_pos < 40*mm:
                c.showPage()
                c.setFont(font_name, 18)
                y_pos = height - 30*mm
            
            if line == 'PARAGRAPH_BREAK':
                # Marker = spazio tra paragrafi
                y_pos -= paragraph_spacing
            else:
                c.drawString(left_margin, y_pos, line)
                y_pos -= line_height
        
        # Footer
        c.setFont(font_name, 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        footer = f"Tipărit la {dt.now().strftime('%d/%m/%Y ora %H:%M')} de {room_name}"
        c.drawCentredString(width / 2, 20*mm, footer)
        c.save()
        
        # 3. Stampa
        printer_name = get_default_printer()
        print_success = False
        
        if printer_name and os.path.exists(pdf_path):
            print_success = print_pdf_silent(pdf_path, printer_name)
            if print_success:
                cursor.execute("""
                    UPDATE [Employee].[dbo].[KiosRequestes]
                    SET Executed = 1
                    WHERE RequestWhat = ? AND RequestDate = (
                        SELECT MAX(RequestDate) FROM [Employee].[dbo].[KiosRequestes]
                        WHERE RequestWhat = ?)
                """, (f'Stampa News {news_id}', f'Stampa News {news_id}'))
                conn.commit()
                logger.info("✅ Stampa eseguita e registrata con successo")
            else:
                logger.warning("⚠️ PDF generato ma stampa fallita")
        else:
            if not printer_name:
                logger.warning("⚠️ Nessuna stampante configurata")
            if not os.path.exists(pdf_path):
                logger.error(f"⚠️ PDF non trovato: {pdf_path}")
        
        return jsonify({
            'success': True,
            'message': 'Richiesta processata',
            'printed': print_success,
            'pdf_generated': os.path.exists(pdf_path),
            'printer_available': printer_name is not None
        })
        
    except Exception as e:
        logger.error(f"Errore stampa news: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Crea directory temp se non esiste
    os.makedirs('temp', exist_ok=True)
    
    # Avvia servizio keep-alive stampante (ogni 5 minuti)
    logger.info("Avvio Printer Keep-Alive service...")
    start_printer_keepalive(interval_seconds=300)
    
    try:
        # Avvia server
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # Arresta keep-alive alla chiusura
        logger.info("Arresto Printer Keep-Alive service...")
        stop_printer_keepalive()
