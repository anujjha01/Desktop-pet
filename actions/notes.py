"""Small local notes stored beside the Kitty project."""

from datetime import datetime
from pathlib import Path


NOTES_FILE = Path(__file__).resolve().parent.parent / "kitty_notes.txt"


def add_note(text):
    clean = " ".join(text.split())
    if not clean:
        raise ValueError("I didn't hear what to write down.")
    with NOTES_FILE.open("a", encoding="utf-8") as notes:
        notes.write(f"{datetime.now():%Y-%m-%d %H:%M}  {clean}\n")
    return "I saved that note."


def read_notes():
    if not NOTES_FILE.exists():
        return "You don't have any notes yet. Say, take a note, then tell me what to remember."
    lines = NOTES_FILE.read_text(encoding="utf-8").splitlines()
    if not lines:
        return "You don't have any notes yet."
    latest = lines[-3:]
    return "Your latest notes are: " + ". ".join(latest)
