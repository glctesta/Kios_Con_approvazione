# Release Notes - v2.3.4

**Data:** 2026-04-08

## Novità

### Tastierino numerico per inserimento manuale del badge

È stato aggiunto un tastierino numerico on-screen nella form di richiesta
assenza (`templates/request.html`). Il tastierino viene mostrato automaticamente
quando il campo del codice badge riceve il focus e permette all'utente di
inserire manualmente il numero del badge (utile quando lo scanner RFID non è
disponibile o non funziona).

**Comportamento:**
- Tasti 0-9, tasto **C** (Clear) e tasto **⌫** (Backspace).
- Il tastierino si nasconde automaticamente dopo una lettura badge valida.
- Viene ripristinato al reset della form.

### Tempo di attesa inserimento badge differenziato

Il delay prima di avviare la validazione del badge ora è differenziato a
seconda della modalità di input:

- **Scanner RFID** → `badgeReadDelay = 500 ms` (lettura rapida, invariato).
- **Tastierino manuale** → `badgeReadDelayKeypad = 2500 ms` (tempo più lungo
  per permettere di completare l'inserimento di tutte le cifre prima che
  parta la ricerca).

La modalità tastierino si attiva al primo click su un tasto del tastierino
(`state.keypadMode = true`) e si resetta al reset della form. Gli scanner RFID
mantengono quindi i tempi di risposta originali.

## File modificati

- `templates/request.html` — aggiunto markup tastierino
- `static/css/styles.css` — stile tastierino numerico
- `static/js/request.js` — logica tastierino e delay differenziato
- `CREA_PACCHETTO.ps1` — bump versione 2.3.4
