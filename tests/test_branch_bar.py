from ui.branch_bar import BranchSection
from ui.panel import GitPanel
from tests.test_git_service import make_repo


def make(qtbot, tmp_path, monkeypatch):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    section = BranchSection(panel)
    panel.add_section("分支", section)
    monkeypatch.setattr("ui.panel.confirm", lambda *a, **k: True)
    return svc, panel, section


def test_combo_lists_branches(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    svc.create_branch("dev")
    svc.switch("main")
    panel.refresh()
    items = [section.combo.itemText(i) for i in range(section.combo.count())]
    assert set(items) == {"main", "dev"}
    assert section.combo.currentText() == "main"


def test_switch_branch(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    svc.create_branch("dev")
    svc.switch("main")
    panel.refresh()
    section.combo.setCurrentText("dev")
    section.btn_switch.click()
    assert svc.status().branch == "dev"


def test_new_branch(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    monkeypatch.setattr(
        "ui.branch_bar.QInputDialog.getText", lambda *a, **k: ("feature-x", True)
    )
    panel.refresh()
    section.btn_new.click()
    assert svc.status().branch == "feature-x"


def test_merge_branch(qtbot, tmp_path, monkeypatch):
    svc, panel, section = make(qtbot, tmp_path, monkeypatch)
    svc.create_branch("dev")
    (tmp_path / "b.txt").write_text("hi")
    svc.stage("b.txt")
    svc.commit("on dev")
    svc.switch("main")
    panel.refresh()
    monkeypatch.setattr("ui.branch_bar.pick_branch", lambda *a, **k: "dev")
    section.btn_merge.click()
    assert len(svc.log()) == 2
