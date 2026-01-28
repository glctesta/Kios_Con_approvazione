# Analisi: Invio Email Notifica Richiesta Assenza

## Flusso Completo

### 1. **Recupero Indirizzi Email dei Manager**
**File**: `absence_request.py` (linea 562)

```python
def get_manager_emails(self, employee_hire_history_id):
    """Recupera email manager tramite stored procedure GetManager"""
    try:
        cursor = self.conn.cursor()
        
        # Crea e popola la table variable
        query = """
        DECLARE @Ids dbo.EmployeeIdTableType;
        
        INSERT INTO @Ids VALUES (?);
        
        -- Esegui la SP
        EXEC GetManager @Ids;
        """
        
        cursor.execute(query, (employee_hire_history_id,))
        rows = cursor.fetchall()
        
        logger.debug(f"Dati grezzi ritornati dalla SP GetManager: {rows}")
        
        emails = []
        for row in rows:
            # Itera su tutti i campi della riga per estrarre tutte le email
            for field in row:
                # Verifica che il campo non sia NULL
                if field is not None:
                    # Converte in stringa se necessario
                    field_str = field.strip() if isinstance(field, str) else str(field).strip()
                    
                    # Se il campo contiene più email separate da virgola o semicolon, divide
                    if field_str:
                        # Prova a dividere per virgola o semicolon
                        if ',' in field_str or ';' in field_str:
                            # Divide per virgola o semicolon
                            separators = [',', ';']
                            email_list = [field_str]
                            for sep in separators:
                                new_list = []
                                for item in email_list:
                                    if sep in item:
                                        new_list.extend(item.split(sep))
                                    else:
                                        new_list.append(item)
                                email_list = new_list
                            
                            # Processa ogni email estratta
                            for email_item in email_list:
                                email = email_item.strip()
                                # Valida che sia un'email (contiene @) e non vuota
                                if email and '@' in email:
                                    # Evita duplicati nella lista
                                    if email not in emails:
                                        emails.append(email)
                                        logger.debug(f"Email estratta (da separatori): {email}")
                        else:
                            # Email singola
                            # Valida che sia un'email (contiene @) e non vuota
                            if field_str and '@' in field_str:
                                # Evita duplicati nella lista
                                if field_str not in emails:
                                    emails.append(field_str)
                                    logger.debug(f"Email estratta (singola): {field_str}")
        
        logger.info(f"Email manager trovate: {emails}")
        if not emails:
            logger.warning(f"Nessuna email trovata per hire_history_id {employee_hire_history_id}")
        
        return emails
        
    except Exception as e:
        logger.error(f"Errore recupero email manager: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # In caso di errore, restituisci lista vuota invece di bloccare
        return []
```

**Cosa fa:**
- Chiama la **Stored Procedure `GetManager`** passando `employee_hire_history_id`
- Usa una **table variable di tipo `EmployeeIdTableType`**
- Itera sui risultati e estrae tutte le email dai campi non-NULL
- Valida che siano email vere (contengono `@`)
- Evita duplicati
- **Ritorna**: Lista di indirizzi email dei manager

---

### 2. **Invio Email nei Manager**
**File**: `app.py` (linea 861-930)

```python
# Invia email notifica ai manager
try:
    logger.info("Recupero email manager...")
    manager_emails = request_manager.get_manager_emails(hire_history_id)
    
    # Se non ci sono manager, usa email fallback
    if not manager_emails:
        logger.warning(f"Nessun manager trovato per hire_history_id {hire_history_id}, uso email fallback")
        manager_emails = ['gianluca.testa@vandewiele.com']
    
    logger.info(f"Invio email a: {manager_emails}")
    
    # Prepara email HTML
    subject = f"Nouă cerere de absență - {registry_info['doc_name']}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #667eea;">Nouă Cerere de Absență</h2>
        
        <p>S-a înregistrat o nouă cerere de absență care necesită aprobare:</p>
        
        <table style="border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 8px; font-weight: bold;">Număr cerere:</td>
                <td style="padding: 8px;">{registry_info['doc_name']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Data cerere:</td>
                <td style="padding: 8px;">{registry_info['doc_date'].strftime('%d.%m.%Y')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Angajat:</td>
                <td style="padding: 8px;">{employee_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Tip absență:</td>
                <td style="padding: 8px;">{request_type_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Perioada:</td>
                <td style="padding: 8px;">{date_start.strftime('%d.%m.%Y')} - {date_end.strftime('%d.%m.%Y')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Zile lucrătoare:</td>
                <td style="padding: 8px;">{working_days if working_days else '-'}</td>
            </tr>
        </table>
        
        <p style="color: #f59e0b; font-weight: bold;">⚠️ Questa richiesta è in attesa di approvazione.</p>
        
        <p>Vii prego di verificare e approvare/rifiutare la richiesta nel sistema di gestione.</p>
    </body>
    </html>
    """
    
    # Invia email usando utils.send_email
    send_email(
        recipients=manager_emails,
        subject=subject,
        body=body,
        is_html=True
    )
    
    logger.info("Email notifica inviata con successo")
        
except Exception as email_error:
    # Non bloccare la richiesta se l'email fallisce
    logger.error(f"Errore invio email notifica: {str(email_error)}")
    import traceback
    logger.error(traceback.format_exc())
```

**Cosa fa:**
- Chiama `get_manager_emails()` per recuperare gli indirizzi
- **Se nessun manager trovato**: usa email fallback `gianluca.testa@vandewiele.com`
- Prepara email HTML con i dettagli della richiesta:
  - Numero richiesta
  - Data richiesta
  - Nome dipendente
  - Tipo di assenza
  - Periodo (data inizio - data fine)
  - Giorni lavorativi
  - Orari (se assenza parziale)
- Chiama `utils.send_email()` con `is_html=True`
- **Non blocca** la richiesta se l'email fallisce (error handling graceful)

---

### 3. **Invio Email (Funzione Utils)**
**File**: `utils.py` (linea 48-90)

```python
def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    smtp_host: str = "vandewiele-com.mail.protection.outlook.com",
    smtp_port: int = 25,
    is_html: bool = False,  # <-- nuovo parametro opzionale, default False
    timeout: int= 15
) -> None:
    """
    Invia l'email ai destinatari specificati.

    Args:
        recipients: Lista di indirizzi email destinatari
        subject: Oggetto dell'email
        body: Corpo dell'email (testo o HTML se is_html=True)
        smtp_host: Host SMTP
        smtp_port: Porta SMTP
        is_html: Se True invia il corpo come HTML (default: False)
    """
    if not recipients:
        logger.error("Nessun destinatario specificato per l'email")
        return

    try:
        sender = EmailSender(smtp_host, smtp_port)

        # ATTENZIONE: credenziali hardcoded – idealmente spostarle in config sicura
        sender.save_credentials(
            "Accounting@Eutron.it",
            "9jHgFhSs7Vf+"
        )

        sender.send_email(
            to_email=', '.join(recipients),
            subject=subject,
            body=body,
            is_html=is_html  # <-- passa il flag
        )
        logger.info("Email inviata con successo a %d destinatari", len(recipients))
        print("email inviata")
    except Exception as e:
        logger.error("Errore nell'invio dell'email: %s", str(e))
        raise
```

**Cosa fa:**
- Valida che ci siano destinatari
- Crea istanza di `EmailSender` con SMTP Host: **`vandewiele-com.mail.protection.outlook.com`** e porta **25**
- Salva credenziali (username: `Accounting@Eutron.it`)
- Chiama il metodo `send_email()` di `EmailSender` passando:
  - `to_email`: lista email unite da virgola
  - `subject`: oggetto
  - `body`: corpo (testo o HTML)
  - `is_html`: flag per formato HTML

---

## Diagramma Flusso

```
Utente invia richiesta assenza
    ↓
app.py - POST /api/request-absence
    ↓
absence_request.get_manager_emails(hire_history_id)
    ↓
SQL SP GetManager con EmployeeIdTableType
    ↓
Ritorna lista di email manager
    ↓
Se vuota → Fallback: gianluca.testa@vandewiele.com
    ↓
utils.send_email(recipients, subject, body, is_html=True)
    ↓
EmailSender.send_email() via SMTP
    ↓
Email inviata ai manager ✓
```

---

## Dettagli Importanti

### **Email Fallback**
Se nessun manager viene trovato dalla SP `GetManager`, il sistema invia automaticamente l'email a:
```
gianluca.testa@vandewiele.com
```

### **SMTP Configuration**
- **Host**: `vandewiele-com.mail.protection.outlook.com`
- **Porta**: 25 (non autenticato)
- **Username**: `Accounting@Eutron.it`
- **Password**: `9jHgFhSs7Vf+` ⚠️ **Hardcoded - RISCHIO SICUREZZA**

### **Email Format**
- **Format**: HTML
- **Encoding**: UTF-8
- **Lingua**: Rumeno + qualche parte in italiano

### **Campi Email Notifica**
1. Numero cerere (da Registry)
2. Data cerere (da Registry)
3. Nome dipendente
4. Tipo assenza
5. Periodo (inizio - fine)
6. Ore (se assenza parziale)
7. Giorni lavorativi

### **Error Handling**
- Se la SP fallisce → ritorna lista vuota, viene usato fallback
- Se l'invio email fallisce → **non blocca la richiesta**, solo log
- Se non ci sono destinatari → errore log, nessun invio

---

## Possibili Miglioramenti

1. **Sicurezza Credenziali**: Spostare username/password in file config sicuro
2. **Validazione Email**: Aggiungere regex per validare formato email
3. **Retry Logic**: Aggiungere retry per invio email
4. **Template Email**: Spostare template HTML in file separato
5. **CC/BCC**: Possibilità di aggiungere CC ai manager
6. **Notifiche Fallimento**: Notificare se SP non restituisce risultati

