"""GitHub CLI（gh）封裝：偵測、登入狀態、建立倉庫並推送。"""
from __future__ import annotations

import shutil
import subprocess

from git_service import GitResult


def find_gh() -> str | None:
    return shutil.which("gh")


def gh_available() -> bool:
    return find_gh() is not None


def _run_gh(repo_path: str | None, *args: str) -> GitResult:
    exe = find_gh()
    if exe is None:
        return GitResult(False, "", "gh not installed", 127)
    p = subprocess.run(
        [exe, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdin=subprocess.DEVNULL,
        cwd=repo_path,
    )
    return GitResult(p.returncode == 0, p.stdout, p.stderr, p.returncode)


def gh_authed() -> bool:
    return _run_gh(None, "auth", "status").ok


def repo_create_args(name: str, private: bool) -> list[str]:
    visibility = "--private" if private else "--public"
    return ["repo", "create", name, visibility, "--source=.", "--remote=origin", "--push"]


def repo_create(repo_path: str, name: str, private: bool) -> GitResult:
    return _run_gh(repo_path, *repo_create_args(name, private))
