"""Тёмная тема Tokyo Night для приложения"""

DARK_STYLE = """
/* ===== ОСНОВНОЙ ФОН ===== */
QWidget {
    background-color: #1a1b26;
    color: #c0caf5;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 14px;
}

/* ===== ВКЛАДКИ ===== */
QTabWidget::pane {
    border: 1px solid #2f334d;
    border-radius: 8px;
    background-color: #1a1b26;
    padding: 12px;
}

QTabBar::tab {
    background-color: #24283b;
    color: #a9b1d6;
    padding: 14px 32px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid #2f334d;
    font-size: 15px;
    font-weight: 500;
    min-width: 200px;
}

QTabBar::tab:selected {
    background-color: #7aa2f7;
    color: #1a1b26;
    font-weight: bold;
    border: 1px solid #7aa2f7;
}

QTabBar::tab:hover:!selected {
    background-color: #2f334d;
    color: #c0caf5;
}

/* ===== КНОПКИ ===== */
QPushButton {
    background-color: #7aa2f7;
    color: #1a1b26;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 15px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #9ab8ff;
}

QPushButton:pressed {
    background-color: #5d87e0;
}

QPushButton:disabled {
    background-color: #3b4261;
    color: #565f89;
}

QPushButton#btn_recreate {
    background-color: #bb9af7;
}
QPushButton#btn_recreate:hover { background-color: #d4b8ff; }
QPushButton#btn_recreate:pressed { background-color: #a07de0; }

QPushButton#btn_clear {
    background-color: #f7768e;
}
QPushButton#btn_clear:hover { background-color: #ff94a8; }
QPushButton#btn_clear:pressed { background-color: #e05d75; }

QPushButton#btn_select_model {
    background-color: #7dcfff;
}
QPushButton#btn_select_model:hover { background-color: #9ee0ff; }

/* ===== РАДИОКНОПКИ ===== */
QRadioButton {
    color: #c0caf5;
    spacing: 8px;
    padding: 6px;
    font-size: 14px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid #565f89;
    background-color: #1a1b26;
}

QRadioButton::indicator:hover {
    border: 2px solid #7aa2f7;
}

QRadioButton::indicator:checked {
    background-color: #7aa2f7;
    border: 2px solid #7aa2f7;
}

/* ===== ПОЛЯ ВВОДА ===== */
QSpinBox, QDoubleSpinBox {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #2f334d;
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 14px;
    min-height: 22px;
    selection-background-color: #7aa2f7;
    selection-color: #1a1b26;
}

QSpinBox:hover, QDoubleSpinBox:hover { border-color: #7aa2f7; }
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #7aa2f7;
    background-color: #2a2e45;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 18px;
    background-color: #2f334d;
    border-left: 1px solid #2f334d;
    border-top-right-radius: 4px;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 18px;
    background-color: #2f334d;
    border-left: 1px solid #2f334d;
    border-bottom-right-radius: 4px;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: none;
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #7aa2f7;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: none;
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #7aa2f7;
}

/* ===== КОМБОБОКСЫ ===== */
QComboBox {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #2f334d;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 22px;
    font-size: 14px;
}

QComboBox:hover { border-color: #7aa2f7; }
QComboBox:focus {
    border: 1px solid #7aa2f7;
    background-color: #2a2e45;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid #2f334d;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    background-color: #2f334d;
}

QComboBox QAbstractItemView {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #7aa2f7;
    selection-background-color: #7aa2f7;
    selection-color: #1a1b26;
    outline: none;
}

/* ===== ПОЛЯ ТЕКСТА ===== */
QLineEdit {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #2f334d;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 14px;
    min-height: 22px;
    selection-background-color: #7aa2f7;
    selection-color: #1a1b26;
}

QLineEdit:hover { border-color: #7aa2f7; }
QLineEdit:focus {
    border: 1px solid #7aa2f7;
    background-color: #2a2e45;
}

/* ===== МЕТКИ ===== */
QLabel {
    color: #c0caf5;
    background-color: transparent;
    font-size: 14px;
}

/* ===== GROUP BOX ===== */
QGroupBox {
    background-color: #24283b;
    border: 1px solid #2f334d;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 20px;
    font-weight: bold;
    color: #7aa2f7;
    font-size: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: #7aa2f7;
}

/* ===== ПРОГРЕСС-БАР ===== */
QProgressBar {
    border: 1px solid #2f334d;
    border-radius: 10px;
    background-color: #24283b;
    text-align: center;
    color: #1a1b26;
    font-weight: bold;
    font-size: 13px;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7aa2f7, stop:0.5 #bb9af7, stop:1 #7dcfff
    );
    border-radius: 8px;
}

/* ===== СКРОЛЛБАРЫ ===== */
QScrollBar:vertical {
    background-color: #1a1b26;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #565f89;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7aa2f7;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ===== TOOLTIP ===== */
QToolTip {
    background-color: #2f334d;
    color: #c0caf5;
    border: 1px solid #7aa2f7;
    border-radius: 4px;
    padding: 6px;
    font-size: 13px;
}

/* ===== МЕНЮ-БАР ===== */
QMenuBar {
    background-color: #1a1b26;
    color: #c0caf5;
    font-size: 14px;
    padding: 2px;
}

QMenuBar::item:selected {
    background-color: #7aa2f7;
    color: #1a1b26;
}

QMenu {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #2f334d;
}

QMenu::item:selected {
    background-color: #7aa2f7;
    color: #1a1b26;
}

/* ===== ТЕКСТОВОЕ ПОЛЕ СПРАВКИ ===== */
QTextEdit {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #2f334d;
    border-radius: 6px;
    padding: 15px;
    font-size: 13px;
    line-height: 1.6;
}

QTextEdit h2 { color: #7aa2f7; font-size: 16px; margin-top: 20px; }
QTextEdit h3 { color: #bb9af7; font-size: 14px; margin-top: 15px; }
QTextEdit b { color: #7dcfff; }
QTextEdit code {
    background-color: #1a1b26;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', monospace;
    color: #9ece6a;
}
"""