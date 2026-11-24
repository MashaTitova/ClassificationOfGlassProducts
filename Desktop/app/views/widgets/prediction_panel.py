"""Панель предсказаний"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

import pandas as pd
from models.data_model import FEATURE_COLUMNS

import logging
logger = logging.getLogger(__name__)

class PredictionPanel(QWidget):
    """Вкладка предсказаний:"""

    predict_new_requested = Signal(dict)    
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def get_input_values(self, input_table: QTableWidget) -> tuple:
        """
        Считывает значения из таблицы ввода.
        Возвращает кортеж (features, errors), где:
          - features: dict с валидными значениями
          - errors: список строк с описанием проблем
        """
        features = {}
        errors = []
        headers = ['Id'] + FEATURE_COLUMNS

        for col_idx, col_name in enumerate(headers):
            if col_idx >= input_table.columnCount():
                errors.append(f"{col_name}: колонка не найдена в таблице")
                continue

            item = input_table.item(0, col_idx)
            if item is None:
                errors.append(f"{col_name}: ячейка пуста")
                continue

            text = item.text().strip()
            if not text:
                errors.append(f"{col_name}: ячейка пустая")
                continue

            try:
                if col_name == 'Id':
                    features[col_name] = int(text)
                else:
                    features[col_name] = float(text)
            except ValueError:
                errors.append(f"{col_name}: '{text}' не является числом")

        return features, errors

    def reset_input_table(self, input_table: QTableWidget):
        """Сбрасывает таблицу к значениям по умолчанию"""
        defaults = {
            'Id': '1', 'RI': '1.52101', 'Na': '13.64', 'Mg': '4.49',
            'Al': '1.10', 'Si': '71.78', 'K': '0.06', 'Ca': '8.75',
            'Ba': '0.00', 'Fe': '0.00'
        }
        headers = ['Id'] + FEATURE_COLUMNS
        for col_idx, col_name in enumerate(headers):
            item = input_table.item(0, col_idx)
            if item is not None:
                item.setText(defaults.get(col_name, '0.0'))

    def show_prediction_result(self, result: dict, result_label: QLabel):
        """Отображает результат предсказания"""
        pred = result.get('prediction', '?')
        proba = result.get('probabilities')
        idx = result.get('index', '?')
        
        logger.info(f"[show_prediction_result] Отображение: pred={pred}, proba_count={len(proba) if proba else 0}")
        
        html = (
            f"<b style='color:#7aa2f7;font-size:14px'>Объект #{idx}</b><br>"
            f"<b style='color:#9ece6a;font-size:15px'>Предсказанный Type: {pred}</b><br>"
        )

        if proba:
            html += "<br><b style='color:#bb9af7'>Вероятности по классам:</b><br>"
            for cls, p in sorted(proba.items()):
                bar_len = int(p * 30)
                bar = "█" * bar_len + "░" * (30 - bar_len)
                html += (
                    f"<span style='color:#7dcfff'>Class {cls}</span>: "
                    f"<span style='color:#565f89;font-family:monospace'>{bar}</span> "
                    f"<b>{p:.3f}</b><br>"
                )
        else:
            html += "<br><span style='color:#e0af68'>Модель не вернула вероятности</span><br>"

        result_label.setText(html)
        logger.info(f"[show_prediction_result] Отображено")

    def show_model_metrics(self, evaluation: dict, result_label: QLabel):
        """Отображает оценку уверенности конкретного предсказания"""
        if not evaluation:
            result_label.setText("Оценка недоступна")
            return

        conf = evaluation['confidence']
        margin = evaluation['margin']
        entropy = evaluation['normalized_entropy']

        # Цветовая индикация уверенности
        if conf >= 0.8:
            conf_color = '#9ece6a'  # зелёный — высокая
            conf_text = 'Высокая'
        elif conf >= 0.5:
            conf_color = '#e0af68'  # жёлтый — средняя
            conf_text = 'Средняя'
        else:
            conf_color = '#f7768e'  # красный — низкая
            conf_text = 'Низкая'

        # Цвет для margin
        if margin >= 0.3:
            margin_color = '#9ece6a'
        elif margin >= 0.1:
            margin_color = '#e0af68'
        else:
            margin_color = '#f7768e'

        # Цвет для entropy 
        if entropy <= 0.3:
            entropy_color = '#9ece6a'
        elif entropy <= 0.7:
            entropy_color = '#e0af68'
        else:
            entropy_color = '#f7768e'

        html = (
            f"<b style='color:#bb9af7;font-size:14px'>Оценка уверенности предсказания:</b><br><br>"
            f"<span style='color:{conf_color};font-size:13px'>"
            f"<b>Уверенность:</b> {conf:.3f} ({conf_text})</span><br>"
            f"<span style='color:{margin_color};font-size:13px'>"
            f"<b>Margin (разрыв с 2-м местом):</b> {margin:.3f}</span><br>"
            f"<span style='color:{entropy_color};font-size:13px'>"
            f"<b>Неопределённость (entropy):</b> {entropy:.3f}</span>"
        )

        result_label.setText(html)

    def show_error(self, message: str, result_label: QLabel):
        result_label.setText(f"<span style='color:#f7768e'>{message}</span>")