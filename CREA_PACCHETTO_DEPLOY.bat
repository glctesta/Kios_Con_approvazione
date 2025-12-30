@echo off
REM ========================================
REM   Crea Pacchetto Deployment Kiosk
REM   Versione 2.1 - Gestione Assenze
REM ========================================

echo.
echo ========================================
echo   Preparazione Pacchetto Deployment
echo ========================================
echo.

cd /d "%~dp0"

REM Nome pacchetto con timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set PACKAGE_NAME=Kiosk_Deploy_%datetime:~0,8%_%datetime:~8,6%

echo Creazione pacchetto: %PACKAGE_NAME%.zip
echo.

REM Crea cartella temporanea
if exist deploy_temp rmdir /s /q deploy_temp
mkdir deploy_temp

echo [1/7] Copia file Python...
copy /Y *.py deploy_temp\ >nul 2>&1
echo   - File .py copiati

echo [2/7] Copia file configurazione...
copy /Y requirements.txt deploy_temp\ >nul 2>&1
copy /Y print_config.json deploy_temp\ >nul 2>&1
copy /Y *.bat deploy_temp\ >nul 2>&1
echo   - requirements.txt copiato
echo   - print_config.json copiato
echo   - File .bat copiati

echo [3/7] Copia documentazione...
copy /Y *.md deploy_temp\ >nul 2>&1
echo   - File .md copiati

echo [4/9] Copia risorse...
copy /Y logo.png deploy_temp\ >nul 2>&1
echo   - logo.png copiato

echo [5/9] Copia font DejaVuSans...
copy /Y DejaVuSans.ttf deploy_temp\ >nul 2>&1
copy /Y DejaVuSans-Bold.ttf deploy_temp\ >nul 2>&1
if exist DejaVuSans.ttf (
    echo   - Font DejaVuSans copiati
) else (
    echo   ! ATTENZIONE: Font DejaVuSans non trovati
)

echo [6/9] Copia DLL lettore RFID...
if exist IDReader.dll (
    copy /Y IDReader.dll deploy_temp\ >nul 2>&1
    echo   - IDReader.dll copiato
) else (
    echo   ! ATTENZIONE: IDReader.dll non trovato
)

echo [7/9] Copia cartelle templates e static...
xcopy /E /I /Y templates deploy_temp\templates\ >nul 2>&1
xcopy /E /I /Y static deploy_temp\static\ >nul 2>&1
echo   - templates\ copiato
echo   - static\ copiato

echo [8/9] Copia configurazione database...
if exist db_config.enc (
    copy /Y db_config.enc deploy_temp\ >nul 2>&1
    echo   - db_config.enc copiato
) else (
    echo   ! ATTENZIONE: db_config.enc non trovato
)

if exist encryption_key.key (
    copy /Y encryption_key.key deploy_temp\ >nul 2>&1
    echo   - encryption_key.key copiato
) else (
    echo   ! ATTENZIONE: encryption_key.key non trovato
)

echo [9/9] Crea struttura cartelle...
mkdir deploy_temp\temp >nul 2>&1
echo   - Cartella temp\ creata

echo.
echo Creazione archivio ZIP...
powershell -Command "Compress-Archive -Path 'deploy_temp\*' -DestinationPath '%PACKAGE_NAME%.zip' -Force"

if exist %PACKAGE_NAME%.zip (
    echo.
    echo ========================================
    echo   PACCHETTO CREATO CON SUCCESSO!
    echo ========================================
    echo.
    echo File: %PACKAGE_NAME%.zip
    for %%A in (%PACKAGE_NAME%.zip) do (
        set size=%%~zA
        set /a sizeMB=%%~zA/1024/1024
    )
    for %%A in (%PACKAGE_NAME%.zip) do echo Dimensione: %%~zA bytes
    echo.
    echo Contenuto pacchetto:
    echo.
    dir deploy_temp /b
    echo.
    echo File totali:
    dir deploy_temp /s /b | find /c /v ""
    echo.
    echo ========================================
    echo   VERIFICA FILE CRITICI
    echo ========================================
    echo.
    if exist deploy_temp\requirements.txt (
        echo [OK] requirements.txt presente
    ) else (
        echo [!!] requirements.txt MANCANTE
    )
    if exist deploy_temp\app.py (
        echo [OK] app.py presente
    ) else (
        echo [!!] app.py MANCANTE
    )
    if exist deploy_temp\logo.png (
        echo [OK] logo.png presente
    ) else (
        echo [!!] logo.png MANCANTE
    )
    if exist deploy_temp\templates (
        echo [OK] templates\ presente
    ) else (
        echo [!!] templates\ MANCANTE
    )
    if exist deploy_temp\static (
        echo [OK] static\ presente
    ) else (
        echo [!!] static\ MANCANTE
    )
    echo.
    echo Pacchetto pronto per deployment!
    echo.
) else (
    echo.
    echo ========================================
    echo   ERRORE CREAZIONE PACCHETTO
    echo ========================================
    echo.
    echo Impossibile creare il file ZIP.
    echo Verifica che PowerShell sia disponibile.
    echo.
)

REM Pulizia
echo Pulizia file temporanei...
rmdir /s /q deploy_temp

echo.
echo ========================================
echo   COMPLETATO
echo ========================================
echo.
echo Premi un tasto per aprire la cartella...
pause >nul
explorer .
