"""Windows voice, local SAPI, one phrase at a time."""

import logging
import queue
import threading

log = logging.getLogger("kitty")


class Speaker:
    def __init__(self):
        self._queue = queue.Queue()
        self._lock = threading.Lock()
        self._speaking = False
        self._thread = threading.Thread(target=self._loop, name="kitty-voice", daemon=True)
        self._thread.start()

    @property
    def speaking(self):
        with self._lock:
            return self._speaking or not self._queue.empty()

    def say(self, text):
        text = " ".join(text.split())
        if not text:
            return
        with self._lock:
            self._speaking = True
        self._queue.put(text[:240])

    def close(self):
        self._queue.put(None)

    def _loop(self):
        try:
            import pythoncom
            import pyttsx3

            pythoncom.CoInitialize()
            engine = pyttsx3.init()
            engine.setProperty("rate", 176)
            for voice in engine.getProperty("voices") or []:
                name = (voice.name or "").lower()
                if "zira" in name or "female" in name:
                    engine.setProperty("voice", voice.id)
                    break
        except Exception:
            log.exception("voice output unavailable")
            while True:
                if self._queue.get() is None:
                    return
                with self._lock:
                    self._speaking = not self._queue.empty()
            return

        while True:
            text = self._queue.get()
            if text is None:
                break
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                log.exception("could not speak")
            with self._lock:
                self._speaking = not self._queue.empty()
