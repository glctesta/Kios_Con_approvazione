# 🖨️ STAMPA AUTOMATICA PDF - Guida Completa

## 📋 Panoramica

L'applicazione **Generare Adeverințe** include un sistema di **stampa automatica** che invia il PDF generato direttamente alla stampante Windows predefinita, senza intervento dell'utente.

---

## ✅ Come Funziona

### **Flusso Automatico**

```
1. Dipendente avvicina badge RFID
2. Sistema riconosce dipendente
3. Seleziona motivo certificato
4. Click "Generează Adeverință"
   ↓
5. PDF generato in temp/
   ↓
6. PDF inviato AUTOMATICAMENTE alla stampante
   ↓
7. Notifica: "✅ Stampato su: [NOME_STAMPANTE]"
   ↓
8. PDF rimane salvato in temp/ come backup
```

### **Vantaggi**

- ✅ **Zero click** - Nessun dialogo di stampa
- ✅ **Veloce** - Stampa immediata dopo generazione
- ✅ **Affidabile** - 3 metodi di stampa fallback
- ✅ **Sicuro** - PDF sempre salvato come backup
- ✅ **Kiosk-friendly** - Perfetto per modalità chiosco

---

## 🔧 Configurazione

### **1. Imposta Stampante Predefinita Windows**

```
Windows 10/11:
1. Impostazioni → Dispositivi → Stampanti e scanner
2. Seleziona la stampante desiderata
3. Click "Gestisci"
4. Click "Imposta come predefinita"

Oppure:
1. Pannello di Controllo → Dispositivi e Stampanti
2. Click destro sulla stampante
3. "Imposta come stampante predefinita"
```

### **2. Installa SumatraPDF (Consigliato)**

**Perché SumatraPDF?**
- Stampa completamente silenziosa (no dialog)
- Leggero e veloce
- Supporto nativo per stampa da riga di comando
- Gratuito e open-source

**Installazione:**

1. Scarica da: https://www.sumatrapdfreader.org/download-free-pdf-viewer
2. Installa in: `C:\Program Files\SumatraPDF\`
3. L'applicazione lo rileverà automaticamente

### **3. Configura `print_config.json`**

```json
{
    "printing": {
        "enabled": true,
        "auto_print": true,
        "printer_name": null,
        "use_default_printer": true,
        "silent_print": true
    },
    "pdf": {
        "save_to_temp": true,
        "temp_folder": "temp",
        "auto_delete_after_print": false,
        "keep_days": 7
    }
}
```

---

## 🎯 Metodi di Stampa

L'applicazione prova automaticamente 3 metodi (in ordine):

### **Metodo 1: SumatraPDF** ⭐ (Migliore)

```python
sumatra_path = r"C:\Program Files\SumatraPDF\SumatraPDF.exe"
subprocess.run([
    sumatra_path,
    "-print-to", printer_name,
    "-silent",
    pdf_path
])
```

**Pro:**
- ✅ Completamente silenzioso
- ✅ Nessun dialogo
- ✅ Velocissimo
- ✅ Affidabile

**Contro:**
- ⚠️ Richiede installazione

---

### **Metodo 2: Adobe Reader** (Fallback)

```python
adobe_path = r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
subprocess.run([
    adobe_path,
    "/t", pdf_path,
    printer_name
])
```

**Pro:**
- ✅ Spesso già installato
- ✅ Stampa automatica con `/t`

**Contro:**
- ⚠️ Può mostrare finestra temporanea
- ⚠️ Più lento di SumatraPDF

---

### **Metodo 3: Windows ShellExecute** (Ultimo Fallback)

```python
win32api.ShellExecute(
    0,
    "print",
    pdf_path,
    f'/d:"{printer_name}"',
    ".",
    0
)
```

**Pro:**
- ✅ Sempre disponibile (nativo Windows)
- ✅ Non richiede software esterno

**Contro:**
- ⚠️ Può aprire applicazione predefinita
- ⚠️ Comportamento varia per applicazione

---

## 📊 Monitoraggio Stampa

### **Log Server**

Il server Flask registra ogni tentativo di stampa:

```
2025-12-23 14:30:15 - INFO - Tentativo stampa PDF su: HP LaserJet Pro
2025-12-23 14:30:16 - INFO - PDF inviato alla stampante: HP LaserJet Pro
```

Oppure in caso di errore:

```
2025-12-23 14:30:15 - WARNING - Stampa PDF fallita, PDF salvato in temp/
2025-12-23 14:30:15 - ERROR - Errore stampa PDF: [dettagli errore]
```

### **Notifiche Frontend**

L'utente vede toast notification:

- ✅ **Successo**: "✅ Stampato su: HP LaserJet Pro"
- ⚠️ **Fallimento**: "⚠️ Stampa non riuscita - PDF salvato in temp/"

---

## 🛠️ Risoluzione Problemi

### **Problema: Stampa non funziona**

**Diagnosi:**

1. Verifica stampante predefinita:
```powershell
# PowerShell
Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default = TRUE"
```

2. Verifica SumatraPDF installato:
```powershell
Test-Path "C:\Program Files\SumatraPDF\SumatraPDF.exe"
```

3. Controlla log server per errori

**Soluzioni:**

- ✅ Imposta stampante predefinita Windows
- ✅ Installa SumatraPDF
- ✅ Verifica che stampante sia online
- ✅ Controlla permessi utente per stampare

---

### **Problema: PDF stampato ma vuoto**

**Causa**: Firma amministratore o logo mancanti

**Soluzione**:
1. Verifica firma in database:
```sql
SELECT [Signature] FROM [Employee].[dbo].[Administrators] WHERE adminid = 3
```

2. Verifica logo:
```powershell
Test-Path "static\logo.png"
```

---

### **Problema: Stampa troppo lenta**

**Causa**: Usa Adobe Reader invece di SumatraPDF

**Soluzione**:
1. Installa SumatraPDF
2. Riavvia applicazione
3. Verifica log: dovrebbe dire "Uso SumatraPDF per stampa silenziosa"

---

## 🔐 Sicurezza

### **Permessi Richiesti**

L'applicazione richiede:
- ✅ Permesso di lettura cartella `temp/`
- ✅ Permesso di scrittura cartella `temp/`
- ✅ Permesso di stampa su stampante predefinita

### **Privacy**

- ✅ PDF salvati localmente in `temp/`
- ✅ Nessun invio a server esterni
- ✅ Numero badge oscurato nell'interfaccia
- ✅ PDF eliminati automaticamente dopo 7 giorni

---

## 📈 Statistiche Stampa

### **Script Monitoraggio**

```python
import os
from datetime import datetime, timedelta

def print_statistics():
    temp_folder = "temp"
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    pdfs = [f for f in os.listdir(temp_folder) if f.endswith('.pdf')]
    
    recent_pdfs = []
    for pdf in pdfs:
        filepath = os.path.join(temp_folder, pdf)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        if mtime >= week_ago:
            recent_pdfs.append(pdf)
    
    print(f"📊 Statistiche Ultimi 7 Giorni:")
    print(f"   Certificati generati: {len(recent_pdfs)}")
    print(f"   Media giornaliera: {len(recent_pdfs) / 7:.1f}")
    print(f"   Totale PDF in temp/: {len(pdfs)}")

if __name__ == "__main__":
    print_statistics()
```

---

## 🎛️ Opzioni Avanzate

### **Disabilita Stampa Automatica**

Modifica `print_config.json`:

```json
{
    "printing": {
        "enabled": false,
        "auto_print": false
    }
}
```

Risultato: PDF solo salvato in `temp/`, nessuna stampa

---

### **Usa Stampante Specifica**

```json
{
    "printing": {
        "printer_name": "HP LaserJet Pro MFP M428fdw",
        "use_default_printer": false
    }
}
```

---

### **Elimina PDF Dopo Stampa**

```json
{
    "pdf": {
        "auto_delete_after_print": true
    }
}
```

⚠️ **Attenzione**: Non consigliato! Perdi backup in caso di problemi stampa

---

## 📞 Supporto

### **Elencare Stampanti Disponibili**

```python
from pdf_printer import list_available_printers

printers = list_available_printers()
for printer in printers:
    print(f"📄 {printer}")
```

### **Test Stampa Manuale**

```python
from pdf_printer import print_pdf_silent

pdf_path = "temp/Certificate_20251223143045.pdf"
success = print_pdf_silent(pdf_path)

if success:
    print("✅ Stampa avviata con successo")
else:
    print("❌ Stampa fallita")
```

---

## ✅ Checklist Pre-Produzione

- [ ] Stampante Windows configurata come predefinita
- [ ] SumatraPDF installato in `C:\Program Files\SumatraPDF\`
- [ ] `print_config.json` configurato correttamente
- [ ] Test stampa manuale eseguito con successo
- [ ] Cartella `temp/` creata e scrivibile
- [ ] Dipendenza `pywin32` installata (`pip install pywin32`)
- [ ] Log server verificati per conferma stampa
- [ ] Backup PDF configurato (opzionale)

---

**Ultimo aggiornamento**: 23 Dicembre 2025  
**Versione**: 1.0.0
