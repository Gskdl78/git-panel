from ui.theme import DARK_QSS, apply_dark_theme


def test_dark_qss_has_core_colors():
    assert "#1e1e1e" in DARK_QSS and "QPushButton" in DARK_QSS
    # 樣式化 drop-down 子控制項會抑制原生下拉箭頭，必須不存在
    assert "::drop-down" not in DARK_QSS


def test_dark_qss_styles_check_indicators():
    # 深色底下原生指示器沒有對比，必須自繪三種型態
    assert "QRadioButton::indicator" in DARK_QSS
    assert "QCheckBox::indicator" in DARK_QSS
    assert "QListWidget::indicator" in DARK_QSS
    # 自繪後原生勾勾/圓點不會畫出來，checked 狀態必須另有樣式區分
    assert ":checked" in DARK_QSS
    assert ":disabled" in DARK_QSS
    # 補指示器樣式時不可順手把 drop-down 加回來
    assert "::drop-down" not in DARK_QSS


def test_checked_radio_renders_differently_than_unchecked(qtbot):
    """離屏渲染驗證：勾選與未勾選的 radio 畫面必須不同（不能兩個都看不出來）。"""
    from PySide6.QtWidgets import QRadioButton

    def grab(checked):
        rb = QRadioButton("x")
        rb.setStyleSheet(DARK_QSS)
        rb.setAutoExclusive(False)
        rb.setChecked(checked)
        rb.resize(80, 24)
        qtbot.addWidget(rb)
        return rb.grab().toImage()

    off = grab(False)
    on = grab(True)
    assert off != on


def test_apply_dark_theme_sets_app_stylesheet(qtbot):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    old = app.styleSheet()
    try:
        apply_dark_theme(app)
        assert "#1e1e1e" in app.styleSheet()
    finally:
        app.setStyleSheet(old)  # 不污染其他測試
