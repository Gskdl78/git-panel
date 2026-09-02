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
