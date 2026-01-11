// Kiosk Inactivity Timeout
// Ritorna alla homepage dopo 30 secondi di inattività

(function () {
    // Configurazione
    const INACTIVITY_TIMEOUT = 30000; // 30 secondi in millisecondi
    const HOME_URL = '/'; // URL homepage

    let inactivityTimer = null;

    // Eventi da monitorare per rilevare attività
    const activityEvents = [
        'mousedown',
        'mousemove',
        'keypress',
        'scroll',
        'touchstart',
        'click'
    ];

    // Resetta il timer di inattività
    function resetInactivityTimer() {
        // Pulisci timer esistente
        if (inactivityTimer) {
            clearTimeout(inactivityTimer);
        }

        // Avvia nuovo timer
        inactivityTimer = setTimeout(() => {
            returnToHome();
        }, INACTIVITY_TIMEOUT);
    }

    // Torna alla homepage
    function returnToHome() {
        const currentPath = window.location.pathname;

        // Se non siamo già sulla homepage
        if (currentPath !== HOME_URL) {
            console.log('⏱️ Timeout inattività - ritorno alla homepage');
            window.location.href = HOME_URL;
        }
    }

    // Registra event listeners per attività utente
    function initInactivityMonitor() {
        activityEvents.forEach(eventName => {
            document.addEventListener(eventName, resetInactivityTimer, true);
        });

        // Avvia timer iniziale
        resetInactivityTimer();

        console.log('✅ Inactivity monitor attivo (timeout: ' + (INACTIVITY_TIMEOUT / 1000) + 's)');
    }

    // Avvia al caricamento DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initInactivityMonitor);
    } else {
        initInactivityMonitor();
    }

})();
