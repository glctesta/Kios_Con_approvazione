"""
Test certificato Windows Certificate Store
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 80)
print("TEST CERTIFICATO WINDOWS CERTIFICATE STORE")
print("=" * 80)
print()

try:
    from windows_cert_signer import WindowsCertificateSigner
    
    print("[1/2] Ricerca certificato in Windows Store...")
    signer = WindowsCertificateSigner()
    
    cert = signer.find_certificate_with_private_key()
    
    if cert:
        print()
        print("=" * 80)
        print("CERTIFICATO TROVATO!")
        print("=" * 80)
        print()
        print(f"Subject: {signer.cert_info['subject']}")
        print(f"Issuer: {signer.cert_info['issuer']}")
        print(f"Thumbprint: {signer.cert_thumbprint}")
        print(f"Valido da: {signer.cert_info['valid_from']}")
        print(f"Valido fino: {signer.cert_info['valid_until']}")
        print()
        print("=" * 80)
        
        # Test firma
        print()
        print("[2/2] Test firma PDF...")
        
        # Crea PDF di test
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        test_pdf = 'test_windows_cert.pdf'
        c = canvas.Canvas(test_pdf, pagesize=A4)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(A4[0]/2, A4[1] - 100, "TEST FIRMA WINDOWS CERTIFICATE")
        c.setFont("Helvetica", 12)
        c.drawString(50, A4[1] - 150, f"Certificato: {signer.cert_info['subject']}")
        c.save()
        
        print(f"PDF creato: {test_pdf}")
        
        # Firma
        signed = signer.sign_pdf(test_pdf)
        
        if signed:
            print(f"PDF firmato: {signed}")
            print()
            print("=" * 80)
            print("TEST COMPLETATO CON SUCCESSO!")
            print("=" * 80)
            print()
            print("Prossimi passi:")
            print("  1. Apri test_windows_cert.pdf")
            print("  2. Verifica il timbro firma in basso a destra")
            print("  3. Il sistema e pronto per firmare documenti reali!")
            print()
        else:
            print("Firma fallita")
        
    else:
        print()
        print("=" * 80)
        print("NESSUN CERTIFICATO TROVATO")
        print("=" * 80)
        print()
        print("Verificare:")
        print("  1. Certificato installato in Windows (certmgr.msc)")
        print("  2. Certificato ha chiave privata")
        print("  3. Certificato in Personal/My store")
        print()
    
except Exception as e:
    print()
    print("ERRORE:")
    print(str(e))
    print()
    import traceback
    traceback.print_exc()

print()
input("Premi INVIO per uscire...")
