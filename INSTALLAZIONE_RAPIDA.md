═══════════════════════════════════════════════════════════════════
  KIOSK HR v2.2.0 - GUIDA INSTALLAZIONE RAPIDA
═══════════════════════════════════════════════════════════════════

📦 PACCHETTO: Kiosk_HR_v2.2.0_20260103_130243.zip
📏 DIMENSIONE: 2.88 MB
📅 DATA: 03 Gennaio 2026

═══════════════════════════════════════════════════════════════════
⚡ INSTALLAZIONE IN 5 PASSI
═══════════════════════════════════════════════════════════════════

1️⃣ PREREQUISITI
   ✅ Python 3.11 installato
   ✅ Connessione SQL Server disponibile
   ✅ Server SMTP raggiungibile
   ✅ Microsoft Edge installato
   ✅ Permessi amministratore

2️⃣ ESTRAZIONE
   • Copia ZIP sulla macchina target
   • Estrai in C:\Kiosk_HR\
   
3️⃣ INSTALLAZIONE
   • Apri PowerShell come Amministratore
   • cd C:\Kiosk_HR
   • .\INSTALLA.bat
   
4️⃣ CONFIGURAZIONE
   • python setup.py
   • Inserisci:
     - Server DB: VANDEWIELESRV\TRACEABILITYRS
     - Database: Employee
     - SMTP: mail.vandewiele.com:587
     - Email mittente e password
     
5️⃣ AVVIO
   • START_APP.bat (modalità normale)
   • START_SISTEMA_KIOSK.bat (modalità fullscreen)
   • Apri browser: http://localhost:5000

═══════════════════════════════════════════════════════════════════
📋 COSA È INCLUSO
═══════════════════════════════════════════════════════════════════

✅ Applicazione completa (16 file Python)
✅ Templates HTML e CSS
✅ JavaScript frontend
✅ 57 immagini slideshow
✅ Font DejaVuSans
✅ Logo e GTMC.png
✅ DLL lettore RFID
✅ Script installazione e avvio
✅ Documentazione completa (11 guide)
✅ File configurazione template

═══════════════════════════════════════════════════════════════════
🎯 FUNZIONALITÀ v2.2.0
═══════════════════════════════════════════════════════════════════

✨ NOVITÀ v2.2.0:
   • Sistema News & Slideshow simultaneo (dual-frame)
   • Frame NEWS (50% schermo) - links esterni
   • Frame SLIDESHOW (50% schermo) - immagini
   • Configurazione flessibile

🔧 FUNZIONI ESISTENTI:
   • Richieste assenza con approvazione
   • Generazione certificati PDF
   • Firma digitale documenti
   • Stampa automatica
   • Lettore badge RFID
   • Verifica stato richieste
   • Reinvio notifiche email
   • Report annuale assenze
   • Multi-lingua IT/RO

═══════════════════════════════════════════════════════════════════
⚠️ NOTE IMPORTANTI
═══════════════════════════════════════════════════════════════════

⚠️ USARE PYTHON 3.11 (non versioni successive!)
⚠️ I file .enc e .key vanno rigenerati con setup.py
⚠️ Configurare News URL dopo l'installazione
⚠️ Verificare connessione database prima di iniziare

═══════════════════════════════════════════════════════════════════
🔧 CONFIGURAZIONE NEWS (POST-INSTALLAZIONE)
═══════════════════════════════════════════════════════════════════

Dopo setup.py, modifica configurazione:
1. Accedi tramite config_manager.py
2. Aggiungi sezione news_config:
   {
       "news_url": "https://example.com/news",
       "enable_dual_frame": true
   }

═══════════════════════════════════════════════════════════════════
🆘 TROUBLESHOOTING VELOCE
═══════════════════════════════════════════════════════════════════

❌ Python non trovato
   → Verifica installazione: python --version

❌ Dipendenze non installate
   → venv\Scripts\activate
   → pip install -r requirements.txt -v

❌ Database non raggiungibile
   → Testa connessione con SQL Management Studio
   → Verifica firewall Windows

❌ Email non inviate
   → Verifica server SMTP e credenziali
   → Controlla firewall porta 587

❌ Slideshow vuoto
   → Verifica directory Images/ con file X*.* o S*.*
   → Controlla permessi lettura

═══════════════════════════════════════════════════════════════════
📞 SUPPORTO
═══════════════════════════════════════════════════════════════════

Sviluppatore: Gianluca Testa
Email: gianluca.testa@vandewiele.com
Versione: 2.2.0

Per supporto fornire:
• Versione Windows
• Versione Python
• app_debug.log (ultime 100 righe)
• Screenshot errore

═══════════════════════════════════════════════════════════════════
✅ VERIFICA POST-INSTALLAZIONE
═══════════════════════════════════════════════════════════════════

□ Servizio Flask attivo (http://localhost:5000)
□ Pagina launcher si carica correttamente
□ Test generazione certificato OK
□ Test richiesta assenza OK
□ Email di test ricevuta
□ Slideshow funzionante (se configurato)
□ News frame funzionante (se configurato)
□ Stampa PDF funzionante (se configurata)
□ RFID funzionante (se presente)

═══════════════════════════════════════════════════════════════════

🎉 TUTTI I FILE NECESSARI SONO INCLUSI NEL PACCHETTO!
   Non manca nulla - installazione completa garantita!

═══════════════════════════════════════════════════════════════════
