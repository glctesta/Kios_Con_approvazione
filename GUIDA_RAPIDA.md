# 🚀 GUIDA RAPIDA - Sistema Generare Adeverințe

## 📋 Indice
1. [Avvio Applicazione](#avvio-applicazione)
2. [Utilizzo](#utilizzo)
3. [Configurazione Database](#configurazione-database)
4. [Risoluzione Problemi](#risoluzione-problemi)

---

## 🎯 Avvio Applicazione

### **Metodo 1: Doppio Click (CONSIGLIATO)** ✅

1. **Doppio click** su `START_APP.bat`
2. Attendi che appaia: `Server in esecuzione su: http://localhost:5000`
3. Apri il browser e vai su: **http://localhost:5000**

### **Metodo 2: Manuale**

```powershell
# 1. Apri PowerShell nella cartella del progetto
cd c:\Users\gtesta\PythonProjetcs\Python\Adeverente

# 2. Attiva ambiente virtuale
.\venv\Scripts\Activate.ps1

# 3. Avvia server
python app.py
```

### **Metodo 3: Visual Studio Code**

1. Apri il progetto in VS Code
2. Premi `F5` oppure
3. Apri terminale integrato e digita: `python app.py`

---

## 💻 Utilizzo dell'Applicazione

### **Flusso Operativo**

```
1. Avvicina Badge RFID → 2. Sistema riconosce dipendente → 3. Seleziona motivo → 4. Genera PDF → 5. Stampa Automatica
```

### **Passaggi Dettagliati**

#### **1. Lettura Badge** 🔖
- Avvicina il badge al lettore RFID
- Il numero viene inserito automaticamente (oscurato con `••••••••••`)
- Sistema valida il badge in tempo reale

#### **2. Riconoscimento Dipendente** ✅
- Se badge valido: appare nome dipendente
- Toast notification: "Bun venit [NOME]!"
- Status verde: "✅ Recunoscut"

#### **3. Selezione Motivo** 📝
- Scegli dal menu a tendina:
  - Banca
  - Asigurari
  - Pensie
  - Altele (campo personalizzato)

#### **4. Generazione Certificato** 📄
- Click su "Generează Adeverință"
- PDF generato automaticamente
- **Stampa automatica sulla stampante predefinita** 🖨️
- Toast notification mostra stato stampa

#### **5. Stampa Automatica** 🖨️
- **PDF stampato automaticamente** sulla stampante Windows predefinita
- Notifica: "✅ Stampato su: [NOME_STAMPANTE]"
- Se stampa fallisce: "⚠️ Stampa non riuscita - PDF salvato in temp/"
- PDF sempre salvato in `temp/` come backup

#### **6. Reset** 🔄
- Click "Resetează" per nuovo certificato
- Form si svuota automaticamente
- Auto-reset dopo 30 secondi di inattività

---

## 🖨️ Configurazione Stampa

### **Stampante Predefinita**

L'applicazione usa la **stampante predefinita di Windows**. Per configurarla:

```
1. Pannello di Controllo → Dispositivi e Stampanti
2. Click destro sulla stampante desiderata
3. "Imposta come stampante predefinita"
```

### **Metodi di Stampa Supportati**

L'applicazione prova automaticamente (in ordine):

1. **SumatraPDF** (consigliato per stampa silenziosa)
   - Scarica da: https://www.sumatrapdfreader.org/
   - Installa in: `C:\Program Files\SumatraPDF\`

2. **Adobe Reader** (se installato)
   - Usa il comando `/t` per stampa automatica

3. **Comando Windows nativo** (fallback)
   - Usa `ShellExecute` con comando "print"

### **File di Configurazione: `print_config.json`**

```json
{
    "printing": {
        "enabled": true,              // Abilita stampa
        "auto_print": true,           // Stampa automatica
        "printer_name": null,         // null = usa predefinita
        "use_default_printer": true,  // Usa stampante predefinita
        "silent_print": true          // Stampa silenziosa (no dialog)
    },
    "pdf": {
        "save_to_temp": true,         // Salva sempre in temp/
        "temp_folder": "temp",        // Cartella temporanea
        "auto_delete_after_print": false,  // Non cancellare dopo stampa
        "keep_days": 7                // Mantieni 7 giorni
    }
}
```

### **Disabilitare Stampa Automatica**

Se vuoi solo salvare il PDF senza stampare:

```json
{
    "printing": {
        "enabled": false,
        "auto_print": false
    }
}
```

### **Usare Stampante Specifica**

Per usare sempre una stampante specifica:

```json
{
    "printing": {
        "printer_name": "HP LaserJet Pro",
        "use_default_printer": false
    }
}
```

### **Elencare Stampanti Disponibili**

```python
# Esegui in Python per vedere tutte le stampanti
from pdf_printer import list_available_printers
print(list_available_printers())
```

---

## 📁 Gestione PDF

### **Dove Vengono Salvati i PDF?**

- **Cartella**: `temp/`
- **Nome file**: `Certificate_YYYYMMDDHHMMSS.pdf` o `Adv7_YYYYMMDDHHMMSS.pdf`
- **Esempio**: `Certificate_20251223143045.pdf`

### **Pulizia Automatica**

I PDF vengono mantenuti per 7 giorni (configurabile). Per pulire manualmente:

```powershell
# Elimina PDF più vecchi di 7 giorni
Get-ChildItem temp\*.pdf | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item
```

### **Backup PDF**

Consigliato creare backup periodico:

```powershell
# Copia tutti i PDF in cartella backup
xcopy temp\*.pdf backup\ /D /Y
```

---

## 🗄️ Configurazione Database

### **File di Configurazione**

Il file `db_config.json` contiene le credenziali:

```json
{
    "server": "NOME_SERVER",
    "database": "Employee",
    "username": "utente",
    "password": "password"
}
```

### **Tabelle Utilizzate**

| Tabella | Scopo |
|---------|-------|
| `Employee.dbo.Employees` | Dati dipendenti |
| `Employee.dbo.EmployeeHireHistory` | Storico assunzioni |
| `Employee.dbo.Administrators` | **Firma amministratore** |
| `Timeclocking.dbo.Employee` | Badge RFID |
| `Employee.dbo.Registro` | Numerazione documenti |

### **Query Firma Amministratore**

```sql
SELECT [Signature]
FROM [Employee].[dbo].[Administrators] 
WHERE adminid = 3
```

---

## 🔧 Risoluzione Problemi

### **Problema: Server non si avvia**

**Errore**: `ModuleNotFoundError: No module named 'flask'`

**Soluzione**:
```powershell
# Attiva ambiente virtuale
.\venv\Scripts\Activate.ps1

# Installa dipendenze
pip install -r requirements.txt
```

---

### **Problema: Logo non appare**

**Causa**: File `static/logo.png` mancante

**Soluzione**:
```powershell
# Copia il tuo logo
copy "percorso\tuo\logo.png" "static\logo.png"
```

**Nota**: L'app funziona anche senza logo (viene nascosto automaticamente)

---

### **Problema: Badge non riconosciuto**

**Errore**: "❌ Badge non riconosciuto o dipendente non attivo"

**Verifica**:
1. Badge esiste in `Timeclocking.dbo.Employee`?
2. Dipendente ha `EndWorkDate IS NULL`?
3. Connessione database attiva?

**Query di test**:
```sql
SELECT E.EmployeeName, E.EmployeeSurname, ET.UniqueID
FROM Employee.dbo.Employees E
INNER JOIN Timeclocking.dbo.Employee ET 
    ON E.EmployeeNID = ET.UniqueID
WHERE ET.DataStop IS NULL
```

---

### **Problema: Firma non appare nel PDF**

**Causa**: Firma non presente nel database

**Verifica**:
```sql
SELECT [Signature]
FROM [Employee].[dbo].[Administrators] 
WHERE adminid = 3
```

**Soluzione**: Inserisci firma come VARBINARY nel database

---

### **Problema: Porta 5000 già in uso**

**Errore**: `Address already in use`

**Soluzione 1** - Cambia porta in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Cambia porta
```

**Soluzione 2** - Termina processo esistente:
```powershell
# Trova processo
netstat -ano | findstr :5000

# Termina processo (sostituisci PID)
taskkill /PID <numero_pid> /F
```

---

## 📁 Struttura Progetto

```
Adeverente/
├── app.py                      # Server Flask principale
├── certificate_generator.py    # Generazione PDF
├── db_config.json             # Configurazione database
├── requirements.txt           # Dipendenze Python
├── START_APP.bat              # Script avvio rapido
│
├── static/                    # File statici
│   ├── css/
│   │   └── styles.css        # Stili CSS
│   ├── js/
│   │   └── app.js            # Logica frontend
│   └── logo.png              # Logo aziendale (opzionale)
│
├── templates/                 # Template HTML
│   └── index.html            # Interfaccia principale
│
├── temp/                      # PDF generati (temporanei)
│
└── venv/                      # Ambiente virtuale Python
```

---

## 🎨 Personalizzazione

### **Cambiare Colori**

Modifica `static/css/styles.css`:

```css
:root {
    --primary-color: #2563eb;      /* Blu principale */
    --success-color: #10b981;      /* Verde successo */
    --danger-color: #ef4444;       /* Rosso errore */
}
```

### **Aggiungere Motivi Certificato**

Modifica `templates/index.html`:

```html
<select id="reasonSelect">
    <option value="">Selectați motivul...</option>
    <option value="Banca">Banca</option>
    <option value="Asigurari">Asigurari</option>
    <option value="NUOVO_MOTIVO">Nuovo Motivo</option>  <!-- Aggiungi qui -->
</select>
```

---

## 📊 Monitoraggio

### **Log Server**

I log appaiono nel terminale:

```
2025-12-23 14:13:36 - INFO - Badge validato: 0009969135
2025-12-23 14:13:38 - INFO - Certificato generato: Certificate_20251223141338.pdf
```

### **Log Browser**

Apri Console Sviluppatore (`F12`):

```javascript
✅ App.js loaded successfully
🚀 Certificate Generator - KIOSK MODE initialized
✅ Badge validato: TESTA GIANLUCA
```

---

## � Sicurezza

### **Privacy Badge**
- ✅ Numero badge oscurato con `type="password"`
- ✅ Non visualizzato nell'interfaccia
- ✅ Trasmesso solo via HTTPS in produzione

### **Database**
- ✅ Credenziali in `db_config.json` (escluso da Git)
- ✅ Connessione con autenticazione SQL Server
- ✅ Query parametrizzate (protezione SQL injection)

---

## 📞 Supporto

### **Contatti**
- **Sviluppatore**: Gianluca Testa
- **Email**: gtesta@vandewiele.com

### **Documentazione Aggiuntiva**
- `README.md` - Panoramica generale
- `GUIDA_RAPIDA.md` - Questo documento
- Commenti nel codice sorgente

---

## ✅ Checklist Pre-Produzione

- [ ] Database configurato correttamente
- [ ] Logo aziendale copiato in `static/logo.png`
- [ ] Firma amministratore presente nel database
- [ ] Badge RFID testati e funzionanti
- [ ] Stampante configurata per PDF
- [ ] Backup database attivo
- [ ] Ambiente virtuale attivato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)

---

**Ultimo aggiornamento**: 23 Dicembre 2025  
**Versione**: 1.0.0
