@echo off
REM ========================================
REM KIOSK HR - Sistema Adeverințe
REM Script di Installazione Automatica
REM Versione: 2.2.0
REM Data: 2026-01-03
REM ========================================

REM Imposta la directory corrente a quella dello script
REM Questo evita problemi quando viene eseguito come amministratore
cd /d "%~dp0"

echo.
echo ========================================
echo   KIOSK HR - Installazione Sistema
echo   Versione 2.2.0
echo ========================================
echo.
echo Directory installazione: %CD%
echo.

REM Verifica privilegi amministratore
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRORE] Questo script richiede privilegi di amministratore.
    echo Fare clic destro e selezionare "Esegui come amministratore"
    pause
    exit /b 1
)

echo [1/8] Verifica Python 3.11...
python --version 2>nul | findstr "3.11" >nul
if %errorLevel% neq 0 (
    echo [ERRORE] Python 3.11 non trovato!
    echo.
    echo Installare Python 3.11 da: https://www.python.org/downloads/
    echo IMPORTANTE: Durante l'installazione selezionare "Add Python to PATH"
    pause
    exit /b 1
)
echo [OK] Python 3.11 trovato

echo.
echo [2/8] Creazione ambiente virtuale...
if exist venv (
    echo [INFO] Ambiente virtuale esistente trovato, lo rimuovo...
    rmdir /s /q venv
)
python -m venv venv
if %errorLevel% neq 0 (
    echo [ERRORE] Impossibile creare ambiente virtuale
    pause
    exit /b 1
)
echo [OK] Ambiente virtuale creato

echo.
echo [3/8] Attivazione ambiente virtuale...
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo [ERRORE] Impossibile attivare ambiente virtuale
    pause
    exit /b 1
)
echo [OK] Ambiente virtuale attivato

echo.
echo [4/8] Aggiornamento pip...
echo [INFO] Questo potrebbe richiedere 30-60 secondi...
REM Usa --no-cache-dir per evitare problemi e mostra output per monitorare
python -m pip install --upgrade pip --no-cache-dir 2>nul
if %errorLevel% neq 0 (
    echo [AVVISO] Aggiornamento pip fallito, procedo con versione attuale
    echo [INFO] Questo non impedisce l'installazione delle dipendenze
) else (
    echo [OK] pip aggiornato
)

echo.
echo [5/8] Installazione dipendenze Python...
echo [INFO] Questo potrebbe richiedere alcuni minuti, attendere...
echo [INFO] Verranno installati: Flask, Pillow, reportlab, pyodbc, ecc.
echo.
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo.
    echo [ERRORE] Installazione dipendenze fallita
    echo [INFO] Verificare la connessione internet e riprovare
    pause
    exit /b 1
)
echo.
echo [OK] Dipendenze installate

echo.
echo [6/8] Verifica file di configurazione...
if not exist "db_config.enc" (
    echo [AVVISO] File db_config.enc non trovato
    echo [INFO] Sarà necessario configurare la connessione al database
)
if not exist "email_credentials.enc" (
    echo [AVVISO] File email_credentials.enc non trovato
    echo [INFO] Sarà necessario configurare le credenziali email
)
if not exist "encryption_key.key" (
    echo [AVVISO] File encryption_key.key non trovato
    echo [INFO] Sarà necessario generare le chiavi di crittografia
)
if not exist "email_key.key" (
    echo [AVVISO] File email_key.key non trovato
)
echo [OK] Verifica configurazione completata

echo.
echo [7/8] Creazione directory necessarie...
if not exist "temp" mkdir temp
if not exist "Images" mkdir Images
echo [OK] Directory create

echo.
echo [8/8] Verifica componenti aggiuntivi...
if not exist "IDReader.dll" (
    echo [AVVISO] IDReader.dll non trovato - Lettore RFID non disponibile
)
if not exist "DejaVuSans.ttf" (
    echo [AVVISO] Font DejaVuSans.ttf non trovato
)
if not exist "DejaVuSans-Bold.ttf" (
    echo [AVVISO] Font DejaVuSans-Bold.ttf non trovato
)
if not exist "logo.png" (
    echo [AVVISO] logo.png non trovato
)
if not exist "GTMC.png" (
    echo [AVVISO] GTMC.png non trovato
)
echo [OK] Verifica componenti completata

echo.
echo ========================================
echo   INSTALLAZIONE COMPLETATA!
echo ========================================
echo.
echo Prossimi passi:
echo.
echo 1. Configurare la connessione al database (se necessario)
echo    Eseguire: python setup.py
echo.
echo 2. Avviare l'applicazione:
echo    Eseguire: START_APP.bat
echo.
echo 3. Per modalità Kiosk fullscreen:
echo    Eseguire: START_SISTEMA_KIOSK.bat
echo.
echo 4. Consultare README.md per maggiori informazioni
echo.
echo ========================================
echo.

pause
