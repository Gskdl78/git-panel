from ui.commit_box import CommitSection
from ui.panel import GitPanel
from tests.test_git_service import make_repo, make_repo_with_remote


def make(qtbot, tmp_path, monkeypatch, accept=True):
    svc = make_repo(tmp_path)
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    section = CommitSection(panel)
    panel.add_section("提交", section)
    monkeypatch.setattr("ui.panel.confirm", lambda *a, **k: accept)
    return svc, panel, section


def test_commit_with_message(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    panel.refresh()
    section.message.setPlainText("我的提交")
    section.btn_commit.click()
    assert svc.log()[0].subject == "我的提交"
    assert section.message.toPlainText() == ""  # 成功後清空


def test_commit_empty_message_blocked(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    panel.refresh()
    monkeypatch.setattr(
        "ui.commit_box.QMessageBox.warning", lambda *a, **k: None
    )
    section.btn_commit.click()
    assert svc.log() == []  # 沒有訊息不會提交


def test_commit_nothing_staged_blocked(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    (tmp_path / "a.txt").write_text("hi")
    panel.refresh()
    monkeypatch.setattr(
        "ui.commit_box.QMessageBox.warning", lambda *a, **k: None
    )
    section.message.setPlainText("msg")
    section.btn_commit.click()
    assert svc.log() == []


def make_with_remote(qtbot, tmp_path, monkeypatch, accept=True):
    """同步走自己的確認框（模組層 import），故 patch ui.commit_box.confirm。"""
    svc, work, _ = make_repo_with_remote(tmp_path)
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    section = CommitSection(panel)
    panel.add_section("提交", section)
    (work / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    panel.refresh()
    monkeypatch.setattr("ui.commit_box.confirm", lambda *a, **k: accept)
    return svc, panel, section


def remote_has_main(svc) -> bool:
    return "refs/heads/main" in svc.run("ls-remote", "origin", "main").stdout


def test_sync_pulls_then_pushes(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make_with_remote(qtbot, tmp_path, monkeypatch)
    section.btn_sync.click()
    assert remote_has_main(svc)  # 已推上遠端
    assert "git pull --rebase" in panel.output.toPlainText()  # 有寫進輸出區


def test_sync_cancel_does_nothing(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make_with_remote(qtbot, tmp_path, monkeypatch, accept=False)
    section.btn_sync.click()
    assert not remote_has_main(svc)  # 取消後未推送
    assert panel.output.toPlainText().strip() == ""
