from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from errors import explain_error
from git_service import GitService
from ui.confirm_dialog import confirm
from ui.output_log import OutputLog
from ui.wizards import clone_dialog

WIDTH = 320


class SimplePanel(QWidget):
    WIDTH = WIDTH

    def __init__(self, cwd: str, on_ready: Callable[[str], None]):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.cwd = cwd
        self.on_ready = on_ready

        lay = QVBoxLayout(self)
        title = QLabel("這個資料夾還不是 git 專案")
        title.setWordWrap(True)
        title.setStyleSheet("font-weight: bold;")
        lay.addWidget(title)

        self.btn_init = QPushButton("初始化")
        self.btn_clone = QPushButton("Clone")
        lay.addWidget(self.btn_init)
        lay.addWidget(self.btn_clone)
        lay.addStretch()
        self.output = OutputLog()
        lay.addWidget(self.output)

        self.btn_init.clicked.connect(self._init)
        self.btn_clone.clicked.connect(self._clone)

    def _init(self) -> None:
        if not confirm(
            self,
            "初始化",
            f"在這個資料夾建立新的 git 專案：\n{self.cwd}",
            "git init -b main",
        ):
            return
        self.output.log_command("git init -b main")
        result = GitService(self.cwd).init()
        if result.ok:
            self.output.log_ok()
            self.on_ready(self.cwd)
        else:
            self.output.log_error(result.text, explain_error(result))

    def _clone(self) -> None:
        picked = clone_dialog(self, self.cwd)
        if not picked:
            return
        url, dest = picked
        if not confirm(
            self, "Clone", f"從 {url} 下載整個專案到：\n{dest}", f"git clone {url} {dest}"
        ):
            return
        self.output.log_command(f"git clone {url} {dest}")
        result = GitService.clone(url, dest)
        if result.ok:
            self.output.log_ok()
            self.on_ready(dest)
        else:
            self.output.log_error(result.text, explain_error(result))
