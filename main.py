"""git-panel 主程式：組面板、磁吸到終端機視窗右緣、跟著終端機生命週期結束。"""

from __future__ import annotations

import argparse
import atexit
import os
import sys

import psutil
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

import lockfile
from git_service import GitService
from ui.advanced_bar import AdvancedSection
from ui.branch_bar import BranchSection
from ui.commit_box import CommitSection
from ui.file_list import FileListSection
from ui.history_view import HistorySection
from ui.panel import GitPanel
from ui.simple_panel import SimplePanel
from window_tracker import WindowTracker, find_terminal_hwnd


def build_full_panel(service: GitService) -> GitPanel:
    panel = GitPanel(service)
    panel.add_section("檔案變更", FileListSection(panel))
    panel.add_section("提交", CommitSection(panel))
    panel.add_section("分支", BranchSection(panel))
    panel.add_section("歷史", HistorySection(panel))
    panel.add_section("進階", AdvancedSection(panel))
    panel.refresh()
    return panel


def place_panel(panel, left: int, top: int, right: int, bottom: int) -> None:
    """把面板貼在終端機視窗右緣（傳入為實體像素，setGeometry 需要邏輯像素）。"""
    screen = panel.screen() or QApplication.primaryScreen()
    ratio = screen.devicePixelRatio() if screen else 1.0
    panel.setGeometry(
        int(right / ratio),
        int(top / ratio),
        GitPanel.WIDTH,
        int((bottom - top) / ratio),
    )


class App:
    """把面板、追蹤器、生命週期綁在一起；精簡模式完成後切換成完整面板。"""

    def __init__(self, app: QApplication, cwd: str, hwnd: int, claude_pid: int):
        self.app = app
        self.hwnd = hwnd
        self.panel = None
        self._last_rect = None

        service = GitService(cwd)
        if service.is_repo():
            self.panel = build_full_panel(service)
        else:
            self.panel = SimplePanel(cwd, self._on_repo_ready)

        self.tracker = WindowTracker(hwnd)
        self.tracker.geometry_changed.connect(self._on_geometry)
        # 注意：tracker 第一次 tick 會送出 minimized_changed(False) 當作初始狀態，
        # _on_minimized 只是 setVisible，重複收到同樣的值不會有副作用。
        self.tracker.minimized_changed.connect(self._on_minimized)
        self.tracker.closed.connect(app.quit)

        self.claude_watch = QTimer()
        self.claude_watch.timeout.connect(
            lambda: None if psutil.pid_exists(claude_pid) else app.quit()
        )
        self.claude_watch.start(1000)

        import win32gui

        rect = win32gui.GetWindowRect(hwnd)
        self._on_geometry(*rect)
        self.panel.show()

    def _on_geometry(self, left, top, right, bottom):
        self._last_rect = (left, top, right, bottom)
        place_panel(self.panel, left, top, right, bottom)

    def _on_minimized(self, minimized: bool):
        self.panel.setVisible(not minimized)

    def _on_repo_ready(self, repo_path: str):
        old = self.panel
        self.panel = build_full_panel(GitService(repo_path))
        if self._last_rect:
            place_panel(self.panel, *self._last_rect)
        self.panel.show()
        old.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, default=os.getppid())
    parser.add_argument("--cwd", default=os.getcwd())
    args = parser.parse_args()

    app = QApplication(sys.argv)
    # 順序很重要：find_terminal_hwnd 會沿祖先程序找「任何有視窗的祖先」當退路，
    # 必須在面板視窗建立／顯示之前呼叫，否則可能找到面板自己的視窗。
    hwnd = find_terminal_hwnd(args.pid)
    if hwnd is None:
        return 0  # 找不到終端機視窗就安靜退出
    if not lockfile.acquire(hwnd):
        return 0  # 這個終端機已經有面板了
    # 只在 acquire 成功後才註冊 release：release 是無條件刪檔，
    # 提前註冊會在「鎖被別人持有」時誤刪對方的鎖。
    atexit.register(lockfile.release, hwnd)

    App(app, args.cwd, hwnd, args.pid)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
