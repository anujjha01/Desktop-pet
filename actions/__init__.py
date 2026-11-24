"""Run a parsed command and return the line Kitty should say."""

from datetime import datetime

from actions import apps, browser, calculator, conversation, folders, notes
from voice.commands import Command


def perform(command: Command) -> str:
    name = command.name
    arg = command.arg
    if name == "chat":
        return conversation.reply(arg)
    if name == "note_add":
        return notes.add_note(arg)
    if name == "note_read":
        return notes.read_notes()
    if name == "calculate":
        return calculator.calculate(arg)
    if name == "edge_search":
        browser.edge_search(arg)
        return f"Searching Edge for {arg}."
    if name == "time":
        clock = datetime.now().strftime("%I:%M %p").lstrip("0")
        return f"It's {clock}."
    if name == "date":
        today = datetime.now().strftime("%A, %B %d").replace(" 0", " ")
        return f"Today is {today}."
    if name == "google":
        browser.google(arg)
        return f"Searching Google for {arg}."
    if name == "youtube_search":
        browser.youtube(arg)
        return f"Searching YouTube for {arg}."
    if name == "linkedin_search":
        browser.linkedin(arg)
        return f"Searching LinkedIn for {arg}."
    if name == "facebook_search":
        browser.facebook_search(arg)
        return f"Searching Facebook people for {arg}."
    if name == "open_site":
        browser.site(arg)
        return f"Opening {browser.display_name(arg)}."
    if name == "top":
        browser.top(arg)
        return f"Opening the top of {browser.display_name(arg)}."
    if name == "chatgpt":
        browser.copy_text(arg)
        browser.site("chatgpt")
        return "I opened ChatGPT and copied your question. Paste it in."
    if name == "open_app":
        apps.open_app(arg)
        label = "File Explorer" if arg == "file explorer" else arg.capitalize()
        return f"Opening {label}."
    if name == "open_app_any":
        apps.open_app(arg)
        return f"Opening {arg} from your apps."
    if name == "open_folder":
        label = folders.open_folder(arg)
        return f"Opening {label}."
    if name == "open_item":
        try:
            apps.open_app(arg)
            return f"Opening {arg}."
        except LookupError:
            label = folders.open_folder(arg)
            return f"Opening {label}."
    raise ValueError(name)
