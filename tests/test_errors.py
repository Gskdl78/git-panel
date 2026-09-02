from errors import explain_error
from git_service import GitResult


def err(stderr):
    return GitResult(False, "", stderr, 1)


def test_rejected_push():
    msg = explain_error(err("! [rejected] main -> main (fetch first)"))
    assert "拉取" in msg


def test_conflict():
    msg = explain_error(err("CONFLICT (content): Merge conflict in a.txt"))
    assert "衝突" in msg


def test_auth():
    msg = explain_error(err("fatal: Authentication failed for 'https://github.com/x'"))
    assert "登入" in msg or "認證" in msg


def test_unknown_returns_none():
    assert explain_error(err("some random error")) is None


def test_gh_name_exists():
    assert "同名" in explain_error(err("Name already exists on this account"))


def test_gh_network_error():
    assert "連不上" in explain_error(err("error connecting to api.github.com"))


def test_gh_not_logged_in():
    msg = explain_error(err("To get started with GitHub CLI, please run:  gh auth login"))
    assert "gh auth login" in msg
