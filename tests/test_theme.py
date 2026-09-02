from ui.theme import DARK_QSS, apply_dark_theme


def test_dark_qss_has_core_colors():
    assert "#1e1e1e" in DARK_QSS and "QPushButton" in DARK_QSS
    # 樣式化 drop-down 子控制項會抑制原生下拉箭頭，必須不存在
    assert "::drop-down" not in DARK_QSS


def test_apply_dark_theme_sets_app_stylesheet(qtbot):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    old = app.styleSheet()
    try:
        apply_dark_theme(app)
        assert "#1e1e1e" in app.styleSheet()
    finally:
        app.setStyleSheet(old)  # 不污染其他測試
