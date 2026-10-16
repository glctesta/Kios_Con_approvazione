@echo off
REM ============================================================
REM RIMUOVI_AUTOSTART.bat  (v2 - SENZA DIRITTI DI AMMINISTRATORE)
REM ------------------------------------------------------------
REM Rimuove la ripartenza automatica del kiosk HR:
REM   - valore KioskHR_Autostart dalla chiave HKCU\...\Run
REM   - file KioskHR_Autostart.vbs da 'Esecuzione automatica'
REM   - vecchio task schedulato KioskHR_Watchdog (se presente)
REM Su richiesta, arresta anche i processi del kiosk in esecuzione.
REM Nessun privilegio di amministratore richiesto.
REM ============================================================

setlocal EnableDelayedExpansion
set "INSTALL_LOG=%~dp0logs\autostart_install.log"

echo.
echo ============================================================
echo   KIOSK HR - RIMOZIONE AVVIO AUTOMATICO (senza admin)
echo ============================================================
echo.

set "RUN_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "RUN_VALUE=KioskHR_Autostart"
set "STARTUP_VBS=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\KioskHR_Autostart.vbs"

REM --- 1) Valore di registro HKCU Run ---
echo [1/4] Rimozione chiave di registro...
reg delete "%RUN_KEY%" /v %RUN_VALUE% /f >nul 2>&1
reg query "%RUN_KEY%" /v %RUN_VALUE% >nul 2>&1
if %errorLevel% equ 0 (
    echo [ERRORE] Il valore di registro risulta ancora presente!
) else (
    echo [OK] Valore %RUN_VALUE% rimosso da HKCU\...\Run.
)

REM --- 2) File in Esecuzione automatica ---
echo [2/4] Rimozione file da 'Esecuzione automatica'...
if exist "%STARTUP_VBS%" (
    del /f /q "%STARTUP_VBS%" >nul 2>&1
    if exist "%STARTUP_VBS%" (
        echo [ERRORE] Impossibile eliminare %STARTUP_VBS%
    ) else (
        echo [OK] File KioskHR_Autostart.vbs eliminato.
    )
) else (
    echo [OK] Nessun file da rimuovere ^(gia' assente^).
)

REM --- 3) Vecchio task amministrativo (se presente) ---
echo [3/4] Controllo vecchio task 'KioskHR_Watchdog'...
schtasks /query /tn "KioskHR_Watchdog" >nul 2>&1
if %errorLevel% equ 0 (
    schtasks /delete /tn "KioskHR_Watchdog" /f >nul 2>&1
    if !errorLevel! equ 0 (
        echo [OK] Task rimosso.
    ) else (
        echo [AVVISO] Task presente ma non rimovibile senza admin. Rimuoverlo con:
        echo          schtasks /delete /tn KioskHR_Watchdog /f   ^(come admin^)
    )
) else (
    echo [OK] Nessun vecchio task presente.
)

REM --- 4) Arresto processi kiosk (opzionale) ---
echo [4/4] Arresto processi in esecuzione...
choice /C SN /M "Arrestare ora supervisore/server kiosk (S/N)"
if errorlevel 2 goto :skip_stop

REM Termina supervisore, vecchio watchdog e server Flask (Get-CimInstance:
REM wmic non e' piu' disponibile sulle versioni recenti di Windows)
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe' OR Name='python.exe'\" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'kiosk_supervisor|kiosk_watchdog|app[.]py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1
echo [OK] Supervisore e server Flask arrestati.

choice /C SN /M "Chiudere anche il browser kiosk Chrome/Edge (S/N)"
if errorlevel 2 goto :skip_stop
taskkill /F /IM chrome.exe >nul 2>&1
taskkill /F /IM msedge.exe >nul 2>&1
echo [OK] Browser chiusi.

:skip_stop
if exist "%~dp0logs" echo [%date% %time%] REMOVE autostart >> "%INSTALL_LOG%"

echo.
echo ============================================================
echo   AVVIO AUTOMATICO DISABILITATO
echo ============================================================
echo.
echo Il kiosk HR non partira' piu' automaticamente al logon.
echo Per riabilitarlo esegui: INSTALLA_AUTOSTART.bat
echo.
pause
