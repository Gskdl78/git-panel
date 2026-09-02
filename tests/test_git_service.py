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


def test_status_no_ahead_behind_without_remote(tmp_path):
    svc = make_repo(tmp_path)
    st = svc.status()
    assert st.ahead == 0 and st.behind == 0
