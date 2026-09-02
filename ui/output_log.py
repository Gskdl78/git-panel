from __future__ import annotations

import html

from PySide6.QtWidgets import QTextEdit


class OutputLog(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        self.setMaximumHeight(140)

    def log_command(self, command: str) -> None:
        self.append(f'<span style="color:#888">&gt; {html.escape(command)}</span>')

    def log_ok(self, text: str = "完成 ✓") -> None:
        self.append(f'<span style="color:#2a7a2a">{html.escape(text)}</span>')

    def log_error(self, raw: str, explanation: str | None = None) -> None:
        if explanation:
            self.append(
                f'<span style="color:#c00000;font-weight:bold">{html.escape(explanation)}</span>'
            )
        if raw.strip():
            self.append(f'<span style="color:#c00000">{html.escape(raw.strip())}</span>')
