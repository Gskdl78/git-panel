import copy

from hook_setup import add_hook, remove_hook

CMD = "pythonw C:/x/launch.py"


def test_add_hook_to_empty_settings():
    s = add_hook({}, CMD)
    entries = s["hooks"]["SessionStart"]
    assert any(
        h["command"] == CMD
        for e in entries
        for h in e["hooks"]
    )


def test_add_hook_idempotent():
    s = add_hook(add_hook({}, CMD), CMD)
    entries = s["hooks"]["SessionStart"]
    count = sum(
        1 for e in entries for h in e["hooks"] if h["command"] == CMD
    )
    assert count == 1


def test_add_hook_preserves_existing():
    existing = {
        "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "other"}]}]},
        "model": "opus",
    }
    s = add_hook(copy.deepcopy(existing), CMD)
    assert s["model"] == "opus"
    all_cmds = [h["command"] for e in s["hooks"]["SessionStart"] for h in e["hooks"]]
    assert "other" in all_cmds and CMD in all_cmds


def test_remove_hook():
    s = remove_hook(add_hook({}, CMD), CMD)
    all_cmds = [
        h["command"]
        for e in s.get("hooks", {}).get("SessionStart", [])
        for h in e.get("hooks", [])
    ]
    assert CMD not in all_cmds
