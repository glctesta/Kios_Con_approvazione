@echo off
REM ========================================
REM Disinstallazione Kiosk Reports Service
REM ========================================

echo.
echo ========================================
echo KIOSK REPORTS SERVICE - DISINSTALLAZIONE
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
echo.

REM Verifica se il servizio esiste
sc query KioskReportsService >nul 2>&1
if %errorLevel% neq 0 (
    echo Il servizio non è installato.
    pause
    exit /b 0
)

REM Ferma il servizio
echo Arresto servizio...
net stop KioskReportsService
timeout /t 2 >nul

REM Rimuovi il servizio
echo Rimozione servizio...
if exist "%SERVICE_EXE%" (
    "%SERVICE_EXE%" remove
) else (
    sc delete KioskReportsService
)

if %errorLevel% neq 0 (
    echo ERRORE: Rimozione fallita!
    pause
    exit /b 1
)

echo.
echo ========================================
echo DISINSTALLAZIONE COMPLETATA!
echo ========================================
echo.

pause
