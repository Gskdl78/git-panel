from main import build_full_panel
from tests.test_git_service import make_repo


def test_build_full_panel_has_all_sections(qtbot, tmp_path):
    svc = make_repo(tmp_path)
    panel = build_full_panel(svc)
    qtbot.addWidget(panel)
    assert len(panel.sections) == 5
    assert "main" in panel.header.text()


def test_full_panel_respects_fixed_width(qtbot, tmp_path):
    """面板必須固定 320 寬；提交按鈕列（扣掉 8+8 邊距）不得超過 304。

    這裡不驗 panel.minimumSizeHint()：tmp_path 的目錄名很長，標題列 QLabel
    會把整體最小寬撐大，量到的是測試夾具而不是版面。
    """
    from ui.commit_box import CommitSection
    from ui.panel import GitPanel
    svc = make_repo(tmp_path)
    panel = build_full_panel(svc)
    qtbot.addWidget(panel)
    panel.show()
    assert panel.width() == GitPanel.WIDTH
    assert CommitSection(panel).minimumSizeHint().width() <= 304
