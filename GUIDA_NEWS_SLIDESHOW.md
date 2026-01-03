# Sistema News & Slideshow - Guida Utilizzo

## 📢 Panoramica

Il sistema News & Slideshow è integrato nella pagina principale del Kiosk HR e mostra automaticamente:
1. **Messaggi importanti** dalla tabella `Employee.dbo.News` (priorità)
2. **Slideshow immagini** dalla directory `Images` (fallback se non ci sono news)

## 🎯 Funzionalità

### Messaggi News

#### Priorità Messaggi
- **Messaggi Mandatory** (`IsMandatory = 1`): Hanno priorità assoluta
  - Se presenti, vengono mostrati SOLO questi
  - Header colorato in arancione/rosso per evidenziare l'urgenza
  - Utili per comunicazioni critiche (chiusure, emergenze, ecc.)

- **Messaggi Normali** (`IsMandatory = 0`): Mostrati solo se non ci sono mandatory
  - Header colorato in blu/viola
  - Per comunicazioni standard

#### Filtraggio per Date
- Il sistema mostra solo i messaggi attivi al momento corrente
- Filtro automatico: `StartNews <= Data Attuale <= EndNews`
- I messaggi scaduti non vengono visualizzati

#### Rotazione Messaggi
- Se ci sono più messaggi attivi, vengono mostrati in loop
- Intervallo di rotazione: **8 secondi** per messaggio
- Animazione fade smooth tra i messaggi
- Indicatore contatore: "1 / 3" (messaggio corrente / totale)

### Slideshow Immagini

#### Quando si Attiva
- Lo slideshow si attiva automaticamente quando **non ci sono news attive**
- Mostra le immagini presenti nella directory `Images`

#### Formati Supportati
- `.jpg` / `.jpeg`
- `.png`
- `.gif`
- `.bmp`
- `.webp`

#### Rotazione Immagini
- Intervallo: **5 secondi** per immagine
- Animazione fade smooth
- Contatore immagini: "1 / 5"

## 📊 Struttura Database

### Tabella: `Employee.dbo.News`

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

### Campi

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `NewId` | INT | ID univoco del messaggio |
| `EmployeerId` | INT | ID dipendente (opzionale, per future implementazioni) |
| `StartNews` | DATETIME | Data/ora inizio visualizzazione |
| `EndNews` | DATETIME | Data/ora fine visualizzazione |
| `News` | NVARCHAR(MAX) | Testo del messaggio |
| `Publisher` | NVARCHAR(255) | Nome di chi ha pubblicato il messaggio |
| `IsMandatory` | BIT | 1 = Priorità alta, 0 = Normale |

## 💡 Esempi di Utilizzo

### Esempio 1: Messaggio Normale

```sql
INSERT INTO [Employee].[dbo].[News] 
    ([StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    ('2026-01-03 08:00:00', '2026-01-10 18:00:00', 
     'Ricordiamo a tutti i dipendenti che venerdì 10 gennaio ci sarà la riunione mensile alle ore 14:00 in sala conferenze.',
     'Dipartimento HR', 0)
```

### Esempio 2: Messaggio Urgente (Mandatory)

```sql
INSERT INTO [Employee].[dbo].[News] 
    ([StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    ('2026-01-03 00:00:00', '2026-01-03 23:59:59', 
     '⚠️ ATTENZIONE: Oggi pomeriggio dalle 14:00 alle 16:00 il sistema sarà in manutenzione. Vi preghiamo di completare le vostre operazioni entro le 13:30.',
     'IT Department', 1)
```

### Esempio 3: Messaggio Multi-Giorno

```sql
INSERT INTO [Employee].[dbo].[News] 
    ([StartNews], [EndNews], [News], [Publisher], [IsMandatory])
VALUES 
    ('2026-01-06 00:00:00', '2026-01-12 23:59:59', 
     'Settimana della Sicurezza: dal 6 al 12 gennaio. Partecipate ai workshop sulla sicurezza sul lavoro. Iscrizioni aperte in bacheca.',
     'Safety Manager', 0)
```

### Esempio 4: Più Messaggi Contemporanei

```sql
-- Messaggio 1
INSERT INTO [Employee].[dbo].[News] 
VALUES ('2026-01-03 08:00:00', '2026-01-05 18:00:00', 
        'Nuova procedura per richieste ferie: utilizzare il nuovo modulo disponibile sul portale.',
        'HR Manager', 0)

-- Messaggio 2
INSERT INTO [Employee].[dbo].[News] 
VALUES ('2026-01-03 08:00:00', '2026-01-05 18:00:00', 
        'Ricordiamo che il parcheggio est sarà chiuso per lavori di manutenzione.',
        'Facility Manager', 0)

-- Questi due messaggi verranno mostrati in loop (8 secondi ciascuno)
```

## 🎨 Design e Animazioni

### Caratteristiche Visive

- **Header Gradiente**: 
  - Blu/Viola per messaggi normali
  - Arancione/Rosso per messaggi mandatory
  
- **Icona Animata**: 📢 con effetto bounce

- **Transizioni Smooth**: Fade in/out tra messaggi

- **Responsive**: Si adatta automaticamente a schermi diversi

- **Bordo Colorato**: Bordo blu che identifica il riquadro

## 📁 Gestione Immagini Slideshow

### Convenzione Nomi File

**IMPORTANTE**: Solo le immagini il cui nome inizia con la lettera **'X'** (maiuscola o minuscola) vengono incluse nello slideshow.

Esempi validi:
- ✅ `X_evento_aziendale.jpg`
- ✅ `x_natale_2025.png`
- ✅ `Xmas_party.jpg`
- ❌ `evento.jpg` (non inizia con X)
- ❌ `natale.png` (non inizia con X)

### Aggiungere Immagini

1. Rinominare le immagini con prefisso **'X'** (es: `X_immagine1.jpg`)
2. Copiare le immagini nella directory `Images` del progetto
3. Formati supportati: JPG, PNG, GIF, BMP, WEBP
4. Le immagini vengono caricate automaticamente al refresh della pagina

### Rimuovere Immagini

1. Eliminare i file dalla directory `Images`
2. Refresh della pagina per aggiornare lo slideshow

### Best Practices

- **Naming**: Usare nomi descrittivi dopo la X (es: `X_safety_week.jpg`)
- **Risoluzione consigliata**: 1920x1080 o 16:9 ratio
- **Dimensione file**: Max 2MB per immagine
- **Contenuto**: Immagini aziendali, eventi, celebrazioni, safety tips

## 🔧 Configurazione Tecnica

### Endpoint API

#### GET `/api/news`
Recupera news attive dal database

**Response:**
```json
{
    "success": true,
    "has_news": true,
    "news": [
        {
            "id": 1,
            "message": "Testo del messaggio",
            "publisher": "Nome Publisher",
            "is_mandatory": false,
            "start_date": "2026-01-03T08:00:00",
            "end_date": "2026-01-10T18:00:00"
        }
    ],
    "is_mandatory": false
}
```

#### GET `/api/slideshow-images`
Recupera lista immagini disponibili

**Response:**
```json
{
    "success": true,
    "images": [
        "/images/image1.jpg",
        "/images/image2.png"
    ]
}
```

### Parametri Configurabili

Nel file `launcher.html`, è possibile modificare:

```javascript
// Intervallo rotazione news (millisecondi)
newsInterval = setInterval(() => { ... }, 8000);  // 8 secondi

// Intervallo rotazione slideshow (millisecondi)
slideshowInterval = setInterval(() => { ... }, 5000);  // 5 secondi
```

## 🐛 Troubleshooting

### Le news non vengono visualizzate

1. **Verificare date**: Controllare che `StartNews <= Data Attuale <= EndNews`
2. **Controllare database**: Eseguire query manuale per verificare i dati
3. **Console browser**: Aprire F12 e controllare errori JavaScript
4. **Log server**: Verificare `app_debug.log` per errori di connessione

### Lo slideshow non funziona

1. **Verificare directory**: Assicurarsi che `Images` esista
2. **Verificare immagini**: Controllare che ci siano file con estensioni valide
3. **Permessi**: Verificare permessi di lettura sulla directory
4. **Console**: Controllare errori di caricamento immagini

### Messaggi mandatory non hanno priorità

1. **Verificare campo**: `IsMandatory` deve essere `1` (non `'1'` o `true`)
2. **Query SQL**: Controllare che il campo sia di tipo `BIT`

## 📞 Supporto

Per problemi o domande:
- **Email**: gianluca.testa@vandewiele.com
- **GitHub**: https://github.com/glctesta/kiosk-hr-adeverente

---

**Versione**: 2.2.0  
**Data**: 2026-01-03  
**Sviluppato da**: GTMC (Gianluca Testa)
