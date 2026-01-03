# 📦 PACCHETTO DEPLOYMENT KIOSK HR v2.2.0

**Data Creazione:** 03 Gennaio 2026 - 13:02:43  
**Nome File:** `Kiosk_HR_v2.2.0_20260103_130243.zip`  
**Dimensione:** 2.88 MB  
**Versione Applicazione:** 2.2.0

---

## ✅ PACCHETTO CREATO CON SUCCESSO!

Il pacchetto ZIP contiene **TUTTI** i file necessari per l'installazione completa del sistema Kiosk HR su una nuova macchina.

---

## 📋 CONTENUTO DEL PACCHETTO

### 🐍 Applicazione Python (16 file)
- `app.py` - **Applicazione principale Flask**
- `absence_report.py` - Generazione report assenze
- `absence_request.py` - Gestione richieste assenza
- `badge_reader.py` - Lettura badge RFID
- `certificate_generator.py` - Generazione certificati PDF
- `config_manager.py` - Gestione configurazioni
- `db_connection.py` - Connessione database
- `digital_signature.py` - Firma digitale documenti
- `email_connector.py` - Invio email
- `pdf_printer.py` - Stampa PDF
- `printer_keepalive.py` - Mantenimento stampante attiva
- `rfid_reader.py` - Driver RFID
- `setup.py` - Setup iniziale
- `update_signature.py` - Aggiornamento firme
- `utils.py` - Utilità varie
- `requirements.txt` - **Dipendenze Python**

### 🎨 Templates HTML (Directory `templates/`)
- `launcher.html` - Pagina principale kiosk
- `request.html` - Form richiesta assenza
- `check.html` - Verifica stato richieste
- `absences.html` - Riepilogo annuale assenze
- `news.html` - **Pagina News & Slideshow v2.2.0**

### 💅 Static Files (Directory `static/`)
- **CSS:** `styles.css`, `news.css`
- **JavaScript:** `launcher.js`, `request.js`, `check.js`, `news.js`
- **Immagini:** Logo e slideshow

### 🖼️ Immagini Slideshow (Directory `Images/`)
**57 immagini** per slideshow (file X*.* e S*.*)
- Immagini generiche (X*)
- Immagini stagionali/festive (S*)

### 📚 Font e Risorse
- `DejaVuSans.ttf` - Font principale
- `DejaVuSans-Bold.ttf` - Font grassetto
- `logo.png` - Logo aziendale (16 KB)
- `GTMC.png` - Logo GTMC (9 KB)
- `IDReader.dll` - **DLL per lettore RFID** (13 KB)

### 🔐 File Configurazione
- `print_config.json` - Configurazione stampante
- `encryption_key.key` - Chiave crittografia database
- `email_key.key` - Chiave crittografia email
- `db_config.enc` - Configurazione database (crittografata)
- `email_credentials.enc` - Credenziali email (crittografate)

⚠️ **IMPORTANTE:** I file `.enc` e `.key` sono specifici della macchina di sviluppo. Su una nuova installazione dovrai eseguire `python setup.py` per ricrearli.

### 🚀 Script di Installazione e Avvio
- `INSTALLA.bat` - **Script installazione completa** (crea venv, installa dipendenze)
- `START_APP.bat` - Avvio applicazione Flask
- `START_SISTEMA_KIOSK.bat` - Avvio completo sistema kiosk
- `AGGIORNA_FIRMA.bat` - Aggiornamento firma digitale
- `MOSTRA_IP_KIOSK.bat` - Visualizzazione indirizzo IP

### 📖 Documentazione Completa (11 documenti)
- `README.md` - Introduzione generale
- `INSTALLAZIONE_MANUALE.md` - Procedura installazione manuale
- `DEPLOYMENT.md` - Guida deployment
- `GUIDA_RAPIDA.md` - Guida rapida utente
- `GUIDA_RFID.md` - Configurazione RFID
- `GUIDA_KIOSK_FULLSCREEN.md` - Modalità kiosk fullscreen
- `GUIDA_NEWS_SLIDESHOW.md` - **Sistema News & Slideshow v2.2.0**
- `CONFIGURAZIONE_RETE.md` - Configurazione rete
- `STAMPA_AUTOMATICA.md` - Configurazione stampa automatica
- `RELEASE_NOTES_v2.2.0.md` - **Note di rilascio v2.2.0**
- `RELEASE_NOTES_v2.1.1.md` - Note di rilascio v2.1.1

### 📁 Directory Vuote (da creare)
- `temp/` - Directory temporanea per PDF
- `Images/` - Directory per immagini slideshow (già con 57 immagini)

---

## 🎯 COSA CONTIENE QUESTA VERSIONE

### ✨ Versione 2.2.0 - Architettura Dual-Frame
La versione 2.2.0 introduce il **sistema News & Slideshow simultaneo**:
- ✅ **Doppio iframe** per visualizzazione simultanea news e slideshow
- ✅ **Frame NEWS** (50% schermo) - collegamenti esterni configurabili
- ✅ **Frame SLIDESHOW** (50% schermo) - immagini personalizz abili
- ✅ **Configurazione flessibile** tramite `db_config.enc`
- ✅ **Immagini stagionali** basate su data corrente

### 🔧 Funzionalità Complete
- ✅ Richieste assenza con workflow approvazione
- ✅ Generazione certificati PDF personalizzati
- ✅ Firma digitale documenti
- ✅ Stampa automatica su stampante configurata
- ✅ Lettura badge RFID (opzionale)
- ✅ Verifica stato richieste in tempo reale
- ✅ Reinvio notifiche email ai manager
- ✅ Report annuale assenze PDF
- ✅ Supporto multi-lingua (IT/RO)
- ✅ Sistema News & Slideshow v2.2.0

---

## 📥 ISTRUZIONI PER L'INSTALLAZIONE

### STEP 1: Trasferimento File
1. Copia il file `Kiosk_HR_v2.2.0_20260103_130243.zip` sulla macchina target
2. Estrai il contenuto in una directory, ad esempio: `C:\Kiosk_HR\`

### STEP 2: Prerequisiti
Assicurati che sulla macchina target sia installato:
- ✅ **Python 3.11** (IMPORTANTE: versione 3.11, non superiore)
- ✅ **Microsoft Edge** (per modalità kiosk fullscreen)
- ✅ **Connessione al database SQL Server**
- ✅ **Accesso al server SMTP aziendale**

### STEP 3: Installazione Automatica
```batch
# Esegui come Amministratore
cd C:\Kiosk_HR
INSTALLA.bat
```

Lo script `INSTALLA.bat` esegue automaticamente:
1. Verifica presenza Python 3.11
2. Creazione ambiente virtuale (`venv`)
3. Installazione dipendenze da `requirements.txt`
4. Verifica installazione completata

### STEP 4: Configurazione
```batch
# Configura database e email
python setup.py
```

Il setup interattivo ti chiederà:
- **Server database** (es: `VANDEWIELESRV\TRACEABILITYRS`)
- **Nome database** (es: `Employee`)
- **Server SMTP** (es: `mail.vandewiele.com`)
- **Porta SMTP** (es: `587`)
- **Email mittente** (es: `kiosk@vandewiele.com`)
- **Password email**

Tutti i dati sensibili vengono crittografati automaticamente.

### STEP 5: Configurazione News & Slideshow (v2.2.0)
Dopo il setup, dovrai configurare gli URL delle news:
1. Apri `db_config.enc` (decrittografato tramite `config_manager.py`)
2. Aggiungi la sezione `news_config`:
```json
{
    "database": {...},
    "email": {...},
    "news_config": {
        "news_url": "https://example.com/news",
        "enable_dual_frame": true
    }
}
```

### STEP 6: Avvio Sistema
```batch
# Modalità normale
START_APP.bat

# Modalità kiosk fullscreen
START_SISTEMA_KIOSK.bat
```

### STEP 7: Verifica Installazione
1. Apri browser: `http://localhost:5000`
2. Verifica che la pagina principal e si carichi
3. Testa generazione certificato
4. Verifica News & Slideshow (se configurato)

---

## 🔍 FILE IMPORTANTI DA NON DIMENTICARE

### ⚠️ CRITICI (Necessari per il funzionamento)
- ✅ `app.py` - Applicazione principale
- ✅ `requirements.txt` - Dipendenze Python
- ✅ Tutti i file `.py` nella root
- ✅ Directory `templates/` completa
- ✅ Directory `static/` completa
- ✅ Font `DejaVuSans*.ttf`
- ✅ `logo.png`

### 🔧 CONFIGURAZIONE (Da configurare dopo installazione)
- ⚙️ `db_config.enc` - Configurazione database
- ⚙️ `email_credentials.enc` - Credenziali email
- ⚙️ `encryption_key.key` - Chiave crittografia
- ⚙️ `email_key.key` - Chiave email
- ⚙️ `print_config.json` - Configurazione stampante

### 📚 OPZIONALI (Ma altamente consigliati)
- 📄 `INSTALLA.bat` - Installazione automatica
- 📄 `START_APP.bat` - Avvio rapido
- 📄 Tutta la documentazione `.md`
- 🖼️ Immagini slideshow in `Images/`
- 🔌 `IDReader.dll` - Solo se usi RFID

---

## 🛠️ TROUBLESHOOTING

### Problema: Python non trovato
**Soluzione:** Verifica che Python 3.11 sia installato e nel PATH
```batch
python --version
```
Dovrebbe mostrare: `Python 3.11.x`

### Problema: Dipendenze non si installano
**Soluzione:** Usa `pip` con verbose:
```batch
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt -v
```

### Problema: Database non raggiungibile
**Soluzione:** 
1. Verifica connessione di rete al server SQL
2. Testa con SQL Server Management Studio
3. Verifica firewall Windows
4. Controlla configurazione in `db_config.enc`

### Problema: Email non vengono inviate
**Soluzione:**
1. Verifica server SMTP e porta
2. Controlla credenziali email
3. Verifica firewall non blocchi porta SMTP
4. Testa invio manuale da PowerShell

### Problema: Slideshow non mostra immagini
**Soluzione:**
1. Verifica directory `Images/` contenga file X*.* o S*.*
2. Controlla permessi lettura sulla directory
3. Verifica log applicazione per errori

---

## 📞 SUPPORTO

**Sviluppatore:** Gianluca Testa  
**Email:** gianluca.testa@vandewiele.com  
**Versione:** 2.2.0  
**Data Pacchetto:** 03/01/2026

### In caso di problemi fornire:
1. Versione Windows
2. Versione Python (`python --version`)
3. Log applicazione (`app_debug.log` - ultime 100 righe)
4. Screenshot errore
5. Passi per riprodurre il problema

---

## 📊 STATISTICHE PACCHETTO

| Componente | Quantità |
|-----------|----------|
| **File Python** | 16 |
| **Templates HTML** | 5 |
| **File CSS** | 2 |
| **File JavaScript** | 4 |
| **Immagini Slideshow** | 57 |
| **Script BAT** | 5 |
| **Documenti MD** | 11 |
| **Font** | 2 |
| **DLL** | 1 |
| **File Configurazione** | 5 |
| **Dimensione Totale** | 2.88 MB |

---

## ✅ CHECKLIST PRE-DEPLOYMENT

Prima di procedere al deployment, verifica:

- [ ] Python 3.11 installato sulla macchina target
- [ ] Connessione al database SQL Server funzionante
- [ ] Server SMTP raggiungibile
- [ ] Microsoft Edge installato (per kiosk mode)
- [ ] Permessi amministratore disponibili
- [ ] Stampante configurata (se necessaria)
- [ ] Lettore RFID connesso (se necessario)
- [ ] File ZIP completo e non corrotto
- [ ] Backup sistema esistente (se upgrade)

---

## 🎉 DEPLOYMENT COMPLETATO!

Il pacchetto `Kiosk_HR_v2.2.0_20260103_130243.zip` è pronto per essere installato su qualsiasi macchina Windows che soddisfi i prerequisiti.

**Tutti i file sono inclusi - non manca nulla! ✅**

---

*Generato automaticamente da CREA_PACCHETTO.ps1*  
*Vandewiele GTMC - Kiosk HR System v2.2.0*
