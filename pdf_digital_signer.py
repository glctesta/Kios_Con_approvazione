"""
Modulo per firma digitale PDF con certificati
Supporta certificati Windows, PKCS#12 (.p12/.pfx), e PEM
"""
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Import condizionale di pyHanko (potrebbe non essere installato)
try:
    from pyhanko.sign import signers, fields
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
    from pyhanko.sign.fields import SigFieldSpec
    from pyhanko.sign.validation import validate_pdf_signature
    PYHANKO_AVAILABLE = True
except ImportError:
    PYHANKO_AVAILABLE = False
    logger.warning("pyHanko non installato - firma digitale PDF non disponibile")


class PDFDigitalSigner:
    """Gestisce la firma digitale di documenti PDF"""
    
    def __init__(self, cert_path=None, cert_password=None):
        """
        Inizializza il modulo di firma
        
        Args:
            cert_path: Percorso al file certificato (.pfx, .p12, .pem)
            cert_password: Password del certificato (se richiesta)
        """
        self.cert_path = cert_path
        self.cert_password = cert_password
        
        if not PYHANKO_AVAILABLE:
            logger.warning("pyHanko non disponibile - installare con: pip install pyHanko")
    
    def find_windows_certificate(self):
        """
        Cerca un certificato nel Windows Certificate Store
        
        Returns:
            Signer object se trovato, None altrimenti
        """
        if not PYHANKO_AVAILABLE:
            return None
        
        try:
            from pyhanko_certvalidator import ValidationContext
            from pyhanko.sign import signers
            
            # Cerca certificato con chiave privata in Windows Store
            # Questo richiede pyhanko_certvalidator per Windows
            logger.info("Cerco certificato in Windows Certificate Store...")
            
            # TODO: Implementare ricerca nel Windows Store
            # Per ora usiamo solo file certificati
            logger.warning("Ricerca Windows Store non ancora implementata")
            return None
            
        except Exception as e:
            logger.debug(f"Errore ricerca certificato Windows: {e}")
            return None
    
    def load_certificate_from_file(self, cert_path, password=None):
        """
        Carica certificato da file (.pfx, .p12, .pem)
        
        Args:
            cert_path: Percorso file certificato
            password: Password (bytes o str)
        
        Returns:
            Signer object
        """
        if not PYHANKO_AVAILABLE:
            raise ImportError("pyHanko non installato")
        
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Certificato non trovato: {cert_path}")
        
        # Converti password in bytes se necessario
        if password and isinstance(password, str):
            password = password.encode('utf-8')
        
        try:
            # Carica certificato PKCS#12 (.pfx/.p12)
            if cert_path.lower().endswith(('.pfx', '.p12')):
                signer = signers.SimpleSigner.load_pkcs12(
                    pfx_file=cert_path,
                    passphrase=password
                )
                logger.info(f"Certificato PKCS#12 caricato: {cert_path}")
                return signer
            
            # Carica certificato PEM
            elif cert_path.lower().endswith('.pem'):
                signer = signers.SimpleSigner.load(
                    key_file=cert_path,
                    cert_file=cert_path,
                    key_passphrase=password
                )
                logger.info(f"Certificato PEM caricato: {cert_path}")
                return signer
            
            else:
                raise ValueError(f"Formato certificato non supportato: {cert_path}")
                
        except Exception as e:
            logger.error(f"Errore caricamento certificato: {e}")
            raise
    
    def get_certificate_info(self, signer):
        """
        Estrae informazioni dal certificato
        
        Args:
            signer: Oggetto SimpleSigner
        
        Returns:
            dict con nome, organizzazione, email, etc.
        """
        try:
            cert = signer.signing_cert
            subject = cert.subject
            
            # Estrai campi common name, organization, etc.
            info = {
                'common_name': None,
                'organization': None,
                'organizational_unit': None,
                'email': None,
                'country': None,
                'valid_from': cert.not_valid_before,
                'valid_until': cert.not_valid_after
            }
            
            # Parsea subject per estrarre i campi
            for attr in subject:
                oid = attr.oid
                value = attr.value
                
                # Common Name (CN)
                if oid.dotted_string == '2.5.4.3':
                    info['common_name'] = value
                # Organization (O)
                elif oid.dotted_string == '2.5.4.10':
                    info['organization'] = value
                # Organizational Unit (OU)
                elif oid.dotted_string == '2.5.4.11':
                    info['organizational_unit'] = value
                # Country (C)
                elif oid.dotted_string == '2.5.4.6':
                    info['country'] = value
                # Email
                elif oid.dotted_string == '1.2.840.113549.1.9.1':
                    info['email'] = value
            
            logger.info(f"Info certificato: {info['common_name']} - {info['organization']}")
            return info
            
        except Exception as e:
            logger.warning(f"Errore estrazione info certificato: {e}")
            return {
                'common_name': 'Utente Sconosciuto',
                'organization': None,
                'organizational_unit': None,
                'email': None,
                'country': None,
                'valid_from': None,
                'valid_until': None
            }
    
    def sign_pdf(self, input_pdf_path, output_pdf_path=None, 
                 signature_field_spec=None, reason=None, location=None):
        """
        Firma digitalmente un PDF
        
        Args:
            input_pdf_path: Percorso PDF da firmare
            output_pdf_path: Percorso PDF firmato (default: sovrascrivi input)
            signature_field_spec: Specifica del campo firma visibile (SigFieldSpec)
            reason: Motivo della firma
            location: Luogo della firma
        
        Returns:
            str: Percorso PDF firmato
        """
        if not PYHANKO_AVAILABLE:
            logger.warning("pyHanko non disponibile - PDF non firmato")
            return input_pdf_path
        
        if not os.path.exists(input_pdf_path):
            raise FileNotFoundError(f"PDF non trovato: {input_pdf_path}")
        
        # Output path
        if output_pdf_path is None:
            output_pdf_path = input_pdf_path
        
        try:
            # Carica certificato
            if self.cert_path:
                signer = self.load_certificate_from_file(self.cert_path, self.cert_password)
            else:
                # Prova Windows Store
                signer = self.find_windows_certificate()
                if signer is None:
                    logger.warning("Nessun certificato configurato - PDF non firmato")
                    return input_pdf_path
            
            # Estrai info certificato per firma visibile
            cert_info = self.get_certificate_info(signer)
            
            # Apri PDF per firma
            with open(input_pdf_path, 'rb') as pdf_file:
                writer = IncrementalPdfFileWriter(pdf_file)
                
                # Crea campo firma se specificato
                if signature_field_spec is None:
                    # Campo firma di default (invisibile)
                    signature_field_spec = SigFieldSpec(
                        sig_field_name='Signature1',
                        box=None  # Invisibile
                    )
                
                # Metadati firma
                signature_meta = signers.PdfSignatureMetadata(
                    field_name=signature_field_spec.sig_field_name,
                    reason=reason or 'Firma documento ufficiale',
                    location=location or cert_info.get('organization', 'Unknown'),
                    name=cert_info.get('common_name', 'Unknown')
                )
                
                # Firma il PDF
                out = signers.sign_pdf(
                    writer,
                    signature_meta=signature_meta,
                    signer=signer,
                    existing_fields_only=False
                )
                
                # Salva PDF firmato
                if output_pdf_path == input_pdf_path:
                    # Sovrascrivi file originale
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        tmp.write(out.getvalue())
                        tmp_path = tmp.name
                    
                    os.replace(tmp_path, input_pdf_path)
                    logger.info(f"PDF firmato (sovrascritto): {input_pdf_path}")
                else:
                    # Salva in nuovo file
                    with open(output_pdf_path, 'wb') as f:
                        f.write(out.getvalue())
                    logger.info(f"PDF firmato salvato: {output_pdf_path}")
                
                return output_pdf_path
                
        except Exception as e:
            logger.error(f"Errore firma PDF: {e}")
            logger.exception(e)
            # Non blocchiamo - restituiamo PDF non firmato
            return input_pdf_path
    
    def verify_signature(self, pdf_path):
        """
        Verifica la firma digitale di un PDF
        
        Args:
            pdf_path: Percorso PDF da verificare
        
        Returns:
            dict con informazioni sulla verifica
        """
        if not PYHANKO_AVAILABLE:
            return {'valid': None, 'message': 'pyHanko non disponibile'}
        
        try:
            with open(pdf_path, 'rb') as pdf_file:
                # Valida prima firma trovata
                result = validate_pdf_signature(pdf_file)
                
                return {
                    'valid': result.bottom_line,
                    'signer': result.signer_reported_name,
                    'timestamp': result.timestamp,
                    'message': 'Firma valida' if result.bottom_line else 'Firma non valida'
                }
                
        except Exception as e:
            logger.error(f"Errore verifica firma: {e}")
            return {'valid': False, 'message': str(e)}


def create_visible_signature_field(page_width, page_height, 
                                   position='bottom-right', width=200, height=80):
    """
    Crea una specifica per campo firma visibile
    
    Args:
        page_width: Larghezza pagina PDF
        page_height: Altezza pagina PDF
        position: Posizione ('bottom-right', 'bottom-left', 'top-right', 'top-left')
        width: Larghezza riquadro firma
        height: Altezza riquadro firma
    
    Returns:
        SigFieldSpec per firma visibile
    """
    if not PYHANKO_AVAILABLE:
        return None
    
    margin = 50
    
    # Calcola coordinate in base alla posizione
    if position == 'bottom-right':
        x = page_width - width - margin
        y = margin
    elif position == 'bottom-left':
        x = margin
        y = margin
    elif position == 'top-right':
        x = page_width - width - margin
        y = page_height - height - margin
    elif position == 'top-left':
        x = margin
        y = page_height - height - margin
    else:
        # Default bottom-right
        x = page_width - width - margin
        y = margin
    
    return SigFieldSpec(
        sig_field_name='Signature1',
        box=(x, y, x + width, y + height)
    )
