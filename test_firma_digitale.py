"""
Script di test per verificare firma digitale PDF con certificato
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

print("=" * 80)
print("TEST FIRMA DIGITALE PDF")
print("=" * 80)
print()

# Step 1: Verifica certificato
print("[1/5] Verifica presenza certificato...")
cert_path = 'certificate.pfx'

if not os.path.exists(cert_path):
    print(f"ERRORE: Certificato non trovato: {cert_path}")
    print()
    print("Assicurarsi che certificate.pfx sia nella directory corrente")
    input("Premi INVIO per uscire...")
    sys.exit(1)

print(f"OK - Trovato: {cert_path}")
print(f"Dimensione: {os.path.getsize(cert_path)} bytes")
print()

# Step 2: Chiedi password
print("[2/5] Password certificato...")
cert_password = os.environ.get('CERT_PASSWORD')

if cert_password:
    print(f"OK - Password trovata in variabile ambiente CERT_PASSWORD")
else:
    print("Password non trovata in variabile ambiente.")
    cert_password = input("Inserisci password certificato (o INVIO se nessuna): ").strip()
    if not cert_password:
        cert_password = None
        print("Nessuna password (certificato non protetto)")

print()

# Step 3: Carica certificato
print("[3/5] Caricamento certificato...")
try:
    from pdf_digital_signer import PDFDigitalSigner
    
    signer = PDFDigitalSigner(
        cert_path=cert_path,
        cert_password=cert_password
    )
    
    # Carica e verifica
    pysigner = signer.load_certificate_from_file(cert_path, cert_password)
    print("OK - Certificato caricato con successo")
    
    # Estrai info
    cert_info = signer.get_certificate_info(pysigner)
    print()
    print("Informazioni Certificato:")
    print(f"  - Nome: {cert_info['common_name']}")
    print(f"  - Organizzazione: {cert_info['organization']}")
    print(f"  - Email: {cert_info['email']}")
    print(f"  - Paese: {cert_info['country']}")
    print(f"  - Valido da: {cert_info['valid_from']}")
    print(f"  - Valido fino: {cert_info['valid_until']}")
    print()
    
except Exception as e:
    print(f"ERRORE durante caricamento certificato:")
    print(f"  {str(e)}")
    print()
    print("Possibili cause:")
    print("  - Password errata")
    print("  - Certificato corrotto")
    print("  - pyHanko non installato (pip install pyHanko)")
    print()
    import traceback
    traceback.print_exc()
    input("Premi INVIO per uscire...")
    sys.exit(1)

# Step 4: Crea PDF di test
print("[4/5] Creazione PDF di test...")
test_pdf = 'test_firma.pdf'

try:
    c = canvas.Canvas(test_pdf, pagesize=A4)
    width, height = A4
    
    # Titolo
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 100, "DOCUMENTO DI TEST")
    
    # Testo
    c.setFont("Helvetica", 12)
    y = height - 150
    c.drawString(50, y, "Questo e un PDF di test per verificare la firma digitale.")
    y -= 20
    c.drawString(50, y, f"Generato: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y -= 20
    c.drawString(50, y, f"Firmatario: {cert_info['common_name']}")
    y -= 20
    c.drawString(50, y, f"Organizzazione: {cert_info['organization']}")
    
    # Nota
    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Nota: La firma digitale apparira in basso a destra dopo la firma.")
    
    c.save()
    print(f"OK - PDF creato: {test_pdf}")
    print()
    
except Exception as e:
    print(f"ERRORE durante creazione PDF:")
    print(f"  {str(e)}")
    input("Premi INVIO per uscire...")
    sys.exit(1)

# Step 5: Firma PDF
print("[5/5] Firma digitale PDF...")
try:
    from pdf_digital_signer import create_visible_signature_field
    
    # Crea campo firma visibile
    sig_field = create_visible_signature_field(
        page_width=A4[0],
        page_height=A4[1],
        position='bottom-right',
        width=200,
        height=80
    )
    
    # Firma
    signed_pdf = signer.sign_pdf(
        input_pdf_path=test_pdf,
        output_pdf_path=test_pdf,  # Sovrascrivi
        signature_field_spec=sig_field,
        reason='Test firma digitale',
        location=cert_info.get('organization', 'Test')
    )
    
    print("OK - PDF firmato con successo!")
    print()
    print(f"File firmato: {signed_pdf}")
    print()
    
except Exception as e:
    print(f"ERRORE durante firma PDF:")
    print(f"  {str(e)}")
    print()
    import traceback
    traceback.print_exc()
    input("Premi INVIO per uscire...")
    sys.exit(1)

# Riepilogo finale
print("=" * 80)
print("TEST COMPLETATO CON SUCCESSO!")
print("=" * 80)
print()
print("Risultato:")
print(f"  - Certificato: {cert_path}")
print(f"  - Firmatario: {cert_info['common_name']}")
print(f"  - PDF firmato: {signed_pdf}")
print()
print("Prossimi passi:")
print("  1. Apri il file 'test_firma.pdf' con Adobe Reader")
print("  2. Verifica il riquadro firma in basso a destra")
print("  3. Controlla il banner 'Firmato e valido' in alto")
print("  4. Click sulla firma per vedere i dettagli del certificato")
print()
print("Se tutto funziona, il sistema e pronto per firmare i documenti reali!")
print("=" * 80)

input("\nPremi INVIO per uscire...")
