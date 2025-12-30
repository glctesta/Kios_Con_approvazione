/**
 * CHECK REQUEST STATUS - FRONTEND APPLICATION
 * Verificare stare cerere absență
 */

// ========================================
// STATE MANAGEMENT
// ========================================
const state = {
    currentRequestNumber: null,
    autoResetTimeout: null
};

// ========================================
// CONFIGURATION
// ========================================
const config = {
    autoResetDelay: 30000
};

// ========================================
// DOM ELEMENTS
// ========================================
const elements = {
    requestNumber: document.getElementById('requestNumber'),
    checkBtn: document.getElementById('checkBtn'),
    resetBtn: document.getElementById('resetBtn'),
    checkForm: document.getElementById('checkForm'),
    resultSection: document.getElementById('resultSection'),
    resultCard: document.getElementById('resultCard'),
    resultIcon: document.getElementById('resultIcon'),
    resultTitle: document.getElementById('resultTitle'),
    resultRequestNumber: document.getElementById('resultRequestNumber'),
    resultRequestDate: document.getElementById('resultRequestDate'),
    resultRequestType: document.getElementById('resultRequestType'),
    resultPeriod: document.getElementById('resultPeriod'),
    resultDays: document.getElementById('resultDays'),
    resultStatus: document.getElementById('resultStatus'),
    resultApprover: document.getElementById('resultApprover'),
    resultApprovedBy: document.getElementById('resultApprovedBy'),
    resendBtn: document.getElementById('resendBtn'),
    newCheckBtn: document.getElementById('newCheckBtn'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer')
};

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', function () {
    attachEventListeners();
    elements.requestNumber.focus();
});

// ========================================
// EVENT LISTENERS
// ========================================
function attachEventListeners() {
    // Form submit
    elements.checkForm.addEventListener('submit', handleFormSubmit);

    // Reset button
    elements.resetBtn.addEventListener('click', resetForm);

    // New check button
    elements.newCheckBtn.addEventListener('click', resetForm);

    // Resend notification button
    elements.resendBtn.addEventListener('click', handleResendNotification);
}

// ========================================
// FORM HANDLING
// ========================================
async function handleFormSubmit(e) {
    e.preventDefault();

    const requestNumber = elements.requestNumber.value.trim();

    if (!requestNumber) {
        showToast('Introduceți numărul cererii', 'warning');
        return;
    }

    await checkRequestStatus(requestNumber);
}

async function checkRequestStatus(requestNumber) {
    try {
        showLoading('Se verifică cererea...');

        const response = await fetch('/api/check-request-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ requestNumber })
        });

        const data = await response.json();

        hideLoading();

        if (data.success) {
            state.currentRequestNumber = requestNumber;
            showResult(data.request);
            startAutoReset();
        } else {
            showToast(data.error || 'Cerere nu a fost găsită', 'error');
        }

    } catch (error) {
        hideLoading();
        console.error('Errore verifica stato:', error);
        showToast('Errore di connessione', 'error');
    }
}

// ========================================
// RESEND NOTIFICATION
// ========================================
async function handleResendNotification() {
    if (!state.currentRequestNumber) {
        showToast('Număr cerere lipsă', 'error');
        return;
    }

    try {
        showLoading('Se retrimite notificarea...');

        const response = await fetch('/api/resend-absence-notification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ requestNumber: state.currentRequestNumber })
        });

        const data = await response.json();

        hideLoading();

        if (data.success) {
            showToast('Notificare retrimisă cu succes!', 'success');
            // Disabilita temporaneamente il pulsante per evitare spam
            elements.resendBtn.disabled = true;
            elements.resendBtn.textContent = '✓ Trimis';
            setTimeout(() => {
                elements.resendBtn.disabled = false;
                elements.resendBtn.innerHTML = '<span class="btn-icon">📧</span> Retrimite Notificare';
            }, 10000); // Riabilita dopo 10 secondi
        } else {
            showToast(data.error || 'Eroare la retrimiterea notificării', 'error');
        }

    } catch (error) {
        hideLoading();
        console.error('Errore reinvio notifica:', error);
        showToast('Eroare de conexiune', 'error');
    }
}

function showResult(request) {
    // Popola dati
    elements.resultRequestNumber.textContent = request.request_number;
    elements.resultRequestDate.textContent = new Date(request.request_date).toLocaleDateString('ro-RO');
    elements.resultRequestType.textContent = request.request_type;
    elements.resultPeriod.textContent =
        `${new Date(request.date_start).toLocaleDateString('ro-RO')} - ${new Date(request.date_end).toLocaleDateString('ro-RO')}`;
    elements.resultDays.textContent = request.working_days || '-';

    // Usa lo stato calcolato dal backend
    const status = request.status || 'unknown';

    // Nascondi il pulsante di reinvio per default
    elements.resendBtn.style.display = 'none';

    switch (status) {
        case 'approved':
            // APPROVATA
            elements.resultIcon.textContent = '✅';
            elements.resultTitle.textContent = 'Cerere Aprobată';
            elements.resultStatus.textContent = '✅ ' + request.status_text;
            elements.resultStatus.style.color = '#10b981';
            elements.resultCard.style.borderColor = '#10b981';

            if (request.approved_by) {
                elements.resultApprovedBy.textContent = request.approved_by;
                elements.resultApprover.style.display = 'block';
            } else {
                elements.resultApprover.style.display = 'none';
            }
            break;

        case 'rejected':
            // RESPINTA
            elements.resultIcon.textContent = '❌';
            elements.resultTitle.textContent = 'Cerere Respinsă';
            elements.resultStatus.textContent = '❌ ' + request.status_text;
            elements.resultStatus.style.color = '#ef4444';
            elements.resultCard.style.borderColor = '#ef4444';

            if (request.approved_by) {
                elements.resultApprovedBy.textContent = request.approved_by;
                elements.resultApprover.style.display = 'block';
            } else {
                elements.resultApprover.style.display = 'none';
            }
            break;

        case 'expired':
            // SCADUTA (non autorizzata in tempo)
            elements.resultIcon.textContent = '⏰';
            elements.resultTitle.textContent = 'Cerere Expirată';
            elements.resultStatus.textContent = '⏰ ' + request.status_text;
            elements.resultStatus.style.color = '#dc2626';
            elements.resultCard.style.borderColor = '#dc2626';
            elements.resultApprover.style.display = 'none';
            break;

        case 'pending':
            // IN ATTESA (può ancora essere approvata)
            elements.resultIcon.textContent = '⏳';
            elements.resultTitle.textContent = 'Cerere în Așteptare';
            elements.resultStatus.textContent = '⏳ ' + request.status_text;
            elements.resultStatus.style.color = '#f59e0b';
            elements.resultCard.style.borderColor = '#f59e0b';
            elements.resultApprover.style.display = 'none';

            // Mostra il pulsante di reinvio solo se è pending
            if (request.can_resend) {
                elements.resendBtn.style.display = 'inline-flex';
            }
            break;

        default:
            // SCONOSCIUTO
            elements.resultIcon.textContent = '❓';
            elements.resultTitle.textContent = 'Stare Necunoscută';
            elements.resultStatus.textContent = '❓ ' + (request.status_text || 'Necunoscut');
            elements.resultStatus.style.color = '#64748b';
            elements.resultCard.style.borderColor = '#64748b';
            elements.resultApprover.style.display = 'none';
    }

    // Mostra risultato
    elements.checkForm.style.display = 'none';
    elements.resultSection.style.display = 'block';
}

// ========================================
// RESET FUNCTIONS
// ========================================
function resetForm() {
    elements.requestNumber.value = '';
    elements.checkForm.style.display = 'block';
    elements.resultSection.style.display = 'none';

    state.currentRequestNumber = null;

    if (state.autoResetTimeout) {
        clearTimeout(state.autoResetTimeout);
        state.autoResetTimeout = null;
    }

    elements.requestNumber.focus();
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
