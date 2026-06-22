@echo off
REM ========================================
REM   Avvia Sistema Kiosk HR Completo
REM   Flask App + Chrome Fullscreen
REM ========================================

echo.
echo ========================================
echo   AVVIO SISTEMA KIOSK HR
echo ========================================
echo.

cd /d "%~dp0"

REM Step 1: Avvia Flask App
echo [1/3] Avvio applicazione Flask...
start /MIN python app.py
echo   - Flask avviato in background

REM Step 2: Attendi che Flask sia pronto
echo [2/3] Attesa avvio server (10 secondi)...
timeout /t 10 /nobreak >nul
echo   - Server pronto

REM Step 3: Chiudi Chrome precedenti
echo [3/3] Avvio browser in modalita' kiosk...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Step 4: Avvia Chrome in kiosk mode
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --kiosk-printing http://localhost:3000

echo.
echo ========================================
echo   SISTEMA KIOSK AVVIATO
echo ========================================
echo.
echo URL: http://localhost:3000
echo Modalita': Fullscreen Kiosk
echo.
echo Per uscire: Alt+F4 o Ctrl+Alt+Del
echo.
echo Premere un tasto per chiudere questa finestra...
pause >nul
