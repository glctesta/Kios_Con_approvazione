# 🔧 SOLUZIONE PROBLEMA INSTALLAZIONE

## ❌ Problema Riscontrato

```
[3/8] Attivazione ambiente virtuale...
The system cannot find the path specified.
[ERRORE] Impossibile attivare ambiente virtuale
```

## 🎯 Causa del Problema

Quando si esegue `INSTALLA.bat` come **Amministratore**, Windows potrebbe cambiare automaticamente la directory corrente in `C:\Windows\System32`, causando la creazione dell'ambiente virtuale nella directory sbagliata invece che nella directory dell'applicazione.

## ✅ SOLUZIONE 1: Usa il Nuovo Pacchetto (CONSIGLIATO)

Ho creato un **nuovo pacchetto corretto**:

**File:** `Kiosk_HR_v2.2.0_20260103_131149.zip`  
**Correzione:** Lo script ora imposta automaticamente la directory corrente a quella dello script, indipendentemente da dove viene eseguito.

### Passaggi:
1. **Elimina** la vecchia installazione sul computer target
2. **Trasferisci** il nuovo file ZIP: `Kiosk_HR_v2.2.0_20260103_131149.zip`
3. **Estrai** in `C:\Kiosk_HR\`
4. **Esegui** `INSTALLA.bat` come Amministratore
5. ✅ Il problema è risolto!

---

## ✅ SOLUZIONE 2: Correggi Manualmente (se preferisci)

Se hai già estratto il pacchetto sul computer target, puoi correggere manualmente:

### Opzione A: Aggiungi il cambi o directory
1. Apri `INSTALLA.bat` con Notepad
2. Dopo la riga `@echo off`, aggiungi:
   ```batch
   cd /d "%~dp0"
   ```
3. Salva e riprova

### Opzione B: Esegui da Esplora File
1. **NON** aprire PowerShell o CMD come amministratore
2. Apri **Esplora File**
3. Naviga in `C:\Kiosk_HR\`
4. Fai **click destro** su `INSTALLA.bat`
5. Seleziona **"Esegui come amministratore"**

Questo assicura che la directory corrente sia `C:\Kiosk_HR\` quando lo script parte.

---

## ✅ SOLUZIONE 3: Installazione Manuale Step-by-Step

Se le soluzioni precedenti non funzionano, ecco i comandi manuali:

```batch
REM 1. Apri PowerShell come Amministratore

REM 2. Vai nella directory dell'applicazione
cd C:\Kiosk_HR

REM 3. Verifica di essere nella directory corretta
dir

REM 4. Crea ambiente virtuale
python -m venv venv

REM 5. Attiva ambiente virtuale
venv\Scripts\activate.bat

REM 6. Aggiorna pip
python -m pip install --upgrade pip

REM 7. Installa dipendenze
pip install -r requirements.txt

REM 8. Crea directory necessarie
mkdir temp
mkdir Images

REM 9. Configura database e email
python setup.py

REM 10. Avvia applicazione
START_APP.bat
```

---

## 🔍 Verifica Pre-Installazione

Prima di procedere con l'installazione, verifica:

```batch
REM Apri PowerShell come Amministratore

REM Vai nella directory
cd C:\Kiosk_HR

REM Verifica Python
python --version
# Deve mostrare: Python 3.11.x

REM Verifica file presenti
dir app.py
dir requirements.txt
dir INSTALLA.bat

REM Se tutto OK, procedi con:
.\INSTALLA.bat
```

---

## 📋 Checklist Installazione Corretta

Quando esegui `INSTALLA.bat` corretto, dovresti vedere:

```
========================================
  KIOSK HR - Installazione Sistema
  Versione 2.2.0
========================================

Directory installazione: C:\Kiosk_HR    <-- IMPORTANTE!

[1/8] Verifica Python 3.11...
[OK] Python 3.11 trovato

[2/8] Creazione ambiente virtuale...
[OK] Ambiente virtuale creato

[3/8] Attivazione ambiente virtuale...
[OK] Ambiente virtuale attivato          <-- DEVE ESSERE OK!

[4/8] Aggiornamento pip...
[OK] pip aggiornato

[5/8] Installazione dipendenze Python...
[OK] Dipendenze installate

[6/8] Verifica file di configurazione...
[OK] Verifica configurazione completata

[7/8] Creazione directory necessarie...
[OK] Directory create

[8/8] Verifica componenti aggiuntivi...
[OK] Verifica componenti completata

========================================
  INSTALLAZIONE COMPLETATA!
========================================
```

**Nota:** La riga `Directory installazione:` deve mostrare `C:\Kiosk_HR` (o la directory dove hai estratto i file), **NON** `C:\Windows\System32`!

---

## ⚠️ Se il Problema Persiste

### Verifica Directory Venv Creata
```batch
cd C:\Kiosk_HR
dir
```

Se vedi la cartella `venv` nella lista, l'ambiente virtuale è stato creato correttamente.

### Verifica Contenuto Venv
```batch
dir venv\Scripts
```

Dovresti vedere:
- `activate.bat`
- `python.exe`
- `pip.exe`

### Se Venv è in C:\Windows\System32
```batch
REM Vai in C:\Kiosk_HR
cd C:\Kiosk_HR

REM Rimuovi eventuale venv errato
if exist venv rmdir /s /q venv

REM Ricrea venv nella directory corretta
python -m venv venv

REM Attiva venv
venv\Scripts\activate.bat

REM Verifica che (venv) appaia nel prompt
REM Dovresti vedere: (venv) C:\Kiosk_HR>

REM Installa dipendenze
pip install -r requirements.txt
```

---

## 📦 Differenze tra i Due Pacchetti

| File | Vecchio | Nuovo (Corretto) |
|------|---------|------------------|
| Nome | `Kiosk_HR_v2.2.0_20260103_130243.zip` | `Kiosk_HR_v2.2.0_20260103_131149.zip` |
| Data | 13:02:43 | 13:11:49 |
| INSTALLA.bat | Versione 2.1.1 (senza `cd`) | Versione 2.2.0 (con `cd /d "%~dp0"`) |
| Problema | ❌ Possibile errore con Admin | ✅ Funziona sempre |

---

## 📞 Supporto

Se dopo queste soluzioni il problema persiste:

1. Invia screenshot completo dell'errore
2. Indica la directory dove hai estratto i file
3. Esegui e invia output di:
   ```batch
   cd C:\Kiosk_HR
   echo %CD%
   python --version
   dir venv
   ```

**Email:** gianluca.testa@vandewiele.com

---

## ✅ Riepilogo

**SOLUZIONE RACCOMANDATA:**
1. ✅ Usa il nuovo pacchetto: `Kiosk_HR_v2.2.0_20260103_131149.zip`
2. ✅ Estrai in `C:\Kiosk_HR\`
3. ✅ Esegui `INSTALLA.bat` come Amministratore da Esplora File
4. ✅ Il problema è risolto!

**Il nuovo pacchetto include il fix e funzionerà correttamente! 🎉**
