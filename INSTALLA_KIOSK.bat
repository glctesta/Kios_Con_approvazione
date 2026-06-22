@echo off
REM ========================================
REM   INSTALLAZIONE KIOSK - PC Destinazione
REM   Esegui questo script sul PC kiosk
REM ========================================

echo.
echo ========================================
echo   INSTALLAZIONE KIOSK ANGAJATI
echo ========================================
echo.

REM Vai alla cartella dello script
cd /d "%~dp0"

echo Cartella installazione: %CD%
echo.

REM Verifica Python
echo [1/5] Verifica Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERRORE: Python non trovato!
    echo.
    echo Installa Python 3.11 da:
    echo https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    echo.
    echo IMPORTANTE: Seleziona "Add Python to PATH" durante installazione
    echo.
    pause
    exit /b 1
)
python --version
echo Python OK
echo.

REM Verifica ODBC Driver
echo [2/5] Verifica ODBC Driver...
powershell -Command "Get-OdbcDriver -Name 'ODBC Driver 18 for SQL Server' -ErrorAction SilentlyContinue" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ATTENZIONE: ODBC Driver 18 non trovato!
    echo.
    echo Scarica da:
    echo https://go.microsoft.com/fwlink/?linkid=2249004
    echo.
    choice /C SN /M "Continua comunque? (S/N)"
    if errorlevel 2 exit /b 1
) else (
    echo ODBC Driver OK
)
echo.

REM Verifica file necessari
echo [3/5] Verifica file applicazione...
set MISSING=0

if not exist "app.py" (
    echo [MANCANTE] app.py
    set MISSING=1
)
if not exist "requirements.txt" (
    echo [MANCANTE] requirements.txt
    set MISSING=1
)
if not exist "logo.png" (
    echo [MANCANTE] logo.png
    set MISSING=1
)
if not exist "templates" (
    echo [MANCANTE] cartella templates
    set MISSING=1
)
if not exist "static" (
    echo [MANCANTE] cartella static
    set MISSING=1
)

if %MISSING%==1 (
    echo.
    echo ERRORE: File mancanti!
    echo Assicurati di aver estratto completamente il file ZIP.
    echo.
    pause
    exit /b 1
)
echo Tutti i file presenti
echo.

REM Installa dipendenze
echo [4/5] Installazione dipendenze Python...
echo Questo potrebbe richiedere alcuni minuti...
echo.

REM Aggiorna pip prima
echo Aggiornamento pip...
python -m pip install --upgrade pip --quiet
echo.

REM Installa dipendenze una per una per gestire meglio errori
echo Installazione Flask...
pip install Flask==3.0.0 Flask-CORS==4.0.0
echo.

echo Installazione database driver...
pip install pyodbc>=5.1.0
echo.

echo Installazione PDF libraries...
pip install reportlab==4.0.7
pip install Pillow --upgrade
pip install PyPDF2>=3.0.0
echo.

echo Installazione utilities...
pip install cryptography>=41.0.0
pip install python-dotenv==1.0.0
pip install pywin32>=306
echo.

echo Dipendenze installate con successo!
echo.

REM Configurazione database
echo [5/5] Configurazione database...
if exist "db_config.enc" (
    echo Configurazione database gia presente
    echo.
    choice /C SN /M "Vuoi riconfigurare? (S/N)"
    if errorlevel 2 goto skip_config
)

echo.
echo Avvio configurazione database...
python setup.py
if errorlevel 1 (
    echo.
    echo ERRORE: Configurazione database fallita!
    echo.
    pause
    exit /b 1
)

:skip_config
echo.
echo ========================================
echo   INSTALLAZIONE COMPLETATA!
echo ========================================
echo.
echo Prossimi passi:
echo.
echo 1. Verifica configurazione stampante (se necessaria)
echo 2. Testa applicazione con: START_APP.bat
echo 3. Apri browser: http://localhost:3000
echo.
echo Per avvio automatico:
echo - Crea collegamento a START_APP.bat
echo - Copia in: shell:startup
echo.
echo ========================================
echo.

choice /C SN /M "Vuoi avviare l'applicazione ora? (S/N)"
if errorlevel 2 goto end
if errorlevel 1 (
    echo.
    echo Avvio applicazione...
    call START_APP.bat
)

:end
echo.
pause
