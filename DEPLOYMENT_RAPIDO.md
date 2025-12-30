# 🚀 GUIDA RAPIDA DEPLOYMENT KIOSK HR

## 📋 PANORAMICA

Questa guida spiega come installare e configurare l'applicazione Kiosk HR sul PC target e renderla accessibile dalla rete aziendale.

### **SERVIZI DISPONIBILI**

1. **📄 Adeverințe** - Generazione certificati medici e di lavoro
2. **📊 Raport Absențe** - Report storico ferie, malattie e permessi
3. **🔧 Serviciu 3** - In sviluppo
4. **⚙️ Serviciu 4** - In sviluppo

---

## 🖥️ PARTE 1: PC SVILUPPO (Creazione Pacchetto)

### **1. Prepara il Pacchetto**

```batch
cd C:\Users\gtesta\PythonProjetcs\Python\Adeverente
CREA_PACCHETTO_DEPLOY.bat
```

Questo crea un file ZIP: `Kiosk_Deploy_YYYYMMDD_HHMMSS.zip`

### **2. File Inclusi nel Pacchetto**

- ✅ Tutti i file Python (`.py`)
- ✅ Templates HTML (`templates/`)
- ✅ CSS e JavaScript (`static/`)
- ✅ Font DejaVuSans (`.ttf`)
- ✅ Logo aziendale (`logo.png`)
- ✅ Script di installazione (`INSTALLA_KIOSK.bat`)
- ✅ Script di avvio (`START_APP.bat`)
- ✅ Configurazioni (`requirements.txt`, `print_config.json`)
- ✅ Documentazione completa

### **3. Trasferisci il Pacchetto**

Copia il file ZIP sul PC Kiosk (es. via USB, rete condivisa, ecc.)

---

## 🖥️ PARTE 2: PC KIOSK (Installazione)

### **PREREQUISITI**

- ✅ Windows 10/11
- ✅ Python 3.11 o 3.14 installato
- ✅ Connessione al database SQL Server
- ✅ Stampante predefinita configurata

### **INSTALLAZIONE AUTOMATICA**

#### **1. Estrai il Pacchetto**

```
C:\Kiosk\Adeverente\
```

#### **2. Esegui Installazione**

**Doppio click su:**
```
INSTALLA_KIOSK.bat
```

Lo script:
- ✅ Verifica Python
- ✅ Aggiorna pip
- ✅ Installa dipendenze
- ✅ Verifica configurazione database
- ✅ Testa connessione

#### **3. Configura Database** (se necessario)

Se non hai i file di configurazione:

```batch
python setup.py
```

Inserisci:
- Server SQL
- Database
- Username
- Password

---

## 🌐 PARTE 3: ACCESSO DALLA RETE AZIENDALE

### **CONFIGURAZIONE SERVER**

#### **1. Trova l'IP del PC Kiosk**

```batch
ipconfig
```

Cerca: `IPv4 Address` (es. `192.168.10.50`)

#### **2. Configura Firewall Windows**

**Apri PowerShell come Amministratore:**

```powershell
# Crea regola firewall per porta 5000
New-NetFirewallRule -DisplayName "Kiosk HR App" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# Verifica regola creata
Get-NetFirewallRule -DisplayName "Kiosk HR App"
```

**OPPURE manualmente:**

1. Apri **Windows Defender Firewall**
2. Click **Impostazioni avanzate**
3. Click **Regole connessioni in entrata**
4. Click **Nuova regola...**
5. Tipo: **Porta**
6. Protocollo: **TCP**, Porta: **5000**
7. Azione: **Consenti connessione**
8. Profili: **Dominio, Privato, Pubblico**
9. Nome: **Kiosk HR App**

#### **3. Avvia Applicazione**

**Doppio click su:**
```
START_APP.bat
```

L'app sarà disponibile su:
- **PC Kiosk**: http://localhost:5000
- **Rete aziendale**: http://192.168.10.50:5000

### **VERIFICA ACCESSO RETE**

Da un altro PC sulla rete:

1. Apri browser
2. Vai a: `http://192.168.10.50:5000`
3. Dovresti vedere la pagina launcher

---

## 🔧 CONFIGURAZIONE AVANZATA

### **AVVIO AUTOMATICO ALL'ACCESSO**

#### **Metodo 1: Cartella Esecuzione Automatica**

1. Premi `Win + R`
2. Digita: `shell:startup`
3. Copia `START_APP.bat` nella cartella

#### **Metodo 2: Utilità di Pianificazione**

1. Apri **Utilità di pianificazione**
2. Click **Crea attività di base...**
3. Nome: **Kiosk HR App**
4. Trigger: **All'accesso**
5. Azione: **Avvia programma**
6. Programma: `C:\Kiosk\Adeverente\START_APP.bat`
7. Fine

### **CONFIGURAZIONE STAMPANTE**

Verifica stampante predefinita:

```batch
# Elenca stampanti
wmic printer get name,default

# Imposta stampante predefinita
rundll32 printui.dll,PrintUIEntry /y /n "Nome Stampante"
```

### **CONFIGURAZIONE KIOSK MODE (Opzionale)**

Per bloccare il PC in modalità kiosk:

1. Crea utente Windows dedicato: `KioskUser`
2. Configura **Accesso assegnato** (Windows Settings)
3. Seleziona browser in modalità kiosk
4. URL: `http://localhost:5000`

---

## 📱 ACCESSO DA DISPOSITIVI MOBILI

L'applicazione è accessibile anche da tablet/smartphone sulla rete:

```
http://192.168.10.50:5000
```

**Nota**: L'interfaccia è responsive e si adatta a schermi di diverse dimensioni.

---

## 🔍 RISOLUZIONE PROBLEMI

### **Problema: Applicazione non accessibile dalla rete**

**Soluzione:**
1. Verifica firewall (vedi sopra)
2. Verifica IP: `ipconfig`
3. Testa connessione: `ping 192.168.10.50` (da altro PC)
4. Verifica app in esecuzione: controlla `START_APP.bat`

### **Problema: Errore connessione database**

**Soluzione:**
1. Verifica `db_config.enc` esiste
2. Riesegui: `python setup.py`
3. Verifica connettività SQL Server

### **Problema: Caratteri rumeni non visualizzati**

**Soluzione:**
1. Verifica presenza file `DejaVuSans.ttf` e `DejaVuSans-Bold.ttf`
2. Se mancano, copiali dalla cartella di sviluppo

### **Problema: Stampa non funziona**

**Soluzione:**
1. Verifica stampante predefinita: `wmic printer get name,default`
2. Controlla `print_config.json`
3. Verifica driver stampante installati

---

## 📊 MONITORAGGIO

### **Log Applicazione**

I log sono salvati in:
```
C:\Kiosk\Adeverente\app_debug.log
```

Visualizza log in tempo reale:
```batch
powershell Get-Content app_debug.log -Wait -Tail 50
```

### **Statistiche Utilizzo**

Controlla file PDF generati:
```
C:\Kiosk\Adeverente\temp\
```

---

## 🔒 SICUREZZA

### **Credenziali Database**

- ✅ Criptate in `db_config.enc`
- ✅ Chiave in `encryption_key.key`
- ⚠️ **NON condividere questi file pubblicamente**

### **Accesso Rete**

- ✅ Solo rete interna aziendale
- ⚠️ NON esporre su Internet senza VPN/firewall

---

## 📞 SUPPORTO

Per problemi o domande:

1. Controlla `app_debug.log`
2. Verifica `GUIDA_RAPIDA.md`
3. Consulta `DEPLOYMENT.md` per dettagli avanzati

---

## ✅ CHECKLIST FINALE

### **PC Kiosk**
- [ ] Python 3.11/3.14 installato
- [ ] Pacchetto estratto in `C:\Kiosk\Adeverente`
- [ ] `INSTALLA_KIOSK.bat` eseguito con successo
- [ ] Database configurato (`db_config.enc` presente)
- [ ] Stampante predefinita configurata
- [ ] Firewall configurato (porta 5000)
- [ ] `START_APP.bat` avviato
- [ ] Applicazione accessibile su http://localhost:5000

### **Rete Aziendale**
- [ ] IP PC Kiosk identificato (es. 192.168.10.50)
- [ ] Firewall Windows configurato
- [ ] Accesso testato da altro PC: http://192.168.10.50:5000
- [ ] Tutti i servizi funzionanti

### **Funzionalità**
- [ ] ✅ Launcher page visibile
- [ ] ✅ Servizio Adeverințe funzionante
- [ ] ✅ Servizio Raport Absențe funzionante
- [ ] ✅ Validazione badge RFID
- [ ] ✅ Generazione PDF
- [ ] ✅ Stampa automatica
- [ ] ✅ Caratteri rumeni corretti
- [ ] ✅ Auto-redirect alla home

---

## 🎉 DEPLOYMENT COMPLETATO!

L'applicazione Kiosk HR è ora:
- ✅ Installata sul PC target
- ✅ Accessibile dalla rete aziendale
- ✅ Pronta per l'uso in produzione

**URL Accesso:**
- **Locale**: http://localhost:5000
- **Rete**: http://[IP-PC-KIOSK]:5000

---

*Ultimo aggiornamento: 26 Dicembre 2025*
