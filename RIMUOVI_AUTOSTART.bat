@echo off
REM ============================================================
REM RIMUOVI_AUTOSTART.bat
REM Rimuove il task di avvio automatico dal Task Scheduler
REM e ferma il watchdog in esecuzione.
REM ============================================================

echo.
echo ============================================================
echo   KIOSK HR - RIMOZIONE AVVIO AUTOMATICO
echo ============================================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRORE] Questo script deve essere eseguito come Amministratore!
    pause
    exit /b 1
)

set "TASK_NAME=KioskHR_Watchdog"

REM Ferma il task se in esecuzione
echo Arresto del watchdog in esecuzione...
schtasks /end /tn "%TASK_NAME%" >nul 2>&1

REM Termina anche eventuali processi Python del kiosk
echo Terminazione processi Flask/watchdog...
taskkill /f /fi "WINDOWTITLE eq kiosk_watchdog*" >nul 2>&1
for /f "tokens=2" %%p in ('wmic process where "commandline like '%%kiosk_watchdog%%'" get processid /format:list 2^>nul ^| findstr "="') do (
    taskkill /f /pid %%p >nul 2>&1
)
for /f "tokens=2" %%p in ('wmic process where "commandline like '%%app.py%%'" get processid /format:list 2^>nul ^| findstr "="') do (
    taskkill /f /pid %%p >nul 2>&1
)

REM Rimuovi il task
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorLevel% equ 0 (
    schtasks /delete /tn "%TASK_NAME%" /f
    echo Task '%TASK_NAME%' rimosso.
) else (
    echo Task '%TASK_NAME%' non trovato ^(gia' rimosso^).
)

echo.
echo ============================================================
echo   AVVIO AUTOMATICO DISABILITATO
echo ============================================================
echo.
echo Il server Kiosk HR non partira' piu' automaticamente.
echo Per riabilitarlo esegui: INSTALLA_AUTOSTART.bat
echo.
pause
