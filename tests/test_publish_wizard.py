from git_service import GitResult, GitService
from ui.panel import GitPanel
from tests.test_git_service import make_repo


def make_panel(qtbot, tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)  # 呼叫端可傳尚未建立的子目錄
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
