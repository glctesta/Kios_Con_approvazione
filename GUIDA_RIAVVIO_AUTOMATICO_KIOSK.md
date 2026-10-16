# 🔄 RIPARTENZA AUTOMATICA DEL KIOSK DOPO SPEGNIMENTO (v2.4.1)

Sistema ricostruito per fare in modo che il kiosk HR **riparta da solo in
modalità kiosk** quando il PC viene spento (interruzione di corrente compresa),
**senza privilegi di amministratore**.

## 🔗 La catena di avvio

```
Accensione PC  →  accesso utente Windows (autologon)
   →  HKCU\...\Run  +  cartella "Esecuzione automatica"   [doppia copertura]
      →  wscript.exe AVVIO_KIOSK.vbs                       [nessuna finestra]
         →  pythonw kiosk_supervisor.py                    [single-instance]
            →  app.py (server Flask)                       [riavviato se crasha]
            →  Chrome/Edge --kiosk --incognito             [riaperto se chiuso]
```

| Componente | Ruolo |
|----|----|
| `INSTALLA_AUTOSTART.bat` | Registra l'avvio automatico (senza admin), verifica e logga |
| `HKCU\...\Run` | Prima registrazione: valore `KioskHR_Autostart` per-utente |
| Cartella *Esecuzione automatica* | Seconda registrazione: `KioskHR_Autostart.vbs` generato con percorsi assoluti |
| `AVVIO_KIOSK.vbs` | Launcher nascosto: risolve la cartella del progetto e il pythonw (venv prima, PATH poi) |
| `kiosk_supervisor.py` | Supervisore: mantiene vivi server e browser kiosk |
| `RIMUOVI_AUTOSTART.bat` | Rimozione pulita di tutto (senza admin) |

## 🛡️ Perché è solido e sicuro

**Solido:**
- *Doppia copertura*: se una delle due registrazioni venisse rimossa da policy
  o pulizie di sistema, l'altra fa comunque partire il kiosk.
- *Single-instance*: il supervisore blocca un socket locale (127.0.0.1:39731)
  come mutex — mai due supervisori, anche con doppia partenza contemporanea.
  Il lock è rilasciato automaticamente dal sistema operativo a processo morto.
- *Server già attivo?* Se `/api/health` risponde già all'avvio (es. avviato da
  altri), il supervisore non duplica il server e gestisce solo il browser.
- *Crash del server*: riavvio automatico con backoff (5 s; pausa di 60 s dopo
  5 crash in 2 minuti, per non infiammare i log in caso di guasto persistente).
- *Browser chiuso*: la finestra kiosk viene riaperta (verifica ogni 10 s della
  finestra principale, immune ai processi in background di Edge/Chrome).
- *Spegnimento improvviso*: Chrome parte in `--incognito`, quindi niente
  prompt "Ripristinare le pagine?" al riavvio.
- *Avvio pulito*: il browser viene aperto solo dopo che `/api/health` risponde
  (max 150 s di grazia, poi kill e riavvio del server).

**Sicuro:**
- **Nessun privilegio di amministratore**: si tocca solo l'hive `HKCU`
  dell'utente e la propria cartella Startup. Nessun task di sistema, nessun
  servizio, nessun `RunLevel` elevato.
- *Verifica con read-back*: l'installer rilegge il registro e conferma che il
  valore punti davvero al launcher, prima di dichiarare successo.
- *Log tracciati*: `logs/autostart_install.log` (installazioni/rimozioni) e
  `logs/kiosk_supervisor.log` (rotante, 2 MB × 3).
- *Idempotente*: rieseguire l'installer non crea duplicati né danni.
- Nessuna credenziale coinvolta: la catena avvia solo script locali del progetto.

## 📥 Installazione (utente normale, NO admin)

1. Doppio clic su **`INSTALLA_AUTOSTART.bat`**.
2. Lo script verifica i prerequisiti, registra le due coperture, le rilegge
   per conferma e controlla lo stato dell'autologon di Windows.
3. Al termine propone l'avvio immediato con verifica funzionale
   (attende `http://127.0.0.1:3000/api/health` per max 60 s).

⚠️ **Nota importante — autologon di Windows**: senza admin non è possibile
attivare l'accesso automatico di Windows. Se il PC si ferma sulla schermata di
login dopo uno spegnimento, l'autostart scatterà solo al momento dell'accesso.
Per il ripristino *completamente* automatico attivare l'accesso automatico
**una volta sola** (operazione di sistema, richiede admin, NON fa parte
dell'installer): `netplwiz` → utente kiosk → deselezionare "Gli utenti devono
inserire un nome utente e una password". L'installer controlla e avvisa se
l'autologon non risulta attivo.

## 🧪 Verifiche dopo l'installazione

- Riavviare il PC (o disconnettere/riconnettere l'utente): la pagina kiosk deve
  ricomparire da sola entro ~1 minuto dal desktop.
- Chiudere il browser con Alt+F4: la finestra kiosk deve riaprirsi entro ~30 s.
- Terminare il processo Python del server: deve ripartire entro ~15 s
  (vedi `logs/kiosk_supervisor.log`).

## 🧹 Rimozione

Doppio clic su **`RIMUOVI_AUTOSTART.bat`** (no admin): rimuove valore di
registro, file Startup e vecchio task `KioskHR_Watchdog` se presente; su
conferma arresta anche supervisore/server e, a richiesta, il browser.

## 🔧 Comandi utili

```bat
:: Stato supervisor (log in tempo reale)
type logs\kiosk_supervisor.log

:: Avvio manuale dell'intera catena (nascosto)
wscript.exe //B //nologo AVVIO_KIOSK.vbs

:: Verifica server
powershell -Command "Invoke-WebRequest http://127.0.0.1:3000/api/health -UseBasicParsing"

:: Valore autostart registrato
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v KioskHR_Autostart
```

## 🗳️ Migrazione dal vecchio sistema (task admin)

Il vecchio `KioskHR_Watchdog` (Task Scheduler, admin, solo server senza browser)
non serve più: l'installer tenta di rimuoverlo automaticamente; se il PC non ha
admin disponibili il tentativo fallisce senza conseguenze (il single-instance
lock impedisce comunque doppie partite del server). Per la pulizia completa:
`schtasks /delete /tn KioskHR_Watchdog /f` una volta come admin.

## ✅ Test eseguiti (16.10.2026, PC di sviluppo)

- `py_compile kiosk_supervisor.py`: OK.
- Lock single-instance: seconda istanza correttamente bloccata.
- Ricerca browser: Chrome trovato con argomenti kiosk corretti.
- `health_ok()` senza server: `False` senza eccezioni.
- `browser_window_alive()`: funziona (rileva la finestra corrente).
- Launcher statico `AVVIO_KIOSK.vbs`: percorso felice → comando corretto e
  quotato; percorso senza supervisore → uscita silenziosa (safety check).
- VBS generato dall'installer: sintassi valida, comando corretto.
- `reg add`/`reg query` dell'installer: round-trip aggiunto→verificato→rimosso OK.
