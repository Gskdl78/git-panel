import subprocess
import sys

import lockfile


def test_acquire_and_release():
    hwnd = 999901
    assert lockfile.acquire(hwnd)
    lockfile.release(hwnd)
    assert lockfile.acquire(hwnd)
    lockfile.release(hwnd)


def test_acquire_blocked_by_live_pid():
    hwnd = 999902
    assert lockfile.acquire(hwnd)  # 寫入目前進程 pid（存活中）
    assert not lockfile.acquire(hwnd)
    lockfile.release(hwnd)


def test_stale_lock_from_dead_pid(tmp_path):
    hwnd = 999903
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    import lockfile as lf
    with open(lf._lock_path(hwnd), "w") as f:
        f.write(str(p.pid))
    assert lf.acquire(hwnd)  # 死掉的 pid 視為過期鎖
    lf.release(hwnd)
