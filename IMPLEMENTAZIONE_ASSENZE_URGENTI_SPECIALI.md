# 🚨 IMPLEMENTAZIONE ASSENZE URGENTI E MOTIVI SPECIALI (v2.4.0 - 16.10.2026)

## 📋 REGOLE IMPLEMENTATE

### 1) Assenze urgenti — `Invoire urgenta (recuperabila)` (IDRequestType **18**)

- Per legge il dipendente ha diritto a **10 giorni/anno**.
- I giorni devono essere **recuperati**:
  - **nel mese** in cui viene richiesta l'assenza (`UrgentRecoveryPeriod = 'MONTH'`
    → scadenza = fine mese della data di inizio), oppure
  - **entro l'anno lavorativo** (`UrgentRecoveryPeriod = 'YEAR'`
    → scadenza = 31.12 dell'anno della data di inizio).
- **La scelta è un parametro della tabella SQL**: `AbsenceRequestes.UrgentRecoveryPeriod`
  (`MONTH` / `YEAR`), con la scadenza calcolata memorizzata in
  `AbsenceRequestes.UrgentRecoveryDeadline`.
- Nessun preavviso minimo (DayNoZone = 0): possono partire dallo stesso giorno.

### 2) Motivi speciali — `Motive speciale (deces, casatorie)` (IDRequestType **19**)

- **Massimo 5 giorni/anno** per dipendente (decesso, matrimonio, naștere, altro).
- Devono essere giustificati da **documentazione da presentare fisicamente al
  dep. HR entro 5 giorni dalla richiesta** (parametro `AbsenceRules.DocsDeadlineDays = 5`,
  scadenza salvata in `AbsenceRequestes.DocumentationDeadline` = data inizio + 5).
- **Pena**: annullamento della richiesta e **conversione in giorni di congedo ordinario**
  (`AbsenceRules.ConvertToIDRequestType = 1` → *Concediu odihna*).

## 🗄️ MODIFICHE DATABASE (già applicate in produzione)

Script idempotente: **`sql/MIGRAZIONE_ASSENZE_URGENTI_SPECIALI.sql`**
(eseguito 16.10.2026, 9/9 batch OK, tramite `temp/apply_migration.py`).

### `[Timeclocking].[dbo].[RequestType]`
| ID | RequestName | Abbreviation | EntireDay |
|----|-------------|--------------|-----------|
| 18 | Invoire urgenta (recuperabila) | IU | 1 |
| 19 | Motive speciale (deces, casatorie) | MS | 1 |

### `[Employee].[dbo].[AbsenceRules]` (nuove colonne + righe)
| IDRequestType | DayNoZone | MaxDaysPerYear | DocsDeadlineDays | ConvertToIDRequestType |
|----|----|----|----|----|
| 18 | 0 | 10 | NULL | NULL |
| 19 | 0 | 5 | 5 | 1 |

Nuove colonne: `MaxDaysPerYear` (smallint), `DocsDeadlineDays` (tinyint),
`ConvertToIDRequestType` (tinyint).

### `[Employee].[dbo].[AbsenceRequestes]` (nuove colonne)
| Colonna | Tipo | Significato |
|----|----|----|
| UrgentRecoveryPeriod | varchar(10) NULL | scelta dipendente: `MONTH` / `YEAR` |
| UrgentRecoveryDeadline | date NULL | scadenza recupero calcolata |
| SpecialReason | nvarchar(200) NULL | motivo speciale dichiarato |
| DocumentationDeadline | date NULL | scadenza presentazione documenti (inizio + 5 gg) |
| DocumentationReceived | bit NULL | documenti consegnati all'HR |
| DocumentationReceivedDate | datetime NULL | data consegna documenti |
| ConvertedToOrdinary | bit NOT NULL DEFAULT 0 | annullata e convertita in congedo ordinario |
| ConvertedToOrdinaryDate | datetime NULL | data conversione |
| ConvertedAbsenceRequestId | int NULL | id della richiesta di congedo ordinario creata |

### `[Employees]` (nuovo DB del programma in gestione dipendenti)
- `app.LeaveTypes`: nuove colonne `RequiresDocumentation`, `DocsDeadlineDays`,
  `ConvertToLeaveTypeId`, `IsRecoverable`; nuovi tipi:
  - **AU** — Assenze urgenti (recuperabili), max 10 gg, IsRecoverable = 1
  - **MS** — Motivi speciali, max 5 gg, RequiresDocumentation = 1, DocsDeadlineDays = 5, ConvertToLeaveTypeId = 1
- `app.LeaveRequests`: stesse colonne di tracciatura di `AbsenceRequestes`
  (UrgentRecoveryPeriod, UrgentRecoveryDeadline, Documentation*,
  ConvertedToOrdinary*, ConvertedLeaveRequestId).

## 🖥️ MODIFICHE AL KIOSK

| File | Modifica |
|----|----|
| `absence_request.py` | Costanti `URGENT_ABSENCE_TYPE_ID=18` / `SPECIAL_ABSENCE_TYPE_ID=19`; `get_request_types()` con regole quota; metodi `get_quota_info`, `get_absence_days_used`, `check_quota_availability`, `compute_urgent_recovery_deadline`, `get_docs_deadline_days`, `get_request_type_name`, `mark_special_documentation_received`, `convert_expired_special_absences`; `save_absence_request` esteso; PDF conferma esteso; lista richieste manager estesa |
| `app.py` | `/api/submit-absence-request` accetta `urgentRecoveryPeriod` e `specialReason`, valida quota 10/5 e blocca il superamento; nuovi endpoint `POST /api/absence-quota` e `POST /api/hr/special-docs-sweep` (token manager); sweep all'avvio; **email al superiore con tipo di congedo sempre in evidenza** (anche nel subject) |
| `templates/request.html` | Selettore "Perioada de recuperare" (urgenza), selettore "Motiv special" + dettaglio + avviso documentazione obbligatoria, card quota residua; fix artefatto PowerShell sull'include script |
| `static/js/request.js` | Visibilità condizionale dei nuovi campi, caricamento quota residua, blocco submit se quota superata, validazioni, campi nel body della POST, promemoria scadenze dopo l'invio |
| `service_kiosk_reports.py` | Job giornaliero **06:30**: `check_and_convert_special_absences()` → conversione automatica + email HR |

## ⏰ CONVERSIONE AUTOMATICA (documento mancante)

Tre livelli di sicurezza:
1. **Avvio app** (`app.py` `__main__`): sweep best-effort.
2. **Servizio report** (`service_kiosk_reports.py`): ogni giorno alle 06:30.
3. **Endpoint manuale** `POST /api/hr/special-docs-sweep` con token manager
   (per forzare il controllo, es. dopo la consegna/scadenza documenti).

La conversione: annulla la richiesta speciale (`Rejected=1` + `RefuseMotive` esplicativo,
`ConvertedToOrdinary=1`) e crea una **nuova richiesta di Concediu odihna** per lo stesso
periodo/dipendente (con entry Registro propria), collegata tramite
`ConvertedAbsenceRequestId`. Email di riepilogo ai destinatari HR.

## 📰 NEWS DI ANNUNCIO

- `Employee.dbo.News` **NewId 783**: visibile dal 16.10.2026 al **03.01.2027 23:59**.
- `Employees.app.News` **NewsId 656**: stesso contenuto (PublishUntil 03.01.2027,
  ShowOnKiosk = 1, Lang = ro).

## 🧪 TEST ESEGUITI (16.10.2026)

- `py_compile` su `app.py`, `absence_request.py`, `service_kiosk_reports.py`: OK
- `node --check static/js/request.js`: OK
- Smoke test DB (`temp/smoke_test.py`): tipi 18/19 con regole corrette, deadline
  recupero corrette (fine mese / 31.12), quota 10/5 con residui iniziali pieni,
  sweep conversione = 0 (nessuna richiesta speciale esistente), tutto OK.

## 🔄 NOTE OPERATIVE PER HR

- Registrazione consegna documenti (motivi speciali):
  `AbsenceRequestManager.mark_special_documentation_received(absence_request_id)`
  oppure UPDATE diretto su `AbsenceRequestes.DocumentationReceived = 1`.
- Modifica dei limiti di legge (es. 10 → 12 giorni urgenti): basta aggiornare
  `AbsenceRules.MaxDaysPerYear` / `DocsDeadlineDays` — nessuna modifica al codice.
