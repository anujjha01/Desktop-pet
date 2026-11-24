"""Open common Windows locations and find folders in personal directories."""

import os
import re
from pathlib import Path


def _key(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _roots():
    home = Path.home()
    one_drive = Path(os.environ.get("OneDrive", home / "OneDrive"))
    names = ("Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos")
    roots = []
    for name in names:
        roots.extend((one_drive / name, home / name))
    roots.extend((one_drive, home))
    seen = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved.is_dir() and resolved not in seen:
            seen.add(resolved)
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
    visited = 0
    for root in _roots():
        try:
            base_depth = len(root.parts)
            for current, dirs, _files in os.walk(root, onerror=lambda _error: None):
                visited += 1
                current_path = Path(current)
                depth = len(current_path.parts) - base_depth
                dirs[:] = [
                    directory for directory in dirs
                    if not directory.startswith(".")
                    and directory.lower() not in {"appdata", "node_modules", ".git", ".venv"}
                    and depth < 5
                ]
                for directory in dirs:
                    key = _key(directory)
                    found = current_path / directory
                    if key == target:
                        exact.append(found)
                    elif len(target) >= 4 and (key.startswith(target) or target in key):
                        partial.append(found)
                if len(exact) >= 2:
                    break
                if visited >= 4000:
                    break
        except OSError:
            continue
        if len(exact) >= 2 or visited >= 4000:
            break
    choices = exact or (partial if len(partial) == 1 else [])
    if choices:
        return str(choices[0]), choices[0].name
    if len(partial) > 1:
        raise LookupError(f"I found several folders matching {name}. Say the full folder path or a more specific name.")
    raise LookupError(f"I couldn't find a folder named {name} in your Desktop, OneDrive, Documents, or Downloads.")


def open_folder(name):
    path, label = find_folder(name)
    os.startfile(path)
    return label
