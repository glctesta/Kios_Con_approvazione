# Risoluzione Problemi Installazione

**Data:** 2026-01-09  
**Script:** INSTALLA.bat / INSTALLA_RAPIDA.bat

---

## 🔴 **Problema CRITICO: Virtual Environment in System32**

### Sintomi
```
[2/8] Creazione ambiente virtuale...
Actual environment location may have moved due to redirects, links or junctions.
  Requested location: "C:\Windows\System32\venv\Scripts\python.exe"
  Actual location:    "C:\Windows\SysWOW64\venv\Scripts\python.exe"

[3/8] Attivazione ambiente virtuale...
The system cannot find the path specified.
[ERRORE] Impossibile attivare ambiente virtuale
```

### Causa
Lo script viene eseguito dalla directory `C:\Windows\System32` invece che dalla cartella del progetto. Questo succede quando:
- Si esegue il .bat con "Esegui come amministratore" dal menu contestuale
- Windows UAC (User Account Control) cambia la directory corrente

### ✅ Soluzione 1: Usa Script Aggiornati (CONSIGLIATO)

Gli script `INSTALLA.bat` e `INSTALLA_RAPIDA.bat` sono stati aggiornati (2026-01-09) con:
- ✅ Rilevamento automatico di System32
- ✅ Messaggio di errore chiaro se in directory sbagliata
- ✅ Uso di `pushd` invece di `cd` per gestire UAC

**Passi:**
1. Scaricare l'ultima versione del package ZIP da GitHub
2. Estrarre in una cartella (es. `C:\Kiosk_HR`)
3. Eseguire il .bat da quella cartella

Se hai ancora la versione vecchia, **aggiorna il package ZIP**!

---

### ✅ Soluzione 2: PowerShell come Amministratore dalla Directory Corretta

**Metodo corretto per eseguire come Admin:**

1. Aprire Esplora Risorse
2. Navigare nella cartella del progetto (quella con `app.py`)
3. Tenere premuto **SHIFT**
4. Click destro in uno spazio vuoto della cartella
5. Selezionare **"Apri finestra PowerShell qui come amministratore"**
6. Eseguire: `.\INSTALLA.bat` oppure `.\INSTALLA_RAPIDA.bat`

**Perché funziona:**
- La directory corrente è GIÀ quella giusta
- UAC non cambia la directory
- Il venv viene creato nel posto giusto

---

### ✅ Soluzione 3: Copia Temporanea in C:\Temp

Se le altre soluzioni non funzionano:

1. **Copiare** l'intera cartella del progetto in `C:\Temp\Kiosk_HR`
2. Navigare in `C:\Temp\Kiosk_HR` con Esplora Risorse
3. Click destro su `INSTALLA_RAPIDA.bat`
4. "Esegui come amministratore"
5. Al termine, **copiare** la cartella installata nella posizione definitiva

**Perché funziona:**
- `C:\Temp` non ha restrizioni UAC particolari
- Evita problemi di redirect System32

---

### ❌ NON Funziona: Click Destro Diretto

**NON fare:**
```
❌ Click destro su INSTALLA.bat → "Esegui come amministratore"
```

**Perché fallisce:**
- Windows apre il .bat da System32
- La directory corrente diventa System32
- Il venv viene creato nel posto sbagliato

---

## 🐛 Problema: Script si Blocca su "Aggiornamento pip"


### Sintomi
- Lo script INSTALLA.bat si blocca alla fase `[4/8] Aggiornamento pip...`
- Non mostra errori, ma non avanza
- Il cursore lampeggia ma non succede nulla

### Causa
L'aggiornamento di pip può richiedere molto tempo o bloccarsi per diversi motivi:
- Connessione internet lenta
- Proxy aziendale che blocca PyPI
- Conflitti  con versioni precedenti di pip
- Cache corrotta
- Pip che tenta di aggiornarsi mentre è in esecuzione

---

## ✅ Soluzioni (in ordine di preferenza)

### Soluzione 1: Usa INSTALLA_RAPIDA.bat (CONSIGLIATO)

Questo script **salta completamente l'aggiornamento di pip** e procede direttamente all'installazione.

**Passi:**
1. Chiudere il prompt bloccato (Ctrl+C oppure chiudi finestra)
2. Fare click destro su `INSTALLA_RAPIDA.bat`
3. Selezionare "Esegui come amministratore"
4. Attendere completamento

**Vantaggi:**
- ✅ Non si blocca
- ✅ Più veloce
- ✅ Usa la versione pip già presente con Python 3.11

**Quando usarla:**
- Sempre come prima scelta se INSTALLA.bat si blocca
- Installazioni su PC senza connessione a PyPI
- Ambienti con proxy restrittivi

---

### Soluzione 2: Usa la Nuova Versione di INSTALLA.bat

La versione aggiornata di INSTALLA.bat (dopo fix 2026-01-09):
- ✅ Mostra il progresso dell'aggiornamento pip
- ✅ Ha un timeout e gestione errori migliorata
- ✅ Non blocca più se pip fallisce (procede comunque)

**Passi:**
1. Assicurarsi di avere la versione aggiornata (controllare che ci sia `--no-cache-dir`)
2. Eseguire come amministratore

---

### Soluzione 3: Installazione Manuale

Se entrambi gli script falliscono, installazione passo-passo manuale.

**Passi:**

1. **Apri PowerShell come Amministratore**
   ```powershell
   # Vai nella directory del progetto
   cd "C:\path\to\Adeverente"
   ```

2. **Crea ambiente virtuale**
   ```powershell
   python -m venv venv
   ```

3. **Attiva ambiente virtuale**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   Se ricevi errore "impossibile caricare", esegui:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **SALTA aggiornamento pip** (o fallo solo se funziona velocemente)
   ```powershell
   # Opzionale - prova ma se si blocca, Ctrl+C e vai avanti
   python -m pip install --upgrade pip --timeout 30
   ```

5. **Installa dipendenze UNA PER UNA** (per identificare problemi)
   ```powershell
   pip install Flask
   pip install Pillow
   pip install reportlab
   pip install pyodbc
   pip install requests
   pip install schedule
   pip install loguru
   pip install cryptography
   pip install pytz
   pip install keyring
   ```

6. **Verifica installazione**
   ```powershell
   pip list
   ```

---

## 🐛 Problema: Pillow Fallisce con "zlib not found"

### Sintomi
```
ERROR: Failed building wheel for Pillow
RequiredDependencyException:

The headers or library files could not be found for zlib,
a required dependency when compiling Pillow from source.
```

### Causa
Pip sta cercando di **compilare Pillow da source** invece di usare una **wheel pre-compilata**. Succede quando:
- pip è troppo vecchio e non riconosce le wheel disponibili
- La versione di Pillow richiesta non ha wheel per Python 3.11/Windows
- pip ignora il `requirements.txt` e cerca l'ultima versione

### ✅ Soluzione 1: Usa Script Aggiornati (Fix Automatica)

Gli script `INSTALLA.bat` e `INSTALLA_RAPIDA.bat` aggiornati (2026-01-09):
- ✅ Installano **prima** Pillow 10.4.0 separatamente  
- ✅ Usano flag `--only-binary :all:` per **forzare** uso di wheel
- ✅ Falliscono immediatamente se wheel non disponibile (invece di provare a compilare)

**Passi:**
1. Scaricare l'ultima versione del package ZIP
2. Eseguire `INSTALLA_RAPIDA.bat` come amministratore
3. Lo script installerà Pillow separatamente prima delle altre dipendenze

---

### ✅ Soluzione 2: Installazione Manuale Pillow

Se gli script aggiornati non sono disponibili:

```powershell
# Attiva virtual environment
.\venv\Scripts\Activate.ps1

# Installa Pillow con wheel obbligatoria
pip install Pillow==10.4.0 --only-binary :all:

# Se fallisce, prova versione precedente
pip install Pillow==10.3.0 --only-binary :all:

# Poi installa le altre dipendenze
pip install -r requirements.txt
```

**Versioni Pillow testate con wheel per Python 3.11:**
- ✅ Pillow 10.4.0 (consigliata)
- ✅ Pillow 10.3.0
- ✅ Pillow 10.2.0
- ❌ Pillow 11.x (potrebbe non avere wheel)

---

### ✅ Soluzione 3: Aggiorna pip Prima

A volte pip vecchio non riconosce le wheel disponibili:

```powershell
# Aggiorna pip
python -m pip install --upgrade pip

# Verifica versione (deve essere >= 23.0)
pip --version

# Poi riprova installazione
pip install Pillow==10.4.0 --only-binary :all:
pip install -r requirements.txt
```

---

### ❌ NON Funziona: Lasciare pip Compilare

**NON fare:**
```
❌ pip install Pillow  (senza --only-binary)
❌ Installare Visual Studio Build Tools per compilare
```

**Perché:**
- Richiede 4+ GB di download (Visual Studio)
- Configurazione complessa
-  Wheel pre-compilate sono già disponibili!

---

## 🔧 Debug Avanzato


### Verifica Connessione a PyPI

```powershell
# Test connessione
python -m pip install --dry-run requests

# Usa mirror alternativo (se PyPI bloccato)
python -m pip install Flask --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Pulisci Cache pip

```powershell
# Rimuovi cache corrotta
python -m pip cache purge

# Reinstalla senza cache
pip install -r requirements.txt --no-cache-dir
```

### Verifica Proxy

Se l'azienda usa un proxy:

```powershell
# Imposta proxy temporaneamente
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080

# Poi riprova installazione
pip install -r requirements.txt
```

---

## 📋 Checklist Pre-Installazione

Prima di eseguire l'installazione, verificare:

- [ ] **Python 3.11** installato e in PATH
  ```powershell
  python --version  # Deve mostrare: Python 3.11.x
  ```

- [ ] **Connessione internet** attiva
  ```powershell
  ping pypi.org
  ```

- [ ] **Privilegi amministratore** attivi
  ```powershell
  net session  # Deve completare senza errori
  ```

- [ ] **Antivirus/Firewall** non blocca Python/pip
  - Aggiungere eccezione per `python.exe`
  - Aggiungere eccezione per la cartella del progetto

- [ ] **Spazio disco** sufficiente (min 500 MB liberi)

---

## 🚦 Quale Script Usare?

| Scenario | Script Consigliato | Note |
|----------|-------------------|------|
| Prima installazione, PC aziendale | `INSTALLA_RAPIDA.bat` | Salta pip upgrade |
| Prima installazione, connessione lenta | `INSTALLA_RAPIDA.bat` | Più veloce |
| INSTALLA.bat si è bloccato | `INSTALLA_RAPIDA.bat` | Usa questo |
| PC personale, buona connessione | `INSTALLA.bat` | Versione completa |
| Entrambi falliscono | Installazione Manuale | Segui Soluzione 3 |

---

## 📝 Log di Installazione

Per salvare un log dell'installazione (utile per troubleshooting):

```powershell
# Script normale con log
INSTALLA_RAPIDA.bat > installazione_log.txt 2>&1
```

Poi controllare il file `installazione_log.txt` per vedere dove si è bloccato.

---

## ⚡ Quick Fix

**Se hai fretta e non vuoi leggere tutto:**

1. **Chiudi** qualsiasi installazione bloccata
2. **Usa** `INSTALLA_RAPIDA.bat` come amministratore
3. **Aspetta** che finisca (mostra il progresso)
4. **Fine!** Puoi avviare con `START_APP.bat`

---

## 🆘 Contatto Supporto

Se nessuna soluzione funziona, raccogliere:

1. Versione di Windows: `winver`
2. Versione Python: `python --version`
3. Output errore completo (screenshot o testo)
4. File `installazione_log.txt` (se creato)

E contattare il supporto IT con queste informazioni.

---

**Aggiornato:** 2026-01-09  
**Fix Applicata:** Gestione robusta pip + script alternativo rapido
