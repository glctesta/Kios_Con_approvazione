"""
Fix print-pdf endpoint to support both GET and POST
"""

import os

# Read current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the print_pdf_endpoint function (around line 861-894)
start_line = None
end_line = None

for i, line in enumerate(lines):
    if '@app.route(\'/api/print-pdf\', methods=[\'POST\'])' in line:
        start_line = i
    if start_line is not None and i > start_line and (line.strip().startswith('@app.route') or line.strip().startswith('if __name__')):
        end_line = i
        break

if start_line is None:
    print("ERROR: Could not find print-pdf endpoint")
    exit(1)

print(f"Found endpoint at lines {start_line+1} to {end_line}")

# New endpoint code
new_code = '''@app.route('/api/print-pdf', methods=['POST'])
@app.route('/api/print-pdf/<filename>', methods=['GET'])
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


'''

# Replace the function
new_lines = lines[:start_line] + [new_code] + lines[end_line:]

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ Endpoint updated successfully!")
print("✓ Now supports both GET and POST requests")
print("✓ Added detailed logging")
