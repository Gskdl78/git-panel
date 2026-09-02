from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from git_service import RepoStatus
from ui.file_list import DiffDialog


class HistorySection(QListWidget):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        self.setMaximumHeight(120)
        self.setStyleSheet("font-size: 11px;")
        self.itemDoubleClicked.connect(self._on_double_clicked)

    def refresh(self, status: RepoStatus) -> None:
        self.clear()
        for c in self.panel.service.log(30):
            item = QListWidgetItem(f"{c.sha}  {c.subject}")
            item.setData(Qt.UserRole, c.sha)
            self.addItem(item)

    def _on_double_clicked(self, item: QListWidgetItem) -> None:
        sha = item.data(Qt.UserRole)
        DiffDialog(self.panel, sha, self.panel.service.show_commit(sha)).exec()
