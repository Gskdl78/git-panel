from ui.panel import GitPanel
from tests.test_git_service import make_repo


def test_panel_refresh_header(qtbot, tmp_path, monkeypatch):
    svc = make_repo(tmp_path)
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    panel.refresh()
    assert "main" in panel.header.text()


def test_run_action_cancel_does_nothing(qtbot, tmp_path, monkeypatch):
    svc = make_repo(tmp_path)
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    monkeypatch.setattr("ui.panel.confirm", lambda *a, **k: False)
    assert panel.run_action("測試", "說明", ["status"]) is False
    assert panel.output.toPlainText() == ""


def test_run_action_confirmed_runs_and_logs(qtbot, tmp_path, monkeypatch):
    svc = make_repo(tmp_path)
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    monkeypatch.setattr("ui.panel.confirm", lambda *a, **k: True)
    assert panel.run_action("測試", "說明", ["status"]) is True
    assert "git status" in panel.output.toPlainText()


def test_run_action_failure_logs_error(qtbot, tmp_path, monkeypatch):
    svc = make_repo(tmp_path)
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    monkeypatch.setattr("ui.panel.confirm", lambda *a, **k: True)
    assert panel.run_action("測試", "說明", ["merge", "no-such-branch"]) is False
    assert "no-such-branch" in panel.output.toPlainText() or "合併" in panel.output.toPlainText()
