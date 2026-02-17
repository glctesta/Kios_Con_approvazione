@echo off
REM ========================================
REM Installazione Kiosk Reports Service
REM ========================================

echo.
echo ========================================
echo KIOSK REPORTS SERVICE - INSTALLAZIONE
echo ========================================
echo.

REM Verifica privilegi amministratore
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRORE: Questo script richiede privilegi di amministratore!
    echo Esegui come amministratore e riprova.
    pause
    exit /b 1
)

REM Ottieni directory corrente
set "SERVICE_DIR=%~dp0"
set "SERVICE_EXE=%SERVICE_DIR%dist\KioskReportsService.exe"

echo Directory servizio: %SERVICE_DIR%
echo Eseguibile: %SERVICE_EXE%
echo.

REM Verifica esistenza eseguibile
if not exist "%SERVICE_EXE%" (
    echo ERRORE: Eseguibile non trovato!
    echo Esegui prima: build_service.bat
    pause
    exit /b 1
)

REM Ferma servizio se già in esecuzione
echo Controllo servizio esistente...
sc query KioskReportsService >nul 2>&1
if %errorLevel% equ 0 (
    echo Servizio esistente trovato. Arresto in corso...
    net stop KioskReportsService
    timeout /t 2 >nul
    
    echo Rimozione servizio esistente...
    sc delete KioskReportsService
    timeout /t 2 >nul
)

REM Installa il servizio
echo.
echo Installazione servizio...
"%SERVICE_EXE%" --startup=auto install

if %errorLevel% neq 0 (
    echo ERRORE: Installazione fallita!
    pause
    exit /b 1
)

REM Configura descrizione servizio
sc description KioskReportsService "Servizio automatico per l'invio di report mensili sull'utilizzo del Kiosk HR. Invia statistiche il primo giorno di ogni mese alle 08:00."

REM Configura recovery del servizio (riavvio automatico in caso di errore)
sc failure KioskReportsService reset= 86400 actions= restart/60000/restart/60000/restart/60000

REM Avvia il servizio
echo.
echo Avvio servizio...
net start KioskReportsService

if %errorLevel% neq 0 (
    echo ATTENZIONE: Il servizio è installato ma non è partito.
    echo Controlla i log per dettagli.
) else (
    echo.
    echo ========================================
    echo INSTALLAZIONE COMPLETATA CON SUCCESSO!
    echo ========================================
    echo.
    echo Il servizio è ora in esecuzione e invierà
    echo automaticamente i report il 1° di ogni mese alle 08:00.
    echo.
    echo Comandi utili:
    echo   - Ferma servizio:  net stop KioskReportsService
    echo   - Avvia servizio:  net start KioskReportsService
    echo   - Stato servizio:  sc query KioskReportsService
    echo.
)

pause
