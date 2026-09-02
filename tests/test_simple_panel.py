from git_service import GitService
from ui.simple_panel import SimplePanel


def test_init_creates_repo_and_calls_on_ready(qtbot, tmp_path, monkeypatch):
    ready = []
    panel = SimplePanel(str(tmp_path), ready.append)
    qtbot.addWidget(panel)
    monkeypatch.setattr("ui.simple_panel.confirm", lambda *a, **k: True)
    panel.btn_init.click()
    assert GitService(str(tmp_path)).is_repo()
    assert ready == [str(tmp_path)]


def test_init_cancelled_does_nothing(qtbot, tmp_path, monkeypatch):
    ready = []
    panel = SimplePanel(str(tmp_path), ready.append)
    qtbot.addWidget(panel)
    monkeypatch.setattr("ui.simple_panel.confirm", lambda *a, **k: False)
    panel.btn_init.click()
    assert not GitService(str(tmp_path)).is_repo()
    assert ready == []
