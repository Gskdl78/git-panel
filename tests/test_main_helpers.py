from main import build_full_panel
from tests.test_git_service import make_repo


def test_build_full_panel_has_all_sections(qtbot, tmp_path):
    svc = make_repo(tmp_path)
    panel = build_full_panel(svc)
    qtbot.addWidget(panel)
    assert len(panel.sections) == 5
    assert "main" in panel.header.text()
