"""Open common Windows locations and find folders in personal directories."""

import os
import re
import logging
from pathlib import Path


def _key(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _roots():
    home = Path.home()
    one_drive = Path(os.environ.get("OneDrive", home / "OneDrive"))
    # Search the synced profile first, then the rest of the user profile.
    # Searching each common folder separately caused the same files to be
    # scanned repeatedly and could hit the limit before reaching nested folders.
    for root in (one_drive, home):
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved.is_dir():
            yield resolved


def _known_location(name):
    aliases = {
        "desktop": ("Desktop",), "my desktop": ("Desktop",),
        "downloads": ("Downloads",), "my downloads": ("Downloads",),
        "documents": ("Documents",), "my documents": ("Documents",),
        "pictures": ("Pictures",), "music": ("Music",), "videos": ("Videos",),
    }
    if name in {"this pc", "computer"}:
        return "shell:MyComputerFolder", "This PC"
    drive = re.fullmatch(r"([a-z]) drive", name)
    if drive:
        path = Path(f"{drive.group(1).upper()}:\\")
        if path.exists():
            return str(path), f"{drive.group(1).upper()} drive"
        raise LookupError(f"I couldn't find the {drive.group(1).upper()} drive.")
    parts = aliases.get(name)
    if parts:
        folder = parts[0]
        for base in (Path(os.environ.get("OneDrive", Path.home() / "OneDrive")), Path.home()):
            path = base / folder
            if path.is_dir():
                return str(path), folder
        raise LookupError(f"I couldn't find your {folder} folder.")
    return None


def find_folder(name):
    name = " ".join(name.lower().split())
    known = _known_location(name)
    if known:
        return known

    candidate = Path(os.path.expandvars(os.path.expanduser(name)))
    if candidate.is_dir():
        return str(candidate.resolve()), candidate.name or str(candidate)

    target = _key(name)
    exact = []
    partial = []
    for root in _roots():
        visited = 0
        try:
            base_depth = len(root.parts)
            for current, dirs, _files in os.walk(root, onerror=lambda _error: None):
                visited += 1
                current_path = Path(current)
                depth = len(current_path.parts) - base_depth
                dirs[:] = [
                    directory for directory in dirs
                    if not directory.startswith(".")
                    and directory.lower() not in {
                        "appdata", "node_modules", ".git", ".venv",
                        "windows", "program files", "program files (x86)",
                        "programdata", "$recycle.bin", "system volume information",
                    }
                    and not (root == Path.home().resolve() and directory.lower() == "onedrive")
                    and depth < 12
                ]
                for directory in dirs:
                    key = _key(directory)
                    found = current_path / directory
                    if key == target:
                        exact.append(found)
                    elif len(target) >= 4 and (key.startswith(target) or target in key):
                        partial.append(found)
                if exact:
                    break
                if visited >= 12000:
                    break
        except OSError:
            continue
        if exact:
            break
    partial.sort(
        key=lambda path: (
            not _key(path.name).startswith(target),
            abs(len(_key(path.name)) - len(target)),
        )
    )
    choices = exact or partial
    if choices:
        return str(choices[0]), choices[0].name
    raise LookupError(f"I couldn't find a folder named {name} in your OneDrive or user folder.")


def open_folder(name):
    path, label = find_folder(name)
    os.startfile(path)
    logging.getLogger("kitty").info("opened folder: %s", path)
    return label
