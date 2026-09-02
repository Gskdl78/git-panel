from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from git_service import RepoStatus
from ui.wizards import pick_branch


class BranchSection(QWidget):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.combo = QComboBox()
        lay.addWidget(self.combo)

        row = QHBoxLayout()
        self.btn_switch = QPushButton("切換")
        self.btn_new = QPushButton("新增")
        self.btn_merge = QPushButton("合併")
        self.btn_abort = QPushButton("中止合併")
        self.btn_abort.setStyleSheet("color: #c00000;")
        self.btn_abort.hide()
        for b in (self.btn_switch, self.btn_new, self.btn_merge):
            row.addWidget(b)
        lay.addLayout(row)
        lay.addWidget(self.btn_abort)

        self.btn_switch.clicked.connect(self._switch)
        self.btn_new.clicked.connect(self._new)
        self.btn_merge.clicked.connect(self._merge)
        self.btn_abort.clicked.connect(self._abort)

    def refresh(self, status: RepoStatus) -> None:
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItems(self.panel.service.branches())
        self.combo.setCurrentText(status.branch)
        self.combo.blockSignals(False)
        conflicts = self.panel.service.conflicted_files()
        self.btn_abort.setVisible(bool(conflicts))
        if conflicts:
            self.panel.output.log_error(
                "衝突檔案：" + "、".join(conflicts),
                "有合併衝突待解決，可交給 Claude Code 或手動處理後提交。",
            )

    def _switch(self) -> None:
        target = self.combo.currentText()
        if not target or target == self.panel.status.branch:
            return
        self.panel.run_action(
            "切換",
            f"從 {self.panel.status.branch} 切換到 {target} 分支，工作目錄檔案會跟著變。",
            ["switch", target],
        )

    def _new(self) -> None:
        name, ok = QInputDialog.getText(
            self, "新增分支", "新分支名稱：", QLineEdit.Normal, ""
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        self.panel.run_action(
            "新增",
            f"以目前的 {self.panel.status.branch} 為起點建立新分支 {name} 並切換過去。",
            ["switch", "-c", name],
        )

    def _merge(self) -> None:
        others = [b for b in self.panel.service.branches() if b != self.panel.status.branch]
        source = pick_branch(self.panel, others, "合併分支")
        if not source:
            return
        self.panel.run_action(
            "合併",
            f"把 {source} 分支的提交合併進目前的 {self.panel.status.branch} 分支。",
            ["merge", source],
        )

    def _abort(self) -> None:
        self.panel.run_action(
            "中止合併",
            "放棄這次合併，回到合併前的狀態。",
            ["merge", "--abort"],
        )
