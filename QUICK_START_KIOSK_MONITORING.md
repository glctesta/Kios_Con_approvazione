# Kiosk Monitoring System - Quick Start Guide

## 📊 Panoramica

Sistema completo di monitoraggio dell'utilizzo del Kiosk HR che traccia tutte le richieste e invia report mensili automatici.

## 🚀 Deploy Rapido

### Step 1: Setup Database (Obbligatorio)

Aprire **SQL Server Management Studio** e connettersi al database Employee.

Copiare e eseguire lo script SQL dalla documentazione:
- Aprire il file: `SETUP_DATABASE_KIOSK_MONITORING.md`
- Copiare tutto lo script SQL
- Eseguirlo nel database **Employee**

Verifica:
```sql
SELECT TOP 5 * FROM Employee.dbo.KiosRequestes;
```

### Step 2: Test Logging (Verificare funzionamento)

1. Avviare l'applicazione Kiosk (`START_APP.bat`)
2. Effettuare una richiesta qualsiasi (certificato, report assenze, ecc.)
3. Verificare che sia stata registrata:

```sql
SELECT TOP 10 * 
FROM Employee.dbo.KiosRequestes
ORDER BY RequestDate DESC;
```

Dovreste vedere la vostra richiesta con:
- `RequestDate`: Data/ora
- `IpRequest`: IP del terminale
- `RequestBy`: Vostro nome
- `RequestWhat`: Tipo di richiesta
- `Executed`: 1 (successo)

### Step 3: Configurare Email Report (Opzionale)

Se volete modificare i destinatari dei report mensili:

1. Aprire `service_kiosk_reports.py`
2. Trovare la sezione:
```python
self.recipients = [
    "Gianluca.Testa@Vandewiele.com",
    "Cornelia.Ormenisan@Vandewiele.com"
]
```
3. Modificare gli indirizzi email come necessario
4. Salvare il file

### Step 4: Test Report Email (Prima di schedulare)

Per testare che l'email venga inviata correttamente:

1. Aprire `service_kiosk_reports.py`
2. Nel metodo `run_service()`, trovare e **decommentare** queste righe:
```python
# Per test: esegui subito (commentare in produzione)
logger.info("Esecuzione test immediata...")
self.send_monthly_report()
```

3. Eseguire il test:
```batch
START_KIOSK_REPORTS_SERVICE.bat
```

4. Verificate di ricevere l'email (può richiedere 1-2 minuti)

5. **IMPORTANTE**: Dopo il test, **ricommentare** le righe di test e salvare

### Step 5: Installare Servizio Windows (Produzione)

Per avviare automaticamente il servizio report ogni mese:

**Opzione A: NSSM (Consigliato)**

1. Scaricare NSSM da: https://nssm.cc/download
2. Estrarre `nssm.exe` in `C:\tools\nssm` (o altra cartella)
3. Aprire PowerShell come **Amministratore**
4. Eseguire:

```powershell
cd C:\Users\gtesta\PythonProjetcs\Python\Adeverente

C:\tools\nssm\nssm.exe install KioskReportsService "C:\Users\gtesta\PythonProjetcs\Python\Adeverente\venv\Scripts\python.exe"
C:\tools\nssm\nssm.exe set KioskReportsService AppParameters "C:\Users\gtesta\PythonProjetcs\Python\Adeverente\service_kiosk_reports.py"
C:\tools\nssm\nssm.exe set KioskReportsService AppDirectory "C:\Users\gtesta\PythonProjetcs\Python\Adeverente"
C:\tools\nssm\nssm.exe set KioskReportsService DisplayName "Kiosk HR Reports Service"
C:\tools\nssm\nssm.exe set KioskReportsService Description "Generates monthly usage reports for Kiosk HR system"
C:\tools\nssm\nssm.exe set KioskReportsService Start SERVICE_AUTO_START

# Avvia il servizio
C:\tools\nssm\nssm.exe start KioskReportsService
```

Verifica servizio:
```powershell
Get-Service KioskReportsService
```

**Opzione B: Windows Task Scheduler**

1. Aprire **Task Scheduler** (Utilità di pianificazione)
2. Creare nuova attività:
   - Nome: `Kiosk HR Monthly Report`
   - Trigger: Mensile, giorno 1, alle 08:00
   - Azione: Avvia programma
     - Programma: `C:\Users\gtesta\PythonProjetcs\Python\Adeverente\venv\Scripts\python.exe`
     - Argomenti: `service_kiosk_reports.py`
     - Percorso: `C:\Users\gtesta\PythonProjetcs\Python\Adeverente`
   - Impostazioni: Esegui con privilegi più elevati

## 📧 Contenuto Report Mensile

L'email mensile include:

**Statistiche Mese Precedente:**
- Totale richieste
- Utenti unici
- Tasso di successo
- Top 10 tipi di richieste
- Top 10 utenti più attivi

**Statistiche Year-To-Date (YTD):**
- Totale richieste dall'inizio dell'anno
- Utenti unici totali
- Tasso di successo complessivo
- Top 10 tipi di richieste YTD
- Top 10 utenti più attivi YTD

**Design:**
- Email HTML professionale
- Logo aziendale incluso
- Grafici e tabelle formattate
- Lingua: Inglese

## 📁 File Aggiunti al Progetto

```
Adeverente/
├── kiosk_request_logger.py              # Modulo logging richieste
├── service_kiosk_reports.py             # Servizio report mensili
├── KIOSK_MONITORING_SYSTEM.md           # Documentazione completa
├── SETUP_DATABASE_KIOSK_MONITORING.md   # Script SQL setup
├── START_KIOSK_REPORTS_SERVICE.bat      # Script avvio servizio
└── QUICK_START_KIOSK_MONITORING.md      # Questa guida
```

**Modifiche file esistenti:**
- `app.py`: Aggiunte chiamate ai metodi di logging
- `static/js/app.js`: Aggiunto badge number nel payload

## 🔍 Query Utili

### Statistiche Mensili
```sql
SELECT 
    YEAR(RequestDate) AS Anno,
    MONTH(RequestDate) AS Mese,
    COUNT(*) AS TotaleRichieste,
    COUNT(DISTINCT RequestBy) AS UtentiUnici
FROM Employee.dbo.KiosRequestes
GROUP BY YEAR(RequestDate), MONTH(RequestDate)
ORDER BY Anno DESC, Mese DESC;
```

### Top 10 Utenti
```sql
SELECT TOP 10
    RequestBy,
    COUNT(*) AS NumeroRichieste
FROM Employee.dbo.KiosRequestes
WHERE YEAR(RequestDate) = YEAR(GETDATE())
GROUP BY RequestBy
ORDER BY NumeroRichieste DESC;
```

### Richieste Ultime 24 Ore
```sql
SELECT *
FROM Employee.dbo.KiosRequestes
WHERE RequestDate >= DATEADD(HOUR, -24, GETDATE())
ORDER BY RequestDate DESC;
```

## 🛠️ Troubleshooting

### Le richieste non vengono registrate
1. Verificare che la tabella `KiosRequestes` esista
2. Controllare log applicazione: `app_debug.log`
3. Verificare permessi database

### Email non arrivano
1. Controllare log servizio: `kiosk_reports_service.log`
2. Verificare configurazione SMTP in `email_connector.py`
3. Verificare destinatari in `service_kiosk_reports.py`

### Il servizio non parte automaticamente
1. Verificare che sia installato come servizio Windows
2. Controllare Event Viewer di Windows
3. Testare manualmente: `START_KIOSK_REPORTS_SERVICE.bat`

## 📞 Supporto

Per problemi o domande:
- Email: Gianluca.Testa@Vandewiele.com
- Documentazione completa: `KIOSK_MONITORING_SYSTEM.md`
- Setup database: `SETUP_DATABASE_KIOSK_MONITORING.md`

## ✅ Checklist Deployment

- [ ] Eseguito script SQL creazione tabella
- [ ] Testato logging con richiesta di prova
- [ ] Verificato dati in tabella KiosRequestes
- [ ] Configurati destinatari email (se necessario)
- [ ] Testato invio email report
- [ ] Installato servizio Windows/Task Scheduler
- [ ] Verificato avvio automatico servizio
- [ ] Documentato procedura per team

---

**Versione**: 1.0.0  
**Data**: 09/01/2026  
**By**: GTMC - Gianluca Testa Management Consulting
