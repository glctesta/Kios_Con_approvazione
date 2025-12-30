@echo off
REM ========================================
REM   Setup Python 3.11 e Firma Digitale
REM ========================================

echo.
echo ========================================
echo   Setup Ambiente Python 3.11
echo ========================================
echo.

REM Vai alla cartella del progetto
cd /d "%~dp0"

echo [1/6] Verifica versione Python...
python --version
echo.

echo [2/6] Elimina vecchio ambiente virtuale...
if exist venv (
    rmdir /s /q venv
    echo Ambiente virtuale eliminato.
) else (
    echo Nessun ambiente virtuale da eliminare.
)
echo.

echo [3/6] Crea nuovo ambiente virtuale con Python 3.11...
python -m venv venv
if errorlevel 1 (
    echo ERRORE: Impossibile creare ambiente virtuale!
    echo Verifica che Python 3.11 sia installato.
    pause
    exit /b 1
)
echo Ambiente virtuale creato.
echo.

echo [4/6] Attiva ambiente virtuale...
call venv\Scripts\activate.bat
echo.

echo [5/6] Aggiorna pip...
python -m pip install --upgrade pip
echo.

echo [6/6] Installa dipendenze...
pip install -r requirements.txt
echo.

echo ========================================
echo   Post-installazione pywin32
echo ========================================
echo.
python -m pywin32_postinstall -install
if errorlevel 1 (
    echo ATTENZIONE: Post-install pywin32 fallito.
    echo Questo potrebbe non essere critico.
)
echo.

echo ========================================
echo   Test Certificati Digitali
echo ========================================
echo.
python digital_signature.py
echo.

echo ========================================
echo   Setup Completato!
echo ========================================
echo.
echo Prossimi passi:
echo 1. Verifica che i certificati siano stati trovati
echo 2. Avvia il server con: python app.py
echo 3. Testa la firma digitale
echo.

pause
