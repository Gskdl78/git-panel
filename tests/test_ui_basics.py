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
