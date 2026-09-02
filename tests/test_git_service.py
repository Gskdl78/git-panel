import pytest

from git_service import GitService


def make_repo(tmp_path):
    svc = GitService(str(tmp_path))
    assert svc.run("init", "-b", "main").ok
    svc.run("config", "user.email", "t@t.t")
    svc.run("config", "user.name", "t")
    return svc


def test_run_returns_result(tmp_path):
    svc = GitService(str(tmp_path))
    r = svc.run("--version")
    assert r.ok and "git version" in r.stdout


def test_is_repo(tmp_path):
    svc = GitService(str(tmp_path))
    assert not svc.is_repo()
    svc.run("init", "-b", "main")
    assert svc.is_repo()


def test_status_untracked_file(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    st = svc.status()
    assert st.branch == "main"
    assert len(st.files) == 1
    f = st.files[0]
    assert f.path == "a.txt" and not f.staged


def test_status_staged_file(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.run("add", "a.txt")
    st = svc.status()
    assert st.files[0].staged


def test_status_chinese_filename(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "中文檔名.txt").write_text("hi", encoding="utf-8")
    st = svc.status()
    assert st.files[0].path == "中文檔名.txt"
    assert svc.run("add", "--", st.files[0].path).ok  # 路徑可回饋給 git 使用


def test_status_no_ahead_behind_without_remote(tmp_path):
    svc = make_repo(tmp_path)
    st = svc.status()
    assert st.ahead == 0 and st.behind == 0


def test_stage_unstage(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    assert svc.status().files[0].staged
    svc.unstage("a.txt")
    assert not svc.status().files[0].staged


def test_commit_and_log(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    assert svc.commit("第一個提交").ok
    commits = svc.log()
    assert len(commits) == 1 and commits[0].subject == "第一個提交"
    assert svc.status().files == []


def test_diff_file(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("line1\n")
    svc.stage("a.txt")
    svc.commit("c1")
    (tmp_path / "a.txt").write_text("line1\nline2\n")
    assert "+line2" in svc.diff_file("a.txt")


def test_show_commit(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi\n")
    svc.stage("a.txt")
    svc.commit("c1")
    sha = svc.log()[0].sha
    assert "c1" in svc.show_commit(sha)
