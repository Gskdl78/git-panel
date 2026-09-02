from ui.wizards import RESET_MODES, is_dangerous_reset, reset_args


def test_reset_args():
    assert reset_args("abc123", "hard") == ["reset", "--hard", "abc123"]
    assert reset_args("abc123", "soft") == ["reset", "--soft", "abc123"]


def test_danger_levels():
    assert is_dangerous_reset("hard")
    assert not is_dangerous_reset("soft")
    assert not is_dangerous_reset("mixed")


def test_reset_modes_have_chinese_descriptions():
    assert set(RESET_MODES) == {"soft", "mixed", "hard"}
    for desc in RESET_MODES.values():
        assert len(desc) > 4
