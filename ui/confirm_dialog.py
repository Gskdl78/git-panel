from __future__ import annotations

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
    desc.setWordWrap(True)
    lay.addWidget(desc)

    lay.addWidget(QLabel("將執行："))
    cmd = QLabel(command)
    cmd.setWordWrap(True)
    cmd.setStyleSheet(
        "font-family: Consolas, monospace; background: #f2f2f2; padding: 6px; border-radius: 3px;"
    )
    lay.addWidget(cmd)

    if danger:
        warn = QLabel("⚠ 此操作不容易復原，請再次確認！")
        warn.setStyleSheet("color: #c00000; font-weight: bold;")
        lay.addWidget(warn)

    row = QHBoxLayout()
    row.addStretch()
    ok = QPushButton("我了解風險，執行" if danger else "確認")
    cancel = QPushButton("取消")
    if danger:
        ok.setStyleSheet("background: #c00000; color: white; padding: 4px 12px;")
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
