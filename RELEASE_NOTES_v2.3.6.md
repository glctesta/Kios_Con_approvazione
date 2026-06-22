# Release Notes - Kiosk HR v2.3.6

**Data rilascio:** 2026-04-20

## Obiettivo

Garantire che le email di notifica per le richieste di assenza (ferie, permessi, Bilet de voie, Invoire, ecc.) vengano inviate esattamente ai **superiori gerarchici** del dipendente appartenenti allo **stesso Main CdcId**, indipendentemente dal comportamento interno della stored procedure `Employee.dbo.GetManager` precedentemente utilizzata.

## Cambiamenti principali

### Sostituzione della SP `GetManager` con query inline esplicita

Prima del fix la funzione `get_manager_emails()` in `absence_request.py` invocava la stored procedure `[Employee].[dbo].[GetManager]` passando l'`EmployeeHireHistoryId` del dipendente richiedente. La logica interna della SP non era verificabile lato applicativo.

Ora la funzione esegue direttamente la query SQL canonica che individua i superiori gerarchici secondo i criteri:

- `EmployeeHireHistory.EndWorkDate IS NULL` e `employeerid = 2` (rapporto di lavoro attivo)
- `EmployeeCdcStories.DateOut IS NULL` (assegnazione CdC attiva)
- `Functions.FunctionCode > FunctionCode` del dipendente target (funzione superiore)
- `CostCenters.CdcId = MainCdcId` del dipendente target (stesso centro di costo principale)
- `EmployeeAddress.WorkEmail` non vuoto e `EmployeeAddress.DateOut IS NULL`

Questo garantisce che i destinatari delle email coincidano esattamente con quelli restituiti dalla query di riferimento concordata, senza dipendere dalla SP lato DB.

## File modificati

- `absence_request.py`
  - Riscritta `get_manager_emails()`: rimossa la chiamata a `EXEC [Employee].[dbo].[GetManager]` e a `EmployeeIdTableType`; inserita la query inline con `DECLARE @FunctionCode`, `@MainCdcId` e SELECT finale dei superiori.
  - Parsing semplificato: la query ritorna `(Employee, WorkEmail)`, quindi l'estrazione dell'email prende direttamente l'ultimo campo (niente più scan generico su tutti i campi della riga).
  - Gestione robusta dei result-set multipli conservata (avanza con `cursor.nextset()` fino al result-set con righe).
  - Log invariati nella forma, aggiornati nel contenuto (`[GET_MANAGER_EMAILS] Superiore: NOME -> email`).

- `CREA_PACCHETTO.ps1`
  - Bump versione 2.3.5 → 2.3.6.
  - Aggiunto `RELEASE_NOTES_v2.3.6.md` nell'elenco dei file di documentazione inclusi nel pacchetto.

## Comportamento invariato

- Il flusso chiamante in `app.py` (endpoint `/api/submit-absence-request`) non cambia: continua a chiamare `get_manager_emails(hire_history_id)` e a usare il fallback `gianluca.testa@vandewiele.com` se la lista è vuota.
- Il template HTML dell'email, l'oggetto, l'SMTP host e le credenziali restano invariati.
- La gestione degli errori resta graceful: se la query fallisce, l'invio email non blocca la richiesta.

## Test consigliati post-deploy

1. Inviare una richiesta di assenza per un dipendente noto con superiori gerarchici noti e verificare nei log `[GET_MANAGER_EMAILS] Email superiori gerarchici trovate (TOTALE N): [...]` che l'elenco coincida con l'output della query SQL eseguita manualmente su SSMS con lo stesso `EmployeeHireHistoryId`.
2. Verificare che le email arrivino effettivamente alle caselle dei superiori indicati.
3. Verificare che per un dipendente senza superiori gerarchici configurati scatti ancora il fallback sull'indirizzo di `gianluca.testa@vandewiele.com`.
