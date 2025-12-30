# 📋 RELEASE NOTES - v2.1.0
## Sistema Kiosk HR - Gestione Richieste Assenza

**Data Release:** 30 Dicembre 2025  
**Versione:** 2.1.0  
**Tipo:** Feature Update - Gestione Richieste Assenza Scadute

---

## 🎯 Nuove Funzionalità

### 1. **Rilevamento Automatico Richieste Scadute**
Il sistema ora distingue automaticamente tra richieste:
- ✅ **Approvate** - Autorizzate correttamente dal manager
- ❌ **Respinte** - Rifiutate esplicitamente
- ⏰ **Scadute** - Non autorizzate in tempo (data attuale > data inizio)
- ⏳ **In Attesa** - Ancora valide per l'approvazione

**Logica Implementata:**
```
SE data_attuale > data_inizio E NON approvata E NON rifiutata
  → SCADUTA (messaggio: "Expirată - neautorizată la timp")

SE data_attuale ≤ data_inizio E NON approvata E NON rifiutata
  → IN ATTESA (può essere reinviata)
```

### 2. **Reinvio Notifiche ai Manager**
Nuova funzionalità per reinviare le notifiche email ai manager per richieste ancora in attesa:

**Caratteristiche:**
- 📧 Pulsante "Retrimite Notificare" visibile solo per richieste `pending`
- 🔒 Anti-spam: disabilitazione automatica per 10 secondi dopo l'invio
- ✓ Feedback visivo immediato
- 🔔 Email con template professionale e icona promemoria

### 3. **Email Fallback Automatica**
Sistema di fallback per garantire che le notifiche non vengano mai perse:

**Comportamento:**
- Se vengono trovati manager → Email inviata ai manager
- Se NON vengono trovati manager → Email inviata a `gianluca.testa@vandewiele.com`

**Applicato a:**
- Creazione nuove richieste (`/api/submit-absence-request`)
- Reinvio notifiche (`/api/resend-absence-notification`)

---

## 🔧 Modifiche Tecniche

### Backend (`app.py`)

#### Endpoint Modificati:

**`/api/check-request-status` (Migliorato)**
- Aggiunto calcolo automatico dello stato (`approved`, `rejected`, `expired`, `pending`)
- Aggiunto campo `can_resend` per controllare la visibilità del pulsante
- Corretta query SQL per usare `EmployrrHireHistoryId` (nome colonna database)

**`/api/submit-absence-request` (Aggiornato)**
- Aggiunta logica fallback email a `gianluca.testa@vandewiele.com`
- Rimossa condizione che bloccava l'invio se non c'erano manager

#### Nuovi Endpoint:

**`/api/resend-absence-notification` (Nuovo)**
```python
POST /api/resend-absence-notification
Body: { "requestNumber": "2ARQ-2025" }

Response: {
  "success": true,
  "message": "Notificare retrimisă cu succes",
  "recipients": ["manager@example.com"]
}
```

**Funzionalità:**
- Recupera informazioni richiesta tramite JOIN con tabelle Employee
- Trova manager tramite stored procedure `GetManager`
- Usa fallback email se non trova manager
- Invia email HTML professionale con template promemoria

### Frontend

#### File Modificati:

**`templates/check.html`**
- Aggiunto pulsante "Retrimite Notificare" con icona 📧
- Pulsante nascosto di default, mostrato solo per richieste pending

**`static/js/check.js`**
- Implementata funzione `handleResendNotification()`
- Aggiunta logica switch/case per gestire 4 stati diversi
- Implementato sistema anti-spam con disabilitazione temporanea
- Aggiornati colori e icone per ogni stato:
  - ✅ Verde per approvate
  - ❌ Rosso per respinte
  - ⏰ Rosso scuro per scadute
  - ⏳ Arancione per in attesa

---

## 🎨 Miglioramenti UI/UX

### Interfaccia Verifica Stato
1. **Colori Distintivi:** Ogni stato ha un colore e icona univoci
2. **Messaggi Chiari:** Testi in rumeno comprensibili
3. **Feedback Immediato:** Toast notifications per conferme/errori
4. **Anti-Spam:** Prevenzione invii multipli accidentali

### Email Template
- Design HTML professionale
- Icona 🔔 per email di promemoria
- Tabella riepilogativa con tutti i dettagli
- Footer con disclaimer automatico

---

## 📦 File Modificati

### Backend
- `app.py` - Endpoint check-request-status, submit-absence-request, resend-absence-notification

### Frontend
- `templates/check.html` - Aggiunto pulsante reinvio
- `static/js/check.js` - Logica gestione stati e reinvio notifiche

### CSS
- `static/css/styles.css` - Ottimizzazioni header e layout compatto

---

## 🚀 Istruzioni Deployment

### 1. Backup Database
```sql
-- Nessuna modifica al database richiesta
-- Tutte le modifiche sono solo applicative
```

### 2. Aggiornamento File
Copiare i seguenti file nella directory di produzione:
- `app.py`
- `templates/check.html`
- `static/js/check.js`
- `static/css/styles.css`

### 3. Riavvio Servizio
```batch
# Fermare il servizio
taskkill /F /IM python.exe

# Riavviare con il nuovo codice
START_APP.bat
```

### 4. Verifica Funzionamento
1. Accedere a `http://localhost:5000/verifica`
2. Testare con una richiesta esistente
3. Verificare che gli stati siano corretti
4. Testare il pulsante "Retrimite Notificare" (se presente)

---

## ⚠️ Note Importanti

### Compatibilità
- ✅ Compatibile con tutte le versioni precedenti
- ✅ Nessuna modifica al database richiesta
- ✅ Nessuna dipendenza aggiuntiva

### Email Fallback
L'email `gianluca.testa@vandewiele.com` riceverà notifiche per:
- Dipendenti senza manager configurato
- Errori nella stored procedure `GetManager`
- Qualsiasi situazione in cui non vengono trovati destinatari

### Performance
- Nessun impatto sulle performance
- Query ottimizzate con JOIN appropriati
- Cache non necessaria per questa funzionalità

---

## 🐛 Bug Fix

### Risolti in questa versione:
1. **Colonna Database:** Corretto nome colonna da `EmployeeHireHistoryId` a `EmployrrHireHistoryId`
2. **Query SQL:** Rimosso riferimento a colonna `IssuedBy` non esistente
3. **Email Blocking:** Rimossa condizione che impediva l'invio email senza manager

---

## 📞 Supporto

Per problemi o domande:
- **Email:** gianluca.testa@vandewiele.com
- **Logs:** Verificare `app_debug.log` per dettagli errori

---

## 📅 Prossimi Sviluppi

Funzionalità pianificate per versioni future:
- Dashboard manager per approvazione diretta da web
- Notifiche push per richieste in scadenza
- Report statistiche richieste per reparto
- Integrazione calendario aziendale

---

**Fine Release Notes v2.1.0**
