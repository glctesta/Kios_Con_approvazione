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

    // Se IsConsideredEntireDay = 0 → Mostra campi orari
    if (!selectedType.entire_day) {
        showTimeFields();

        // Data fine = data inizio (stesso giorno)
        syncEndDateWithStartDate();

        // Disabilita modifica data fine
        elements.dateEnd.readOnly = true;
        elements.dateEnd.style.backgroundColor = '#f3f4f6';
        elements.dateEnd.style.cursor = 'not-allowed';

        // Nascondi info giorni lavorativi (non ha senso per assenza oraria)
        elements.workingDaysInfo.style.display = 'none';

    } else {
        hideTimeFields();

        // Riabilita modifica data fine
        elements.dateEnd.readOnly = false;
        elements.dateEnd.style.backgroundColor = '';
        elements.dateEnd.style.cursor = '';
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
    if (elements.dateStart.value) {
        elements.dateEnd.value = elements.dateStart.value;
    }

    // Aggiungi listener per mantenere sincronizzazione
    const originalDateStartHandler = elements.dateStart.onchange;

    elements.dateStart.onchange = function (e) {
        // Chiama handler originale se esiste
        if (originalDateStartHandler) {
            originalDateStartHandler.call(this, e);
        }

        // Se è assenza parziale, sincronizza data fine
        const requestTypeId = parseInt(elements.requestType.value);
        if (requestTypeId) {
            const selectedType = state.requestTypes.find(t => t.id === requestTypeId);
            if (selectedType && !selectedType.entire_day) {
                elements.dateEnd.value = this.value;
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

// Attach event listeners quando il DOM è pronto
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
        const requestTypeId = parseInt(elements.requestType.value);
        if (!requestTypeId || !state.requestTypes.length) return false;

        const selectedType = state.requestTypes.find(t => t.id === requestTypeId);
        return selectedType && !selectedType.entire_day;
    }
};
