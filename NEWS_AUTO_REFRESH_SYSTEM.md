# Sistema Auto-Refresh News - Documentazione

## Panoramica
Il programma Kiosk dispone di un **sistema automatico di refresh delle news** che controlla periodicamente il database per rilevare eventuali nuove comunicazioni o modifiche a quelle esistenti, senza bisogno di riavviare l'applicazione o eseguire refresh manuali.

## Query Database
Il sistema esegue la seguente query sulla tabella `[Employee].[dbo].[News]`:

```sql
SELECT 
    NewId,
    EmployeerId,
    StartNews,
    EndNews,
    News,
    Publisher,
    IsMandatory
FROM [Employee].[dbo].[News]
WHERE GETDATE() >= StartNews AND GETDATE() <= EndNews
ORDER BY IsMandatory DESC, StartNews ASC
```

### Filtri Applicati
✅ **News Attive**: Vengono mostrate solo le news la cui data corrente è compresa tra `StartNews` ed `EndNews`  
✅ **Priorità Mandatory**: Le news con flag `IsMandatory = 1` vengono visualizzate per prime  
✅ **Ordinamento**: Prima le news obbligatorie, poi in ordine di data di inizio

---

## Tempistiche del Refresh

### 🔄 Refresh Iniziale
- **All'avvio dell'applicazione**: Le news vengono caricate immediatamente
- **Primo controllo automatico**: Dopo **5 minuti** dall'avvio

### 🔄 Refresh Periodico
- **Frequenza**: Ogni **5 minuti**
- **Continuazione**: Il refresh continua indefinitamente finché l'applicazione è in esecuzione

### 📊 Timeline Esempio
```
00:00 - Avvio applicazione → Caricamento iniziale news
05:00 - Primo auto-refresh → Controllo modifiche
10:00 - Secondo auto-refresh → Controllo modifiche
15:00 - Terzo auto-refresh → Controllo modifiche
...
```

---

## Logica di Aggiornamento Intelligente

Il sistema **NON aggiorna sempre** la visualizzazione, ma confronta le news esistenti con quelle nuove:

### ✅ Aggiornamento Automatico se:
- Il **numero di news** è cambiato
- Almeno un **`NewId`** è diverso
- Il **contenuto di un messaggio** (`News`) è stato modificato
- Lo **stato `IsMandatory`** di almeno una news è cambiato

### ⏸️ Nessun Aggiornamento se:
- Le news sono identiche a quelle precedenti
- Nessun dato rilevante è stato modificato

### 🔄 Comportamento Specifico

#### Se vengono aggiunte nuove news:
1. ✅ Il sistema **rileva l'aggiunta**
2. ✅ **Ferma la rotazione corrente** (se ci sono più news)
3. ✅ **Aggiorna l'elenco delle news**
4. ✅ **Riavvia la rotazione dalla prima news**

#### Se tutte le news scadono:
1. ✅ Il sistema **rileva che non ci sono più news attive**
2. ✅ **Nasconde il frame delle news**
3. ✅ Mostra il messaggio: _"Nu există comunicări în acest moment"_

---

## File Coinvolti

### Frontend
- **File**: `templates/launcher.html`
- **Funzioni principali**:
  - `initializeNews()` - Caricamento iniziale
  - `refreshNews()` - Refresh periodico e controllo modifiche
  - `hasNewsChanged()` - Confronto tra vecchie e nuove news
  - `startNewsRotation()` - Gestione rotazione multipla news
  - `displayNews()` - Visualizzazione singola news

### Backend
- **File**: `app.py`
- **Endpoint**: `/api/news` (metodo GET)
- **Funzione**: `get_news()`
- **Logica**:
  - Connessione al database SQL Server
  - Esecuzione query news attive
  - Separazione news mandatory/regular
  - Risposta JSON con elenco news

---

## Esempio di Utilizzo

### Scenario 1: Aggiunta di una Nuova News
1. **HR inserisce una news nel database** (usando interfaccia gestionale o SQL)
2. **Al prossimo refresh** (entro 5 minuti): la news viene rilevata automaticamente
3. **L'applicazione aggiorna la visualizzazione** senza intervento manuale
4. **Gli utenti vedono la nuova comunicazione**

### Scenario 2: Modifica di una News Esistente
1. **HR modifica il contenuto di una news** (campo `News`)
2. **Al prossimo refresh**: il sistema rileva la modifica
3. **L'applicazione aggiorna il testo** mostrato a video
4. **Gli utenti vedono la versione aggiornata**

### Scenario 3: Scadenza Automatica
1. **Una news raggiunge la data `EndNews`**
2. **Al prossimo refresh**: la news non viene più inclusa nella query
3. **L'applicazione rimuove automaticamente** la news dalla rotazione
4. **Gli utenti non vedono più la news scaduta**

---

## Log e Debug

Il sistema scrive messaggi di log nella console JavaScript:

```javascript
// Caricamento iniziale
"News API Response: {...}"
"Starting news rotation with N news items"

// Auto-refresh
"Auto-refresh news..."
"News modificate, aggiornamento in corso..."  // Se ci sono modifiche
"Nessuna modifica alle news"                  // Se non ci sono modifiche
"News non più disponibili"                    // Se tutte le news sono scadute
```

Per verificare il funzionamento:
1. Aprire **DevTools** del browser (F12)
2. Navigare alla tab **Console**
3. Osservare i messaggi di log durante il funzionamento

---

## Configurazione dei Tempi di Refresh

### Per Modificare l'Intervallo di Refresh

**File**: `templates/launcher.html`

**Linea 219** (primo refresh):
```javascript
setTimeout(() => refreshNews(), 5 * 60 * 1000); // 5 minuti
```

**Linea 271** (refresh successivi):
```javascript
setTimeout(() => refreshNews(), 5 * 60 * 1000); // 5 minuti
```

### Valori Consigliati
- **Minimo**: 2-3 minuti (per aggiornamenti rapidi, ma più carico sul database)
- **Ottimale**: 5 minuti (bilanciamento tra reattività e performance)
- **Bassa priorità**: 10-15 minuti (per news poco frequenti)

---

## FAQ - Domande Frequenti

### ❓ Le news nuove vengono mostrate automaticamente?
**✅ SÌ** - Ogni 5 minuti il sistema controlla il database e aggiorna automaticamente le news visualizzate.

### ❓ Devo riavviare l'applicazione per vedere nuove news?
**❌ NO** - Il sistema di auto-refresh rileva automaticamente le modifiche senza bisogno di riavvio.

### ❓ Quanto tempo ci vuole perché una nuova news appaia?
**⏱️ Massimo 5 minuti** - Il sistema esegue un controllo ogni 5 minuti. Nel caso peggiore, la news apparirà entro 5 minuti dall'inserimento.

### ❓ Cosa succede se modifico una news già pubblicata?
**🔄 Viene aggiornata automaticamente** - Al prossimo refresh (entro 5 minuti), il sistema rileva la modifica e aggiorna il contenuto visualizzato.

### ❓ Le news scadute vengono rimosse automaticamente?
**✅ SÌ** - Quando una news supera la data `EndNews`, al prossimo refresh viene automaticamente rimossa dalla visualizzazione.

### ❓ Posso impostare un refresh più frequente?
**✅ SÌ** - Modificare i valori nelle linee 219 e 271 di `launcher.html`. Ad esempio, per 2 minuti: `2 * 60 * 1000`.

### ❓ Il sistema funziona anche offline?
**⚠️ PARZIALMENTE** - Le news già caricate continueranno a ruotare, ma il refresh automatico fallirà fino al ripristino della connessione.

---

## Verifica del Funzionamento

### Test Manuale
1. **Aprire l'applicazione Kiosk** nella pagina launcher
2. **Osservare le news correnti** (se presenti)
3. **Inserire una nuova news nel database** usando SQL:
   ```sql
   INSERT INTO [Employee].[dbo].[News] 
       ([EmployeerId], [StartNews], [EndNews], [News], [Publisher], [IsMandatory])
   VALUES 
       (NULL, GETDATE(), DATEADD(day, 7, GETDATE()), 
        'Test auto-refresh', 'Sistema', 0)
   ```
4. **Attendere 5 minuti**
5. **Verificare che la nuova news appaia** automaticamente

### Test con Script
Utilizzare lo script di test fornito: `test_api_news.py`

```bash
python test_api_news.py
```

---

## Note Tecniche

### Gestione della Rotazione
- **Singola news**: Viene mostrata staticamente
- **Più news**: Rotazione automatica ogni 8 secondi
- **News mandatory**: Hanno priorità assoluta (se presenti, solo quelle vengono mostrate)

### Animazioni
- **Fade out**: 300ms
- **Cambio contenuto**
- **Fade in**: 300ms

### Sicurezza
- **Query parametrizzate**: Previene SQL injection
- **Error handling**: Gestione errori di connessione senza bloccare l'applicazione
- **Connessioni fresche**: Ogni richiesta usa una nuova connessione per evitare "connection broken"

---

## Changelog

### Versione 2.0 (2026-01-20)
✅ **Allineato intervallo primo refresh a 5 minuti** (era 15 minuti)  
✅ **Migliorata coerenza di timing** tra primo e successivi refresh  
✅ **Aggiunta documentazione completa** del sistema

### Versione 1.0 (Data precedente)
✅ Implementazione iniziale sistema auto-refresh  
✅ Logica di confronto intelligente news  
✅ Gestione separata news mandatory/regular

---

## Supporto

Per problemi o domande sul sistema di auto-refresh:
- **Verificare i log** nella console del browser
- **Testare l'endpoint** `/api/news` direttamente
- **Controllare la connessione** al database SQL Server
- **Verificare le date** `StartNews` e `EndNews` delle news nel database

---

**Documento creato**: 2026-01-20  
**Ultima modifica**: 2026-01-20  
**Versione**: 2.0
