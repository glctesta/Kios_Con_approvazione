# Query SQL per Gestione News

Questo documento contiene tutte le query SQL utili per gestire la tabella `Employee.dbo.News`.

---

## 1. Visualizzare Tutte le News

```sql
SELECT 
    NewId,
    EmployeerId,
    StartNews,
    EndNews,
    News,
    Publisher,
    IsMandatory,
    CASE 
        WHEN GETDATE() >= StartNews AND GETDATE() <= EndNews 
        THEN '🟢 ATTIVA' 
        ELSE '🔴 SCADUTA/FUTURA' 
    END AS Stato
FROM [Employee].[dbo].[News]
ORDER BY StartNews DESC;
```

---

## 2. Visualizzare Solo News Attive

```sql
SELECT 
    NewId,
    StartNews,
    EndNews,
    News,
    Publisher,
    IsMandatory
FROM [Employee].[dbo].[News]
WHERE GETDATE() >= StartNews 
  AND GETDATE() <= EndNews
ORDER BY IsMandatory DESC, StartNews ASC;
```

---

## 3. Inserire una News Normale (valida 7 giorni)

```sql
INSERT INTO [Employee].[dbo].[News] 
    ([EmployeerId], [StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    (2,                                    -- EmployeerId (tipicamente 2)
     GETDATE(),                            -- Inizia ora
     DATEADD(DAY, 7, GETDATE()),           -- Termina tra 7 giorni
     'Bine ați venit! Aceasta este o comunicare de test.',
     'Departament HR',
     0);                                   -- Non obbligatoria
```

---

## 4. Inserire una News Urgente/Obbligatoria (solo oggi)

```sql
INSERT INTO [Employee].[dbo].[News] 
    ([EmployeerId], [StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    (2, 
     -- Oggi alle 08:00
     CAST(CAST(GETDATE() AS DATE) AS DATETIME) + CAST('08:00:00' AS DATETIME),
     -- Oggi alle 18:00
     CAST(CAST(GETDATE() AS DATE) AS DATETIME) + CAST('18:00:00' AS DATETIME),
     '⚠️ ATENȚIE: Comunicare urgentă!',
     'Amministrazione',
     1);  -- OBBLIGATORIA
```

---

## 5. Modificare una News Esistente

```sql
UPDATE [Employee].[dbo].[News]
SET 
    News = 'Messaggio aggiornato: Meniu cantină modificat.',
    EndNews = DATEADD(DAY, 3, GETDATE())
WHERE NewId = 1;  -- Sostituire con l'ID corretto
```

---

## 6. Eliminare una News

```sql
DELETE FROM [Employee].[dbo].[News]
WHERE NewId = 1;  -- Sostituire con l'ID da eliminare
```

---

## 7. Disattivare una News (impostare EndNews a ieri)

```sql
UPDATE [Employee].[dbo].[News]
SET EndNews = DATEADD(DAY, -1, GETDATE())
WHERE NewId = 1;
```

---

## 8. Verificare News Visibili nel Kiosk (con logica priorità)

```sql
DECLARE @CurrentDate DATETIME = GETDATE();

-- News attive
WITH ActiveNews AS (
    SELECT 
        NewId, EmployeerId, StartNews, EndNews,
        News, Publisher, IsMandatory
    FROM [Employee].[dbo].[News]
    WHERE @CurrentDate >= StartNews 
      AND @CurrentDate <= EndNews
)
-- Se esistono mandatory, mostra solo quelle
SELECT 
    NewId, StartNews, EndNews, News, Publisher, IsMandatory,
    CASE 
        WHEN IsMandatory = 1 THEN '🔴 PRIORITÀ MASSIMA'
        ELSE '🟢 Normale'
    END AS Priorità
FROM ActiveNews
WHERE 
    CASE 
        WHEN EXISTS (SELECT 1 FROM ActiveNews WHERE IsMandatory = 1) 
        THEN IsMandatory 
        ELSE 1 
    END = 1
ORDER BY IsMandatory DESC, StartNews ASC;
```

---

## 9. Creare News per Tutta la Settimana Corrente

```sql
INSERT INTO [Employee].[dbo].[News] 
    ([EmployeerId], [StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    (2,
     -- Lunedì
     DATEADD(DAY, -(DATEPART(WEEKDAY, GETDATE()) - 1), 
             CAST(CAST(GETDATE() AS DATE) AS DATETIME)),
     -- Domenica 23:59:59
     DATEADD(DAY, 7 - DATEPART(WEEKDAY, GETDATE()), 
             CAST(CAST(GETDATE() AS DATE) AS DATETIME) + CAST('23:59:59' AS DATETIME)),
     'Comunicare pentru săptămâna curentă.',
     'Management',
     0);
```

---

## 10. Pulizia News Scadute (oltre 30 giorni fa)

```sql
DELETE FROM [Employee].[dbo].[News]
WHERE EndNews < DATEADD(DAY, -30, GETDATE());
```

---

## 11. Statistiche News

```sql
SELECT 
    COUNT(*) AS TotaleNews,
    SUM(CASE WHEN GETDATE() >= StartNews AND GETDATE() <= EndNews 
        THEN 1 ELSE 0 END) AS NewsAttive,
    SUM(CASE WHEN EndNews < GETDATE() THEN 1 ELSE 0 END) AS NewsScadute,
    SUM(CASE WHEN StartNews > GETDATE() THEN 1 ELSE 0 END) AS NewsFuture,
    SUM(CASE WHEN IsMandatory = 1 THEN 1 ELSE 0 END) AS NewsMandatory
FROM [Employee].[dbo].[News];
```

---

## 📝 Note Importanti

### Priorità Mandatory
Se esiste anche **una sola news con `IsMandatory = 1` attiva**, il sistema mostrerà **SOLO le news mandatory**, nascondendo tutte le altre.

### Formato Date
- Usare sempre formato: `'YYYY-MM-DD HH:MM:SS'`
- Esempio: `'2026-01-09 08:00:00'`

### EmployeerId
- Valore tipico: **2** (GTMC/Vandewiele)
- Può essere usato per filtrare news per specifici gruppi

### Rotazione
- News multiple ruotano automaticamente ogni **8 secondi**
- Una sola news rimane fissa

### Messaggio
- Campo `NVARCHAR(MAX)` - supporta messaggi molto lunghi
- Può contenere emoji: ⚠️ 🔔 📢 ✅ ❌
- **Consigliato:** max 200-300 caratteri per leggibilità

### Lingua
- Tutti i messaggi devono essere in **RUMENO**
- Il sistema non traduce automaticamente

---

## 🧪 Esempi Pratici

### Comunicazione Mensa
```sql
INSERT INTO [Employee].[dbo].[News] 
VALUES (2, GETDATE(), DATEADD(DAY, 1, GETDATE()),
        'Astăzi la cantină: paste cu carne și salată.',
        'Cantină', 0);
```

### Alert Manutenzione
```sql
INSERT INTO [Employee].[dbo].[News] 
VALUES (2, 
        CAST(CAST(GETDATE() AS DATE) AS DATETIME) + CAST('14:00:00' AS DATETIME),
        CAST(CAST(GETDATE() AS DATE) AS DATETIME) + CAST('15:30:00' AS DATETIME),
        '⚠️ Întrerupere curent electric între orele 14:30-15:30.',
        'Manutenzione', 1);
```

### Auguri Festività
```sql
INSERT INTO [Employee].[dbo].[News] 
VALUES (2, '2026-12-24 00:00:00', '2026-12-26 23:59:59',
        '🎄 La mulți ani! Vă dorim sărbători fericite!',
        'Direcție', 0);
```
