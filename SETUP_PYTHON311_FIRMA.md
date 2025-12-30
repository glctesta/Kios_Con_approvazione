# 🔐 GUIDA FIRMA DIGITALE CERTSIGN - Python 3.11

## 📥 STEP 1: Download e Installazione Python 3.11

### Download
- **URL**: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
- **Versione**: Python 3.11.9 (ultima stabile)

### Installazione
1. Esegui `python-3.11.9-amd64.exe`
2. ✅ Seleziona: **"Add Python 3.11 to PATH"**
3. ✅ Seleziona: **"Install for all users"** (opzionale)
4. Click: **"Install Now"**
5. Attendi completamento
6. Click: **"Close"**

---

## 🔄 STEP 2: Ricrea Ambiente Virtuale

Apri **nuovo** PowerShell nella cartella progetto:

```powershell
# Vai alla cartella progetto
cd c:\Users\gtesta\PythonProjetcs\Python\Adeverente

# Verifica versione Python
python --version
# DEVE mostrare: Python 3.11.9

# Elimina vecchio ambiente virtuale (Python 3.14)
Remove-Item -Recurse -Force venv

# Crea nuovo ambiente con Python 3.11
python -m venv venv

# Attiva ambiente virtuale
.\venv\Scripts\Activate.ps1

# Verifica che venv usi Python 3.11
python --version
# DEVE mostrare: Python 3.11.9
```

---

## 📦 STEP 3: Installa Dipendenze

```powershell
# Assicurati che venv sia attivo (dovresti vedere (venv) nel prompt)

# Aggiorna pip
python -m pip install --upgrade pip

# Installa tutte le dipendenze
pip install -r requirements.txt

# Post-install pywin32 (IMPORTANTE!)
python -m pywin32_postinstall -install
```

**Nota**: Se `pywin32_postinstall` da errore, non è critico. Prova comunque il passo successivo.

---

## 🧪 STEP 4: Testa Certificati

```powershell
# Testa il modulo firma digitale
python digital_signature.py
```

**Output atteso**:
```
=== CERTIFICATI DISPONIBILI ===

1. Subject: Gianluca Testa
   Issuer: CertSign
   Chiave privata: ✅ Sì

2. Subject: [altri certificati...]
   ...
```

Se vedi i certificati con chiave privata, **PERFETTO!** ✅

---

## 🚀 STEP 5: Riavvia Server

```powershell
# Avvia server Flask
python app.py
```

**Output atteso**:
```
 * Serving Flask app 'app'
 * Debug mode: on
INFO - Font Arial registrato per supporto Unicode
INFO - pyHanko caricato con successo - Firma digitale disponibile
WARNING: This is a development server.
 * Running on http://0.0.0.0:5000
```

Cerca la riga: **"pyHanko caricato con successo"** ✅

---

## 🔐 STEP 6: Testa Firma Digitale

### Opzione A: Test Manuale

```powershell
# Crea un PDF di test
python -c "from reportlab.pdfgen import canvas; c = canvas.Canvas('test.pdf'); c.drawString(100, 750, 'Test PDF'); c.save()"

# Firma il PDF
python -c "from digital_signature import sign_pdf_with_certsign; sign_pdf_with_certsign('test.pdf', 'test_signed.pdf')"

# Verifica che test_signed.pdf sia stato creato
dir test_signed.pdf
```

### Opzione B: Test tramite Applicazione

1. Apri browser: http://localhost:5000
2. Scansiona badge
3. Seleziona motivo
4. Genera certificato
5. Verifica nel log server: **"PDF firmato digitalmente con CertSign"**

---

## 📊 VERIFICA FINALE

### Checklist Completa

- [ ] Python 3.11.9 installato
- [ ] `python --version` mostra 3.11.9
- [ ] Ambiente virtuale ricreato
- [ ] Dipendenze installate
- [ ] `digital_signature.py` mostra certificati
- [ ] Server Flask avviato
- [ ] Log mostra "pyHanko caricato con successo"
- [ ] Test firma PDF funziona

---

## 🔧 RISOLUZIONE PROBLEMI

### Problema: "python --version" mostra ancora 3.14

**Soluzione**:
```powershell
# Trova dove è installato Python 3.11
where.exe python

# Usa path completo per creare venv
C:\Users\gtesta\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

---

### Problema: "pywin32_postinstall" non trovato

**Soluzione**:
```powershell
# Reinstalla pywin32
pip uninstall pywin32
pip install pywin32==306

# Riprova post-install
python -m pywin32_postinstall -install
```

---

### Problema: Certificati non trovati

**Verifica con PowerShell**:
```powershell
Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.HasPrivateKey} | Select-Object Subject, Issuer
```

Se vedi certificati qui ma non in Python, verifica che:
1. Python 3.11 sia attivo
2. pywin32 sia installato correttamente
3. Ambiente virtuale sia attivo

---

## 📞 SUPPORTO

Se hai problemi:

1. **Controlla log server** - Cerca errori
2. **Verifica versione Python** - `python --version`
3. **Testa certificati** - `python digital_signature.py`
4. **Controlla dipendenze** - `pip list | findstr pywin32`

---

## 🎯 PROSSIMI PASSI (Dopo Setup)

Una volta che tutto funziona:

1. ✅ Integrerò firma digitale in `certificate_generator.py`
2. ✅ Ogni PDF sarà firmato automaticamente con CertSign
3. ✅ Firma visibile nel PDF con timestamp
4. ✅ Validità legale garantita

---

**Buona installazione! Fammi sapere quando hai completato e testiamo insieme!** 🚀

---

**Ultimo aggiornamento**: 23 Dicembre 2025  
**Versione**: 1.0.0
