# 🚀 Guida Deploy - Kiosk HR v2.3.0

## 📋 Prerequisiti

### Software Richiesto
- Python 3.11 o superiore
- SQL Server (già configurato)
- Windows 10/11
- Stampante configurata nel sistema (es. "Color Birou")

### Certificati e Credenziali
- Certificato digitale CertSign installato in Windows Certificate Store
- Credenziali email configurate (file `email_credentials.enc` e `email_key.key`)
- File `db_config.enc` e `encryption_key.key` per database

---

## 🔧 Installazione

### 1. Clona o Aggiorna il Repository
```bash
cd C:\Path\To\Your\Project
git pull origin main
```

### 2. Crea/Attiva Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Installa Dipendenze
```bash
pip install -r requirements.txt
```

### 4. Verifica Configurazione

#### a) Database (`db_config.enc`)
Il file deve contenere le credenziali criptate per SQL Server.

#### b) Email (`email_credentials.enc`)
Il file deve contenere:
- SMTP server
- Porta
- Username
- Password

#### c) Stampante (`config.py`)
Verifica che il nome stampante sia corretto:
```python
DEFAULT_PRINTER = "Color Birou"  # O il nome della tua stampante
```

### 5. Crea Directory Necessarie
```bash
mkdir temp
mkdir logs
```

---

## ▶️ Avvio Applicazione

### Modalità Sviluppo
```bash
python app.py
```
L'app sarà disponibile su: `http://localhost:5000`

### Modalità Produzione (come Servizio Windows)

#### Opzione 1: NSSM (Recommended)
```bash
# Scarica NSSM da https://nssm.cc/download
nssm install KioskHR "C:\Path\To\venv\Scripts\python.exe" "C:\Path\To\app.py"
nssm set KioskHR AppDirectory "C:\Path\To\Project"
nssm start KioskHR
```

#### Opzione 2: Task Scheduler
1. Apri Task Scheduler
2. Crea nuova attività:
   - **Nome**: Kiosk HR
   - **Trigger**: All'avvio del sistema
   - **Action**: Esegui `python.exe` con argomento `app.py`
   - **Directory**: Path del progetto

---

## 🆕 Novità v2.3.0

### Sistema News
- **Auto-refresh**: La pagina aggiorna le news automaticamente ogni 30-60 secondi
- **Scorrimento verticale**: Per news con testo lungo
- **Stampa silenziosa**: Click sul frame news per stampare (senza popup Adobe)

### Localizzazione
- Tutti i PDF news ora in **rumeno**
- Formato: "Comunicare Companiei", "Publicat de:", "ID Știri:", "Tipărit la..."

---

## 🔍 Verifica Installazione

### Test Database
```bash
python -c "from db_connection import DatabaseConnection; db = DatabaseConnection(); print('DB OK' if db.connect() else 'DB ERRORE')"
```

### Test Stampante
```bash
python pdf_printer.py
```
Dovrebbe stampare un PDF di test su "Color Birou".

### Test News API
```bash
curl http://localhost:5000/api/news
```
Dovrebbe restituire le news attive in JSON.

### Test News Print
1. Vai su `http://localhost:5000`
2. Clicca sul frame news in basso
3. Verifica che la stampante stampi il PDF senza aprire Adobe

---

## 📁 Struttura File Principali

```
Adeverente/
├── app.py                      # Flask app principale
├── pdf_printer.py              # Sistema stampa silenziosa (SEMPLIFICATO)
├── config.py                   # Configurazione stampante
├── db_connection.py            # Connessione database
├── requirements.txt            # Dipendenze Python
├── templates/
│   └── launcher.html           # UI principale con news frame
├── static/
│   ├── css/
│   └── js/
├── temp/                       # PDF temporanei (auto-pulizia)
├── logs/                       # Log applicazione
└── logo.png                    # Logo aziendale (per PDF)
```

---

## 🐛 Troubleshooting

### News non visibili
- Verifica che ci siano record in `[Employee].[dbo].[News]` con `Activ = 1`
- Controlla console browser (F12) per errori JavaScript

### Stampa non funziona
1. Verifica nome stampante in `config.py`
2. Testa con: `python pdf_printer.py`
3. Controlla log in `logs/app.log`

### Errore "Printer not found"
```python
# In config.py, cambia:
DEFAULT_PRINTER = "NomeTuaStampante"
```

### PDF non si genera
- Verifica che esista `logo.png` nella root del progetto
- Controlla che `temp/` esista e sia scrivibile

---

## 📊 Monitoring

### Log Files
- `logs/app.log` - Log principale applicazione
- `logs/offline_events.json` - Eventi network offline

### Database Audit
Tutte le stampe news sono registrate in:
```sql
SELECT * FROM [Employee].[dbo].[KiosRequestes]
WHERE RequestWhat LIKE 'Stampa News%'
ORDER BY RequestDate DESC
```

---

## 🔄 Aggiornamenti Futuri

Per aggiornare:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
# Riavvia servizio
```

---

## 📞 Supporto

Per problemi o domande:
- Email: gianluca.testa@vandewiele.com
- GitHub Issues: https://github.com/glctesta/kiosk-hr-adeverente/issues

---

**Versione**: 2.3.0  
**Data Rilascio**: 21 Gennaio 2026  
**Autore**: Gianluca Testa
