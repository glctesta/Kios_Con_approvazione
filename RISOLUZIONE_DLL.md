# Risoluzione Problema Dipendenze IDReader.dll

## 🔴 PROBLEMA

```
ERROR loading WinDLL: Could not find module 'IDReader.dll' 
(or one of its dependencies). Try using the full path with constructor syntax.
```

**Causa**: La DLL `IDReader.dll` richiede altre DLL (dipendenze) che non sono presenti nel sistema.

---

## ✅ SOLUZIONI

### **Soluzione 1: Installare Visual C++ Redistributable** (CONSIGLIATO)

La maggior parte delle DLL Windows richiede le librerie Visual C++ Runtime.

#### **Download e Installazione**:

1. **Visual C++ 2015-2022 Redistributable (x64)**:
   - Link: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Scarica ed esegui
   - Riavvia il computer

2. **Se Python è 32-bit, installa anche x86**:
   - Link: https://aka.ms/vs/17/release/vc_redist.x86.exe

3. **Versioni precedenti** (se necessario):
   - VC++ 2013: https://aka.ms/highdpimfc2013x64enu
   - VC++ 2010: https://www.microsoft.com/download/details.aspx?id=26999

#### **Dopo l'installazione**:
```bash
python check_dll_deps.py
```

---

### **Soluzione 2: Identificare Dipendenze Mancanti**

#### **Opzione A: Dependency Walker** (Tool Grafico)

1. **Download**: https://www.dependencywalker.com/
2. **Esegui** `depends.exe`
3. **File → Open** → Seleziona `IDReader.dll`
4. **Cerca** DLL con icona rossa (= mancanti)
5. **Copia** le DLL mancanti nella directory del progetto

#### **Opzione B: dumpbin** (Command Line)

Se hai Visual Studio installato:

```bash
cd c:\Users\gtesta\PythonProjetcs\Python\Adeverente

# Vedi dipendenze
dumpbin /DEPENDENTS IDReader.dll

# Output esempio:
#   msvcr120.dll
#   kernel32.dll
#   user32.dll
```

Cerca le DLL mancanti in:
- `C:\Windows\System32\`
- `C:\Windows\SysWOW64\` (per DLL 32-bit)

---

### **Soluzione 3: Copiare DLL dal Kit del Lettore**

Il lettore RFID ABK-C2EM-RW dovrebbe avere un CD/DVD o download con:
- `IDReader.dll`
- **Altre DLL necessarie**
- Driver
- Software di test

**Azione**:
1. Cerca il pacchetto software del lettore
2. Copia **tutte le DLL** nella directory del progetto:
   ```
   c:\Users\gtesta\PythonProjetcs\Python\Adeverente\
   ```

---

### **Soluzione 4: Usare Path Assoluto**

Modifica `rfid_reader.py`:

```python
import os

# Usa path assoluto
dll_path = os.path.abspath('IDReader.dll')
dll_dir = os.path.dirname(dll_path)

# Aggiungi directory al PATH
os.environ['PATH'] = dll_dir + os.pathsep + os.environ['PATH']

# Carica DLL
self.dll = ctypes.WinDLL(dll_path)
```

---

## 🔍 DIAGNOSTICA

### **Verifica Architettura**

```bash
# Verifica Python
python -c "import sys; print('64-bit' if sys.maxsize > 2**32 else '32-bit')"

# Verifica DLL (con dumpbin)
dumpbin /HEADERS IDReader.dll | findstr machine
# Output:
#   8664 machine (x64)  → 64-bit
#   14C machine (x86)   → 32-bit
```

**IMPORTANTE**: Python e DLL devono avere la stessa architettura!

---

## 📋 CHECKLIST

- [ ] Installato Visual C++ Redistributable 2015-2022 (x64)
- [ ] Riavviato il computer
- [ ] Eseguito `python check_dll_deps.py`
- [ ] Verificato architettura Python e DLL
- [ ] Copiato tutte le DLL dal kit del lettore
- [ ] Testato con `python test_dll_simple.py`

---

## 🆘 SE IL PROBLEMA PERSISTE

### **Opzione 1: Contattare il Fornitore**

Chiedi al fornitore del lettore ABK-C2EM-RW:
- Pacchetto SDK completo
- Esempi Python
- Lista completa dipendenze

### **Opzione 2: Usare Software Fornito**

Se il lettore ha software proprietario:
1. Installa il software ufficiale
2. Verifica che funzioni
3. Copia tutte le DLL dal software nella directory del progetto

### **Opzione 3: Driver Alternativo**

Verifica se il lettore supporta:
- **HID** (Human Interface Device) - Nessuna DLL necessaria
- **Serial Port** - Usa `pyserial`
- **Keyboard Emulation** - Legge come tastiera

---

## 📞 INFORMAZIONI NECESSARIE

Per aiutarti meglio, fornisci:

1. **Output di**:
   ```bash
   python check_dll_deps.py
   ```

2. **Architettura**:
   ```bash
   python -c "import sys; print(sys.version)"
   ```

3. **Dependency Walker screenshot** (se possibile)

4. **Contenuto CD/DVD** del lettore (lista file)

---

## 🎯 PROSSIMI PASSI

1. **Installa VC++ Redistributable**
2. **Riavvia PC**
3. **Esegui**:
   ```bash
   python check_dll_deps.py
   python test_dll_simple.py
   ```
4. **Condividi risultato**

---

**GUIDA COMPLETA DIPENDENZE!** 🔧📚
