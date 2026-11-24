"""Start a few local Windows apps."""

import os
import re
import shutil
import subprocess
from pathlib import Path
from difflib import SequenceMatcher

CREATE_NO_WINDOW = 0x08000000


def _existing(paths):
    for path in paths:
        if path and os.path.isfile(path):
            return path
    return None


def _chrome():
    return _existing(
        [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
    )


def _edge():
    return _existing(
        [
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        ]
    )


def edge_executable():
    return _edge()


def _start_menu_shortcut(name):
    roots = [
        Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("APPDATA", ""))
        / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    ]
    key = re.sub(r"[^a-z0-9]", "", name.lower())
    links = []
    for root in roots:
        if root.is_dir():
            try:
                links.extend(root.rglob("*.lnk"))
            except OSError:
                continue
    exact = [link for link in links if re.sub(r"[^a-z0-9]", "", link.stem.lower()) == key]
    if exact:
        return exact[0]
    matches = []
    for link in links:
        title = re.sub(r"[^a-z0-9]", "", link.stem.lower())
        score = SequenceMatcher(None, key, title).ratio()
        if score >= 0.84:
            matches.append((score, link))
    matches.sort(key=lambda item: item[0], reverse=True)
    if matches and (len(matches) == 1 or matches[0][0] > matches[1][0] + 0.08):
        return matches[0][1]
    return None


def open_app(name, argument=None):
    name = " ".join(name.lower().split())
    if name == "chrome":
        path = _chrome()
        if path:
            subprocess.Popen([path] + ([argument] if argument else []))
            return
        shortcut = _start_menu_shortcut("Google Chrome")
        if shortcut:
            os.startfile(str(shortcut), "open", argument or "")
            return
        raise LookupError("I couldn't find Chrome on this PC.")
    if name == "edge":
        path = _edge()
        if path:
            subprocess.Popen([path] + ([argument] if argument else []))
            return
        shortcut = _start_menu_shortcut("Microsoft Edge")
        if shortcut:
            os.startfile(str(shortcut), "open", argument or "")
            return
        raise LookupError("I couldn't find Microsoft Edge on this PC.")
    programs = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "file explorer": "explorer.exe",
    }
    if name in programs:
        subprocess.Popen([programs[name]], creationflags=CREATE_NO_WINDOW)
        return

    shortcut = _start_menu_shortcut(name)
    if shortcut:
        if argument:
            os.startfile(str(shortcut), "open", argument)
        else:
            os.startfile(str(shortcut))
        return

    executable = shutil.which(name)
    if executable:
        subprocess.Popen([executable] + ([argument] if argument else []))
        return
    raise LookupError(f"I couldn't find an app called {name} in the Start Menu or app path.")
