@echo off
REM ============================================================
REM CONFIGURA_EMAIL.bat
REM Configura le credenziali SMTP (email + password) in modo sicuro.
REM La password viene salvata cifrata in email_credentials.enc
REM ============================================================
echo.
echo ============================================================
echo   KIOSK HR - CONFIGURAZIONE EMAIL SMTP
echo ============================================================
echo.

set "KIOSK_DIR=%~dp0"
if "%KIOSK_DIR:~-1%"=="\" set "KIOSK_DIR=%KIOSK_DIR:~0,-1%"

REM Trova Python nel venv o nel sistema
set "PYTHON_EXE="
if exist "%KIOSK_DIR%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%KIOSK_DIR%\venv\Scripts\python.exe"
) else (
    for /f "delims=" %%i in ('where python.exe 2^>nul') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)

if not defined PYTHON_EXE (
    echo [ERRORE] Python non trovato. Installa Python o crea il venv.
    pause
    exit /b 1
)

"%PYTHON_EXE%" "%KIOSK_DIR%\setup_email_credentials.py"
pause
