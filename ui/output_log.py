from __future__ import annotations

import html

from PySide6.QtWidgets import QTextEdit


def _fmt(text: str) -> str:
    """跳脫 HTML 並保留換行（append 走 rich text 路徑，\\n 會被折成空白）。"""
    return html.escape(text).replace("\n", "<br>")


class OutputLog(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        self.setMaximumHeight(140)

    def log_command(self, command: str) -> None:
        self.append(f'<span style="color:#8a8a8a">&gt; {_fmt(command)}</span>')

    def log_ok(self, text: str = "完成 ✓") -> None:
        self.append(f'<span style="color:#4ec94e">{_fmt(text)}</span>')

    def log_error(self, raw: str, explanation: str | None = None) -> None:
        if explanation:
            self.append(
                f'<span style="color:#f14c4c;font-weight:bold">{_fmt(explanation)}</span>'
            )
        if raw.strip():
            self.append(f'<span style="color:#f14c4c">{_fmt(raw.strip())}</span>')
