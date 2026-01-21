# 🚀 GUIDA RAPIDA: Implementazione Campi Orari Assenza

## ✅ GIÀ COMPLETATO

1. **Backend API**: Endpoint `/api/request-types` creato ✅
2. **JavaScript Helper**: File `static/js/time-fields.js` creato ✅  
3. **Documentazione**: File `PATCH_REQUEST_JS_ORARI.txt` con modifiche da fare ✅

---

## 📝 PASSI MANUALI DA COMPLETARE

### 1. Mod ificare `templates/request.html`

**Posizione**: Tra le righe 86-88 (dopo Data Inizio, prima di Data Fine)

**Codice da inserire**:
```html
                </div>

                <!-- Campi Orari (visibili solo per assenze parziali) -->
                <div id="timeFieldsGroup" class="time-fields-group" style="display: none;">
                    <div class="form-group">
                        <label for="fromTime" class="form-label">
                            <span class="label-text">Dalle ore *</span>
                            <span class="label-helper">Orario inizio assenza</span>
                        </label>
                        <input type="time" id="fromTime" name="fromTime" class="form-input" 
                               min="07:30" max="22:30" step="900">
                    </div>

                    <div class="form-group">
                        <label for="toTime" class="form-label">
                            <span class="label-text">Fino alle ore *</span>
                            <span class="label-helper">Orario fine assenza</span>
                        </label>
                        <input type="time" id="toTime" name="toTime" class="form-input" 
                               min="07:30" max="22:30" step="900">
                    </div>
                </div>

                <!-- Data Fine -->
```

### 2. Aggiungere script in `templates/request.html`

**Posizione**: Prima della chiusura `</body>` (linea ~160)

**Codice da aggiungere PRIMA di `<script src="/static/js/request.js"></script>`**:
```html
    <script src="/static/js/time-fields.js"></script>
    <script src="/static/js/request.js"></script>
```

### 3. Modificare `static/js/request.js`

Applicare le 4 modifiche descritte in `PATCH_REQUEST_JS_ORARI.txt`:

#### Modifica 1: handleRequestTypeChange (linea ~298)
```javascript
    } else {
        elements.availableDaysInfo.style.display = 'none';
    }

    // NUOVO: Gestisci visibilità campi orari
    if (window.timeFieldsManagement) {
        window.timeFieldsManagement.handleTimeFieldsVisibility(requestTypeId);
    }

    // Ricalcola giorni lavorativi se date già selezionate
```

#### Modifica 2: submitRequest body JSON (linea ~437)
```javascript
            body: JSON.stringify({
                badgeNumber: elements.badgeInput.value.trim(),
                requestTypeId: state.selectedRequestType,
                dateStart: state.dateStart.toISOString().split('T')[0],
                dateEnd: state.dateEnd.toISOString().split('T')[0],
                // NUOVO: Aggiungi orari se assenza parziale
                ...(window.timeFieldsManagement?.isPartialAbsence() ? {
                    fromTime: window.timeFieldsManagement.getTimeValues().fromTime,
                    toTime: window.timeFieldsManagement.getTimeValues().toTime
                } : {})
            })
```

#### Modifica 3: handleFormSubmit validazione (linea ~422)
```javascript
        }
    }

    // NUOVO: Valida orari per assenze parziali
    if (window.timeFieldsManagement?.isPartialAbsence()) {
        if (!window.timeFieldsManagement.validateTimeRange()) {
            return;
        }
        
        const {fromTime, toTime} = window.timeFieldsManagement.getTimeValues();
        if (!fromTime || !toTime) {
            showToast('Inserire orario inizio e fine', 'warning');
            return;
        }
    }

    await submitRequest();
```

#### Modifica 4: calculateWorkingDays (linea ~331)
```javascript
async function calculateWorkingDays() {
    if (!state.dateStart || !state.dateEnd || !state.selectedRequestType) {
        return;
    }

    // NUOVO: Salta calcolo per assenze parziali
    if (window.timeFieldsManagement?.isPartialAbsence()) {
        elements.workingDaysInfo.style.display = 'none';
        elements.submitBtn.disabled = false;
        return;
    }
    
    try {
        // ... resto invariato
```

---

## 🧪 TEST

1. Riavvia app: `python app.py`
2. Apri http://localhost:5000/cerere
3. Scansiona badge
4. **Seleziona tipo con IsConsideredEntireDay = 0** (es: Permesso)
5. **Verifica**: Campi "Dalle ore" e "Fino alle ore" appaiono ✅
6. Compila e invia

---

## 🔍 LOG UTILI

```python
# app.py - endpoint API
2026-01-21 11:40:00 - INFO - Request types recuperati: [
    {'id': 1, 'name': 'Ferie', 'entire_day': True},
    {'id': 10, 'name': 'Permesso', 'entire_day': False}  ← Questo mostrerà campi orari
]

# Browser Console
Time fields visibility: true  ← Quando campi visibili
From: 08:00, To: 12:00  ← Valori or
ari
```

---

## ⚠️ TROUBLESHOOTING

### Campi orari non appaiono
1. Verifica console browser (F12): `window.timeFieldsManagement` deve esistere
2. Verifica che `time-fields.js` sia caricato PRIMA di `request.js`
3. Verifica che il tipo richiesta abbia `entire_day: false` nell'API response

### Errore submit
1. Verifica che `fromTime` e `toTime` siano nel JSON body  
2. Backend deve ricevere questi campi e salvarli in DB

---

## 📋 CHECKLIST FINALE

- [ ] File `time-fields.js` presente in `static/js/`
- [ ] File `request.html` modificato con campi orari HTML
- [ ] Script `time-fields.js` caricato in `request.html`
- [ ] File `request.js` modificato con 4 patch
- [ ] App riavviata
- [ ] Test con tipo IsConsideredEntireDay=0 funzionante

---

**Completando questi passi, i campi orari appariranno automaticamente! 🎉**
