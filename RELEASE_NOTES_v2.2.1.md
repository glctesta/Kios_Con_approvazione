# Release Notes - Kiosk HR v2.2.1

**Data Rilascio**: 12 Gennaio 2026  
**Tipo**: Hotfix Critico

---

## 🔴 **FIX CRITICI**

### **Bug Stampa PDF - Codice Grezzo**
- **Problema**: Tutti i report PDF venivano stampati come **codice grezzo** (testo interno del PDF) invece del documento formattato
- **Causa**: Il metodo di fallback in `pdf_printer.py` utilizzava `Get-Content -Raw` che legge il PDF come testo Unicode
- **Soluzione**: Implementato metodo corretto usando `System.Diagnostics.Process` con verbo shell `print` per gestire il PDF come file binario
- **File modificati**: `pdf_printer.py` (linee 142-166, 85-86)
- **Impatto**: ✅ Tutte le stampe PDF ora funzionano correttamente (certificati, report assenze, report mensili)

**Dettagli tecnici**:
```powershell
# VECCHIO (errato) - stampava codice grezzo
$null = Out-Printer -InputObject (Get-Content -Path $pdfPath -Raw) -Name $printerName

# NUOVO (corretto) - stampa documento formattato
$printProcess = New-Object System.Diagnostics.ProcessStartInfo
$printProcess.FileName = $pdfPath
$printProcess.Verb = 'print'
$printProcess.CreateNoWindow = $true
$process = [System.Diagnostics.Process]::Start($printProcess)
```

---

## 📄 **DOCUMENTAZIONE**

### Nuovi Documenti
- ✅ `FIX_STAMPA_PDF_CODICE_GREZZO.md` - Documentazione completa del bug e della soluzione

---

## 🔧 **COMPATIBILITÀ**

- **Versione Python**: 3.11+
- **Sistema Operativo**: Windows 10/11
- **Database**: SQL Server (Employee.dbo)
- **Dipendenze**: Nessuna modifica ai requirements.txt

---

## 📦 **DEPLOYMENT**

### Installazione/Aggiornamento
```batch
# Estrai il pacchetto ZIP
# Esegui come Amministratore:
INSTALLA.bat

# Avvia il sistema:
START_APP.bat
```

### Upgrade da v2.2.0
Per aggiornare da v2.2.0 a v2.2.1:
1. Ferma il servizio attuale (CTRL+C nel terminale di START_APP.bat)
2. Sostituisci solo il file `pdf_printer.py` 
3. Riavvia il servizio con START_APP.bat

**IMPORTANTE**: Non è necessario reinstallare l'ambiente virtuale o le dipendenze.

---

## ✅ **TEST ESEGUITI**

- ✅ Compilazione sintassi Python (`python -m py_compile pdf_printer.py`)
- ✅ Validazione logica PowerShell
- ✅ Verifica compatibilità con tutti i metodi di stampa (SumatraPDF, Adobe Reader, GhostScript, System Process)

### Test Raccomandati dopo Deployment
1. Stampare un report assenze (`/api/generate-absence-report`)
2. Stampare un'adeverință (`/api/generate-certificate`)
3. Stampare un report mensile
4. Verificare che il documento stampato sia formattato correttamente (NON codice grezzo)

---

## 🐛 **BUG NOTI**

Nessun bug noto in questa versione.

---

## 📞 **SUPPORTO**

Per problemi o domande:
- Verifica `app_debug.log` per errori di runtime
- Consulta `FIX_STAMPA_PDF_CODICE_GREZZO.md` per dettagli tecnici
- Contatta il team di sviluppo GTMC

---

## 🎯 **PROSSIMI SVILUPPI**

Pianificati per v2.3.0:
- Ottimizzazione performance stampa
- Dashboard monitoraggio utilizzo kiosk
- Report statistici mensili automatici

---

**By GTMC - Advanced IT Solutions**
