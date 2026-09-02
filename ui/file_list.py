from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem, QPlainTextEdit, QVBoxLayout

from git_service import RepoStatus


class DiffDialog(QDialog):
    def __init__(self, parent, path: str, text: str):
        super().__init__(parent)
        self.setWindowTitle(f"差異：{path}")
        self.resize(560, 420)
        lay = QVBoxLayout(self)
        view = QPlainTextEdit(text or "（沒有差異內容）")
        view.setReadOnly(True)
        view.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        lay.addWidget(view)


class FileListSection(QListWidget):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        self.setMaximumHeight(150)
        self._updating = False
        self.itemChanged.connect(self._on_item_changed)
        self.itemDoubleClicked.connect(self._on_double_clicked)

    def refresh(self, status: RepoStatus) -> None:
        self._updating = True
        self.clear()
        for f in status.files:
            item = QListWidgetItem(f.path)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if f.staged else Qt.Unchecked)
            item.setData(Qt.UserRole, f)
            self.addItem(item)
        self._updating = False

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        if self._updating:
            return
        path = item.text()
        if item.checkState() == Qt.Checked:
            self.panel.output.log_command(f"git add -- {path}")
            self.panel.service.stage(path)
        else:
            self.panel.output.log_command(f"git reset HEAD -- {path}")
            self.panel.service.unstage(path)
        self.panel.refresh()

    def _on_double_clicked(self, item: QListWidgetItem) -> None:
        f = item.data(Qt.UserRole)
        path = item.text()
        if f is not None and f.index_status == "?":  # 未追蹤檔：顯示檔案內容
            try:
                import os
                full = os.path.join(self.panel.service.repo_path, path)
                with open(full, encoding="utf-8", errors="replace") as fh:
                    text = "（新檔案）\n" + fh.read()
            except OSError:
                text = "（無法讀取檔案）"
        else:
            text = self.panel.service.diff_file(path, staged=bool(f and f.staged))
        DiffDialog(self.panel, path, text).exec()
