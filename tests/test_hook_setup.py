import copy

import hook_setup
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


def test_save_load_roundtrip_atomic(tmp_path, monkeypatch):
    # 絕不碰真正的 ~/.claude/settings.json
    target = tmp_path / "claude" / "settings.json"
    monkeypatch.setattr(hook_setup, "SETTINGS_PATH", str(target))

    hook_setup._save(add_hook({}, CMD))

    assert target.exists()
    assert not (tmp_path / "claude" / "settings.json.tmp").exists()  # 暫存檔已被 replace 掉

    loaded = hook_setup._load()
    all_cmds = [
        h["command"]
        for e in loaded["hooks"]["SessionStart"]
        for h in e["hooks"]
    ]
    assert CMD in all_cmds
