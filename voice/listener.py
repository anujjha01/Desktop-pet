"""Always-on local listener. Vosk stays on this PC. No audio is uploaded."""

import json
import logging
import queue
import threading
import urllib.request
import zipfile
from pathlib import Path

import sounddevice as sd
from vosk import KaldiRecognizer, Model

from voice.commands import has_wake

log = logging.getLogger("kitty")

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_NAME = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000


def model_dir(root: Path) -> Path:
    return root / "models" / MODEL_NAME


def model_ready(path: Path) -> bool:
    return (path / "conf" / "mfcc.conf").exists() and (path / "am").exists()


def ensure_model(root: Path, on_progress) -> Path:
    dest = model_dir(root)
    if model_ready(dest):
        return dest
    folder = root / "models"
    folder.mkdir(parents=True, exist_ok=True)
    zip_path = folder / "vosk-model.zip"
    on_progress("Downloading voice...")

    last = ""

    def hook(done, total):
        nonlocal last
        if total:
            text = f"Downloading voice {min(100, int(done * 100 / total))}%"
        else:
            text = "Downloading voice..."
        if text != last:
            last = text
            on_progress(text)

    request = urllib.request.Request(MODEL_URL, headers={"User-Agent": "kitty-desktop-pet"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, zip_path.open("wb") as handle:
            total = int(response.headers.get("Content-Length") or 0)
            done = 0
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                done += len(chunk)
                if total:
                    hook(done, total)
                else:
                    on_progress("Downloading voice...")
        on_progress("Unpacking voice...")
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(folder)
    finally:
        zip_path.unlink(missing_ok=True)

    if not model_ready(dest):
        raise RuntimeError("The voice model unpacked, but it does not look complete.")
    return dest


class Listener:
    def __init__(self, model_path: Path, events: queue.Queue):
        self.model_path = model_path
        self.events = events
        self._running = True
        self._paused = threading.Event()
        self._reset = threading.Event()
        # Keep latency bounded if the recognizer briefly falls behind. Dropping
        # the oldest block is better than responding to stale speech seconds later.
        self._audio = queue.Queue(maxsize=12)
        self._thread = threading.Thread(target=self._run, name="kitty-listen", daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._running = False

    def set_paused(self, paused: bool):
        if paused:
            self._paused.set()
        else:
            self._paused.clear()
            self._reset.set()

    @property
    def paused(self):
        return self._paused.is_set()

    def _run(self):
        try:
            model = Model(str(self.model_path))
            recognizer = KaldiRecognizer(model, SAMPLE_RATE)
            log.info("microphone input device: %s", sd.query_devices(kind="input").get("name", "default"))
            self.events.put(("ready", ""))
            last_partial = ""

            def callback(indata, frames, time_info, status):
                if status:
                    log.warning("microphone: %s", status)
                if self._paused.is_set():
                    return
                try:
                    self._audio.put_nowait(bytes(indata))
                except queue.Full:
                    try:
                        self._audio.get_nowait()
                        self._audio.put_nowait(bytes(indata))
                    except queue.Empty:
                        pass
                    except queue.Full:
                        pass

            with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=4000,
                dtype="int16",
                channels=1,
                callback=callback,
            ):
                while self._running:
                    try:
                        pcm = self._audio.get(timeout=0.2)
                    except queue.Empty:
                        continue
                    if self._paused.is_set():
                        continue
                    if self._reset.is_set():
                        recognizer = KaldiRecognizer(model, SAMPLE_RATE)
                        self._reset.clear()
                        last_partial = ""
                        continue
                    if recognizer.AcceptWaveform(pcm):
                        text = json.loads(recognizer.Result()).get("text", "").strip()
                        last_partial = ""
                        if text:
                            log.info("heard: %s", text)
                            self.events.put(("final", text))
                    else:
                        partial = json.loads(recognizer.PartialResult()).get("partial", "").strip()
                        if partial and partial != last_partial:
                            last_partial = partial
                            if has_wake(partial):
                                self.events.put(("wake", partial))
                            else:
                                self.events.put(("partial", partial))
        except Exception as exc:
            log.exception("listener failed")
            self.events.put(("error", str(exc)))
