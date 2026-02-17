# Kiosk Reports Service - Guida Installazione

## 📋 Panoramica

Il **Kiosk Reports Service** è un servizio Windows che invia automaticamente report mensili sull'utilizzo del Kiosk HR il primo giorno di ogni mese alle ore 08:00.

## ✅ Prerequisiti

- Windows Server o Windows 10/11
- Privilegi di amministratore
- Connessione al database SQL Server configurata
- File `db_config.enc` presente nella directory del servizio

## 🚀 Installazione Rapida

### Passo 1: Build del Servizio (già completato)

Il servizio è già stato compilato e l'eseguibile si trova in:
```
dist\KioskReportsService.exe
```

### Passo 2: Installazione del Servizio

1. **Apri PowerShell o CMD come Amministratore**
   - Tasto destro su PowerShell/CMD → "Esegui come amministratore"

2. **Naviga nella directory del progetto**
   ```batch
   cd C:\Users\gtesta\PythonProjetcs\Python\Adeverente
   ```

3. **Esegui lo script di installazione**
   ```batch
   INSTALL_SERVICE.bat
   ```

4. **Verifica l'installazione**
   ```batch
   sc query KioskReportsService
   ```
   
   Dovresti vedere:
   ```
   STATE              : 4  RUNNING
   ```

## 📊 Funzionalità

- ✅ **Avvio automatico** all'avvio di Windows
- ✅ **Riavvio automatico** in caso di crash (fino a 3 tentativi)
- ✅ **Controllo giornaliero** alle 08:00
- ✅ **Invio report** solo il 1° giorno del mese
- ✅ **Logging completo** in `kiosk_reports_service.log`

## 📧 Destinatari Email

I report vengono inviati automaticamente a:
- Gianluca.Testa@Vandewiele.com
- Cornelia.Ormenisan@Vandewiele.com

## 🔧 Gestione del Servizio

### Comandi Utili

```batch
# Avvia il servizio
net start KioskReportsService

# Ferma il servizio
net stop KioskReportsService

# Riavvia il servizio
net stop KioskReportsService && net start KioskReportsService

# Verifica stato
sc query KioskReportsService

# Visualizza log
type kiosk_reports_service.log
```

### Disinstallazione

Per rimuovere il servizio:
```batch
# Esegui come Amministratore
UNINSTALL_SERVICE.bat
```

## 📝 Contenuto del Report

Ogni report include:

### Statistiche Mensili
- Totale richieste
- Richieste completate con successo
- Richieste fallite
- Utenti unici
- Terminali unici
- Tasso di successo

### Statistiche Year-To-Date (YTD)
- Totale richieste dall'inizio dell'anno
- Statistiche cumulative
- Trend di utilizzo

### Top 10
- Tipi di richieste più frequenti (mensili e YTD)
- Utenti più attivi (mensili e YTD)

## 🔍 Troubleshooting

### Il servizio non si avvia

1. **Verifica i log**
   ```batch
   type kiosk_reports_service.log
   ```

2. **Verifica la connessione al database**
   - Assicurati che `db_config.enc` sia presente
   - Verifica che il database sia raggiungibile

3. **Verifica le credenziali email**
   - Il servizio usa le credenziali hardcoded in `service_kiosk_reports.py`

### Il report non viene inviato

1. **Verifica la data**
   - Il report viene inviato SOLO il 1° del mese

2. **Controlla i log**
   ```batch
   type kiosk_reports_service.log
   ```

3. **Test manuale**
   - Modifica `service_kiosk_reports.py` (righe 546-547)
   - Decommenta le righe di test
   - Ricompila e reinstalla

### Ricompilare il servizio

Se devi modificare il codice:

1. **Modifica i file Python** necessari

2. **Ricompila**
   ```batch
   BUILD_SERVICE.bat
   ```

3. **Reinstalla**
   ```batch
   UNINSTALL_SERVICE.bat
   INSTALL_SERVICE.bat
   ```

## 📂 Struttura File

```
Adeverente/
├── dist/
│   └── KioskReportsService.exe      # Eseguibile del servizio
├── service_kiosk_reports.py          # Logica principale
├── service_wrapper.py                # Wrapper Windows Service
├── build_service.spec                # Configurazione PyInstaller
├── BUILD_SERVICE.bat                 # Script di compilazione
├── INSTALL_SERVICE.bat               # Script di installazione
├── UNINSTALL_SERVICE.bat             # Script di disinstallazione
├── db_config.enc                     # Configurazione DB (criptata)
└── kiosk_reports_service.log         # Log del servizio
```

## 🎯 Prossimi Passi

1. ✅ Build completato
2. ⏳ Installazione del servizio
3. ⏳ Verifica funzionamento
4. ⏳ Monitoraggio primo invio (1° del mese prossimo)

## 📞 Supporto

Per problemi o domande:
- Controlla i log: `kiosk_reports_service.log`
- Verifica lo stato: `sc query KioskReportsService`
- Consulta questa guida per troubleshooting

---

**Versione**: 1.0  
**Data creazione**: 2026-02-17  
**Autore**: Sistema Kiosk HR
