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


def test_diff_file_staged(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("line1\n")
    svc.stage("a.txt")
    svc.commit("c1")
    (tmp_path / "a.txt").write_text("line1\nline2\n")
    svc.stage("a.txt")
    assert "+line2" in svc.diff_file("a.txt", staged=True)
    assert svc.diff_file("a.txt") == ""  # 已全部進暫存區，工作區無差異


def test_show_commit(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi\n")
    svc.stage("a.txt")
    svc.commit("c1")
    sha = svc.log()[0].sha
    assert "c1" in svc.show_commit(sha)


def make_repo_with_remote(tmp_path):
    remote = tmp_path / "remote.git"
    GitService(str(tmp_path)).run("init", "--bare", "-b", "main", str(remote))
    work = tmp_path / "work"
    work.mkdir()
    svc = make_repo(work)
    svc.run("remote", "add", "origin", str(remote))
    return svc, work, remote


def test_push_and_ahead_count(tmp_path):
    svc, work, _ = make_repo_with_remote(tmp_path)
    (work / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    assert svc.push().ok
    assert svc.status().ahead == 0
    (work / "b.txt").write_text("hi")
    svc.stage("b.txt")
    svc.commit("c2")
    assert svc.status().ahead == 1


def test_sync_pull_then_push(tmp_path):
    svc, work, _ = make_repo_with_remote(tmp_path)
    (work / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    assert svc.sync().ok
    assert svc.status().ahead == 0


def test_clone(tmp_path):
    svc, work, remote = make_repo_with_remote(tmp_path)
    (work / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    svc.push()
    dest = tmp_path / "cloned"
    from git_service import GitService as GS

    assert GS.clone(str(remote), str(dest)).ok
    assert (dest / "a.txt").exists()


def test_init(tmp_path):
    d = tmp_path / "new"
    d.mkdir()
    svc = GitService(str(d))
    assert svc.init().ok
    assert svc.is_repo()


def test_branches_create_switch(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    assert svc.create_branch("dev").ok
    assert set(svc.branches()) == {"main", "dev"}
    assert svc.status().branch == "dev"
    assert svc.switch("main").ok
    assert svc.status().branch == "main"


def test_merge_and_conflict(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("base\n")
    svc.stage("a.txt")
    svc.commit("c1")
    svc.create_branch("dev")
    (tmp_path / "a.txt").write_text("dev\n")
    svc.stage("a.txt")
    svc.commit("dev change")
    svc.switch("main")
    (tmp_path / "a.txt").write_text("main\n")
    svc.stage("a.txt")
    svc.commit("main change")
    r = svc.merge("dev")
    assert not r.ok
    assert svc.conflicted_files() == ["a.txt"]
    assert svc.abort_merge().ok


def test_stash_and_pop(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    (tmp_path / "a.txt").write_text("changed")
    assert svc.stash().ok
    assert svc.status().files == []
    assert svc.stash_pop().ok
    assert len(svc.status().files) == 1


def test_reset_and_revert(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("v1")
    svc.stage("a.txt")
    svc.commit("c1")
    (tmp_path / "a.txt").write_text("v2")
    svc.stage("a.txt")
    svc.commit("c2")
    sha1 = svc.log()[1].sha
    assert svc.revert(svc.log()[0].sha).ok
    assert len(svc.log()) == 3
    assert svc.reset(sha1, "hard").ok
    assert len(svc.log()) == 1


def test_tag(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    assert svc.tag("v1.0").ok


def test_current_branch(tmp_path):
    svc = make_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hi")
    svc.stage("a.txt")
    svc.commit("c1")
    assert svc.current_branch() == "main"
    svc.create_branch("dev")
    assert svc.current_branch() == "dev"
