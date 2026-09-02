from PySide6.QtCore import Qt

from ui.file_list import FileListSection
from ui.panel import GitPanel
from tests.test_git_service import make_repo


def make_panel(qtbot, tmp_path):
    svc = make_repo(tmp_path)
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    section = FileListSection(panel)
    panel.add_section("檔案變更", section)
    return svc, panel, section


def test_lists_changed_files(qtbot, tmp_path):
    svc, panel, section = make_panel(qtbot, tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    panel.refresh()
    assert section.count() == 1
    assert section.item(0).text() == "a.txt"
    assert section.item(0).checkState() == Qt.Unchecked


def test_check_stages_file(qtbot, tmp_path):
    svc, panel, section = make_panel(qtbot, tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    panel.refresh()
    section.item(0).setCheckState(Qt.Checked)
    assert svc.status().files[0].staged


def test_uncheck_unstages_file(qtbot, tmp_path):
    svc, panel, section = make_panel(qtbot, tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    panel.refresh()
    assert section.item(0).checkState() == Qt.Checked
    section.item(0).setCheckState(Qt.Unchecked)
    assert not svc.status().files[0].staged
