@echo off
REM ========================================
REM KIOSK HR - Update v2.2.0
REM Sistema News & Slideshow
REM ========================================

echo.
echo ========================================
echo   KIOSK HR - Update v2.2.0
echo   Sistema News ^& Slideshow
echo ========================================
echo.

REM Verifica che siamo nella directory corretta
if not exist "app.py" (
    echo [ERRORE] Directory installazione Kiosk HR non trovata!
    echo.
    echo Assicurarsi di essere nella directory root dell'applicazione
    echo dove si trova app.py
    echo.
    pause
    exit /b 1
)

echo [INFO] Directory Kiosk HR trovata
echo.

REM Chiedi conferma
echo Questa procedura aggiornerà i seguenti file:
echo   - app.py
echo   - templates\launcher.html
echo   - static\css\launcher.css
echo   - Images\ (aggiungerà nuove immagini)
echo.
set /p CONFIRM="Continuare con l'aggiornamento? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Aggiornamento annullato.
    pause
    exit /b 0
)

echo.
echo [1/6] Creazione backup file esistenti...
if not exist "backup_v2.2.0" mkdir backup_v2.2.0

if exist "app.py" copy /Y "app.py" "backup_v2.2.0\app.py.backup" >nul
if exist "templates\launcher.html" copy /Y "templates\launcher.html" "backup_v2.2.0\launcher.html.backup" >nul
if exist "static\css\launcher.css" copy /Y "static\css\launcher.css" "backup_v2.2.0\launcher.css.backup" >nul

echo [OK] Backup creato in backup_v2.2.0\

echo.
echo [2/6] Aggiornamento app.py...
copy /Y "app.py" "..\" >nul
echo [OK] app.py aggiornato

echo.
echo [3/6] Aggiornamento templates\launcher.html...
if not exist "..\templates" mkdir ..\templates
copy /Y "templates\launcher.html" "..\templates\" >nul
echo [OK] launcher.html aggiornato

echo.
echo [4/6] Aggiornamento static\css\launcher.css...
if not exist "..\static\css" mkdir ..\static\css
copy /Y "static\css\launcher.css" "..\static\css\" >nul
echo [OK] launcher.css aggiornato

echo.
echo [5/6] Copia immagini slideshow...
if not exist "..\Images" mkdir ..\Images
xcopy /Y /Q "Images\*.*" "..\Images\" >nul
echo [OK] Immagini copiate

echo.
echo [6/6] Installazione completata!
echo.
echo ========================================
echo   AGGIORNAMENTO COMPLETATO!
echo ========================================
echo.
echo Prossimi passi:
echo.
echo 1. Configurare tabella News nel database:
echo    Aprire e eseguire: CREATE_NEWS_TABLE.sql
echo.
echo 2. Inserire messaggi di test:
echo    Aprire e eseguire: INSERT_NEWS_TEST.sql
echo.
echo 3. Riavviare l'applicazione:
echo    python app.py
echo.
echo 4. Testare il sistema:
echo    Aprire http://localhost:3000
echo    Verificare i due frame (Slideshow e News)
echo.
echo 5. Consultare la documentazione:
echo    - GUIDA_NEWS_SLIDESHOW.md
echo    - RELEASE_NOTES_v2.2.0.md
echo.
echo ========================================
echo.
echo [BACKUP] I file originali sono in: backup_v2.2.0\
echo.

pause
