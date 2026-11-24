"""Borderless desktop window, color-key transparent around the cat.

Other apps cover the cat. It keeps walking and listening underneath.
"""

import ctypes

import pygame
import win32api
import win32con
import win32gui

from pet.sprites import H, SCALE, frame_surface

MAGENTA = (255, 0, 128)
WIDTH = 168
HEIGHT = H * SCALE + 40


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def work_area():
    rect = RECT()
    ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
    return rect.left, rect.top, rect.right, rect.bottom


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class PetWindow:
    def __init__(self, x, y):
        pygame.display.set_caption("Kitty")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        self.font = pygame.font.SysFont("segoeui", 15)
        self.hwnd = pygame.display.get_wm_info()["window"]
        self._apply_style()
        self.move(x, y)
        self.rest_behind()

    def _apply_style(self):
        style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_NOACTIVATE
        style &= ~(win32con.WS_EX_APPWINDOW | win32con.WS_EX_TOPMOST)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, style)
        win32gui.SetLayeredWindowAttributes(
            self.hwnd, win32api.RGB(*MAGENTA), 0, win32con.LWA_COLORKEY
        )
        win32gui.SetWindowPos(
            self.hwnd,
            win32con.HWND_NOTOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE
            | win32con.SWP_NOSIZE
            | win32con.SWP_NOACTIVATE
            | win32con.SWP_FRAMECHANGED,
        )

    def move(self, x, y):
        self.x = int(x)
        self.y = int(y)
        win32gui.SetWindowPos(
            self.hwnd,
            0,
            self.x,
            self.y,
            0,
            0,
            win32con.SWP_NOSIZE
            | win32con.SWP_NOZORDER
            | win32con.SWP_NOACTIVATE
            | win32con.SWP_SHOWWINDOW,
        )

    def rest_behind(self):
        """Stay above the desktop and under normal app windows.

        The taskbar is topmost. Following that window pulls Kitty into the
        same band, which is why it used to paint over every program.
        """
        style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        if style & win32con.WS_EX_TOPMOST:
            win32gui.SetWindowLong(
                self.hwnd, win32con.GWL_EXSTYLE, style & ~win32con.WS_EX_TOPMOST
            )
            win32gui.SetWindowPos(
                self.hwnd,
                win32con.HWND_NOTOPMOST,
                0,
                0,
                0,
                0,
                win32con.SWP_NOMOVE
                | win32con.SWP_NOSIZE
                | win32con.SWP_NOACTIVATE
                | win32con.SWP_FRAMECHANGED,
            )

        desktop = win32gui.FindWindow("Progman", None)
        if not desktop:
            return
        above = win32gui.GetWindow(desktop, win32con.GW_HWNDPREV)
        if not above or above == self.hwnd:
            return
        above_style = win32gui.GetWindowLong(above, win32con.GWL_EXSTYLE)
        if above_style & win32con.WS_EX_TOPMOST:
            return
        win32gui.SetWindowPos(
            self.hwnd,
            above,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
        )

    def draw(self, cat):
        self.screen.fill(MAGENTA)
        image = frame_surface(cat.state, cat.frame, cat.facing)
        sprite_x = (WIDTH - image.get_width()) // 2
        sprite_y = HEIGHT - image.get_height()
        pygame.draw.ellipse(
            self.screen, (224, 200, 180),
            (sprite_x + 20, HEIGHT - 13, image.get_width() - 40, 7),
        )
        self.screen.blit(image, (sprite_x, sprite_y))
        if cat.bubble:
            self._bubble(cat.bubble)
        pygame.display.flip()

    def _bubble(self, text):
        size = 15
        font = self.font
        label = font.render(text, True, (59, 36, 25))
        while label.get_width() > WIDTH - 20 and size > 11:
            size -= 1
            font = pygame.font.SysFont("segoeui", size)
            label = font.render(text, True, (59, 36, 25))
        pad = 6
        rect = label.get_rect()
        rect.midtop = (WIDTH // 2, 6)
        box = rect.inflate(pad * 2, pad * 2)
        is_listening = text.lower() == "listening"
        fill = (224, 245, 234) if is_listening else (255, 248, 240)
        shadow = box.move(0, 2)
        pygame.draw.rect(self.screen, (120, 93, 76), shadow, border_radius=9)
        pygame.draw.rect(self.screen, fill, box, border_radius=9)
        border = (96, 116, 91) if is_listening else (59, 36, 25)
        pygame.draw.rect(self.screen, border, box, width=1, border_radius=9)
        self.screen.blit(label, rect)

    def popup(self, listening_paused, startup_on):
        menu = win32gui.CreatePopupMenu()
        pause_label = "Resume background listening" if listening_paused else "Pause background listening"
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1, pause_label)
        startup_flags = win32con.MF_STRING
        if startup_on:
            startup_flags |= win32con.MF_CHECKED
        win32gui.AppendMenu(menu, startup_flags, 2, "Start with Windows")
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
        win32gui.AppendMenu(menu, win32con.MF_STRING, 3, "Quit")
        cursor = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        command = win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_LEFTALIGN | win32con.TPM_RETURNCMD | win32con.TPM_RIGHTBUTTON,
            cursor[0],
            cursor[1],
            0,
            self.hwnd,
            None,
        )
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        win32gui.DestroyMenu(menu)
        return command
