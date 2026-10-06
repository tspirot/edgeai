Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "d:\Projekti\rPI5 projrcts\kvo-te"
WshShell.Run "python kvo_te.py", 1, False
