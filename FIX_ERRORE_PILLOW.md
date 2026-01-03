# 🔧 SOLUZIONE ERRORE PILLOW - COMPILAZIONE ZLIB

## ❌ Errore Riscontrato

```
RequiredDependencyException: zlib
The headers or library files could not be found for zlib,
a required dependency when compiling Pillow from source.
ERROR: Failed building wheel for Pillow
```

## 🎯 Causa del Problema

Pillow sta cercando di compilare da sorgente invece di usare un wheel precompilato. Questo può succedere quando:
1. La versione di Pillow specificata non ha wheel per Python 3.11 su Windows
2. pip/setuptools non riesce a trovare i wheel precompilati
3. La connessione a PyPI è limitata

## ✅ SOLUZIONE 1: Usa il Nuovo Pacchetto (CONSIGLIATO)

Ho aggiornato `requirements.txt` con **Pillow 10.4.0** che ha sicuramente wheel precompilati per Python 3.11 su Windows.

**Nuovo pacchetto in arrivo...**

---

## ✅ SOLUZIONE 2: Installazione Manuale Step-by-Step

Se preferisci installare manualmente le dipendenze:

### Opzione A: Installa Pillow separatamente con versione specifica

```batch
REM 1. Attiva ambiente virtuale
cd C:\Wandewiele\Kiosk
venv\Scripts\activate.bat

REM 2. Aggiorna pip, setuptools e wheel
python -m pip install --upgrade pip setuptools wheel

REM 3. Installa Pillow 10.4.0 (versione con wheel garantiti)
pip install Pillow==10.4.0

REM 4. Installa le altre dipendenze
pip install Flask==3.0.0 Werkzeug==3.0.1
pip install pyodbc==5.0.1
pip install reportlab==4.0.7 PyPDF2==3.0.1
pip install cryptography==41.0.7
pip install secure-smtplib==0.1.1
pip install python-dateutil==2.8.2 pytz==2023.3
pip install pywin32==306
pip install schedule==1.2.0
pip install loguru==0.7.2
pip install keyring==24.3.0
```

### Opzione B: Scarica manualmente il wheel di Pillow

```batch
REM 1. Vai su https://pypi.org/project/Pillow/#files
REM 2. Scarica il wheel per Python 3.11 Windows:
REM    Pillow-10.4.0-cp311-cp311-win32.whl (per Windows 32-bit)
REM    oppure
REM    Pillow-10.4.0-cp311-cp311-win_amd64.whl (per Windows 64-bit)

REM 3. Copia il file .whl in C:\Wandewiele\Kiosk\

REM 4. Installa il wheel locale
cd C:\Wandewiele\Kiosk
venv\Scripts\activate.bat
pip install Pillow-10.4.0-cp311-cp311-win_amd64.whl
```

### Opzione C: Usa --only-binary per forzare wheel

```batch
cd C:\Wandewiele\Kiosk
venv\Scripts\activate.bat

REM Forza pip a usare solo wheel precompilati (non compila da sorgente)
pip install --only-binary :all: -r requirements.txt
```

---

## ✅ SOLUZIONE 3: Semplifica requirements.txt

Se il problema persiste, crea un file `requirements_minimal.txt` con solo le dipendenze essenziali:

```text
# requirements_minimal.txt - Solo pacchetti essenziali

Flask==3.0.0
pyodbc==5.0.1
reportlab==4.0.7
cryptography==41.0.7
python-dateutil==2.8.2
pywin32==306
Pillow==10.4.0
```

Poi installa:
```batch
pip install -r requirements_minimal.txt
```

---

## ✅ SOLUZIONE 4: Verifica Architettura Python

Il problema potrebbe essere l'architettura di Python installata.

```batch
REM Verifica se Python è 32-bit o 64-bit
python -c "import platform; print(platform.machine())"
```

**Output:**
- `AMD64` o `x86_64` = Python 64-bit ✅ (CORRETTO per Windows moderni)
- `x86` o `i686` = Python 32-bit ⚠️ (potrebbe causare problemi)

**Se hai Python 32-bit:**
1. Disinstalla Python corrente
2. Scarica Python 3.11 **64-bit** da python.org
3. Reinstalla
4. Riprova installazione

---

## ✅ SOLUZIONE 5: Aggiorna pip e setuptools

```batch
cd C:\Wandewiele\Kiosk
venv\Scripts\activate.bat

REM Aggiorna pip alla versione più recente
python -m pip install --upgrade pip

REM Aggiorna setuptools e wheel
pip install --upgrade setuptools wheel

REM Riprova installazione
pip install -r requirements.txt
```

---

## ✅ SOLUZIONE 6: Usa Cache Locale

Se la rete aziendale blocca alcuni download:

```batch
REM 1. Su un PC con internet libero, scarica tutti i wheel
pip download -r requirements.txt -d C:\temp\wheels

REM 2. Copia la directory C:\temp\wheels sul PC target

REM 3. Sul PC target, installa dai file locali
cd C:\Wandewiele\Kiosk
venv\Scripts\activate.bat
pip install --no-index --find-links C:\temp\wheels -r requirements.txt
```

---

## 🔍 VERIFICA INSTALLAZIONE

Dopo aver risolto il problema, verifica che Pillow sia installato:

```batch
cd C:\Wandewiele\Kiosk
venv\Scripts\activate.bat

REM Verifica versione Pillow installata
python -c "import PIL; print(PIL.__version__)"
```

Dovrebbe mostrare: `10.4.0`

---

## 📋 Checklist Risoluzione Problema

- [ ] Python 3.11 64-bit installato
- [ ] pip aggiornato (`python -m pip install --upgrade pip`)
- [ ] setuptools e wheel aggiornati
- [ ] Ambiente virtuale creato correttamente in `C:\Wandewiele\Kiosk\venv`
- [ ] Usare requirements.txt aggiornato (Pillow 10.4.0)
- [ ] Connessione internet funzionante (per scaricare wheel da PyPI)
- [ ] Nessun firewall/proxy che blocca PyPI

---

## 🎯 SOLUZIONE RACCOMANDATA (Riepilogo)

```batch
REM 1. Vai nella directory dell'applicazione
cd C:\Wandewiele\Kiosk

REM 2. Elimina vecchio venv se esiste
if exist venv rmdir /s /q venv

REM 3. Ricrea ambiente virtuale
python -m venv venv

REM 4. Attiva ambiente
venv\Scripts\activate.bat

REM 5. Aggiorna pip e strumenti
python -m pip install --upgrade pip setuptools wheel

REM 6. Installa Pillow per primo (versione con wheel)
pip install Pillow==10.4.0

REM 7. Installa le altre dipendenze
pip install Flask==3.0.0 Werkzeug==3.0.1
pip install pyodbc==5.0.1
pip install reportlab==4.0.7 PyPDF2==3.0.1
pip install cryptography==41.0.7
pip install secure-smtplib==0.1.1
pip install python-dateutil==2.8.2 pytz==2023.3
pip install pywin32==306
pip install schedule==1.2.0
pip install loguru==0.7.2
pip install keyring==24.3.0

REM 8. Verifica installazione
python -c "import PIL; print('Pillow:', PIL.__version__)"
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import pyodbc; print('pyodbc OK')"

REM 9. Se tutto OK, configura e avvia
python setup.py
START_APP.bat
```

---

## 📦 Nuovo Pacchetto in Arrivo

Sto creando un nuovo pacchetto con:
- ✅ `requirements.txt` aggiornato (Pillow 10.4.0)
- ✅ `INSTALLA.bat` corretto (con cd /d "%~dp0")
- ✅ Questa guida inclusa

---

## 📞 Note Aggiuntive

### Perché Pillow 10.4.0?
- ✅ Versione stabile e testata
- ✅ Wheel precompilati disponibili per tutte le architetture Windows
- ✅ Compatibile con Python 3.11
- ✅ Supporto completo per le funzionalità usate dall'applicazione

### Alternative a Pillow
**NON NECESSARIO** - Pillow è essenziale per:
- Generazione PDF con immagini (reportlab)
- Manipolazione immagini slideshow
- Ottimizzazione immagini per web

---

## ✅ Risultato Atteso

Dopo aver applicato la soluzione, l'installazione dovrebbe procedere così:

```
[5/8] Installazione dipendenze Python...
[INFO] Questo potrebbe richiedere alcuni minuti...
Collecting Flask==3.0.0
  Downloading Flask-3.0.0-py3-none-any.whl (99 kB)
...
Collecting Pillow==10.4.0
  Downloading Pillow-10.4.0-cp311-cp311-win_amd64.whl (2.6 MB)  <-- WHEEL!
  ✅ Nessuna compilazione da sorgente
...
Successfully installed ...
[OK] Dipendenze installate
```

**La chiave è vedere "Downloading ... .whl" invece di "Building wheel for Pillow"!**

---

*Guida aggiornata: 03/01/2026 - 13:17*
