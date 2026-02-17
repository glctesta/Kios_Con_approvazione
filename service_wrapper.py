"""
Windows Service Wrapper per Kiosk Reports Service
Permette l'esecuzione come servizio Windows
"""
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import logging
from pathlib import Path

# Aggiungi directory corrente al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service_kiosk_reports import KioskReportsService

# Configurazione logging per il servizio
log_path = Path(__file__).parent / 'kiosk_reports_service.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class KioskReportsWindowsService(win32serviceutil.ServiceFramework):
    """
    Servizio Windows per Kiosk Reports
    """
    _svc_name_ = "KioskReportsService"
    _svc_display_name_ = "Kiosk HR Reports Service"
    _svc_description_ = "Servizio automatico per l'invio di report mensili sull'utilizzo del Kiosk HR"

    def __init__(self, args):
        """Inizializza il servizio"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True
        self.service = None

    def SvcStop(self):
        """Ferma il servizio"""
        logger.info("Richiesta di stop del servizio ricevuta")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        """Esegue il servizio"""
        try:
            logger.info("=" * 60)
            logger.info("KIOSK REPORTS WINDOWS SERVICE - AVVIO")
            logger.info("=" * 60)
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )

            # Inizializza e avvia il servizio
            self.service = KioskReportsService()
            
            # Avvia il servizio in un thread separato
            import threading
            service_thread = threading.Thread(target=self.service.run_service)
            service_thread.daemon = True
            service_thread.start()

            # Attendi segnale di stop
            while self.is_running:
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                if rc == win32event.WAIT_OBJECT_0:
                    break

            logger.info("Servizio in fase di arresto...")
            
        except Exception as e:
            logger.error(f"Errore critico nel servizio: {e}", exc_info=True)
            servicemanager.LogErrorMsg(f"Errore nel servizio: {e}")
        finally:
            logger.info("Servizio arrestato")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, '')
            )


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(KioskReportsWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(KioskReportsWindowsService)
