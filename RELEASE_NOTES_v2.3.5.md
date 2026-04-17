# Release Notes - Kiosk HR v2.3.5

**Data rilascio:** 2026-04-17

## Obiettivo

Risolvere il problema della stampa per gli utenti che accedono al server dai loro PC in rete locale: prima dell'aggiornamento, i documenti venivano stampati sempre sulla stampante predefinita del computer dove gira il server. Ora la stampa avviene sulla stampante del PC da cui l'utente ha effettuato la richiesta.

## Cambiamenti principali

### Stampa lato client con bottone di conferma e countdown 15s

**Comportamento nuovo, unificato kiosk + utenti remoti:**

1. L'utente fa la richiesta (certificato / cerere di assenza / raport istoric absențe).
2. Il server genera il PDF e lo salva in `temp/`, poi risponde al browser.
3. Nella pagina risultato compare il bottone **"Printează (15)"** con countdown decrescente.
4. **Click sul bottone** → stampa client-side via iframe nascosto:
   - **Sul kiosk** (Chrome lanciato con `--kiosk-printing`) → stampa silenziosa immediata sulla stampante predefinita del kiosk (comportamento come prima).
   - **Sui PC remoti in rete** → il browser mostra il dialog di stampa standard; l'utente conferma e il documento esce sulla stampante locale del suo PC.
5. **Se nessun click entro 15 secondi** → bottone sparisce e il PDF viene eliminato da `temp/` (privacy su dispositivi condivisi).
6. Auto-reset a 30 secondi come prima.

Il kiosk non cambia esperienza utente: un tap in più sul touchscreen, nessun popup di conferma grazie al flag `--kiosk-printing` già presente in `AVVIA_TUTTO.BAT`, `START_KIOSK_FULLSCREEN.bat`, `START_SISTEMA_KIOSK.bat`.

## File modificati

- `app.py`
  - Rimossa la stampa server-side (`get_default_printer` + `print_pdf_silent`) dai 3 endpoint principali: `/api/generate-certificate`, `/api/generate-absence-report`, `/api/submit-absence-request`.
  - Sostituito endpoint `/api/do-print` con `/api/delete-pdf/<filename>` per la pulizia dei PDF temporanei (con protezione path traversal).
- `static/js/app.js`, `static/js/request.js`, `static/js/absence.js`
  - Nuovo `startPrintCountdown()` che gestisce il countdown di 15 secondi sul bottone `#printBtn`.
  - Nuovo `handlePrint()` / `printCertificate()` che usa un iframe nascosto + `contentWindow.print()` per la stampa client-side.
  - Chiamata a `/api/delete-pdf` per eliminare il PDF dopo stampa o dopo il timeout.

## Cosa NON è stato toccato

- `/api/news/print` (stampa news cliccando sul frame news nel launcher): rimane server-side perché è una funzione kiosk-interna.
- `printer_keepalive.py`: invariato (serve a mantenere sveglia la stampante del kiosk).
- `pdf_printer.py`: invariato (ancora usato da `/api/news/print`).

## Test consigliati dopo deploy

- Sul kiosk: richiesta certificato → bottone "Printează (15, 14, 13...)" → tap → stampa silenziosa sulla stampante del kiosk.
- Sul kiosk: nessun tap per 15s → bottone sparisce → PDF eliminato da `temp/`.
- Da PC remoto in rete: richiesta → click bottone → dialog di stampa del browser con stampante locale selezionabile.
- Stesso test per le 3 funzioni: adeverință, cerere de absență, raport istoric absențe.
