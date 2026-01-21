# 📦 KIOSK HR v2.3.3 - PACCHETTO DEPLOY COMPLETO

**Data**: 21 Gennaio 2026  
**Versione**: 2.3.3  
**Build**: Complete Deploy Package

---

## 🎁 CONTENUTO PACCHETTO

Questo ZIP contiene **TUTTI** i file necessari per il deploy completo del sistema Kiosk HR con le ultime feature:

### Backend Python
- `app.py` ✅ Endpoint API completi + email con orari
- `absence_request.py` ✅ Gestione richieste + PDF con orari
- `pdf_printer.py` ✅ Stampa silenziosa SumatraPDF
- `badge_reader.py` ✅ Lettura badge RFID
- `utils.py` ✅ Utility comuni
- `config_manager.py` ✅ Gestione configurazione
- `database_connection.py` ✅ Connessione SQL Server

### Frontend
- `templates/*.html` ✅ Tutti i template (launcher, request, ecc.)
- `static/js/request.js` ✅ Logica richieste assenza
- `static/js/time-fields.js` ✅ **NUOVO** Gestione campi orari
- `static/js/inactivity-timeout.js` ✅ Timeout inattività
- `static/css/styles.css` ✅ Stili applicazione

### Assets & Config
- `static/*.png/svg/ico` ✅ Logo e icone
- `config.json` ✅ Configurazione app
- `requirements.txt` ✅ Dipendenze Python

### Documentazione
- `RELEASE_NOTES_v2.3.3.md` ✅ Note di rilascio
- `DEPLOY.md` ✅ Guida installazione
- `GUIDA_PDFTOPRINTER.md` ✅ Guida stampa
- Tutti gli altri `.md`

---

## 🚀 INSTALLAZIONE RAPIDA

### 1️⃣ BACKUP
```powershell
# Backup installazione corrente
Copy-Item -Path "C:\Kiosk_HR" -Destination "C:\Kiosk_HR_BACKUP_$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

### 2️⃣ ESTRAZIONE
```powershell
# Estrai in directory esistente (sovrascrive file vecchi)
Expand-Archive -Path "Kiosk_HR_Complete_Deploy_v2.3.3_*.zip" -DestinationPath "C:\Kiosk_HR" -Force
```

### 3️⃣ VERIFICA DIPENDENZE
```powershell
cd C:\Kiosk_HR
pip install -r requirements.txt
```

### 4️⃣ AVVIO
```powershell
python app.py
```

### 5️⃣ TEST
- Apri browser: http://localhost:5000
- Test richiesta assenza con permesso orario
- Verifica email con orari

---

## ✨ NOVITÀ v2.3.3

### 🕐 Campi Orari Assenza (100% Completo)
**Cosa fa**: Permette richieste di assenza con orari specifici (9:00-12:00, ecc.)

**Come funziona**:
1. Badge → Seleziona tipo permesso
2. **Campi "Dalle ore" / "Fino alle ore" appaiono automaticamente**
3. Compila date + orari
4. Submit → Salvato in DB con orari
5. Email manager include **"Orario: Dalle ore XX - Fino alle ore YY"**
6. PDF conferma mostra gli orari

**File modificati**:
- `templates/request.html` - Campi HTML
- `static/js/request.js` - Logica submitspaiono automaticament

e validazione
- `static/js/time-fields.js` - **NUOVO** Modulo orari
- `app.py` - Endpoint + email
- `absence_request.py` - PDF

### 🖨️ Stampa Silenziosa v2
- SumatraPDF come metodo primario
- Controllo `Printable = 1` per news
- Formattazione PDF migliorata

---

## 🔧 COSA È CAMBIATO

| File | Modificato | Descrizione |
|------|-----------|-------------|
| `app.py` | ✅ Sì | Endpoint /api/submit-absence-request con orari |
| `absence_request.py` | ✅ Sì | PDF con visualizzazione orari |
| `pdf_printer.py` | ✅ Sì | SumatraPDF integrato |
| `templates/request.html` | ✅ Sì | Campi HTML orari |
| `static/js/request.js` | ✅ Sì | Validazione e submit orari |
| `static/js/time-fields.js` | ✅ **NUOVO** | Modulo gestione orari |

---

## ⚙️ CONFIGURAZIONE

**Nessuna configurazione aggiuntiva necessaria!**

Il sistema usa i campi DB già esistenti:
- `AbsenceRequestes.FromTime` (time)
- `AbsenceRequestes.ToTime` (time)
- `RequestType.IsConsideredEntireDay` (bit)

---

## 🧪 TEST WORKFLOW

### Test Assenza Oraria
1. **Login**: Passa badge
2. **Tipo**: Seleziona "Permesso" o altro con `IsConsideredEntireDay = 0`
3. **Verifiche**:
   - ✅ Campi "Dalle ore" / "Fino alle ore" appaiono
   - ✅ Data fine = data inizio (sincronizzata)
   - ✅ Validazione min 30 minuti
4. **Submit**: Compila e invia
5. **Email**: Verifica che contenga "Orario: Dalle ore XX - Fino alle ore YY"

### Test Assenza Intera Giornata
1. **Login**: Passa badge
2. **Tipo**: Seleziona "Ferie" (`IsConsideredEntireDay = 1`)
3. **Verifiche**:
   - ✅ Campi orari NON appaiono
   - ✅ Funziona come prima
4. **Submit**: Normale

---

## 📞 TROUBLESHOOTING

### Campi orari non appaiono
**Soluzione**: Verifica che il tipo richiesta abbia `IsConsideredEntireDay = 0` nel DB

### Errore "Perioada selectată nu conține zile lucrătoare"
**Soluzione**: Refresh browser (Ctrl+F5) per caricare nuovo JavaScript

### Email non include orari
**Soluzione**: Verifica che `app.py` sia aggiornato (deve avere `from_time` e `to_time` nell'email template)

---

## 📋 CHECKLIST POST-INSTALLAZIONE

- [ ] Backup completato
- [ ] ZIP estratto in directory corretta
- [ ] `pip install -r requirements.txt` eseguito
- [ ] App avviata senza errori
- [ ] Test browser http://localhost:5000 OK
- [ ] Test richiesta con orari OK
- [ ] Email con orari ricevuta OK
- [ ] Stampa news funzionante OK

---

## 🎯 SUPPORTO

**Documentazione completa**: Vedi file `.md` inclusi
**Logs**: Controlla console Python per debug
**Database**: Nessuna migrazione necessaria

---

## ✅ PRODUCTION READY

**Questo pacchetto è completo e pronto per la produzione!**

Tutte le feature sono state testate e validate.  
Nessuna dipendenza mancante.  
Deploy testato su ambiente di sviluppo.

**Buon deploy! 🚀**

---

*Kiosk HR v2.3.3 - Vandewiele Italia*  
*© 2026 - Sistema HR Automatizzato*
