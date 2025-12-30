# 🌐 CONFIGURAZIONE ACCESSO RETE AZIENDALE

## 📋 PANORAMICA

Questa guida spiega come configurare l'applicazione Kiosk HR per essere accessibile da tutti i computer della rete aziendale.

---

## 🎯 OBIETTIVO

**Scenario:**
- PC Kiosk: `192.168.10.50` (esempio)
- Altri PC rete: `192.168.10.x`
- Tutti devono accedere a: `http://192.168.10.50:5000`

---

## ⚙️ CONFIGURAZIONE PC KIOSK

### **STEP 1: Identifica IP del PC Kiosk**

Apri **Prompt dei comandi** sul PC Kiosk:

```batch
ipconfig
```

**Output esempio:**
```
Scheda Ethernet Ethernet:
   Indirizzo IPv4. . . . . . . . . : 192.168.10.50
   Subnet Mask . . . . . . . . . . : 255.255.255.0
   Gateway predefinito . . . . . . : 192.168.10.1
```

**Annota l'IP**: `192.168.10.50`

---

### **STEP 2: Configura Firewall Windows**

#### **Metodo A: PowerShell (Consigliato)**

**Apri PowerShell come Amministratore:**

1. Click destro su **Start**
2. Seleziona **Windows PowerShell (amministratore)**

**Esegui comando:**

```powershell
# Crea regola firewall per Flask (porta 5000)
New-NetFirewallRule `
    -DisplayName "Kiosk HR - Flask Server" `
    -Direction Inbound `
    -LocalPort 5000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Domain,Private,Public `
    -Enabled True

# Verifica regola creata
Get-NetFirewallRule -DisplayName "Kiosk HR - Flask Server" | Format-List
```

**Output atteso:**
```
DisplayName  : Kiosk HR - Flask Server
Enabled      : True
Direction    : Inbound
Action       : Allow
```

#### **Metodo B: Interfaccia Grafica**

1. **Apri Windows Defender Firewall**
   - Cerca "Firewall" nel menu Start
   - Click "Windows Defender Firewall con sicurezza avanzata"

2. **Crea Regola In Entrata**
   - Click su "Regole connessioni in entrata" (sinistra)
   - Click "Nuova regola..." (destra)

3. **Configurazione Regola**
   - **Tipo di regola**: Porta → Avanti
   - **Protocollo**: TCP
   - **Porte locali specifiche**: `5000` → Avanti
   - **Azione**: Consenti la connessione → Avanti
   - **Profili**: ✅ Dominio, ✅ Privato, ✅ Pubblico → Avanti
   - **Nome**: `Kiosk HR - Flask Server`
   - **Descrizione**: `Accesso applicazione Kiosk HR dalla rete aziendale`
   - Click **Fine**

4. **Verifica Regola**
   - Cerca "Kiosk HR" nella lista
   - Verifica che sia **Abilitata** (segno di spunta verde)

---

### **STEP 3: Verifica Configurazione Flask**

Assicurati che `app.py` sia configurato per accettare connessioni da rete:

**File: `app.py` (ultima riga)**

```python
if __name__ == '__main__':
    # Crea directory temp se non esiste
    os.makedirs('temp', exist_ok=True)
    
    # Avvia server
    # host='0.0.0.0' permette accesso da rete
    app.run(host='0.0.0.0', port=5000, debug=True)
```

✅ **Già configurato correttamente!**

---

### **STEP 4: Avvia Applicazione**

**Doppio click su:**
```
START_APP.bat
```

**Verifica output:**
```
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://192.168.10.50:5000
```

✅ Se vedi `Running on all addresses`, la configurazione è corretta!

---

## 🖥️ TEST ACCESSO DA ALTRI PC

### **STEP 1: Test da PC Kiosk (Locale)**

Sul PC Kiosk, apri browser e vai a:

```
http://localhost:5000
```

✅ Dovrebbe mostrare la pagina launcher

### **STEP 2: Test da Altro PC (Rete)**

Da un altro PC sulla stessa rete:

1. Apri browser (Chrome, Edge, Firefox)
2. Vai a: `http://192.168.10.50:5000`
3. Dovrebbe mostrare la stessa pagina launcher

### **STEP 3: Test Connettività**

Se non funziona, testa connettività:

**Da altro PC, apri Prompt comandi:**

```batch
# Test ping
ping 192.168.10.50

# Test porta (PowerShell)
Test-NetConnection -ComputerName 192.168.10.50 -Port 5000
```

**Output atteso:**
```
TcpTestSucceeded : True
```

---

## 🔧 RISOLUZIONE PROBLEMI

### **Problema 1: "Impossibile raggiungere il sito"**

**Causa**: Firewall blocca connessioni

**Soluzione:**
1. Verifica regola firewall creata (vedi STEP 2)
2. Verifica app in esecuzione: `START_APP.bat`
3. Verifica IP corretto: `ipconfig`

**Test firewall:**
```powershell
# Disabilita temporaneamente firewall (SOLO PER TEST!)
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Test accesso da altro PC
# Se funziona, il problema è il firewall

# Riabilita firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

### **Problema 2: "ERR_CONNECTION_REFUSED"**

**Causa**: Applicazione non in esecuzione o porta sbagliata

**Soluzione:**
1. Verifica `START_APP.bat` in esecuzione
2. Verifica porta 5000 in ascolto:
   ```batch
   netstat -an | findstr :5000
   ```
   Output atteso: `TCP 0.0.0.0:5000 ... LISTENING`

### **Problema 3: IP cambia continuamente**

**Causa**: DHCP assegna IP dinamico

**Soluzione: Configura IP Statico**

1. **Pannello di controllo** → **Centro connessioni di rete**
2. Click su connessione attiva (Ethernet/Wi-Fi)
3. **Proprietà** → **Protocollo Internet versione 4 (TCP/IPv4)**
4. Seleziona **Utilizza il seguente indirizzo IP**:
   - **Indirizzo IP**: `192.168.10.50`
   - **Subnet mask**: `255.255.255.0`
   - **Gateway predefinito**: `192.168.10.1`
   - **Server DNS preferito**: `192.168.10.1` (o DNS aziendale)
5. Click **OK**

**OPPURE via PowerShell:**

```powershell
# Trova nome interfaccia
Get-NetAdapter

# Configura IP statico (adatta InterfaceAlias)
New-NetIPAddress `
    -InterfaceAlias "Ethernet" `
    -IPAddress 192.168.10.50 `
    -PrefixLength 24 `
    -DefaultGateway 192.168.10.1

# Configura DNS
Set-DnsClientServerAddress `
    -InterfaceAlias "Ethernet" `
    -ServerAddresses 192.168.10.1
```

---

## 📱 ACCESSO DA DISPOSITIVI MOBILI

L'applicazione è accessibile anche da smartphone/tablet sulla rete Wi-Fi aziendale:

```
http://192.168.10.50:5000
```

**Nota**: Assicurati che i dispositivi mobili siano sulla stessa rete (stesso range IP `192.168.10.x`)

---

## 🔐 SICUREZZA

### **Raccomandazioni**

✅ **FARE:**
- Usare solo su rete interna aziendale
- Configurare firewall per bloccare accesso esterno
- Monitorare log accessi: `app_debug.log`
- Usare credenziali database criptate

❌ **NON FARE:**
- Esporre su Internet pubblico senza VPN
- Usare su reti Wi-Fi pubbliche
- Condividere credenziali database

### **Configurazione Firewall Avanzata (Opzionale)**

Limita accesso solo a range IP aziendale:

```powershell
# Rimuovi regola esistente
Remove-NetFirewallRule -DisplayName "Kiosk HR - Flask Server"

# Crea regola con restrizione IP
New-NetFirewallRule `
    -DisplayName "Kiosk HR - Flask Server (Restricted)" `
    -Direction Inbound `
    -LocalPort 5000 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 192.168.10.0/24 `
    -Profile Domain,Private `
    -Enabled True
```

Questo permette accesso solo da IP `192.168.10.1` - `192.168.10.254`

---

## 📊 MONITORAGGIO ACCESSI

### **Log Connessioni**

Visualizza log in tempo reale:

```batch
powershell Get-Content app_debug.log -Wait -Tail 50
```

**Esempio log:**
```
2025-12-26 13:30:15 - werkzeug - INFO - 192.168.10.25 - - [26/Dec/2025 13:30:15] "GET / HTTP/1.1" 200 -
2025-12-26 13:30:20 - werkzeug - INFO - 192.168.10.30 - - [26/Dec/2025 13:30:20] "POST /api/validate-badge HTTP/1.1" 200 -
```

Puoi vedere:
- IP client (`192.168.10.25`, `192.168.10.30`)
- Timestamp
- Endpoint richiesto
- Status code

---

## 🎯 CONFIGURAZIONE DNS (Opzionale)

Per accedere con nome invece di IP:

### **Metodo 1: File HOSTS (Ogni PC)**

Su ogni PC client, modifica:
```
C:\Windows\System32\drivers\etc\hosts
```

Aggiungi:
```
192.168.10.50    kiosk-hr.local
```

Accesso:
```
http://kiosk-hr.local:5000
```

### **Metodo 2: DNS Server Aziendale**

Configura record A nel DNS server:
- **Nome**: `kiosk-hr`
- **Tipo**: A
- **IP**: `192.168.10.50`

Accesso:
```
http://kiosk-hr.azienda.local:5000
```

---

## ✅ CHECKLIST CONFIGURAZIONE RETE

### **PC Kiosk**
- [ ] IP identificato (es. `192.168.10.50`)
- [ ] IP statico configurato (opzionale ma consigliato)
- [ ] Firewall Windows configurato (porta 5000)
- [ ] Regola firewall verificata e abilitata
- [ ] `app.py` configurato con `host='0.0.0.0'`
- [ ] `START_APP.bat` avviato
- [ ] Accesso locale testato: http://localhost:5000

### **PC Client (Test)**
- [ ] Ping a PC Kiosk funzionante
- [ ] Test porta 5000 funzionante
- [ ] Accesso browser funzionante: http://192.168.10.50:5000
- [ ] Tutti i servizi accessibili
- [ ] Stampa funzionante (se configurata)

### **Rete**
- [ ] Tutti i PC sulla stessa subnet
- [ ] Gateway configurato correttamente
- [ ] DNS funzionante (opzionale)
- [ ] Firewall aziendale permette traffico interno

---

## 🎉 CONFIGURAZIONE COMPLETATA!

L'applicazione è ora accessibile da tutta la rete aziendale!

**URL Accesso:**
- **PC Kiosk**: http://localhost:5000
- **Rete Aziendale**: http://192.168.10.50:5000
- **Con DNS** (opzionale): http://kiosk-hr.local:5000

---

## 📞 SUPPORTO

**Problemi comuni:**
1. Firewall → Verifica regola creata
2. IP cambia → Configura IP statico
3. Connessione rifiutata → Verifica app in esecuzione
4. Timeout → Verifica rete e ping

**Log:**
```
C:\Kiosk\Adeverente\app_debug.log
```

---

*Ultimo aggiornamento: 26 Dicembre 2025*
