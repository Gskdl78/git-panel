"""SessionStart hook 啟動器：找到 claude 進程、detached 啟動面板後立刻退出。"""

from __future__ import annotations

import os
import subprocess
import sys

import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
CLAUDE_EXES = {"node.exe", "claude.exe", "bun.exe"}


def find_claude_pid() -> int:
    try:
        for anc in psutil.Process(os.getpid()).parents():
            if anc.name().lower() in CLAUDE_EXES:
                return anc.pid
    except psutil.Error:
        pass
    return os.getppid()


def main() -> None:
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    subprocess.Popen(
        [
            pythonw,
            os.path.join(HERE, "main.py"),
            "--pid", str(find_claude_pid()),
            "--cwd", os.getcwd(),
        ],
        creationflags=(
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_NO_WINDOW
        ),
        close_fds=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    main()
