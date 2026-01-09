# Setup Database - Tabella KiosRequestes

## Script SQL per la Creazione della Tabella di Monitoraggio

Eseguire il seguente script SQL sul database **Employee** per creare la tabella che registra le richieste del Kiosk:

```sql
-- ========================================
-- SCRIPT CREAZIONE TABELLA KiosRequestes
-- ========================================
-- Database: Employee
-- Tabella per il monitoraggio dell'utilizzo del Kiosk HR

USE [Employee];
GO

-- Verifica se la tabella esiste già
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[KiosRequestes]') AND type in (N'U'))
BEGIN
    PRINT 'Creazione tabella KiosRequestes...';
    
    CREATE TABLE [dbo].[KiosRequestes] (
        [KiosRequestId] INT IDENTITY(1,1) NOT NULL,
        [RequestDate] DATETIME NOT NULL DEFAULT GETDATE(),
        [IpRequest] NVARCHAR(50) NULL,
        [RequestBy] NVARCHAR(200) NULL,
        [RequestWhat] NVARCHAR(500) NULL,
        [Executed] BIT NOT NULL DEFAULT 1,
        
        CONSTRAINT [PK_KiosRequestes] PRIMARY KEY CLUSTERED ([KiosRequestId] ASC)
            WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, 
                  ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
    ) ON [PRIMARY];
    
    PRINT 'Tabella KiosRequestes creata con successo!';
END
ELSE
BEGIN
    PRINT 'Tabella KiosRequestes già esistente.';
END
GO

-- Crea indici per migliorare le performance delle query di reporting
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_KiosRequestes_RequestDate' 
               AND object_id = OBJECT_ID('dbo.KiosRequestes'))
BEGIN
    PRINT 'Creazione indice IX_KiosRequestes_RequestDate...';
    
    CREATE NONCLUSTERED INDEX [IX_KiosRequestes_RequestDate]
        ON [dbo].[KiosRequestes] ([RequestDate] ASC)
        INCLUDE ([RequestBy], [RequestWhat], [Executed]);
    
    PRINT 'Indice creato con successo!';
END
ELSE
BEGIN
    PRINT 'Indice IX_KiosRequestes_RequestDate già esistente.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_KiosRequestes_RequestBy' 
               AND object_id = OBJECT_ID('dbo.KiosRequestes'))
BEGIN
    PRINT 'Creazione indice IX_KiosRequestes_RequestBy...';
    
    CREATE NONCLUSTERED INDEX [IX_KiosRequestes_RequestBy]
        ON [dbo].[KiosRequestes] ([RequestBy] ASC);
    
    PRINT 'Indice creato con successo!';
END
ELSE
BEGIN
    PRINT 'Indice IX_KiosRequestes_RequestBy già esistente.';
END
GO

-- Query di test per verificare la struttura
PRINT '';
PRINT '========================================';
PRINT 'STRUTTURA TABELLA KiosRequestes:';
PRINT '========================================';

SELECT 
    COLUMN_NAME AS 'Colonna',
    DATA_TYPE AS 'Tipo Dato',
    CHARACTER_MAXIMUM_LENGTH AS 'Lunghezza Max',
    IS_NULLABLE AS 'Nullable',
    COLUMN_DEFAULT AS 'Default'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'KiosRequestes'
ORDER BY ORDINAL_POSITION;
GO

PRINT '';
PRINT '========================================';
PRINT 'Setup completato!';
PRINT '========================================';
GO
```

## Descrizione Campi

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `KiosRequestId` | INT IDENTITY | ID univoco della richiesta (auto-incrementale) |
| `RequestDate` | DATETIME | Data e ora della richiesta (default: GETDATE()) |
| `IpRequest` | NVARCHAR(50) | Indirizzo IP del terminale kiosk |
| `RequestBy` | NVARCHAR(200) | Nome completo del dipendente |
| `RequestWhat` | NVARCHAR(500) | Descrizione della richiesta |
| `Executed` | BIT | 1 = richiesta eseguita con successo, 0 = fallita |

## Query di Verifica

Dopo la creazione, verificare che tutto funzioni correttamente:

```sql
-- Verifica esistenza tabella
SELECT * FROM sys.tables WHERE name = 'KiosRequestes';

-- Verifica indici
SELECT name, type_desc FROM sys.indexes 
WHERE object_id = OBJECT_ID('dbo.KiosRequestes');

-- Test inserimento
INSERT INTO [Employee].[dbo].[KiosRequestes]
    ([IpRequest], [RequestBy], [RequestWhat], [Executed])
VALUES
    ('192.168.1.100', 'TEST USER', 'Test Request', 1);

-- Verifica inserimento
SELECT TOP 5 * FROM [Employee].[dbo].[KiosRequestes]
ORDER BY RequestDate DESC;
```

## Permessi Necessari

Assicurarsi che l'utente del database utilizzato dall'applicazione Kiosk abbia i seguenti permessi:

```sql
-- Concedi permessi INSERT e SELECT sulla tabella
GRANT INSERT, SELECT ON [Employee].[dbo].[KiosRequestes] TO [NomeUtenteDatabaseKiosk];
GO
```

## Note

- La tabella è stata progettata per essere leggera e performante
- Gli indici ottimizzano le query di reporting per data e utente
- Il campo `Executed` permette di tracciare anche le richieste fallite per analisi
- La tabella non contiene dati sensibili, solo statistiche di utilizzo
