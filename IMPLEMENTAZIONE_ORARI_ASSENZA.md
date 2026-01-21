# 🕐 IMPLEMENTAZIONE ORARI ASSENZA PARZIALE

## 📋 REQUISITI

Per richieste con `IsConsideredEntireDay = 0`, aggiungere campi orari:
- **Dalle Ore**: formato HH:MM (07:30 - 22:30)
- **Fino alle Ore**: formato HH:MM (07:30 - 22:30)
- **Data Fine** = Data Inizio (stesso giorno)
- Salvare in `[Employee].[dbo].[AbsenceRequestes]` campi `FromTime` e `ToTime`

---

## ✅ MODIFICHE GIÀ COMPLETATE

### 1. Backend `absence_request.py`

#### Funzione `save_absence_request` ✅
```python
def save_absence_request(self, registro_id, hire_history_id, request_type_id, 
                        date_start, date_end, from_time=None, to_time=None,
                        username="Unknown", request_type_name="Richiesta Assenza"):
```

**Modifiche**:
- ✅ Aggiunti parametri `from_time` e `to_time`
- ✅ Query INSERT aggiornata con campi `FromTime` e `ToTime`
- ✅ Logging aggiornato per includere orari

**Query SQL**:
```sql
INSERT INTO [Employee].[dbo].[AbsenceRequestes]
    ([RegistroId], [EmployrrHireHistoryId], [IDRequestType], 
     [DateStart], [DateEnd], [FromTime], [ToTime],  -- ← AGGIUNTO
     [Approved], [ApprovedBy], [DateSys])
VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL, GETDATE())
```

---

## ⏳ MODIFICHE DA COMPLETARE

### 2. Template HTML `templates/request.html`

#### A. Aggiungere campi orari nel form

**Posizione**: Dopo i campi Data Inizio e DataFine

```html
<!-- ESISTENTE -->
<div class="form-group">
    <label for="dateStart">Data Inizio:</label>
    <input type="date" id="dateStart" name="dateStart" required>
</div>

<!-- NUOVO: Campi orari condizionali -->
<div class="form-group" id="timeFieldsGroup" style="display: none;">
    <label for="fromTime">Dalle Ore:</label>
    <input type="time" id="fromTime" name="fromTime" 
           min="07:30" max="22:30" step="900">
           <!-- step=900 = incrementi di 15 minuti -->
    
    <label for="toTime">Fino alle Ore:</label>
    <input type="time" id="toTime" name="toTime" 
           min="07:30" max="22:30" step="900">
</div>

<div class="form-group">
    <label for="dateEnd">Data Fine:</label>
    <input type="date" id="dateEnd" name="dateEnd" required>
</div>
```

#### B. JavaScript per gestire visibilità e logica

```javascript
// Dati tipi richiesta con IsConsideredEntireDay
let requestTypes = []; // Popolato da API

// Al caricamento pagina
fetch('/api/request-types')
    .then(res => res.json())
    .then(data => {
        requestTypes = data.request_types;
        populateRequestTypeSelect();
    });

// Quando cambia tipo richiesta
document.getElementById('requestType').addEventListener('change', function() {
    const selectedId = parseInt(this.value);
    const selectedType = requestTypes.find(t => t.id === selectedId);
    
    const timeFields = document.getElementById('timeFieldsGroup');
    const dateEnd = document.getElementById('dateEnd');
    const dateStart = document.getElementById('dateStart');
    
    if (selectedType && !selectedType.entire_day) {
        // Is Considered Entire Day = 0 → Mostra campi orari
        timeFields.style.display = 'block';
        
        // Rendi required i campi orari
        document.getElementById('fromTime').required = true;
        document.getElementById('toTime').required = true;
        
        // Data fine = data inizio (stesso giorno)
        dateEnd.value = dateStart.value;
        dateEnd.readOnly = true;
        
        // Listener per sincronizzare date
        dateStart.addEventListener('input', () => {
            dateEnd.value = dateStart.value;
        });
        
    } else {
        // Giornata intera → Nascondi campi orari
        timeFields.style.display = 'none';
        document.getElementById('fromTime').required = false;
        document.getElementById('toTime').required = false;
        dateEnd.readOnly = false;
    }
});

// Validazione range orario
document.getElementById('toTime').addEventListener('change', function() {
    const fromTime = document.getElementById('fromTime').value;
    const toTime = this.value;
    
    if (fromTime && toTime && toTime <= fromTime) {
        alert('L\'orario di fine deve essere dopo l\'orario di inizio!');
        this.value = '';
    }
});
```

---

### 3. Endpoint Flask API

#### A. Nuovo Endpoint: GET `/api/request-types`

**File**: `app.py`

```python
@app.route('/api/request-types', methods=['GET'])
def get_request_types():
    """Recupera tipi richiesta con info IsConsideredEntireDay"""
    try:
        from absence_request import AbsenceRequestManager
        
        conn = DatabaseConnection(config_manager).connect()
        if notconn:
            return jsonify({'success': False, 'error': 'DB error'}), 500
        
        manager = AbsenceRequestManager(conn)
        request_types = manager.get_request_types()
        
        return jsonify({
            'success': True,
            'request_types': request_types
        })
        
    except Exception as e:
        logger.error(f"Errore recupero tipi richiesta: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

#### B. Endpoint Submit: POST `/api/submit-absence-request`

```python
@app.route('/api/submit-absence-request', methods=['POST'])
def submit_absence_request():
    """Salva richiesta assenza con supporto orari"""
    try:
        data = request.json
        
        # Dati richiesta
        badge_number = data.get('badgeNumber')
        request_type_id = data.get('requestTypeId')
        date_start = datetime.strptime(data.get('dateStart'), '%Y-%m-%d').date()
        date_end = datetime.strptime(data.get('dateEnd'), '%Y-%m-%d').date()
        
        # Orari opzionali (solo se IsConsideredEntireDay = 0)
        from_time = data.get('fromTime')  # Formato: "HH:MM"
        to_time = data.get('toTime')
        
        from absence_request import AbsenceRequestManager
        
        conn = DatabaseConnection(config_manager).connect()
        manager = AbsenceRequestManager(conn)
        
        # 1. Recupera info dipendente
        employee_info = manager.get_available_vacation_days(badge_number, datetime.now().year)
        
        if not employee_info:
            return jsonify({'success': False, 'error': 'Badge non trovato'}), 404
        
        # 2. Validazione regole data (DayNoZone)
        validation = manager.validate_absence_date_rule(request_type_id, date_start)
        if not validation['valid']:
            return jsonify({'success': False, 'error': validation['message']}), 400
        
        # 3. Check duplicati
        is_duplicate = manager.check_duplicate_request(
            employee_info['hire_history_id'],
            request_type_id,
            date_start,
            date_end
        )
        
        if is_duplicate:
            return jsonify({'success': False, 'error': 'Richiesta già esistente'}), 409
        
        # 4. Crea entry registro
        registro_id = manager.create_registry_entry(
            year=datetime.now().year,
            request_date=datetime.now(),
            issued_by=badge_number
        )
        
        if not registro_id:
            return jsonify({'success': False, 'error': 'Errore creazione registro'}), 500
        
        # 5. Salva richiesta CON ORARI
        absence_request_id = manager.save_absence_request(
            registro_id=registro_id,
            hire_history_id=employee_info['hire_history_id'],
            request_type_id=request_type_id,
            date_start=date_start,
            date_end=date_end,
            from_time=from_time,   # ← NUOVO
            to_time=to_time,        # ← NUOVO
            username=badge_number,
            request_type_name=data.get('requestTypeName', 'Assenza')
        )
        
        if not absence_request_id:
            return jsonify({'success': False, 'error': 'Errore salvataggio'}), 500
        
        # 6. Genera PDF conferma
        registry_info = manager.get_registry_info(registro_id)
        
        # Prepara dati per PDF
        request_data = {
            'type_name': data.get('requestTypeName'),
            'date_start': date_start,
            'date_end': date_end,
            'from_time': from_time,   # ← NUOVO per PDF
            'to_time': to_time,        # ← NUOVO per PDF
            'working_days': manager.calculate_working_days(
                date_start, date_end, 
                manager.get_holidays(datetime.now().year)
            ) if not from_time else None  # Solo per giornate intere
        }
        
        employee_data = {
            'name': employee_info['employee_name'],
            'surname': employee_info['employee_surname'],
            'badge': badge_number
        }
        
        pdf_path = manager.generate_confirmation_pdf(
            employee_data,
            request_data,
            registry_info
        )
        
        return jsonify({
            'success': True,
            'request_id': absence_request_id,
            'registro_id': registro_id,
            'pdf_path': pdf_path
        })
        
    except Exception as e:
        logger.error(f"Errore submit richiesta: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

### 4. Aggiornamento PDF Conferma

**File**: `absence_request.py` → `generate_confirmation_pdf()`

**Linea ~690-694**: Modificare per includere orari

```python
y -= 20
c.drawString(50, y, f"Perioada: {request_data['date_start'].strftime('%d.%m.%Y')} - {request_data['date_end'].strftime('%d.%m.%Y')}")

# NUOVO: Mostra orari se presenti
if request_data.get('from_time') and request_data.get('to_time'):
    y -= 20
    c.setFont(self.font_bold, 10)
    c.drawString(50, y, f"Orario: Dalle ore {request_data['from_time']} - Fino alle ore {request_data['to_time']}")

y -= 20
# Solo per giornate intere
if request_data.get('working_days') is not None:
    c.drawString(50, y, f"Zile lucrătoare: {request_data['working_days']}")
```

---

## 🧪 TESTING

### Test Case 1: Assenza Parziale (Permesso Ore)
- Tipo: Permesso (ID = 10, IsConsideredEntireDay = 0)
- Data Inizio: 22/01/2026
- Data Fine: 22/01/2026 (uguale)
- Dalle Ore: 09:00
- Fino alle Ore: 12:00

**Risultato atteso**:
```sql
SELECT * FROM [Employee].[dbo].[AbsenceRequestes]
WHERE AbsenceRequestId = [ultimo_id]

-- Campi:
-- DateStart = 2026-01-22
-- DateEnd = 2026-01-22
-- FromTime = '09:00'
-- ToTime = '12:00'
```

### Test Case 2: Assenza Giornata Intera (Ferie)
- Tipo: Ferie (ID = 1, IsConsideredEntireDay = 1)
- Data Inizio: 23/01/2026
- Data Fine: 25/01/2026
- Orari: NON visualizzati

**Risultato atteso**:
```sql
-- FromTime = NULL
-- ToTime = NULL
```

---

## 📝 CHECKLIST IMPLEMENTAZIONE

### Backend ✅
- [x] `absence_request.py::save_absence_request()` - Parametri from_time/to_time
- [x] Query INSERT con FromTime/ToTime
- [x] Logging orari

### Frontend ⏳
- [ ] `templates/request.html` - Campi input time
- [ ] JavaScript visibilità condizionale
- [ ] Validazione range orario (toTime > fromTime)
- [ ] Sincronizzazione date per assenze parziali

### API ⏳
- [ ] GET `/api/request-types` - Recupera tipi con IsConsideredEntireDay
- [ ] POST `/api/submit-absence-request` - Submit con orari
- [ ] PDF conferma con orari

### Database ✅
- [x] Campi `FromTime` e `ToTime` già esistenti nella tabella

---

## 🔧 FILE DA MODIFICARE

1. ✅ `absence_request.py` - Backend logic (COMPLETATO)
2. ⏳ `app.py` - Endpoints Flask API
3. ⏳ `templates/request.html` - UI form
4. ⏳ `absence_request.py::generate_confirmation_pdf()` - PDF con orari

---

**Status**: Backend completato al 70%. Frontend e API da implementare.

**Priority**: Alta - Funzionalità richiesta dall'utilizzatore per gestione permessi orari.
