# Script per creare pacchetto deploy Kiosk HR v2.3.0

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "  Kiosk HR - Deploy Package Creator"  -ForegroundColor Cyan
Write-Host "  Versione: 2.3.0"  -ForegroundColor Cyan
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""

$version = "2.3.0"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$packageName = "Kiosk_HR_Deploy_v${version}_${timestamp}"
$zipFile = "${packageName}.zip"
$tempDir = "deploy_temp"

Write-Host "[1/5] Pulizia directory temporanea..." -ForegroundColor Yellow
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "[2/5] Copia file applicazione..." -ForegroundColor Yellow
$pythonFiles = "app.py", "absence_report.py", "absence_request.py", "badge_reader.py", "certificate_generator.py", "config.py", "config_manager.py", "db_connection.py", "digital_signature.py", "email_connector.py", "kiosk_logger.py", "offline_logger.py", "pdf_printer.py", "printer_keepalive.py", "setup.py", "utils.py", "windows_cert_signer.py"

foreach ($file in $pythonFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $tempDir
        Write-Host "  OK $file" -ForegroundColor Green
    }
}

Write-Host "[3/5] Copia directory..." -ForegroundColor Yellow
foreach ($dir in "templates", "static", "Images") {
    if (Test-Path $dir) {
        Copy-Item $dir -Destination $tempDir -Recurse
        Write-Host "  OK $dir/" -ForegroundColor Green
    }
}

Write-Host "[4/5] Copia file configurazione..." -ForegroundColor Yellow
$otherFiles = "requirements.txt", "logo.png", "README.md", "CHANGELOG.md", "DEPLOY.md", "DEPLOY_v2.3.0_SUMMARY.md", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "INSTALLA.bat", "START_APP.bat", "START_SISTEMA_KIOSK.bat"

foreach ($file in $otherFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $tempDir
        Write-Host "  OK $file" -ForegroundColor Green
    }
}

Write-Host "[5/5] Creazione archivio ZIP..." -ForegroundColor Yellow
if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

Compress-Archive -Path "$tempDir\*" -DestinationPath $zipFile -CompressionLevel Optimal
Remove-Item $tempDir -Recurse -Force

$zipSize = (Get-Item $zipFile).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  PACCHETTO CREATO CON SUCCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "File: $zipFile" -ForegroundColor Cyan
Write-Host "Dimensione: $zipSizeMB MB" -ForegroundColor Cyan
Write-Host "Percorso: $(Get-Location)\$zipFile" -ForegroundColor Cyan
Write-Host ""
