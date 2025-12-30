# 📦 GUIDA DEPLOYMENT - Kiosk Angajați

## 🎯 Obiettivo

Installare e configurare l'applicazione Kiosk su un nuovo PC Windows.

---

## 📋 PREREQUISITI

### Hardware
- ✅ PC Windows 10/11
- ✅ Lettore badge RFID (opzionale)
- ✅ Stampante configurata (per stampa automatica)
- ✅ Connessione rete al database SQL Server

### Software Richiesto
- ✅ Python 3.11 o superiore
- ✅ ODBC Driver 18 for SQL Server
- ✅ Browser moderno (Chrome, Edge, Firefox)

---

## 🚀 PROCEDURA INSTALLAZIONE

### STEP 1: Preparazione File

#### Opzione A: Copia Manuale
1. **Copia intera cartella** `Adeverente` sul nuovo PC
2. **Posizione consigliata**: `C:\Kiosk\Adeverente`

#### Opzione B: Crea ZIP
```powershell
# Sul PC di sviluppo
Compress-Archive -Path "C:\Users\gtesta\PythonProjetcs\Python\Adeverente" -DestinationPath "Kiosk_Deploy.zip"
```

**File da includere**:
```
Adeverente/
├── app.py
├── certificate_generator.py
├── badge_reader.py
├── db_connection.py
├── config_manager.py
├── pdf_printer.py
├── digital_signature.py
├── pdf_signature_powershell.py
├── update_signature.py
├── utils.py
├── requirements.txt
├── logo.png
├── db_config.enc          ← IMPORTANTE!
├── encryption_key.key     ← IMPORTANTE!
├── print_config.json
├── templates/
│   ├── launcher.html
│   └── index.html
├── static/
│   ├── css/
│   │   ├── launcher.css
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── logo.png
├── temp/                  ← Crea se non esiste
├── START_APP.bat
├── AGGIORNA_FIRMA.bat
└── GUIDA_RAPIDA.md
```

---

### STEP 2: Installazione Python

1. **Download Python 3.11**:
   - URL: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

2. **Installazione**:
   - ✅ Seleziona: **"Add Python to PATH"**
   - ✅ Seleziona: **"Install for all users"**
   - Click: **"Install Now"**

3. **Verifica**:
```powershell
python --version
# Output: Python 3.11.9
```

---

### STEP 3: Installazione ODBC Driver

1. **Download**:
   - URL: https://go.microsoft.com/fwlink/?linkid=2249004
   - Nome: ODBC Driver 18 for SQL Server

2. **Installazione**:
   - Esegui installer
   - Accetta termini
   - Installazione standard

3. **Verifica**:
```powershell
# Apri "ODBC Data Sources (64-bit)"
# Verifica presenza "ODBC Driver 18 for SQL Server"
```

---

### STEP 4: Installazione Dipendenze Python

```powershell
# Vai alla cartella applicazione
cd C:\Kiosk\Adeverente

# Installa dipendenze
pip install -r requirements.txt

# Se errori, installa singolarmente:
pip install Flask==3.0.0
pip install Flask-CORS==4.0.0
pip install pyodbc>=5.1.0
pip install reportlab==4.0.7
pip install Pillow==10.1.0
pip install PyPDF2>=3.0.0
pip install cryptography==41.0.7
pip install python-dotenv==1.0.0
pip install pywin32>=306
```

---

### STEP 5: Configurazione Database

#### Se hai già `db_config.enc` e `encryption_key.key`:
✅ **Copia entrambi i file** nella cartella principale
✅ **Non serve configurare nulla** - Funzionerà subito!

#### Se NON hai i file di configurazione:

1. **Crea configurazione**:
```powershell
python setup.py
```

2. **Inserisci credenziali**:
   - Server: `nome_server_sql`
   - Database: `Employee`
   - Username: `utente_sql`
   - Password: `password_sql`

3. **File generati**:
   - ✅ `db_config.enc` (configurazione crittografata)
   - ✅ `encryption_key.key` (chiave crittografia)

---

### STEP 6: Configurazione Stampante (Opzionale)

Modifica `print_config.json`:

```json
{
    "enabled": true,
    "use_default_printer": true,
    "printer_name": "",
    "silent_print": true,
    "kiosk_mode": {
        "enabled": true,
        "auto_reset_seconds": 30
    }
}
```

**Parametri**:
- `enabled`: `true` per abilitare stampa automatica
- `use_default_printer`: `true` per usare stampante predefinita
- `printer_name`: Nome stampante (se non usi predefinita)
- `auto_reset_seconds`: Secondi prima di reset (kiosk mode)

---

### STEP 7: Test Applicazione

```powershell
# Avvia applicazione
python app.py

# Output atteso:
# * Serving Flask app 'app'
# * Debug mode: on
# * Running on http://0.0.0.0:5000
```

**Apri browser**: http://localhost:5000

**Verifica**:
- ✅ Logo visibile
- ✅ 4 bottoni servizi
- ✅ Click "Adeverințe" funziona
- ✅ Genera certificato di test

---

## 🔧 CONFIGURAZIONE AVANZATA

### Avvio Automatico Windows

1. **Crea collegamento** a `START_APP.bat`
2. **Premi** `Win + R`
3. **Digita**: `shell:startup`
4. **Copia collegamento** nella cartella Startup

### Modalità Kiosk (Fullscreen)

Crea `START_KIOSK.bat`:

```batch
@echo off
start /min python app.py
timeout /t 5 /nobreak
start chrome --kiosk --app=http://localhost:5000
```

### Configurazione Firewall

```powershell
# Permetti Flask attraverso firewall
netsh advfirewall firewall add rule name="Kiosk Flask" dir=in action=allow protocol=TCP localport=5000
```

---

## 🔍 TROUBLESHOOTING

### Problema: "No module named 'flask'"

**Soluzione**:
```powershell
pip install Flask==3.0.0
```

---

### Problema: "File di configurazione non trovato"

**Soluzione**:
1. Verifica presenza `db_config.enc` e `encryption_key.key`
2. Se mancano, esegui `python setup.py`

---

### Problema: "Impossibile connettersi al database"

**Soluzione**:
1. Verifica connessione rete al server SQL
2. Testa con SQL Server Management Studio
3. Controlla firewall
4. Verifica credenziali in configurazione

---

### Problema: "Caratteri rumeni non visualizzati"

**Soluzione**:
1. Installa font Arial (già presente in Windows)
2. Oppure copia font DejaVu in `C:\Windows\Fonts\`

---

### Problema: "Stampa non funziona"

**Soluzione**:
1. Verifica stampante predefinita configurata
2. Controlla `print_config.json`
3. Testa stampa manuale da Windows
4. Verifica log applicazione

---

## 📊 CHECKLIST DEPLOYMENT

### Pre-Deployment
- [ ] Python 3.11 installato
- [ ] ODBC Driver 18 installato
- [ ] File applicazione copiati
- [ ] `db_config.enc` presente
- [ ] `encryption_key.key` presente
- [ ] `logo.png` presente

### Post-Deployment
- [ ] Dipendenze Python installate
- [ ] Connessione database funzionante
- [ ] Applicazione si avvia senza errori
- [ ] Logo visibile nella home
- [ ] Certificato di test generato
- [ ] Stampa funzionante (se abilitata)
- [ ] Caratteri rumeni visualizzati

### Configurazione Opzionale
- [ ] Avvio automatico configurato
- [ ] Modalità kiosk attivata
- [ ] Firewall configurato
- [ ] Lettore badge collegato

---

## 🎯 CONFIGURAZIONE PRODUZIONE

### Disabilita Debug Mode

In `app.py`, alla fine del file:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False
```

### Configura Logging

Crea `logging_config.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kiosk.log'),
        logging.StreamHandler()
    ]
)
```

---

## 📞 SUPPORTO

### Log Applicazione

```powershell
# Visualizza log in tempo reale
Get-Content kiosk.log -Wait -Tail 50
```

### Informazioni Sistema

```powershell
# Versione Python
python --version

# Driver ODBC installati
Get-OdbcDriver

# Stampanti disponibili
Get-Printer
```

---

## 🔄 AGGIORNAMENTI

### Aggiornare Applicazione

1. **Backup**:
```powershell
Copy-Item -Path "C:\Kiosk\Adeverente" -Destination "C:\Kiosk\Backup_$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

2. **Copia nuovi file** (sovrascrivendo)

3. **Mantieni**:
   - `db_config.enc`
   - `encryption_key.key`
   - `print_config.json`
   - `temp/` (PDF generati)

4. **Riavvia applicazione**

---

**Ultimo aggiornamento**: 23 Dicembre 2025  
**Versione**: 1.0.0
