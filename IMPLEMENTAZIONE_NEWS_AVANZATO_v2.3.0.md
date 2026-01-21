# Sistema News Avanzato - Kiosk HR v2.3.0
## Refresh Dinamico, Auto-Scrolling e Stampa

---

## ✅ Implementazione Completata!

Tutte le funzionalità richieste sono state implementate nel progetto **Adeverente (Kiosk HR)**:

### 🎯 Funzionalità Implementate

1. ✅ **Refresh Dinamico Basato su Lunghezza Testo**
   - Breve (< 200 caratteri): **8 secondi**
   - Medio (200-500 caratteri): **12 secondi**
   - Lungo (> 500 caratteri): **20+ secondi**

2. ✅ **Auto-Scrolling per Testi Lunghi**
   - Attivato automaticamente quando il testo supera l'altezza del frame
   - Velocità: 30 pixel/secondo (lento e leggibile)
   - Pausa di 2 secondi al termine prima di tornare all'inizio
   - Il refresh avviene **solo DOPO** il completamento dello scrolling

3. ✅ **Stampa su Click del Frame**
   - Click sul frame news → stampa immediata
   - PDF professionale con:
     - Logo aziendale
     - Data di pubblicazione
     - Publisher
     - ID News
     - **Testo completo con font 20px**
     - Footer con data/ora e nome kiosk

4. ✅ **Registrazione Richieste in Database**
   - Ogni stampa registrata in `[Employee].[dbo].[KiosRequestes]`
   - Campo `RequestWhat`: `'Stampa News [ID]'`
   - Campo `Executed`: `1` dopo stampa completata

---

## 📁 File Modificati

### Backend
✅ **`app.py`** - Aggiunto endpoint `/api/news/print`
- Registra richiesta in `KiosRequestes`
- Genera PDF con ReportLab
- Logo aziendale, metadati, font 20
- Stampa automatica su stampante configurata

### Frontend
✅ **`templates/launcher.html`** - Modificato JavaScript:
- Funzione `displayNews()` completamente riscritta
- Refresh dinamico basato su lunghezza testo
- Auto-scrolling fluido per testi lunghi
- Click handler per stampa
- Feedback visuale (flash verde) dopo stampa

---

## 🚀 Come Testare

### 1. Inserisci News di Test

```sql
USE Employee
GO

-- News BREVE (test refresh 8 sec)
INSERT INTO [dbo].[News] 
VALUES (2, GETDATE(), DATEADD(DAY, 7, GETDATE()), 
        'Domani chiusura mensa per pulizie straordinarie.', 
        'Facility Manager', 0)

-- News MEDIA (test refresh 12 sec)
INSERT INTO [dbo].[News] 
VALUES (2, GETDATE(), DATEADD(DAY, 7, GETDATE()), 
        'Attenzione: Giovedì 23 gennaio riunione generale alle ore 10:00 in sala conferenze. La partecipazione è obbligatoria per tutti i dipendenti. Saranno discussi i nuovi obiettivi trimestrali e le procedure di sicurezza aggiornate.', 
        'HR Department', 0)

-- News LUNGA (test scrolling + refresh 20+ sec)
INSERT INTO [dbo].[News] 
VALUES (2, GETDATE(), DATEADD(DAY, 7, GETDATE()), 
        'COMUNICAZIONE IMPORTANTE - AGGIORNAMENTO PROCEDURE

A partire dal prossimo mese entreranno in vigore le nuove procedure di sicurezza:

1. BADGE E ACCESSI
- Obbligo di esposizione badge in area visibile
- Registrazione ingresso/uscita obbligatoria tramite tornelli
- Accesso aree produttive solo con DPI completi

2. FORMAZIONE OBBLIGATORIA
- Corso sicurezza: 15 febbraio ore 09:00
- Corso qualità ISO 9001: 22 febbraio ore 14:00
- Corso primo soccorso: 1 marzo ore 10:00

3. NUOVI ORARI MENSA
- Primo turno: 12:00 - 13:00
- Secondo turno: 13:00 - 14:00
- Pausa caffè: 10:00 e 15:30

Per informazioni contattare HR Department.', 
        'Management', 0)
GO
```

### 2. Avvia/Riavvia l'Applicazione

```powershell
cd C:\Users\gtesta\PythonProjetcs\Python\Adeverente
python app.py
```

### 3. Apri il Browser

Vai a: `http://localhost:5000`

### 4. Verifica Funzionalità

#### Test Refresh Dinamico
- News breve: cambia dopo **8 secondi**
- News media: cambia dopo **12 secondi**
- News lunga: cambia dopo **20+ secondi** (+ tempo scrolling)

#### Test Auto-Scrolling
- La news lunga dovrebbe **scrollare automaticamente**
- Velocità lenta e leggibile (30px/sec)
- Al termine, pausa 2 sec e torna all'inizio
- Solo dopo, passa alla news successiva

#### Test Stampa
1. **Click** sul frame della news
2. Frame diventa **verde** per 1 secondo (feedback)
3. PDF viene generato e stampato
4. Verifica nel database:

```sql
SELECT TOP 10 *
FROM [Employee].[dbo].[KiosRequestes]
WHERE RequestWhat LIKE 'Stampa News%'
ORDER BY RequestDate DESC
```

---

## 🔧 Configurazione

### Stampante
Assicurati che sia configurata una stampante di default nel sistema.

### Logo
Il file `logo.png` deve trovarsi nella root del progetto Adeverente.

### Personalizzazioni

Nel file `launcher.html`, puoi modificare:

```javascript
// Soglie lunghezza testo (linea ~340)
if (textLength > 500) {
    refreshTime = 20000; // Modifica qui per testi lunghi
} else if (textLength > 200) {
    refreshTime = 12000; // Modifica qui per testi medi
}
// Default: 8000 (8 secondi) per testi brevi

// Velocità scrolling (linea ~366)
const scrollSpeed = 30; // pixel/secondo
// Aumenta per scrolling più veloce, diminuisci per più lento
```

Nel file `app.py`, puoi modificare:

```python
# Font size testo (linea ~1485 circa)
c.setFont(font_name, 20)  # Modifica da 20 a valore desiderato

# Nome kiosk per registrazione (linea ~1406)
room_name = 'Kiosk HR'  # Personalizza nome
```

---

## 📊 Tabella Database

### [Employee].[dbo].[KiosRequestes]

Esempio record dopo stampa:

| Campo | Valore Esempio |
|-------|----------------|
| KiosRequestId | 123 (auto-increment) |
| RequestDate | 2026-01-21 07:30:45 |
| IpRequest | 192.168.1.100 |
| RequestBy | Kiosk HR |
| RequestWhat | Stampa News 5 |
| Executed | 1 |

---

## 🎨 Comportamento Visivo

### Indicatore Stampa
- **Cursore**: puntatore (pointer) sul frame news
- **Tooltip**: "🖨️ Clicca per stampare"
- **Feedback**: flash verde dopo stampa riuscita

### Console Log
Durante il funzionamento, nella console del browser (F12) vedrai:

```
⏱️ News 1: Refresh in 8 secondi (Lunghezza: 45 caratteri, Scrolling: false)
⏱️ News 2: Refresh in 12 secondi (Lunghezza: 250 caratteri, Scrolling: false)
📜 Testo lungo rilevato (850px > 300px), attivo scrolling...
⏱️ News 3: Refresh in 28 secondi (Lunghezza: 580 caratteri, Scrolling: true)
🖨️ Click su news 3, avvio stampa...
✅ News stampata con successo
```

---

##  🔍 Troubleshooting

### Le news non si vedono
1. Verifica che ci siano news attive nel database
2. Controlla console browser (F12) per errori
3. Verifica connessione database in `app_debug.log`

### Lo scrolling non parte
1. Il testo deve essere sufficientemente lungo
2. Verifica altezza contenitore in CSS
3. Controlla console per log "Testo lungo rilevato"

### La stampa non funziona
1. Verifica che sia configurata una stampante di default
2. Controlla che `logo.png` esista
3. Verifica log server per errori ReportLab
4. Controlla che la directory `temp/` esista

### Il PDF viene generato ma non stampato
1. Verifica funzione `get_default_printer()` in `pdf_printer.py`
2. Controlla `print_config.json` per configurazione stampante
3. Verifica permessi Windows per la stampante

---

## 📝 Query Utili

### News attive correnti
```sql
SELECT NewId, News, Publisher, LEN(News) as Lunghezza
FROM [Employee].[dbo].[News]
WHERE GETDATE() BETWEEN StartNews AND EndNews
ORDER BY IsMandatory DESC, StartNews ASC
```

### Stampe effettuate oggi
```sql
SELECT 
    RequestDate,
    RequestWhat,
    IpRequest,
    CASE Executed WHEN 1 THEN 'Completata' ELSE 'In attesa' END as Stato
FROM [Employee].[dbo].[KiosRequestes]
WHERE RequestWhat LIKE 'Stampa News%'
  AND CAST(RequestDate AS DATE) = CAST(GETDATE() AS DATE)
ORDER BY RequestDate DESC
```

### News più stampate
```sql
SELECT 
    SUBSTRING(RequestWhat, 13, LEN(RequestWhat)) as NewsId,
    COUNT(*) as NumeroStampe
FROM [Employee].[dbo].[KiosRequestes]
WHERE RequestWhat LIKE 'Stampa News%'
  AND Executed = 1
GROUP BY SUBSTRING(RequestWhat, 13, LEN(RequestWhat))
ORDER BY COUNT(*) DESC
```

---

## ✨ Miglioramenti Futuri Possibili

1. **Statistiche visualizzazione** - Tracciare views oltre alle stampe
2. **Immagini nelle news** - Supporto allegati
3. **Suoni notifica** - Audio per news mandatory
4. **Anteprima PDF** - Mostra PDF prima di stampare
5. **Multi-lingua** - Traduzioni automatiche

---

## 📞 Support

Per problemi o domande:
- Verificare log: `app_debug.log`
- Console browser (F12)
- Documentazione: `GUIDA_NEWS_SLIDESHOW.md`

---

**Versione**: 2.3.0  
**Data**: 21 Gennaio 2026  
**Progetto**: Kiosk HR (Adeverente)  
**Sviluppato da**: GTMC

🎉 **Implementazione Completata con Successo!**
