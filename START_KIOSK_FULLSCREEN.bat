@echo off
REM ========================================
REM   Avvia Kiosk HR in Modalita' Fullscreen
REM   Chrome Kiosk Mode
REM ========================================

echo.
echo ========================================
echo   Avvio Kiosk HR - Modalita' Fullscreen
echo ========================================
echo.

REM Chiudi eventuali istanze Chrome precedenti
taskkill /F /IM chrome.exe >nul 2>&1

REM Attendi 2 secondi
timeout /t 2 /nobreak >nul

REM Avvia Chrome in modalita' kiosk
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --kiosk-printing http://localhost:5000

echo.
echo Chrome avviato in modalita' kiosk
echo URL: http://localhost:5000
echo.
echo Per uscire: Alt+F4 o Ctrl+Alt+Del
echo.
