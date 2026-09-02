from ui.history_view import HistorySection
from ui.panel import GitPanel
from tests.test_git_service import make_repo


def test_lists_commits(qtbot, tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("第一筆")
    (tmp_path / "b.txt").write_text("hi")
    svc.stage("b.txt")
    svc.commit("第二筆")
    panel = GitPanel(svc)
    qtbot.addWidget(panel)
    section = HistorySection(panel)
    panel.add_section("歷史", section)
    panel.refresh()
    assert section.count() == 2
    assert "第二筆" in section.item(0).text()  # 最新在最上面
