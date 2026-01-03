@echo off
REM ========================================
REM KIOSK HR - Creazione Pacchetto Deploy
REM Versione: 2.2.0
REM Data: 2026-01-03
REM ========================================

echo.
echo ========================================
echo   KIOSK HR - Creazione Pacchetto
echo   Versione 2.2.0
echo ========================================
echo.

REM Imposta nome pacchetto con timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set PACKAGE_NAME=Kiosk_HR_v2.2.0_%TIMESTAMP%.zip

echo [1/6] Preparazione directory temporanea...
if exist "deploy_temp" rmdir /s /q deploy_temp
mkdir deploy_temp
echo [OK] Directory creata

echo.
echo [2/6] Copia file applicazione...
REM File Python principali
copy app.py deploy_temp\ >nul
copy absence_report.py deploy_temp\ >nul
copy absence_request.py deploy_temp\ >nul
copy badge_reader.py deploy_temp\ >nul
copy certificate_generator.py deploy_temp\ >nul
copy config_manager.py deploy_temp\ >nul
copy db_connection.py deploy_temp\ >nul
copy digital_signature.py deploy_temp\ >nul
copy email_connector.py deploy_temp\ >nul
copy pdf_printer.py deploy_temp\ >nul
copy printer_keepalive.py deploy_temp\ >nul
copy rfid_reader.py deploy_temp\ >nul
copy setup.py deploy_temp\ >nul
copy update_signature.py deploy_temp\ >nul
copy utils.py deploy_temp\ >nul
copy requirements.txt deploy_temp\ >nul
echo [OK] File Python copiati

echo.
echo [3/6] Copia templates e static...
xcopy /E /I /Q templates deploy_temp\templates >nul
xcopy /E /I /Q static deploy_temp\static >nul
echo [OK] Templates e static copiati

echo.
echo [4/6] Copia file configurazione e risorse...
REM Font
copy DejaVuSans.ttf deploy_temp\ >nul
copy DejaVuSans-Bold.ttf deploy_temp\ >nul

REM Loghi
copy logo.png deploy_temp\ >nul
copy GTMC.png deploy_temp\ >nul

REM DLL RFID (se presente)
if exist "IDReader.dll" copy IDReader.dll deploy_temp\ >nul

REM File configurazione (template vuoti - l'utente dovrà configurare)
if exist "print_config.json" copy print_config.json deploy_temp\ >nul

REM Chiavi di crittografia (ATTENZIONE: solo per deploy su stessa macchina)
if exist "encryption_key.key" copy encryption_key.key deploy_temp\ >nul
if exist "email_key.key" copy email_key.key deploy_temp\ >nul
if exist "db_config.enc" copy db_config.enc deploy_temp\ >nul
if exist "email_credentials.enc" copy email_credentials.enc deploy_temp\ >nul

echo [OK] File configurazione copiati

echo.
echo [5/6] Copia script e documentazione...
REM Script di installazione e avvio
copy INSTALLA.bat deploy_temp\ >nul
copy START_APP.bat deploy_temp\ >nul
copy START_SISTEMA_KIOSK.bat deploy_temp\ >nul
copy AGGIORNA_FIRMA.bat deploy_temp\ >nul

REM Documentazione
copy README.md deploy_temp\ >nul
copy INSTALLAZIONE_MANUALE.md deploy_temp\ >nul
copy DEPLOYMENT.md deploy_temp\ >nul
copy GUIDA_RAPIDA.md deploy_temp\ >nul
copy GUIDA_RFID.md deploy_temp\ >nul
copy GUIDA_KIOSK_FULLSCREEN.md deploy_temp\ >nul
copy GUIDA_NEWS_SLIDESHOW.md deploy_temp\ >nul
copy CONFIGURAZIONE_RETE.md deploy_temp\ >nul
copy STAMPA_AUTOMATICA.md deploy_temp\ >nul
copy RELEASE_NOTES_v2.2.0.md deploy_temp\ >nul
copy RELEASE_NOTES_v2.1.1.md deploy_temp\ >nul

echo [OK] Script e documentazione copiati

echo.
echo [6/6] Creazione directory necessarie...
mkdir deploy_temp\temp >nul 2>&1
mkdir deploy_temp\Images >nul 2>&1

REM Copia immagini slideshow (solo X* e S*)
if exist "Images" (
    for %%F in (Images\x*.* Images\X*.* Images\s*.* Images\S*.*) do (
        copy "%%F" deploy_temp\Images\ >nul 2>&1
    )
    echo [OK] Immagini slideshow copiate
) else (
    echo [INFO] Directory Images non trovata
)

echo.
echo [7/7] Creazione archivio ZIP...
REM Usa PowerShell per creare ZIP
powershell -Command "Compress-Archive -Path 'deploy_temp\*' -DestinationPath '%PACKAGE_NAME%' -Force"

if exist "%PACKAGE_NAME%" (
    echo [OK] Pacchetto creato: %PACKAGE_NAME%
    
    REM Mostra dimensione
    for %%A in ("%PACKAGE_NAME%") do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
    )
    
    echo.
    echo ========================================
    echo   PACCHETTO CREATO CON SUCCESSO!
    echo ========================================
    echo.
    echo File: %PACKAGE_NAME%
    echo.
    echo Contenuto del pacchetto:
    echo - Applicazione Python completa
    echo - Templates HTML e CSS
    echo - Script di installazione
    echo - Documentazione completa
    echo - Immagini slideshow (X* e S*)
    echo - Font e loghi
    echo.
    echo PROSSIMI PASSI:
    echo 1. Trasferire il file ZIP sulla macchina target
    echo 2. Estrarre il contenuto
    echo 3. Eseguire INSTALLA.bat come Amministratore
    echo 4. Configurare database e email con setup.py
    echo 5. Avviare con START_APP.bat
    echo.
    echo ========================================
) else (
    echo [ERRORE] Impossibile creare pacchetto ZIP
    pause
    exit /b 1
)

REM Pulizia
echo.
echo Pulizia file temporanei...
rmdir /s /q deploy_temp
echo [OK] Pulizia completata

echo.
pause
