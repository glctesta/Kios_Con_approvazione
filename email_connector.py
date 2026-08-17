import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
import os
import ssl
from company_config import SMTP_SERVER as _DEFAULT_SMTP_SERVER, SMTP_PORT as _DEFAULT_SMTP_PORT


class EmailSender:
    def __init__(self, smtp_server=None, smtp_port=None):
        """
        Inizializza il sender email con server e porta SMTP

        Args:
            smtp_server (str): Server SMTP
            smtp_port (int): Porta SMTP (default: 25 per relay server)
        """
        self.smtp_server = smtp_server or _DEFAULT_SMTP_SERVER
        self.smtp_port   = smtp_port   or _DEFAULT_SMTP_PORT
        self.key = None
        self.encrypted_password = None
        self._key_file = "email_key.key"
        self._credentials_file = "email_credentials.enc"

    def setup_encryption(self):
        if os.path.exists(self._key_file):
            with open(self._key_file, "rb") as key_file:
                self.key = key_file.read()
        else:
            self.key = Fernet.generate_key()
            with open(self._key_file, "wb") as key_file:
                key_file.write(self.key)

    def save_credentials(self, email, password=""):
        """
        Salva solo l'indirizzo email (password non necessaria per relay server)

        Args:
            email (str): Indirizzo email mittente
            password (str): Non utilizzato per relay server
        """
        if not self.key:
            self.setup_encryption()

        f = Fernet(self.key)
        credentials = f"{email}:{password}".encode()
        encrypted_credentials = f.encrypt(credentials)

        with open(self._credentials_file, "wb") as cred_file:
            cred_file.write(encrypted_credentials)

    def load_credentials(self) -> tuple:
        """Carica email e password dal file cifrato.

        Returns:
            (email, password) — password e' stringa vuota se non impostata
        """
        if not os.path.exists(self._credentials_file):
            raise FileNotFoundError("Credenziali non trovate. Esegui CONFIGURA_EMAIL.bat")

        if not self.key:
            self.setup_encryption()

        f = Fernet(self.key)
        with open(self._credentials_file, "rb") as cred_file:
            encrypted_credentials = cred_file.read()

        decrypted = f.decrypt(encrypted_credentials).decode()
        email, _, password = decrypted.partition(":")
        return email, password

    def send_email(self, to_email, subject, body, is_html=False):
        """
        Invia una email via SMTP.
        Se la password e' salvata usa autenticazione TLS,
        altrimenti si connette come relay interno senza auth.

        Args:
            to_email (str): Destinatario (o piu' destinatari separati da virgola)
            subject (str): Oggetto
            body (str): Corpo (testo o HTML)
            is_html (bool): True se body e' HTML
        """
        from_email, password = self.load_credentials()

        msg = MIMEMultipart()
        msg['From']    = from_email
        msg['To']      = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

        try:
            print(f"Connessione a {self.smtp_server}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15)
            server.ehlo()

            if password:
                # SMTP autenticato con STARTTLS
                server.starttls()
                server.ehlo()
                server.login(from_email, password)
                print("Autenticazione SMTP riuscita.")
            else:
                # Relay interno senza autenticazione
                print("Relay SMTP senza autenticazione.")

            server.send_message(msg)
            print("Email inviata con successo!")
            server.quit()
            return True

        except Exception as e:
            print(f"Errore nell'invio dell'email: {e}")
            raise

