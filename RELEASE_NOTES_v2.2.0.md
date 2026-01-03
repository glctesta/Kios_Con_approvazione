# Release Notes - Versione 2.2.0

**Data**: 2026-01-03  
**Tipo**: Feature Release - Sistema News & Slideshow

## 🎉 Nuove Funzionalità

### Sistema News & Slideshow Integrato

Aggiunto un riquadro dinamico e accattivante nella pagina principale del launcher che mostra:

#### 📢 **Sistema News dal Database**
- Recupero automatico messaggi dalla tabella `Employee.dbo.News`
- **Priorità Messaggi Mandatory**: 
  - Messaggi con `IsMandatory = 1` hanno priorità assoluta
  - Se presenti, vengono mostrati SOLO questi
  - Header colorato arancione/rosso per evidenziare urgenza
- **Filtraggio Automatico per Date**:
  - Mostra solo messaggi attivi: `StartNews <= Data Attuale <= EndNews`
  - Messaggi scaduti automaticamente nascosti
- **Rotazione Automatica**:
  - Loop continuo tra messaggi multipli
  - Intervallo: 8 secondi per messaggio
  - Animazioni fade smooth
  - Indicatore contatore: "1 / 3"
- **Informazioni Visualizzate**:
  - Testo del messaggio
  - Nome publisher (firma)
  - Contatore messaggi

#### 🖼️ **Slideshow Immagini**
- Attivazione automatica quando non ci sono news attive
- **Filtro Nomi File**: Solo immagini che iniziano con 'X' (es: `X_evento.jpg`)
- **Formati Supportati**: JPG, JPEG, PNG, GIF, BMP, WEBP
- **Rotazione Automatica**:
  - Intervallo: 5 secondi per immagine
  - Animazioni fade smooth
  - Contatore immagini
- **Directory**: `Images/` nella root del progetto

#### 🎨 **Design Accattivante**
- Riquadro posizionato nella seconda riga dei bottoni
- Bordo colorato blu (#667eea)
- Header con gradiente dinamico:
  - Blu/Viola per messaggi normali
  - Arancione/Rosso per messaggi mandatory
- Icona animata con effetto bounce (📢)
- Transizioni smooth tra contenuti
- Spinner di caricamento elegante
- Responsive design per tutti i dispositivi

## 🔧 Modifiche Tecniche

### Backend (app.py)

#### Nuovi Endpoint API

1. **GET `/api/news`**
   - Recupera news attive dal database
   - Separa messaggi mandatory da normali
   - Filtra per date correnti
   - Ordina per priorità e data

2. **GET `/api/slideshow-images`**
   - Recupera lista immagini dalla directory `Images`
   - Filtra solo file che iniziano con 'X'
   - Supporta multiple estensioni immagine

3. **GET `/images/<filename>`**
   - Serve immagini dalla directory `Images`
   - Gestione errori per file non trovati

### Frontend

#### HTML (templates/launcher.html)
- Aggiunto riquadro `news-slideshow-container`
- Tre stati visualizzabili:
  - News display (messaggi database)
  - Slideshow display (immagini)
  - Loading display (caricamento)
- Struttura semantica e accessibile

#### JavaScript
- Sistema di inizializzazione automatica
- Gestione priorità: News → Slideshow → Nessun contenuto
- Funzioni di rotazione con interval management
- Animazioni fade per transizioni smooth
- Gestione errori robusta

#### CSS (static/css/launcher.css)
- Nuove classi per news/slideshow container
- Animazioni keyframe:
  - `bounce` per icona news
  - `spin` per loading spinner
- Stili responsive
- Gradienti dinamici
- Effetti hover e transizioni

## 📊 Database

### Tabella Richiesta: `Employee.dbo.News`

```sql
CREATE TABLE [Employee].[dbo].[News] (
    [NewId] INT IDENTITY(1,1) PRIMARY KEY,
    [EmployeerId] INT NULL,
    [StartNews] DATETIME NOT NULL,
    [EndNews] DATETIME NOT NULL,
    [News] NVARCHAR(MAX) NOT NULL,
    [Publisher] NVARCHAR(255) NOT NULL,
    [IsMandatory] BIT NOT NULL DEFAULT 0
)
```

## 📝 Documentazione

### Nuovo File: `GUIDA_NEWS_SLIDESHOW.md`
Guida completa che include:
- Panoramica funzionalità
- Struttura database
- Esempi SQL per inserimento news
- Gestione immagini slideshow
- Configurazione tecnica
- Troubleshooting
- Best practices

## 💡 Esempi di Utilizzo

### Inserire un Messaggio Normale
```sql
INSERT INTO [Employee].[dbo].[News] 
    ([StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    ('2026-01-03 08:00:00', '2026-01-10 18:00:00', 
     'Ricordiamo a tutti i dipendenti che venerdì 10 gennaio ci sarà la riunione mensale alle ore 14:00.',
     'Dipartimento HR', 0)
```

### Inserire un Messaggio Urgente
```sql
INSERT INTO [Employee].[dbo].[News] 
    ([StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    ('2026-01-03 00:00:00', '2026-01-03 23:59:59', 
     '⚠️ ATTENZIONE: Oggi pomeriggio dalle 14:00 alle 16:00 il sistema sarà in manutenzione.',
     'IT Department', 1)
```

### Aggiungere Immagini allo Slideshow
1. Rinominare immagini con prefisso 'X': `X_evento.jpg`
2. Copiare in directory `Images/`
3. Refresh pagina launcher

## 🎯 Caratteristiche Chiave

### Priorità e Intelligenza
- ✅ Messaggi mandatory hanno priorità assoluta
- ✅ Filtraggio automatico per date
- ✅ Fallback intelligente: News → Slideshow → Nessun contenuto
- ✅ Gestione errori robusta

### User Experience
- ✅ Animazioni fluide e professionali
- ✅ Design accattivante e colorato
- ✅ Indicatori chiari (contatori)
- ✅ Responsive per tutti i dispositivi
- ✅ Non interferisce con funzionalità esistenti

### Manutenibilità
- ✅ Codice modulare e ben documentato
- ✅ Configurazione semplice (intervalli modificabili)
- ✅ Log dettagliati per debugging
- ✅ Guida completa per amministratori

## 🔒 Compatibilità

### Nessun Impatto su Funzionalità Esistenti
- ✅ Tutti i bottoni funzionano normalmente
- ✅ Generazione certificati: OK
- ✅ Richieste assenza: OK
- ✅ Report assenze: OK
- ✅ Verifica stato: OK
- ✅ Layout responsive preservato
- ✅ Performance non impattate

## 📦 File Modificati

### Backend
- `app.py` - Aggiunti 3 nuovi endpoint API

### Frontend
- `templates/launcher.html` - Aggiunto riquadro news/slideshow + JavaScript
- `static/css/launcher.css` - Aggiunti stili per news/slideshow

### Documentazione
- `GUIDA_NEWS_SLIDESHOW.md` - Nuova guida completa
- `RELEASE_NOTES_v2.2.0.md` - Questo file

## 🧪 Testing

### Scenari Testati
- ✅ Nessuna news, nessuna immagine → Mostra "Nessun contenuto"
- ✅ Nessuna news, immagini presenti → Mostra slideshow
- ✅ News normali presenti → Mostra news in loop
- ✅ News mandatory presenti → Mostra SOLO mandatory
- ✅ Mix news mandatory + normali → Mostra SOLO mandatory
- ✅ News scadute → Non visualizzate
- ✅ Immagini senza prefisso X → Ignorate
- ✅ Immagini con prefisso X → Incluse nello slideshow
- ✅ Transizioni tra messaggi → Smooth fade
- ✅ Responsive mobile → Layout corretto

## 🚀 Deploy

**Repository GitHub**: https://github.com/glctesta/kiosk-hr-adeverente  
**Branch**: main  
**Versione**: 2.2.0

## 📋 Prossimi Passi

### Per Utilizzare il Sistema

1. **Creare tabella News** (se non esiste):
   ```sql
   -- Eseguire script SQL fornito nella guida
   ```

2. **Aggiungere messaggi**:
   ```sql
   -- Usare esempi SQL dalla guida
   ```

3. **Aggiungere immagini slideshow**:
   - Rinominare con prefisso 'X'
   - Copiare in `Images/`

4. **Testare**:
   - Aprire pagina launcher
   - Verificare visualizzazione news/slideshow

## 📞 Supporto

Per problemi o domande:
- **Email**: gianluca.testa@vandewiele.com
- **GitHub Issues**: https://github.com/glctesta/kiosk-hr-adeverente/issues
- **Documentazione**: Consultare `GUIDA_NEWS_SLIDESHOW.md`

---

**Sviluppato da**: GTMC (Gianluca Testa)  
**Per**: Vandewiele Romania  
**Data**: 2026-01-03
