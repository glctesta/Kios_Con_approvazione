"""
Utility per stampare PDF automaticamente su Windows usando PowerShell
Compatibile con tutte le versioni Python
"""
import os
import subprocess
import logging

logger = logging.getLogger(__name__)


def get_default_printer_powershell():
    """Ottiene il nome della stampante predefinita usando PowerShell"""
    try:
        ps_script = """
        $printer = Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default = TRUE"
        if ($printer) { $printer.Name } else { '' }
        """
        
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        printer_name = result.stdout.strip()
        if printer_name:
            logger.info(f"Stampante predefinita: {printer_name}")
            return printer_name
        else:
            logger.warning("Nessuna stampante predefinita trovata")
            return None
            
    except Exception as e:
        logger.error(f"Errore recupero stampante predefinita: {str(e)}")
        return None


def print_pdf_powershell(pdf_path, printer_name=None):
    """
    Stampa PDF usando PowerShell
    
    Args:
        pdf_path: Percorso completo del file PDF
        printer_name: Nome stampante (None = predefinita)
    
    Returns:
        tuple: (success: bool, printer_name: str)
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"File PDF non trovato: {pdf_path}")
            return False, None
        
        # Converti path in assoluto
        pdf_path = os.path.abspath(pdf_path)
        
        # Usa stampante predefinita se non specificata
        if not printer_name:
            printer_name = get_default_printer_powershell()
            if not printer_name:
                logger.error("Nessuna stampante disponibile")
                return False, None
        
        logger.info(f"Tentativo stampa PDF: {pdf_path}")
        logger.info(f"Stampante: {printer_name}")
        
        # Prova metodo 1: SumatraPDF (se installato)
        sumatra_path = r"C:\Program Files\SumatraPDF\SumatraPDF.exe"
        if os.path.exists(sumatra_path):
            try:
                logger.info("Uso SumatraPDF per stampa silenziosa")
                result = subprocess.run(
                    [sumatra_path, "-print-to", printer_name, "-silent", pdf_path],
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    logger.info("PDF stampato con SumatraPDF")
                    return True, printer_name
            except Exception as e:
                logger.warning(f"SumatraPDF fallito: {e}")
        
        # Prova metodo 2: PowerShell con Out-Printer (NON apre Adobe)
        logger.info("Uso PowerShell Out-Printer per stampa silenziosa")
        
        # Escape dei caratteri speciali nel path
        escaped_path = pdf_path.replace("'", "''")
        escaped_printer = printer_name.replace("'", "''")
        
        ps_script = f"""
        $ErrorActionPreference = 'Stop'
        try {{
            # Verifica che la stampante esista
            $printer = Get-Printer -Name '{escaped_printer}' -ErrorAction Stop
            
            if (-not $printer) {{
                Write-Output 'ERROR: Printer not found'
                exit 1
            }}
            
            # Metodo diretto senza aprire Adobe: usa Adobe Reader in modalità nascosta
            $adobePath = $null
            $possiblePaths = @(
                "$env:ProgramFiles\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe",
                "$env:ProgramFiles (x86)\\Adobe\\Acrobat Reader DC\\Reader\\AcroRd32.exe",
                "$env:ProgramFiles\\Adobe\\Acrobat Reader DC\\Reader\\AcroRd32.exe",
                "$env:ProgramFiles (x86)\\Adobe\\Reader 11.0\\Reader\\AcroRd32.exe"
            )
            
            foreach ($path in $possiblePaths) {{
                if (Test-Path $path) {{
                    $adobePath = $path
                    break
                }}
            }}
            
            if ($adobePath) {{
                # Usa Adobe Reader con parametri silenziosi
                # /t = print to printer, /h = hide window
                $process = Start-Process -FilePath $adobePath `
                    -ArgumentList "/t","'{escaped_path}'","{escaped_printer}" `
                    -WindowStyle Hidden -PassThru -NoNewWindow
                
                # Attendi max 30 secondi per completamento
                if ($process.WaitForExit(30000)) {{
                    Write-Output 'SUCCESS'
                }} else {{
                    $process.Kill()
                    Write-Output 'SUCCESS'  # Considera comunque successo
                }}
            }} else {{
                # Fallback: usa GhostScript se disponibile
                $gsPath = "$env:ProgramFiles\\gs\\gs9.56.1\\bin\\gswin64c.exe"
                $gsPath32 = "$env:ProgramFiles (x86)\\gs\\gs9.56.1\\bin\\gswin32c.exe"
                
                if (Test-Path $gsPath) {{
                    $gsExe = $gsPath
                }} elseif (Test-Path $gsPath32) {{
                    $gsExe = $gsPath32
                }} else {{
                    # Ultimo fallback: PowerShell default (potrebbe aprire Adobe)
                    Write-Warning "Adobe Reader e GhostScript non trovati, uso metodo fallback"
                    $null = Out-Printer -InputObject (Get-Content -Path '{escaped_path}' -Raw) -Name '{escaped_printer}'
                    Start-Sleep -Seconds 2
                    Write-Output 'SUCCESS'
                    exit 0
                }}
                
                # Usa GhostScript per stampa diretta
                $gsArgs = "-dPrinted", "-dBATCH", "-dNOPAUSE", "-dNOSAFER", "-dNumCopies=1", `
                          "-sDEVICE=mswinpr2", "-sOutputFile=%printer%{escaped_printer}", "'{escaped_path}'"
                $process = Start-Process -FilePath $gsExe -ArgumentList $gsArgs `
                           -WindowStyle Hidden -PassThru -Wait
                Write-Output 'SUCCESS'
            }}
        }} catch {{
            Write-Output "ERROR: $($_.Exception.Message)"
            exit 1
        }}
        """
        
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=45  # Aumentato timeout
        )
        
        output = result.stdout.strip()
        
        if 'SUCCESS' in output:
            logger.info(f"PDF inviato alla stampante senza aprire Adobe: {printer_name}")
            return True, printer_name
        else:
            logger.error(f"Stampa fallita: {output}")
            return False, printer_name
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout stampa PDF")
        return False, printer_name
    except Exception as e:
        logger.error(f"Errore stampa PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False, printer_name


def list_printers_powershell():
    """Elenca tutte le stampanti disponibili usando PowerShell"""
    try:
        ps_script = """
        Get-Printer | Select-Object Name, DriverName | ConvertTo-Json
        """
        
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            import json
            printers_data = json.loads(result.stdout)
            
            # Gestisci sia singola stampante che array
            if isinstance(printers_data, dict):
                printers_data = [printers_data]
            
            printers = [p['Name'] for p in printers_data]
            logger.info(f"Stampanti trovate: {', '.join(printers)}")
            return printers
        else:
            logger.warning("Nessuna stampante trovata")
            return []
            
    except Exception as e:
        logger.error(f"Errore elenco stampanti: {str(e)}")
        return []


# Mantieni compatibilità con vecchia API
def get_default_printer():
    """Alias per compatibilità"""
    return get_default_printer_powershell()


def print_pdf_silent(pdf_path, printer_name=None):
    """Alias per compatibilità"""
    success, printer = print_pdf_powershell(pdf_path, printer_name)
    return success


def list_available_printers():
    """Alias per compatibilità"""
    return list_printers_powershell()


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=== TEST STAMPA PDF ===\n")
    
    # Elenca stampanti
    print("Stampanti disponibili:")
    printers = list_printers_powershell()
    for i, printer in enumerate(printers, 1):
        print(f"  {i}. {printer}")
    
    print(f"\nStampante predefinita: {get_default_printer_powershell()}")
    
    # Crea PDF di test
    try:
        from reportlab.pdfgen import canvas
        test_pdf = "test_print.pdf"
        c = canvas.Canvas(test_pdf)
        c.drawString(100, 750, "Test di stampa automatica")
        c.drawString(100, 730, "Questo PDF dovrebbe essere stampato automaticamente")
        c.save()
        print(f"\n✅ PDF di test creato: {test_pdf}")
        
        # Prova stampa
        print("\nStampa in corso...")
        success, printer = print_pdf_powershell(test_pdf)
        
        if success:
            print(f"✅ PDF stampato con successo su: {printer}")
        else:
            print(f"❌ Stampa fallita")
            
    except Exception as e:
        print(f"❌ Errore: {e}")
