"""Cat state: walk, idle, listen, and talk."""

import random
import time
import math

from pet.sprites import COUNTS


class Cat:
    def __init__(self, x, y, min_x, max_x, min_y, max_y):
        self.x = float(x)
        self.y = float(y)
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.facing = 1
        self.state = "walk"
        self.frame = 0
        self.frame_timer = 0.0
        self.state_timer = 0.0
        self.hold = random.uniform(0.4, 1.2)
        self.speed = 125.0
        self.target_x = float(x)
        self.target_y = float(y)
        self.dragging = False
        self.bubble = ""
        self.bubble_until = 0.0
        self.talk_until = 0.0
        self.listen_until = 0.0

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.frame = 0
            self.frame_timer = 0.0
            self.state_timer = 0.0

    def look_toward(self, center_x, window_width):
        middle = self.x + window_width / 2
        self.facing = 1 if middle < center_x else -1

    def start_listen(self, seconds=8.0):
        self.set_state("listen")
        self.bubble = "Listening"
        self.bubble_until = 0.0
        self.listen_until = time.time() + seconds

    def start_talk(self, bubble):
        self.set_state("talk")
        self.bubble = bubble
        self.bubble_until = 0.0
        self.talk_until = time.time() + 0.8

    def note(self, text, seconds=2.0):
        self.bubble = text
        self.bubble_until = time.time() + seconds

    def resume_roam(self):
        self.bubble = ""
        self.bubble_until = 0.0
        self.hold = random.uniform(2.0, 4.5)
        self.set_state("walk")

    def _choose_destination(self):
        # Pick visible desktop spots across both axes; bias toward the lower
        # half so Kitty still feels grounded while visiting the whole screen.
        lower = self.min_y + (self.max_y - self.min_y) * 0.35
        for _ in range(8):
            target_x = random.uniform(self.min_x, self.max_x)
            target_y = random.uniform(lower, self.max_y)
            if math.hypot(target_x - self.x, target_y - self.y) >= 120:
                break
        self.target_x = target_x
        self.target_y = target_y

    def _animate(self, dt):
        if self.state == "idle":
            interval = 0.16 if self.frame == 1 else 2.4
        elif self.state == "walk":
            interval = 0.13
        elif self.state == "talk":
            interval = 0.16
        else:
            interval = 0.35
        self.frame_timer += dt
        if self.frame_timer >= interval:
            self.frame_timer = 0.0
            self.frame = (self.frame + 1) % COUNTS[self.state]

    def update(self, dt):
        self._animate(dt)
        if (
            self.bubble_until
            and time.time() > self.bubble_until
            and self.state in ("idle", "walk")
        ):
            self.bubble = ""
            self.bubble_until = 0.0

        if self.dragging or self.state in ("listen", "talk"):
            return

        self.state_timer += dt
        if self.state == "walk":
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.hypot(dx, dy)
            step = self.speed * dt
            if distance > step and distance > 0:
                self.facing = 1 if dx > 0 else -1
                self.x += dx / distance * step
                self.y += dy / distance * step
            else:
                self.x = self.target_x
                self.y = self.target_y
                self.hold = random.uniform(0.4, 1.2)
                self.set_state("idle")
        elif self.state == "idle" and self.state_timer >= self.hold:
            self._choose_destination()
            self.hold = random.uniform(0.4, 1.2)
            self.set_state("walk")
