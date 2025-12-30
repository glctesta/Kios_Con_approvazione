# Esempio di utilizzo

from email_connector import EmailSender

def test_email():
    try:
        sender = EmailSender("vandewiele-com.mail.protection.outlook.com",
                         25)
        # sender = EmailSender("smtp.office365.com", 587)
        # Prima volta: salva le credenziali (verranno criptate)
        sender.save_credentials("Accounting@Eutron.it",
                            "9jHgFhSs7Vf+"
                                )

        # Invia una email
        sender.send_email(
            to_email="gtesta@gmail.com",
            subject="Test Email",
            body="Questo è un test di invio email automatico",
            is_html=False
        )

    except Exception as error:
        print(f"Errore dettagliato:{str(error)}")

if __name__ == "__main__":
    test_email()