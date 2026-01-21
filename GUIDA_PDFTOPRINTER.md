# 🖨️ GUIDA: Installazione PDFtoPrinter per Stampa VERAMENTE Silenziosa

## ⚠️ PROBLEMA
Adobe Acrobat Reader, anche con `/t`, apre sempre una finestra brevemente durante la stampa.

## ✅ SOLUZIONE
**PDFtoPrinter.exe** è una utility Windows gratuita che stampa PDF senza aprire NESSUNA finestra.

---

## 📥 INSTALLAZIONE

### Opzione 1: Download Manuale (Raccomandato)

1. **Scarica** da GitHub:  
   https://github.com/stchan/PDFtoPrinter/releases/latest
   
2. **Trova** il file `PDFtoPrinter.exe` tra gli assets

3. **Copia** il file nella directory del progetto:
   ```
   C:\Users\gtesta\PythonProjetcs\Python\Adeverente\PDFtoPrinter.exe
   ```

4. **Done!** Il sistema lo rileverà automaticamente

### Opzione 2: PowerShell Download

```powershell
# Esegui dalla directory del progetto
cd C:\Users\gtesta\PythonProjetcs\Python\Adeverente

# Download diretto  
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri "https://github.com/stchan/PDFtoPrinter/releases/download/3.5.1/PDFtoPrinter.exe" -OutFile "PDFtoPrinter.exe"

# Verifica
if (Test-Path PDFtoPrinter.exe) {
    Write-Host "✅ PDFtoPrinter.exe installato correttamente!" -ForegroundColor Green
} else {
    Write-Host "❌ Download fallito" -ForegroundColor Red
}
```

---

## 🔧 COME FUNZIONA

### Prima (Adobe Reader /t)
```
User click → Backend genera PDF → PowerShell chiama Adobe con /t
→ Adobe SI APRE brevemente → Stampa → Adobe SI CHIUDE
❌ FINESTRA VISIBILE PER 1-2 SECONDI
```

### Dopo (PDFtoPrinter.exe)
```
User click → Backend genera PDF → PowerShell chiama PDFtoPrinter.exe
→ PDFtoPrinter stampa direttamente → Completato
✅ NESSUNA FINESTRA - COMPLETAMENTE SILENZIOSO
```

---

## 📋 LOGICA AUTOMATICA

Il sistema ora prova in ordine:

1. **PDFtoPrinter.exe** (se presente nella directory)
   - → STAMPA SILENZIOSA COMPLETA ✅

2. **Adobe Reader /t** (fallback se PDFtoPrinter non trovato)
   - → Mostra finestra brevemente ⚠️

3. **Errore** (se nessuno dei due disponibile)
   - → Messaggio: "No PDF printer found" ❌

---

## 🧪 TEST

### Test 1: Verifica PDFtoPrinter installato
```powershell
Test-Path "C:\Users\gtesta\PythonProjetcs\Python\Adeverente\PDFtoPrinter.exe"
# Output atteso: True
```

### Test 2: Test stampa manuale
```powershell
cd C:\Users\gtesta\PythonProjetcs\Python\Adeverente
.\PDFtoPrinter.exe "temp\news_7_*.pdf" "Color Birou"
```

### Test 3: Test da app
1. Riavvia `python app.py`
2. Apri http://localhost:5000
3. Click su news frame
4. **Verifica**: NESSUNA finestra Adobe si apre!

---

##  VANTAGGI PDFtoPrinter

| Feature | Adobe /t | PDFtoPrinter | 
|---------|----------|--------------|
| Finestra visibile | ⚠️ SI (1-2s) | ✅ MAI |
| Velocità stampa | ~3-5s | ~1-2s |
| Affidabilità | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Dimensione | ~500MB | 92KB |
| Configurazione | Pre-installato | Download 1 file |

---

## 💡 NOTE TECNICHE

### Sintassi PDFtoPrinter
```bash
PDFtoPrinter.exe "path\to\file.pdf" "PrinterName"
```

### Sintassi PowerShell in pdf_printer.py
```powershell
$pdfToPrinterPath = Join-Path $PSScriptRoot 'PDFtoPrinter.exe'

if (Test-Path $pdfToPrinterPath) {
    # METODO SILENZIOSO
    & $pdfToPrinterPath 'file.pdf' 'Printer Name'
} else {
    # FALLBACK ADOBE
    $adobePath | Start-Process -ArgumentList "/t ..."
}
```

---

## 📦 INCLUSIONE NEL DEPLOY

Per i deploy futuri, includi `PDFtoPrinter.exe` nel pacchetto ZIP:

```powershell
# In CREATE_DEPLOY_PACKAGE.ps1, aggiungere:
if (Test-Path "PDFtoPrinter.exe") {
    Copy-Item "PDFtoPrinter.exe" -Destination $tempDir
    Write-Host "  ✓ PDFtoPrinter.exe" -ForegroundColor Green
}
```

---

## 🔗 RISORSE

- **GitHub**: https://github.com/stchan/PDFtoPrinter
- **License**: Freeware
- **Dimensione**: 92 KB
- **OS Support**: Windows 7/8/10/11

---

## ❓ TROUBLESHOOTING

### "PDFtoPrinter.exe not recognized"
→ Verifica che sia nella directory corretta del progetto

### Stampa va a stampante sbagliata
→ Controlla nome esatto: `Get-Printer | Select Name`

### Nessun output dalla stampante
→ Verifica coda stampa: `Get-PrintJob -PrinterName "ColorBirou"`

---

**Installazione richiesta in**: `C:\Users\gtesta\PythonProjetcs\Python\Adeverente\PDFtoPrinter.exe`

**Dopo l'installazione**: Riavvia `python app.py` e riprova la stampa → Dovrebbe essere COMPLETAMENTE SILENZIOSA! 🎉
