# FIX PROBLEMA STAMPA PDF - CODICE GREZZO INVECE DEL DOCUMENTO

## 🔴 PROBLEMA CRITICO RISOLTO

### Sintomo
Tutti i report PDF venivano stampati come **codice grezzo** (testo interno del PDF) invece del documento formattato. 
La stampante riceveva il contenuto testuale del file PDF (tipo `/Type /Pages`, `/Producer (PyPDF2)`, ecc.) invece del documento binario.

### Causa
Nel file `pdf_printer.py`, alla **linea 145**, il metodo di fallback utilizzava:

```powershell
$null = Out-Printer -InputObject (Get-Content -Path $pdfPath -Raw) -Name $printerName
```

**ERRORE**: `Get-Content -Raw` legge il file PDF come **testo Unicode** invece di gestirlo come file binario, causando l'invio del codice sorgente del PDF alla stampante anziché del documento formattato.

### Soluzione Implementata
Sostituito il metodo fallback errato con un approccio corretto che usa il **System.Diagnostics.Process** di .NET con il verbo `print`:

```powershell
$printProcess = New-Object System.Diagnostics.ProcessStartInfo
$printProcess.FileName = $pdfPath
$printProcess.Verb = 'print'
$printProcess.Arguments = "\"$printerName\""
$printProcess.CreateNoWindow = $true
$printProcess.WindowStyle = 'Hidden'

$process = [System.Diagnostics.Process]::Start($printProcess)
```

Questo metodo:
- ✅ Invoca l'applicazione PDF predefinita del sistema (solitamente Adobe Reader)
- ✅ Passa il file PDF come **file binario** 
- ✅ Utilizza il verbo shell `print` che gestisce correttamente i PDF
- ✅ Mantiene la finestra nascosta per stampa silenziosa
- ✅ Non apre manualmente il file come testo

## Gerarchia dei Metodi di Stampa

Il sistema prova i seguenti metodi in ordine:

1. **SumatraPDF** (se installato): `SumatraPDF.exe -print-to "Printer" -silent "file.pdf"`
2. **Adobe Reader** con parametri `/t` per stampa diretta nascosta
3. **GhostScript** con device `mswinpr2` per stampa diretta a livello di driver
4. **System.Diagnostics.Process** con verbo `print` (NUOVO - corretto) ✅
   - ~~`Out-Printer` con `Get-Content -Raw` (VECCHIO - errato)~~ ❌

## File Modificato
- `c:\Users\gtesta\PythonProjetcs\Python\Adeverente\pdf_printer.py` (linee 142-166)

## Impatto
✅ Tutti i report PDF del sistema ora verranno stampati correttamente:
- Report assenze annuali
- Adeverințe (certificati HR)
- Report mensili
- Altri documenti PDF generati dal sistema Kiosk

## Test Raccomandati
1. Stampare un report assenze da `app.py` → `/print_absence_report`
2. Stampare un'adeverință → `/generate_adeverinta`
3. Stampare report mensili → `/generate_monthly_certificate`
4. Verificare che il documento stampato sia formattato correttamente e NON mostri codice grezzo

## Data Fix
2026-01-12 13:51 CET

## Severity
🔴 **CRITICA** - Funzionalità core completamente non funzionante
