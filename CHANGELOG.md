# Changelog - Kiosk HR Adeverente

Tutte le modifiche rilevanti al progetto saranno documentate in questo file.

## [2.3.7] - 2026-07-20

### ⌨️ Timeout adattivo per inserimento badge manuale
- Rilevamento automatico scansione RFID vs digitazione manuale tramite intervallo tra caratteri
- Digitazione manuale (>150ms tra caratteri): attesa **2000ms** (era 500ms per tutti)
- Scansione RFID (burst veloce): attesa **500ms** invariata

### 💾 Badge persistente durante la sessione
- Badge salvato in `sessionStorage` dopo validazione
- "Generează altă adeverință" mantiene il badge, resetta solo il form
- "Resetează" e timeout inattività cancellano la sessione e tornano alla home
- Home page (`launcher.html`) pulisce automaticamente la sessione al caricamento

---

## [2.3.5] - 2026-04-17


### 🖨️ Stampa client-side (fix accesso da rete locale)

- La stampa dei documenti (certificato, cerere di assenza, raport istoric absențe)
  ora avviene sul browser del client che ha fatto la richiesta, non più sul PC
  dove gira il server.
- Nuovo flusso: al termine della generazione appare il bottone
  **"Printează (15)"** con countdown. Click → stampa client-side via iframe
  nascosto (kiosk silenzioso grazie a `--kiosk-printing`, PC remoti con dialog
  standard del browser). Se non cliccato entro 15s il PDF viene eliminato.

### 🔧 Modifiche tecniche

- `app.py`: rimossa stampa server-side da `/api/generate-certificate`,
  `/api/generate-absence-report`, `/api/submit-absence-request`.
- `app.py`: sostituito endpoint `/api/do-print` con `/api/delete-pdf/<filename>`
  (cleanup PDF con protezione path traversal).
- `static/js/app.js`, `request.js`, `absence.js`: riscritto `handlePrint` con
  stampa via iframe + countdown 15s.
- `/api/news/print` e `printer_keepalive.py` invariati (funzioni kiosk-interne).

## [2.3.0] - 2026-01-21

### ✨ Novità
- **Sistema News Completo**: Integrazione totale del sistema news nel launcher
  - Display dinamico con auto-refresh ogni 30-60 secondi (basato su lunghezza testo)
  - Scorrimento verticale automatico per testi lunghi
  - Click sul frame news per stampa immediata
  
### 🖨️ Stampa News
- **Stampa silenziosa completamente funzionante**:
  - Metodo Windows `printto` nativo (NO popup Adobe)
  - Generazione PDF con logo aziendale
  - Metadati completi in **rumeno**:
    - "Comunicare Companiei" (titolo)
    - "Data:", "Publicat de:", "ID Știri:" (campi)
    - "Tipărit la ... ora ... de ..." (footer)
  - Spaziatura migliorata tra etichette e valori (70mm)
  - Font dimensione 20 per contenuto
  - Registrazione automatica in `KiosRequestes` con flag `Executed`
  - Stampante target: "Color Birou" (configurabile)

### 🔧 Miglioramenti Tecnici
- **pdf_printer.py**: 
  - Codice semplificato da ~300 a ~130 righe
  - Rimosso doppio escape backslash (bugfix)
  - Eliminati metodi complessi (GhostScript, Out-Printer, .NET)
  - Metodo unico robusto: `ProcessStartInfo` con verbo `printto`
  
- **app.py** (`/api/news/print`):
  - PDF generato con formato A4, word-wrap automatico
  - Gestione multi-pagina se necessario
  - Logo aziendale in header
  - Footer con timestamp e nome kiosk

### 🌐 Localizzazione
- Tutti i campi PDF news tradotti in rumeno
- Mantenuta compatibilità con sistema esistente

### 📊 API
- `GET /api/news` - Recupera news attive ordinate per priorità/data
- `POST /api/news/print` - Stampa news specifica (JSON: `newsId`, `newsText`, `newsDate`, `publisher`)
- Response JSON completo: `{pdf_generated, printed, printer_available, success, message}`

### 🐛 Bug Fix
- Risolto errore "filename, directory name, or volume label syntax is incorrect"
- Eliminati problemi con path Windows contenenti backslash
- Stampa funziona anche senza GhostScript o SumatraPDF installati

## [2.2.0] - 2026-01-20

### Modifiche Precedenti
- Sistema richieste assenze
- Gestione adeverințe
- Firma digitale con CertSign
- Sistema email notifiche
- Printer keep-alive service

---

## Formato
Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
