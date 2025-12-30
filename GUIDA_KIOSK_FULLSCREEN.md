# 🖥️ MODALITÀ KIOSK FULLSCREEN - GUIDA COMPLETA

## 📋 OVERVIEW

Per nascondere la barra degli indirizzi, i controlli del browser e mostrare solo il contenuto dell'applicazione, usa la **modalità kiosk fullscreen**.

---

## ✅ SCRIPT CREATI

| File | Browser | Descrizione |
|------|---------|-------------|
| `START_KIOSK_FULLSCREEN.bat` | Chrome | Solo browser kiosk |
| `START_KIOSK_EDGE.bat` | Edge | Solo browser kiosk |
| `START_SISTEMA_KIOSK.bat` | Chrome | App + Browser completo |

---

## 🚀 OPZIONE 1: CHROME KIOSK MODE (CONSIGLIATO)

### **Comando**

```batch
chrome.exe --kiosk --kiosk-printing http://localhost:5000
```

### **Parametri**

- `--kiosk` - Modalità fullscreen senza controlli
- `--kiosk-printing` - Abilita stampa silenziosa
- `http://localhost:5000` - URL applicazione

### **Uso**

```batch
# Doppio click su:
START_KIOSK_FULLSCREEN.bat
```

### **Vantaggi**

✅ Fullscreen completo  
✅ Nessuna barra indirizzo  
✅ Nessun controllo browser  
✅ Stampa silenziosa abilitata  
✅ Ideale per kiosk pubblici  

### **Uscita**

- **Alt + F4** - Chiude Chrome
- **Ctrl + Alt + Del** - Task Manager

---

## 🌐 OPZIONE 2: EDGE KIOSK MODE

### **Comando**

```batch
msedge.exe --kiosk http://localhost:5000 --edge-kiosk-type=fullscreen
```

### **Parametri**

- `--kiosk` - Modalità kiosk
- `--edge-kiosk-type=fullscreen` - Tipo fullscreen
- Alternative: `--edge-kiosk-type=public-browsing` (con reset)

### **Uso**

```batch
# Doppio click su:
START_KIOSK_EDGE.bat
```

---

## 🎯 OPZIONE 3: SISTEMA COMPLETO (APP + BROWSER)

### **Comando**

Usa `START_SISTEMA_KIOSK.bat` che:

1. ✅ Avvia Flask app in background
2. ✅ Attende 10 secondi (server ready)
3. ✅ Chiude Chrome precedenti
4. ✅ Avvia Chrome in kiosk mode

### **Uso**

```batch
# Doppio click su:
START_SISTEMA_KIOSK.bat
```

**Perfetto per**: Avvio automatico all'accensione PC

---

## ⚙️ PARAMETRI AGGIUNTIVI

### **Chrome**

```batch
# Fullscreen + Disabilita gesture
chrome.exe --kiosk --disable-pinch --overscroll-history-navigation=0 http://localhost:5000

# Fullscreen + Nascondi cursore dopo inattività
chrome.exe --kiosk --hide-scrollbars http://localhost:5000

# Fullscreen + Disabilita context menu
chrome.exe --kiosk --disable-features=TranslateUI http://localhost:5000
```

### **Edge**

```batch
# Public browsing (reset automatico)
msedge.exe --kiosk http://localhost:5000 --edge-kiosk-type=public-browsing --kiosk-idle-timeout-minutes=5

# Digital signage (no interazione)
msedge.exe --kiosk http://localhost:5000 --edge-kiosk-type=digital-signage
```

---

## 🔒 BLOCCO TASTI (OPZIONALE)

Per bloccare Alt+F4 e altre combinazioni, usa software dedicati:

### **Opzione A: Windows Kiosk Mode**

Windows 10/11 Pro ha modalità kiosk integrata:

```
1. Impostazioni → Account → Famiglia e altri utenti
2. Configura un chiosco
3. Seleziona app (Chrome/Edge)
4. Configura URL
```

### **Opzione B: Software Terze Parti**

- **KioWare** - https://www.kioware.com/
- **Porteus Kiosk** - https://porteus-kiosk.org/
- **SiteKiosk** - https://www.sitekiosk.com/

---

## 📱 AVVIO AUTOMATICO

### **Metodo 1: Cartella Esecuzione Automatica**

```batch
# Copia shortcut in:
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\

# Oppure:
shell:startup
```

### **Metodo 2: Task Scheduler**

```
1. Task Scheduler → Crea attività di base
2. Nome: Kiosk HR
3. Trigger: All'avvio
4. Azione: Avvia programma
5. Programma: C:\Kiosk\START_SISTEMA_KIOSK.bat
6. ✅ Esegui con privilegi più elevati
```

### **Metodo 3: Registro di Sistema**

```batch
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v KioskHR /t REG_SZ /d "C:\Kiosk\START_SISTEMA_KIOSK.bat" /f
```

---

## 🎨 PERSONALIZZAZIONE CSS

Per nascondere elementi UI tramite CSS (backup):

```css
/* Nascondi scrollbar */
::-webkit-scrollbar {
    display: none;
}

body {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

/* Disabilita selezione testo */
* {
    user-select: none;
    -webkit-user-select: none;
}

/* Nascondi context menu */
body {
    -webkit-touch-callout: none;
}
```

---

## 🧪 TEST

### **Test Chrome Kiosk**

```batch
# 1. Avvia app
python app.py

# 2. In un altro terminale
START_KIOSK_FULLSCREEN.bat

# 3. Verifica
- Nessuna barra indirizzo? ✅
- Fullscreen? ✅
- Stampa funziona? ✅
```

### **Test Sistema Completo**

```batch
# 1. Chiudi tutto
taskkill /F /IM python.exe
taskkill /F /IM chrome.exe

# 2. Avvia sistema
START_SISTEMA_KIOSK.bat

# 3. Verifica
- Flask avviato? ✅
- Chrome aperto? ✅
- Fullscreen? ✅
```

---

## 🆘 TROUBLESHOOTING

### **Chrome non trovato**

```batch
# Verifica path Chrome
dir "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Se diverso, modifica script:
start "" "PATH_CORRETTO\chrome.exe" --kiosk http://localhost:5000
```

### **Edge non trovato**

```batch
# Verifica path Edge
dir "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Oppure:
dir "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
```

### **Porta 5000 occupata**

Modifica URL negli script:
```batch
# Cambia da:
http://localhost:5000

# A:
http://localhost:8080
```

E modifica `app.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=False)
```

---

## 📋 CHECKLIST DEPLOYMENT KIOSK

- [ ] Script `START_SISTEMA_KIOSK.bat` testato
- [ ] Chrome/Edge installato
- [ ] Modalità fullscreen funzionante
- [ ] Stampa silenziosa testata
- [ ] Avvio automatico configurato
- [ ] Tasti bloccati (se necessario)
- [ ] Timeout inattività configurato (opzionale)
- [ ] Backup exit strategy (Ctrl+Alt+Del)

---

## 🎯 RIEPILOGO COMANDI

### **Solo Browser**

```batch
# Chrome
chrome.exe --kiosk --kiosk-printing http://localhost:5000

# Edge
msedge.exe --kiosk http://localhost:5000 --edge-kiosk-type=fullscreen
```

### **Sistema Completo**

```batch
# Avvia tutto
START_SISTEMA_KIOSK.bat
```

### **Uscita**

```
Alt + F4          - Chiude browser
Ctrl + Alt + Del  - Task Manager
```

---

**MODALITÀ KIOSK CONFIGURATA!** 🖥️✅🔒
