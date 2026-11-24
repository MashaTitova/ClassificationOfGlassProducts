# -*- coding: utf-8 -*-
"""Панель лога — сворачивается/разворачивается"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel
)
from PySide6.QtCore import Qt


class LogPanel(QWidget):
    """Сворачиваемая панель логов внизу окна"""

    LEVEL_COLORS = {
        'info':    '#a9b1d6',
        'success': '#9ece6a',
        'warning': '#e0af68',
        'error':   '#f7768e',
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._expanded = False
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Заголовок-кнопка
        header = QWidget()
        header.setFixedHeight(32)
        header.setStyleSheet("background-color: #24283b; border-top: 1px solid #2f334d;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 10, 0)

        self.toggle_btn = QPushButton("▼ Журнал действий")
        self.toggle_btn.setFlat(True)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #7aa2f7;
                border: none; font-weight: bold; font-size: 13px;
                text-align: left; padding: 0;
            }
            QPushButton:hover { color: #9ab8ff; }
        """)
        self.toggle_btn.clicked.connect(self.toggle)
        h_layout.addWidget(self.toggle_btn)

        self.counter_lbl = QLabel("0 записей")
        self.counter_lbl.setStyleSheet("color: #565f89; font-size: 12px;")
        h_layout.addWidget(self.counter_lbl)
        h_layout.addStretch()

        clear_btn = QPushButton("Очистить")
        clear_btn.setFixedSize(80, 24)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b4261; color: #a9b1d6;
                border-radius: 4px; font-size: 11px; padding: 0;
            }
            QPushButton:hover { background-color: #4a5278; }
        """)
        clear_btn.clicked.connect(self.clear)
        h_layout.addWidget(clear_btn)
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setFixedSize(110, 24)
        self.save_btn.setToolTip("Сохранить лог в JSON (или нажмите F3)")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2f334d; color: #7aa2f7;
                border-radius: 4px; font-size: 11px; padding: 0;
                border: 1px solid #3b4261;
            }
            QPushButton:hover {
                background-color: #3b4261;
                color: #9ab8ff;
            }
            QPushButton:pressed {
                background-color: #1a1b26;
            }
        """)
        # Сигнал будет подключён из main_window
        h_layout.addWidget(self.save_btn)
        self.main_layout.addWidget(header)

        # Содержимое (скрыто по умолчанию)
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setMaximumHeight(180)
        self.content.setStyleSheet("""
            QTextEdit {
                background-color: #1a1b26;
                color: #a9b1d6;
                border: none;
                border-top: 1px solid #2f334d;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 6px;
            }
        """)
        self.content.setVisible(False)
        self.main_layout.addWidget(self.content)

    def toggle(self):
        self._expanded = not self._expanded
        self.content.setVisible(self._expanded)
        arrow = "▲" if self._expanded else "▼"
        self.toggle_btn.setText(f"{arrow} Журнал действий")

    def add_entry(self, timestamp: str, level: str, message: str):
        color = self.LEVEL_COLORS.get(level, '#a9b1d6')
        html = (
            f"<span style='color:#565f89'>[{timestamp}]</span> "
            f"<span style='color:{color};font-weight:bold'>[{level.upper()}]</span> "
            f"<span style='color:#c0caf5'>{message}</span>"
        )
        self.content.append(html)
        # Авто-прокрутка
        sb = self.content.verticalScrollBar()
        sb.setValue(sb.maximum())
        # Обновить счётчик
        n = self.content.document().blockCount()
        self.counter_lbl.setText(f"{n} записей")

    def clear(self):
        self.content.clear()
        self.counter_lbl.setText("0 записей")