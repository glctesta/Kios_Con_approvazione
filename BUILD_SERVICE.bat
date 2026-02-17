@echo off
REM ========================================
REM Build Kiosk Reports Service Executable
REM ========================================

echo.
echo ========================================
echo KIOSK REPORTS SERVICE - BUILD
echo ========================================
echo.

REM Verifica installazione PyInstaller
python -c "import PyInstaller" 2>nul
if %errorLevel% neq 0 (
    echo PyInstaller non trovato. Installazione in corso...
    pip install pyinstaller
    if %errorLevel% neq 0 (
        echo ERRORE: Impossibile installare PyInstaller!
        pause
        exit /b 1
    )
)

REM Verifica installazione pywin32
python -c "import win32serviceutil" 2>nul
if %errorLevel% neq 0 (
    echo pywin32 non trovato. Installazione in corso...
    pip install pywin32
    if %errorLevel% neq 0 (
        echo ERRORE: Impossibile installare pywin32!
        pause
        exit /b 1
    )
    
    REM Configura pywin32
    echo Configurazione pywin32...
    python -c "import win32api"
)

REM Pulisci build precedenti
echo Pulizia build precedenti...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build con PyInstaller
echo.
echo Build in corso...
pyinstaller build_service.spec

if %errorLevel% neq 0 (
    echo.
    echo ERRORE: Build fallita!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETATA CON SUCCESSO!
echo ========================================
echo.
echo Eseguibile creato in: dist\KioskReportsService.exe
echo.
echo Prossimi passi:
echo   1. Esegui INSTALL_SERVICE.bat come amministratore
echo   2. Verifica il servizio con: sc query KioskReportsService
echo.

pause
