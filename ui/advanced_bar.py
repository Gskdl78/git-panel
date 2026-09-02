from __future__ import annotations

import os

from PySide6.QtWidgets import (
    QGridLayout,
    QInputDialog,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from errors import explain_error
from git_service import GitService, RepoStatus
from ui.confirm_dialog import confirm
from ui.wizards import (
    clone_dialog,
    is_dangerous_reset,
    pick_commit,
    pick_reset_mode,
    reset_args,
    RESET_MODES,
)


class AdvancedSection(QWidget):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.toggle = QToolButton()
        self.toggle.setText("進階 ▸")
        self.toggle.setCheckable(True)
        # background 明寫 transparent：app 層 QSS 會給 QToolButton 底色，
        # 這顆是「像文字的展開切換」而非按鈕，需保留原本扁平外觀
        self.toggle.setStyleSheet("border: none; background: transparent; color: #9a9a9a;")
        lay.addWidget(self.toggle)

        self.container = QWidget()
        grid = QGridLayout(self.container)
        grid.setContentsMargins(0, 0, 0, 0)
        self.btn_stash = QPushButton("暫存")
        self.btn_pop = QPushButton("取回")
        self.btn_revert = QPushButton("還原")
        self.btn_reset = QPushButton("重設")
        self.btn_tag = QPushButton("標籤")
        self.btn_clone = QPushButton("Clone")
        buttons = [
            self.btn_stash, self.btn_pop, self.btn_revert,
            self.btn_reset, self.btn_tag, self.btn_clone,
        ]
        for i, b in enumerate(buttons):
            grid.addWidget(b, i // 3, i % 3)
        self.container.hide()
        lay.addWidget(self.container)

        self.toggle.toggled.connect(self._on_toggle)
        self.btn_stash.clicked.connect(self._stash)
        self.btn_pop.clicked.connect(self._pop)
        self.btn_revert.clicked.connect(self._revert)
        self.btn_reset.clicked.connect(self._reset)
        self.btn_tag.clicked.connect(self._tag)
        self.btn_clone.clicked.connect(self._clone)

    def refresh(self, status: RepoStatus) -> None:
        pass

    def _on_toggle(self, checked: bool) -> None:
        self.container.setVisible(checked)
        self.toggle.setText("進階 ▾" if checked else "進階 ▸")

    def _stash(self) -> None:
        self.panel.run_action(
            "暫存",
            "把目前所有未提交的變更（含新檔案）先收起來，讓工作目錄變乾淨；之後可用「取回」拿回來。",
            ["stash", "push", "-u"],
        )

    def _pop(self) -> None:
        self.panel.run_action(
            "取回",
            "把最近一次「暫存」收起來的變更放回工作目錄。",
            ["stash", "pop"],
        )

    def _revert(self) -> None:
        sha = pick_commit(self.panel, self.panel.service.log(30), "還原提交")
        if not sha:
            return
        self.panel.run_action(
            "還原",
            f"建立一個新提交來抵銷 {sha} 的變更（原本的歷史紀錄會保留）。",
            ["revert", "--no-edit", sha],
        )

    def _reset(self) -> None:
        sha = pick_commit(self.panel, self.panel.service.log(30), "重設到哪個提交")
        if not sha:
            return
        mode = pick_reset_mode(self.panel)
        if not mode:
            return
        self.panel.run_action(
            "重設",
            f"把分支退回到 {sha}。模式 {mode}：{RESET_MODES[mode]}",
            reset_args(sha, mode),
            danger=is_dangerous_reset(mode),
        )

    def _tag(self) -> None:
        name, ok = QInputDialog.getText(
            self, "建立標籤", "標籤名稱（例如 v1.0）：", QLineEdit.Normal, ""
        )
        if not ok or not name.strip():
            return
        self.panel.run_action(
            "標籤",
            f"在目前的提交上建立標籤 {name.strip()}，方便日後找到這個版本。",
            ["tag", name.strip()],
        )

    def _clone(self) -> None:
        parent_dir = os.path.dirname(os.path.abspath(self.panel.service.repo_path))
        picked = clone_dialog(self.panel, parent_dir)
        if not picked:
            return
        url, dest = picked
        if not confirm(
            self.panel,
            "Clone",
            f"從 {url} 下載整個專案到：\n{dest}",
            f"git clone {url} {dest}",
        ):
            return
        self.panel.output.log_command(f"git clone {url} {dest}")
        result = GitService.clone(url, dest)
        if result.ok:
            self.panel.output.log_ok(f"完成 ✓ 已下載到 {dest}")
        else:
            self.panel.output.log_error(result.text, explain_error(result))
