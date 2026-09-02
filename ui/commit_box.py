from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from errors import explain_error
from git_service import RepoStatus


class CommitSection(QWidget):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.message = QTextEdit()
        self.message.setPlaceholderText("輸入 commit 訊息…")
        self.message.setMaximumHeight(60)
        lay.addWidget(self.message)

        row = QHBoxLayout()
        self.btn_commit = QPushButton("提交")
        self.btn_push = QPushButton("推送")
        self.btn_pull = QPushButton("拉取")
        self.btn_sync = QPushButton("同步")
        for b in (self.btn_commit, self.btn_push, self.btn_pull, self.btn_sync):
            row.addWidget(b)
        lay.addLayout(row)

        self.btn_commit.clicked.connect(self._commit)
        self.btn_push.clicked.connect(self._push)
        self.btn_pull.clicked.connect(self._pull)
        self.btn_sync.clicked.connect(self._sync)

    def refresh(self, status: RepoStatus) -> None:
        pass  # 提交區沒有需要隨狀態更新的顯示

    def _commit(self) -> None:
        msg = self.message.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "無法提交", "請先輸入 commit 訊息。")
            return
        staged = [f for f in self.panel.status.files if f.staged]
        if not staged:
            QMessageBox.warning(self, "無法提交", "還沒有勾選任何檔案（沒有已暫存的變更）。")
            return
        ok = self.panel.run_action(
            "提交",
            f"將已勾選的 {len(staged)} 個檔案提交到本地紀錄，訊息：「{msg}」。",
            ["commit", "-m", msg],
        )
        if ok:
            self.message.clear()

    def _push(self) -> None:
        st = self.panel.status
        n = f"{st.ahead} 個" if st.ahead else "本地"
        self.panel.run_action(
            "推送",
            f"將 {st.branch} 分支的{n}提交上傳到遠端（origin）。",
            ["push", "-u", "origin", "HEAD"],
        )

    def _pull(self) -> None:
        self.panel.run_action(
            "拉取",
            "從遠端（origin）下載最新的提交並合併到目前分支。",
            ["pull"],
        )

    def _sync(self) -> None:
        from ui.confirm_dialog import confirm

        st = self.panel.status
        if not confirm(
            self.panel,
            "同步",
            f"先把遠端新提交拉下來（rebase 方式），再把你的 {st.ahead} 個提交推上去。",
            "git pull --rebase\ngit push -u origin HEAD",
        ):
            return
        self.panel.output.log_command("git pull --rebase && git push")
        result = self.panel.service.sync()
        if result.ok:
            self.panel.output.log_ok()
        else:
            self.panel.output.log_error(result.text, explain_error(result))
        self.panel.refresh()
