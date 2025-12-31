"""
Servizio Keep-Alive Stampante
Mantiene attiva la connessione con la stampante predefinita
inviando periodicamente una semplice inquiry senza stampare nulla
"""
import time
import logging
import subprocess
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class PrinterKeepAlive:
    """
    Servizio che mantiene viva la connessione con la stampante predefinita
    inviando periodicamente una query di stato senza stampare
    """
    
    def __init__(self, interval_seconds=300):
        """
        Args:
            interval_seconds: Intervallo in secondi tra le query (default: 5 minuti)
        """
        self.interval = interval_seconds
        self.running = False
        self.thread = None
        self.last_check = None
        self.printer_name = None
        
    def get_default_printer(self):
        """Ottiene il nome della stampante predefinita"""
        try:
            ps_script = """
            $printer = Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default = TRUE"
            if ($printer) { $printer.Name } else { '' }
            """
            
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            printer_name = result.stdout.strip()
            if printer_name:
                return printer_name
            return None
                
        except Exception as e:
            logger.error(f"Errore recupero stampante predefinita: {e}")
            return None
    
    def ping_printer(self):
        """
        Invia una semplice query di stato alla stampante senza stampare
        Questo mantiene attiva la connessione e previene lo sleep
        """
        try:
            # Ottieni stampante predefinita
            printer_name = self.get_default_printer()
            
            if not printer_name:
                logger.warning("Nessuna stampante predefinita trovata per keep-alive")
                return False
            
            # Se la stampante è cambiata, logga
            if self.printer_name != printer_name:
                logger.info(f"Stampante keep-alive: {printer_name}")
                self.printer_name = printer_name
            
            # Query di stato della stampante (non stampa nulla)
            ps_script = f"""
            try {{
                $printer = Get-Printer -Name '{printer_name}' -ErrorAction Stop
                if ($printer) {{
                    # Verifica solo lo stato, non stampa
                    $status = $printer.PrinterStatus
                    Write-Output "OK:$status"
                }} else {{
                    Write-Output "ERROR:Printer not found"
                }}
            }} catch {{
                Write-Output "ERROR:$($_.Exception.Message)"
            }}
            """
            
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout.strip()
            
            if output.startswith('OK'):
                status = output.split(':')[1] if ':' in output else 'Unknown'
                logger.debug(f"Printer keep-alive OK - Status: {status}")
                self.last_check = datetime.now()
                return True
            else:
                logger.warning(f"Printer keep-alive failed: {output}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout durante printer keep-alive")
            return False
        except Exception as e:
            logger.error(f"Errore printer keep-alive: {e}")
            return False
    
    def _run_loop(self):
        """Loop principale del servizio keep-alive"""
        logger.info(f"Printer Keep-Alive avviato (intervallo: {self.interval}s)")
        
        while self.running:
            try:
                # Esegui ping stampante
                self.ping_printer()
                
                # Attendi intervallo
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Errore nel loop keep-alive: {e}")
                time.sleep(60)  # Attendi 1 minuto prima di riprovare
    
    def start(self):
        """Avvia il servizio keep-alive in background"""
        if self.running:
            logger.warning("Printer Keep-Alive già in esecuzione")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Printer Keep-Alive thread avviato")
    
    def stop(self):
        """Ferma il servizio keep-alive"""
        if not self.running:
            return
        
        logger.info("Arresto Printer Keep-Alive...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Printer Keep-Alive arrestato")
    
    def get_status(self):
        """Restituisce lo stato del servizio"""
        return {
            'running': self.running,
            'printer_name': self.printer_name,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'interval_seconds': self.interval
        }


# Istanza globale del servizio
_printer_keepalive = None


def start_printer_keepalive(interval_seconds=300):
    """
    Avvia il servizio keep-alive globale
    
    Args:
        interval_seconds: Intervallo in secondi (default: 5 minuti)
    """
    global _printer_keepalive
    
    if _printer_keepalive is None:
        _printer_keepalive = PrinterKeepAlive(interval_seconds)
        _printer_keepalive.start()
    else:
        logger.warning("Printer Keep-Alive già avviato")


def stop_printer_keepalive():
    """Ferma il servizio keep-alive globale"""
    global _printer_keepalive
    
    if _printer_keepalive:
        _printer_keepalive.stop()
        _printer_keepalive = None


def get_printer_keepalive_status():
    """Restituisce lo stato del servizio keep-alive"""
    global _printer_keepalive
    
    if _printer_keepalive:
        return _printer_keepalive.get_status()
    else:
        return {'running': False}


# Test
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== TEST PRINTER KEEP-ALIVE ===\n")
    
    # Avvia servizio
    keepalive = PrinterKeepAlive(interval_seconds=30)  # Test ogni 30 secondi
    keepalive.start()
    
    print("Servizio avviato. Premi Ctrl+C per fermare...\n")
    
    try:
        while True:
            status = keepalive.get_status()
            print(f"\rStatus: {status['running']} | Printer: {status['printer_name']} | Last: {status['last_check']}", end='')
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nArresto servizio...")
        keepalive.stop()
        print("Servizio arrestato.")
