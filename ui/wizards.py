from __future__ import annotations

import os

from PySide6.QtWidgets import QFileDialog, QInputDialog, QLineEdit

from git_service import Commit

RESET_MODES: dict[str, str] = {
    "soft": "保留所有變更（只把提交紀錄退回，檔案內容不動）",
    "mixed": "保留檔案變更，但取消暫存（預設模式）",
    "hard": "完全丟棄！檔案內容也會退回，之後的變更全部消失",
}


def reset_args(sha: str, mode: str) -> list[str]:
    return ["reset", f"--{mode}", sha]


def is_dangerous_reset(mode: str) -> bool:
    return mode == "hard"


def pick_branch(parent, branches: list[str], title: str) -> str | None:
    if not branches:
        return None
    name, ok = QInputDialog.getItem(parent, title, "選擇分支：", branches, 0, False)
    return name if ok else None


def pick_commit(parent, commits: list[Commit], title: str) -> str | None:
    if not commits:
        return None
    labels = [f"{c.sha}  {c.subject}" for c in commits]
    label, ok = QInputDialog.getItem(parent, title, "選擇提交：", labels, 0, False)
    if not ok:
        return None
    return label.split()[0]


def pick_reset_mode(parent) -> str | None:
    labels = [f"{mode}：{desc}" for mode, desc in RESET_MODES.items()]
    label, ok = QInputDialog.getItem(parent, "重設模式", "選擇模式：", labels, 1, False)
    if not ok:
        return None
    return label.split("：")[0]


def clone_dialog(parent, default_dir: str) -> tuple[str, str] | None:
    url, ok = QInputDialog.getText(
        parent, "Clone 專案", "GitHub 倉庫網址：", QLineEdit.Normal, ""
    )
    if not ok or not url.strip():
        return None
    dest_parent = QFileDialog.getExistingDirectory(parent, "選擇要放在哪個資料夾", default_dir)
    if not dest_parent:
        return None
    repo_name = url.rstrip("/").split("/")[-1].removesuffix(".git")
    return url.strip(), os.path.join(dest_parent, repo_name)
