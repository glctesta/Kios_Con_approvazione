@echo off
REM ========================================
REM KIOSK HR - Avvio Modalità Kiosk
REM Versione 2.3.3
REM ========================================

echo.
echo ========================================
echo   KIOSK HR - Avvio Sistema
echo ========================================
echo.

REM Avvia app Flask in background
echo [1/2] Avvio server Flask...
start /B python app.py

REM Attendi 5 secondi per far partire il server
echo [2/2] Attesa avvio server (5 secondi)...
timeout /t 5 /nobreak > nul

REM Avvia browser in modalità kiosk
echo [3/3] Apertura browser modalità kiosk...

REM Prova Chrome prima
where chrome.exe >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Browser: Google Chrome
    start chrome.exe --kiosk http://localhost:5000 --start-fullscreen --incognito
    goto :end
)

REM Se Chrome non c'è, usa Edge
where msedge.exe >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Browser: Microsoft Edge
    start msedge.exe --kiosk http://localhost:5000 --edge-kiosk-type=fullscreen
    goto :end
)

REM Fallback a browser di default
echo Browser: Default
start http://localhost:5000

:end
echo.
echo ========================================
echo   Sistema avviato!
echo   Premi ALT+F4 per uscire da kiosk mode
echo ========================================
echo.
pause
