"""Original 32x32 pixel tabby. Frames scale up with nearest-neighbor."""

from functools import lru_cache

import pygame

W = H = 32
SCALE = 4

OUTLINE = (59, 36, 25, 255)
FUR = (242, 163, 72, 255)
FUR_DEEP = (214, 122, 46, 255)
STRIPE = (176, 86, 38, 255)
WHITE = (255, 247, 238, 255)
PINK = (244, 150, 166, 255)
NOSE = (214, 96, 114, 255)
EYE = (42, 32, 28, 255)
SHINE = (255, 255, 255, 255)
MOUTH = (122, 52, 60, 255)
PAW = (255, 236, 224, 255)

COUNTS = {"idle": 2, "walk": 4, "listen": 2, "talk": 2}


def _grid():
    return [[None for _ in range(W)] for _ in range(H)]


def _fill(grid, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= xx < W and 0 <= yy < H and color is not None:
                grid[yy][xx] = color


def _dot(grid, x, y, color):
    if 0 <= x < W and 0 <= y < H and color is not None:
        grid[y][x] = color


def _outline(grid):
    solid = [(x, y) for y in range(H) for x in range(W) if grid[y][x] is not None]
    edge = []
    for x, y in solid:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and grid[ny][nx] is None:
                edge.append((nx, ny))
    for x, y in edge:
        if grid[y][x] is None:
            grid[y][x] = OUTLINE


def _paint(pose, frame):
    grid = _grid()
    bob = -1 if pose == "walk" and frame in (1, 3) else 0

    def fill(x, y, w, h, color):
        _fill(grid, x, y + bob, w, h, color)

    def dot(x, y, color):
        _dot(grid, x, y + bob, color)

    ear_lift = -2 if pose == "listen" else 0
    wag = frame if pose == "walk" else (1 if pose == "talk" and frame else 0)
    tails = (
        ((4, 14), (5, 16), (7, 18), (9, 20)),
        ((5, 12), (6, 14), (8, 16), (9, 19)),
        ((4, 15), (5, 17), (7, 19), (9, 20)),
        ((6, 13), (7, 15), (8, 17), (9, 19)),
    )
    for x, y in tails[wag % 4]:
        fill(x, y, 2, 2, FUR_DEEP)
    dot(3, 12 + (wag % 2), STRIPE)

    for y, x, w in ((6, 12, 2), (7, 11, 4), (8, 11, 5)):
        fill(x, y + ear_lift, w, 1, FUR)
    fill(12, 8 + ear_lift, 2, 1, PINK)

    for y, x, w in ((3, 20, 2), (4, 19, 4), (5, 18, 5), (6, 18, 6), (7, 18, 6)):
        fill(x, y + ear_lift, w, 1, FUR)
    fill(20, 6 + ear_lift, 2, 2, PINK)

    fill(12, 8, 14, 9, FUR)
    fill(15, 9, 2, 2, STRIPE)
    fill(20, 13, 6, 4, WHITE)

    if pose == "idle" and frame == 1:
        fill(21, 13, 4, 1, EYE)
    elif pose == "listen":
        fill(20, 11, 4, 4, EYE)
        dot(21, 12, SHINE)
        if frame == 1:
            dot(22, 12, SHINE)
    else:
        fill(21, 12, 3, 3, EYE)
        dot(22, 13, SHINE)

    fill(24, 14, 2, 2, NOSE)
    if pose == "talk":
        fill(22, 16, 4, 2 if frame == 0 else 1, MOUTH)
    else:
        fill(23, 16, 2, 1, MOUTH)

    for y in (14, 16):
        dot(27, y, WHITE)
        dot(28, y, WHITE)

    fill(10, 16, 12, 8, FUR)
    fill(13, 17, 2, 5, STRIPE)
    fill(17, 17, 2, 4, STRIPE)
    fill(14, 20, 4, 3, WHITE)

    if pose == "walk":
        # Back leg, then front leg. A smaller y lifts that paw.
        steps = ((10, 23, 20, 21), (11, 23, 19, 23), (12, 21, 18, 23), (11, 23, 19, 23))
        back_x, back_y, front_x, front_y = steps[frame]
    else:
        back_x, back_y, front_x, front_y = 11, 23, 19, 23

    fill(back_x, back_y, 3, 5, FUR)
    fill(back_x, back_y + 4, 4, 2, PAW)
    fill(front_x, front_y, 3, 5, FUR_DEEP)
    fill(front_x, front_y + 4, 4, 2, PAW)

    _outline(grid)
    return grid


def _surface(pose, frame):
    grid = _paint(pose, frame)
    raw = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(H):
        for x in range(W):
            color = grid[y][x]
            if color is not None:
                raw.set_at((x, y), color)
    return pygame.transform.scale(raw, (W * SCALE, H * SCALE))


@lru_cache(maxsize=None)
def frame_surface(pose, index, facing):
    count = COUNTS[pose]
    image = _surface(pose, index % count)
    if facing < 0:
        return pygame.transform.flip(image, True, False)
    return image
