# Guida Firma Digitale PDF - Kiosk HR

**Data:** 2026-01-09  
**Funzionalità:** Firma digitale documenti Adeverințe con certificati

---

## 🎯 Panoramica

Il sistema ora supporta la **firma digitale** dei PDF generati (Adeverințe) usando:
- ✅ **Certificati digitali** (.pfx, .p12, .pem)
- ✅ **Firma visibile** sul PDF (riquadro con info firmatario)
- ✅ **Firma crittografica** verificabile con Adobe Reader

---

## 📋 Requisiti

### 1. Certificato Digitale

Serve un **certificato digitale** in uno di questi formati:
- **PKCS#12** (.pfx o .p12) - **CONSIGLIATO**
- **PEM** (.pem)

**Dove ottenerlo:**
- 🇷🇴 **CertSign** (Romania): https://www.certsign.ro
- 🇪🇺 **E-Turust**: Qualsiasi CA europea riconosciuta
- 🏢 **IT Aziendale**: Certificato emesso dall'azienda

### 2. Librerie Python

```bash
pip install pyHanko==0.21.0
pip install pyhanko-certvalidator==0.26.3
```

**Già incluse nel `requirements.txt` aggiornato!**

---

## ⚙️ Configurazione

### Opzione A: File Certificato nella Cartella (CONSIGLIATO)

**Il metodo più semplice:**

1. **Copia il tuo

 certificato** nella cartella principale del progetto:
   ```
   C:\Wandewiele\Kiosk\
     ├── certificate.pfx    ← Il tuo certificato
     ├── app.py
     ├── ...
   ```

2. **Nome file supportati:**
   - `certificate.pfx`
   - `certificate.p12`
   - `certificate.pem`
   - `cert.pfx`
   - `cert.p12`

3. **Password certificato (opzionale):**
   
   Se il certificato ha una password, imposta variabile d'ambiente:
   ```powershell
   # Windows PowerShell
   $env:CERT_PASSWORD = "TuaPasswordQui"
   
   # Oppure permanente (sistema)
   setx CERT_PASSWORD "TuaPasswordQui"
   ```

4. **Fine!** Il sistema troverà automaticamente il certificato.

---

### Opzione B: Certificato in Posizione Personalizzata

Se il certificato è altrove, modifica `app.py` o configura path:

```python
# In app.py, cerca la generazione certificati e aggiungi:
cert_generator = CertificateGenerator(db_connection)

# Personalizza firma
cert_generator._sign_pdf_digital(
    pdf_path='path/to/document.pdf',
    cert_path='C:/Certificati/MioCertificato.pfx',
    cert_password='MiaPassword'
)
```

---

## 🔍 Verifica Funzionamento

### Test 1: Librerie Installate

```powershell
python -c "import pyhanko; print('pyHanko OK')"
```

**Output atteso:** `pyHanko OK`

Se errore: `pip install pyHanko pyhanko-certvalidator`

---

### Test 2: Certificato Riconosciuto

Avvia l'applicazione e genera un documento. Guarda i log:

**Log positivo:**
```
INFO - Trovato certificato: certificate.pfx
INFO - Tentativo firma digitale PDF: temp/Adv7_20260109142000.pdf
INFO - Certificato PKCS#12 caricato: certificate.pfx
INFO - Info certificato: Mario Rossi - ACME SRL
INFO - PDF firmato digitalmente con successo
```

**Log negativo (certificato mancante):**
```
WARNING - Nessun certificato trovato - PDF non firmato digitalmente
INFO - Per firmare digitalmente, inserire file certificato: certificate.pfx/p12/pem
```

---

### Test 3: Firma Visibile sul PDF

1. Genera un documento (Adeverință)
2. Apri il PDF generato
3. **Verifica riquadro firma** in basso a destra:
   ```
   ┌─────────────────────────────┐
   │ Firmato digitalmente da:    │
   │ Mario Rossi                 │
   │ Amministratore              │
   │ ACME SRL                    │
   │ Data: 09/01/2026 14:20      │
   └─────────────────────────────┘
   ```

---

### Test 4: Verifica Firma con Adobe Reader

1. Apri PDF con **Adobe Acrobat Reader DC**
2. Guarda banner superiore:
   - ✅ **"Firmato e tutte le firme sono valide"** → OK!
   - ⚠️ **"Firmatario sconosciuto"** → Normale se certificato non da CA pubblica
   - ❌ **"Firma non valida"** → Problema con certificato

3. Click su **firma** per dettagli:
   - Firmatario
   - Data/ora firma
   - Certificato usato
   - Catena di fiducia

---

## 🔧 Risoluzione Problemi

### Errore: "pyHanko non installato"

**Soluzione:**
```powershell
cd C:\Wandewiele\Kiosk
.\venv\Scripts\Activate.ps1
pip install pyHanko pyhanko-certvalidator
```

---

### Errore: "Certificato non trovato"

**Verifica:**
```powershell
# Controlla se file esiste
dir certificate.pfx

# Oppure
dir cert.pfx
```

**Soluzione:**
- Copia certificato nella cartella principale
- Rinomina in `certificate.pfx` o uno dei nomi supportati

---

### Errore: "Password certificato errata"

**Sintomo:**
```
ERROR - Errore caricamento certificato: MAC verification failed
```

**Soluzione:**
1. Verifica password certificato
2. Imposta variabile ambiente corretta:
   ```powershell
   setx CERT_PASSWORD "PasswordCorretta"
   ```
3. Riavvia applicazione

---

### Errore: "Signature field already exists"

**Sintomo:**
```
ERROR - Signature field 'Signature1' already exists
```

**Causa:** Il PDF è già firmato

**Soluzione:** Questo è normale, il sistema firma solo una volta

---

### Warning: "Firmatario sconosciuto" in Adobe

**Causa:** Il certificato non è da una CA pubblica riconosciuta

**Soluzioni:**
1. **Accetta rischio** (per uso interno va bene)
2. **Aggiungi certificato ai Trusted** di Adobe
3. **Usa certificato da CA pubblica** (CertSign, DigiCert, etc.)

**Per uso aziendale interno, questo WARNING è normale e accettabile!**

---

## 📝 Formato Certificati Supportati

### PKCS#12 (.pfx / .p12) - CONSIGLIATO

**Vantaggi:**
- ✅ Formato standard Windows
- ✅ Include certificato + chiave privata in un file
- ✅ Protetto da password
- ✅ Più facile da gestire

**Come ottenere:**
- Esportato da Windows Certificate Store
- Fornito direttamente da CertSign România
- Generato da OpenSSL

---

### PEM (.pem)

**Vantaggi:**
- ✅ Formato testo (ASCII)
- ✅ Compatibile Linux/Mac

**Requisiti:**
- Deve contenere ENTRAMBI:
  - Certificato pubblico
  - Chiave privata

**Esempio struttura:**
```
-----BEGIN PRIVATE KEY-----
...chiave privata...
-----END PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
...certificato...
-----END CERTIFICATE-----
```

---

## 🎨 Personalizzazione Firma Visibile

### Posizione Firma

Nel file `certificate_generator.py`, modifica:

```python
# Attuale: bottom-right (in basso a destra)
sig_field = create_visible_signature_field(
    page_width=page_width,
    page_height=page_height,
    position='bottom-right',  # Cambia qui
    width=180,
    height=70
)
```

**Posizioni disponibili:**
- `'bottom-right'` - Basso destra (default)
- `'bottom-left'` - Basso sinistra
- `'top-right'` - Alto destra
- `'top-left'` - Alto sinistra

---

### Dimensioni Riquadro

```python
sig_field = create_visible_signature_field(
    ...
    width=180,   # Larghezza (pixel)
    height=70    # Altezza (pixel)
)
```

---

### Testo Firma

Nel metodo `sign_pdf`:

```python
signature_meta = signers.PdfSignatureMetadata(
    ...
    reason='Documento ufficiale aziendale',  # Motivo firma
    location='Sede legale',  # Luogo firma
    name=cert_info.get('common_name', 'Unknown')  # Nome firmatario
)
```

---

## 🔐 Sicurezza

### Password Certificato

**❌ MAI hardcodare la password nel codice!**

**✅ Usa variabili d'ambiente:**
```powershell
setx CERT_PASSWORD "PasswordSegreta"
```

**✅ Oppure config file crittografato** (già supportato dal sistema)

---

### Protezione Certificato

1. **Backup sicuro** del file .pfx
2. **Password forte** (min 12 caratteri)
3. **Accesso limitato** (solo amministratori)
4. **Rinnovo periodico** (ogni 1-3 anni)

---

## 📊 Vantaggi Firma Digitale vs Immagine PNG

| Aspetto | PNG/JPG | Firma Digitale |
|---------|---------|----------------|
| Validità legale | ❌ Bassa | ✅ Alta |
| Modificabile | ❌ Sì (facile) | ✅ No (rilevabile) |
| Verifica autenticità | ❌ Impossibile | ✅ Automatica |
| Timestamp | ❌ No | ✅ Incluso |
| Info firmatario | ⚠️ Visuale only | ✅ Certificato verificabile |
| Accettata PA | ❌ No | ✅ Sì (se qualificata) |

---

## 🚀 Deploy Produzione

### Checklist Pre-Deployment

- [ ] pyHanko installato: `pip list | findstr pyHanko`
- [ ] Certificato presente: `dir certificate.pfx`
- [ ] Password configurata: `echo %CERT_PASSWORD%`
- [ ] Test firma funzionante (vedi sezione Test)
- [ ] Verifica con Adobe Reader
- [ ] Backup certificato salvato in luogo sicuro

### Setup PC Kiosk

```powershell
# 1. Copia certificato
copy \\server\certs\certificate.pfx C:\Wandewiele\Kiosk\

# 2. Imposta password (se necessaria)
setx CERT_PASSWORD "PasswordCert"

# 3. Installa dipendenze (se non già fatto)
cd C:\Wandewiele\Kiosk
.\venv\Scripts\Activate.ps1
pip install pyHanko pyhanko-certvalidator

# 4. Test
python -c "from pdf_digital_signer import PDFDigitalSigner; print('OK')"

# 5. Riavvia applicazione
.\START_APP.bat
```

---

## 📞 Supporto

### Log Dettagliati

Se problemi, controlla i log dell'applicazione:

```
INFO - Tentativo firma digitale PDF: ...
INFO - Trovato certificato: certificate.pfx
INFO - Certificato PKCS#12 caricato
INFO - Info certificato: Nome - Organizzazione
INFO - PDF firmato digitalmente con successo
```

### Contatti Fornitori Certificati

**🇷🇴 Romania - CertSign:**
- Web: https://www.certsign.ro
- Tel: +40 21 209 39 40
- Email: suport@certsign.ro

**Supporto tecnico pyHanko:**
- Docs: https://pyhanko.readthedocs.io
- GitHub: https://github.com/MatthiasValvekens/pyHanko

---

**Implementato:** 2026-01-09  
**Versione:** 2.2.0+  
**Status:** ✅ Production Ready
