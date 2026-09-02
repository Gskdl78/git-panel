"""單一實例鎖：每個終端機視窗（HWND）只允許一個 git-panel 面板。

鎖檔放在 %TEMP%/git-panel-<hwnd>.lock，內容為持有者 pid。
若 pid 已不存在（例如面板當掉沒清鎖），視為過期鎖並直接接手。
"""

import os
import tempfile

import psutil


def _lock_path(hwnd: int) -> str:
    return os.path.join(tempfile.gettempdir(), f"git-panel-{hwnd}.lock")


def acquire(hwnd: int) -> bool:
    path = _lock_path(hwnd)
    if os.path.exists(path):
        try:
            with open(path) as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                return False
        except (ValueError, OSError):
            pass
    with open(path, "w") as f:
        f.write(str(os.getpid()))
    return True


def release(hwnd: int) -> None:
    try:
        os.remove(_lock_path(hwnd))
    except OSError:
        pass
