"""固定深色主題：整個 app 套一份 QSS，讓面板外觀貼近 Windows Terminal 的深色配色。

以 QApplication.setStyleSheet 套用，樣式會傳到所有子視窗，
包含 GitPanel、SimplePanel 與各種對話框（QInputDialog / QFileDialog / QMessageBox）。
"""

from __future__ import annotations

DARK_QSS = """
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QDialog {
    background-color: #1e1e1e;
}

QLabel {
    background: transparent;
    color: #e0e0e0;
}

QPushButton, QToolButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px 8px;
}

QPushButton:hover, QToolButton:hover {
    background-color: #3d3d3d;
}

QPushButton:pressed, QToolButton:pressed {
    background-color: #252525;
}

QPushButton:disabled, QToolButton:disabled {
    color: #777;
    border-color: #333;
}

QTextEdit, QPlainTextEdit, QLineEdit, QListWidget, QComboBox, QAbstractSpinBox {
    background-color: #252526;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 3px;
    selection-background-color: #094771;
    selection-color: #ffffff;
}

QListWidget::item {
    padding: 2px;
}

QListWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #2a2d2e;
}

QComboBox::drop-down {
    background-color: #2d2d2d;
    border-left: 1px solid #3c3c3c;
    width: 16px;
}

QComboBox QAbstractItemView {
    background-color: #252526;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    selection-background-color: #094771;
    selection-color: #ffffff;
}

QCheckBox, QRadioButton {
    background: transparent;
    color: #e0e0e0;
}

QMenu {
    background-color: #252526;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
}

QMenu::item:selected {
    background-color: #094771;
}

QScrollBar:vertical {
    background: #1e1e1e;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #424242;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #4f4f4f;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #1e1e1e;
    height: 10px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #424242;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QToolTip {
    background-color: #252526;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
}
"""


def apply_dark_theme(app) -> None:
    """對整個 QApplication 套用深色 QSS。"""
    app.setStyleSheet(DARK_QSS)
