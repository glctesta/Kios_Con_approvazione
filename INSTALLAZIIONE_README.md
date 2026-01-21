# 📦 KIOSK HR v2.3.0 - PACCHETTO INSTALLAZIONE

## 🎉 Benvenuto!

Questo archivio contiene tutti i file necessari per installare il sistema Kiosk HR v2.3.0 su un computer Windows.

---

## 📋 REQUISITI SISTEMA

### Software Necessario
- ✅ **Windows 10/11** (64-bit)
- ✅ **Python 3.11 o superiore** → [Download](https://www.python.org/downloads/)
- ✅ **SQL Server** (Accesso ai database Employee e Timeclocking)
- ✅ **Adobe Acrobat Reader DC** → [Download](https://get.adobe.com/reader/)
- ⚠️ **Stampante** configurata (es. "Color Birou")

### Requisiti Opzionali
- Lettore badge RFID (con DLL IDReader.dll)
- Certificato digitale CertSign per firme PDF

---

## 🚀 INSTALLAZIONE RAPIDA

### Metodo 1: Installazione Automatica (Raccomandato)

1. **Estrai lo ZIP** in una cartella (es. `C:\KioskHR`)

2. **Esegui INSTALLA.bat** (click destro → "Esegui come amministratore")
   - Installa dipendenze Python
   - Configura virtual environment
   - Prepara le directory necessarie

3. **Configura la connessione database**
   ```bash
   python setup.py
   ```
   - Inserisci server SQL
   - Inserisci credenziali
   - Inserisci credenziali email SMTP

4. **Avvia l'applicazione**
   ```bash
   START_APP.bat
   ```

5. **Apri il browser**
   - Locale: http://localhost:5000
   - Rete: http://[IP-COMPUTER]:5000

### Metodo 2: Installazione Manuale

```bash
# 1. Crea virtual environment
python -m venv venv

# 2. Attiva environment
.\venv\Scripts\activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Configura database
python setup.py

# 5. Avvia applicazione
python app.py
```

---

## 🆕 NOVITÀ v2.3.0

### ✨ Sistema News
- **Display dinamico** nel launcher con frame dedicato
- **Auto-refresh** automatico ogni 30-60 secondi
- **Scorrimento verticale** per testi lunghi
- **Click to Print** → Stampa immediata con un click

### 🖨️ Stampa Silenziosa
- **VERAMENTE silenziosa** - NO popup Adobe Acrobat
- Metodo Adobe Reader `/t` (print and terminate)
- PDF generati con logo aziendale
- Localizzazione **rumena completa**

### 🇷🇴 Localizzazione
Tutti i campi PDF news in rumeno:
- Titolo: "Comunicare Companiei"
- Campi: "Data:", "Publicat de:", "ID Știri:"
- Footer: "Tipărit la ... ora ... de ..."

### ⚡ Performance
- `pdf_printer.py` ottimizzato (-60% codice)
- Metodo stampa unico e robusto
- Eliminati errori path Windows

### 📊 API
- `GET /api/news` - Lista news attive
- `POST /api/news/print` - Stampa news
- Registrazione audit in `KiosRequestes`

---

## 📁 STRUTTURA FILES

```
KioskHR/
├── app.py                    # Applicazione Flask principale
├── pdf_printer.py            # Sistema stampa silenziosa ⭐ AGGIORNATO
├── templates/                # Template HTML
│   └── launcher.html         # Menu principale con news ⭐ AGGIORNATO  
├── static/                   # CSS, JS, immagini
├── requirements.txt          # Dipendenze Python
├── logo.png                  # Logo aziendale (per PDF)
├── INSTALLA.bat              # Script installazione
├── START_APP.bat             # Avvio applicazione
├── README.md                 # Questo file
├── DEPLOY.md                 # Guida deploy dettagliata
├── CHANGELOG.md              # Storico versioni
└── DEPLOY_v2.3.0_SUMMARY.md  # Riepilogo v2.3.0

```

---

## ⚙️ CONFIGURAZIONE

### 1. Database
Il file `db_config.enc` (creato da `setup.py`) contiene le credenziali criptate per SQL Server.

### 2. Email
Il file `email_credentials.enc` (creato da `setup.py`) contiene le credenziali SMTP.

### 3. Stampante
Modifica `config.py` per cambiare la stampante predefinita:
```python
DEFAULT_PRINTER = "Color Birou"  # Cambia con il nome della tua stampante
```

### 4. Adobe Reader
Il sistema cerca Adobe Reader in:
- `C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe`
- `C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe`  
- `C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe`

Se non trovato, usa SumatraPDF (se installato).

---

## 🔍 VERIFICA INSTALLAZIONE

### Test Database
```bash
python -c "from db_connection import DatabaseConnection; db = DatabaseConnection(); print('DB OK' if db.connect() else 'DB ERRORE')"
```

### Test Stampante
```bash
python pdf_printer.py
```
Dovrebbe stampare un PDF di test su "Color Birou".

### Test Web
1. Avvia: `python app.py`
2. Apri browser: `http://localhost:5000`
3. Dovresti vedere il launcher con il frame news in basso

### Test Stampa News
1. Vai su http://localhost:5000
2. Click sul frame news
3. Controlla console browser (F12) → Dovrebbe dire "✅ News stampata con successo"
4. Verifica che **NESSUNA finestra Adobe si apra**
5. La stampante dovrebbe stampare il PDF

---

## 🐛 TROUBLESHOOTING

### L'applicazione non si avvia
- Verifica Python 3.11 installato: `python --version`
- Verifica environment attivo: vedi `(venv)` prima del prompt
- Controlla log: `logs/app.log`

### Errore connessione database
- Verifica credenziali in `setup.py`
- Testa connessione SQL Server Manualmente
- Verifica firewall Windows

### Stampa non funziona
- Verifica Adobe Reader installato
- Verifica nome stampante in `config.py`
- Testa: `python pdf_printer.py`

### Adobe Acrobat si apre invece di stampare silenziosamente
⚠️ **Questo problema è stato RISOLTO in v2.3.0!**

Se persiste:
1. Verifica Adobe Reader DC installato (non versioni vecchie)
2. Controlla log: `logs/app.log`
3. Verifica che il path Adobe sia corretto in `pdf_printer.py`

### News non visibili
- Verifica record in database `[Employee].[dbo].[News]` con `Activ = 1`
- Controlla console browser (F12) per errori JavaScript
- Verifica API: `http://localhost:5000/api/news`

---

## 📞 SUPPORTO

### Documentazione
- **README.md** - Overview generale
- **DEPLOY.md** - Guida deploy completa con troubleshooting
- **CHANGELOG.md** - Storico versioni dettagliato
- **DEPLOY_v2.3.0_SUMMARY.md** - Riepilogo versione attuale

### Contatti
- **Email**: gianluca.testa@vandewiele.com
- **GitHub**: https://github.com/glctesta/kiosk-hr-adeverente

---

## 📊 MONITORING

### Log Files
- `logs/app.log` - Log applicazione principale
- `logs/offline_events.json` - Eventi network offline

### Database Audit
Tutte le stampe news sono registrate in:
```sql
SELECT * FROM [Employee].[dbo].[KiosRequestes]
WHERE RequestWhat LIKE 'Stampa News%'
ORDER BY RequestDate DESC
```

---

## 🔄 AGGIORNAMENTI FUTURI

Per aggiornare a versioni future:

```bash
# Backup configurazione
copy db_config.enc db_config.enc.bak
copy email_credentials.enc email_credentials.enc.bak

# Download nuova versione
git pull origin main
# oppure estrai nuovo ZIP

# Aggiorna dipendenze
pip install -r requirements.txt --upgrade

# Ripristina configurazione
copy db_config.enc.bak db_config.enc
copy email_credentials.enc.bak email_credentials.enc

# Riavvia servizio
```

---

**Versione**: 2.3.0  
**Data Rilascio**: 21 Gennaio 2026  
**Build**: 20260121_090755  
**Status**: ✅ PRODUCTION READY  

---

**© 2026 GTMC - Vandewiele Romania**

Buona installazione! 🚀
