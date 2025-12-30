"""
Modulo per interfacciarsi con il lettore RFID ABK-C2EM-RW
Usa la libreria IDReader.dll
"""

import ctypes
import os
import logging
import threading
import time

logger = logging.getLogger(__name__)


class RFIDReader:
    """Classe per gestire il lettore RFID ABK-C2EM-RW"""
    
    def __init__(self, dll_path='IDReader.dll'):
        """
        Inizializza il lettore RFID
        
        Args:
            dll_path: Path alla DLL IDReader.dll
        """
        self.dll_path = dll_path
        self.dll = None
        self.is_connected = False
        self.last_card_id = None
        self.callback = None
        self.reader_thread = None
        self.stop_reading = False
        
        try:
            # Carica la DLL
            if not os.path.exists(dll_path):
                logger.error(f"DLL non trovata: {dll_path}")
                return
            
            self.dll = ctypes.WinDLL(dll_path)
            logger.info(f"DLL caricata: {dll_path}")
            
        except Exception as e:
            logger.error(f"Errore caricamento DLL: {str(e)}")
    
    def connect(self, port='COM1', baudrate=9600):
        """
        Connette al lettore RFID
        
        Args:
            port: Porta seriale (es. 'COM1', 'COM3')
            baudrate: Velocità comunicazione (default 9600)
        
        Returns:
            bool: True se connesso, False altrimenti
        """
        try:
            if not self.dll:
                logger.error("DLL non caricata")
                return False
            
            # Funzioni tipiche per lettori RFID (da adattare alla DLL specifica)
            # Esempio generico - verificare documentazione IDReader.dll
            
            # Prova a connettersi
            # result = self.dll.OpenPort(port.encode(), baudrate)
            
            # Per ora simuliamo la connessione
            self.is_connected = True
            logger.info(f"Connesso al lettore RFID su {port}")
            return True
            
        except Exception as e:
            logger.error(f"Errore connessione lettore RFID: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnette dal lettore RFID"""
        try:
            self.stop_reading = True
            
            if self.reader_thread and self.reader_thread.is_alive():
                self.reader_thread.join(timeout=2)
            
            if self.dll and self.is_connected:
                # self.dll.ClosePort()
                pass
            
            self.is_connected = False
            logger.info("Disconnesso dal lettore RFID")
            
        except Exception as e:
            logger.error(f"Errore disconnessione: {str(e)}")
    
    def read_card(self, timeout=5):
        """
        Legge una card RFID (lettura singola)
        
        Args:
            timeout: Timeout in secondi
        
        Returns:
            str: ID della card letta, None se timeout o errore
        """
        try:
            if not self.is_connected:
                logger.error("Lettore non connesso")
                return None
            
            # Buffer per l'ID della card
            card_id_buffer = ctypes.create_string_buffer(32)
            
            # Leggi card (esempio generico - verificare documentazione)
            # result = self.dll.ReadCard(card_id_buffer, timeout)
            
            # Per ora simuliamo la lettura
            # In produzione, questa funzione dovrebbe chiamare la DLL
            logger.info("Attesa lettura card RFID...")
            
            # Placeholder - sostituire con chiamata reale alla DLL
            return None
            
        except Exception as e:
            logger.error(f"Errore lettura card: {str(e)}")
            return None
    
    def start_continuous_reading(self, callback):
        """
        Avvia lettura continua in background
        
        Args:
            callback: Funzione da chiamare quando viene letta una card
                     Firma: callback(card_id: str)
        """
        if not self.is_connected:
            logger.error("Lettore non connesso")
            return False
        
        self.callback = callback
        self.stop_reading = False
        
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()
        
        logger.info("Lettura continua avviata")
        return True
    
    def stop_continuous_reading(self):
        """Ferma la lettura continua"""
        self.stop_reading = True
        if self.reader_thread:
            self.reader_thread.join(timeout=2)
        logger.info("Lettura continua fermata")
    
    def _read_loop(self):
        """Loop di lettura continua (eseguito in thread separato)"""
        while not self.stop_reading:
            try:
                card_id = self.read_card(timeout=1)
                
                if card_id and card_id != self.last_card_id:
                    self.last_card_id = card_id
                    
                    if self.callback:
                        self.callback(card_id)
                
                time.sleep(0.1)  # Piccola pausa per non sovraccaricare
                
            except Exception as e:
                logger.error(f"Errore nel loop di lettura: {str(e)}")
                time.sleep(1)
    
    def __del__(self):
        """Cleanup quando l'oggetto viene distrutto"""
        self.disconnect()


# ========================================
# FUNZIONI DI UTILITÀ
# ========================================

def test_reader():
    """Funzione di test per il lettore RFID"""
    print("=== TEST LETTORE RFID ABK-C2EM-RW ===")
    
    reader = RFIDReader()
    
    if reader.connect(port='COM3'):
        print("✓ Connesso al lettore")
        
        print("\nAttesa lettura card (10 secondi)...")
        card_id = reader.read_card(timeout=10)
        
        if card_id:
            print(f"✓ Card letta: {card_id}")
        else:
            print("✗ Nessuna card letta")
        
        reader.disconnect()
        print("✓ Disconnesso")
    else:
        print("✗ Errore connessione")


if __name__ == '__main__':
    # Test del modulo
    test_reader()
