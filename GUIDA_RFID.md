# Guida Integrazione Lettore RFID ABK-C2EM-RW

## 📋 OVERVIEW

Il modulo `rfid_reader.py` fornisce un wrapper Python per interfacciarsi con il lettore RFID **ABK-C2EM-RW** tramite la libreria `IDReader.dll`.

---

## 🔧 STATO ATTUALE

✅ **Completato**:
- Struttura base del modulo
- Gestione connessione/disconnessione
- Lettura singola e continua
- Thread separato per lettura background
- Logging completo

⚠️ **DA COMPLETARE**:
- Mappatura funzioni specifiche della DLL
- Parametri corretti per le chiamate DLL
- Test con hardware reale

---

## 📚 DOCUMENTAZIONE NECESSARIA

Per completare l'integrazione, servono le seguenti informazioni dalla documentazione di `IDReader.dll`:

### 1. **Funzioni Esportate**

Verificare quali funzioni sono esportate dalla DLL:
```python
# Esempio per ispezionare la DLL
import ctypes
dll = ctypes.WinDLL('IDReader.dll')

# Funzioni tipiche per lettori RFID:
# - OpenPort / Connect
# - ClosePort / Disconnect
# - ReadCard / GetCardID
# - WriteCard (se supportato)
# - GetVersion
```

### 2. **Parametri Funzioni**

Per ogni funzione, verificare:
- **Tipo parametri** (int, string, pointer, ecc.)
- **Valore di ritorno**
- **Codici errore**

**Esempio**:
```c
// Documentazione tipica
int OpenPort(char* portName, int baudRate);
// Return: 0 = success, -1 = error

int ReadCard(char* cardIdBuffer, int bufferSize, int timeout);
// Return: lunghezza ID letto, -1 = error
```

### 3. **Configurazione Porta**

- **Porta seriale**: COM1, COM3, USB?
- **Baud rate**: 9600, 115200?
- **Parametri aggiuntivi**: Parity, StopBits, DataBits?

---

## 🔨 COME COMPLETARE IL MODULO

### Step 1: Mappare le Funzioni DLL

Modificare `rfid_reader.py` per definire le funzioni:

```python
def __init__(self, dll_path='IDReader.dll'):
    self.dll = ctypes.WinDLL(dll_path)
    
    # Definisci le funzioni esportate
    # Esempio:
    self.dll.OpenPort.argtypes = [ctypes.c_char_p, ctypes.c_int]
    self.dll.OpenPort.restype = ctypes.c_int
    
    self.dll.ReadCard.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    self.dll.ReadCard.restype = ctypes.c_int
    
    self.dll.ClosePort.argtypes = []
    self.dll.ClosePort.restype = ctypes.c_int
```

### Step 2: Implementare `connect()`

```python
def connect(self, port='COM1', baudrate=9600):
    try:
        # Chiamata reale alla DLL
        result = self.dll.OpenPort(port.encode('utf-8'), baudrate)
        
        if result == 0:  # Success
            self.is_connected = True
            logger.info(f"Connesso a {port}")
            return True
        else:
            logger.error(f"Errore connessione: codice {result}")
            return False
            
    except Exception as e:
        logger.error(f"Errore: {str(e)}")
        return False
```

### Step 3: Implementare `read_card()`

```python
def read_card(self, timeout=5):
    try:
        # Buffer per l'ID
        buffer_size = 32
        card_id_buffer = ctypes.create_string_buffer(buffer_size)
        
        # Leggi card
        result = self.dll.ReadCard(
            card_id_buffer,
            buffer_size,
            timeout * 1000  # Timeout in ms
        )
        
        if result > 0:  # Successo
            card_id = card_id_buffer.value.decode('utf-8')
            logger.info(f"Card letta: {card_id}")
            return card_id
        else:
            return None
            
    except Exception as e:
        logger.error(f"Errore lettura: {str(e)}")
        return None
```

### Step 4: Implementare `disconnect()`

```python
def disconnect(self):
    try:
        self.stop_reading = True
        
        if self.dll and self.is_connected:
            result = self.dll.ClosePort()
            logger.info(f"Disconnesso (result: {result})")
        
        self.is_connected = False
        
    except Exception as e:
        logger.error(f"Errore disconnessione: {str(e)}")
```

---

## 🧪 TESTING

### Test Base

```python
from rfid_reader import RFIDReader

# Crea istanza
reader = RFIDReader()

# Connetti (verificare porta corretta)
if reader.connect(port='COM3', baudrate=9600):
    print("✓ Connesso")
    
    # Leggi card
    card_id = reader.read_card(timeout=10)
    if card_id:
        print(f"✓ Card: {card_id}")
    
    # Disconnetti
    reader.disconnect()
```

### Test Lettura Continua

```python
def on_card_read(card_id):
    print(f"Card letta: {card_id}")

reader = RFIDReader()
reader.connect()
reader.start_continuous_reading(callback=on_card_read)

# Lascia leggere per 30 secondi
import time
time.sleep(30)

reader.stop_continuous_reading()
reader.disconnect()
```

---

## 🔗 INTEGRAZIONE CON KIOSK

Una volta completato il modulo, integrarlo nell'applicazione:

### 1. Modifica `badge_reader.py`

```python
from rfid_reader import RFIDReader

class BadgeReader:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.rfid_reader = RFIDReader()
        self.rfid_reader.connect(port='COM3')
    
    def read_badge_rfid(self, timeout=10):
        """Legge badge da lettore RFID"""
        card_id = self.rfid_reader.read_card(timeout=timeout)
        
        if card_id:
            # Normalizza e valida
            return self.normalize_badge_number(card_id)
        
        return None
```

### 2. Endpoint API per RFID

```python
@app.route('/api/read-rfid', methods=['POST'])
def read_rfid():
    """Legge badge da lettore RFID"""
    try:
        badge_reader = BadgeReader(db_connection.connect())
        card_id = badge_reader.read_badge_rfid(timeout=10)
        
        if card_id:
            # Valida badge
            employee = badge_reader.get_employee_by_badge(card_id)
            
            if employee:
                return jsonify({
                    'success': True,
                    'badge': card_id,
                    'employee': employee
                })
        
        return jsonify({'success': False, 'error': 'Nessuna card letta'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### 3. Frontend JavaScript

```javascript
async function readRFID() {
    showLoading('Avvicinare il badge al lettore...');
    
    const response = await fetch('/api/read-rfid', {
        method: 'POST'
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Badge letto con successo
        populateEmployeeData(data.employee);
    } else {
        showToast('Nessun badge letto', 'error');
    }
    
    hideLoading();
}
```

---

## 📝 CHECKLIST COMPLETAMENTO

- [ ] Ottenere documentazione `IDReader.dll`
- [ ] Identificare funzioni esportate
- [ ] Mappare parametri e tipi
- [ ] Implementare `connect()`
- [ ] Implementare `read_card()`
- [ ] Implementare `disconnect()`
- [ ] Testare con hardware reale
- [ ] Verificare porta seriale corretta
- [ ] Integrare in `badge_reader.py`
- [ ] Creare endpoint API
- [ ] Testare workflow completo

---

## 🆘 TROUBLESHOOTING

### DLL non caricata
```
Errore: OSError: [WinError 126] Impossibile trovare il modulo specificato
```
**Soluzione**: Verificare che `IDReader.dll` sia nella stessa directory di `rfid_reader.py` o nel PATH

### Porta COM non trovata
```
Errore: Porta COM3 non disponibile
```
**Soluzione**: 
- Verificare Device Manager → Porte (COM e LPT)
- Provare altre porte (COM1, COM4, ecc.)
- Verificare driver installati

### Timeout lettura
```
Nessuna card letta dopo 10 secondi
```
**Soluzione**:
- Verificare che il lettore sia acceso
- Avvicinare la card al lettore
- Verificare baudrate corretto

---

## 📞 SUPPORTO

Per completare l'integrazione, fornire:
1. **Documentazione** `IDReader.dll` (PDF, header file .h)
2. **Esempi** di codice (C++, C#, VB)
3. **Specifiche** lettore ABK-C2EM-RW

---

**MODULO PRONTO PER COMPLETAMENTO!** 🔧📡
