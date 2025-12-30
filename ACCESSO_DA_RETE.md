# 🌐 ACCESSO DA RETE - GUIDA COMPLETA

## ✅ SÌ, PUOI ACCEDERE DA ALTRI PC!

L'applicazione Flask è già configurata per accettare connessioni da qualsiasi IP sulla rete.

```python
# In app.py (ultima riga)
app.run(host='0.0.0.0', port=5000, debug=True)
```

`host='0.0.0.0'` significa: **accetta connessioni da qualsiasi IP**.

---

## 🔍 TROVA L'IP DEL KIOSK

### **Metodo 1: Script Automatico** (FACILE)

```batch
# Doppio click su:
MOSTRA_IP_KIOSK.bat
```

Lo script:
- ✅ Mostra l'IP del kiosk
- ✅ Mostra URL di accesso
- ✅ Verifica firewall
- ✅ Può aprire porta automaticamente

### **Metodo 2: Command Prompt**

```batch
ipconfig
```

Cerca "IPv4 Address":
```
Ethernet adapter Ethernet:
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
                                       ^^^^^^^^^^^^
                                       Questo è l'IP!
```

### **Metodo 3: PowerShell**

```powershell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress
```

---

## 🌐 URL DI ACCESSO

### **Dal Kiosk Stesso**

```
http://localhost:5000
http://127.0.0.1:5000
```

### **Da Altri PC sulla Rete**

```
http://IP_DEL_KIOSK:5000
```

**Esempi**:
```
http://192.168.1.100:5000
http://192.168.0.50:5000
http://10.0.0.25:5000
```

---

## 🔥 CONFIGURAZIONE FIREWALL

### **Verifica Stato Porta**

```batch
netsh advfirewall firewall show rule name="Kiosk HR"
```

**Output se aperta**:
```
Rule Name:                            Kiosk HR
Enabled:                              Yes
Direction:                            In
Profiles:                             Domain,Private,Public
LocalPort:                            5000
Protocol:                             TCP
Action:                               Allow
```

**Output se chiusa**:
```
No rules match the specified criteria.
```

### **Apri Porta 5000** (Richiede Amministratore)

```batch
# Esegui come Amministratore
netsh advfirewall firewall add rule name="Kiosk HR" dir=in action=allow protocol=TCP localport=5000
```

**Conferma**:
```
Ok.
```

### **Chiudi Porta** (se necessario)

```batch
netsh advfirewall firewall delete rule name="Kiosk HR"
```

---

## 🧪 TEST CONNESSIONE

### **Step 1: Avvia Kiosk**

Sul PC kiosk:
```batch
START_APP.bat
```

### **Step 2: Trova IP**

Sul PC kiosk:
```batch
MOSTRA_IP_KIOSK.bat
```

Esempio output:
```
IP Kiosk: 192.168.1.100
URL: http://192.168.1.100:5000
```

### **Step 3: Apri Firewall**

Sul PC kiosk (come Amministratore):
```batch
netsh advfirewall firewall add rule name="Kiosk HR" dir=in action=allow protocol=TCP localport=5000
```

### **Step 4: Testa da Altro PC**

Su un altro PC sulla stessa rete:

1. Apri browser (Chrome, Edge, Firefox)
2. Vai a: `http://192.168.1.100:5000`
3. Dovresti vedere la pagina launcher

---

## 📱 ACCESSO DA DISPOSITIVI MOBILI

### **Smartphone/Tablet**

1. Connetti dispositivo alla **stessa rete WiFi**
2. Apri browser mobile
3. Vai a: `http://IP_KIOSK:5000`

**Esempio**:
```
http://192.168.1.100:5000
```

### **QR Code** (Opzionale)

Puoi generare un QR code con l'URL per accesso rapido:

1. Vai su: https://www.qr-code-generator.com/
2. Inserisci: `http://192.168.1.100:5000`
3. Genera QR code
4. Stampa e attacca vicino al kiosk

---

## 🔒 SICUREZZA

### **Rete Locale**

L'accesso è limitato alla **rete locale** (LAN):
- ✅ PC sulla stessa rete possono accedere
- ❌ PC su internet NON possono accedere

### **Firewall Windows**

Il firewall Windows protegge:
- ✅ Solo porta 5000 aperta
- ✅ Solo connessioni TCP
- ✅ Solo traffico in entrata

### **Autenticazione** (Opzionale)

Se vuoi aggiungere autenticazione:

```python
# In app.py
from functools import wraps
from flask import request, abort

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.password != 'password_sicura':
            abort(401)
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@require_auth
def launcher():
    return render_template('launcher.html')
```

---

## 🌍 ACCESSO DA INTERNET (Avanzato)

### **⚠️ NON CONSIGLIATO per Kiosk**

Se vuoi accesso da internet:

1. **Port Forwarding** sul router
   - Porta esterna: 8080
   - Porta interna: 5000
   - IP interno: 192.168.1.100

2. **IP Pubblico**
   - Trova IP pubblico: https://whatismyipaddress.com/
   - URL: `http://IP_PUBBLICO:8080`

3. **HTTPS** (Obbligatorio)
   - Usa Cloudflare Tunnel
   - O certificato SSL

**Rischi**:
- ❌ Esposizione a internet
- ❌ Attacchi possibili
- ❌ Necessita autenticazione forte

---

## 📊 SCENARI D'USO

### **Scenario 1: Kiosk Singolo**

```
Kiosk PC (192.168.1.100)
└── Accesso: http://localhost:5000
```

### **Scenario 2: Kiosk + PC Ufficio**

```
Kiosk PC (192.168.1.100)
├── Accesso locale: http://localhost:5000
│
PC Ufficio (192.168.1.50)
└── Accesso remoto: http://192.168.1.100:5000
```

### **Scenario 3: Kiosk + Multipli PC**

```
Kiosk PC (192.168.1.100)
├── Accesso locale: http://localhost:5000
│
PC Ufficio 1 (192.168.1.51)
├── Accesso: http://192.168.1.100:5000
│
PC Ufficio 2 (192.168.1.52)
├── Accesso: http://192.168.1.100:5000
│
Tablet (WiFi)
└── Accesso: http://192.168.1.100:5000
```

---

## 🆘 TROUBLESHOOTING

### **Problema: "Impossibile raggiungere il sito"**

**Causa**: Firewall blocca connessione

**Soluzione**:
```batch
# Come Amministratore
netsh advfirewall firewall add rule name="Kiosk HR" dir=in action=allow protocol=TCP localport=5000
```

### **Problema: "Connessione rifiutata"**

**Causa**: Flask non in ascolto

**Soluzione**:
```batch
# Verifica che Flask sia avviato
START_APP.bat
```

### **Problema: "Timeout"**

**Causa**: IP errato o rete diversa

**Soluzione**:
1. Verifica IP: `ipconfig`
2. Verifica stessa rete
3. Ping test: `ping 192.168.1.100`

### **Problema: Funziona solo su kiosk**

**Causa**: `host='127.0.0.1'` invece di `'0.0.0.0'`

**Soluzione**: Verifica `app.py`:
```python
# CORRETTO
app.run(host='0.0.0.0', port=5000)

# SBAGLIATO
app.run(host='127.0.0.1', port=5000)
```

---

## ✅ CHECKLIST ACCESSO RETE

- [ ] Flask avviato (`START_APP.bat`)
- [ ] IP kiosk identificato (`ipconfig`)
- [ ] Firewall configurato (porta 5000 aperta)
- [ ] Stesso network (PC sulla stessa rete)
- [ ] URL corretto (`http://IP:5000`)
- [ ] Browser aggiornato
- [ ] Test da altro PC funzionante

---

## 🎯 RIEPILOGO

**SÌ, PUOI ACCEDERE DA ALTRI PC!**

```
1. Trova IP kiosk
   → MOSTRA_IP_KIOSK.bat

2. Apri firewall
   → netsh advfirewall firewall add rule...

3. Accedi da altro PC
   → http://IP_KIOSK:5000

4. Funziona! ✅
```

---

**ACCESSO DA RETE CONFIGURATO!** 🌐✅
