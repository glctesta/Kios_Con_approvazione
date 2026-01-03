════════════════════════════════════════════════════════════════════════════════
  ISTRUZIONI IMMEDIATE PER IL COMPUTER TARGET
  Kiosk HR v2.2.0 - Pacchetto Finale con TUTTI i Fix
════════════════════════════════════════════════════════════════════════════════

📦 FILE DA USARE: Kiosk_HR_v2.2.0_20260103_131834.zip
⏰ TEMPO INSTALLAZIONE: 10-15 minuti

════════════════════════════════════════════════════════════════════════════════
⚡ INSTALLAZIONE RAPIDA (5 PASSI)
════════════════════════════════════════════════════════════════════════════════

PASSO 1: PREPARAZIONE
─────────────────────
□ Trasferisci il file ZIP sul computer target (USB, rete, ecc.)
□ Estrai il contenuto in: C:\Wandewiele\Kiosk\
□ Verifica di avere tutti i file estratti

PASSO 2: ESECUZIONE INSTALLA.BAT
──────────────────────────────────
□ Apri Esplora File
□ Vai in C:\Wandewiele\Kiosk\
□ Fai CLICK DESTRO su INSTALLA.bat
□ Seleziona "Esegui come amministratore"
□ ATTENDI il completamento (circa 5-10 minuti)

PASSO 3: CONFIGURAZIONE
────────────────────────
Quando INSTALLA.bat finisce, esegui:

□ Apri PowerShell o CMD nella directory C:\Wandewiele\Kiosk\
□ Attiva ambiente virtuale:
    venv\Scripts\activate.bat

□ Configura database e email:
    python setup.py

  Ti chiederà:
  - Server database: VANDEWIELESRV\TRACEABILITYRS
  - Nome database: Employee
  - Server SMTP: mail.vandewiele.com
  - Porta SMTP: 587
  - Email mittente: kiosk@vandewiele.com
  - Password email: [inserisci password]

PASSO 4: CONFIGURAZIONE NEWS (OPZIONALE)
──────────────────────────────────────────
Se vuoi attivare il sistema News & Slideshow:

□ Dopo setup.py, modifica la configurazione:
  - Gli URL verranno configurati nel database
  - Consulta GUIDA_NEWS_SLIDESHOW.md per dettagli

PASSO 5: AVVIO
───────────────
□ Avvia l'applicazione:
    START_APP.bat

□ Apri browser e vai a:
    http://localhost:5000

□ Se tutto funziona, per modalità kiosk fullscreen:
    START_SISTEMA_KIOSK.bat

════════════════════════════════════════════════════════════════════════════════
✅ VERIFICA INSTALLAZIONE CORRETTA
════════════════════════════════════════════════════════════════════════════════

Durante INSTALLA.bat, devi vedere:

[1/8] Verifica Python 3.11...
[OK] Python 3.11 trovato                                    ✓

[2/8] Creazione ambiente virtuale...
[OK] Ambiente virtuale creato                               ✓

[3/8] Attivazione ambiente virtuale...
[OK] Ambiente virtuale attivato                             ✓ FIX 1 OK

[4/8] Aggiornamento pip...
[OK] pip aggiornato                                         ✓

[5/8] Installazione dipendenze Python...
Downloading Pillow-10.4.0-cp311-cp311-win_amd64.whl        ✓ FIX 2 OK
[OK] Dipendenze installate                                  ✓

[6/8] Verifica file di configurazione...
[OK] Verifica configurazione completata                     ✓

[7/8] Creazione directory necessarie...
[OK] Directory create                                       ✓

[8/8] Verifica componenti aggiuntivi...
[OK] Verifica componenti completata                         ✓

========================================
  INSTALLAZIONE COMPLETATA!            ✅ TUTTO OK!
========================================

════════════════════════════════════════════════════════════════════════════════
❌ SE QUALCOSA VA STORTO
════════════════════════════════════════════════════════════════════════════════

ERRORE 1: "The system cannot find the path specified"
──────────────────────────────────────────────────────
✅ RISOLTO in questo pacchetto!
Se persiste, leggi: FIX_PROBLEMA_INSTALLAZIONE.md

ERRORE 2: "ERROR: Failed building wheel for Pillow"
────────────────────────────────────────────────────
✅ RISOLTO in questo pacchetto!
Se persiste, leggi: FIX_ERRORE_PILLOW.md

ERRORE 3: "Python non trovato"
────────────────────────────────
Installa Python 3.11 64-bit da:
https://www.python.org/downloads/
IMPORTANTE: Seleziona "Add Python to PATH" durante l'installazione

ERRORE 4: "Database non raggiungibile"
───────────────────────────────────────
Verifica:
□ Sei connesso alla rete aziendale
□ SQL Server è raggiungibile: ping VANDEWIELESRV
□ Firewall non blocca la connessione
□ Credenziali database corrette

ERRORE 5: "Email non inviate"
───────────────────────────────
Verifica:
□ Server SMTP raggiungibile: telnet mail.vandewiele.com 587
□ Credenziali email corrette
□ Firewall non blocca porta 587

════════════════════════════════════════════════════════════════════════════════
📋 CHECKLIST VELOCE
════════════════════════════════════════════════════════════════════════════════

PRIMA DI INIZIARE:
□ Python 3.11 64-bit installato sul computer target
□ File ZIP trasferito sul computer target
□ Permessi amministratore disponibili
□ Connessione al database SQL Server testata
□ Connessione al server SMTP verificata

DURANTE INSTALLAZIONE:
□ Estratto ZIP in C:\Wandewiele\Kiosk\
□ Eseguito INSTALLA.bat come amministratore
□ Tutti i passaggi [1/8] - [8/8] completati con [OK]
□ Nessun errore visualizzato

DOPO INSTALLAZIONE:
□ Eseguito python setup.py
□ Configurato database correttamente
□ Configurato email correttamente
□ Testato START_APP.bat
□ Applicazione accessibile su http://localhost:5000
□ Funzioni base testate (certificato, richiesta assenza)

════════════════════════════════════════════════════════════════════════════════
🎯 TEST FUNZIONALITÀ BASE
════════════════════════════════════════════════════════════════════════════════

Dopo l'avvio, testa:

TEST 1: Pagina Principale
□ Apri http://localhost:5000
□ Verifica che la pagina launcher si carichi
□ Verifica che i pulsanti siano visibili

TEST 2: Generazione Certificato
□ Clicca su "Certificat Vechime în Muncă"
□ Inserisci codice badge (es: 111111)
□ Verifica generazione PDF

TEST 3: Richiesta Assenza
□ Clicca su "Cerere de Absență"
□ Inserisci codice badge
□ Verifica form richiesta si carichi

TEST 4: Verifica Stato
□ Clicca su "Verificare Stare Cerere"
□ Inserisci numero richiesta (es: 1ARQ-2026)
□ Verifica visualizzazione stato

TEST 5: News & Slideshow (se configurato)
□ Verifica frame news si carichi
□ Verifica slideshow scorra immagini
□ Verifica transizioni funzionino

════════════════════════════════════════════════════════════════════════════════
📞 SUPPORTO
════════════════════════════════════════════════════════════════════════════════

Se hai bisogno di assistenza:

Email: gianluca.testa@vandewiele.com

Fornisci:
1. Output completo di INSTALLA.bat (screenshot o testo)
2. Versione Python (python --version)
3. Architettura (python -c "import platform; print(platform.machine())")
4. Descrizione errore
5. Screenshot errore (se applicabile)

════════════════════════════════════════════════════════════════════════════════
✨ QUESTO PACCHETTO INCLUDE
════════════════════════════════════════════════════════════════════════════════

✅ FIX 1: Errore directory ambiente virtuale
✅ FIX 2: Errore compilazione Pillow
✅ 16 file Python applicazione completa
✅ 5 template HTML (incluso News v2.2.0)
✅ 57 immagini slideshow
✅ Script installazione e avvio
✅ 15 guide documentazione
✅ Font, loghi, DLL RFID
✅ File configurazione

════════════════════════════════════════════════════════════════════════════════

🎉 TUTTO PRONTO PER L'INSTALLAZIONE!

Segui i 5 passi sopra e il sistema sarà operativo in 10-15 minuti.

════════════════════════════════════════════════════════════════════════════════
Vandewiele GTMC - Kiosk HR System v2.2.0
Ultimo aggiornamento: 03/01/2026 - 13:18
════════════════════════════════════════════════════════════════════════════════
