/**
 * ABSENCE REQUEST - FRONTEND APPLICATION
 * Gestione cerere absență (richieste assenza)
 */

// ========================================
// STATE MANAGEMENT
// ========================================
const state = {
    selectedEmployee: null,
    requestTypes: [],
    selectedRequestType: null,
    availableDays: 0,
    dateStart: null,
    dateEnd: null,
    workingDays: 0,
    currentPdfPath: null,
    badgeReadTimeout: null,
    autoResetTimeout: null,
    isProcessing: false
};

// Rendi state globale per time-fields.js
window.state = state;

// ========================================
// CONFIGURATION
// ========================================
const config = {
    badgeReadDelay: 500,
    autoResetDelay: 30000,
    vacationRequestTypeId: 1  // IDRequestType per ferie
};

// ========================================
// DOM ELEMENTS
// ========================================
const elements = {
    badgeInput: document.getElementById('badgeInput'),
    badgeStatus: document.getElementById('badgeStatus'),
    employeeInfo: document.getElementById('employeeInfo'),
    employeeName: document.getElementById('employeeName'),
    availableDaysInfo: document.getElementById('availableDaysInfo'),
    availableDays: document.getElementById('availableDays'),
    requestType: document.getElementById('requestType'),
    dateStart: document.getElementById('dateStart'),
    dateEnd: document.getElementById('dateEnd'),
    workingDaysInfo: document.getElementById('workingDaysInfo'),
    workingDays: document.getElementById('workingDays'),
    workingDaysHelper: document.getElementById('workingDaysHelper'),
    submitBtn: document.getElementById('submitBtn'),
    resetBtn: document.getElementById('resetBtn'),
    requestForm: document.getElementById('requestForm'),
    resultSection: document.getElementById('resultSection'),
    resultRequestNumber: document.getElementById('resultRequestNumber'),
    resultEmployee: document.getElementById('resultEmployee'),
    resultType: document.getElementById('resultType'),
    resultPeriod: document.getElementById('resultPeriod'),
    resultDays: document.getElementById('resultDays'),
    printBtn: document.getElementById('printBtn'),
    newRequestBtn: document.getElementById('newRequestBtn'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer')
};

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', function () {
    loadRequestTypes();
    attachEventListeners();
    setMinDate();
    elements.badgeInput.focus();
});

async function loadRequestTypes() {
    try {
        const response = await fetch('/api/request-types');
        const data = await response.json();

        if (data.success) {
            state.requestTypes = data.request_types;
            populateRequestTypes();
        } else {
            showToast('Errore caricamento tipi richiesta', 'error');
        }
    } catch (error) {
        console.error('Errore caricamento tipi richiesta:', error);
        showToast('Errore di connessione', 'error');
    }
}

function populateRequestTypes() {
    elements.requestType.innerHTML = '<option value="">Selectați...</option>';

    state.requestTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = type.name;
        elements.requestType.appendChild(option);
    });
}

function setMinDate(dayNoZone) {
    // Imposta data minima basata su DayNoZone (0 = oggi, 1 = domani, ecc.)
    if (dayNoZone === undefined || dayNoZone === null) {
        dayNoZone = 1; // default: domani
    }
    const minDateObj = new Date();
    minDateObj.setDate(minDateObj.getDate() + dayNoZone);
    // Usa formato locale YYYY-MM-DD per evitare problemi timezone con toISOString()
    const year = minDateObj.getFullYear();
    const month = String(minDateObj.getMonth() + 1).padStart(2, '0');
    const day = String(minDateObj.getDate()).padStart(2, '0');
    const minDate = `${year}-${month}-${day}`;

    elements.dateStart.min = minDate;
    elements.dateEnd.min = minDate;

    // Se le date già selezionate sono prima del nuovo minimo, resettale
    if (elements.dateStart.value && elements.dateStart.value < minDate) {
        elements.dateStart.value = '';
        state.dateStart = null;
    }
    if (elements.dateEnd.value && elements.dateEnd.value < minDate) {
        elements.dateEnd.value = '';
        state.dateEnd = null;
    }
}

// ========================================
// EVENT LISTENERS
// ========================================
function attachEventListeners() {
    // Badge input
    elements.badgeInput.addEventListener('input', handleBadgeInput);

    // Request type change
    elements.requestType.addEventListener('change', handleRequestTypeChange);

    // Date changes
    elements.dateStart.addEventListener('change', handleDateChange);
    elements.dateEnd.addEventListener('change', handleDateChange);

    // Form submit
    elements.requestForm.addEventListener('submit', handleFormSubmit);

    // Reset button
    elements.resetBtn.addEventListener('click', resetForm);

    // Print button
    elements.printBtn.addEventListener('click', handlePrint);

    // New request button
    elements.newRequestBtn.addEventListener('click', resetToKioskMode);
}

// ========================================
// BADGE HANDLING
// ========================================
function handleBadgeInput(e) {
    clearTimeout(state.badgeReadTimeout);

    const badgeNumber = e.target.value.trim();

    if (badgeNumber.length === 0) {
        updateBadgeStatus('waiting');
        elements.employeeInfo.style.display = 'none';
        state.selectedEmployee = null;
        disableForm();
        return;
    }

    updateBadgeStatus('reading');

    state.badgeReadTimeout = setTimeout(() => {
        validateBadge(badgeNumber);
    }, config.badgeReadDelay);
}

async function validateBadge(badgeNumber) {
    try {
        updateBadgeStatus('reading');

        const response = await fetch('/api/validate-badge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ badgeNumber })
        });

        const data = await response.json();

        if (data.success) {
            state.selectedEmployee = data.employee;
            updateBadgeStatus('success');
            showEmployeeInfo(data.employee);
            enableForm();
            showToast(`Bun venit, ${data.employee.name}!`, 'success');

            // Carica giorni disponibili per anno corrente
            await loadAvailableDays(badgeNumber);
        } else {
            updateBadgeStatus('error');
            elements.employeeInfo.style.display = 'none';
            state.selectedEmployee = null;
            disableForm();
            showToast(data.error || 'Badge invalid', 'error');

            setTimeout(() => {
                resetBadgeInput();
            }, 2000);
        }
    } catch (error) {
        console.error('Errore validazione badge:', error);
        updateBadgeStatus('error');
        showToast('Errore di connessione', 'error');
    }
}

async function loadAvailableDays(badgeNumber) {
    try {
        const currentYear = new Date().getFullYear();

        const response = await fetch('/api/available-vacation-days', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                badgeNumber: badgeNumber,
                year: currentYear
            })
        });

        const data = await response.json();

        if (data.success) {
            state.availableDays = data.available_days;
            // Non mostrare subito, solo quando si seleziona tipo ferie
        } else {
            console.warn('Impossibile caricare giorni disponibili');
        }
    } catch (error) {
        console.error('Errore caricamento giorni disponibili:', error);
    }
}

function showEmployeeInfo(employee) {
    elements.employeeName.textContent = employee.name;
    elements.employeeInfo.style.display = 'block';
}

function updateBadgeStatus(status) {
    const statusIcon = elements.badgeStatus.querySelector('.status-icon');
    const statusText = elements.badgeStatus.querySelector('.status-text');

    elements.badgeStatus.className = 'badge-status ' + status;

    switch (status) {
        case 'waiting':
            statusIcon.textContent = '\uD83D\uDCF1';
            statusText.textContent = '\u00CEn a\u0219teptare...';
            break;
        case 'reading':
            statusIcon.textContent = '\uD83D\uDD04';
            statusText.textContent = 'Citire...';
            break;
        case 'success':
            statusIcon.textContent = '\u2705';
            statusText.textContent = 'Valid';
            break;
        case 'error':
            statusIcon.textContent = '\u274C';
            statusText.textContent = 'Invalid';
            break;
    }
}

// ========================================
// FORM HANDLING
// ========================================
function enableForm() {
    elements.requestType.disabled = false;
    elements.dateStart.disabled = false;
    elements.dateEnd.disabled = false;
}

function disableForm() {
    elements.requestType.disabled = true;
    elements.dateStart.disabled = true;
    elements.dateEnd.disabled = true;
    elements.submitBtn.disabled = true;
}

function handleRequestTypeChange(e) {
    const requestTypeId = parseInt(e.target.value);

    if (!requestTypeId) {
        state.selectedRequestType = null;
        elements.availableDaysInfo.style.display = 'none';
        return;
    }

    state.selectedRequestType = requestTypeId;

    // Aggiorna data minima in base a DayNoZone del tipo selezionato
    const selectedType = state.requestTypes.find(t => t.id === requestTypeId);
    if (selectedType) {
        // Resetta le date quando cambia il tipo di richiesta
        // in modo che il calendario rifletta il nuovo minimo
        elements.dateStart.value = '';
        elements.dateEnd.value = '';
        state.dateStart = null;
        state.dateEnd = null;
        state.workingDays = 0;
        elements.workingDaysInfo.style.display = 'none';
        elements.submitBtn.disabled = true;

        setMinDate(selectedType.day_no_zone);
    }

    // Mostra giorni disponibili solo per ferie (IDRequestType = 1)
    if (requestTypeId === config.vacationRequestTypeId) {
        elements.availableDays.textContent = state.availableDays;
        elements.availableDaysInfo.style.display = 'block';

        if (state.availableDays <= 0) {
            showToast('Nu ave\u021bi zile de concediu disponibile!', 'warning');
        }
    } else {
        elements.availableDaysInfo.style.display = 'none';
    }

    // Gestisci visibilit\u00e0 campi orari
    if (window.timeFieldsManagement) {
        window.timeFieldsManagement.handleTimeFieldsVisibility(requestTypeId);
    }

    // Ricalcola giorni lavorativi se date gi\u00e0 selezionate
    if (state.dateStart && state.dateEnd) {
        calculateWorkingDays();
    }
}

async function handleDateChange() {
    const startDate = elements.dateStart.value;
    const endDate = elements.dateEnd.value;

    if (!startDate || !endDate) {
        elements.workingDaysInfo.style.display = 'none';
        elements.submitBtn.disabled = true;
        return;
    }

    // Verifica che data fine >= data inizio
    if (new Date(endDate) < new Date(startDate)) {
        showToast('Data sf\u00e2r\u0219it trebuie s\u0103 fie dup\u0103 data \u00eenceput', 'warning');
        elements.dateEnd.value = '';
        elements.workingDaysInfo.style.display = 'none';
        elements.submitBtn.disabled = true;
        return;
    }

    state.dateStart = new Date(startDate);
    state.dateEnd = new Date(endDate);

    await calculateWorkingDays();
}

async function calculateWorkingDays() {
    // Salta calcolo per assenze parziali
    if (window.timeFieldsManagement && window.timeFieldsManagement.isPartialAbsence()) {
        elements.workingDaysInfo.style.display = 'none';
        elements.submitBtn.disabled = false;
        return;
    }

    if (!state.dateStart || !state.dateEnd || !state.selectedRequestType) {
        return;
    }

    try {
        showLoading('Calcul zile lucr\u0103toare...');

        const response = await fetch('/api/calculate-working-days', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dateStart: state.dateStart.toISOString().split('T')[0],
                dateEnd: state.dateEnd.toISOString().split('T')[0],
                requestTypeId: state.selectedRequestType
            })
        });

        const data = await response.json();

        hideLoading();

        if (data.success) {
            state.workingDays = data.working_days;
            elements.workingDays.textContent = data.working_days;

            // Mostra info giorni lavorativi
            elements.workingDaysInfo.style.display = 'block';

            // Verifica disponibilit\u00e0 per ferie
            if (state.selectedRequestType === config.vacationRequestTypeId) {
                if (state.workingDays > state.availableDays) {
                    elements.workingDaysHelper.textContent =
                        `\u26A0\uFE0F Ave\u021bi doar ${state.availableDays} zile disponibile!`;
                    elements.workingDaysHelper.style.color = '#ef4444';
                    elements.submitBtn.disabled = true;
                    showToast(`Zile solicitate (${state.workingDays}) > Zile disponibile (${state.availableDays})`, 'error');
                } else {
                    elements.workingDaysHelper.textContent =
                        `\u2713 Zile disponibile dup\u0103 cerere: ${state.availableDays - state.workingDays}`;
                    elements.workingDaysHelper.style.color = '#10b981';
                    elements.submitBtn.disabled = false;
                }
            } else {
                elements.workingDaysHelper.textContent = '';
                elements.submitBtn.disabled = false;
            }
        } else {
            showToast(data.error || 'Errore calcolo giorni', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Errore calcolo giorni lavorativi:', error);
        showToast('Errore di connessione', 'error');
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();

    if (state.isProcessing) return;

    // SKIP COMPLETO VALIDAZIONI PER ASSENZE PARZIALI
    if (window.timeFieldsManagement && window.timeFieldsManagement.isPartialAbsence()) {
        // Validazioni minime per assenze orarie
        if (!state.selectedEmployee) {
            showToast('Scana\u021bi badge-ul', 'warning');
            return;
        }
        if (!state.selectedRequestType) {
            showToast('Selecta\u021bi tipul de absen\u021b\u0103', 'warning');
            return;
        }
        
        // Valida orari
        const {fromTime, toTime} = window.timeFieldsManagement.getTimeValues();
        if (!fromTime || !toTime) {
            showToast('Inserire orario inizio e fine', 'warning');
            return;
        }
        if (!window.timeFieldsManagement.validateTimeRange()) {
            return;
        }
        
        // Se state \u00e8 popolato, vai direttamente a submit
        if (window.state && window.state.dateStart && window.state.dateEnd) {
            console.log(' Assenza parziale validata - submit diretto');
            await submitRequest();
            return;
        }
    }

    // Validazioni finali
    if (!state.selectedEmployee) {
        showToast('Scana\u021bi badge-ul', 'warning');
        return;
    }

    if (!state.selectedRequestType) {
        showToast('Selecta\u021bi tipul de absen\u021b\u0103', 'warning');
        return;
    }

    if (!state.dateStart || !state.dateEnd) {
        showToast('Selecta\u021bi perioada', 'warning');
        return;
    }

    if (state.workingDays <= 0) {
        showToast('Perioada selectat\u0103 nu con\u021bine zile lucr\u0103toare', 'warning');
        return;
    }

    // Verifica giorni disponibili per ferie
    if (state.selectedRequestType === config.vacationRequestTypeId) {
        if (state.workingDays > state.availableDays) {
            showToast('Nu ave\u021bi suficiente zile de concediu disponibile', 'error');
            return;
        }
    }

    await submitRequest();
}

async function submitRequest() {
    try {
        state.isProcessing = true;
        showLoading('Se trimite cererea...');

        const response = await fetch('/api/submit-absence-request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                badgeNumber: elements.badgeInput.value.trim(),
                requestTypeId: state.selectedRequestType,
                dateStart: state.dateStart.toISOString().split('T')[0],
                dateEnd: state.dateEnd.toISOString().split('T')[0],
                fromTime: window.timeFieldsManagement?.getTimeValues().fromTime || null,
                toTime: window.timeFieldsManagement?.getTimeValues().toTime || null
            })
        });

        const data = await response.json();

        hideLoading();

        if (data.success) {
            state.currentPdfPath = data.pdf_path;
            showResult(data);
            showToast('Cerere \u00eenregistrat\u0103 cu succes!', 'success');

            // Auto-print
            if (data.print_success) {
                showToast(`Trimis la imprimant\u0103: ${data.printer_name}`, 'success');
            }

            // Auto-reset
            startAutoReset();
        } else {
            showToast(data.error || 'Errore invio richiesta', 'error');
            state.isProcessing = false;
        }

    } catch (error) {
        hideLoading();
        console.error('Errore invio richiesta:', error);
        showToast('Errore di connessione', 'error');
        state.isProcessing = false;
    }
}

function showResult(data) {
    const requestTypeName = state.requestTypes.find(t => t.id === state.selectedRequestType)?.name || '';

    elements.resultRequestNumber.textContent = data.request_number;
    elements.resultEmployee.textContent = state.selectedEmployee.name;
    elements.resultType.textContent = requestTypeName;
    elements.resultPeriod.textContent =
        `${state.dateStart.toLocaleDateString('ro-RO')} - ${state.dateEnd.toLocaleDateString('ro-RO')}`;
    elements.resultDays.textContent = state.workingDays;

    elements.requestForm.style.display = 'none';
    elements.resultSection.style.display = 'block';
}

// ========================================
// PRINT HANDLING
// ========================================
async function handlePrint() {
    if (!state.currentPdfPath) {
        showToast('Nessun PDF da stampare', 'error');
        return;
    }

    try {
        const response = await fetch('/api/do-print', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pdf_path: state.currentPdfPath
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Trimis la imprimant\u0103: ${data.printer_name}`, 'success');
        } else {
            showToast('Errore stampa', 'error');
        }

    } catch (error) {
        console.error('Errore stampa:', error);
        showToast('Errore di connessione', 'error');
    }
}

// ========================================
// RESET FUNCTIONS
// ========================================
function resetForm() {
    elements.badgeInput.value = '';
    elements.requestType.value = '';
    elements.dateStart.value = '';
    elements.dateEnd.value = '';
    elements.employeeInfo.style.display = 'none';
    elements.availableDaysInfo.style.display = 'none';
    elements.workingDaysInfo.style.display = 'none';

    state.selectedEmployee = null;
    state.selectedRequestType = null;
    state.availableDays = 0;
    state.dateStart = null;
    state.dateEnd = null;
    state.workingDays = 0;
    state.currentPdfPath = null;

    updateBadgeStatus('waiting');
    disableForm();

    elements.badgeInput.focus();
}

function resetBadgeInput() {
    elements.badgeInput.value = '';
    elements.badgeInput.disabled = false;
    elements.badgeInput.focus();
    updateBadgeStatus('waiting');
}

function startAutoReset() {
    if (state.autoResetTimeout) {
        clearTimeout(state.autoResetTimeout);
    }

    state.autoResetTimeout = setTimeout(() => {
        showToast('Revenire automat\u0103 la ecranul ini\u021bial...', 'warning');
        setTimeout(() => {
            resetToKioskMode();
        }, 3000);
    }, config.autoResetDelay);
}

function resetToKioskMode() {
    if (state.autoResetTimeout) {
        clearTimeout(state.autoResetTimeout);
        state.autoResetTimeout = null;
    }

    // Redirect alla home launcher
    window.location.href = '/';
}

// ========================================
// UI HELPERS
// ========================================
function showLoading(message = '\u00CEnc\u0103rcare...') {
    elements.loadingOverlay.querySelector('.loading-text').textContent = message;
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = document.createElement('span');
    icon.className = 'toast-icon';
    icon.textContent = type === 'success' ? '\u2705' : type === 'error' ? '\u274C' : type === 'warning' ? '\u26A0\uFE0F' : '\u2139\uFE0F';

    const messageSpan = document.createElement('span');
    messageSpan.className = 'toast-message';
    messageSpan.textContent = message;

    // Per messaggi lunghi, permetti al testo di andare su pi\u00f9 righe
    if (message.length > 100) {
        messageSpan.style.whiteSpace = 'pre-wrap';
        messageSpan.style.maxWidth = '500px';
        messageSpan.style.lineHeight = '1.5';
        toast.style.maxWidth = '600px';
    }

    toast.appendChild(icon);
    toast.appendChild(messageSpan);

    elements.toastContainer.appendChild(toast);

    // Timeout pi\u00f9 lungo per messaggi di errore lunghi
    let timeout = 4000; // 4 secondi di default
    if (type === 'error' && message.length > 100) {
        timeout = 10000; // 10 secondi per errori lunghi
    }

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, timeout);
}
