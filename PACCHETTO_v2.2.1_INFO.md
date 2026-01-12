# 📦 PACCHETTO DEPLOYMENT KIOSK HR v2.2.1

**Data Creazione**: 12 Gennaio 2026, 13:58  
**Nome Pacchetto**: `Kiosk_HR_v2.2.1_20260112_135838.zip`  
**Dimensione**: 2.9 MB  
**Tipo**: Hotfix Critico

---

## 🔴 **MOTIVO DEL RILASCIO**

### Hotfix Critico: Stampa PDF
Risolto bug **CRITICO** che causava la stampa del codice grezzo dei PDF invece dei documenti formattati.

**Problema**: Tutti i report PDF (certificati, report assenze, report mensili) venivano stampati come testo interno del PDF invece del documento formattato.

**Risoluzione**: Modificato `pdf_printer.py` per utilizzare il metodo corretto di stampa Windows (`System.Diagnostics.Process` con verbo `print`).

---

## 📋 **CONTENUTO DEL PACCHETTO**

### File Applicazione Python (20 moduli)
- ✅ `app.py` - Server Flask principale
- ✅ `absence_report.py` - Generatore report assenze
- ✅ `absence_request.py` - Gestione richieste assenza
- ✅ `badge_reader.py` - Lettura badge RFID
- ✅ `certificate_generator.py` - Generatore certificati/adeverințe
- ✅ `config_manager.py` - Gestione configurazione
- ✅ `db_connection.py` - Connessione database
- ✅ `digital_signature.py` - Firma digitale PDF
- ✅ `email_connector.py` - Invio email
- ✅ `kiosk_request_logger.py` - **NUOVO** - Logging utilizzo kiosk
- ✅ `offline_logger.py` - **NUOVO** - Logging offline
- ✅ `pdf_printer.py` - **AGGIORNATO CON FIX** - Stampa PDF
- ✅ `pdf_digital_signer.py` - Firma digitale avanzata
- ✅ `printer_keepalive.py` - Gestione stampante
- ✅ `rfid_reader.py` - Driver RFID
- ✅ `service_kiosk_reports.py` - **NUOVO** - Servizio report mensili
- ✅ `setup.py` - Configurazione iniziale
- ✅ `update_signature.py` - Aggiornamento firme
- ✅ `utils.py` - Utility varie
- ✅ `windows_cert_signer.py` - Firma con certificati Windows
- ✅ `requirements.txt` - Dipendenze Python

### Templates HTML (5 file)
- `index.html` - Pagina certificati
- `absence.html` - Pagina report assenze
- `request.html` - Pagina richieste assenza
- `check.html` - Verifica stato richieste
- `launcher.html` - Menu principale launcher

### File Statici
- **CSS**: Stili per tutte le pagine
- **JavaScript**: Logic frontend, network monitor, RFID reader
- **Immagini**: Logo aziendale, immagini slideshow (X* e S*)
- **Font**: DejaVuSans.ttf, DejaVuSans-Bold.ttf (supporto caratteri rumeni)

### Script di Deployment
- ✅ `INSTALLA.bat` - Installazione automatica ambiente virtuale
- ✅ `START_APP.bat` - Avvio server Flask
- ✅ `START_SISTEMA_KIOSK.bat` - Avvio sistema completo
- ✅ `START_KIOSK_REPORTS_SERVICE.bat` - **NUOVO** - Avvio servizio report
- ✅ `AGGIORNA_FIRMA.bat` - Aggiornamento firma digitale

### Documentazione Completa (15 file)
- ✅ `README.md` - Overview del progetto
- ✅ `RELEASE_NOTES_v2.2.1.md` - **NUOVO** - Note di rilascio v2.2.1
- ✅ `FIX_STAMPA_PDF_CODICE_GREZZO.md` - **NUOVO** - Dettagli fix critico
- ✅ `DEPLOYMENT.md` - Guida deployment
- ✅ `INSTALLAZIONE_MANUALE.md` - Installazione manuale
- ✅ `GUIDA_RAPIDA.md` - Quick start
- ✅ `GUIDA_RFID.md` - Configurazione RFID
- ✅ `GUIDA_KIOSK_FULLSCREEN.md` - Modalità kiosk fullscreen
- ✅ `GUIDA_NEWS_SLIDESHOW.md` - Sistema news e slideshow
- ✅ `CONFIGURAZIONE_RETE.md` - Setup rete
- ✅ `STAMPA_AUTOMATICA.md` - Configurazione stampa
- ✅ `KIOSK_MONITORING_SYSTEM.md` - Sistema monitoraggio
- ✅ `RELEASE_NOTES_v2.2.0.md` - Note versione precedente
- ✅ `RELEASE_NOTES_v2.1.1.md` - Note versione precedente

### Risorse
- `logo.png` - Logo aziendale Vandewiele
- `GTMC.png` - Logo GTMC
- `IDReader.dll` - Driver lettore RFID (se presente)
- `print_config.json` - Configurazione stampante
- File di crittografia (`.enc`, `.key`)

---

## 🚀 **ISTRUZIONI DEPLOYMENT**

### 1. Preparazione
```batch
# Trasferire il file ZIP sulla macchina target
# Estrarre in: C:\Kiosk_HR\
```

### 2. Installazione
```batch
# Aprire PowerShell/CMD come Amministratore
cd C:\Kiosk_HR

# Eseguire installazione
INSTALLA.bat

# Attendere completamento (creazione venv, installazione dipendenze)
```

### 3. Configurazione
```batch
# Configurare database e email
python setup.py

# Inserire:
# - Server SQL Server
# - Nome database: Employee
# - Credenziali SQL
# - Server SMTP e credenziali email
```

### 4. Avvio
```batch
# Avvio manuale per test
START_APP.bat

# Verifica: http://localhost:5000

# Avvio sistema completo (app + servizio report)
START_SISTEMA_KIOSK.bat
```

---

## 🔄 **UPGRADE DA v2.2.0**

Se hai già installato la versione 2.2.0, puoi fare un upgrade rapido:

### Opzione A: Sostituzione File Singolo (Solo Fix)
```batch
# Ferma il servizio attuale
# Sostituisci solo: pdf_printer.py
# Riavvia con: START_APP.bat
```

### Opzione B: Installazione Completa
```batch
# Ferma il servizio attuale
# Backup directory corrente
# Estrai nuovo pacchetto
# Mantieni file di configurazione (.enc, .key, print_config.json)
# Avvia con: START_APP.bat
```

**IMPORTANTE**: Non è necessario reinstallare Python o le dipendenze se provieni da v2.2.0.

---

## ✅ **VERIFICA INSTALLATION**

Dopo l'installazione, verifica che tutto funzioni:

### 1. Test Server
```batch
# Apri browser
http://localhost:5000

# Verifica che appaia il launcher con i servizi
```

### 2. Test Stampa PDF (CRITICO)
```batch
# Accedi a: http://localhost:5000/certificati
# Genera un certificato di prova
# Verifica che la stampa mostri il documento formattato
# NON deve mostrare codice grezzo (tipo /Type /Pages, ecc.)
```

### 3. Test Database
```batch
# Verifica connessione database nel log
type app_debug.log | findstr "Connessione"
```

### 4. Test News Sistema
```batch
# Verifica slideshow e news nel launcher
# Controlla che le immagini scorrano
```

---

## 📊 **MONITORAGGIO**

### Log Files
- `app_debug.log` - Log runtime applicazione
- `logs/offline_events.log` - Log eventi offline (se presente)

### Comandi Utili
```batch
# Visualizza log in tempo reale
powershell Get-Content app_debug.log -Wait -Tail 50

# Verifica processi attivi
tasklist | findstr python

# Test connessione database
python -c "from db_connection import *; print(DatabaseConnection(ConfigManager()).test_connection())"
```

---

## 🐛 **TROUBLESHOOTING**

### Problema: Stampa PDF mostra codice grezzo
**Causa**: Vecchia versione di pdf_printer.py  
**Soluzione**: Assicurati di usare v2.2.1

### Problema: Errore connessione database
**Causa**: Credenziali errate o server non raggiungibile  
**Soluzione**: Riesegui `python setup.py` per configurare

### Problema: News non si caricano
**Causa**: Tabella News non presente o vuota  
**Soluzione**: Verifica esistenza `Employee.dbo.News` nel database

### Problema: RFID non funziona
**Causa**: DLL non presente o driver non installato  
**Soluzione**: Copia `IDReader.dll` e installa driver RFID

---

## 📞 **SUPPORTO**

Per problemi o domande:
1. Consulta `app_debug.log` per errori
2. Leggi `FIX_STAMPA_PDF_CODICE_GREZZO.md` per dettagli tecnici
3. Verifica `TROUBLESHOOTING` nella documentazione
4. Contatta team GTMC

---

## 📈 **STATISTICHE PACCHETTO**

- **File Python**: 20 moduli
- **Templates HTML**: 5 pagine
- **File JavaScript**: 3 script
- **File CSS**: 4 stylesheet
- **Documentazione**: 15 guide
- **Script Deployment**: 5 batch files
- **Totale file**: ~60+
- **Dimensione compressa**: 2.9 MB

---

## 🎯 **SVILUPPI FUTURI**

Pianificati per v2.3.0:
- Dashboard monitoraggio utilizzo kiosk in tempo reale
- Report statistici mensili visuali
- Ottimizzazione performance stampa batch
- Sistema cache intelligente per report frequenti

---

**Pacchetto creato con successo!** ✅  
**By GTMC - Advanced IT Solutions**  
**Data**: 12 Gennaio 2026, 13:58
