# 🏢 Sistema Kiosk HR - Adeverențe și Cereri Absență
## Sistema di Gestione Certificati e Richieste Assenza

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/glctesta/kiosk-hr-adeverente)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()

Sistema web completo per la gestione automatizzata di certificati HR e richieste di assenza, progettato per ambienti kiosk aziendali.

---

## 📋 Caratteristiche Principali

### 🎫 Generazione Certificati
- ✅ Generazione automatica certificati/adeverințe
- 📄 PDF professionale con firma digitale
- 🖨️ Stampa automatica su stampante configurata
- 📧 Invio email automatico HR
- 🏷️ Numerazione progressiva automatica

### 📅 Gestione Richieste Assenza
- ✅ Creazione richieste ferie/permessi
- 📊 Calcolo automatico giorni lavorativi
- 🔍 Verifica disponibilità ferie
- 📧 Notifiche automatiche ai manager
- ⏰ **Rilevamento richieste scadute** (v2.1.0)
- 🔄 **Reinvio notifiche** (v2.1.0)

### 📊 Report Storico Assenze
- 📈 Report dettagliato ferie/malattie/permessi
- 📅 Calcolo automatico con bonus anzianità
- 📄 PDF professionale con grafici
- 🖨️ Stampa automatica

### 🔐 Sicurezza
- 🎫 Autenticazione tramite badge RFID
- 🔒 Credenziali database crittografate
- 🔑 Gestione sicura chiavi di cifratura
- 📝 Logging completo operazioni

---

## 🚀 Novità Versione 2.1.0

### Gestione Intelligente Richieste Assenza

#### 🎯 Stati Richiesta
Il sistema ora distingue automaticamente:
- ✅ **Approvate** - Autorizzate dal manager
- ❌ **Respinte** - Rifiutate esplicitamente
- ⏰ **Scadute** - Non autorizzate in tempo
- ⏳ **In Attesa** - Ancora valide per approvazione

#### 📧 Reinvio Notifiche
- Pulsante "Retrimite Notificare" per richieste pending
- Anti-spam con disabilitazione temporanea (10s)
- Email fallback automatica se manager non trovati

#### 🎨 UI Migliorata
- Colori distintivi per ogni stato
- Icone intuitive (✅/❌/⏰/⏳)
- Feedback visivo immediato
- Header compatto ottimizzato

---

## 🛠️ Tecnologie Utilizzate

### Backend
- **Python 3.11** - Linguaggio principale
- **Flask 3.0** - Web framework
- **pyodbc** - Connessione SQL Server
- **ReportLab** - Generazione PDF
- **cryptography** - Cifratura credenziali

### Frontend
- **HTML5** - Struttura
- **CSS3** - Styling moderno
- **JavaScript ES6** - Logica client-side
- **Fetch API** - Comunicazione asincrona

### Database
- **SQL Server** - Database aziendale
- **Stored Procedures** - Logica business
- **Views** - Aggregazione dati

---

## 📦 Installazione

### Prerequisiti
- Windows 10/11
- Python 3.11
- SQL Server (accesso al database aziendale)
- Stampante configurata (opzionale)
- Lettore RFID (opzionale)

### Setup Rapido

```batch
# 1. Clona repository
git clone https://github.com/glctesta/kiosk-hr-adeverente.git
cd kiosk-hr-adeverente

# 2. Crea ambiente virtuale
python -m venv venv
venv\Scripts\activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Configura database
python setup.py

# 5. Avvia applicazione
START_APP.bat
```

### Configurazione Kiosk Fullscreen

```batch
# Avvia in modalità kiosk fullscreen
START_KIOSK_FULLSCREEN.bat
```

---

## 📖 Documentazione

### Guide Disponibili
- 📘 [**GUIDA_RAPIDA.md**](GUIDA_RAPIDA.md) - Guida utente completa
- 🚀 [**DEPLOYMENT_v2.1.0.md**](DEPLOYMENT_v2.1.0.md) - Istruzioni deployment
- 📋 [**RELEASE_NOTES_v2.1.0.md**](RELEASE_NOTES_v2.1.0.md) - Note di rilascio
- 🔧 [**GUIDA_DEPLOYMENT.md**](GUIDA_DEPLOYMENT.md) - Deployment avanzato
- 🖨️ [**STAMPA_AUTOMATICA.md**](STAMPA_AUTOMATICA.md) - Configurazione stampa
- 🎫 [**GUIDA_RFID.md**](GUIDA_RFID.md) - Setup lettore RFID
- 🌐 [**CONFIGURAZIONE_RETE.md**](CONFIGURAZIONE_RETE.md) - Accesso da rete

---

## 🎯 Utilizzo

### 1. Generazione Certificato
```
1. Avvicinare badge RFID al lettore
2. Selezionare motivo certificato
3. Confermare generazione
4. PDF generato e stampato automaticamente
```

### 2. Richiesta Assenza
```
1. Avvicinare badge RFID
2. Selezionare tipo assenza (ferie/permesso)
3. Scegliere periodo
4. Confermare richiesta
5. Email inviata ai manager automaticamente
```

### 3. Verifica Stato Richiesta
```
1. Inserire numero richiesta (es: 2ARQ-2025)
2. Visualizzare stato corrente
3. Se pending: reinviare notifica ai manager
```

### 4. Report Storico
```
1. Avvicinare badge RFID
2. Selezionare anno
3. Generare report
4. PDF con dettaglio ferie/malattie/permessi
```

---

## 🔧 Configurazione

### Database
Credenziali crittografate in:
- `db_config.enc` - Configurazione database
- `encryption_key.key` - Chiave cifratura

### Email
Configurazione SMTP in:
- `email_credentials.enc` - Credenziali email
- `email_key.key` - Chiave cifratura email

### Stampa
Configurazione stampante in:
- `print_config.json` - Impostazioni stampa

---

## 📊 Architettura

```
┌─────────────────────────────────────────┐
│         Frontend (Browser)              │
│  HTML5 + CSS3 + JavaScript ES6          │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON
┌──────────────▼──────────────────────────┐
│         Backend (Flask)                 │
│  - app.py (Routes)                      │
│  - certificate_generator.py             │
│  - absence_request.py                   │
│  - absence_report.py                    │
└──────────────┬──────────────────────────┘
               │ pyodbc
┌──────────────▼──────────────────────────┐
│      SQL Server Database                │
│  - Employee.dbo.*                       │
│  - Timeclocking.dbo.*                   │
└─────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Problema: Servizio non si avvia
```batch
# Verifica log
type app_debug.log

# Verifica dipendenze
pip list
```

### Problema: Errore database
```batch
# Verifica connessione
python -c "from db_connection import DatabaseConnection; print(DatabaseConnection().connect())"
```

### Problema: Stampa non funziona
```batch
# Verifica stampante
python pdf_printer.py
```

---

## 📞 Supporto

**Contatto:** gianluca.testa@vandewiele.com

**Informazioni da fornire:**
- Versione sistema (vedi `app.py`)
- Log applicazione (`app_debug.log`)
- Screenshot errore
- Passi per riprodurre

---

## 📅 Roadmap

### v2.2.0 (Q1 2026)
- [ ] Dashboard manager per approvazioni
- [ ] Notifiche push browser
- [ ] API REST documentata
- [ ] Autenticazione multi-fattore

### v2.3.0 (Q2 2026)
- [ ] App mobile companion
- [ ] Integrazione calendario Outlook
- [ ] Report analytics avanzati
- [ ] Supporto multi-lingua

---

## 📄 Licenza

Proprietario - Vandewiele Romania  
© 2025 Tutti i diritti riservati

---

## 👥 Autori

**Gianluca Testa**  
IT Manager - Vandewiele Romania  
📧 gianluca.testa@vandewiele.com

---

## 🙏 Ringraziamenti

- Team HR Vandewiele Romania
- Utenti beta tester
- Comunità Flask e Python

---

**Versione:** 2.1.0  
**Ultimo Aggiornamento:** 30 Dicembre 2025
