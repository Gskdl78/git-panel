import os

import window_tracker


def test_windows_for_pid_returns_list():
    assert isinstance(window_tracker.windows_for_pid(os.getpid()), list)


def test_find_terminal_hwnd_does_not_crash():
    hwnd = window_tracker.find_terminal_hwnd(os.getpid())
    assert hwnd is None or isinstance(hwnd, int)
