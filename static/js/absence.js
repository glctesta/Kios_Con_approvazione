/**
 * ABSENCE REPORT - FRONTEND APPLICATION
 * Gestione raport istoric absențe
 */

// ========================================
// STATE MANAGEMENT
// ========================================
const state = {
    selectedEmployee: null,
    selectedYear: null,
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
    showResultDuration: 10000
};

// ========================================
// DOM ELEMENTS
// ========================================
const elements = {
    badgeInput: document.getElementById('badgeInput'),
    badgeStatus: document.getElementById('badgeStatus'),
    employeeInfo: document.getElementById('employeeInfo'),
    employeeName: document.getElementById('employeeName'),
    yearSelect: document.getElementById('yearSelect'),
    generateBtn: document.getElementById('generateBtn'),
    resetBtn: document.getElementById('resetBtn'),
    absenceForm: document.getElementById('absenceForm'),
    resultSection: document.getElementById('resultSection'),
    resultEmployee: document.getElementById('resultEmployee'),
    resultYear: document.getElementById('resultYear'),
    resultDate: document.getElementById('resultDate'),
    printBtn: document.getElementById('printBtn'),
    newReportBtn: document.getElementById('newReportBtn'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer')
};

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', function () {
    initializeYearSelect();
    attachEventListeners();
    elements.badgeInput.focus();
});

function initializeYearSelect() {
    const currentYear = new Date().getFullYear();
    const years = [];

    // Ultimi 5 anni + anno corrente + prossimo anno
    for (let i = currentYear + 1; i >= currentYear - 5; i--) {
        years.push(i);
    }

    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (year === currentYear) {
            option.selected = true;
        }
        elements.yearSelect.appendChild(option);
    });

    state.selectedYear = currentYear;
}

// ========================================
// EVENT LISTENERS
// ========================================
function attachEventListeners() {
    // Badge input
    elements.badgeInput.addEventListener('input', handleBadgeInput);

    // Year select
    elements.yearSelect.addEventListener('change', function () {
        state.selectedYear = parseInt(this.value);
        validateForm();
    });

    // Form submit
    elements.absenceForm.addEventListener('submit', handleFormSubmit);

    // Reset button
    elements.resetBtn.addEventListener('click', resetForm);

    // Print button
    elements.printBtn.addEventListener('click', handlePrint);

    // New report button
    elements.newReportBtn.addEventListener('click', resetToKioskMode);
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
        validateForm();
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
            validateForm();
            showToast(`Bun venit, ${data.employee.name}!`, 'success');
        } else {
            updateBadgeStatus('error');
            elements.employeeInfo.style.display = 'none';
            state.selectedEmployee = null;
            validateForm();
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
function validateForm() {
    const isValid = state.selectedEmployee !== null && state.selectedYear !== null;
    elements.generateBtn.disabled = !isValid;
}

async function handleFormSubmit(e) {
    e.preventDefault();

    if (state.isProcessing) return;

    if (!state.selectedEmployee || !state.selectedYear) {
        showToast('Completați toate câmpurile', 'warning');
        return;
    }

    await generateReport();
}

async function generateReport() {
    try {
        state.isProcessing = true;
        showLoading('Se generează raportul...');

        const response = await fetch('/api/generate-absence-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                badgeNumber: elements.badgeInput.value.trim(),
                year: state.selectedYear
            })
        });

        const data = await response.json();

        hideLoading();

        if (data.success) {
            state.currentPdfPath = data.pdf_path;
            showResult(data);
            showToast('Raport generat cu succes!', 'success');

            // Auto-print
            if (data.print_success) {
                showToast(`Trimis la imprimantă: ${data.printer_name}`, 'success');
            }

            // Auto-reset
            startAutoReset();
        } else {
            showToast(data.error || 'Errore generazione raport', 'error');
            state.isProcessing = false;
        }

    } catch (error) {
        console.error('Errore generazione raport:', error);
        hideLoading();
        showToast('Errore di connessione', 'error');
        state.isProcessing = false;
    }
}

function showResult(data) {
    elements.resultEmployee.textContent = state.selectedEmployee.name;
    elements.resultYear.textContent = state.selectedYear;
    elements.resultDate.textContent = new Date().toLocaleDateString('ro-RO');

    elements.absenceForm.style.display = 'none';
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
    elements.yearSelect.value = new Date().getFullYear();
    elements.employeeInfo.style.display = 'none';

    state.selectedEmployee = null;
    state.selectedYear = new Date().getFullYear();
    state.currentPdfPath = null;

    updateBadgeStatus('waiting');
    validateForm();

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

    toast.appendChild(icon);
    toast.appendChild(messageSpan);

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
}
