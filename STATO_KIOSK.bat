@echo off
REM ============================================================
REM STATO_KIOSK.bat
REM Mostra lo stato attuale del server Kiosk HR:
REM   - Task Scheduler (autostart)
REM   - Processo watchdog
REM   - Processo Flask (app.py)
REM   - Ultime righe del log watchdog
REM ============================================================

echo.
echo ============================================================
echo   KIOSK HR - STATO DEL SISTEMA
echo ============================================================
echo.

set "TASK_NAME=KioskHR_Watchdog"
set "KIOSK_DIR=%~dp0"
if "%KIOSK_DIR:~-1%"=="\" set "KIOSK_DIR=%KIOSK_DIR:~0,-1%"

REM --- Task Scheduler ---
echo [1] Task Scheduler (avvio automatico)
echo ------------------------------------------
schtasks /query /tn "%TASK_NAME%" /fo LIST 2>nul | findstr /i "TaskName Status Last Run Next Run"
if %errorLevel% neq 0 (
    echo     TASK NON INSTALLATO
    echo     Esegui INSTALLA_AUTOSTART.bat per abilitarlo
)
echo.

REM --- Processo watchdog ---
echo [2] Processo Watchdog
echo ------------------------------------------
set "WATCHDOG_RUNNING=NO"
for /f "tokens=1,2" %%a in ('wmic process where "commandline like '%%kiosk_watchdog%%'" get name^,processid /format:csv 2^>nul ^| findstr /v "Node"') do (
    echo     ATTIVO - PID: %%b  (%%a)
    set "WATCHDOG_RUNNING=SI"
)
if "%WATCHDOG_RUNNING%"=="NO" (
    echo     NON IN ESECUZIONE
)
echo.

REM --- Processo Flask ---
echo [3] Server Flask (app.py)
echo ------------------------------------------
set "FLASK_RUNNING=NO"
for /f "tokens=1,2" %%a in ('wmic process where "commandline like '%%app.py%%'" get name^,processid /format:csv 2^>nul ^| findstr /v "Node"') do (
    echo     ATTIVO - PID: %%b  (%%a)
    set "FLASK_RUNNING=SI"
)
if "%FLASK_RUNNING%"=="NO" (
    echo     NON IN ESECUZIONE
)
echo.

REM --- Porta 5000 ---
echo [4] Porta 5000 (Flask listener)
echo ------------------------------------------
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorLevel% equ 0 (
    echo     IN ASCOLTO - Server raggiungibile
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do echo     PID: %%p
) else (
    echo     NON IN ASCOLTO - Server non risponde su porta 5000
)
echo.

REM --- Log watchdog (ultime 15 righe) ---
echo [5] Ultime righe log watchdog
echo ------------------------------------------
set "LOG_FILE=%KIOSK_DIR%\kiosk_watchdog.log"
if exist "%LOG_FILE%" (
    powershell -NoProfile -Command "Get-Content '%LOG_FILE%' -Tail 15"
) else (
    echo     Log non trovato: %LOG_FILE%
)
echo.
echo ============================================================
echo.
pause
