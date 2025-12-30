"""
Script di test per IDReader.dll
Ispeziona e testa il lettore RFID ABK-C2EM-RW
"""

import ctypes
import os
import sys
import time


def print_separator(title=""):
    """Stampa separatore visivo"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def test_dll_loading():
    """Test 1: Caricamento DLL"""
    print_separator("TEST 1: Caricamento DLL")
    
    dll_path = 'IDReader.dll'
    
    if not os.path.exists(dll_path):
        print(f"✗ ERRORE: {dll_path} non trovato nella directory corrente")
        print(f"  Directory corrente: {os.getcwd()}")
        return None
    
    print(f"✓ File trovato: {dll_path}")
    print(f"  Dimensione: {os.path.getsize(dll_path)} bytes")
    
    try:
        # Prova WinDLL (per DLL Windows standard)
        dll = ctypes.WinDLL(dll_path)
        print("✓ DLL caricata con successo (WinDLL)")
        return dll
        
    except Exception as e:
        print(f"✗ Errore caricamento WinDLL: {e}")
        
        try:
            # Prova CDLL (per DLL con calling convention C)
            dll = ctypes.CDLL(dll_path)
            print("✓ DLL caricata con successo (CDLL)")
            return dll
        except Exception as e2:
            print(f"✗ Errore caricamento CDLL: {e2}")
            return None


def test_common_functions(dll):
    """Test 2: Prova funzioni comuni per lettori RFID"""
    print_separator("TEST 2: Test Funzioni Comuni")
    
    if not dll:
        print("✗ DLL non caricata, skip test")
        return
    
    # Lista di nomi di funzioni comuni per lettori RFID
    common_functions = [
        # Connessione
        'OpenPort', 'Open', 'Connect', 'Initialize', 'Init',
        'ClosePort', 'Close', 'Disconnect', 'Shutdown',
        
        # Lettura
        'ReadCard', 'Read', 'GetCardID', 'GetID', 'ReadUID',
        'ReadBlock', 'ReadData',
        
        # Scrittura
        'WriteCard', 'Write', 'WriteBlock', 'WriteData',
        
        # Info
        'GetVersion', 'GetDeviceInfo', 'GetStatus',
        
        # Beep/LED
        'Beep', 'SetLED', 'LED',
    ]
    
    found_functions = []
    
    print("Ricerca funzioni esportate...")
    for func_name in common_functions:
        try:
            func = getattr(dll, func_name)
            found_functions.append(func_name)
            print(f"  ✓ Trovata: {func_name}")
        except AttributeError:
            pass
    
    if found_functions:
        print(f"\n✓ Trovate {len(found_functions)} funzioni:")
        for func in found_functions:
            print(f"  - {func}")
    else:
        print("\n✗ Nessuna funzione comune trovata")
        print("  La DLL potrebbe usare nomi di funzioni diversi")
    
    return found_functions


def test_port_opening(dll, found_functions):
    """Test 3: Prova ad aprire una porta"""
    print_separator("TEST 3: Apertura Porta")
    
    if not dll or not found_functions:
        print("✗ Skip test (nessuna funzione trovata)")
        return
    
    # Cerca funzioni di apertura porta
    open_functions = [f for f in found_functions if 'Open' in f or 'Connect' in f or 'Init' in f]
    
    if not open_functions:
        print("✗ Nessuna funzione di apertura porta trovata")
        return
    
    print(f"Funzioni di apertura disponibili: {open_functions}")
    
    # Prova diverse porte COM
    ports = ['COM1', 'COM3', 'COM4', 'COM5']
    
    for func_name in open_functions[:1]:  # Prova solo la prima
        print(f"\nTest funzione: {func_name}")
        
        try:
            func = getattr(dll, func_name)
            
            # Prova diverse signature
            for port in ports:
                try:
                    print(f"  Tentativo {port}...")
                    
                    # Prova 1: Solo porta (string)
                    result = func(port.encode('utf-8'))
                    print(f"    ✓ Chiamata riuscita! Result: {result}")
                    
                    if result == 0 or result == 1:
                        print(f"    ✓ Possibile successo (result={result})")
                        return True
                    
                except Exception as e:
                    # Prova 2: Porta + baudrate
                    try:
                        result = func(port.encode('utf-8'), 9600)
                        print(f"    ✓ Chiamata riuscita (con baudrate)! Result: {result}")
                        
                        if result == 0 or result == 1:
                            print(f"    ✓ Possibile successo (result={result})")
                            return True
                            
                    except:
                        pass
                
        except Exception as e:
            print(f"  ✗ Errore: {e}")
    
    print("\n⚠️ Nessuna porta aperta con successo")
    print("  Potrebbe essere necessario specificare parametri diversi")


def test_read_card(dll, found_functions):
    """Test 4: Prova a leggere una card"""
    print_separator("TEST 4: Lettura Card")
    
    if not dll or not found_functions:
        print("✗ Skip test (nessuna funzione trovata)")
        return
    
    # Cerca funzioni di lettura
    read_functions = [f for f in found_functions if 'Read' in f or 'Get' in f]
    
    if not read_functions:
        print("✗ Nessuna funzione di lettura trovata")
        return
    
    print(f"Funzioni di lettura disponibili: {read_functions}")
    print("\n⚠️ AVVICINARE UNA CARD AL LETTORE ORA!")
    print("   Attesa 5 secondi...")
    time.sleep(5)
    
    for func_name in read_functions[:2]:  # Prova le prime 2
        print(f"\nTest funzione: {func_name}")
        
        try:
            func = getattr(dll, func_name)
            
            # Prova con buffer
            buffer_size = 32
            card_buffer = ctypes.create_string_buffer(buffer_size)
            
            try:
                # Prova 1: Solo buffer
                result = func(card_buffer)
                print(f"  ✓ Chiamata riuscita! Result: {result}")
                
                if card_buffer.value:
                    print(f"  ✓ Card ID: {card_buffer.value.decode('utf-8', errors='ignore')}")
                    return card_buffer.value
                    
            except:
                try:
                    # Prova 2: Buffer + size
                    result = func(card_buffer, buffer_size)
                    print(f"  ✓ Chiamata riuscita (con size)! Result: {result}")
                    
                    if card_buffer.value:
                        print(f"  ✓ Card ID: {card_buffer.value.decode('utf-8', errors='ignore')}")
                        return card_buffer.value
                        
                except:
                    try:
                        # Prova 3: Buffer + size + timeout
                        result = func(card_buffer, buffer_size, 5000)
                        print(f"  ✓ Chiamata riuscita (con timeout)! Result: {result}")
                        
                        if card_buffer.value:
                            print(f"  ✓ Card ID: {card_buffer.value.decode('utf-8', errors='ignore')}")
                            return card_buffer.value
                            
                    except Exception as e:
                        print(f"  ✗ Errore: {e}")
                        
        except Exception as e:
            print(f"  ✗ Errore: {e}")
    
    print("\n⚠️ Nessuna card letta")


def main():
    """Funzione principale"""
    print_separator("TEST LETTORE RFID ABK-C2EM-RW")
    print("Script di diagnostica per IDReader.dll")
    print(f"Directory: {os.getcwd()}")
    
    # Test 1: Carica DLL
    dll = test_dll_loading()
    
    if not dll:
        print("\n" + "=" * 70)
        print("CONCLUSIONE: Impossibile caricare la DLL")
        print("=" * 70)
        return
    
    # Test 2: Cerca funzioni
    found_functions = test_common_functions(dll)
    
    # Test 3: Prova apertura porta
    if found_functions:
        test_port_opening(dll, found_functions)
    
    # Test 4: Prova lettura card
    if found_functions:
        test_read_card(dll, found_functions)
    
    # Conclusione
    print_separator("CONCLUSIONE")
    
    if found_functions:
        print("✓ DLL caricata e funzioni trovate")
        print("\nFunzioni disponibili:")
        for func in found_functions:
            print(f"  - {func}")
        
        print("\nPROSSIMI PASSI:")
        print("1. Verificare documentazione per parametri corretti")
        print("2. Testare con hardware collegato")
        print("3. Aggiornare rfid_reader.py con funzioni corrette")
    else:
        print("⚠️ DLL caricata ma nessuna funzione comune trovata")
        print("\nPROSSIMI PASSI:")
        print("1. Ottenere documentazione IDReader.dll")
        print("2. Verificare se è la DLL corretta per ABK-C2EM-RW")
        print("3. Usare tool come 'dumpbin /EXPORTS IDReader.dll' per vedere tutte le funzioni")
    
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrotto dall'utente")
    except Exception as e:
        print(f"\n\nERRORE FATALE: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nPremi INVIO per uscire...")
    input()
