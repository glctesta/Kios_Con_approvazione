# 🏢 KIOSK HR - SISTEMA GESTIONE RISORSE UMANE

## 📋 PANORAMICA

**Kiosk HR** è un'applicazione web moderna per la gestione self-service delle risorse umane, accessibile tramite badge RFID.

### **✨ SERVIZI DISPONIBILI**

| Servizio | Descrizione | Stato |
|----------|-------------|-------|
| 📄 **Adeverințe** | Generazione certificati medici e di lavoro | ✅ Attivo |
| 📊 **Raport Absențe** | Report storico ferie, malattie e permessi | ✅ Attivo |
| 🔧 **Serviciu 3** | In sviluppo | 🚧 Prossimamente |
| ⚙️ **Serviciu 4** | In sviluppo | 🚧 Prossimamente |

---

## 🚀 DEPLOYMENT RAPIDO

### **📦 PREREQUISITI**

- Windows 10/11
- Python 3.11 o 3.14
- SQL Server (connessione database)
- Stampante configurata

### **⚡ INSTALLAZIONE IN 3 PASSI**

#### **1. Crea Pacchetto (PC Sviluppo)**

```batch
CREA_PACCHETTO_DEPLOY.bat
```

#### **2. Installa (PC Kiosk)**

Estrai ZIP in `C:\Kiosk\Adeverente\` ed esegui:

```batch
INSTALLA_KIOSK.bat
```

#### **3. Avvia Applicazione**

```batch
START_APP.bat
```

**Accesso**: http://localhost:5000

---

## 🌐 ACCESSO DALLA RETE AZIENDALE

### **CONFIGURAZIONE FIREWALL**

**PowerShell (Amministratore):**

```powershell
New-NetFirewallRule -DisplayName "Kiosk HR" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### **ACCESSO DA ALTRI PC**

1. Trova IP PC Kiosk: `ipconfig`
2. Da altro PC: `http://[IP-KIOSK]:5000`

**Esempio**: `http://192.168.10.50:5000`

---

## 📚 DOCUMENTAZIONE COMPLETA

| Documento | Descrizione |
|-----------|-------------|
| **DEPLOYMENT_RAPIDO.md** | Guida deployment completa |
| **CONFIGURAZIONE_RETE.md** | Configurazione accesso rete aziendale |
| **GUIDA_RAPIDA.md** | Guida utente finale |
| **INSTALLAZIONE_MANUALE.md** | Installazione manuale dipendenze |

---

## 🔧 TECNOLOGIE

### **Backend**
- Python 3.11/3.14
- Flask 3.0.0
- pyodbc (SQL Server)
- reportlab (PDF generation)
- cryptography (sicurezza)

### **Frontend**
- HTML5 / CSS3
- JavaScript (Vanilla)
- Design responsive

### **Database**
- SQL Server
- Database: Employee, Timeclocking

---

## 📊 FUNZIONALITÀ PRINCIPALI

### **🎫 Autenticazione Badge RFID**
- Lettura automatica badge
- Validazione dipendente
- Normalizzazione numero badge (10 cifre)

### **📄 Generazione Certificati**
- Certificati medici (Adeverința 7)
- Certificati di lavoro
- Firma digitale amministratore
- Logo aziendale
- Supporto caratteri rumeni (ă, â, î, ș, ț)

### **📊 Report Absențe**
- Situazione ferie dettagliata
- Bonus anzianità automatico
- Malattie e permessi
- Calcolo solo giorni lavorativi
- Esclusione weekend e festività

### **🖨️ Stampa Automatica**
- Stampa silenziosa
- Stampante predefinita
- Configurazione personalizzabile

### **🔒 Sicurezza**
- Credenziali database criptate
- Chiave crittografia separata
- Privacy badge (mascheramento)

### **🏠 Kiosk Mode**
- Auto-redirect dopo inattività
- Bottone "Torna Indietro"
- Reset automatico form
- Interfaccia touch-friendly

---

## 🗂️ STRUTTURA PROGETTO

```
Adeverente/
├── app.py                      # Applicazione Flask principale
├── absence_report.py           # Generatore report absențe
├── certificate_generator.py   # Generatore certificati
├── badge_reader.py             # Lettore badge RFID
├── db_connection.py            # Connessione database
├── config_manager.py           # Gestione configurazione
├── pdf_printer.py              # Stampa PDF
├── utils.py                    # Utility varie
│
├── templates/                  # Template HTML
│   ├── launcher.html           # Pagina principale
│   ├── index.html              # Certificati
│   └── absence.html            # Report absențe
│
├── static/                     # Risorse statiche
│   ├── css/
│   │   ├── launcher.css        # Stili launcher
│   │   └── styles.css          # Stili globali
│   ├── js/
│   │   ├── app.js              # JavaScript certificati
│   │   └── absence.js          # JavaScript absențe
│   └── logo.png                # Logo aziendale
│
├── DejaVuSans.ttf              # Font caratteri rumeni
├── DejaVuSans-Bold.ttf         # Font bold
├── logo.png                    # Logo aziendale
│
├── db_config.enc               # Config database (criptato)
├── encryption_key.key          # Chiave crittografia
├── print_config.json           # Config stampante
│
├── START_APP.bat               # Avvio applicazione
├── INSTALLA_KIOSK.bat          # Installazione
├── CREA_PACCHETTO_DEPLOY.bat   # Creazione pacchetto
│
└── temp/                       # PDF generati (temporanei)
```

---

## ⚙️ CONFIGURAZIONE

### **Database**

```python
# Esegui setup
python setup.py
```

Inserisci:
- Server: `SQLSERVER01`
- Database: `Employee`
- Username: `kiosk_user`
- Password: `********`

### **Stampante**

Modifica `print_config.json`:

```json
{
    "default_printer": "HP LaserJet",
    "auto_print": true,
    "silent_print": true
}
```

### **Rete**

Modifica `app.py` (ultima riga):

```python
# Accesso solo locale
app.run(host='127.0.0.1', port=5000)

# Accesso da rete
app.run(host='0.0.0.0', port=5000)
```

---

## 🧪 TEST

### **Test Locale**

```
http://localhost:5000
```

### **Test Rete**

```
http://[IP-PC-KIOSK]:5000
```

### **Test Servizi**

1. **Launcher**: Verifica 4 bottoni visibili
2. **Certificati**: Scansiona badge → Genera certificato
3. **Absențe**: Scansiona badge → Genera report
4. **Stampa**: Verifica PDF stampato

---

## 📝 LOG

### **Visualizza Log**

```batch
type app_debug.log
```

### **Log in Tempo Reale**

```powershell
Get-Content app_debug.log -Wait -Tail 50
```

### **Livelli Log**

- **INFO**: Operazioni normali
- **WARNING**: Avvisi
- **ERROR**: Errori

---

## 🔍 TROUBLESHOOTING

### **Problema: Applicazione non si avvia**

**Soluzione:**
1. Verifica Python installato: `python --version`
2. Verifica dipendenze: `pip list`
3. Controlla log: `app_debug.log`

### **Problema: Errore connessione database**

**Soluzione:**
1. Verifica `db_config.enc` presente
2. Riesegui: `python setup.py`
3. Test connessione SQL Server

### **Problema: Caratteri rumeni non visualizzati**

**Soluzione:**
1. Verifica font: `DejaVuSans.ttf`, `DejaVuSans-Bold.ttf`
2. Copia font dalla cartella sviluppo

### **Problema: Stampa non funziona**

**Soluzione:**
1. Verifica stampante predefinita: `wmic printer get name,default`
2. Controlla `print_config.json`
3. Test stampa manuale

### **Problema: Non accessibile da rete**

**Soluzione:**
1. Verifica firewall: porta 5000 aperta
2. Verifica IP: `ipconfig`
3. Test ping da altro PC
4. Verifica `app.py`: `host='0.0.0.0'`

---

## 🔐 SICUREZZA

### **Best Practices**

✅ **FARE:**
- Usare credenziali database criptate
- Limitare accesso a rete interna
- Monitorare log regolarmente
- Backup configurazione

❌ **NON FARE:**
- Esporre su Internet pubblico
- Condividere `encryption_key.key`
- Usare su reti non sicure
- Disabilitare firewall

---

## 📞 SUPPORTO

### **Problemi Comuni**

| Problema | Soluzione |
|----------|-----------|
| Python non trovato | Installa Python 3.11/3.14 |
| Dipendenze mancanti | Esegui `INSTALLA_KIOSK.bat` |
| Database non raggiungibile | Verifica connessione SQL Server |
| Firewall blocca | Configura porta 5000 |

### **Contatti**

- **Log**: `app_debug.log`
- **Documentazione**: `*.md`
- **Configurazione**: `setup.py`

---

## 📈 ROADMAP

### **Versione Corrente: 2.0**

- ✅ Launcher multi-servizio
- ✅ Certificati medici
- ✅ Report absențe
- ✅ Supporto rete aziendale
- ✅ Font rumeni

### **Prossime Funzionalità**

- 🚧 Serviciu 3 (TBD)
- 🚧 Serviciu 4 (TBD)
- 🚧 Dashboard amministratore
- 🚧 Statistiche utilizzo

---

## 📄 LICENZA

Uso interno aziendale.

---

## 🎉 CREDITS

**Sviluppato da**: Gianluca Testa  
**Data**: Dicembre 2025  
**Versione**: 2.0  

---

*Per informazioni dettagliate, consulta la documentazione completa nella cartella del progetto.*
