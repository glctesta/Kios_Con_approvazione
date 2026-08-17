@echo off
REM ============================================================
REM INSTALLA_AUTOSTART.bat
REM Registra il Kiosk HR Watchdog nel Task Scheduler di Windows
REM in modo che parta automaticamente ad ogni avvio del sistema,
REM anche dopo un'interruzione di corrente.
REM
REM RICHIEDE: privilegi di Amministratore
REM ============================================================

setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo   KIOSK HR - INSTALLAZIONE AVVIO AUTOMATICO
echo ============================================================
echo.

REM --- Verifica privilegi amministratore ---
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRORE] Questo script deve essere eseguito come Amministratore!
    echo Fai clic destro sul file ^> "Esegui come amministratore"
    echo.
    pause
    exit /b 1
)

REM --- Percorsi ---
set "KIOSK_DIR=%~dp0"
REM Rimuovi backslash finale se presente
if "%KIOSK_DIR:~-1%"=="\" set "KIOSK_DIR=%KIOSK_DIR:~0,-1%"

set "WATCHDOG_SCRIPT=%KIOSK_DIR%\kiosk_watchdog.py"
set "TASK_NAME=KioskHR_Watchdog"
set "TASK_DESCR=Kiosk HR - Avvio automatico server Flask con watchdog. Riparte dopo interruzione corrente."

REM Trova Python (prima venv, poi sistema)
set "PYTHON_EXE="
if exist "%KIOSK_DIR%\venv\Scripts\pythonw.exe" (
    set "PYTHON_EXE=%KIOSK_DIR%\venv\Scripts\pythonw.exe"
) else if exist "%KIOSK_DIR%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%KIOSK_DIR%\venv\Scripts\python.exe"
) else (
    for /f "delims=" %%i in ('where pythonw.exe 2^>nul') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)
if not defined PYTHON_EXE (
    for /f "delims=" %%i in ('where python.exe 2^>nul') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)

if not defined PYTHON_EXE (
    echo [ERRORE] Python non trovato!
    echo Installa Python oppure crea il venv nella cartella del progetto.
    pause
    exit /b 1
)

echo Directory Kiosk  : %KIOSK_DIR%
echo Watchdog script  : %WATCHDOG_SCRIPT%
echo Python           : %PYTHON_EXE%
echo Task Scheduler   : %TASK_NAME%
echo.

REM --- Verifica watchdog ---
if not exist "%WATCHDOG_SCRIPT%" (
    echo [ERRORE] File kiosk_watchdog.py non trovato in:
    echo          %WATCHDOG_SCRIPT%
    pause
    exit /b 1
)

REM --- Rimuovi task precedente se esiste ---
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorLevel% equ 0 (
    echo Task esistente trovato. Rimozione in corso...
    schtasks /delete /tn "%TASK_NAME%" /f >nul
    echo Task rimosso.
)

REM --- Crea il task XML per configurazione avanzata ---
set "XML_FILE=%TEMP%\kiosk_task.xml"

(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo   ^<RegistrationInfo^>
echo     ^<Description^>%TASK_DESCR%^</Description^>
echo   ^</RegistrationInfo^>
echo   ^<Triggers^>
echo     ^<BootTrigger^>
echo       ^<Enabled^>true^</Enabled^>
echo       ^<Delay^>PT30S^</Delay^>
echo     ^</BootTrigger^>
echo   ^</Triggers^>
echo   ^<Principals^>
echo     ^<Principal id="Author"^>
echo       ^<LogonType^>S4U^</LogonType^>
echo       ^<RunLevel^>HighestAvailable^</RunLevel^>
echo     ^</Principal^>
echo   ^</Principals^>
echo   ^<Settings^>
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^>
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^>
echo     ^<AllowHardTerminate^>true^</AllowHardTerminate^>
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^>
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^>
echo     ^<IdleSettings^>
echo       ^<StopOnIdleEnd^>false^</StopOnIdleEnd^>
echo       ^<RestartOnIdle^>false^</RestartOnIdle^>
echo     ^</IdleSettings^>
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^>
echo     ^<Enabled^>true^</Enabled^>
echo     ^<Hidden^>false^</Hidden^>
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^>
echo     ^<WakeToRun^>false^</WakeToRun^>
echo     ^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^>
echo     ^<Priority^>7^</Priority^>
echo     ^<RestartOnFailure^>
echo       ^<Interval^>PT1M^</Interval^>
echo       ^<Count^>10^</Count^>
echo     ^</RestartOnFailure^>
echo   ^</Settings^>
echo   ^<Actions Context="Author"^>
echo     ^<Exec^>
echo       ^<Command^>"%PYTHON_EXE%"^</Command^>
echo       ^<Arguments^>"%WATCHDOG_SCRIPT%"^</Arguments^>
echo       ^<WorkingDirectory^>%KIOSK_DIR%^</WorkingDirectory^>
echo     ^</Exec^>
echo   ^</Actions^>
echo ^</Task^>
) > "%XML_FILE%"

REM --- Importa il task ---
schtasks /create /tn "%TASK_NAME%" /xml "%XML_FILE%" /f
del "%XML_FILE%" >nul 2>&1

if %errorLevel% neq 0 (
    echo.
    echo [ERRORE] Registrazione task fallita.
    echo Verifica i privilegi e riprova.
    pause
    exit /b 1
)

REM --- Avvia subito senza aspettare il riavvio ---
echo.
echo Avvio immediato del watchdog...
schtasks /run /tn "%TASK_NAME%"
timeout /t 2 >nul

echo.
echo ============================================================
echo   INSTALLAZIONE COMPLETATA CON SUCCESSO!
echo ============================================================
echo.
echo Il server Kiosk HR si avviera' automaticamente:
echo   - Ad ogni accensione del PC
echo   - Dopo ogni interruzione di corrente
echo   - Se il processo Flask crasha (watchdog lo rilancia)
echo.
echo Task registrato : %TASK_NAME%
echo Log watchdog    : %KIOSK_DIR%\kiosk_watchdog.log
echo.
echo Comandi utili:
echo   Avvia subito  : schtasks /run /tn %TASK_NAME%
echo   Ferma         : schtasks /end /tn %TASK_NAME%
echo   Stato         : schtasks /query /tn %TASK_NAME%
echo   Rimuovi       : esegui RIMUOVI_AUTOSTART.bat
echo.
pause
