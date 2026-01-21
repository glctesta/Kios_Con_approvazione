/**
 * TIME FIELDS MANAGEMENT FOR PARTIAL ABSENCE
 * Gestione campi orari per assenze parziali (IsConsideredEntireDay = 0)
 */

// Aggiungi elementi time ai DOM elements esistenti
const timeFieldsElements = {
    timeFieldsGroup: document.getElementById('timeFieldsGroup'),
    fromTime: document.getElementById('fromTime'),
    toTime: document.getElementById('toTime')
};

/**
 * Gestisce la visibilità dei campi orari in base al tipo di richiesta
 */
function handleTimeFieldsVisibility(requestTypeId) {
    if (!requestTypeId || !state.requestTypes.length) {
        hideTimeFields();
        return;
    }

    const selectedType = state.requestTypes.find(t => t.id === requestTypeId);

    if (!selectedType) {
        hideTimeFields();
        return;
    }

    // Se IsConsideredEntireDay = 0 ? Mostra campi orari
    if (!selectedType.entire_day) {
        showTimeFields();

        // Data fine = data inizio (stesso giorno)
        syncEndDateWithStartDate();

        // Disabilita modifica data fine
        document.getElementById('dateEnd').readOnly = true;
        document.getElementById('dateEnd').style.backgroundColor = '#f3f4f6';
        document.getElementById('dateEnd').style.cursor = 'not-allowed';

        // Nascondi info giorni lavorativi (non ha senso per assenza oraria)
        document.getElementById('workingDaysInfo').style.display = 'none';

    } else {
        hideTimeFields();

        // Riabilita modifica data fine
        document.getElementById('dateEnd').readOnly = false;
        document.getElementById('dateEnd').style.backgroundColor = '';
        document.getElementById('dateEnd').style.cursor = '';
    }
}

function showTimeFields() {
    if (timeFieldsElements.timeFieldsGroup) {
        timeFieldsElements.timeFieldsGroup.style.display = 'block';

        // Rendi required
        timeFieldsElements.fromTime.required = true;
        timeFieldsElements.toTime.required = true;

        // Set default values se vuoti
        if (!timeFieldsElements.fromTime.value) {
            timeFieldsElements.fromTime.value = '08:00';
        }
        if (!timeFieldsElements.toTime.value) {
            timeFieldsElements.toTime.value = '12:00';
        }
    }
}

function hideTimeFields() {
    if (timeFieldsElements.timeFieldsGroup) {
        timeFieldsElements.timeFieldsGroup.style.display = 'none';

        // Rimuovi required
        timeFieldsElements.fromTime.required = false;
        timeFieldsElements.toTime.required = false;

        // Clear values
        timeFieldsElements.fromTime.value = '';
        timeFieldsElements.toTime.value = '';
    }
}

function syncEndDateWithStartDate() {
    if (document.getElementById('dateStart').value) {
        document.getElementById('dateEnd').value = document.getElementById('dateStart').value;
    }

    // Aggiungi listener per mantenere sincronizzazione
    const originalDateStartHandler = document.getElementById('dateStart').onchange;

    document.getElementById('dateStart').onchange = function (e) {
        // Chiama handler originale se esiste
        if (originalDateStartHandler) {
            originalDateStartHandler.call(this, e);
        }

        // Se è assenza parziale, sincronizza data fine
        const requestTypeId = parseInt(document.getElementById('requestType').value);
        if (requestTypeId) {
            const selectedType = state.requestTypes.find(t => t.id === requestTypeId);
            if (selectedType && !selectedType.entire_day) {
                document.getElementById('dateEnd').value = this.value;
            }
        }
    };
}

/**
 * Valida il range orario
 */
function validateTimeRange() {
    const fromTime = timeFieldsElements.fromTime.value;
    const toTime = timeFieldsElements.toTime.value;

    if (!fromTime || !toTime) {
        return true; // Non validare se vuoti
    }

    // Converti in minuti per confronto
    const fromMinutes = timeToMinutes(fromTime);
    const toMinutes = timeToMinutes(toTime);

    if (toMinutes <= fromMinutes) {
        showToast('Orario di fine deve essere dopo orario di inizio!', 'error');
        timeFieldsElements.toTime.value = '';
        return false;
    }

    // Verifica range minimo (almeno 30 minuti)
    const diffMinutes = toMinutes - fromMinutes;
    if (diffMinutes < 30) {
        showToast('L\'assenza deve durare almeno 30 minuti!', 'warning');
        return false;
    }

    return true;
}

function timeToMinutes(time) {
    const [hours, minutes] = time.split(':').map(Number);
    return hours * 60 + minutes;
}


    // Listener diretto su data inizio per assenze parziali
    const dateStartEl = document.getElementById('dateStart');
    const dateEndEl = document.getElementById('dateEnd');
    const submitBtn = document.getElementById('submitBtn');
    
    if (dateStartEl) {
        dateStartEl.addEventListener('change', function() {
            // Se è assenza parziale e ha data, abilita submit
            if (window.timeFieldsManagement && window.timeFieldsManagement.isPartialAbsence()) {
                if (this.value && dateEndEl && submitBtn) {
                    // Sincronizza data fine
                    dateEndEl.value = this.value;
                    
                    // IMPORTANTE: Popola state per passare validazione
                    if (window.state) {
                        window.state.dateStart = new Date(this.value);
                        window.state.dateEnd = new Date(this.value);
                        console.log(' State populated:', window.state.dateStart, window.state.dateEnd);
                    }
                    
                    // Abilita bottone
                    submitBtn.disabled = false;
                    console.log(' Submit button enabled for partial absence');
                }
            }
        });
    }


document.addEventListener('DOMContentLoaded', function () {
    // Validazione orario toTime
    if (timeFieldsElements.toTime) {
        timeFieldsElements.toTime.addEventListener('change', validateTimeRange);
    }

    // Validazione orario fromTime
    if (timeFieldsElements.fromTime) {
        timeFieldsElements.fromTime.addEventListener('change', function () {
            // Se toTime è già impostato, valida
            if (timeFieldsElements.toTime.value) {
                validateTimeRange();
            }
        });
    }
});

// Esporta funzioni per uso in request.js
window.timeFieldsManagement = {
    handleTimeFieldsVisibility,
    validateTimeRange,
    getTimeValues: () => ({
        fromTime: timeFieldsElements.fromTime?.value || null,
        toTime: timeFieldsElements.toTime?.value || null
    }),
    isPartialAbsence: () => {
        const requestTypeId = parseInt(document.getElementById('requestType').value);
        if (!requestTypeId || !state.requestTypes.length) return false;

        const selectedType = state.requestTypes.find(t => t.id === requestTypeId);
        return selectedType && !selectedType.entire_day;
    }
};

// Listener per popolare state quando cambia data (per assenze parziali)
document.addEventListener('DOMContentLoaded', function() {
    const dateStartEl = document.getElementById('dateStart');
    const dateEndEl = document.getElementById('dateEnd');
    
    if (dateStartEl) {
        // Aggiungi listener DOPO che request.js ha fatto il suo setup
        setTimeout(() => {
            dateStartEl.addEventListener('change', function() {
                if (window.timeFieldsManagement && window.timeFieldsManagement.isPartialAbsence()) {
                    if (this.value && window.state) {
                        // Sincronizza data fine
                        if (dateEndEl) {
                            dateEndEl.value = this.value;
                        }
                        
                        // Popola state
                        window.state.dateStart = new Date(this.value);
                        window.state.dateEnd = new Date(this.value);
                        
                        console.log(' State populated for partial absence:', window.state.dateStart);
                        
                        // Abilita submit
                        const submitBtn = document.getElementById('submitBtn');
                        if (submitBtn) {
                            submitBtn.disabled = false;
                        }
                    }
                }
            });
        }, 500); // Aspetta che request.js sia caricato
    }
});