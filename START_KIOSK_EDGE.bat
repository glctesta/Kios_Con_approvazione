@echo off
REM ========================================
REM   Avvia Kiosk HR in Modalita' Fullscreen
REM   Microsoft Edge Kiosk Mode
REM ========================================

echo.
echo ========================================
echo   Avvio Kiosk HR - Edge Fullscreen
echo ========================================
echo.

REM Chiudi eventuali istanze Edge precedenti
taskkill /F /IM msedge.exe >nul 2>&1

REM Attendi 2 secondi
timeout /t 2 /nobreak >nul

REM Avvia Edge in modalita' kiosk
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk http://localhost:3000 --edge-kiosk-type=fullscreen

echo.
echo Edge avviato in modalita' kiosk
echo URL: http://localhost:3000
echo.
echo Per uscire: Ctrl+Alt+Del
echo.
