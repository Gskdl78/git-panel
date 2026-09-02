from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


def _build_dialog(parent, title: str, description: str, command: str, danger: bool) -> QDialog:
    dlg = QDialog(parent)
    dlg.setWindowTitle(f"確認：{title}")
    dlg.setMinimumWidth(300)
    lay = QVBoxLayout(dlg)

    desc = QLabel(description)
    # 使用者內容（commit 訊息、網址）可能含標記，強制純文字避免被當富文字渲染
    desc.setTextFormat(Qt.PlainText)
    desc.setWordWrap(True)
    lay.addWidget(desc)

    lay.addWidget(QLabel("將執行："))
    cmd = QLabel(command)
    cmd.setTextFormat(Qt.PlainText)
    cmd.setWordWrap(True)
    cmd.setStyleSheet(
        "font-family: Consolas, monospace; background: #2a2a2a; color: #e0e0e0;"
        " padding: 6px; border-radius: 3px;"
    )
    lay.addWidget(cmd)

    if danger:
        warn = QLabel("⚠ 此操作不容易復原，請再次確認！")
        warn.setStyleSheet("color: #f14c4c; font-weight: bold;")
        lay.addWidget(warn)

    row = QHBoxLayout()
    row.addStretch()
    ok = QPushButton("我了解風險，執行" if danger else "確認")
    cancel = QPushButton("取消")
    if danger:
        # 需要 QPushButton:hover 這條：app 層 QSS 的 hover 比無選擇器的宣告優先，
        # 少了它滑過危險按鈕會變回灰色
        ok.setStyleSheet(
            "QPushButton { background: #c00000; color: white; padding: 4px 12px; }"
            "QPushButton:hover { background: #d61a1a; }"
        )
        # 危險操作：Enter 不應觸發破壞性按鈕，預設落在「取消」
        ok.setAutoDefault(False)
        cancel.setDefault(True)
    ok.clicked.connect(dlg.accept)
    cancel.clicked.connect(dlg.reject)
    row.addWidget(ok)
    row.addWidget(cancel)
    lay.addLayout(row)
    return dlg


def confirm(parent, title: str, description: str, command: str, danger: bool = False) -> bool:
    return _build_dialog(parent, title, description, command, danger).exec() == QDialog.Accepted
