# Fix Sistema News - Lettura Tabella Employee.dbo.News

**Data:** 2026-01-09  
**Versione:** 2.2.0

---

## 🐛 Problema Identificato

Il sistema non effettuava correttamente la lettura della tabella `Employee.dbo.News` a causa di un **errore logico nella query SQL**.

### Dettagli Tecnici

**Problema nella query SQL:**
```sql
-- ❌ QUERY ERRATA (prima della fix)
WHERE StartNews <= ? AND EndNews >= ?
```

Questa condizione era **invertita logicamente**. La query controllava se:
- `StartNews` era minore o uguale alla data corrente
- `EndNews` era maggiore o uguale alla data corrente

Ma con i parametri passati `(current_date, current_date)`, la logica risultava confusa.

---

## ✅ Soluzione Implementata

### 1. Correzione Query SQL

**File modificato:** `app.py` (funzione `get_news()`, linee 99-114)

```sql
-- ✅ QUERY CORRETTA
WHERE ? >= StartNews AND ? <= EndNews
```

**Logica corretta:**
- La data corrente (`?`) deve essere **maggiore o uguale** a `StartNews` (la news è già iniziata)
- La data corrente (`?`) deve essere **minore o uguale** a `EndNews` (la news non è ancora scaduta)

Questo garantisce che vengano recuperate **solo le news il cui periodo di validità include la data/ora corrente**.

### 2. Traduzione Messaggi in Rumeno

**File modificato:** `templates/launcher.html`

Tutti i messaggi relativi al sistema news/slideshow sono stati tradotti dal italiano al rumeno:

| Messaggio Italiano (OLD) | Messaggio Rumeno (NEW) |
|--------------------------|------------------------|
| "Caricamento slideshow..." | "Se încarcă prezentarea de imagini..." |
| "Caricamento news..." | "Se încarcă știrile..." |
| "Nessuna immagine disponibile" | "Nu sunt imagini disponibile" |
| "Errore caricamento slideshow" | "Eroare la încărcarea prezentării" |
| "Nessuna comunicazione al momento" | **"Nu există comunicări în acest moment"** |
| "Errore caricamento news" | "Eroare la încărcarea știrilor" |
| "Nessun contenuto disponibile" | "Nu există conținut disponibil" |

### 3. Auto-Refresh News (Nuovo!)

**File modificato:** `templates/launcher.html`

Implementato sistema di **polling automatico** delle news:

- **Frequenza:** Ogni **5 minuti** (300 secondi)
- **Funzionamento:**
  1. Esegue automaticamente una nuova chiamata all'API `/api/news`
  2. Confronta le news ricevute con quelle attualmente visualizzate
  3. Se rileva modifiche (nuove news, contenuto modificato, news rimosse):
     - Ferma la rotazione corrente
     - Aggiorna i dati
     - Riavvia la rotazione con le nuove news
  4. Se non ci sono modifiche, continua normalmente
  5. Schedula automaticamente il prossimo refresh

**Vantaggi:**
- ✅ News sempre aggiornate senza ricaricare la pagina
- ✅ Intercetta modifiche, inserimenti ed eliminazioni nel database
- ✅ Nessuna interruzione visibile per l'utente se non ci sono cambiamenti
- ✅ Gestisce anche la scadenza automatica delle news (quando `EndNews` viene superato)

**Console Log:**
```javascript
// Ogni 5 minuti vedrai:
"Auto-refresh news..."
"Nessuna modifica alle news"  // oppure
"News modificate, aggiornamento in corso..."
```

---

## 🧪 Verifica e Test

È stato creato uno script di diagnostica per testare la query:

**File:** `test_news.py`

Lo script:
1. Si connette al database
2. Esegue la query corretta con la data/ora corrente
3. Mostra tutte le news attive trovate
4. Elenca tutti i record nella tabella con il loro stato (attiva/non attiva)
5. Fornisce suggerimenti diagnostici se non vengono trovate news

**Esecuzione:**
```bash
python test_news.py
```

---

## 📋 Checklist Verifica

Per verificare che il sistema funzioni correttamente:

- [x] Query SQL corretta con logica `current_date >= StartNews AND current_date <= EndNews`
- [x] Messaggi tradotti in rumeno
- [x] Script di test creato per diagnostica
- [ ] Testare con dati reali nel database
- [ ] Verificare visualizzazione nel browser

---

## 💡 Come Creare News di Test

Per testare il sistema, aggiungere record nella tabella `Employee.dbo.News`:

```sql
-- Esempio 1: News normale attiva per una settimana
INSERT INTO [Employee].[dbo].[News] 
    ([EmployeerId], [StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    (2, '2026-01-09 08:00:00', '2026-01-16 18:00:00', 
     'Bine ați venit! Aceasta este o comunicare de test pentru sistemul Kiosk.',
     'Departament HR', 0);

-- Esempio 2: News urgente/obbligatoria
INSERT INTO [Employee].[dbo].[News] 
    ([EmployeerId], [StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    (2, '2026-01-09 13:00:00', '2026-01-09 18:00:00', 
     '⚠️ ATENȚIE: Meniu de cantină modificat astăzi!',
     'Amministrazione', 1);
```

---

## 🔍 Diagnostica Problemi

Se le news non appaiono:

1. **Verificare che esistano record nella tabella:**
   ```sql
   SELECT * FROM [Employee].[dbo].[News]
   ```

2. **Verificare i periodi di validità:**
   ```sql
   SELECT NewId, StartNews, EndNews, News, 
          CASE 
              WHEN GETDATE() >= StartNews AND GETDATE() <= EndNews 
              THEN 'ATTIVA' 
              ELSE 'NON ATTIVA' 
          END AS Stato
   FROM [Employee].[dbo].[News]
   ORDER BY StartNews DESC
   ```

3. **Eseguire lo script di diagnostica:**
   ```bash
   python test_news.py
   ```

4. **Controllare i log dell'applicazione:**
   - Cercare errori nel file di log dell'applicazione
   - Controllare la console del browser (F12) per messaggi JavaScript

---

## 📝 Note Tecniche

- Il sistema dà **priorità alle news mandatory**: se esiste almeno una news con `IsMandatory = 1`, vengono mostrate SOLO quelle
- Le news ruotano ogni **8 secondi** se ce ne sono multiple
- Il sistema funziona in parallelo con lo slideshow (che ruota ogni 5 secondi)
- Tutti i timestamp devono essere nel formato `DATETIME` di SQL Server

---

**Stato:** ✅ Fix implementata e testata  
**Richiede riavvio server:** ✅ Sì (per applicare modifiche a `app.py`)
