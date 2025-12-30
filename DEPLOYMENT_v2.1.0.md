# 🚀 GUIDA DEPLOYMENT v2.1.0
## Aggiornamento Sistema Gestione Richieste Assenza

**Versione:** 2.1.0  
**Data:** 30 Dicembre 2025  
**Tempo Stimato:** 10-15 minuti

---

## 📋 Prerequisiti

✅ Accesso al server di produzione  
✅ Permessi amministratore  
✅ Backup del sistema esistente  
✅ Servizio Kiosk attualmente funzionante

---

## 🎯 Cosa Viene Aggiornato

Questa versione introduce:
- ✅ Rilevamento automatico richieste scadute
- 📧 Reinvio notifiche ai manager
- 🔄 Email fallback automatica
- 🎨 UI migliorata per verifica stato

**IMPORTANTE:** Nessuna modifica al database richiesta!

---

## 📦 OPZIONE 1: Deployment Automatico (Consigliato)

### Passo 1: Crea Pacchetto
```batch
cd C:\Users\gtesta\PythonProjetcs\Python\Adeverente
CREA_PACCHETTO_DEPLOY.bat
```

Questo creerà un file `Kiosk_Deploy_YYYYMMDD_HHMMSS.zip`

### Passo 2: Trasferisci al Server
Copia il file ZIP sul server di produzione

### Passo 3: Estrai e Sostituisci
```batch
# Sul server di produzione
cd C:\Kiosk_HR

# Backup versione corrente
xcopy /E /I /Y . C:\Kiosk_HR_Backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%\

# Estrai nuovo pacchetto (sovrascrive file esistenti)
powershell -Command "Expand-Archive -Path 'Kiosk_Deploy_*.zip' -DestinationPath '.' -Force"
```

### Passo 4: Riavvia Servizio
```batch
# Ferma il servizio
taskkill /F /IM python.exe

# Riavvia
START_APP.bat
```

---

## 📝 OPZIONE 2: Deployment Manuale

Se preferisci aggiornare solo i file modificati:

### File da Aggiornare

#### 1. Backend
```batch
# Copia app.py
copy /Y app.py C:\Kiosk_HR\app.py
```

#### 2. Frontend - Templates
```batch
# Copia check.html
copy /Y templates\check.html C:\Kiosk_HR\templates\check.html
```

#### 3. Frontend - JavaScript
```batch
# Copia check.js
copy /Y static\js\check.js C:\Kiosk_HR\static\js\check.js
```

#### 4. CSS (Opzionale - solo se vuoi header compatto)
```batch
# Copia styles.css
copy /Y static\css\styles.css C:\Kiosk_HR\static\css\styles.css
```

#### 5. Documentazione
```batch
# Copia release notes
copy /Y RELEASE_NOTES_v2.1.0.md C:\Kiosk_HR\
```

### Riavvia Servizio
```batch
taskkill /F /IM python.exe
cd C:\Kiosk_HR
START_APP.bat
```

---

## ✅ Verifica Post-Deployment

### 1. Verifica Servizio Attivo
```batch
# Controlla che il servizio sia in esecuzione
tasklist | findstr python.exe
```

Dovresti vedere un processo `python.exe` attivo.

### 2. Test Funzionalità Base
1. Apri browser: `http://localhost:5000`
2. Verifica che la pagina principale si carichi
3. Testa generazione certificato

### 3. Test Nuove Funzionalità

#### Test Verifica Stato
1. Vai a: `http://localhost:5000/verifica`
2. Inserisci un numero richiesta esistente (es: `2ARQ-2025`)
3. Clicca "Verifică Starea"

**Verifica:**
- ✅ Lo stato viene mostrato correttamente
- ✅ Il colore corrisponde allo stato (verde/rosso/arancione)
- ✅ L'icona è appropriata (✅/❌/⏰/⏳)

#### Test Reinvio Notifica (solo per richieste pending)
1. Se la richiesta è "În Așteptare"
2. Verifica che appaia il pulsante "Retrimite Notificare"
3. Clicca il pulsante
4. Verifica toast di successo
5. Controlla email ricevuta

### 4. Verifica Logs
```batch
# Apri il log per verificare eventuali errori
notepad C:\Kiosk_HR\app_debug.log
```

Cerca messaggi recenti. Non dovrebbero esserci errori.

---

## 🔍 Troubleshooting

### Problema: Servizio non si avvia

**Soluzione:**
```batch
# Verifica log errori
type C:\Kiosk_HR\app_debug.log

# Verifica dipendenze
cd C:\Kiosk_HR
python -m pip list
```

### Problema: Pulsante "Retrimite Notificare" non appare

**Causa Possibile:** La richiesta non è in stato "pending"

**Verifica:**
- Data attuale deve essere ≤ data inizio richiesta
- Richiesta non deve essere già approvata o rifiutata

### Problema: Email non vengono inviate

**Verifica:**
1. Controlla configurazione email in `email_credentials.enc`
2. Verifica log per errori SMTP
3. Controlla che il fallback email sia corretto nel codice

**Log da cercare:**
```
Reinvio notifica a: ['email@example.com']
Email promemoria inviata con successo
```

### Problema: Errore "Invalid column name"

**Causa:** Query SQL non aggiornata

**Soluzione:**
Verifica che `app.py` usi `EmployrrHireHistoryId` (con doppia 'r')

---

## 🔄 Rollback (Se Necessario)

Se qualcosa va storto, puoi tornare alla versione precedente:

```batch
# Ferma servizio
taskkill /F /IM python.exe

# Ripristina backup
xcopy /E /I /Y C:\Kiosk_HR_Backup_YYYYMMDD\* C:\Kiosk_HR\

# Riavvia
cd C:\Kiosk_HR
START_APP.bat
```

---

## 📊 Monitoraggio Post-Deployment

### Primi 24 Ore
- ✅ Controlla log ogni 2-3 ore
- ✅ Monitora email ricevute
- ✅ Verifica feedback utenti

### Prima Settimana
- ✅ Controlla statistiche utilizzo funzione reinvio
- ✅ Verifica che le email fallback funzionino
- ✅ Raccogli feedback utenti

---

## 📧 Email di Test

Per testare il sistema email, puoi usare:

```python
# Da eseguire in Python console
from utils import send_email

send_email(
    recipients=['gianluca.testa@vandewiele.com'],
    subject='Test Email Sistema Kiosk v2.1.0',
    body='<h1>Test Email</h1><p>Sistema funzionante!</p>',
    is_html=True
)
```

---

## 📞 Supporto

### In caso di problemi:

**Email:** gianluca.testa@vandewiele.com

**Informazioni da fornire:**
1. Versione sistema operativo
2. Contenuto `app_debug.log` (ultime 50 righe)
3. Screenshot dell'errore
4. Passi per riprodurre il problema

---

## ✨ Funzionalità Opzionali

### Configurazione Email Fallback Personalizzata

Se vuoi cambiare l'email fallback da `gianluca.testa@vandewiele.com`:

1. Apri `app.py`
2. Cerca: `manager_emails = ['gianluca.testa@vandewiele.com']`
3. Sostituisci con l'email desiderata
4. Riavvia il servizio

**Nota:** Ci sono 2 occorrenze da modificare:
- Riga ~675 (submit_absence_request)
- Riga ~980 (resend_absence_notification)

---

## 📈 Metriche di Successo

Dopo il deployment, monitora:

| Metrica | Target | Come Verificare |
|---------|--------|-----------------|
| Uptime servizio | >99% | Task Manager |
| Email inviate | 100% | Log applicazione |
| Errori HTTP 500 | 0 | Log applicazione |
| Tempo risposta | <2s | Test manuale |
| Feedback utenti | Positivo | Survey/interviste |

---

## 🎓 Formazione Utenti

### Messaggio da comunicare agli utenti:

```
📢 AGGIORNAMENTO SISTEMA KIOSK HR - v2.1.0

Nuove funzionalità disponibili:

✅ Verifica automatica richieste scadute
📧 Possibilità di reinviare notifiche ai manager
⏰ Indicazione chiara dello stato di ogni richiesta

Come usare:
1. Vai su "Verificare Stare Cerere"
2. Inserisci il numero della tua richiesta
3. Se la richiesta è ancora in attesa, puoi reinviare la notifica

Per domande: gianluca.testa@vandewiele.com
```

---

## 🔐 Checklist Finale

Prima di considerare il deployment completato:

- [ ] Backup creato
- [ ] File aggiornati
- [ ] Servizio riavviato
- [ ] Test funzionalità base OK
- [ ] Test verifica stato OK
- [ ] Test reinvio notifica OK (se applicabile)
- [ ] Log verificati (nessun errore)
- [ ] Email test inviata con successo
- [ ] Documentazione aggiornata
- [ ] Utenti informati

---

**Fine Guida Deployment v2.1.0**

✅ Sistema pronto per la produzione!
