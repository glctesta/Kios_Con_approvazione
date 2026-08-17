"""
company_config.py
-----------------
Punto unico di verità per tutti i parametri aziendali configurabili.
Legge da print_config.json (sezione "company") e riexpone le costanti
usate in tutti i moduli del progetto.

Per modificare un parametro basta editare print_config.json —
nessun file Python deve essere toccato.
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'print_config.json')

_DEFAULTS = {
    "employer_id": 2,
    "smtp_server": "vandewiele-com.mail.protection.outlook.com",
    "smtp_port": 25,
    "email_from": "Accounting@Eutron.it",
    "fallback_email": "gianluca.testa@vandewiele.com",
    "report_recipients": [
        "Gianluca.Testa@Vandewiele.com",
        "Cornelia.Ormenisan@Vandewiele.com"
    ]
}


def _load() -> dict:
    """Legge la sezione 'company' da print_config.json."""
    try:
        with open(_CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cfg = data.get('company', {})
        if not cfg:
            logger.warning("Sezione 'company' assente in print_config.json — uso valori di default.")
        return {**_DEFAULTS, **cfg}
    except FileNotFoundError:
        logger.warning(f"{_CONFIG_FILE} non trovato — uso valori di default per company config.")
        return dict(_DEFAULTS)
    except Exception as e:
        logger.error(f"Errore lettura company config: {e} — uso valori di default.")
        return dict(_DEFAULTS)


# ── Carica una volta all'import ──────────────────────────────────────────────
_cfg = _load()

# ID numerico del datore di lavoro nella tabella Employee.dbo.Employeers
EMPLOYER_ID: int = int(_cfg['employer_id'])

# Email / SMTP
SMTP_SERVER: str   = str(_cfg['smtp_server'])
SMTP_PORT: int     = int(_cfg['smtp_port'])
EMAIL_FROM: str    = str(_cfg['email_from'])

# Email di fallback usata quando nessun manager è trovato
FALLBACK_EMAIL: str = str(_cfg['fallback_email'])

# Destinatari dei report mensili di utilizzo kiosk
REPORT_RECIPIENTS: list = list(_cfg['report_recipients'])


def reload():
    """Ricarica la configurazione da disco (utile per hot-reload senza riavviare il server)."""
    global _cfg, EMPLOYER_ID, SMTP_SERVER, SMTP_PORT, EMAIL_FROM, FALLBACK_EMAIL, REPORT_RECIPIENTS
    _cfg = _load()
    EMPLOYER_ID        = int(_cfg['employer_id'])
    SMTP_SERVER        = str(_cfg['smtp_server'])
    SMTP_PORT          = int(_cfg['smtp_port'])
    EMAIL_FROM         = str(_cfg['email_from'])
    FALLBACK_EMAIL     = str(_cfg['fallback_email'])
    REPORT_RECIPIENTS  = list(_cfg['report_recipients'])
    logger.info(f"company_config ricaricata: employer_id={EMPLOYER_ID}, smtp={SMTP_SERVER}")
