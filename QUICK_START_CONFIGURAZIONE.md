# Quick Start - Prima Configurazione Kiosk HR

**Problema:** Server avviato ma errore: "File di configurazione non trovato"

**Soluzione:** Devi configurare la connessione al database (prima volta).

---

## ⚡ Configurazione Rapida (5 minuti)

### Step 1: Attiva Virtual Environment

```powershell
# Apri PowerShell nella cartella del progetto
cd C:\Wandewiele\Kiosk

# Attiva virtual environment
.\venv\Scripts\Activate.ps1
```

**Verifica:** Dovresti vedere `(venv)` all'inizio del prompt.

---

### Step 2: Esegui Setup Database

```powershell
python setup.py
```

Lo script ti chiederà:

```
=== CONFIGURAZIONE DATABASE ===

Driver ODBC (default: ODBC Driver 17 for SQL Server):
[Premi INVIO se va bene]

Server (es: localhost\SQLEXPRESS):
> INSERISCI_QUI_IL_TUO_SERVER

Database (es: Employee):
> Employee

Username (es: sa):
> INSERISCI_USERNAME

Password:
> INSERISCI_PASSWORD

[Testa connessione...]
✓ Connessione riuscita!
✓ Configurazione salvata in db_config.enc
```

---

### Step 3: Configurazione Email (Opzionale)

Se vuoi abilitare le notifiche email:

```powershell
python setup.py --email
```

Ti chiederà:
- Server SMTP (es: smtp.gmail.com)
- Porta (es: 587)
- Username email
- Password email

**NOTA:** Puoi saltare questo step per ora e configurarlo dopo.

---

### Step 4: Riavvia Server

```powershell
# Se il server è ancora attivo, fermalo (Ctrl+C)

# Riavvia
python app.py
```

**Verifica:** Dovresti vedere:
```
 * Running on http://0.0.0.0:5000
```

Apri browser su: **http://localhost:5000**

---

## 🔍 Verifica Configurazione

Dopo aver eseguito setup.py, dovresti avere questi file:

```
C:\Wandewiele\Kiosk\
  ├── db_config.enc           ✓ (creato da setup.py)
  ├── encryption_key.key      ✓ (creato automaticamente)
  ├── email_credentials.enc   ⚠ (opzionale)
  ├── email_key.key          ⚠ (opzionale)
  └── config.ini             ✓ (già presente)
```

---

## 📋 Parametri Comuni Database

### SQL Server Locale
```
Driver: ODBC Driver 17 for SQL Server
Server: localhost\SQLEXPRESS
Database: Employee
Username: sa
Password: [tua password]
```

### SQL Server Remoto
```
Driver: ODBC Driver 17 for SQL Server
Server: 192.168.1.100
Database: Employee
Username: kiosk_user
Password: [tua password]
```

### Autenticazione Windows
```
Driver: ODBC Driver 17 for SQL Server
Server: SERVER_NAME
Database: Employee
Username: (lascia vuoto)
Password: (lascia vuoto)
```

**NOTA:** Per autenticazione Windows, lo script setup.py potrebbe richiedere modifiche.

---

## ❌ Problemi Comuni

### Errore: "ODBC Driver not found"

**Soluzione:** Installa ODBC Driver 17:
```
https://go.microsoft.com/fwlink/?linkid=2249004
```

Dopo installazione, esegui di nuovo `python setup.py`

---

### Errore: "Login failed for user"

**Cause:**
- Username/password errati
- SQL Server non accetta connessioni remote
- Firewall blocca porta 1433

**Verifica:**
1. Testa connessione con SQL Server Management Studio (SSMS)
2. Verifica che SQL Server sia in modalità "Mixed Authentication"
3. Controlla firewall Windows

---

### Errore: "Cannot open database 'Employee'"

**Soluzione:**
- Verifica che il database `Employee` esista
- Verifica che l'utente abbia permessi su quel database

**Per creare/verificare database:**
```sql
-- In SSMS
USE master;
GO

-- Verifica se esiste
SELECT name FROM sys.databases WHERE name = 'Employee';

-- Dai permessi all'utente
USE Employee;
GRANT SELECT, INSERT, UPDATE, DELETE TO [nome_utente];
```

---

## 🚀 Test Rapido

Dopo la configurazione:

```powershell
# Test connessione database
python check_news.py
```

**Output atteso:**
```
Data corrente: 2026-01-09 14:25:00
---
NEWS ATTIVE TROVATE: 0
(o mostra le news se presenti)
```

Se vedi questo, **la configurazione è OK!** ✅

---

## 📞 Hai Ancora Problemi?

1. **Controlla i log:**
   - Guarda l'output del server `python app.py`
   - Cerca errori specifici

2. **Verifica file creati:**
   ```powershell
   dir db_config.enc
   dir encryption_key.key
   ```

3. **Test connessione manuale:**
   ```powershell
   python
   >>> from config_manager import ConfigManager
   >>> from db_connection import DatabaseConnection
   >>> cm = ConfigManager()
   >>> db = DatabaseConnection(cm)
   >>> conn = db.connect()
   >>> print("OK!" if conn else "ERRORE")
   ```

---

**Prossimi passi dopo configurazione:**
1. ✅ Server funzionante
2. ✅ Database connesso
3. 📄 Consultare README.md per funzionalità complete
4. 🎯 Inserire news di test (vedi GUIDA_SQL_NEWS.md)

---

**Creato:** 2026-01-09  
**Per:** Prima configurazione Kiosk HR dopo installazione
