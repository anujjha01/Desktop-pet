"""Optional sign-in shortcut in the Windows Startup folder."""

import sys
from pathlib import Path


def shortcut_path():
    appdata = Path.home() / "AppData" / "Roaming"
    startup = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return startup / "Kitty.lnk"


def enabled():
    return shortcut_path().exists()


def set_enabled(turn_on, main_file: Path):
    path = shortcut_path()
    if not turn_on:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    import win32com.client

    pythonw = Path(sys.executable).with_name("pythonw.exe")
    target = pythonw if pythonw.exists() else Path(sys.executable)
    shell = win32com.client.Dispatch("WScript.Shell")
    link = shell.CreateShortCut(str(path))
    link.Targetpath = str(target)
    link.Arguments = f'"{main_file}"'
    link.WorkingDirectory = str(main_file.parent)
    link.Description = "Kitty desktop cat"
    link.WindowStyle = 7
    link.save()
