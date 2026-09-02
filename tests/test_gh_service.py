import gh_service
from tests.test_git_service import make_repo


def test_repo_create_args_private():
    assert gh_service.repo_create_args("myrepo", True) == [
        "repo", "create", "myrepo", "--private",
        "--source=.", "--remote=origin", "--push",
    ]


def test_repo_create_args_public():
    assert "--public" in gh_service.repo_create_args("x", False)


def test_gh_available_follows_which(monkeypatch):
    monkeypatch.setattr(gh_service.shutil, "which", lambda _: None)
    assert not gh_service.gh_available()
    monkeypatch.setattr(gh_service.shutil, "which", lambda _: "C:/gh.exe")
    assert gh_service.gh_available()


def test_repo_create_without_gh_returns_failure(monkeypatch):
    monkeypatch.setattr(gh_service.shutil, "which", lambda _: None)
    r = gh_service.repo_create("C:/x", "n", True)
    assert not r.ok and r.code == 127


def test_has_remote(tmp_path):
    svc = make_repo(tmp_path)
    assert not svc.has_remote()
    svc.run("remote", "add", "origin", "https://example.com/x.git")
    assert svc.has_remote()
