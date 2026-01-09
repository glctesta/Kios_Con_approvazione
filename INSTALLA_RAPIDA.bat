@echo off
REM ========================================
REM KIOSK HR - Sistema Adeverințe
REM Script di Installazione RAPIDA (senza aggiornamento pip)
REM Versione: 2.2.0
REM Usare questo se INSTALLA.bat si blocca
REM ========================================

REM Imposta la directory corrente a quella dello script
cd /d "%~dp0"

echo.
echo ========================================
echo   KIOSK HR - Installazione RAPIDA
echo   Versione 2.2.0
echo   (senza aggiornamento pip)
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

echo [1/6] Verifica Python 3.11...
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
echo [2/6] Creazione ambiente virtuale...
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
echo [3/6] Attivazione ambiente virtuale...
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo [ERRORE] Impossibile attivare ambiente virtuale
    pause
    exit /b 1
)
echo [OK] Ambiente virtuale attivato

echo.
echo [4/6] SKIP aggiornamento pip (modalità rapida)
echo [INFO] Verrà usata la versione pip già presente
echo.

echo.
echo [5/6] Installazione dipendenze Python...
echo [INFO] Questo potrebbe richiedere alcuni minuti, attendere...
echo [INFO] Verranno installati: Flask, Pillow, reportlab, pyodbc, ecc.
echo.
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo.
    echo [ERRORE] Installazione dipendenze fallita
    echo [INFO] Verificare la connessione internet e riprovare
    echo.
    echo [SUGGERIMENTO] Se il problema persiste, provare ad installare manualmente:
    echo   venv\Scripts\activate
    echo   pip install Flask Pillow reportlab pyodbc requests schedule loguru cryptography pytz keyring
    pause
    exit /b 1
)
echo.
echo [OK] Dipendenze installate

echo.
echo [6/6] Creazione directory necessarie...
if not exist "temp" mkdir temp
if not exist "Images" mkdir Images
echo [OK] Directory create

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
echo 3. Consultare README.md per maggiori informazioni
echo.
echo ========================================
echo.

pause
