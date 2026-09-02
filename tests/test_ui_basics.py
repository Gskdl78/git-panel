from ui.output_log import OutputLog


def test_output_log_command_and_ok(qtbot):
    log = OutputLog()
    qtbot.addWidget(log)
    log.log_command("git push -u origin HEAD")
    log.log_ok()
    text = log.toPlainText()
    assert "git push" in text and "完成" in text


def test_output_log_error_with_explanation(qtbot):
    log = OutputLog()
    qtbot.addWidget(log)
    log.log_error("fatal: boom", "白話說明")
    text = log.toPlainText()
    assert "白話說明" in text and "fatal: boom" in text


def test_confirm_dialog_builds(qtbot):
    # 只驗證能建構不 exec（exec 會卡住測試）
    from ui.confirm_dialog import _build_dialog
    dlg = _build_dialog(None, "推送", "說明文字", "git push", danger=True)
    qtbot.addWidget(dlg)
    assert "確認" in dlg.windowTitle()


def test_danger_dialog_enter_defaults_to_cancel(qtbot):
    from PySide6.QtWidgets import QPushButton
    from ui.confirm_dialog import _build_dialog
    dlg = _build_dialog(None, "重設", "說明", "git reset --hard abc", danger=True)
    qtbot.addWidget(dlg)
    buttons = {b.text(): b for b in dlg.findChildren(QPushButton)}
    assert set(buttons) == {"我了解風險，執行", "取消"}
    assert not buttons["我了解風險，執行"].autoDefault()
    assert buttons["取消"].isDefault()


def test_confirm_dialog_labels_are_plain_text(qtbot):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel
    from ui.confirm_dialog import _build_dialog
    dlg = _build_dialog(None, "提交", "訊息：「<b>粗體</b>」", "git commit -m <b>粗體</b>", False)
    qtbot.addWidget(dlg)
    desc = next(l for l in dlg.findChildren(QLabel) if "訊息" in l.text())
    assert "<b>" in desc.text()
    assert desc.textFormat() == Qt.PlainText


def test_output_log_preserves_newlines(qtbot):
    from ui.output_log import OutputLog
    log = OutputLog()
    qtbot.addWidget(log)
    log.log_error("error: line1\nhint: line2")
    text = log.toPlainText()
    assert "line1" in text and "line2" in text
    assert "line1 hint" not in text  # 沒有被折成同一行
