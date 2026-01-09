@echo off
REM ========================================
REM AVVIO SERVIZIO REPORT KIOSK HR
REM ========================================
REM Avvia il servizio di generazione report mensili
REM per il monitoraggio dell'utilizzo del Kiosk

echo ========================================
echo KIOSK HR - SERVIZIO REPORT MENSILI
echo ========================================
echo.

REM Vai alla directory dello script
cd /d "%~dp0"

REM Verifica che esista l'ambiente virtuale
if not exist "venv\Scripts\activate.bat" (
    echo [ERRORE] Ambiente virtuale non trovato!
    echo Eseguire prima INSTALLA.bat
    pause
    exit /b 1
)

REM Attiva ambiente virtuale
echo [INFO] Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

REM Verifica che esista il file del servizio
if not exist "service_kiosk_reports.py" (
    echo [ERRORE] File service_kiosk_reports.py non trovato!
    pause
    exit /b 1
)

echo [INFO] Avvio servizio report...
echo.
echo Il servizio inviera' report mensili ogni 1° del mese alle 08:00
echo Destinatari:
echo  - Gianluca.Testa@Vandewiele.com
echo  - Cornelia.Ormenisan@Vandewiele.com
echo.
echo Premere CTRL+C per interrompere il servizio
echo.
echo ========================================
echo.

REM Avvia il servizio
python service_kiosk_reports.py

REM Se il servizio termina, mostra messaggio
echo.
echo ========================================
echo Servizio terminato
echo ========================================
pause
