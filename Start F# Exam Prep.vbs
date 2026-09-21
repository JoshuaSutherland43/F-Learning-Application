' Double-click this file to start the F# Exam Prep server (if it isn't already
' running) and open it in your browser. No console window, no command prompt.

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
backendDir = scriptDir & "\backend"
pyw = "C:\Python313\pythonw.exe"
pidFile = backendDir & "\server.pid"
appUrl = "http://localhost:5000/"

' --- Is the server already running? ---
running = False
On Error Resume Next
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
http.SetTimeouts 1000, 1000, 1000, 1000
http.Open "GET", "http://127.0.0.1:5000/api/curriculum", False
http.Send
If Err.Number = 0 Then
    If http.Status = 200 Then running = True
End If
Err.Clear
On Error Goto 0

' --- If not, start it (hidden, no window) and remember its process id ---
If Not running Then
    If Not fso.FileExists(pyw) Then
        MsgBox "Could not find Python at:" & vbCrLf & pyw & vbCrLf & vbCrLf & _
               "Edit this .vbs file and fix the 'pyw' path to match your Python install.", vbCritical, "F# Exam Prep"
        WScript.Quit 1
    End If

    shell.CurrentDirectory = backendDir
    Set execObj = shell.Exec("""" & pyw & """ """ & backendDir & "\app.py""")

    Set pidF = fso.CreateTextFile(pidFile, True)
    pidF.WriteLine execObj.ProcessID
    pidF.Close

    ' Give Flask a moment to finish booting before we open the browser.
    WScript.Sleep 1800
End If

shell.Run appUrl
