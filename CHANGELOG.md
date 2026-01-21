# Changelog - Kiosk HR Adeverente

Tutte le modifiche rilevanti al progetto saranno documentate in questo file.

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
