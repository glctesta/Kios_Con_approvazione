# Guida Installazione Rapida - Kiosk HR v2.2.0

## 📦 Contenuto Pacchetto

Il pacchetto ZIP contiene:
- ✅ Applicazione Python completa
- ✅ Templates HTML/CSS con sistema News & Slideshow
- ✅ Script di installazione automatica
- ✅ Documentazione completa
- ✅ Immagini slideshow (X* e S*)
- ✅ Font, loghi e risorse

## 🚀 Installazione in 5 Passi

### 1️⃣ **Prerequisiti**

Prima di iniziare, assicurati di avere:
- **Windows 10/11**
- **Python 3.11** installato ([Download](https://www.python.org/downloads/))
  - ⚠️ Durante l'installazione Python, selezionare "Add Python to PATH"
- **SQL Server** accessibile (database Employee)
- **Privilegi Amministratore** sulla macchina

### 2️⃣ **Estrazione Pacchetto**

1. Copiare il file ZIP sulla macchina target
2. Estrarre in una directory (es: `C:\KioskHR\`)
3. Aprire la directory estratta

### 3️⃣ **Installazione Automatica**

1. **Fare clic destro** su `INSTALLA.bat`
2. Selezionare **"Esegui come amministratore"**
3. Lo script eseguirà automaticamente:
   - ✅ Verifica Python 3.11
   - ✅ Creazione ambiente virtuale
   - ✅ Installazione dipendenze
   - ✅ Verifica file di configurazione
   - ✅ Creazione directory necessarie

### 4️⃣ **Configurazione Database ed Email**

1. Eseguire `setup.py`:
   ```bash
   python setup.py
   ```

2. Inserire i parametri richiesti:
   - **Database SQL Server**:
     - Server: `nome_server` o `IP:porta`
     - Database: `Employee`
     - Username: `utente_sql`
     - Password: `password_sql`
   
   - **Email SMTP**:
     - Server: `smtp.server.com`
     - Porta: `587` (o 25, 465)
     - Username: `email@domain.com`
     - Password: `password_email`

3. Le credenziali vengono salvate **crittografate** in:
   - `db_config.enc`
   - `email_credentials.enc`

### 5️⃣ **Avvio Applicazione**

#### Modalità Normale (Test)
```bash
START_APP.bat
```
- Apre browser su `http://localhost:5000`
- Ideale per test e debug

#### Modalità Kiosk (Produzione)
```bash
START_SISTEMA_KIOSK.bat
```
- Avvia in fullscreen
- Nasconde barra indirizzi
- Modalità kiosk completa

## 🔧 Configurazione Aggiuntiva

### Sistema News & Slideshow

#### Creare Tabella News (se non esiste)
```sql
CREATE TABLE [Employee].[dbo].[News] (
    [NewId] INT IDENTITY(1,1) PRIMARY KEY,
    [EmployeerId] INT NULL,
    [StartNews] DATETIME NOT NULL,
    [EndNews] DATETIME NOT NULL,
    [News] NVARCHAR(MAX) NOT NULL,
    [Publisher] NVARCHAR(255) NOT NULL,
    [IsMandatory] BIT NOT NULL DEFAULT 0
)
```

#### Aggiungere Messaggi
```sql
-- Messaggio normale
INSERT INTO [Employee].[dbo].[News] 
VALUES ('2026-01-03 08:00:00', '2026-01-10 18:00:00', 
        'Benvenuti nel nuovo sistema Kiosk HR!',
        'IT Department', 0)

-- Messaggio urgente
INSERT INTO [Employee].[dbo].[News] 
VALUES ('2026-01-03 00:00:00', '2026-01-03 23:59:59', 
        '⚠️ Manutenzione sistema oggi pomeriggio 14:00-16:00',
        'IT Department', 1)
```

#### Aggiungere Immagini Slideshow
1. Rinominare immagini con prefisso **X** o **S**:
   - `X_evento.jpg`
   - `S_safety.jpg`
2. Copiare in directory `Images/`
3. Refresh pagina launcher

### Stampante (Opzionale)

Se si desidera la stampa automatica:
1. Configurare stampante predefinita in Windows
2. Modificare `print_config.json` se necessario
3. Testare con generazione certificato

### Lettore RFID (Opzionale)

Se si ha un lettore RFID:
1. Verificare presenza `IDReader.dll`
2. Consultare `GUIDA_RFID.md`
3. Installare driver lettore

## 🌐 Accesso da Rete

Per accedere da altri PC sulla rete:

1. **Trovare IP della macchina**:
   ```bash
   ipconfig
   ```
   Cercare "Indirizzo IPv4"

2. **Configurare Firewall**:
   - Aprire porta 5000
   - O eseguire `MOSTRA_IP_KIOSK.bat` (se presente)

3. **Accedere da altri PC**:
   ```
   http://<IP-MACCHINA>:5000
   ```

## ✅ Verifica Installazione

### Test Funzionalità Base

1. **Pagina Launcher**: `http://localhost:5000`
   - ✅ Logo aziendale visibile
   - ✅ 4 bottoni servizi
   - ✅ Riquadro news/slideshow funzionante

2. **Generazione Certificati**: `/certificati`
   - ✅ Scansione badge
   - ✅ Selezione motivo
   - ✅ Generazione PDF

3. **Richiesta Assenza**: `/cerere`
   - ✅ Scansione badge
   - ✅ Selezione tipo assenza
   - ✅ Calcolo giorni lavorativi
   - ✅ Invio richiesta

4. **Sistema News**:
   - ✅ Messaggi dal database visualizzati
   - ✅ Rotazione automatica
   - ✅ Priorità mandatory funzionante

5. **Slideshow**:
   - ✅ Immagini X* e S* visualizzate
   - ✅ Ordine random
   - ✅ Rotazione ogni 5 secondi

## 🆘 Risoluzione Problemi

### Errore: Python non trovato
**Soluzione**: Installare Python 3.11 e selezionare "Add to PATH"

### Errore: Connessione database fallita
**Soluzione**: 
- Verificare credenziali in `setup.py`
- Testare connessione SQL Server
- Controllare firewall

### News non visualizzate
**Soluzione**:
- Verificare tabella `Employee.dbo.News` esiste
- Controllare date: `StartNews <= Oggi <= EndNews`
- Aprire console browser (F12) per errori

### Slideshow non funziona
**Soluzione**:
- Verificare directory `Images/` esiste
- Verificare immagini iniziano con X o S
- Controllare formati: JPG, PNG, GIF, BMP, WEBP

### Stampa non funziona
**Soluzione**:
- Configurare stampante predefinita
- Verificare driver stampante
- Controllare `print_config.json`

## 📚 Documentazione Completa

Per maggiori dettagli, consultare:
- **README.md** - Panoramica generale
- **GUIDA_RAPIDA.md** - Guida utente
- **GUIDA_NEWS_SLIDESHOW.md** - Sistema news e slideshow
- **DEPLOYMENT.md** - Deploy in produzione
- **CONFIGURAZIONE_RETE.md** - Accesso da rete
- **STAMPA_AUTOMATICA.md** - Configurazione stampa
- **GUIDA_RFID.md** - Lettore badge RFID
- **GUIDA_KIOSK_FULLSCREEN.md** - Modalità kiosk

## 📞 Supporto

Per assistenza:
- **Email**: gianluca.testa@vandewiele.com
- **GitHub**: https://github.com/glctesta/kiosk-hr-adeverente

## 🔄 Aggiornamenti

Per aggiornare a una versione successiva:
1. Fare backup di `db_config.enc` e `email_credentials.enc`
2. Estrarre nuovo pacchetto
3. Ripristinare file di configurazione
4. Eseguire `INSTALLA.bat`

---

**Versione**: 2.2.0  
**Data**: 2026-01-03  
**Sviluppato da**: GTMC (Gianluca Testa)  
**Per**: Vandewiele Romania
