# Implementazione Sistema di Logging e Disclaimer

## Data: 2025-12-31

### Modifiche Implementate

Sono state implementate due nuove funzionalità nel sistema Kiosk HR:

---

## 1. Sistema di Logging Operazioni

### Descrizione
Ogni volta che il servizio eroga un documento o registra una richiesta di assenza, il sistema salva automaticamente:
- Nome utente (dipendente)
- Servizio richiesto
- Data, ora, minuto e secondo dell'operazione
- Esito dell'operazione (successo/fallimento)
- Eventuali messaggi di errore
- Informazioni aggiuntive

### Tabella Database

La tabella `Employee.dbo.ServiceOperationLog` deve essere creata nel database Employee.

**Script SQL per creare la tabella:**

```sql
USE [Employee]
GO

-- Crea la tabella se non esiste
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ServiceOperationLog]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ServiceOperationLog](
        [LogId] [int] IDENTITY(1,1) NOT NULL,
        [Username] [nvarchar](100) NOT NULL,
        [ServiceName] [nvarchar](200) NOT NULL,
        [OperationTimestamp] [datetime] NOT NULL DEFAULT (GETDATE()),
        [Success] [bit] NOT NULL,
        [ErrorMessage] [nvarchar](max) NULL,
        [AdditionalInfo] [nvarchar](max) NULL,
        CONSTRAINT [PK_ServiceOperationLog] PRIMARY KEY CLUSTERED 
        (
            [LogId] ASC
        )
    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
    
    PRINT 'Tabella ServiceOperationLog creata con successo'
END
ELSE
BEGIN
    PRINT 'Tabella ServiceOperationLog già esistente'
END
GO

-- Crea indice per ricerche per username
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ServiceOperationLog_Username' AND object_id = OBJECT_ID('dbo.ServiceOperationLog'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_ServiceOperationLog_Username] 
    ON [dbo].[ServiceOperationLog] ([Username] ASC)
    INCLUDE ([OperationTimestamp], [ServiceName], [Success])
    
    PRINT 'Indice IX_ServiceOperationLog_Username creato con successo'
END
GO

-- Crea indice per ricerche per data
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ServiceOperationLog_Timestamp' AND object_id = OBJECT_ID('dbo.ServiceOperationLog'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_ServiceOperationLog_Timestamp] 
    ON [dbo].[ServiceOperationLog] ([OperationTimestamp] DESC)
    INCLUDE ([Username], [ServiceName], [Success])
    
    PRINT 'Indice IX_ServiceOperationLog_Timestamp creato con successo'
END
GO

-- Crea indice per ricerche per servizio
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_ServiceOperationLog_Service' AND object_id = OBJECT_ID('dbo.ServiceOperationLog'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_ServiceOperationLog_Service] 
    ON [dbo].[ServiceOperationLog] ([ServiceName] ASC)
    INCLUDE ([OperationTimestamp], [Username], [Success])
    
    PRINT 'Indice IX_ServiceOperationLog_Service creato con successo'
END
GO

PRINT 'Setup tabella ServiceOperationLog completato'
GO
```

### Query di Esempio per Consultare i Log

```sql
-- Visualizza tutti i log recenti
SELECT TOP 100 
    LogId,
    Username,
    ServiceName,
    OperationTimestamp,
    CASE WHEN Success = 1 THEN 'Successo' ELSE 'Fallito' END AS Esito,
    ErrorMessage,
    AdditionalInfo
FROM Employee.dbo.ServiceOperationLog
ORDER BY OperationTimestamp DESC

-- Log per un utente specifico
SELECT 
    ServiceName,
    OperationTimestamp,
    CASE WHEN Success = 1 THEN 'Successo' ELSE 'Fallito' END AS Esito,
    AdditionalInfo
FROM Employee.dbo.ServiceOperationLog
WHERE Username = 'COGNOME NOME'
ORDER BY OperationTimestamp DESC

-- Statistiche per servizio
SELECT 
    ServiceName,
    COUNT(*) AS TotaleOperazioni,
    SUM(CASE WHEN Success = 1 THEN 1 ELSE 0 END) AS Successi,
    SUM(CASE WHEN Success = 0 THEN 1 ELSE 0 END) AS Fallimenti,
    CAST(SUM(CASE WHEN Success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) AS PercentualeSuccesso
FROM Employee.dbo.ServiceOperationLog
GROUP BY ServiceName
ORDER BY TotaleOperazioni DESC

-- Log delle ultime 24 ore
SELECT 
    Username,
    ServiceName,
    OperationTimestamp,
    CASE WHEN Success = 1 THEN 'Successo' ELSE 'Fallito' END AS Esito
FROM Employee.dbo.ServiceOperationLog
WHERE OperationTimestamp >= DATEADD(HOUR, -24, GETDATE())
ORDER BY OperationTimestamp DESC
```

### File Modificati
- `utils.py`: Aggiunta funzione `log_service_operation()`
- `certificate_generator.py`: Integrato logging nella generazione certificati
- `absence_request.py`: Integrato logging nelle richieste di assenza
- `app.py`: Aggiornata chiamata a `save_absence_request` con parametri per logging

---

## 2. Disclaimer in Rumeno nel Report Assenze

### Descrizione
Aggiunto disclaimer in rumeno (font 8) nel footer di ogni pagina del documento di riepilogo assenze annuali.

### Testo del Disclaimer
```
Dacă datele solicitate nu corespund cu ceea ce vă amintiți, vă rugăm să vă adresați 
biroului de Personal al Vandewiele România. Țineți cont că sistemul este în fază de 
dezvoltare și ar putea genera erori. Ne cerem scuze în avans, în cazul în care ar trebui 
să se întâmple. Vă mulțumim pentru înțelegere, Direcția.
```

### Traduzione Italiana
```
Se i dati richiesti non corrispondono a quanto vi ricordate, vi preghiamo di rivolgervi 
all'ufficio del Personale della Vandewiele Romania. Tenete in considerazione che il 
sistema è in fase di sviluppo e potrebbe generare degli errori. Ce ne scusiamo in 
anticipo, nel caso dovesse accadere. Grazie per la comprensione, La Direzione.
```

### File Modificati
- `absence_report.py`: 
  - Aggiunto metodo `_draw_disclaimer_footer()` per disegnare il disclaimer
  - Integrato disclaimer nel footer di tutte le pagine del PDF

---

## 3. Firma GTMC nella Pagina Principale

### Descrizione
Aggiunta firma discreta "By GTMC" con logo nel footer della pagina principale (launcher).

### Caratteristiche
- **Posizionamento**: Footer della pagina launcher, sotto il copyright
- **Stile**: Discreto, con opacità ridotta (50%) che aumenta all'hover (80%)
- **Logo**: Altezza 20px, con effetto grayscale che si rimuove all'hover
- **Design**: Minimalista e professionale, non invasivo

### File Modificati
- ✅ `templates/launcher.html` - Aggiunto elemento HTML per la firma GTMC
- ✅ `static/css/launcher.css` - Aggiunto stile CSS per rendering discreto
- ✅ `GTMC.png` - Logo GTMC generato e posizionato nella root del progetto

---

## 4. Servizio Printer Keep-Alive

### Descrizione
Servizio automatico che mantiene attiva la connessione con la stampante predefinita del sistema, inviando periodicamente una semplice query di stato senza stampare nulla. Questo previene che la stampante vada in sleep o si disconnetta.

### Funzionamento
- **Intervallo**: Ogni 5 minuti (300 secondi) - configurabile
- **Operazione**: Query di stato PowerShell (`Get-Printer`) senza stampa
- **Thread**: Eseguito in background come daemon thread
- **Auto-start**: Si avvia automaticamente con l'applicazione Flask
- **Auto-stop**: Si arresta automaticamente alla chiusura dell'applicazione

### Caratteristiche Tecniche
- **Non invasivo**: Non stampa nulla, solo verifica stato
- **Resiliente**: Gestisce errori e timeout senza bloccare l'applicazione
- **Logging**: Registra tutte le operazioni per diagnostica
- **Thread-safe**: Utilizza threading.Thread con daemon=True

### File Modificati
- ✅ `printer_keepalive.py` - Nuovo modulo con classe PrinterKeepAlive
- ✅ `app.py` - Integrato avvio/arresto automatico del servizio

### Configurazione
Per modificare l'intervallo di keep-alive, editare in `app.py`:
```python
start_printer_keepalive(interval_seconds=300)  # Default: 5 minuti
```

Intervalli consigliati:
- **Produzione**: 300 secondi (5 minuti)
- **Test**: 60 secondi (1 minuto)
- **Debug**: 30 secondi

---

## Istruzioni per il Deployment

### 1. Creare la Tabella di Logging
Eseguire lo script SQL sopra riportato sul database Employee per creare la tabella `ServiceOperationLog` e i relativi indici.

### 2. Testare il Sistema
1. Generare un certificato e verificare che venga creato un record nella tabella `ServiceOperationLog`
2. Creare una richiesta di assenza e verificare il logging
3. Generare un report assenze e verificare che il disclaimer appaia in tutte le pagine
4. Verificare che la firma "By GTMC" appaia discretamente nel footer della pagina launcher
5. Verificare nei log che il Printer Keep-Alive si avvii e funzioni correttamente

### 3. Monitoraggio
Utilizzare le query di esempio fornite per monitorare:
- Operazioni recenti
- Statistiche di successo/fallimento per servizio
- Attività per utente

---

## Note Tecniche

### Gestione Errori nel Logging
Il sistema di logging è progettato per non bloccare mai le operazioni principali. Se il logging fallisce:
- L'errore viene registrato nel log applicativo
- L'operazione principale continua normalmente
- Non viene sollevata alcuna eccezione

### Caratteri Rumeni
Il disclaimer utilizza caratteri speciali rumeni (ă, â, î, ș, ț) che sono correttamente supportati dal font DejaVuSans utilizzato nel sistema.

### Performance
Gli indici creati sulla tabella `ServiceOperationLog` garantiscono query veloci anche con grandi volumi di dati:
- Ricerca per username
- Ricerca per data/ora
- Ricerca per tipo di servizio

---

## Manutenzione

### Pulizia Periodica dei Log
Si consiglia di implementare una procedura di pulizia periodica per evitare che la tabella cresca eccessivamente:

```sql
-- Elimina log più vecchi di 1 anno
DELETE FROM Employee.dbo.ServiceOperationLog
WHERE OperationTimestamp < DATEADD(YEAR, -1, GETDATE())
```

### Backup
Includere la tabella `ServiceOperationLog` nelle procedure di backup regolari del database Employee.
