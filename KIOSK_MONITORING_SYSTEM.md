# Sistema di Monitoraggio Utilizzo Kiosk HR

## Panoramica

Questo sistema implementa un monitoraggio completo dell'utilizzo del Kiosk HR, registrando tutte le richieste effettuate dagli utenti e generando report mensili automatici.

## Componenti

### 1. Database - Tabella `KiosRequestes`

La tabella traccia ogni richiesta effettuata nel kiosk:

```sql
CREATE TABLE [Employee].[dbo].[KiosRequestes] (
    [KiosRequestId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [RequestDate] DATETIME NOT NULL DEFAULT GETDATE(),
    [IpRequest] NVARCHAR(50) NULL,
    [RequestBy] NVARCHAR(200) NULL,
    [RequestWhat] NVARCHAR(500) NULL,
    [Executed] BIT NOT NULL DEFAULT 1
);

-- Indici per performance
CREATE NONCLUSTERED INDEX [IX_KiosRequestes_RequestDate]
    ON [dbo].[KiosRequestes] ([RequestDate] ASC)
    INCLUDE ([RequestBy], [RequestWhat], [Executed]);

CREATE NONCLUSTERED INDEX [IX_KiosRequestes_RequestBy]
    ON [dbo].[KiosRequestes] ([RequestBy] ASC);
```

**Campi:**
- `KiosRequestId`: ID univoco della richiesta (auto-incrementale)
- `RequestDate`: Data e ora della richiesta
- `IpRequest`: Indirizzo IP del terminale kiosk
- `RequestBy`: Nome del dipendente (recuperato dal badge)
- `RequestWhat`: Descrizione della richiesta (es. "Certificato - Medico", "Cerere Absență - Ferie")
- `Executed`: Flag che indica se la richiesta è stata eseguita con successo

### 2. Modulo `kiosk_request_logger.py`

Gestisce il logging di tutte le richieste:

**Funzionalità principali:**
- `get_client_ip()`: Recupera l'indirizzo IP del terminale
- `get_employee_name_from_badge()`: Recupera il nome del dipendente dal badge
- `log_request()`: Registra una richiesta generica
- `log_certificate_request()`: Log specifico per certificati
- `log_absence_report_request()`: Log specifico per report assenze
- `log_absence_request_submission()`: Log specifico per richieste assenza
- `log_request_status_check()`: Log specifico per verifiche stato

**Query utilizzata per recuperare il nome dal badge:**
```sql
SELECT e.EmployeeSurname + ' ' + e.EmployeeName AS EmployeeName 
FROM tbuserkey U 
INNER JOIN employee.dbo.employees e ON e.employeeid = u.idanga 
INNER JOIN employee.dbo.EmployeeHireHistory H ON h.employeeid = e.EmployeeId  
    AND h.employeerid = 2 AND h.EndWorkDate IS NULL 
INNER JOIN employee.dbo.EmployeeAddress A ON a.EmployeeId = e.EmployeeId  
    AND a.dateout IS NULL
INNER JOIN employee.dbo.EmployeeBadgeHistory BH  
    ON bh.EmployeeHireHistoryId = h.EmployeeHireHistoryId AND bh.dateout IS NULL
INNER JOIN employee.dbo.badges B ON b.BadgeId = BH.BadgeID
WHERE b.NoBadge = ?
```

### 3. Servizio `service_kiosk_reports.py`

Servizio di background che:
- Genera report mensili automaticamente ogni 1° del mese alle 08:00
- Invia email a destinatari specificati con statistiche YTD e mensili
- Utilizza template HTML professionale con logo e grafici

**Destinatari email:**
- Gianluca.Testa@Vandewiele.com
- Cornelia.Ormenisan@Vandewiele.com

**Report include:**
- Statistiche mensili (mese precedente)
- Statistiche YTD (Year-To-Date)
- Top 10 tipi di richieste più frequenti
- Top 10 utenti più attivi
- Tasso di successo delle richieste
- Numero di utenti unici e terminali unici

### 4. Integrazione in `app.py`

Il sistema è integrato in tutte le funzioni principali:

**Certificati (`/api/generate-certificate`):**
```python
kiosk_logger.log_certificate_request(badge_number, reason, executed=True)
```

**Report Assenze (`/api/generate-absence-report`):**
```python
kiosk_logger.log_absence_report_request(badge_number, year, executed=True)
```

**Richieste Assenza (`/api/submit-absence-request`):**
```python
kiosk_logger.log_absence_request_submission(badge_number, request_type_name, executed=True)
```

## Installazione e Configurazione

### Step 1: Creazione Tabella Database

Eseguire le seguenti query SQL sul database `Employee`:

```sql
USE [Employee];
GO

-- Crea tabella
CREATE TABLE [dbo].[KiosRequestes] (
    [KiosRequestId] INT IDENTITY(1,1) NOT NULL,
    [RequestDate] DATETIME NOT NULL DEFAULT GETDATE(),
    [IpRequest] NVARCHAR(50) NULL,
    [RequestBy] NVARCHAR(200) NULL,
    [RequestWhat] NVARCHAR(500) NULL,
    [Executed] BIT NOT NULL DEFAULT 1,
    CONSTRAINT [PK_KiosRequestes] PRIMARY KEY CLUSTERED ([KiosRequestId] ASC)
) ON [PRIMARY];
GO

-- Crea indici
CREATE NONCLUSTERED INDEX [IX_KiosRequestes_RequestDate]
    ON [dbo].[KiosRequestes] ([RequestDate] ASC)
    INCLUDE ([RequestBy], [RequestWhat], [Executed]);
GO

CREATE NONCLUSTERED INDEX [IX_KiosRequestes_RequestBy]
    ON [dbo].[KiosRequestes] ([RequestBy] ASC);
GO
```

### Step 2: Verifica File Installati

Assicurarsi che i seguenti file siano presenti:
- `kiosk_request_logger.py`
- `service_kiosk_reports.py`

### Step 3: Configurazione Servizio Report (Opzionale)

Per modificare i destinatari email, editare `service_kiosk_reports.py`:

```python
self.recipients = [
    "Gianluca.Testa@Vandewiele.com",
    "Cornelia.Ormenisan@Vandewiele.com"
]
```

### Step 4: Avvio Servizio Report

**Modalità Manuale (Test):**
```batch
cd C:\Users\gtesta\PythonProjetcs\Python\Adeverente
venv\Scripts\activate
python service_kiosk_reports.py
```

**Modalità Automatica (Windows Service):**

Usare NSSM (Non-Sucking Service Manager):

```batch
nssm install KioskReportsService "C:\Users\gtesta\PythonProjetcs\Python\Adeverente\venv\Scripts\python.exe"
nssm set KioskReportsService AppParameters "C:\Users\gtesta\PythonProjetcs\Python\Adeverente\service_kiosk_reports.py"
nssm set KioskReportsService AppDirectory "C:\Users\gtesta\PythonProjetcs\Python\Adeverente"
nssm set KioskReportsService DisplayName "Kiosk HR Reports Service"
nssm set KioskReportsService Description "Servizio per generazione report mensili utilizzo Kiosk HR"
nssm set KioskReportsService Start SERVICE_AUTO_START
nssm start KioskReportsService
```

## Query di Esempio

### Statistiche Mensili
```sql
SELECT 
    YEAR(RequestDate) AS Anno,
    MONTH(RequestDate) AS Mese,
    COUNT(*) AS TotaleRichieste,
    COUNT(DISTINCT RequestBy) AS UtentiUnici,
    COUNT(DISTINCT IpRequest) AS TerminaliUnici,
    SUM(CASE WHEN Executed = 1 THEN 1 ELSE 0 END) AS RichiesteRiuscite,
    SUM(CASE WHEN Executed = 0 THEN 1 ELSE 0 END) AS RichiesteFallite
FROM [Employee].[dbo].[KiosRequestes]
GROUP BY YEAR(RequestDate), MONTH(RequestDate)
ORDER BY Anno DESC, Mese DESC;
```

### Top 10 Tipi di Richieste
```sql
SELECT TOP 10
    RequestWhat,
    COUNT(*) AS Conteggio
FROM [Employee].[dbo].[KiosRequestes]
WHERE YEAR(RequestDate) = YEAR(GETDATE())
GROUP BY RequestWhat
ORDER BY Conteggio DESC;
```

### Top 10 Utenti Attivi
```sql
SELECT TOP 10
    RequestBy,
    COUNT(*) AS NumeroRichieste
FROM [Employee].[dbo].[KiosRequestes]
WHERE YEAR(RequestDate) = YEAR(GETDATE())
GROUP BY RequestBy
ORDER BY NumeroRichieste DESC;
```

### Analisi per Terminale (IP)
```sql
SELECT 
    IpRequest,
    COUNT(*) AS NumeroRichieste,
    COUNT(DISTINCT RequestBy) AS UtentiDistinti
FROM [Employee].[dbo].[KiosRequestes]
WHERE RequestDate >= DATEADD(MONTH, -1, GETDATE())
GROUP BY IpRequest
ORDER BY NumeroRichieste DESC;
```

## Test del Sistema

### Test Logging
Per testare il logging, effettuare alcune richieste dal kiosk e verificare:

```sql
SELECT TOP 10 * 
FROM [Employee].[dbo].[KiosRequestes]
ORDER BY RequestDate DESC;
```

### Test Report Manuale
Per testare il servizio di report manualmente (senza attendere il 1° del mese):

1. Modificare `service_kiosk_reports.py`
2. Decommentare la riga nel metodo `run_service()`:
```python
# Per test: esegui subito (commentare in produzione)
logger.info("Esecuzione test immediata...")
self.send_monthly_report()
```
3. Eseguire il servizio:
```batch
python service_kiosk_reports.py
```

## Troubleshooting

### Il logging non funziona
- Verificare che la tabella `KiosRequestes` esista
- Verificare i permessi di scrittura sul database
- Controllare i log in `app_debug.log`

### Email non ricevute
- Verificare configurazione SMTP in `email_connector.py`
- Verificare credenziali email
- Controllare i log in `kiosk_reports_service.log`

### Dati IP mancanti
- L'IP viene recuperato automaticamente dal server
- Potrebbe essere "Unknown" se il server non riesce a risolvere l'hostname

## Manutenzione

### Pulizia Dati Vecchi
Per mantenere le performance, considerare di archiviare/eliminare dati più vecchi di 2 anni:

```sql
-- Archivia in tabella storica
SELECT * INTO KiosRequestes_Archive
FROM [Employee].[dbo].[KiosRequestes]
WHERE RequestDate < DATEADD(YEAR, -2, GETDATE());

-- Elimina i vecchi record
DELETE FROM [Employee].[dbo].[KiosRequestes]
WHERE RequestDate < DATEADD(YEAR, -2, GETDATE());
```

### Aggiornamento Destinatari Email
Modificare la lista in `service_kiosk_reports.py` e riavviare il servizio.

## Sicurezza

- Il sistema NON registra dati sensibili (es. password, numeri di carta)
- Registra solo informazioni di utilizzo (chi, cosa, quando)
- I log sono archiviati nel database aziendale protetto
- Le email contengono solo statistiche aggregate

## Versioni

- **v1.0.0** (2026-01-09): Implementazione iniziale
  - Logging tutte le richieste kiosk
  - Report mensili automatici
  - Integrazione completa in app.py
