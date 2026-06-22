// Network Connection Monitor
// Monitora connessione e mostra overlay quando offline

let isOnline = true;
let offlineStartTime = null;
let isCheckingConnection = false;

const offlineOverlay = document.getElementById('offlineOverlay');

// Controlla connessione al server locale Flask (unica fonte di verità per il kiosk)
async function checkServerConnection() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);

        const response = await fetch('/api/health', {
            method: 'GET',
            signal: controller.signal,
            cache: 'no-cache'
        });

        clearTimeout(timeoutId);
        return response.ok;
    } catch (error) {
        console.debug('Server check fallito:', error.message);
        return false;
    }
}

// Mostra overlay offline
function showOfflineOverlay() {
    if (!offlineStartTime) {
        offlineStartTime = new Date();
        console.warn('⚠️ Connessione persa:', offlineStartTime);
    }

    if (offlineOverlay) {
        offlineOverlay.style.display = 'flex';
    }
}

// Nascondi overlay offline
function hideOfflineOverlay() {
    if (offlineStartTime) {
        const offlineEndTime = new Date();
        const duration = (offlineEndTime - offlineStartTime) / 1000;

        console.log('✅ Connessione ripristinata. Durata offline:', duration.toFixed(1), 'secondi');

        // Log recovery
        logOfflineRecovery(offlineEndTime, duration);

        offlineStartTime = null;
    }

    if (offlineOverlay) {
        offlineOverlay.style.display = 'none';
    }
}

// Log recupero connessione
async function logOfflineRecovery(timestamp, duration) {
    try {
        await fetch('/api/log-offline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_type: 'end',
                timestamp: timestamp.toISOString(),
                duration_seconds: duration,
                user_agent: navigator.userAgent,
                page: window.location.pathname
            }),
            signal: AbortSignal.timeout(5000)
        });
    } catch (error) {
        console.debug('Log offline failed (normale)');
    }
}

// Check connessione: solo server locale (il kiosk non richiede internet pubblico)
async function performConnectionCheck() {
    if (isCheckingConnection) return;

    isCheckingConnection = true;

    try {
        const serverOk = await checkServerConnection();

        if (!serverOk) {
            if (isOnline) {
                console.warn('🔴 Server locale non raggiungibile');
                isOnline = false;
                showOfflineOverlay();
            }
            return;
        }

        if (!isOnline) {
            console.log('✅ Server locale raggiungibile');
            isOnline = true;
            hideOfflineOverlay();
        }

    } finally {
        isCheckingConnection = false;
    }
}

// Event listeners
window.addEventListener('online', () => {
    console.log('🟢 Browser online event');
    setTimeout(() => performConnectionCheck(), 1000);
});

window.addEventListener('offline', () => {
    console.warn('🔴 Browser offline event');
    isOnline = false;
    showOfflineOverlay();
});

// Polling ogni 15 secondi
setInterval(() => performConnectionCheck(), 15000);

// Check iniziale con delay
setTimeout(() => {
    console.log('🔍 Check connessione iniziale...');
    performConnectionCheck();
}, 2000);
