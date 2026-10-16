-- =====================================================================
-- MIGRAZIONE: ASSENZE URGENTI E ASSENZE SPECIALI (v2.4.0)
-- ---------------------------------------------------------------------
-- Regole implementate:
--   1) ASSENZE URGENTI  (IDRequestType 18, Timeclocking):
--      - diritto per legge a max 10 giorni/anno per dipendente
--      - i giorni devono essere recuperati NEL MESE della richiesta
--        oppure ENTRO L'ANNO LAVORATIVO: la scelta del dipendente e'
--        un parametro (AbsenceRequestes.UrgentRecoveryPeriod = 'MONTH'|'YEAR')
--        con la scadenza calcolata memorizzata in UrgentRecoveryDeadline
--   2) ASSENZE SPECIALI (IDRequestType 19, Timeclocking):
--      - max 5 giorni/anno per dipendente (decesso, matrimonio, etc.)
--      - documentazione giustificativa da presentare fisicamente al
--        dep. HR entro 5 giorni dalla richiesta (AbsenceRules.DocsDeadlineDays)
--      - pena l'annullamento e la conversione in giorni di congedo
--        ordinario (AbsenceRules.ConvertToIDRequestType = 1)
--
-- Database coinvolti:
--   [Timeclocking]  -> tabella RequestType (2 nuovi tipi, ID fissi 18/19)
--   [Employee]      -> AbsenceRules (parametri quota), AbsenceRequestes
--                      (dati richiesta: scelta recupero + documentazione)
--   [Employees]     -> app.LeaveTypes / app.LeaveRequests (stessa logica
--                      per il nuovo programma di gestione dipendenti)
--
-- Script IDEMPOTENTE: puo' essere rieseguito senza errori.
-- I batch sono separati dal marcatore "-- >>> BATCH" per il runner Python.
-- In esecuzione manuale da SSMS: rimuovere i marcatori o eseguire a blocchi.
-- =====================================================================


-- >>> BATCH 1: [Timeclocking] nuovi tipi di richiesta (ID fissi per riferimenti nel codice kiosk)
IF NOT EXISTS (SELECT 1 FROM [Timeclocking].[dbo].[RequestType] WHERE IDRequestType = 18)
BEGIN
    SET IDENTITY_INSERT [Timeclocking].[dbo].[RequestType] ON;
    INSERT INTO [Timeclocking].[dbo].[RequestType]
        (IDRequestType, RequestName, Abbreviation, IsConsideredEntireDay, IsConsideredWeekends, IsConsideredPublicHoliday)
    VALUES
        (18, N'Invoire urgenta (recuperabila)', 'IU', 1, 0, 0);
    SET IDENTITY_INSERT [Timeclocking].[dbo].[RequestType] OFF;
    PRINT 'RequestType 18 (Invoire urgenta) inserito';
END
ELSE PRINT 'RequestType 18 gia presente';

IF NOT EXISTS (SELECT 1 FROM [Timeclocking].[dbo].[RequestType] WHERE IDRequestType = 19)
BEGIN
    SET IDENTITY_INSERT [Timeclocking].[dbo].[RequestType] ON;
    INSERT INTO [Timeclocking].[dbo].[RequestType]
        (IDRequestType, RequestName, Abbreviation, IsConsideredEntireDay, IsConsideredWeekends, IsConsideredPublicHoliday)
    VALUES
        (19, N'Motive speciale (deces, casatorie)', 'MS', 1, 0, 0);
    SET IDENTITY_INSERT [Timeclocking].[dbo].[RequestType] OFF;
    PRINT 'RequestType 19 (Motive speciale) inserito';
END
ELSE PRINT 'RequestType 19 gia presente';


-- >>> BATCH 2: [Employee].AbsenceRules - nuove colonne parametriche
IF COL_LENGTH('[Employee].[dbo].[AbsenceRules]', 'MaxDaysPerYear') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRules] ADD MaxDaysPerYear smallint NULL;
IF COL_LENGTH('[Employee].[dbo].[AbsenceRules]', 'DocsDeadlineDays') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRules] ADD DocsDeadlineDays tinyint NULL;
IF COL_LENGTH('[Employee].[dbo].[AbsenceRules]', 'ConvertToIDRequestType') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRules] ADD ConvertToIDRequestType tinyint NULL;
PRINT 'AbsenceRules: colonne parametro aggiunte (se assenti)';


-- >>> BATCH 3: [Employee].AbsenceRules - righe regole per i due nuovi tipi
IF NOT EXISTS (SELECT 1 FROM [Employee].[dbo].[AbsenceRules] WHERE IDRequestType = 18 AND DateOut IS NULL)
BEGIN
    INSERT INTO [Employee].[dbo].[AbsenceRules]
        (IDRequestType, DayNoZone, MaxDaysPerYear, DocsDeadlineDays, ConvertToIDRequestType)
    VALUES
        (18, 0, 10, NULL, NULL);  -- urgente: stesso giorno, 10 giorni/anno, nessun documento
    PRINT 'Regola AbsenceRules per tipo 18 inserita';
END
ELSE PRINT 'Regola tipo 18 gia presente';

IF NOT EXISTS (SELECT 1 FROM [Employee].[dbo].[AbsenceRules] WHERE IDRequestType = 19 AND DateOut IS NULL)
BEGIN
    INSERT INTO [Employee].[dbo].[AbsenceRules]
        (IDRequestType, DayNoZone, MaxDaysPerYear, DocsDeadlineDays, ConvertToIDRequestType)
    VALUES
        (19, 0, 5, 5, 1);  -- speciale: stesso giorno, 5 giorni/anno, documenti entro 5 gg, conversione in Concediu odihna (1)
    PRINT 'Regola AbsenceRules per tipo 19 inserita';
END
ELSE PRINT 'Regola tipo 19 gia presente';


-- >>> BATCH 4: [Employee].AbsenceRequestes - colonne per urgenza/recupero e documentazione
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'UrgentRecoveryPeriod') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD UrgentRecoveryPeriod varchar(10) NULL; -- 'MONTH' | 'YEAR' (scelta dipendente)
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'UrgentRecoveryDeadline') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD UrgentRecoveryDeadline date NULL;
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'SpecialReason') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD SpecialReason nvarchar(200) NULL;
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'DocumentationDeadline') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD DocumentationDeadline date NULL;
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'DocumentationReceived') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD DocumentationReceived bit NULL;
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'DocumentationReceivedDate') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD DocumentationReceivedDate datetime NULL;
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'ConvertedToOrdinary') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD ConvertedToOrdinary bit NOT NULL CONSTRAINT DF_AbsenceRequestes_ConvertedToOrdinary DEFAULT (0);
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'ConvertedToOrdinaryDate') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD ConvertedToOrdinaryDate datetime NULL;
IF COL_LENGTH('[Employee].[dbo].[AbsenceRequestes]', 'ConvertedAbsenceRequestId') IS NULL
    ALTER TABLE [Employee].[dbo].[AbsenceRequestes] ADD ConvertedAbsenceRequestId int NULL;
PRINT 'AbsenceRequestes: colonne urgenza/documentazione aggiunte (se assenti)';


-- >>> BATCH 5: [Employees].app.LeaveTypes - colonne parametriche (nuovo programma gestione dipendenti)
IF COL_LENGTH('[Employees].[app].[LeaveTypes]', 'RequiresDocumentation') IS NULL
    ALTER TABLE [Employees].[app].[LeaveTypes] ADD RequiresDocumentation bit NOT NULL CONSTRAINT DF_LeaveTypes_RequiresDocumentation DEFAULT (0);
IF COL_LENGTH('[Employees].[app].[LeaveTypes]', 'DocsDeadlineDays') IS NULL
    ALTER TABLE [Employees].[app].[LeaveTypes] ADD DocsDeadlineDays int NULL;
IF COL_LENGTH('[Employees].[app].[LeaveTypes]', 'ConvertToLeaveTypeId') IS NULL
    ALTER TABLE [Employees].[app].[LeaveTypes] ADD ConvertToLeaveTypeId int NULL;
IF COL_LENGTH('[Employees].[app].[LeaveTypes]', 'IsRecoverable') IS NULL
    ALTER TABLE [Employees].[app].[LeaveTypes] ADD IsRecoverable bit NOT NULL CONSTRAINT DF_LeaveTypes_IsRecoverable DEFAULT (0);
PRINT 'app.LeaveTypes: colonne parametro aggiunte (se assenti)';


-- >>> BATCH 6: [Employees].app.LeaveTypes - righe dei due nuovi tipi
IF NOT EXISTS (SELECT 1 FROM [Employees].[app].[LeaveTypes] WHERE LeaveCode = 'AU')
BEGIN
    INSERT INTO [Employees].[app].[LeaveTypes]
        (LeaveCode, LeaveDescription, LeaveDescriptionRo, LeaveDescriptionEn,
         IsPaid, MaxDaysPerYear, RequiresApproval, RequiresMedicalCert, MinAdvanceDays, IsActive,
         RequiresDocumentation, DocsDeadlineDays, ConvertToLeaveTypeId, IsRecoverable)
    VALUES
        ('AU', 'Assenze urgenti (recuperabili)', 'Invoire urgenta (recuperabila)', 'Urgent leave (recoverable)',
         1, 10, 1, 0, 0, 1, 0, NULL, NULL, 1);
    PRINT 'LeaveType AU (assenze urgenti) inserito';
END
ELSE PRINT 'LeaveType AU gia presente';

IF NOT EXISTS (SELECT 1 FROM [Employees].[app].[LeaveTypes] WHERE LeaveCode = 'MS')
BEGIN
    INSERT INTO [Employees].[app].[LeaveTypes]
        (LeaveCode, LeaveDescription, LeaveDescriptionRo, LeaveDescriptionEn,
         IsPaid, MaxDaysPerYear, RequiresApproval, RequiresMedicalCert, MinAdvanceDays, IsActive,
         RequiresDocumentation, DocsDeadlineDays, ConvertToLeaveTypeId, IsRecoverable)
    VALUES
        ('MS', 'Motivi speciali (decesso, matrimonio, ...)', 'Motive speciale (deces, casatorie)', 'Special leave (bereavement, marriage, ...)',
         1, 5, 1, 0, 0, 1, 1, 5, 1, 0);  -- documenti obbligatori entro 5 gg, conversione in LeaveTypeId 1 (Ferie annuali)
    PRINT 'LeaveType MS (motivi speciali) inserito';
END
ELSE PRINT 'LeaveType MS gia presente';


-- >>> BATCH 7: [Employees].app.LeaveRequests - colonne per urgenza/recupero e documentazione
IF COL_LENGTH('[Employees].[app].[LeaveRequests]', 'UrgentRecoveryPeriod') IS NULL
    ALTER TABLE [Employees].[app].[LeaveRequests] ADD UrgentRecoveryPeriod varchar(10) NULL; -- 'MONTH' | 'YEAR'
IF COL_LENGTH('[Employees].[app].[LeaveRequests]', 'UrgentRecoveryDeadline') IS NULL
    ALTER TABLE [Employees].[app].[LeaveRequests] ADD UrgentRecoveryDeadline date NULL;
IF COL_LENGTH('[Employees].[app].[LeaveRequests]', 'DocumentationDeadline') IS NULL
    ALTER TABLE [Employees].[app].[LeaveRequests] ADD DocumentationDeadline date NULL;
IF COL_LENGTH('[Employees].[app].[LeaveRequests]', 'DocumentationReceived') IS NULL
    ALTER TABLE [Employees].[app].[LeaveRequests] ADD DocumentationReceived bit NULL;
IF COL_LENGTH('[Employees].[app].[LeaveRequests]', 'DocumentationReceivedDate') IS NULL
    ALTER TABLE [Employees].[app].[LeaveRequests] ADD DocumentationReceivedDate datetime NULL;
IF COL_LENGTH('[Employees].[app].[LeaveRequests]', 'ConvertedToOrdinary') IS NULL
    ALTER TABLE [Employees].[app].[LeaveRequests] ADD ConvertedToOrdinary bit NOT NULL CONSTRAINT DF_LeaveRequests_ConvertedToOrdinary DEFAULT (0);
IF COL_LENGTH('[Employees].[app].[LeaveRequests]', 'ConvertedToOrdinaryDate') IS NULL
    ALTER TABLE [Employees].[app].[LeaveRequests] ADD ConvertedToOrdinaryDate datetime NULL;
IF COL_LENGTH('[Employees].[app].[LeaveRequests]', 'ConvertedLeaveRequestId') IS NULL
    ALTER TABLE [Employees].[app].[LeaveRequests] ADD ConvertedLeaveRequestId int NULL;
PRINT 'app.LeaveRequests: colonne urgenza/documentazione aggiunte (se assenti)';

-- >>> BATCH 8: verifica finale
SELECT rt.IDRequestType, rt.RequestName, rt.Abbreviation, ar.DayNoZone, ar.MaxDaysPerYear, ar.DocsDeadlineDays, ar.ConvertToIDRequestType
FROM [Timeclocking].[dbo].[RequestType] rt
LEFT JOIN [Employee].[dbo].[AbsenceRules] ar ON ar.IDRequestType = rt.IDRequestType AND ar.DateOut IS NULL
WHERE rt.IDRequestType IN (18, 19);

SELECT LeaveTypeId, LeaveCode, LeaveDescription, MaxDaysPerYear, RequiresDocumentation, DocsDeadlineDays, ConvertToLeaveTypeId, IsRecoverable
FROM [Employees].[app].[LeaveTypes]
WHERE LeaveCode IN ('AU', 'MS');
