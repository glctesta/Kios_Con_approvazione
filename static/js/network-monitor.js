// Network Connection Monitor
// Monitora connessione e mostra overlay quando offline

let isOnline = true;  // Assume online all'inizio
let offlineStartTime = null;
let isCheckingConnection = false;

const offlineOverlay = document.getElementById('offlineOverlay');

// Controlla connessione al server locale
async function checkServerConnection() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

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

// Controlla connessione internet esterna (non solo localhost)
async function checkInternetConnection() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000); // 8s timeout

        // Usa Google favicon (piccolo, veloce, sempre disponibile)
        const response = await fetch('https://www.google.com/favicon.ico', {
            method: 'HEAD',
            mode: 'no-cors',
            cache: 'no-cache',
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        // no-cors restituisce sempre ok, quindi se arriva qui è online
        return true;
    } catch (error) {
        console.debug('Internet check fallito:', error.message);
        return false;
    }
}

// Mostra overlay offline
function showOfflineOverlay() {
    if (!offlineStartTime) {
        offlineStartTime = new Date();
        console.warn('Connessione persa:', offlineStartTime);
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

        console.log('Connessione ripristinata. Durata offline:', duration, 'secondi');

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

// Check connessione completo (server + internet)
async function performConnectionCheck() {
    if (isCheckingConnection) return;

    isCheckingConnection = true;

    try {
        const browserOnline = navigator.onLine;

        // Se browser offline, non serve controllare altro
        if (!browserOnline) {
            if (isOnline) {
                console.warn('Browser offline');
                isOnline = false;
                showOfflineOverlay();
            }
            return;
        }

        // Controlla sia server che internet
        const [serverOk, internetOk] = await Promise.all([
            checkServerConnection(),
            checkInternetConnection()
        ]);

        // Serve ENTRAMBI per essere online
        const currentlyOnline = browserOnline && serverOk && internetOk;

        // Cambio stato
        if (isOnline && !currentlyOnline) {
            if (!serverOk) {
                console.warn('Server non raggiungibile!');
            }
            if (!internetOk) {
                console.warn('Internet non raggiungibile!');
            }
            isOnline = false;
            showOfflineOverlay();
        } else if (!isOnline && currentlyOnline) {
            console.log('Connessione ripristinata!');
            isOnline = true;
            hideOfflineOverlay();
        }
    } finally {
        isCheckingConnection = false;
    }
}

// Event listeners
window.addEventListener('online', () => {
    console.log('Browser online');
    setTimeout(() => performConnectionCheck(), 1000);
});

window.addEventListener('offline', () => {
    console.warn('Browser offline');
    isOnline = false;
    showOfflineOverlay();
});

// Polling ogni 10 secondi
setInterval(() => performConnectionCheck(), 10000);

// Check iniziale con delay
setTimeout(() => {
    console.log('Check connessione iniziale...');
    performConnectionCheck();
}, 2000); // Attendi 2s dopo page load
