@echo off
REM ========================================
REM   Aggiorna Firma Amministratore
REM ========================================

echo.
echo ========================================
echo   Utility Aggiornamento Firma
echo ========================================
echo.

cd /d "%~dp0"

echo Avvio programma aggiornamento firma...
echo.

python update_signature.py

if errorlevel 1 (
    echo.
    echo ERRORE: Impossibile avviare il programma.
    echo Verifica che Python sia installato e che le dipendenze siano presenti.
    echo.
    pause
    exit /b 1
)

echo.
pause
