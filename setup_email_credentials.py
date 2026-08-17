"""
setup_email_credentials.py
--------------------------
Script interattivo per configurare le credenziali SMTP del Kiosk HR.
Salva email e password cifrate in email_credentials.enc usando Fernet.

Esegui una volta sola al momento dell'installazione:
    python setup_email_credentials.py

I dati salvati vengono letti automaticamente da email_connector.py
ogni volta che viene inviata una email.
"""

import os
import sys
import getpass
from pathlib import Path

# Assicura che il working directory sia la root del progetto
BASE_DIR = Path(__file__).parent.resolve()
os.chdir(BASE_DIR)

sys.path.insert(0, str(BASE_DIR))

from cryptography.fernet import Fernet
from company_config import SMTP_SERVER, SMTP_PORT, EMAIL_FROM

KEY_FILE  = BASE_DIR / 'email_key.key'
CRED_FILE = BASE_DIR / 'email_credentials.enc'


def load_or_create_key() -> bytes:
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    print(f"[OK] Chiave di cifratura creata: {KEY_FILE}")
    return key


def save_credentials(email: str, password: str):
    key = load_or_create_key()
    token = Fernet(key).encrypt(f"{email}:{password}".encode())
    CRED_FILE.write_bytes(token)
    print(f"[OK] Credenziali salvate cifrate in: {CRED_FILE}")


def load_credentials() -> tuple[str, str]:
    if not CRED_FILE.exists():
        return None, None
    key = load_or_create_key()
    raw = Fernet(key).decrypt(CRED_FILE.read_bytes()).decode()
    email, _, password = raw.partition(":")
    return email, password


def test_smtp(email: str, password: str) -> bool:
    import smtplib
    print(f"\nTest connessione SMTP verso {SMTP_SERVER}:{SMTP_PORT}...")
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.ehlo()
        if password:
            server.starttls()
            server.ehlo()
            server.login(email, password)
            print("[OK] Login SMTP riuscito con autenticazione.")
        else:
            print("[OK] Connessione relay riuscita (senza autenticazione).")
        server.quit()
        return True
    except Exception as e:
        print(f"[ERRORE] Test SMTP fallito: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("  CONFIGURAZIONE CREDENZIALI EMAIL - KIOSK HR")
print("=" * 60)
print()
print(f"Server SMTP   : {SMTP_SERVER}:{SMTP_PORT}")
print(f"(modificabile in print_config.json → company.smtp_server)")
print()

# Mostra credenziali attuali se esistono
current_email, current_pwd = load_credentials()
if current_email:
    masked = ("*" * (len(current_pwd) - 2) + current_pwd[-2:]) if current_pwd else "(vuota)"
    print(f"Credenziali attuali → email: {current_email}  password: {masked}")
    print()
    risposta = input("Vuoi sovrascriverle? [s/N] ").strip().lower()
    if risposta not in ('s', 'si', 'y', 'yes'):
        print("\nNessuna modifica effettuata.")
        sys.exit(0)
    print()

# Email mittente
default_email = current_email or EMAIL_FROM
email_input = input(f"Email mittente [{default_email}]: ").strip()
email = email_input if email_input else default_email

# Password
print()
print("Inserisci la password SMTP.")
print("  → Se usi un relay interno senza autenticazione, lascia vuoto e premi Invio.")
print("  → La password NON viene mostrata mentre la scrivi.")
print()
password = getpass.getpass("Password SMTP: ")
password2 = getpass.getpass("Conferma password: ") if password else ""

if password and password != password2:
    print("\n[ERRORE] Le password non corrispondono. Riprova.")
    sys.exit(1)

# Salva
save_credentials(email, password)

# Test opzionale
print()
do_test = input("Vuoi testare la connessione SMTP adesso? [S/n] ").strip().lower()
if do_test not in ('n', 'no'):
    ok = test_smtp(email, password)
    if not ok:
        print("\n[ATTENZIONE] Il test ha fallito. Le credenziali sono state salvate")
        print("             ma verifica i parametri SMTP in print_config.json.")

print()
print("=" * 60)
print("  CONFIGURAZIONE COMPLETATA")
print("=" * 60)
print(f"  Email    : {email}")
print(f"  Password : {'(relay senza password)' if not password else '*** salvata cifrata ***'}")
print(f"  File     : {CRED_FILE}")
print()
print("Per modificare in futuro riesegui questo script.")
print()
