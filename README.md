# Kitty

A small cat that walks on the Windows desktop, wakes up when you say **computer**, **kitty**, or **sweety**, and runs a fixed set of commands. Speech recognition and the reply voice stay on this PC. Nothing is sent to a cloud model.

## Run it

From this folder:

```bat
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Or double-click `run.bat`. The first launch downloads the small English Vosk model (about 40 MB) into `models/`.

Python 3.12 is the one to use. The voice library does not ship a build for newer Pythons yet.

## What you can say

Kitty keeps listening while you work in other apps; you do not need to focus its window. Say a command directly, or add a wake word first:

- computer open youtube
- sweety open youtube
- sweety search google for weather
- kitty play lofi on youtube
- kitty ask chatgpt how to make tea
- kitty open linkedin
- kitty search linkedin for software engineer
- sweety top post on youtube
- kitty open notepad
- kitty what time is it
- open the Downloads folder
- open folder projects
- open app Spotify
- search Edge for quiet cafes
- search Facebook for Ada Lovelace
- take a note to call the dentist
- read my notes
- calculate 12 times 3
- what's today's date

Kitty can also chat with you. Try **hi**, **hi Kitty**, **how are you**, **tell me a joke**, **I'm bored**, **what's your name**, or **what can you do**. These replies are generated locally from a small set of friendly responses; Kitty does not use an online chatbot.

Notes are saved locally in `kitty_notes.txt` beside the app. Kitty can read back the latest three notes. Spoken calculations support basic arithmetic, including plus, minus, times, divided by, and modulo.

Sites: YouTube, Google, LinkedIn, Instagram, Facebook, X, and ChatGPT.
Apps: Notepad, Calculator, File Explorer, Chrome, and Edge.

Kitty can also open installed apps by their Start Menu name, open common folders and named folders found in your Desktop, OneDrive, Documents, and Downloads, and open a drive or This PC. Edge searches use Bing and open in Edge.

"Top post" opens that site's feed or trending page in the browser you are already logged into. Kitty does not read posts. A ChatGPT question is copied to the clipboard; paste it into the tab.

## The cat

It strolls around the usable desktop, pauses, and blinks. On the wake word it stops and listens. Drag it with the left mouse button. Right-click for pause listening, start with Windows, and quit. Escape also quits.

If something goes wrong, look at `kitty.log`.
