' ============================================================
' AVVIO_KIOSK.vbs - Avvio nascosto del supervisore kiosk HR
' ------------------------------------------------------------
' Lanciato al logon di Windows da:
'   - chiave HKCU\...\Run (INSTALLA_AUTOSTART.bat)
'   - copia nella cartella "Esecuzione automatica" (generata dall'installer)
' Non richiede privilegi di amministratore e non mostra finestre console.
'
' Risolve da solo la cartella del progetto (funziona anche se spostata)
' e usa il pythonw del venv se presente, altrimenti quello nel PATH.
' ============================================================
Option Explicit

Dim fso, sh, dir, py, scriptFile
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")

' Cartella del progetto = cartella dove si trova questo .vbs
dir = fso.GetParentFolderName(WScript.ScriptFullName)

' Il supervisore deve esistere, altrimenti esci in silenzio
scriptFile = dir & "\kiosk_supervisor.py"
If Not fso.FileExists(scriptFile) Then
    WScript.Quit 1
End If

' Python senza console: venv prima, PATH poi
py = dir & "\venv\Scripts\pythonw.exe"
If Not fso.FileExists(py) Then
    py = "pythonw.exe"
End If

sh.CurrentDirectory = dir
' 0 = finestra nascosta, False = non attendere la fine
sh.Run """" & py & """ """ & scriptFile & """", 0, False
