from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from errors import explain_error
from git_service import GitService, RepoStatus
from ui.confirm_dialog import confirm
from ui.output_log import OutputLog


class GitPanel(QWidget):
    WIDTH = 320

    def __init__(self, service: GitService):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.service = service
        self.status = RepoStatus()
        self.sections: list = []

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        self.header = QLabel()
        self.header.setStyleSheet("font-weight: bold; font-size: 13px;")
        root.addWidget(self.header)

        self.body = QVBoxLayout()
        self.body.setSpacing(6)
        root.addLayout(self.body)
        root.addStretch()

        root.addWidget(self._section_label("輸出"))
        self.output = OutputLog()
        root.addWidget(self.output)

    @staticmethod
    def _section_label(title: str) -> QLabel:
        lbl = QLabel(f"─── {title} ───")
        lbl.setStyleSheet("color: #999; font-size: 11px;")
        return lbl

    def add_section(self, title: str, widget) -> None:
        self.body.addWidget(self._section_label(title))
        self.body.addWidget(widget)
        self.sections.append(widget)

    def refresh(self) -> None:
        st = self.service.status()
        self.status = st
        parts = [f"📁 {os.path.basename(os.path.abspath(self.service.repo_path))}"]
        if st.branch:
            parts.append(f"● {st.branch}")
        if st.ahead:
            parts.append(f"↑{st.ahead}")
        if st.behind:
            parts.append(f"↓{st.behind}")
        self.header.setText("  ".join(parts))
        for section in self.sections:
            section.refresh(st)

    def run_action(
        self, title: str, description: str, args: list[str], danger: bool = False
    ) -> bool:
        command = "git " + " ".join(args)
        if not confirm(self, title, description, command, danger):
            return False
        self.output.log_command(command)
        result = self.service.run(*args)
        if result.ok:
            self.output.log_ok()
        else:
            self.output.log_error(result.text, explain_error(result))
        self.refresh()
        return result.ok
