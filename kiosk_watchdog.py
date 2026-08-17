"""
kiosk_watchdog.py
-----------------
Watchdog per il server Flask Kiosk HR.
Avvia app.py e lo riavvia automaticamente se crasha o viene terminato.
Pensato per girare come processo di sistema all'avvio di Windows.

Comportamento:
  - Avvia app.py nella stessa directory di questo script
  - Se il processo termina per qualunque motivo, lo rilancia dopo RESTART_DELAY_SEC
  - Dopo MAX_CRASHES_IN_WINDOW crash rapidi (< CRASH_WINDOW_SEC) aspetta piu' a lungo
  - Scrive un log in kiosk_watchdog.log nella stessa directory
"""

import subprocess
import time
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Configurazione ────────────────────────────────────────────────────────────
BASE_DIR          = Path(__file__).parent.resolve()
APP_SCRIPT        = BASE_DIR / 'app.py'
PYTHON_EXE        = sys.executable          # usa lo stesso Python che lancia il watchdog
LOG_FILE          = BASE_DIR / 'kiosk_watchdog.log'
RESTART_DELAY_SEC = 5                        # secondi di attesa prima del riavvio normale
LONG_DELAY_SEC    = 60                       # attesa dopo troppi crash ravvicinati
MAX_CRASHES_IN_WINDOW = 5                    # numero di crash che attiva la pausa lunga
CRASH_WINDOW_SEC  = 120                      # finestra temporale per contare i crash rapidi
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [WATCHDOG] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('kiosk_watchdog')


def run():
    logger.info('=' * 60)
    logger.info('KIOSK HR WATCHDOG - AVVIO')
    logger.info(f'App      : {APP_SCRIPT}')
    logger.info(f'Python   : {PYTHON_EXE}')
    logger.info(f'Restart  : {RESTART_DELAY_SEC}s  |  Max crash: {MAX_CRASHES_IN_WINDOW}/{CRASH_WINDOW_SEC}s')
    logger.info('=' * 60)

    crash_times = []   # timestamp degli ultimi crash
    run_count   = 0

    while True:
        run_count += 1
        start_time = time.time()
        logger.info(f'[Run #{run_count}] Avvio server Flask...')

        try:
            env = os.environ.copy()
            env['PYTHONUTF8']       = '1'
            env['PYTHONIOENCODING'] = 'utf-8'

            proc = subprocess.Popen(
                [PYTHON_EXE, str(APP_SCRIPT)],
                cwd=str(BASE_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )
            logger.info(f'[Run #{run_count}] Processo avviato — PID {proc.pid}')
            proc.wait()  # blocca finche' il processo gira
            exit_code = proc.returncode
        except Exception as e:
            logger.error(f'[Run #{run_count}] Errore nel lancio: {e}')
            exit_code = -1

        elapsed = time.time() - start_time
        logger.warning(f'[Run #{run_count}] Processo terminato — exit code {exit_code}, durata {elapsed:.1f}s')

        # Registra il crash e pulisci quelli vecchi
        now = time.time()
        crash_times.append(now)
        crash_times = [t for t in crash_times if now - t <= CRASH_WINDOW_SEC]

        if len(crash_times) >= MAX_CRASHES_IN_WINDOW:
            logger.error(
                f'[Run #{run_count}] {len(crash_times)} crash in {CRASH_WINDOW_SEC}s — '
                f'attendo {LONG_DELAY_SEC}s prima di riprovare...'
            )
            time.sleep(LONG_DELAY_SEC)
            crash_times.clear()
        else:
            logger.info(f'[Run #{run_count}] Riavvio tra {RESTART_DELAY_SEC}s...')
            time.sleep(RESTART_DELAY_SEC)


if __name__ == '__main__':
    run()
