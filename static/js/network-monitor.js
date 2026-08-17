// Network Connection Monitor
// Monitora la connessione al server Flask locale.
// Mostra l'overlay "offline" solo dopo N fallimenti consecutivi,
// per evitare falsi allarmi quando il server e' temporaneamente occupato.

const POLL_INTERVAL_MS   = 30000;  // controlla ogni 30 secondi
const FETCH_TIMEOUT_MS   = 10000;  // timeout singola richiesta: 10s
const FAILS_TO_OFFLINE   = 3;      // fallimenti consecutivi prima di mostrare overlay
const RECOVERY_TO_ONLINE = 1;      // successi consecutivi per tornare online

let isOnline            = true;
let consecutiveFails    = 0;
let consecutiveOk       = 0;
let offlineStartTime    = null;
let isCheckingConnection = false;

const offlineOverlay = document.getElementById('offlineOverlay');

// Controlla il server Flask tramite l'endpoint /api/health
async function checkServerConnection() {
    try {
        const controller = new AbortController();
        const timeoutId  = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

        const response = await fetch('/api/health', {
            method: 'GET',
            signal: controller.signal,
            cache:  'no-cache'
        });

        clearTimeout(timeoutId);
        return response.ok;
    } catch (error) {
        console.debug('Health check fallito:', error.message);
        return false;
    }
}

// Mostra l'overlay
function showOfflineOverlay() {
    if (!offlineStartTime) {
        offlineStartTime = new Date();
        console.warn('⚠️ Server non raggiungibile da:', offlineStartTime);
    }
    if (offlineOverlay) {
        offlineOverlay.style.display = 'flex';
    }
}

// Nascondi l'overlay
function hideOfflineOverlay() {
    if (offlineStartTime) {
        const duration = ((new Date()) - offlineStartTime) / 1000;
        console.log(`✅ Server raggiungibile. Durata offline: ${duration.toFixed(0)}s`);
        logOfflineRecovery(new Date(), duration);
        offlineStartTime = null;
    }
    if (offlineOverlay) {
        offlineOverlay.style.display = 'none';
    }
}

// Log recupero al backend (best-effort)
async function logOfflineRecovery(timestamp, duration) {
    try {
        await fetch('/api/log-offline', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                event_type:       'end',
                timestamp:        timestamp.toISOString(),
                duration_seconds: duration,
                user_agent:       navigator.userAgent,
                page:             window.location.pathname
            }),
            signal: AbortSignal.timeout(5000)
        });
    } catch (_) { /* ignora se offline */ }
}

// Logica principale con contatore fallimenti/successi
async function performConnectionCheck() {
    if (isCheckingConnection) return;
    isCheckingConnection = true;

    try {
        const serverOk = await checkServerConnection();

        if (serverOk) {
            consecutiveFails = 0;
            consecutiveOk++;

            if (!isOnline && consecutiveOk >= RECOVERY_TO_ONLINE) {
                console.log('✅ Connessione ripristinata');
                isOnline = true;
                hideOfflineOverlay();
            }
        } else {
            consecutiveOk = 0;
            consecutiveFails++;

            console.warn(`🔴 Check fallito (${consecutiveFails}/${FAILS_TO_OFFLINE})`);

            if (isOnline && consecutiveFails >= FAILS_TO_OFFLINE) {
                console.warn('🔴 Server non risponde — mostro overlay');
                isOnline = false;
                showOfflineOverlay();
            }
        }
    } finally {
        isCheckingConnection = false;
    }
}

// Evento browser offline immediato (cavo staccato, WiFi spento)
window.addEventListener('offline', () => {
    console.warn('🔴 Browser: evento offline');
    consecutiveFails = FAILS_TO_OFFLINE;
    isOnline         = false;
    showOfflineOverlay();
});

// Evento browser online: verifica il server prima di nascondere overlay
window.addEventListener('online', () => {
    console.log('🟢 Browser: evento online — verifico server...');
    consecutiveOk = 0;
    setTimeout(() => performConnectionCheck(), 1000);
});

// Polling periodico
setInterval(() => performConnectionCheck(), POLL_INTERVAL_MS);

// Check iniziale ritardato (lascia tempo al server di rispondere al boot)
setTimeout(() => {
    console.log('🔍 Check connessione iniziale...');
    performConnectionCheck();
}, 5000);
