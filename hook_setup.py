"""SessionStart hook 安裝／移除：讀寫 ~/.claude/settings.json，只增修自己的那一條。"""

from __future__ import annotations

import json
import os
import sys

SETTINGS_PATH = os.path.expanduser("~/.claude/settings.json")
HERE = os.path.dirname(os.path.abspath(__file__))


def hook_command() -> str:
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    return f'"{pythonw}" "{os.path.join(HERE, "launch.py")}"'


def _all_commands(settings: dict) -> list[str]:
    return [
        h.get("command", "")
        for e in settings.get("hooks", {}).get("SessionStart", [])
        for h in e.get("hooks", [])
    ]


def add_hook(settings: dict, command: str) -> dict:
    if command in _all_commands(settings):
        return settings
    hooks = settings.setdefault("hooks", {})
    entries = hooks.setdefault("SessionStart", [])
    entries.append(
        {"matcher": "startup|resume", "hooks": [{"type": "command", "command": command}]}
    )
    return settings


def remove_hook(settings: dict, command: str) -> dict:
    entries = settings.get("hooks", {}).get("SessionStart", [])
    for e in entries:
        e["hooks"] = [h for h in e.get("hooks", []) if h.get("command") != command]
    settings.get("hooks", {})["SessionStart"] = [e for e in entries if e.get("hooks")]
    return settings


def _load() -> dict:
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(settings: dict) -> None:
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("install", "uninstall"):
        print("用法: python hook_setup.py install|uninstall")
        sys.exit(1)
    cmd = hook_command()
    if sys.argv[1] == "install":
        _save(add_hook(_load(), cmd))
        print(f"已安裝 SessionStart hook：{cmd}")
        print("下次開啟 Claude Code 時，Git 面板會自動出現。")
    else:
        _save(remove_hook(_load(), cmd))
        print("已移除 SessionStart hook。")


if __name__ == "__main__":
    main()
