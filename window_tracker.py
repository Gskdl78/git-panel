"""追蹤終端機視窗：找出 HWND，並以 QTimer 輪詢位置／最小化／關閉狀態。"""

from __future__ import annotations

import psutil
import win32gui
import win32process
from PySide6.QtCore import QObject, QTimer, Signal

TERMINAL_EXES = {
    "windowsterminal.exe",
    "conhost.exe",
    "cmd.exe",
    "powershell.exe",
    "pwsh.exe",
    "wezterm-gui.exe",
    "alacritty.exe",
}


def windows_for_pid(pid: int) -> list[int]:
    found: list[int] = []

    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and not win32gui.GetParent(hwnd):
            _, wpid = win32process.GetWindowThreadProcessId(hwnd)
            if wpid == pid:
                found.append(hwnd)
        return True

    win32gui.EnumWindows(cb, None)
    return found


def find_terminal_hwnd(start_pid: int) -> int | None:
    try:
        proc = psutil.Process(start_pid)
        chain = [proc] + proc.parents()
    except psutil.Error:
        chain = []
    for p in chain:  # 優先找已知終端機程式
        try:
            if p.name().lower() in TERMINAL_EXES:
                wins = windows_for_pid(p.pid)
                if wins:
                    return wins[0]
        except psutil.Error:
            continue
    for p in chain:  # 退而求其次：任何有視窗的祖先（排除 explorer）
        try:
            if p.name().lower() != "explorer.exe":
                wins = windows_for_pid(p.pid)
                if wins:
                    return wins[0]
        except psutil.Error:
            continue
    return None


class WindowTracker(QObject):
    geometry_changed = Signal(int, int, int, int)  # left, top, right, bottom（實體像素）
    minimized_changed = Signal(bool)
    closed = Signal()

    def __init__(self, hwnd: int, interval_ms: int = 50):
        super().__init__()
        self.hwnd = hwnd
        self._last_rect = None
        self._minimized = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(interval_ms)

    def _tick(self):
        if not win32gui.IsWindow(self.hwnd):
            self._timer.stop()
            self.closed.emit()
            return
        minimized = bool(win32gui.IsIconic(self.hwnd))
        if minimized != self._minimized:
            self._minimized = minimized
            self.minimized_changed.emit(minimized)
        if not minimized:
            rect = win32gui.GetWindowRect(self.hwnd)
            if rect != self._last_rect:
                self._last_rect = rect
                self.geometry_changed.emit(*rect)
