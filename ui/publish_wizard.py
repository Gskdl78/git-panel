"""發佈到 GitHub 精靈：貼現有倉庫網址（純 git）或 gh repo create 新建。"""
from __future__ import annotations

import os

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

import gh_service
from errors import explain_error
from ui.confirm_dialog import confirm


def _choose_mode(panel) -> str | None:
    """回傳 'url'、'create' 或 None（取消）。"""
    dlg = QDialog(panel)
    dlg.setWindowTitle("發佈到 GitHub")
    lay = QVBoxLayout(dlg)
    info = QLabel("這個專案還沒連到遠端倉庫，要怎麼發佈？")
    info.setWordWrap(True)
    lay.addWidget(info)
    rb_url = QRadioButton("貼現有倉庫網址（先在 GitHub 建好空倉庫）")
    rb_create = QRadioButton("新建 GitHub 倉庫（自動建立並推送）")
    rb_url.setChecked(True)
    lay.addWidget(rb_url)
    lay.addWidget(rb_create)
    if not gh_service.gh_available():
        rb_create.setEnabled(False)
        hint = QLabel(
            "（新建功能需要 GitHub CLI：請先在終端機執行 "
            "winget install GitHub.cli，再執行 gh auth login 登入）"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #9a9a9a; font-size: 11px;")
        lay.addWidget(hint)
    row = QHBoxLayout()
    row.addStretch()
    ok = QPushButton("下一步")
    cancel = QPushButton("取消")
    ok.clicked.connect(dlg.accept)
    cancel.clicked.connect(dlg.reject)
    row.addWidget(ok)
    row.addWidget(cancel)
    lay.addLayout(row)
    if dlg.exec() != QDialog.Accepted:
        return None
    return "create" if rb_create.isChecked() else "url"


def _publish_url(panel) -> None:
    url, ok = QInputDialog.getText(
        panel, "貼現有倉庫網址", "GitHub 倉庫網址：", QLineEdit.Normal, ""
    )
    if not ok or not url.strip():
        return
    url = url.strip()
    if not confirm(
        panel,
        "發佈",
        f"將這個專案連到 {url}，並把目前分支推送上去。",
        f"git remote add origin {url}\ngit push -u origin HEAD",
    ):
        return
    panel.output.log_command(f"git remote add origin {url}")
    r = panel.service.run("remote", "add", "origin", url)
    if not r.ok:
        panel.output.log_error(r.text, explain_error(r))
        return
    panel.output.log_command("git push -u origin HEAD")
    r = panel.service.push()
    if r.ok:
        panel.output.log_ok()
    else:
        panel.output.log_error(r.text, explain_error(r))
    panel.refresh()


def _ask_create(panel) -> tuple[str, bool] | None:
    """回傳 (倉庫名, 是否私人) 或 None（取消）。"""
    dlg = QDialog(panel)
    dlg.setWindowTitle("新建 GitHub 倉庫")
    lay = QVBoxLayout(dlg)
    lay.addWidget(QLabel("倉庫名稱："))
    name_edit = QLineEdit(os.path.basename(os.path.abspath(panel.service.repo_path)))
    lay.addWidget(name_edit)
    rb_private = QRadioButton("私人（只有你看得到）")
    rb_public = QRadioButton("公開（所有人都看得到）")
    rb_private.setChecked(True)
    lay.addWidget(rb_private)
    lay.addWidget(rb_public)
    row = QHBoxLayout()
    row.addStretch()
    ok = QPushButton("下一步")
    cancel = QPushButton("取消")
    ok.clicked.connect(dlg.accept)
    cancel.clicked.connect(dlg.reject)
    row.addWidget(ok)
    row.addWidget(cancel)
    lay.addLayout(row)
    if dlg.exec() != QDialog.Accepted:
        return None
    name = name_edit.text().strip()
    if not name:
        return None
    return name, rb_private.isChecked()


def _publish_create(panel) -> None:
    if not gh_service.gh_authed():
        panel.output.log_error(
            "",
            "尚未登入 GitHub CLI：請在終端機執行 gh auth login，"
            "用瀏覽器完成登入後再按一次「推送」。",
        )
        return
    picked = _ask_create(panel)
    if not picked:
        return
    name, private = picked
    kind = "私人" if private else "公開"
    args_preview = "gh " + " ".join(gh_service.repo_create_args(name, private))
    if not confirm(
        panel,
        "發佈",
        f"在 GitHub 建立{kind}倉庫「{name}」，設為遠端並把目前內容推送上去。",
        args_preview,
    ):
        return
    panel.output.log_command(args_preview)
    r = gh_service.repo_create(panel.service.repo_path, name, private)
    if r.ok:
        panel.output.log_ok(f"完成 ✓ 已發佈到 GitHub（{name}）")
    else:
        panel.output.log_error(r.text, explain_error(r))
    panel.refresh()


def publish_wizard(panel) -> None:
    mode = _choose_mode(panel)
    if mode == "url":
        _publish_url(panel)
    elif mode == "create":
        _publish_create(panel)
