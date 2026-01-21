# 🚀 KIOSK HR - RELEASE v2.3.3
**Data rilascio**: 21 Gennaio 2026  
**Versione**: 2.3.3  
**Codename**: "Partial Absence & Silent Print"

---

## 🎯 NOVITÀ PRINCIPALI

### 1. ✨ Campi Orari per Assenze Parziali (NUOVO)
Supporto completo per richieste di assenza con orari specifici (permessi ore, uscite anticipate, ecc.)

**Caratteristiche**:
- Campi "Dalle ore" e "Fino alle ore" appaiono automaticamente per tipi `IsConsideredEntireDay = 0`
- Sincronizzazione automatica data fine = data inizio
- Validazione range orario (min 30 minuti, range 07:30-22:30)
- Salvataggio `FromTime` e `ToTime` in database
- Visualizzazione orari in email e PDF di conferma
- Skip validazione giorni lavorativi per assenze orarie

**Files modificati**:
- `templates/request.html` - Campi HTML orari
- `static/js/request.js` - Logica validazione e submit
- `static/js/time-fields.js` - Modulo gestione orari (**NUOVO**)
- `app.py` - Endpoint e invio email con orari
- `absence_request.py` - PDF con visualizzazione orari

### 2. 🖨️ Stampa Silenziosa v2.3.2
Sistema di stampa 100% silenzioso con SumatraPDF.

**Miglioramenti**:
- SumatraPDF come metodo primario (già installato su molti PC)
- Fallback automatico a PDFtoPrinter se necessario
- Controllo `Printable = 1` prima di stampare news
- Formattazione PDF news migliorata (split paragrafi, spaziatura)

**Files modificati**:
- `pdf_printer.py` - Logica stampa SumatraPDF
- `templates/launcher.html` - Controllo Printable

---

## 📦 CONTENUTO PACCHETTO

```
Kiosk_HR_Deploy_v2.3.3_YYYYMMDD_HHMMSS.zip
├── app.py (modificato)
├── absence_request.py (modificato)
├── pdf_printer.py (modificato)
├── templates/
│   ├── request.html (modificato)
│   └── launcher.html (modificato)
├── static/
│   ├── js/
│   │   ├── request.js (modificato)
│   │   └── time-fields.js (NUOVO)
│   └── css/
│       └── styles.css
└── Documentazione/
    ├── DEPLOY.md
    ├── STATUS_CAMPI_ORARI_FINALE.md
    └── GUIDA_PDFTOPRINTER.md
```

---

## 🔧 INSTALLAZIONE

### 1. Backup
```bash
# Backup directory corrente
Copy-Item -Path "C:\Path\To\Kiosk" -Destination "C:\Path\To\Kiosk_BACKUP_$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

### 2. Deploy
```bash
# Estrai ZIP
Expand-Archive -Path "Kiosk_HR_Deploy_v2.3.3_*.zip" -DestinationPath "C:\Path\To\Kiosk" -Force

# Riavvia servizio/app
# (Metodo dipende dal setup)
```

### 3. Verifica
- ✅ Apri http://localhost:5000
- ✅ Testa richiesta assenza con tipo "Permesso" (IsConsideredEntireDay=0)
- ✅ Verifica che campi orari appaiano
- ✅ Invia richiesta e controlla email

---

## ✅ TEST ESEGUITI

| Feature | Status | Note |
|---------|--------|------|
| Campi orari appaiono | ✅ OK | Solo per IsConsideredEntireDay=0 |
| Sincronizzazione date | ✅ OK | Data fine = data inizio |
| Validazione orari | ✅ OK | Min 30 min, range 07:30-22:30 |
| Submit richiesta | ✅ OK | Dati inviati correttamente |
| Salvataggio DB | ✅ OK | FromTime/ToTime salvati |
| Email con orari | ✅ OK | Visualizzazione condizionale |
| PDF con orari | ✅ OK | Layout dinamico |
| Check duplicati | ✅ OK | Funziona correttamente |
| Stampa News | ✅ OK | SumatraPDF silenziosa |

---

## 🐛 BUGFIX

- ✅ Risolto conflitto endpoint duplicato `/api/request-types`
- ✅ Corretto errore sintassi JavaScript in `request.js`
- ✅ Fix validazione working days per assenze parziali
- ✅ Popolamento corretto `state.dateStart/dateEnd`

---

## 📋 DATABASE

**Campi utilizzati (già esistenti)**:
- `AbsenceRequestes.FromTime` (time)
- `AbsenceRequestes.ToTime` (time)
- `RequestType.IsConsideredEntireDay` (bit)

**Nessuna modifica DB necessaria!**

---

## 🔐 SICUREZZA

- ✅ Validazione input lato client e server
- ✅ Parametrizzazione SQL (no SQL injection)
- ✅ Check duplicati richieste
- ✅ Validazione range orario

---

## 📞 SUPPORTO

**Documentazione completa**:
- `STATUS_CAMPI_ORARI_FINALE.md` - Guida feature orari
- `GUIDA_PDFTOPRINTER.md` - Guida stampa
- `DEPLOY.md` - Procedura deploy standard

**Test workflow**:
1. Badge → Tipo permesso → Campi orari appaiono
2. Compila date + orari (es: 09:00-12:00)
3. Submit → Email inviata con orari
4. Manager approva/rifiuta

---

## 🎉 CONCLUSIONI

**Release production-ready al 100%!**

- ✅ Feature orari assenza completamente funzionante
- ✅ Stampa silenziosa ottimizzata
- ✅ Testato e validato
- ✅ Documentazione completa
- ✅ Zero breaking changes

**Pronto per deploy immediato!** 🚀

---

*Versione 2.3.3 - Sistema Kiosk HR - Vandewiele Italia*  
*Copyright © 2026 - Tutti i diritti riservati*
