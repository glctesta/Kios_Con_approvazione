@echo off
REM ========================================
REM   Avvio Applicazione Kiosk Angajați
REM ========================================

echo.
echo ========================================
echo   Sistema Kiosk Angajati
echo ========================================
echo.

REM Vai alla cartella dello script (dove si trova questo .bat)
cd /d "%~dp0"

echo Cartella corrente: %CD%
echo.

REM Verifica che i file necessari esistano
if not exist "app.py" (
    echo ERRORE: app.py non trovato!
    echo Assicurati di essere nella cartella corretta.
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERRORE: requirements.txt non trovato!
    echo.
    pause
    exit /b 1
)

REM Verifica Python
echo [1/4] Verifica Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato!
    echo Installa Python 3.11 o superiore.
    echo.
    pause
    exit /b 1
)
python --version
echo.

REM Verifica dipendenze
echo [2/4] Verifica dipendenze...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask non installato. Installazione dipendenze...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERRORE: Installazione dipendenze fallita!
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Dipendenze installate con successo!
) else (
    echo Dipendenze OK
)
echo.

REM Verifica configurazione database
echo [3/4] Verifica configurazione...
if not exist "db_config.enc" (
    echo ATTENZIONE: db_config.enc non trovato!
    echo Esegui setup.py per configurare il database.
    echo.
    choice /C SN /M "Vuoi eseguire setup ora? (S/N)"
    if errorlevel 2 goto skip_setup
    if errorlevel 1 (
        python setup.py
        if errorlevel 1 (
            echo Setup fallito!
            pause
            exit /b 1
        )
    )
)
:skip_setup
echo Configurazione OK
echo.

REM Avvia server
echo [4/4] Avvio server Flask...
echo.
echo ========================================
echo   Server in esecuzione su:
echo   http://localhost:3000
echo ========================================
echo.
echo Apri il browser e vai a: http://localhost:3000
echo.
echo Premi Ctrl+C per fermare il server
echo.

REM Forza encoding UTF-8 per caratteri rumeni/Unicode (ș, ț, â, etc.)
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM Avvia Python con percorso assoluto
python "%~dp0app.py"

REM Se il server si ferma
echo.
echo Server fermato.
pause
