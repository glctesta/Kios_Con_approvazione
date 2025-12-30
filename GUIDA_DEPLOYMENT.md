# 📦 PACCHETTO DEPLOYMENT KIOSK HR - GUIDA COMPLETA

## ✅ PACCHETTO CREATO

**File**: `Kiosk_Deploy_YYYYMMDD_HHMMSS.zip`  
**Dimensione**: ~887 KB  
**Data creazione**: Automatica con timestamp

---

## 📋 CONTENUTO PACCHETTO

### **File Python** (Moduli Backend)
- `app.py` - Applicazione Flask principale
- `certificate_generator.py` - Generazione certificati
- `absence_report.py` - Report storico assenze
- `absence_request.py` - Gestione richieste assenza
- `badge_reader.py` - Lettura e validazione badge
- `db_connection.py` - Connessione database
- `config_manager.py` - Gestione configurazione
- `email_connector.py` - Invio email
- `pdf_printer.py` - Stampa PDF silenziosa
- `utils.py` - Funzioni utilità
- `rfid_reader.py` - Lettore RFID (template)

### **File Configurazione**
- `requirements.txt` - Dipendenze Python
- `print_config.json` - Configurazione stampante
- `db_config.enc` - Configurazione database (criptata)
- `encryption_key.key` - Chiave crittografia

### **Script Installazione**
- `INSTALLA_KIOSK.bat` - Installazione automatica
- `START_APP.bat` - Avvio applicazione
- `CREA_PACCHETTO_DEPLOY.bat` - Creazione pacchetto
- `AGGIORNA_FIRMA.bat` - Aggiornamento firma digitale

### **Risorse**
- `logo.png` - Logo aziendale
- `DejaVuSans.ttf` - Font per caratteri rumeni
- `DejaVuSans-Bold.ttf` - Font bold
- `IDReader.dll` - Libreria lettore RFID (se presente)

### **Frontend**
- `templates/` - Template HTML
  - `launcher.html` - Pagina principale
  - `index.html` - Certificati
  - `absence.html` - Report assenze
  - `request.html` - Richiesta assenza
  - `check.html` - Verifica stato
- `static/` - Risorse statiche
  - `css/` - Fogli di stile
  - `js/` - JavaScript
  - `favicon.svg` - Icona sito

### **Documentazione**
- `README.md` - Documentazione principale
- `DEPLOYMENT_RAPIDO.md` - Guida deployment rapido
- `CONFIGURAZIONE_RETE.md` - Configurazione rete
- `GUIDA_FIRMA.md` - Gestione firma digitale
- `GUIDA_RFID.md` - Integrazione lettore RFID
- `RISOLUZIONE_DLL.md` - Troubleshooting DLL
- Altri file `.md`

---

## 🚀 INSTALLAZIONE SU PC TARGET

### **PREREQUISITI**

#### **1. Sistema Operativo**
- Windows 10/11 (64-bit consigliato)
- Account amministratore

#### **2. Software Richiesto**
- **Python 3.11 o 3.14**
  - Download: https://www.python.org/downloads/
  - ⚠️ Selezionare "Add Python to PATH"
  
- **Visual C++ Redistributable 2015-2022**
  - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - Necessario per IDReader.dll

#### **3. Rete**
- Connessione al database SQL Server
- Accesso SMTP per invio email
- Porta 5000 disponibile (o configurabile)

---

## 📥 PROCEDURA INSTALLAZIONE

### **Step 1: Estrai Pacchetto**

```
1. Copia Kiosk_Deploy_YYYYMMDD_HHMMSS.zip sul PC target
2. Estrai in: C:\Kiosk\
3. Risultato: C:\Kiosk\app.py, C:\Kiosk\templates\, ecc.
```

### **Step 2: Installa Prerequisiti**

```batch
# Verifica Python installato
python --version

# Se non installato:
1. Scarica Python 3.11/3.14
2. Esegui installer
3. ✅ Seleziona "Add Python to PATH"
4. Riavvia PC

# Installa VC++ Redistributable
1. Scarica vc_redist.x64.exe
2. Esegui installer
3. Riavvia PC
```

### **Step 3: Esegui Installazione**

```batch
cd C:\Kiosk
INSTALLA_KIOSK.bat
```

Lo script:
- ✅ Verifica Python
- ✅ Aggiorna pip
- ✅ Installa dipendenze da requirements.txt
- ✅ Crea cartelle necessarie
- ✅ Verifica configurazione

### **Step 4: Configura Database**

Se `db_config.enc` non è presente:

```batch
python
>>> from config_manager import ConfigManager
>>> config = ConfigManager()
>>> config.save_db_config(
...     server='SQL_SERVER_IP',
...     database='DatabaseName',
...     username='username',
...     password='password'
... )
>>> exit()
```

### **Step 5: Testa Applicazione**

```batch
START_APP.bat
```

Apri browser: `http://localhost:5000`

---

## 🔧 CONFIGURAZIONE

### **Stampante**

Modifica `print_config.json`:
```json
{
    "default_printer": "Nome Stampante",
    "silent_print": true
}
```

### **Porta Applicazione**

Modifica `app.py` (ultima riga):
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### **Lettore RFID**

Se hai IDReader.dll:
1. Verifica dipendenze: `python check_dll_deps.py`
2. Leggi `RISOLUZIONE_DLL.md`
3. Completa `rfid_reader.py` con documentazione DLL

---

## 🌐 ACCESSO DA RETE

### **Configurazione Firewall**

```batch
# Apri porta 5000
netsh advfirewall firewall add rule name="Kiosk HR" dir=in action=allow protocol=TCP localport=5000
```

### **Accesso da Altri PC**

```
http://IP_PC_KIOSK:5000
```

Esempio: `http://192.168.1.100:5000`

---

## 🔄 AVVIO AUTOMATICO

### **Opzione 1: Task Scheduler**

```
1. Apri Task Scheduler
2. Crea Task Base
3. Trigger: All'avvio
4. Azione: C:\Kiosk\START_APP.bat
5. Esegui con privilegi più elevati
```

### **Opzione 2: Servizio Windows**

Usa NSSM (Non-Sucking Service Manager):
```batch
nssm install KioskHR "C:\Kiosk\START_APP.bat"
nssm start KioskHR
```

---

## ✅ VERIFICA INSTALLAZIONE

### **Checklist**

- [ ] Python 3.11/3.14 installato
- [ ] VC++ Redistributable installato
- [ ] Pacchetto estratto in C:\Kiosk\
- [ ] `INSTALLA_KIOSK.bat` eseguito con successo
- [ ] Database configurato (`db_config.enc` presente)
- [ ] Stampante configurata (`print_config.json`)
- [ ] Applicazione avviata (`START_APP.bat`)
- [ ] Pagina launcher accessibile (http://localhost:5000)
- [ ] Tutti e 4 i servizi funzionanti
- [ ] Firewall configurato (se accesso rete)

### **Test Funzionalità**

1. **Servizio 1: Adeverințe**
   - Inserisci badge
   - Seleziona tipo certificato
   - Genera PDF
   - Verifica stampa

2. **Servizio 2: Raport Absențe**
   - Inserisci badge
   - Genera report
   - Verifica stampa

3. **Servizio 3: Cerere Absență**
   - Inserisci badge
   - Compila form
   - Invia richiesta
   - Verifica email manager

4. **Servizio 4: Verificare Stare**
   - Inserisci numero richiesta
   - Verifica stato

---

## 🆘 TROUBLESHOOTING

### **Errore: Python non trovato**
```
Soluzione: Reinstalla Python con "Add to PATH"
```

### **Errore: Modulo non trovato**
```
Soluzione: cd C:\Kiosk && pip install -r requirements.txt
```

### **Errore: Connessione database**
```
Soluzione: Verifica db_config.enc e connettività rete
```

### **Errore: IDReader.dll**
```
Soluzione: Leggi RISOLUZIONE_DLL.md
```

### **Porta 5000 occupata**
```
Soluzione: Modifica porta in app.py
```

---

## 📞 SUPPORTO

**Documentazione Completa**: Vedi file `.md` nel pacchetto

**File Importanti**:
- `README.md` - Panoramica generale
- `DEPLOYMENT_RAPIDO.md` - Guida veloce
- `CONFIGURAZIONE_RETE.md` - Setup rete aziendale
- `GUIDA_RFID.md` - Integrazione lettore RFID

---

## 🎯 RIEPILOGO RAPIDO

```batch
# 1. Estrai pacchetto
Unzip Kiosk_Deploy_*.zip → C:\Kiosk\

# 2. Installa
cd C:\Kiosk
INSTALLA_KIOSK.bat

# 3. Avvia
START_APP.bat

# 4. Accedi
http://localhost:5000
```

---

**PACCHETTO PRONTO PER DEPLOYMENT!** 📦✅🚀
