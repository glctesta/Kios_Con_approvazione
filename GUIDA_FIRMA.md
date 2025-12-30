# 📝 GUIDA AGGIORNAMENTO FIRMA AMMINISTRATORE

## 📋 Panoramica

Questo programma permette di aggiornare la firma dell'amministratore che appare nei certificati PDF generati.

---

## 🚀 AVVIO RAPIDO

### Metodo 1: Doppio Click
1. Doppio click su `AGGIORNA_FIRMA.bat`
2. Si apre la finestra del programma

### Metodo 2: Python Diretto
```powershell
python update_signature.py
```

---

## 💻 INTERFACCIA PROGRAMMA

### Sezione "Firma Corrente"
- Mostra la firma attualmente nel database
- Nome amministratore
- Dimensioni immagine

### Sezione "Nuova Firma"
- Bottone "Seleziona Immagine Firma"
- Preview della nuova firma
- Info file selezionato

### Bottoni Azione
- **✅ Aggiorna Firma**: Salva nuova firma nel database
- **❌ Annulla**: Chiude programma senza modifiche

---

## 📸 REQUISITI IMMAGINE FIRMA

### Formati Supportati
- ✅ PNG (consigliato)
- ✅ JPG / JPEG
- ✅ BMP

### Dimensioni Consigliate
- **Larghezza**: 300-500 px
- **Altezza**: 100-200 px
- **Proporzioni**: Circa 3:1 (orizzontale)

### Qualità
- **Risoluzione**: 150-300 DPI
- **Sfondo**: Trasparente (PNG) o bianco
- **Colore**: Preferibilmente nero o blu scuro

---

## 🎨 COME CREARE UNA FIRMA DIGITALE

### Opzione A: Scansione Firma Manuale

1. **Firma su carta bianca** con penna nera
2. **Scansiona** a 300 DPI
3. **Ritaglia** solo la firma (senza bordi)
4. **Salva** come PNG

### Opzione B: Firma con Tablet/iPad

1. Usa app firma digitale (es. Adobe Sign, DocuSign)
2. Firma con stilo
3. Esporta come PNG trasparente
4. Ridimensiona se necessario

### Opzione C: Usa Firma Esistente

1. Apri immagine firma esistente
2. Rimuovi sfondo (se necessario)
3. Ridimensiona a dimensioni consigliate
4. Salva come PNG

---

## 📝 PROCEDURA AGGIORNAMENTO

### Step 1: Avvia Programma
```
Doppio click su AGGIORNA_FIRMA.bat
```

### Step 2: Verifica Firma Corrente
- Controlla che sia visualizzata correttamente
- Annota nome amministratore

### Step 3: Seleziona Nuova Firma
1. Click su "📁 Seleziona Immagine Firma"
2. Naviga alla cartella con la firma
3. Seleziona file immagine
4. Verifica preview

### Step 4: Conferma Aggiornamento
1. Click su "✅ Aggiorna Firma"
2. Conferma operazione
3. Attendi messaggio successo

### Step 5: Verifica
- La firma corrente ora mostra la nuova immagine
- Genera un certificato di test per verificare

---

## ⚙️ CONFIGURAZIONE DATABASE

Il programma usa `db_config.json` per connettersi al database.

**Struttura**:
```json
{
    "server": "nome_server",
    "database": "Employee",
    "username": "utente",
    "password": "password"
}
```

**Tabella**: `Employee.dbo.Administrators`  
**Campo**: `Signature` (VARBINARY)  
**Condizione**: `adminid = 3`

---

## 🔍 RISOLUZIONE PROBLEMI

### Problema: "Impossibile caricare db_config.json"

**Causa**: File configurazione mancante o non valido

**Soluzione**:
1. Verifica che `db_config.json` esista nella cartella
2. Controlla sintassi JSON
3. Verifica credenziali database

---

### Problema: "Connessione database fallita"

**Causa**: Credenziali errate o server non raggiungibile

**Soluzione**:
1. Verifica credenziali in `db_config.json`
2. Testa connessione con SQL Server Management Studio
3. Controlla firewall/rete

---

### Problema: "Nessuna firma trovata nel database"

**Causa**: Record amministratore non ha firma

**Soluzione**:
1. Verifica che `adminid = 3` esista
2. Carica una nuova firma con il programma
3. Controlla permessi database

---

### Problema: "Impossibile caricare immagine"

**Causa**: Formato file non supportato o corrotto

**Soluzione**:
1. Usa formato PNG, JPG o BMP
2. Verifica che file non sia corrotto
3. Prova a convertire in PNG

---

### Problema: "Impossibile aggiornare firma"

**Causa**: Permessi database insufficienti

**Soluzione**:
1. Verifica permessi UPDATE su tabella Administrators
2. Usa utente con privilegi adeguati
3. Controlla log errori

---

## 📊 VERIFICA FIRMA AGGIORNATA

### Test Immediato

1. **Genera certificato**:
   - Avvia applicazione principale
   - Genera un certificato qualsiasi
   
2. **Apri PDF generato**:
   - Controlla firma in basso a destra
   - Verifica che sia la nuova firma

3. **Controlla database**:
```sql
SELECT 
    A.adminid,
    E.EmployeeName + ' ' + E.EmployeeSurname AS Administrator,
    DATALENGTH(A.Signature) AS SignatureSize
FROM [Employee].[dbo].[Administrators] A
INNER JOIN [Employee].[dbo].[Employees] E 
    ON A.EmployeeID = E.EmployeeId
WHERE A.adminid = 3
```

---

## 💡 CONSIGLI

### Best Practices

1. **Backup**: Esporta firma corrente prima di sostituirla
2. **Test**: Genera certificato di test dopo aggiornamento
3. **Qualità**: Usa immagini ad alta risoluzione
4. **Formato**: Preferisci PNG con sfondo trasparente
5. **Dimensioni**: Non troppo grande (max 100 KB)

### Quando Aggiornare

- ✅ Cambio amministratore
- ✅ Firma danneggiata/illeggibile
- ✅ Migliore qualità disponibile
- ✅ Requisiti legali cambiati

---

## 🔒 SICUREZZA

### Permessi Richiesti

- **Lettura**: `Employee.dbo.Administrators`
- **Scrittura**: `Employee.dbo.Administrators`
- **Connessione**: Database SQL Server

### Log Operazioni

Il programma registra:
- Caricamento firma corrente
- Selezione nuova firma
- Aggiornamento database
- Errori eventuali

---

## 📞 SUPPORTO

### Log Errori

Controlla console Python per messaggi dettagliati:
```
INFO - Firma corrente caricata: Nome Cognome
INFO - Nuova firma selezionata: firma.png
INFO - Firma aggiornata nel database
```

### Query Diagnostica

```sql
-- Verifica firma presente
SELECT 
    adminid,
    CASE WHEN Signature IS NULL THEN 'NO' ELSE 'SI' END AS HasSignature,
    DATALENGTH(Signature) AS SizeBytes
FROM [Employee].[dbo].[Administrators]
WHERE adminid = 3
```

---

**Ultimo aggiornamento**: 23 Dicembre 2025  
**Versione**: 1.0.0
