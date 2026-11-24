# -*- coding: utf-8 -*-
"""Вкладка OLAP-анализа: сводная таблица, тепловая раскраска, детализация"""

import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

TABLE_STYLE = """
    QTableWidget {
        background-color: #24283b; color: #c0caf5;
        gridline-color: #2f334d; border: 1px solid #2f334d; border-radius: 6px;
        font-size: 12px;
    }
    QHeaderView::section {
        background-color: #2f334d; color: #7aa2f7;
        padding: 5px; border: none; font-weight: bold;
    }
    QScrollBar:vertical {
        background: #2f334d; width: 12px; border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background: #414868; border-radius: 6px; min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background: #7aa2f7;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        background: #2f334d; height: 12px; border-radius: 6px;
    }
    QScrollBar::handle:horizontal {
        background: #414868; border-radius: 6px; min-width: 30px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #7aa2f7;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
"""

SCROLL_STYLE = """
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        background: #2f334d; width: 12px; border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background: #414868; border-radius: 6px; min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background: #7aa2f7;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        background: #2f334d; height: 12px; border-radius: 6px;
    }
    QScrollBar::handle:horizontal {
        background: #414868; border-radius: 6px; min-width: 30px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
"""


def _mix(c1: QColor, c2: QColor, t: float) -> QColor:
    """Линейная интерполяция двух цветов"""
    return QColor(
        round(c1.red() + (c2.red() - c1.red()) * t),
        round(c1.green() + (c2.green() - c1.green()) * t),
        round(c1.blue() + (c2.blue() - c1.blue()) * t),
    )


class OlapPanel(QWidget):
    """View OLAP-анализа"""

    def __init__(self, olap_vm, parent=None):
        super().__init__(parent)
        self.vm = olap_vm
        self._cube = None
        self._init_ui()
        self._connect()

    def _init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Единая область прокрутки на всю вкладку
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet(SCROLL_STYLE)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # --- Срез куба ---
        self.slice_box = QGroupBox('Срез OLAP-куба')
        form = QFormLayout(self.slice_box)
        form.setContentsMargins(15, 28, 15, 12)
        form.setSpacing(12)

        self.combo_rows = QComboBox()
        self.combo_cols = QComboBox()
        self.combo_measure = QComboBox()
        self.combo_agg = QComboBox()
        self.combo_agg.addItems(['Количество', 'Среднее', 'Минимум', 'Максимум', 'Сумма'])

        for w in (self.combo_rows, self.combo_cols, self.combo_measure, self.combo_agg):
            w.setMinimumHeight(34)
            w.setMinimumWidth(220)

        form.addRow('Измерение по строкам:', self.combo_rows)
        form.addRow('Измерение по столбцам:', self.combo_cols)
        form.addRow('Мера:', self.combo_measure)
        form.addRow('Агрегат:', self.combo_agg)

        btn_row = QHBoxLayout()
        self.btn_build = QPushButton('Построить куб')
        self.btn_build.setObjectName('btn_visualize')
        self.btn_build.setMinimumHeight(42)
        self.btn_build.setFixedWidth(240)
        btn_row.addWidget(self.btn_build)
        self.status_label = QLabel('Выберите измерения и постройте куб')
        self.status_label.setStyleSheet('color: #565f89; font-size: 12px;')
        btn_row.addWidget(self.status_label, 1)
        form.addRow(btn_row)

        layout.addWidget(self.slice_box)

        # --- Сводная таблица (скроллится собственными полосами) ---
        self.pivot_box = QGroupBox('Сводная таблица — щёлкните по ячейке для детализации')
        pv = QVBoxLayout(self.pivot_box)
        pv.setContentsMargins(15, 22, 15, 10)

        self.pivot_table = QTableWidget()
        self.pivot_table.setStyleSheet(TABLE_STYLE)
        self.pivot_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pivot_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.pivot_table.verticalHeader().setDefaultSectionSize(30)
        self.pivot_table.setMinimumHeight(220)
        self.pivot_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.pivot_table.cellClicked.connect(self._on_cell_clicked)

        pv.addWidget(self.pivot_table)
        layout.addWidget(self.pivot_box, 2)

        # --- Детализация (скроллится собственными полосами) ---
        self.detail_box = QGroupBox('Детализация (drill-down)')
        dv = QVBoxLayout(self.detail_box)
        dv.setContentsMargins(15, 22, 15, 10)

        self.detail_label = QLabel('Щёлкните по ячейке сводной таблицы, чтобы увидеть исходные записи')
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet('color: #c0caf5; font-size: 12px;')
        dv.addWidget(self.detail_label)

        self.detail_table = QTableWidget()
        self.detail_table.setStyleSheet(TABLE_STYLE)
        self.detail_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detail_table.setMinimumHeight(140)
        self.detail_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        dv.addWidget(self.detail_table)
        layout.addWidget(self.detail_box, 1)

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _connect(self):
        self.vm.dimensions_ready.connect(self._fill_combos)
        self.vm.cube_ready.connect(self._render_cube)
        self.vm.detail_ready.connect(self._render_detail)
        self.vm.message.connect(self._on_message)
        self.btn_build.clicked.connect(self._on_build)
        self.combo_measure.currentTextChanged.connect(
            lambda txt: self.combo_agg.setEnabled(txt != 'Количество объектов')
        )

    # --- Обработчики ---
    def _fill_combos(self, dims, measures):
        for combo, items in ((self.combo_rows, dims), (self.combo_cols, dims),
                             (self.combo_measure, measures)):
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(items)
            if current in items:
                combo.setCurrentText(current)
            combo.blockSignals(False)
        # столбцы по умолчанию — Type
        if 'Type' in dims:
            self.combo_cols.setCurrentText('Type')
        self.status_label.setText('Данные готовы — постройте куб')

    def _on_build(self):
        self.vm.build(
            self.combo_rows.currentText(),
            self.combo_cols.currentText(),
            self.combo_measure.currentText(),
            self.combo_agg.currentText(),
        )

    def _render_cube(self, cube):
        self._cube = cube
        table = cube.table
        is_count = (cube.measure == 'Количество объектов' or cube.agg == 'Количество')

        self.pivot_table.setRowCount(len(table.index))
        self.pivot_table.setColumnCount(len(table.columns))
        self.pivot_table.setHorizontalHeaderLabels([str(c) for c in table.columns])
        self.pivot_table.setVerticalHeaderLabels([str(i) for i in table.index])

        # Диапазон значений без строки/столбца итогов — для тепловой шкалы
        core = table.iloc[:-1, :-1] if len(table) > 1 and table.shape[1] > 1 else table
        s = core.stack()
        vmin, vmax = (float(s.min()), float(s.max())) if len(s) else (0.0, 1.0)

        dark, accent = QColor('#24283b'), QColor('#7aa2f7')
        bold = QFont()
        bold.setBold(True)

        for r, idx in enumerate(table.index):
            for c, col in enumerate(table.columns):
                v = table.iloc[r, c]
                is_total = (r == len(table.index) - 1 or c == len(table.columns) - 1)
                text = f'{v:g}' if is_count else f'{v:.3f}'
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if is_total:
                    item.setBackground(QColor('#2f334d'))
                    item.setFont(bold)
                elif pd.notna(v):
                    t = (float(v) - vmin) / (vmax - vmin) if vmax > vmin else 0.3
                    item.setBackground(_mix(dark, accent, 0.15 + t * 0.7))
                self.pivot_table.setItem(r, c, item)

        self.status_label.setText(
            f'Куб: {cube.row_dim} × {cube.col_dim} | {cube.measure}'
            + ('' if is_count else f' ({cube.agg})')
        )

    def _on_cell_clicked(self, r, c):
        if self._cube is None:
            return
        row_label = self.pivot_table.verticalHeaderItem(r).text()
        col_label = self.pivot_table.horizontalHeaderItem(c).text()
        if row_label == 'Итого' or col_label == 'Итого':
            self._on_message('warning', 'Ячейка итогов не детализируется — выберите ячейку данных')
            return
        self.vm.request_detail(self._cube.row_dim, row_label,
                               self._cube.col_dim, col_label)

    def _render_detail(self, df, desc):
        self.detail_label.setText(f'Фильтр: {desc} — найдено {len(df)} объектов')
        shown = df.head(200)
        self.detail_table.setRowCount(len(shown))
        self.detail_table.setColumnCount(len(df.columns))
        self.detail_table.setHorizontalHeaderLabels([str(c) for c in df.columns])
        for i, (_, row) in enumerate(shown.iterrows()):
            for j, col in enumerate(df.columns):
                self.detail_table.setItem(i, j, QTableWidgetItem(str(row[col])))
        if len(df) > len(shown):
            self.detail_label.setText(
                f'Фильтр: {desc} — найдено {len(df)} объектов (показаны первые {len(shown)})'
            )

    def _on_message(self, level, msg):
        color = {'error': '#f7768e', 'warning': '#e0af68'}.get(level, '#9ece6a')
        self.status_label.setText(f'<span style="color:{color}">{msg}</span>')
