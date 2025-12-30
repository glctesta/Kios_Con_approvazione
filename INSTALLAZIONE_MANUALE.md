# 🔧 INSTALLAZIONE MANUALE - Python 3.14

## ⚠️ IMPORTANTE

Se hai **Python 3.14** e l'installazione automatica fallisce, segui questa procedura manuale.

---

## 📋 PROCEDURA MANUALE

### STEP 1: Aggiorna pip

```powershell
python -m pip install --upgrade pip
```

### STEP 2: Installa dipendenze singolarmente

```powershell
# Web Framework
pip install Flask==3.0.0
pip install Flask-CORS==4.0.0

# Database
pip install pyodbc

# PDF Generation
pip install reportlab==4.0.7
pip install Pillow --upgrade
pip install PyPDF2

# Security
pip install cryptography

# Utilities
pip install python-dotenv
pip install pywin32
```

### STEP 3: Verifica installazione

```powershell
python -c "import flask; print('Flask OK')"
python -c "import pyodbc; print('pyodbc OK')"
python -c "import reportlab; print('reportlab OK')"
python -c "from PIL import Image; print('Pillow OK')"
python -c "import PyPDF2; print('PyPDF2 OK')"
```

Se tutti stampano "OK", l'installazione è riuscita! ✅

### STEP 4: Avvia applicazione

```
Doppio click: START_APP.bat
```

---

## 🔍 TROUBLESHOOTING

### Errore: "No module named 'flask'"

```powershell
pip install Flask==3.0.0 --force-reinstall
```

### Errore: Pillow build failed

```powershell
# Usa versione pre-compilata più recente
pip install Pillow --upgrade --only-binary :all:
```

### Errore: pywin32 non funziona

```powershell
# Installa e configura pywin32
pip install pywin32
python -m pywin32_postinstall -install
```

---

## ✅ CHECKLIST

- [ ] pip aggiornato
- [ ] Flask installato
- [ ] pyodbc installato
- [ ] reportlab installato
- [ ] Pillow installato
- [ ] PyPDF2 installato
- [ ] cryptography installato
- [ ] python-dotenv installato
- [ ] pywin32 installato
- [ ] Tutti i test "OK"
- [ ] START_APP.bat funziona

---

## 💡 CONSIGLIO

**Se continui ad avere problemi con Python 3.14**, considera di usare **Python 3.11**:

1. Disinstalla Python 3.14
2. Installa Python 3.11.9 da:
   https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
3. Riprova installazione

Python 3.11 è più stabile e testato con queste librerie.

---

**Buona installazione!** 🚀
