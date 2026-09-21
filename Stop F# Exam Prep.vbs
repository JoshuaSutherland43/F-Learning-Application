' Double-click this file to stop the F# Exam Prep server that
' "Start F# Exam Prep.vbs" launched.

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pidFile = scriptDir & "\backend\server.pid"

If fso.FileExists(pidFile) Then
    Set f = fso.OpenTextFile(pidFile, 1)
    pid = Trim(f.ReadLine())
    f.Close

    shell.Run "taskkill /PID " & pid & " /F", 0, True
    fso.DeleteFile(pidFile)
    MsgBox "F# Exam Prep server stopped.", vbInformation, "F# Exam Prep"
Else
    MsgBox "No running server found (it may already be stopped).", vbInformation, "F# Exam Prep"
End If
