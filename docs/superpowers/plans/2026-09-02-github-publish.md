# 發佈到 GitHub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 推送/同步偵測無遠端時彈出發佈精靈：貼現有倉庫網址（純 git）或 gh repo create 新建（建庫＋設遠端＋推送一次完成）。

**Architecture:** 新 `gh_service.py` 封裝 gh 呼叫（比照 GitService.run 慣例）；新 `ui/publish_wizard.py` 承載精靈流程；`ui/commit_box.py` 的 `_push`/`_sync` 前置攔截。所有動作照舊經確認框。

**Tech Stack:** 既有（Python/PySide6/subprocess）＋ GitHub CLI（gh，執行期依賴，非測試依賴）

**Spec:** `docs/superpowers/specs/2026-09-02-github-publish-design.md`

## Global Constraints

- UI 全繁體中文；所有動作經確認框（含指令預覽）
- 測試絕不呼叫真實 gh、不連網、不在 GitHub 建立任何東西 — gh 一律 monkeypatch；git 部分用本地 bare repo
- gh 呼叫慣例：CREATE_NO_WINDOW、text、encoding="utf-8"、errors="replace"、stdin=subprocess.DEVNULL
- `confirm` 以模組層 import（monkeypatch 慣例）
- Commit 訊息 feat:/fix:/test:/docs: 前綴

---

### Task 1: gh_service + has_remote + 錯誤翻譯

**Files:**
- Create: `gh_service.py`, `tests/test_gh_service.py`
- Modify: `git_service.py`（附加 has_remote）, `errors.py`（附加 patterns）, `tests/test_errors.py`（附加）

**Interfaces:**
- Consumes: `git_service.GitResult`
- Produces: `gh_service.find_gh() -> str | None`、`gh_available() -> bool`、`gh_authed() -> bool`、`repo_create_args(name, private) -> list[str]`（純函式）、`repo_create(repo_path, name, private) -> GitResult`；`GitService.has_remote() -> bool`

- [ ] **Step 1: 寫失敗測試**

`tests/test_gh_service.py`:
```python
import gh_service
from tests.test_git_service import make_repo


def test_repo_create_args_private():
    assert gh_service.repo_create_args("myrepo", True) == [
        "repo", "create", "myrepo", "--private",
        "--source=.", "--remote=origin", "--push",
    ]


def test_repo_create_args_public():
    assert "--public" in gh_service.repo_create_args("x", False)


def test_gh_available_follows_which(monkeypatch):
    monkeypatch.setattr(gh_service.shutil, "which", lambda _: None)
    assert not gh_service.gh_available()
    monkeypatch.setattr(gh_service.shutil, "which", lambda _: "C:/gh.exe")
    assert gh_service.gh_available()


def test_repo_create_without_gh_returns_failure(monkeypatch):
    monkeypatch.setattr(gh_service.shutil, "which", lambda _: None)
    r = gh_service.repo_create("C:/x", "n", True)
    assert not r.ok and r.code == 127


def test_has_remote(tmp_path):
    svc = make_repo(tmp_path)
    assert not svc.has_remote()
    svc.run("remote", "add", "origin", "https://example.com/x.git")
    assert svc.has_remote()
```

`tests/test_errors.py` 附加：
```python
def test_gh_name_exists():
    assert "同名" in explain_error(err("Name already exists on this account"))


def test_gh_not_logged_in():
    msg = explain_error(err("To get started with GitHub CLI, please run:  gh auth login"))
    assert "gh auth login" in msg
```

- [ ] **Step 2: 執行測試確認失敗**

Run: `python -m pytest tests/test_gh_service.py tests/test_errors.py -v`
Expected: FAIL（ModuleNotFoundError: gh_service；AttributeError: has_remote；新 errors 測試 FAIL）

- [ ] **Step 3: 實作**

`gh_service.py`:
```python
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
```

`git_service.py` 附加到 GitService（clone staticmethod 之前）：
```python
    def has_remote(self) -> bool:
        return bool(self.run("remote").stdout.strip())
```

`errors.py` 的 `_PATTERNS` 附加（保持在清單尾端）：
```python
    ("Name already exists", "GitHub 上已有同名倉庫：請換一個倉庫名稱，或改用「貼現有倉庫網址」連到既有的倉庫。"),
    ("gh auth login", "尚未登入 GitHub CLI：請在終端機執行 gh auth login，用瀏覽器完成登入後再試一次。"),
    ("Could not resolve hostname", "連不上 GitHub：請檢查網路連線後再試。"),
```

- [ ] **Step 4: 執行測試確認通過**

Run: `python -m pytest tests/ -v`
Expected: 全部 passed

- [ ] **Step 5: Commit**

```bash
git add gh_service.py git_service.py errors.py tests/
git commit -m "feat: gh_service 與 has_remote、gh 錯誤翻譯"
```

---

### Task 2: 發佈精靈 + 推送/同步攔截

**Files:**
- Create: `ui/publish_wizard.py`, `tests/test_publish_wizard.py`
- Modify: `ui/commit_box.py`（_push/_sync 前置攔截）, `tests/test_commit_box.py`（附加攔截測試）

**Interfaces:**
- Consumes: Task 1 全部、`ui.confirm_dialog.confirm`、`GitPanel.service/.output/.refresh`、`GitService.push/run`
- Produces: `ui.publish_wizard.publish_wizard(panel) -> None`；內部 `_choose_mode(panel) -> str | None`（"url"/"create"/None）、`_publish_url(panel)`、`_ask_create(panel) -> tuple[str, bool] | None`、`_publish_create(panel)`（全為模組層名稱，可 monkeypatch）

- [ ] **Step 1: 寫失敗測試**

`tests/test_publish_wizard.py`:
```python
from git_service import GitResult, GitService
from ui.panel import GitPanel
from tests.test_git_service import make_repo


def make_panel(qtbot, tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    panel.refresh()
    return svc, panel


def test_publish_url_adds_remote_and_pushes(qtbot, tmp_path, monkeypatch):
    import ui.publish_wizard as pw
    svc, panel = make_panel(qtbot, tmp_path / "work")
    remote = tmp_path / "remote.git"
    GitService(str(tmp_path)).run("init", "--bare", "-b", "main", str(remote))
    monkeypatch.setattr(pw.QInputDialog, "getText", lambda *a, **k: (str(remote), True))
    monkeypatch.setattr(pw, "confirm", lambda *a, **k: True)
    pw._publish_url(panel)
    assert svc.has_remote()
    assert "main" in svc.run("ls-remote", "origin").stdout


def test_publish_url_cancel_no_side_effect(qtbot, tmp_path, monkeypatch):
    import ui.publish_wizard as pw
    svc, panel = make_panel(qtbot, tmp_path)
    monkeypatch.setattr(pw.QInputDialog, "getText", lambda *a, **k: ("x", True))
    monkeypatch.setattr(pw, "confirm", lambda *a, **k: False)
    pw._publish_url(panel)
    assert not svc.has_remote()
    assert panel.output.toPlainText() == ""


def test_publish_create_calls_gh(qtbot, tmp_path, monkeypatch):
    import ui.publish_wizard as pw
    svc, panel = make_panel(qtbot, tmp_path)
    calls = []
    monkeypatch.setattr(pw.gh_service, "gh_authed", lambda: True)
    monkeypatch.setattr(pw, "_ask_create", lambda p: ("myrepo", True))
    monkeypatch.setattr(pw, "confirm", lambda *a, **k: True)
    monkeypatch.setattr(
        pw.gh_service, "repo_create",
        lambda path, name, private: calls.append((path, name, private))
        or GitResult(True, "created", "", 0),
    )
    pw._publish_create(panel)
    assert calls == [(svc.repo_path, "myrepo", True)]
    assert "完成" in panel.output.toPlainText()


def test_publish_create_blocked_when_not_authed(qtbot, tmp_path, monkeypatch):
    import ui.publish_wizard as pw
    svc, panel = make_panel(qtbot, tmp_path)
    monkeypatch.setattr(pw.gh_service, "gh_authed", lambda: False)
    called = []
    monkeypatch.setattr(pw.gh_service, "repo_create", lambda *a: called.append(a))
    pw._publish_create(panel)
    assert called == []
    assert "gh auth login" in panel.output.toPlainText()
```

`tests/test_commit_box.py` 附加：
```python
def test_push_without_remote_opens_wizard(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    opened = []
    monkeypatch.setattr("ui.commit_box.publish_wizard", lambda p: opened.append(p))
    section.btn_push.click()
    assert opened == [panel]


def test_sync_without_remote_opens_wizard(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    opened = []
    monkeypatch.setattr("ui.commit_box.publish_wizard", lambda p: opened.append(p))
    section.btn_sync.click()
    assert opened == [panel]
```
（`make()` 建的 repo 無遠端；既有的 push/sync 測試都用 `make_with_remote`/有遠端情境，攔截不影響它們——若有既有測試因攔截失敗，代表其 repo 無遠端，需在該測試 repo 補 `remote add` 而非改產品碼。）

- [ ] **Step 2: 執行測試確認失敗**

Run: `python -m pytest tests/test_publish_wizard.py tests/test_commit_box.py -v`
Expected: FAIL（ModuleNotFoundError: ui.publish_wizard；attribute publish_wizard 不存在）

- [ ] **Step 3: 實作**

`ui/publish_wizard.py`:
```python
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
```

`ui/commit_box.py`：模組層加 `from ui.publish_wizard import publish_wizard`；`_push` 與 `_sync` 開頭加：
```python
        if not self.panel.service.has_remote():
            publish_wizard(self.panel)
            return
```
（`_sync` 的攔截放在讀取 `st` 之前；其餘不動。）

注意 `log_error("", 說明)` 在 raw 為空時只印說明 — 既有行為（`ui/output_log.py` 對空 raw 跳過），符合需求。

- [ ] **Step 4: 執行測試確認通過**

Run: `python -m pytest tests/ -v`
Expected: 全部 passed（含既有 test_commit_box 的 push/sync 測試——它們的 repo 有遠端，不受攔截影響；若失敗照 Step 1 附註處理測試 repo）

- [ ] **Step 5: Commit**

```bash
git add ui/publish_wizard.py ui/commit_box.py tests/
git commit -m "feat: 發佈到 GitHub 精靈（貼網址/gh 新建）與推送攔截"
```
