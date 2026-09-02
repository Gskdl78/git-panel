from ui.advanced_bar import AdvancedSection
from ui.panel import GitPanel
from tests.test_git_service import make_repo


def make(qtbot, tmp_path, monkeypatch):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("v1")
    svc.stage("a.txt")
    svc.commit("c1")
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    section = AdvancedSection(panel)
    panel.add_section("進階", section)
    monkeypatch.setattr("ui.panel.confirm", lambda *a, **k: True)
    panel.refresh()
    return svc, panel, section


def test_stash_and_pop(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    (tmp_path / "a.txt").write_text("v2")
    panel.refresh()
    section.btn_stash.click()
    assert svc.status().files == []
    section.btn_pop.click()
    assert len(svc.status().files) == 1


def test_reset_hard(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    (tmp_path / "b.txt").write_text("hi")
    svc.stage("b.txt")
    svc.commit("c2")
    sha1 = svc.log()[1].sha
    monkeypatch.setattr("ui.advanced_bar.pick_commit", lambda *a, **k: sha1)
    monkeypatch.setattr("ui.advanced_bar.pick_reset_mode", lambda *a, **k: "hard")
    section.btn_reset.click()
    assert len(svc.log()) == 1


def test_revert(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    sha = svc.log()[0].sha
    monkeypatch.setattr("ui.advanced_bar.pick_commit", lambda *a, **k: sha)
    section.btn_revert.click()
    assert len(svc.log()) == 2


def test_tag(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    monkeypatch.setattr(
        "ui.advanced_bar.QInputDialog.getText", lambda *a, **k: ("v1.0", True)
    )
    section.btn_tag.click()
    assert "v1.0" in svc.run("tag").stdout
