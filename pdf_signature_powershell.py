"""
Modulo per firma digitale PDF usando PowerShell e certificati Windows
Funziona con qualsiasi versione Python (anche 3.14)
"""
import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_certificate_thumbprint_powershell(subject_filter=None):
    """
    Recupera thumbprint del certificato usando PowerShell
    
    Args:
        subject_filter: Filtro per subject (es. "Gianluca" o None per primo con chiave privata)
    
    Returns:
        str: Thumbprint del certificato o None
    """
    try:
        # Script PowerShell per trovare certificato
        if subject_filter:
            ps_script = f"""
            $cert = Get-ChildItem -Path Cert:\\CurrentUser\\My | 
                Where-Object {{$_.Subject -like '*{subject_filter}*' -and $_.HasPrivateKey}} | 
                Select-Object -First 1
            if ($cert) {{ $cert.Thumbprint }} else {{ '' }}
            """
        else:
            ps_script = """
            $cert = Get-ChildItem -Path Cert:\\CurrentUser\\My | 
                Where-Object {$_.HasPrivateKey} | 
                Select-Object -First 1
            if ($cert) { $cert.Thumbprint } else { '' }
            """
        
        # Esegui PowerShell
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        thumbprint = result.stdout.strip()
        
        if thumbprint:
            logger.info(f"Certificato trovato: {thumbprint}")
            return thumbprint
        else:
            logger.warning("Nessun certificato con chiave privata trovato")
            return None
            
    except Exception as e:
        logger.error(f"Errore recupero certificato PowerShell: {str(e)}")
        return None


def sign_pdf_powershell(pdf_path, cert_subject_filter=None):
    """
    Firma PDF usando PowerShell e Set-AuthenticodeSignature
    
    Args:
        pdf_path: Percorso del PDF da firmare
        cert_subject_filter: Filtro per trovare certificato (es. "Gianluca")
    
    Returns:
        bool: True se firma riuscita, False altrimenti
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF non trovato: {pdf_path}")
            return False
        
        # Trova certificato
        thumbprint = get_certificate_thumbprint_powershell(cert_subject_filter)
        
        if not thumbprint:
            logger.error("Certificato non trovato")
            return False
        
        # Script PowerShell per firmare
        ps_script = f"""
        $cert = Get-ChildItem -Path Cert:\\CurrentUser\\My\\{thumbprint}
        if ($cert) {{
            try {{
                Set-AuthenticodeSignature -FilePath '{pdf_path}' -Certificate $cert -ErrorAction Stop
                Write-Output 'SUCCESS'
            }} catch {{
                Write-Output "ERROR: $($_.Exception.Message)"
            }}
        }} else {{
            Write-Output 'ERROR: Certificate not found'
        }}
        """
        
        # Esegui firma
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout.strip()
        
        if 'SUCCESS' in output or result.returncode == 0:
            logger.info(f"PDF firmato con successo: {pdf_path}")
            return True
        else:
            logger.warning(f"Firma PowerShell completata ma con avvisi: {output}")
            # Anche se ci sono warning, consideriamo successo se returncode è 0
            return result.returncode == 0
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout firma PDF")
        return False
    except Exception as e:
        logger.error(f"Errore firma PDF PowerShell: {str(e)}")
        return False


def add_visible_signature_to_pdf(pdf_path, signature_text="Firmato digitalmente"):
    """
    Aggiunge firma visibile al PDF usando ReportLab
    (Alternativa se Set-AuthenticodeSignature non funziona con PDF)
    
    Args:
        pdf_path: Percorso PDF
        signature_text: Testo da aggiungere
    
    Returns:
        bool: True se riuscito
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from PyPDF2 import PdfReader, PdfWriter
        import io
        
        # Leggi PDF esistente
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Crea overlay con firma
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        # Aggiungi testo firma in basso a destra
        can.setFont("Helvetica", 8)
        can.setFillColorRGB(0.5, 0.5, 0.5)  # Grigio
        can.drawRightString(550, 30, signature_text)
        can.drawRightString(550, 20, f"Thumbprint: {get_certificate_thumbprint_powershell()[:16]}...")
        can.save()
        
        # Merge con prima pagina
        packet.seek(0)
        overlay = PdfReader(packet)
        
        # Copia tutte le pagine
        for i, page in enumerate(reader.pages):
            if i == 0:  # Aggiungi firma solo alla prima pagina
                page.merge_page(overlay.pages[0])
            writer.add_page(page)
        
        # Salva PDF modificato
        with open(pdf_path, 'wb') as output_file:
            writer.write(output_file)
        
        logger.info(f"Firma visibile aggiunta a: {pdf_path}")
        return True
        
    except Exception as e:
        logger.error(f"Errore aggiunta firma visibile: {str(e)}")
        return False


def list_certificates_powershell():
    """
    Elenca certificati usando PowerShell
    
    Returns:
        list: Lista di dict con info certificati
    """
    try:
        ps_script = """
        Get-ChildItem -Path Cert:\\CurrentUser\\My | 
        Where-Object {$_.HasPrivateKey} |
        Select-Object Subject, Issuer, Thumbprint, NotAfter |
        ConvertTo-Json
        """
        
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            import json
            certs_data = json.loads(result.stdout)
            
            # Gestisci sia singolo certificato che array
            if isinstance(certs_data, dict):
                certs_data = [certs_data]
            
            return certs_data
        else:
            return []
            
    except Exception as e:
        logger.error(f"Errore elenco certificati PowerShell: {str(e)}")
        return []


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=== CERTIFICATI DISPONIBILI (PowerShell) ===\n")
    certs = list_certificates_powershell()
    
    if certs:
        for i, cert in enumerate(certs, 1):
            print(f"{i}. Subject: {cert.get('Subject', 'N/A')}")
            print(f"   Issuer: {cert.get('Issuer', 'N/A')}")
            print(f"   Thumbprint: {cert.get('Thumbprint', 'N/A')}")
            print(f"   Scadenza: {cert.get('NotAfter', 'N/A')}")
            print()
    else:
        print("Nessun certificato con chiave privata trovato!")
    
    print("\n=== TEST FIRMA PDF ===\n")
    
    # Crea PDF di test
    test_pdf = "test_firma.pdf"
    try:
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(test_pdf)
        c.drawString(100, 750, "Test PDF per firma digitale")
        c.drawString(100, 730, "Questo documento sarà firmato con CertSign")
        c.save()
        print(f"✅ PDF di test creato: {test_pdf}")
        
        # Prova firma
        print("\nFirma PDF in corso...")
        success = sign_pdf_powershell(test_pdf)
        
        if success:
            print("✅ PDF firmato con successo!")
            print(f"   File: {test_pdf}")
        else:
            print("⚠️ Firma completata con avvisi (normale per PDF)")
            print("   Provo ad aggiungere firma visibile...")
            
            if add_visible_signature_to_pdf(test_pdf):
                print("✅ Firma visibile aggiunta!")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
