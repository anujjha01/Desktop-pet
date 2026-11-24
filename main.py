"""Kitty, a desktop cat that listens locally and runs a fixed set of commands."""

import logging
import os
import queue
import sys
import time
from pathlib import Path

import pygame
import win32gui

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from actions import perform
from actions.speech import Speaker
from actions.startup import enabled as startup_enabled
from actions.startup import set_enabled as set_startup
from pet.cat import Cat
from pet.window import HEIGHT, WIDTH, PetWindow, enable_dpi_awareness, work_area
from voice.commands import Command, parse, prepare
from voice.listener import Listener, ensure_model

HELP = (
    "I didn't catch that. Try open YouTube, tell me a joke, or what time is it."
)


def configure_log():
    logging.basicConfig(
        filename=ROOT / "kitty.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def short_bubble(line):
    if line.startswith("I didn't"):
        return "Hmm"
    if line.startswith("I opened ChatGPT"):
        return "Copied"
    if line.startswith(("Hi!", "Hello!", "Hey there!")):
        return "Hello!"
    if line.startswith("Why ") or line.startswith("What do cats") or line.startswith("What do you call"):
        return "Joke time!"
    if line.startswith(("I'm doing", "Pretty good", "I'm happy")):
        return "Pretty good!"
    if line.startswith(("Fair enough", "A quiet day", "Got it.")):
        return "Got it!"
    if line.startswith(("Glad to hear", "That's good", "Nice!")):
        return "Nice!"
    if line.startswith("I'll keep you company"):
        return "I'm here!"
    if len(line) <= 28:
        return line.rstrip(".")
    return "On it"


def main():
    configure_log()
    enable_dpi_awareness()
    left, top, right, bottom = work_area()
    os.environ["SDL_VIDEO_WINDOW_POS"] = f"{left + 80},{bottom - HEIGHT - 8}"
    pygame.init()
    window = PetWindow(left + 80, bottom - HEIGHT - 8)
    cat = Cat(
        x=left + 80,
        y=bottom - HEIGHT - 8,
        min_x=left,
        max_x=right - WIDTH,
        min_y=top,
        max_y=bottom - HEIGHT,
    )
    speaker = Speaker()
    events = queue.Queue()
    listener = None
    armed = False
    conversation_until = 0.0
    running = True
    clock = pygame.time.Clock()

    def redraw(message=None):
        if message is not None:
            cat.bubble = message
        window.draw(cat)
        pygame.event.pump()

    try:
        model = ensure_model(ROOT, redraw)
    except Exception as exc:
        logging.exception("model download failed")
        cat.bubble = "Voice download failed"
        window.draw(cat)
        speaker.say("I could not download the voice model. Check kitty.log.")
        pygame.time.wait(2500)
        speaker.close()
        pygame.quit()
        raise SystemExit(1) from exc

    listener = Listener(model, events)
    listener.start()
    logging.info("background listening started; wake word is optional")
    cat.bubble = "Waking up"
    drag_offset = None

    try:
        while running:
            dt = clock.tick(30) / 1000
            now = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    cat.dragging = True
                    drag_offset = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    cat.dragging = False
                    cat.target_x = cat.x
                    cat.target_y = cat.y
                    drag_offset = None
                elif event.type == pygame.MOUSEMOTION and cat.dragging and drag_offset:
                    cursor_x, cursor_y = win32gui.GetCursorPos()
                    cat.x = cursor_x - drag_offset[0]
                    cat.y = cursor_y - drag_offset[1]
                    cat.x = min(max(cat.x, cat.min_x), cat.max_x)
                    cat.y = min(max(cat.y, cat.min_y), cat.max_y)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    choice = window.popup(listener.paused, startup_enabled())
                    if choice == 1:
                        listener.set_paused(not listener.paused)
                        armed = False
                        cat.resume_roam()
                        cat.note("Ears off" if listener.paused else "Ears on")
                    elif choice == 2:
                        try:
                            set_startup(not startup_enabled(), ROOT / "main.py")
                            cat.note("Starts with Windows" if startup_enabled() else "Startup off")
                        except Exception:
                            logging.exception("startup shortcut failed")
                            cat.note("Startup failed")
                    elif choice == 3:
                        running = False

            while True:
                try:
                    kind, text = events.get_nowait()
                except queue.Empty:
                    break
                if kind == "error":
                    logging.error("listener: %s", text)
                    armed = False
                    speaker.say("I can't hear you. Check the microphone.")
                    cat.start_talk("No microphone")
                elif kind == "ready":
                    if cat.bubble == "Waking up":
                        cat.resume_roam()
                        cat.note("Ready in background", seconds=3)
                elif kind == "wake":
                    if not listener.paused and not armed:
                        armed = True
                        cat.look_toward((left + right) / 2, WIDTH)
                        cat.start_listen()
                    elif armed:
                        cat.listen_until = time.time() + 8
                elif kind == "partial" and armed:
                    cat.listen_until = time.time() + 8
                    preview = text.strip().capitalize()
                    if preview:
                        cat.bubble = preview[:25]
                elif kind == "final":
                    if speaker.speaking:
                        logging.info("ignored speech while Kitty was replying: %r", text)
                        continue
                    phrase = prepare(text, armed)
                    direct_command = None
                    if phrase is None:
                        # Wake-word recognition is the part that failed most
                        # often in the logs. Fixed, allowlisted commands work
                        # on their own, so "open YouTube" remains usable.
                        direct_command = parse(text)
                        if direct_command is None and time.time() < conversation_until:
                            direct_command = Command("chat", text)
                        if direct_command is None:
                            logging.info("ignored speech (no wake/command): %r", text)
                            cat.note(f"Heard {text[:18]}", seconds=3)
                            continue
                        phrase = text
                    logging.info("command phrase: %r (armed=%s)", phrase, armed)
                    if phrase == "":
                        direct_command = parse(text)
                        if direct_command is None:
                            if not armed:
                                armed = True
                                cat.look_toward((left + right) / 2, WIDTH)
                                cat.start_listen()
                            else:
                                cat.listen_until = time.time() + 8
                                cat.bubble = "Listening"
                            continue
                        phrase = text
                    armed = False
                    command = direct_command or parse(phrase)
                    if command is None and time.time() < conversation_until:
                        command = Command("chat", phrase)
                    if command is None:
                        cat.start_talk(f"Heard {phrase[:18]}")
                        speaker.say(HELP)
                        continue
                    try:
                        line = perform(command)
                    except Exception as exc:
                        logging.exception("command failed: %s", command)
                        line = str(exc) if isinstance(exc, (LookupError, OSError, ValueError)) else "I couldn't do that."
                    logging.info("did: %s -> %s", command, line)
                    if command.name == "chat":
                        conversation_until = time.time() + 60
                    else:
                        conversation_until = 0.0
                    cat.look_toward((left + right) / 2, WIDTH)
                    cat.start_talk(short_bubble(line))
                    speaker.say(line)

            if armed and cat.state == "listen" and now > cat.listen_until:
                armed = False
                cat.start_talk("I'm here")
                speaker.say("I'm here.")

            if cat.state == "talk" and not speaker.speaking and now > cat.talk_until:
                cat.resume_roam()

            cat.update(dt)
            window.move(cat.x, cat.y)
            if not cat.dragging:
                window.rest_behind()
            window.draw(cat)
    finally:
        if listener is not None:
            listener.stop()
        speaker.close()
        pygame.quit()


if __name__ == "__main__":
    main()
