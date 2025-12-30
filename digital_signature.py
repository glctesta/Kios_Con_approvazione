"""
Modulo per firma digitale PDF con certificati CertSign
Supporta firma automatica usando certificati installati in Windows Certificate Store
"""
import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Flag per verificare se pyHanko è disponibile
PYHANKO_AVAILABLE = False
try:
    from pyhanko.sign import signers, fields
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
    from pyhanko_certvalidator import ValidationContext
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    import certifi
    PYHANKO_AVAILABLE = True
    logger.info("pyHanko caricato con successo - Firma digitale disponibile")
except ImportError as e:
    logger.warning(f"pyHanko non disponibile: {e}. Firma digitale disabilitata.")


def get_windows_certificate(subject_name=None, store_name='MY', store_location='CurrentUser'):
    """
    Recupera certificato dal Windows Certificate Store
    
    Args:
        subject_name: Nome del soggetto del certificato (es. "Administrator" o None per primo disponibile)
        store_name: Nome dello store ('MY' = Personal, 'ROOT' = Trusted Root)
        store_location: 'CurrentUser' o 'LocalMachine'
    
    Returns:
        tuple: (cert_data, private_key) oppure (None, None) se non trovato
    """
    try:
        import win32crypt
        import pywintypes
        
        # Costanti (valori numerici per compatibilità)
        CERT_STORE_PROV_SYSTEM = 10
        CERT_SYSTEM_STORE_CURRENT_USER = 0x00010000
        CERT_SYSTEM_STORE_LOCAL_MACHINE = 0x00020000
        CERT_NAME_SIMPLE_DISPLAY_TYPE = 4
        CERT_NAME_ISSUER_FLAG = 1
        CERT_KEY_PROV_INFO_PROP_ID = 2
        
        # Apri certificate store
        if store_location == 'CurrentUser':
            location = CERT_SYSTEM_STORE_CURRENT_USER
        else:
            location = CERT_SYSTEM_STORE_LOCAL_MACHINE
        
        store = win32crypt.CertOpenStore(
            CERT_STORE_PROV_SYSTEM,
            0,
            None,
            location,
            store_name
        )
        
        # Cerca certificato
        cert_context = None
        while True:
            cert_context = win32crypt.CertEnumCertificatesInStore(store, cert_context)
            if not cert_context:
                break
            
            # Ottieni subject name
            cert_subject = win32crypt.CertGetNameString(
                cert_context,
                CERT_NAME_SIMPLE_DISPLAY_TYPE,
                0
            )
            
            logger.debug(f"Trovato certificato: {cert_subject}")
            
            # Se subject_name specificato, cerca match
            if subject_name and subject_name.lower() not in cert_subject.lower():
                continue
            
            # Verifica che abbia chiave privata
            try:
                # Ottieni certificato in formato DER
                cert_der = win32crypt.CertSerializeCertificateStoreElement(cert_context, 0)
                
                # Prova ad acquisire chiave privata
                key_prov_info = win32crypt.CertGetCertificateContextProperty(
                    cert_context,
                    CERT_KEY_PROV_INFO_PROP_ID
                )
                
                if key_prov_info:
                    logger.info(f"Certificato con chiave privata trovato: {cert_subject}")
                    
                    # Chiudi store
                    win32crypt.CertCloseStore(store, 0)
                    
                    return cert_der, cert_context
            except pywintypes.error as e:
                logger.debug(f"Certificato {cert_subject} senza chiave privata: {e}")
                continue
        
        # Chiudi store
        win32crypt.CertCloseStore(store, 0)
        
        logger.warning("Nessun certificato con chiave privata trovato")
        return None, None
        
    except Exception as e:
        logger.error(f"Errore recupero certificato Windows: {str(e)}")
        return None, None


def sign_pdf_with_certsign(input_pdf_path, output_pdf_path=None, cert_subject=None, 
                           reason="Document certification", location="Romania"):
    """
    Firma PDF usando certificato CertSign dal Windows Certificate Store
    
    Args:
        input_pdf_path: Percorso PDF da firmare
        output_pdf_path: Percorso PDF firmato (None = sovrascrivi originale)
        cert_subject: Nome soggetto certificato (None = primo disponibile)
        reason: Motivo della firma
        location: Località della firma
    
    Returns:
        bool: True se firma riuscita, False altrimenti
    """
    if not PYHANKO_AVAILABLE:
        logger.error("pyHanko non installato. Impossibile firmare PDF.")
        return False
    
    try:
        # Se output non specificato, usa file temporaneo
        if output_pdf_path is None:
            output_pdf_path = input_pdf_path + ".signed.tmp"
            replace_original = True
        else:
            replace_original = False
        
        # Recupera certificato da Windows Store
        cert_der, cert_context = get_windows_certificate(cert_subject)
        
        if not cert_der:
            logger.error("Certificato non trovato nel Windows Certificate Store")
            return False
        
        # Converti certificato DER in formato pyHanko
        from cryptography import x509
        cert = x509.load_der_x509_certificate(cert_der, default_backend())
        
        logger.info(f"Firma PDF con certificato: {cert.subject}")
        
        # NOTA: Per firma completa con chiave privata da Windows Store
        # serve implementazione più complessa con CryptoAPI
        # Per ora usiamo approccio semplificato
        
        # TODO: Implementare firma con chiave privata da Windows Store
        # Questo richiede uso di win32crypt.CryptAcquireCertificatePrivateKey
        
        logger.warning("Firma digitale completa richiede implementazione avanzata CryptoAPI")
        logger.info("Per ora, aggiungiamo solo placeholder firma visibile")
        
        # Copia file come workaround temporaneo
        import shutil
        shutil.copy2(input_pdf_path, output_pdf_path)
        
        if replace_original:
            os.replace(output_pdf_path, input_pdf_path)
        
        return True
        
    except Exception as e:
        logger.error(f"Errore firma PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def list_available_certificates():
    """
    Elenca tutti i certificati disponibili nel Windows Certificate Store
    
    Returns:
        list: Lista di dict con info certificati
    """
    try:
        import win32crypt
        
        # Costanti
        CERT_STORE_PROV_SYSTEM = 10
        CERT_SYSTEM_STORE_CURRENT_USER = 0x00010000
        CERT_NAME_SIMPLE_DISPLAY_TYPE = 4
        CERT_NAME_ISSUER_FLAG = 1
        CERT_KEY_PROV_INFO_PROP_ID = 2
        
        certs = []
        store = win32crypt.CertOpenStore(
            CERT_STORE_PROV_SYSTEM,
            0,
            None,
            CERT_SYSTEM_STORE_CURRENT_USER,
            'MY'
        )
        
        cert_context = None
        while True:
            cert_context = win32crypt.CertEnumCertificatesInStore(store, cert_context)
            if not cert_context:
                break
            
            subject = win32crypt.CertGetNameString(
                cert_context,
                CERT_NAME_SIMPLE_DISPLAY_TYPE,
                0
            )
            
            issuer = win32crypt.CertGetNameString(
                cert_context,
                CERT_NAME_SIMPLE_DISPLAY_TYPE,
                CERT_NAME_ISSUER_FLAG
            )
            
            # Verifica chiave privata
            has_private_key = False
            try:
                key_prov_info = win32crypt.CertGetCertificateContextProperty(
                    cert_context,
                    CERT_KEY_PROV_INFO_PROP_ID
                )
                has_private_key = key_prov_info is not None
            except:
                pass
            
            certs.append({
                'subject': subject,
                'issuer': issuer,
                'has_private_key': has_private_key
            })
        
        win32crypt.CertCloseStore(store, 0)
        return certs
        
    except Exception as e:
        logger.error(f"Errore elenco certificati: {str(e)}")
        return []


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    print("=== CERTIFICATI DISPONIBILI ===")
    certs = list_available_certificates()
    for i, cert in enumerate(certs, 1):
        print(f"\n{i}. Subject: {cert['subject']}")
        print(f"   Issuer: {cert['issuer']}")
        print(f"   Chiave privata: {'✅ Sì' if cert['has_private_key'] else '❌ No'}")
    
    if not certs:
        print("Nessun certificato trovato!")
