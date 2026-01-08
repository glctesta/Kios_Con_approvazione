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

function setMinDate() {
    // Imposta data minima a domani
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const minDate = tomorrow.toISOString().split('T')[0];

    elements.dateStart.min = minDate;
    elements.dateEnd.min = minDate;
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
            statusIcon.textContent = '📱';
            statusText.textContent = 'În așteptare...';
            break;
        case 'reading':
            statusIcon.textContent = '🔄';
            statusText.textContent = 'Citire...';
            break;
        case 'success':
            statusIcon.textContent = '✅';
            statusText.textContent = 'Valid';
            break;
        case 'error':
            statusIcon.textContent = '❌';
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

    // Mostra giorni disponibili solo per ferie (IDRequestType = 1)
    if (requestTypeId === config.vacationRequestTypeId) {
        elements.availableDays.textContent = state.availableDays;
        elements.availableDaysInfo.style.display = 'block';

        if (state.availableDays <= 0) {
            showToast('Nu aveți zile de concediu disponibile!', 'warning');
        }
    } else {
        elements.availableDaysInfo.style.display = 'none';
    }

    // Ricalcola giorni lavorativi se date già selezionate
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
        showToast('Data sfârșit trebuie să fie după data început', 'warning');
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
    if (!state.dateStart || !state.dateEnd || !state.selectedRequestType) {
        return;
    }

    try {
        showLoading('Calcul zile lucrătoare...');

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

            // Verifica disponibilità per ferie
            if (state.selectedRequestType === config.vacationRequestTypeId) {
                if (state.workingDays > state.availableDays) {
                    elements.workingDaysHelper.textContent =
                        `⚠️ Aveți doar ${state.availableDays} zile disponibile!`;
                    elements.workingDaysHelper.style.color = '#ef4444';
                    elements.submitBtn.disabled = true;
                    showToast(`Zile solicitate (${state.workingDays}) > Zile disponibile (${state.availableDays})`, 'error');
                } else {
                    elements.workingDaysHelper.textContent =
                        `✓ Zile disponibile după cerere: ${state.availableDays - state.workingDays}`;
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

    // Validazioni finali
    if (!state.selectedEmployee) {
        showToast('Scanați badge-ul', 'warning');
        return;
    }

    if (!state.selectedRequestType) {
        showToast('Selectați tipul de absență', 'warning');
        return;
    }

    if (!state.dateStart || !state.dateEnd) {
        showToast('Selectați perioada', 'warning');
        return;
    }

    if (state.workingDays <= 0) {
        showToast('Perioada selectată nu conține zile lucrătoare', 'warning');
        return;
    }

    // Verifica giorni disponibili per ferie
    if (state.selectedRequestType === config.vacationRequestTypeId) {
        if (state.workingDays > state.availableDays) {
            showToast('Nu aveți suficiente zile de concediu disponibile', 'error');
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
                dateEnd: state.dateEnd.toISOString().split('T')[0]
            })
        });

        const data = await response.json();

        hideLoading();

        if (data.success) {
            state.currentPdfPath = data.pdf_path;
            showResult(data);
            showToast('Cerere înregistrată cu succes!', 'success');

            // Auto-print
            if (data.print_success) {
                showToast(`Trimis la imprimantă: ${data.printer_name}`, 'success');
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
            showToast(`Trimis la imprimantă: ${data.printer_name}`, 'success');
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
        showToast('Revenire automată la ecranul inițial...', 'warning');
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
function showLoading(message = 'Încărcare...') {
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
    icon.textContent = type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️';

    const messageSpan = document.createElement('span');
    messageSpan.className = 'toast-message';
    messageSpan.textContent = message;

    // Per messaggi lunghi, permetti al testo di andare su più righe
    if (message.length > 100) {
        messageSpan.style.whiteSpace = 'pre-wrap';
        messageSpan.style.maxWidth = '500px';
        messageSpan.style.lineHeight = '1.5';
        toast.style.maxWidth = '600px';
    }

    toast.appendChild(icon);
    toast.appendChild(messageSpan);

    elements.toastContainer.appendChild(toast);

    // Timeout più lungo per messaggi di errore lunghi
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
