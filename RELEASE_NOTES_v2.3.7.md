# Release Notes - Kiosk HR v2.3.7

**Data:** 2026-07-20

---

## 🆕 Novità

### ⌨️ Timeout adattivo per inserimento badge manuale

Il sistema ora distingue automaticamente tra scansione RFID e digitazione manuale del codice badge:

- **Lettore RFID** (burst veloce, <150ms tra caratteri) → attesa **500ms** prima di validare (invariata)
- **Digitazione manuale** (>150ms tra caratteri) → attesa **2000ms** prima di validare

Prima dell'aggiornamento, il timeout di 500ms era identico per entrambe le modalità, rendendo quasi impossibile digitare manualmente un codice badge senza che il sistema validasse un numero incompleto.

### 💾 Badge persistente durante la sessione

Dopo aver scansionato o digitato il badge, le informazioni del dipendente vengono ora mantenute per tutta la durata della sessione browser (`sessionStorage`):

- **Prima:** selezionando un certificato o cliccando "Generează altă adeverință", il badge veniva perso e il sistema richiedeva una nuova scansione.
- **Adesso:** il badge rimane memorizzato. Il dipendente può generare più adeverințe consecutive senza dover scansionare nuovamente il badge.

**Comportamento dei pulsanti:**
| Pulsante | Comportamento |
|---|---|
| **Generează altă adeverință** | Mantiene il badge, resetta solo il form (motivo) |
| **Resetează** | Cancella il badge e torna alla pagina principale |
| **Timeout inattività (30s)** | Torna alla home → badge cancellato automaticamente |

---

## 🔧 Modifiche tecniche

- `static/js/app.js`:
  - Aggiunto tracciamento `state.lastKeyTime` per rilevare digitazione manuale vs scansione RFID
  - Nuove costanti di configurazione: `badgeReadDelayRFID`, `badgeReadDelayManual`, `manualTypingThreshold`
  - Nuove funzioni: `saveBadgeToSession()`, `clearBadgeSession()`, `restoreBadgeFromSession()`
  - `resetToKioskMode(clearBadge)` parametrizzato: `false` = reset parziale (mantiene badge), `true` = reset completo (cancella badge + redirect home)
  - Pulsante "Resetează" → reset completo; "Generează altă adeverință" → reset parziale

- `templates/launcher.html`:
  - Aggiunto script inline che cancella `sessionStorage` badge al caricamento della home page, garantendo isolamento tra sessioni di utenti diversi

---

## 📁 File modificati

- `static/js/app.js`
- `templates/launcher.html`
